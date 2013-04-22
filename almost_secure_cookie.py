r"""
"Almost secure" implementation of a secure cookie ;)
"""

from hashlib import md5
import json
import time
import webapp2
import UserDict

class SessionError(Exception):
    pass

class SessionHandler(webapp2.RequestHandler):
    """
    Handlers wanting a session can extend this class.
    """
    def dispatch(self):
        self.session = Session(self)
        try:
            webapp2.RequestHandler.dispatch(self)
        finally:
            self.session.send_cookie()


class Session(UserDict.DictMixin):
    """
    This class implements the session
    """
    
    def __init__(self, hndl, cookie_name='sessid', secret=None, max_age=None):
        """
        Initializes session from a Request objet.
        - `cookie_name` is the name of the session cookie
        - `secret` is the secret string used for MACing
        - `max_age` is the expiration time for the cookie
        """
        self.hndl = hndl
        self.cookie_name = cookie_name
        self.secret = (secret or hndl.app.config.get('secret') or "Pulcinella's").replace('|', '')
        self.max_age = max_age or hndl.app.config.get('session_age') or 60*60*24

        try:
            self._parse_cookie(hndl.request.cookies[self.cookie_name])
        except (KeyError, SessionError, TypeError) as e:
            self.dict = {}

    def send_cookie(self):
        self.hndl.response.set_cookie(self.cookie_name,
                                      self._make_cookie(),
                                      max_age=self.max_age)


    def __setitem__(self, key, val):
        if not isinstance(key, str):
            raise SessionError("Keys must be pure strings")
        try:
            json.dumps(val)
        except TypeError:
            raise SessionError("Values must be JSONable")
        self.dict[key] = val

    def __getitem__(self, key):
        return self.dict[key]
    
    def __delitem__(self, key):
        del self.dict[key]
        
    def keys(self):
        return self.dict.keys()

    def _parse_cookie(self, cookie):
        """
        Verifies the MAC and the expiration time of `cookie`, then 
        deserializes it into the session dictionary
        """
        mac, _, ser = cookie.partition('|')
        if md5(ser).hexdigest()[0:8] != mac:
            raise SessionError('MAC verification failed')
        exp, _, dict = ser.partition('|')
        if int(exp) < time.time():
            raise SessionError('Cookie expired')
        self.dict = json.loads(dict)

    def _make_cookie(self):
        """
        Serializes the session dictionary, adds an expiration timestamp,
        and MACs it with a very insecure variant of HMAC.
        """
        ser = str(int(time.time()) + self.max_age) + '|' + json.dumps(self.dict)
        return md5(ser).hexdigest()[0:8] + '|' + ser
