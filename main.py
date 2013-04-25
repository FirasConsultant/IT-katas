# coding=utf-8

import webapp2
from webapp2 import WSGIApplication, Route, RequestHandler
from webapp2_extras import jinja2
import yaml
import logging
import urllib
from google.appengine.api import urlfetch
import xml.etree.ElementTree as ET
from almost_secure_cookie import with_session
from urlparse import urlparse
from os.path import join, dirname
from os import environ
from Crypto import Random
import base64

# config
try:
    secret = base64.b64encode(Random.new().read(15))
    logging.info('Using secret: ' + secret)
except:
    logging.warn("Using Pulcinella's secret.")
    secret = "Pulcinella's"

config = {
    'cas_host': 'https://cas-dev.uvsq.fr',
    'bosses': ['lucadefe@cas-dev.uvsq.fr'],
    'secret':  secret
    }

try:
    config.update(yaml.load(open('config.yaml', 'r')))
except IOError:
    pass


# Template engine
class TemplateHandler(RequestHandler):
    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def cnr(self, view, **context):
        self.response.write(self.jinja2.render_template(view, **context))
        

# Authentication management
class User(dict):
    """
    User model
    """
    def __init__(self, *args, **kw):
        super(User, self).__init__(*args, **kw)
        if 'name' not in self:
            raise ValueError('Missing user name')

        self.name = self['name']
        self.domain = self.get('domain')
        self.is_boss = (self.__repr__()
                        in webapp2.get_app().config['bosses'])

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__() + ('' if self.domain is None else '@' + self.domain)


def loggedin(meth):
    """
    Decorator granting access to a handler method only if the user is logged in
    """
    def wrapper(self, *args, **kw):
        user = self.session.get('user')
        if user:
            self.session['user'] = User(user)
            return meth(self, *args, **kw)
        else:
            return self.redirect_to('login', path=self.request.path)
    return with_session(wrapper)

class Login(TemplateHandler):
    """
    This handles logins using a CAS 2.0 SSO server with SAML 1.1
    attributes (such as cas-dev.uvsq.fr)
    """

    @with_session
    def get(self, path='/'):
        cas_host = self.app.config['cas_host']
        domain = urlparse(cas_host).netloc
        service = urllib.quote((self.app.config.get('cas_service')
                   or self.req.host_url) + self.uri_for('login', path=path), '')
    
        ticket = self.request.GET.get('ticket')
        if ticket:
            url =  '%s/samlValidate?TARGET=%s' % (cas_host, service)
            saml = '''
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
  <SOAP-ENV:Header/>
  <SOAP-ENV:Body>
    <samlp:Request xmlns:samlp="urn:oasis:names:tc:SAML:1.0:protocol"
     MajorVersion="1" MinorVersion="1">
      <samlp:AssertionArtifact>%s</samlp:AssertionArtifact>
    </samlp:Request>
  </SOAP-ENV:Body>
</SOAP-ENV:Envelope>
''' % ticket
            root = ET.fromstring(
                urlfetch.fetch(
                    url, payload=saml, method=urlfetch.POST,
                    validate_certificate=True,
                    headers={'soapaction':
                                 'http://www.oasis-open.org/committees/security',
                             'content-type': 'text/xml',
                             }
                    ).content)
            if root.findall(".//*[@Value='samlp:Success']"):
                user = {attr.get('AttributeName'):
                            [val.text for val in attr]
                    for attr in root.findall(".//*[@AttributeName]")}
                self.session['user'] = User(
                    name=user['login'][0],
                    domain=domain,
                    realname=user['displayname'][0],
                    mail=user['mail'][0],
                    )
                self.redirect(path)

        self.cnr('login.html', title='Login',
                 cas_host=cas_host, service=service)

class Logout(RequestHandler):
    """
    Logs out (it only erases user information from the session cookie,
    the user can keep logging in with an old cookie)
    """

    @loggedin
    def get(self):
        del self.request.registry['user']
        del self.session['user']
        self.response
        self.redirect('/login')


# Individual Katas
katas = [
    ('vigenere', 'Cryptanalyse du chiffre de Vigenère'),
    ('dlog', 'Calcul de logarithmes discrets modulo un nombre premier'),
    ]
kmodules = {k[0]:__import__(k[0]) for k in katas}
kroutes = [Route(('/%s/%s' % (kata, route)).rstrip('/'),
                 Class, name=Class.__name__)
           for kata, module in kmodules.items()
           for route, Class in module.routes]

class Index(RequestHandler):
    def get(self):
        self.response.write('<ul>')
        for k, desc in katas:
            self.response.write('<li><a href="/%s">%s</b></a>.</li>' 
                                % (k, desc))
        self.response.write('</ul>')


# Build the app
routes = [
    Route('/', Index),
    Route('/login', Login),
    Route('/login<path:/.*>', Login, name='login'),
    Route('/logout', Logout),
    ]
app = WSGIApplication(routes + kroutes,
                      debug=environ.get('SERVER_SOFTWARE').startswith('Dev'),
                      config=config)

