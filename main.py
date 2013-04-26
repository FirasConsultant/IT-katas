# coding=utf-8

import webapp2
from webapp2 import WSGIApplication, Route, RequestHandler
from webapp2_extras import jinja2
import yaml
import logging
from almost_secure_cookie import with_session
from os.path import join, dirname
from os import environ
from Crypto import Random
import base64
from auth import CASLogin, GoogleLogin, Logout, loggedin


# Individual Katas
katas = [
    ('vigenere', u'Cryptanalyse du chiffre de Vigenère'),
    ('dlog', u'Calcul de logarithmes discrets modulo un nombre premier'),
    ]


# config
try:
    secret = base64.b64encode(Random.new().read(15))
    logging.info('Using secret: ' + secret)
except:
    logging.warn("Using Pulcinella's secret.")
    secret = "Pulcinella's"

config = {
    'cas_host': 'https://cas-dev.uvsq.fr',
    'bosses': ['lucadefe@cas-dev.uvsq.fr', 
               '109150913449318350064@google.com'],
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


class Index(TemplateHandler):
    """
    Welcome page listing katas and allowing login
    """
    get = loggedin()

# Build the app
kmodules = {k[0]:__import__(k[0]) for k in katas}
kroutes = [Route(('/%s/%s' % (kata, route)).rstrip('/'),
                 Class, name=Class.__name__)
           for kata, module in kmodules.items()
           for route, Class in module.routes]
routes = [
    Route('/', Index),
    Route('/login/CAS<path:/.*>', CASLogin, name='cas'),
    Route('/login/google<path:/.*>', GoogleLogin, name='google'),
    Route('/logout', Logout, name='logout'),
    ]
app = WSGIApplication(routes + kroutes,
                      debug=environ.get('SERVER_SOFTWARE').startswith('Dev'),
                      config=config)

