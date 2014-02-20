r"""
This modules contains all the logic for user management
"""

import webapp2
from webapp2 import RequestHandler
from webapp2_extras import jinja2
import urllib
from urlparse import urlparse
import xml.etree.ElementTree as ET
from almost_secure_cookie import with_session
from google.appengine.api import urlfetch
from google.appengine.api import users as gooser
import main


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
        self.is_boss = (gooser.is_current_user_admin() or
                        self.__repr__()
                        in webapp2.get_app().config['bosses'])

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__() + ('' if self.domain is None else '@' + self.domain)

    def friendly(self):
        return self.get('realname') or self.__str__()

    def __nonzero__(self):
        return True

    # For Python 3.x compatibility
    __bool__ = __nonzero__


class CASLogin(RequestHandler):
    """
    This handles logins using a CAS 2.0 SSO server with SAML 1.1
    attributes (such as cas-dev.uvsq.fr)
    """
    @staticmethod
    def login_url(hndl, path='/'):
        return "%s/login?service=%s" % CASLogin._get_urls(hndl, 'cas', path)

    @staticmethod
    def logout_url(hndl):
        return "%s/logout?service=%s" % CASLogin._get_urls(hndl, 'logout')

    @staticmethod
    def _get_urls(hndl, redirect, path=None):
        cas_host = hndl.app.config['cas_host']
        service = hndl.app.config.get('cas_service') or hndl.request.host_url
        service += hndl.uri_for(redirect, path=path)
        return (cas_host, urllib.quote(service, ''))

    @with_session
    def get(self, path='/'):
        cas_host, service = CASLogin._get_urls(self, 'cas', path)
        domain = urlparse(cas_host).netloc
    
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
                return

        self.abort(403)

class GoogleLogin(RequestHandler):
    """
    This handles logins using Google's User API
    """
    @staticmethod
    def login_url(hndl, path='/'):
        return gooser.create_login_url(
            hndl.uri_for('google', path=path))

    @staticmethod
    def logout_url(hndl):
        return gooser.create_logout_url(hndl.uri_for('logout'))

    @with_session
    def get(self, path='/'):
        user = gooser.get_current_user()
        if user:
            self.session['user'] = User(
                name=user.user_id(),
                domain='google.com',
                realname=user.nickname(),
                mail=user.email(),
                )
            self.redirect(path)
        else:
            abort(403)


def loggedin(meth=None):
    """
    Decorator granting access to a handler method only if the user is logged in
    """
    def wrapper(self, *args, **kw):
        user = self.session.get('user')
        if user:
            self.session['user'] = user = User(user)
        if user and meth:
            return meth(self, *args, **kw)
        else:
            jinja = jinja2.get_jinja2(app=self.app)
            if user:
                if user.domain == 'google.com':
                    logout = GoogleLogin.logout_url(self)
                elif user.domain == urlparse(self.app.config['cas_host']).netloc:
                    logout = CASLogin.logout_url(self)
                else:
                    logout = self.uri_for('logout')
            else:
                logout = None
            self.response.write(jinja.render_template('index.html', **{
                        'katas': main.katas,
                        'user': user and repr(user),
                        'google_login': GoogleLogin.login_url(self, self.request.path),
                        'cas_login': CASLogin.login_url(self, self.request.path),
                        'logout': logout,
                        }))

    return with_session(wrapper)


class Logout(RequestHandler):
    """
    Logs out (it only erases user information from the session cookie,
    the user can keep logging in with an old cookie)
    """

    @loggedin
    def get(self):
        del self.session['user']
        self.response
        self.redirect('/')
