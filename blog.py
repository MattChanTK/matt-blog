import os
import webapp2
import jinja2
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'html')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)

class REDIRECT_URL:

    BLOG_HOME = "/blog"
    BLOG_NEW_POST = "/blog/new_post"
    BLOG_POST_ROOT = "/blog/post"

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class BlogPost(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

class BlogHome(Handler):

    def render_page(self):
        posts = BlogPost.all().order('-created')
        if posts:
            self.render("blog_home.html", posts=posts)

    def get(self):

        self.render_page()

    def post(self):
        self.redirect(REDIRECT_URL.BLOG_NEW_POST)


class NewPost(Handler):

    def render_form(self, subject="", content="", error=""):
        self.render("blog_new_post_form.html", subject=subject, content=content, error=error)

    def get(self):
        self.render_form()

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            blog_post = BlogPost(subject=subject, content=content)
            blog_post.put()
            self.redirect("%s/%d" % (REDIRECT_URL.BLOG_POST_ROOT, blog_post.key().id()))
        else:
            error = "We need both the subject and the content"
            self.render_form(subject, content, error)


class PostPage(Handler):
    def render_page(self, post):
        self.render("blog_post_page.html", post=post)

    def get(self):

        curr_url = self.request.url.split("/")
        post_id = curr_url[-1]

        if post_id:
            post_id = int(post_id)
            post = BlogPost.get_by_id(post_id)
            self.render_page(post)

    def post(self):
        self.redirect(REDIRECT_URL.BLOG_HOME)
