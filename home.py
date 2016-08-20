import webapp2
import blog

class HomePage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write("Welcome to Matthew's Blog!!")

app = webapp2.WSGIApplication([
    ('/blog/new_post', blog.NewPost),
    ('/blog/post/.*', blog.PostPage),
    ('/blog.*', blog.BlogHome),
    ('/.*', HomePage),

], debug=True)
