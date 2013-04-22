from webapp2 import WSGIApplication, Route
import xml.etree.ElementTree as ET
from google.appengine.api import urlfetch
from almost_secure_cookie import SessionHandler as SH

class AuthHandler(SH):
    """
    This handler extends the SessionHandler by verifying that the user
    is logged-in before proceeding to secure_get or secure_post
    """
    def get(self, *args, **kwds):
        if self.session.has_key('userid'):
            self.secure_get(*args, **kwds)
        else:
            self.redirect_to('login', path=self.request.path)

    def post(self, *args, **kwds):
        if self.session.has_key('userid'):
            self.secure_post(*args, **kwds)
        else:
            self.redirect_to('login', path=self.request.path)

class Login(SH):
    """
    This handles logins using a CAS SSO server (such as cas-dev.uvsq.fr)
    """
    def __init__(self, req, res,
                 cas_host='https://cas-dev.uvsq.fr',
                 next='http://proust.prism.uvsq.fr:5999/loc:8080/login'):
        self.cas_host = cas_host
        self.next = next
        self.initialize(req, res)

    def get(self, path='/'):
        next = self.next + path
    
        ticket = self.request.GET.get('ticket')
        if ticket:
            url =  '%s/serviceValidate?service=%s&ticket=%s' % (self.cas_host, next, ticket)
            root = ET.fromstring(urlfetch.fetch(url, validate_certificate=True).content)
            if root[0].tag.rfind('authenticationSuccess') >= 0:
                self.session['userid'] = root[0][0].text
                self.redirect(path)

        self.response.write('<a href="%s/login?service=%s">login</a>' % (self.cas_host, next))

class Logout(SH):
    """
    Logs out (it only erases user information from the session cookie,
    the user can keep logging in with an old cookie)
    """
    def get(self):
        del self.session['userid']
        self.redirect('/login')

class Index(AuthHandler):
    def secure_get(self):
        self.response.write('Hello, %s' % self.session['userid'])

class Vigenere(AuthHandler):
    def secure_get(self):
        self.response.write('Hello, Vigenere')

routes = [
    Route('/', Index),
    Route('/login', Login),
    Route('/login<path:/.*>', Login, name='login'),
    Route('/logout', Logout),
    Route('/vigenere', Vigenere),
]
app = WSGIApplication(routes, debug=True)
