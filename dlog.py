from main import TemplateHandler as TH
from webapp2 import RequestHandler, abort
from almost_secure_cookie import Session
from mission import mission
import random
import logging

levels = [
    (20, 1048583, 5,
     ['']),
    (25, 33554467, 2,
     ['']),
    (30, 1073741827, 2, 
     ['']),
    (32, 4294967311, 3,
     ['']),
    (35, 34359738421, 2,
     ['']),
    (40, 1099511627791, 3,
     ['']),
    (50, 1125899906842679, 11,
     ['']),
    (60, 1152921504606847009, 13,
     ['']),
    (70, 1180591620717411303449, 3,
     ['']),
    (None, None, None,
     ['']),
]

def init(meth):
    """
    Decorator initializing common variables.
    """
    def wrapper(self, *args, **kw):
        self._level_store = Session(self, cookie_name='dlog.level', max_age=30*24*60*60)

        try:
            self._max_level = int(self._level_store.get('level'))
        except (ValueError, TypeError):
            self._max_level = 0
        self._max_level = min(max(0, self._max_level), len(levels))

        if self._solve:
            self._max_level = len(levels) - 1

        try:
            self._level = int(self.request.get('level'))
        except (ValueError, TypeError):
            self._level = self._max_level
        self._level = max(min(self._level, self._max_level), 0)

        self._bits, self._p, self._g, self._text = levels[self._level]
        random.seed(self._agent_at + str(self._level))
        self._exp = self._p and random.randrange(2 ** (self._bits//2 + 1), 2 ** self._bits)

        return meth(self, *args, **kw)

    return wrapper

    
class DLog(TH):
    @mission(2013, 5, 10, 4)
    @init
    def get(self):
        self.cnr('dlog.html',
                 agent=self._agent,
                 countdown=self._countdown,
                 static=self._static,
                 solve=self._solve,
                 level=self._level,
                 max_level=self._max_level,
                 text=self._text,
                 p=self._p,
                 gen=self._g,
                 exp=self._exp,
                 value=self._p and pow(self._g, self._exp, self._p),
                 play_uri=self.uri_for(DLogPlay.__name__)
                 )

class DLogPlay(TH):
    @mission(2013, 5, 10, 4)
    @init
    def get(self):
        try:
            log = int(self.request.get('log'))
        except (ValueError, TypeError):
            return self.cnr('dlog_fail.html',
                            agent=self._agent,
                            countdown=self._countdown,
                            static=self._static,
                            solve=self._solve,
                            level=self._level,
                            uri=self.uri_for(DLog.__name__))

        if (self._exp - log) % (self._p - 1):
            return self.cnr('dlog_fail.html',
                            agent=self._agent,
                            countdown=self._countdown,
                            static=self._static,
                            solve=self._solve,
                            level=self._level,
                            uri=self.uri_for(DLog.__name__))

        if self._level == self._max_level:
            self._level_store['level'] = self._level + 1
            self._level_store.send_cookie()
            logging.warning('%s broke level %s'
                            % (self.session['user'].friendly(), 
                               self._level))
            
        return self.redirect_to(DLog.__name__, level=self._level + 1)


routes = [('', DLog),
          ('play', DLogPlay)]
