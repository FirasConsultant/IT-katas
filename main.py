import webapp2
import xml.etree.ElementTree as ET
from google.appengine.api import urlfetch

def index(req):
    pass

def login(req):
    next = 'http://proust.prism.uvsq.fr:5999/loc:8080/login'
    cas_host = 'https://cas-dev.uvsq.fr'
    
    ticket = req.GET.get('ticket')
    if ticket:
        url =  '%s/serviceValidate?service=%s&ticket=%s' % (cas_host, next, ticket)
        root = ET.fromstring(urlfetch.fetch(url).content)
        if root[0].tag.rfind('authenticationSuccess') >= 0:
            userid = root[0][0].text
            return webapp2.Response(userid)

    return webapp2.Response('<a href="%s/login?service=%s">login</a>' % (cas_host, next))
        

routes = [
    ('/', index),
    ('/login', login)
]
app = webapp2.WSGIApplication(routes, debug=True)
