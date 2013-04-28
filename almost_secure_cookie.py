r"""
"Almost secure" implementation of a secure cookie ;)
"""

from hashlib import md5
import json
import time
import webapp2
import os

API_VERSION = os.environ.get('CURRENT_VERSION_ID').split('.')[0]

class SessionError(Exception):
    pass
    
class Session(dict):
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
        super(Session, self).__init__()
        self._hndl = hndl
        self._cookie_name = cookie_name
        self._secret = (secret or hndl.app.config.get('secret') or "Pulcinella's").replace('|', '')
        self._max_age = max_age or hndl.app.config.get('session_age') or 60*60*24

        try:
            self._parse_cookie(hndl.request.cookies[self._cookie_name])
        except (KeyError, SessionError, TypeError) as e:
            pass

    def send_cookie(self):
        self._hndl.response.set_cookie(self._cookie_name,
                                       self._make_cookie(),
                                       max_age=self._max_age)


    def __setitem__(self, key, val):
        if not isinstance(key, str):
            raise SessionError("Keys must be pure strings")
        try:
            json.dumps(val)
        except TypeError:
            raise SessionError("Values must be JSONable")
        super(Session, self).__setitem__(key, val)

    def _parse_cookie(self, cookie):
        """
        Verifies the MAC and the expiration time of `cookie`, then 
        deserializes it into the session dictionary
        """
        mac, _, ser = cookie.partition('|')
        if md5(self._secret + '|'
               + API_VERSION + '|'
               + ser).hexdigest()[0:8] != mac:
            raise SessionError('MAC verification failed')
        exp, _, dict = ser.partition('|')
        if int(exp) < time.time():
            raise SessionError('Cookie expired')
        self.update(json.loads(dict))

    def _make_cookie(self):
        """
        Serializes the session dictionary, adds an expiration timestamp,
        and MACs it with a very insecure variant of HMAC.
        """
        ser = str(int(time.time()) + self._max_age) + '|' + json.dumps(self)
        return md5(self._secret + '|' 
                   + API_VERSION + '|'
                   + ser).hexdigest()[0:8] + '|' + ser


def with_session(meth):
    """
    Decorator to add session management to a handler method
    """
    def wrapper(self, *args, **kw):
        self.session = Session(self)
        res = meth(self, *args, **kw)
        self.session.send_cookie()
        return res
    return wrapper
