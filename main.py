from webapp2 import WSGIApplication, Route, RequestHandler
import xml.etree.ElementTree as ET
from google.appengine.api import urlfetch
from almost_secure_cookie import SessionHandler as SH
import jinja2
from os.path import join, dirname
import yaml

# config
try:
    config = yaml.load(open('config.yaml', 'r'))
except IOError:
    config = {}

# Template engine
class TemplateHandler(RequestHandler):
    @staticmethod
    def guess_autoescape(template_name):
        if template_name is None or '.' not in template_name:
            return False
        ext = template_name.rsplit('.', 1)[1]
        return ext in ('html', 'htm', 'xml')

    jinja = jinja2.Environment(
        loader=jinja2.FileSystemLoader(
            config.get('template_dir') or
            join(dirname(__file__), 'templates')),
        autoescape=guess_autoescape,
        extensions=['jinja2.ext.autoescape']        
        )

    def cnr(self, view, values):
        self.response.write(self.jinja.get_template(view).render(values))

    def compile(self, view):
        return self.jinja.get_template(view)
        

# Authentication management
class AuthHandler(SH):
    """
    This handler extends the SessionHandler by verifying that the user
    is logged-in before proceeding to secure_get or secure_post
    """
    def dispatch(self):
        if self.session.has_key('userid'):
            super(AuthHandler, self).dispatch()
        else:
            self.redirect_to('login', path=self.request.path)

class Login(SH, TemplateHandler):
    """
    This handles logins using a CAS SSO server (such as cas-dev.uvsq.fr)
    """
    # configuration
    cas_host = 'https://cas-dev.uvsq.fr'
    next = 'http://proust.prism.uvsq.fr:5999/loc:8080/login'

    def get(self, path='/'):
        next = self.next + path
    
        ticket = self.request.GET.get('ticket')
        if ticket:
            url =  '%s/serviceValidate?service=%s&ticket=%s' % (self.cas_host, next, ticket)
            root = ET.fromstring(urlfetch.fetch(url, validate_certificate=True).content)
            if root[0].tag.rfind('authenticationSuccess') >= 0:
                self.session['userid'] = root[0][0].text
                self.redirect(path)

        self.cnr('login.html', {
            'title': 'Login',
            'cas_host': self.cas_host,
            'next': next
            })

class Logout(SH):
    """
    Logs out (it only erases user information from the session cookie,
    the user can keep logging in with an old cookie)
    """
    def get(self):
        del self.session['userid']
        self.redirect('/login')


# Individual Katas
import vigenere


class Index(AuthHandler):
    def get(self):
        self.response.write('Hello, %s' % self.session['userid'])


# Build the app
routes = [
Route('/', Index),
Route('/login', Login),
Route('/login<path:/.*>', Login, name='login'),
Route('/logout', Logout),
Route('/vigenere', vigenere.Vigenere, vigenere.Vigenere.__name__),
Route('/vigenere/download', vigenere.VigenereDownload),    
]
app = WSGIApplication(routes, debug=True, config=config)
