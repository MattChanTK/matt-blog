import os
import webapp2
import jinja2
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "html")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


class REDIRECT_URL:

    BLOG_HOME = "/blog"
    BLOG_NEW_POST = "/blog/new_post"
    BLOG_POST_ROOT = "/blog/post"

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

def  blog_key(name = "default"):
    return db.Key.from_path("blogs", name)

class BlogPost(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now = True)

    def render(self):
        self._render_text = self.content.replace("\n", "<br>")
        return render_str("blog_post.html", p=self)

class BlogHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)


    def render(self, template, **kw):
        self.write(render_str(template, **kw))


class BlogHome(BlogHandler):

    def get(self):
        self.render_page()

    def post(self):
        self.redirect(REDIRECT_URL.BLOG_NEW_POST)

    def render_page(self):
        posts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC LIMIT 10")
        self.render("blog_home.html", posts=posts)


class NewPost(BlogHandler):

    def get(self):
        self.render_form()

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            blog_post = BlogPost(parent=blog_key(), subject=subject, content=content)
            blog_post.put()
            self.redirect("%s/%d" % (REDIRECT_URL.BLOG_POST_ROOT, blog_post.key().id()))
        else:
            error = "We need both the subject and the content"
            self.render_form(subject, content, error)

    def render_form(self, subject="", content="", error=""):
        self.render("blog_new_post_form.html", subject=subject, content=content, error=error)


class PostPage(BlogHandler):

    def get(self, post_id):

        key = db.Key.from_path('BlogPost', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return

        self.render_page(post=post)


    def post(self):
        self.redirect(REDIRECT_URL.BLOG_HOME)

    def render_page(self, post):
        self.render("blog_post_page.html", post=post)