from main import TemplateHandler as TH
from webapp2 import RequestHandler, abort
from almost_secure_cookie import Session
from mission import mission
import random
import logging
from google.appengine.ext import db


levels = [
    (20, 1048583, 5),
    (25, 33554467, 2),
    (30, 1073741827, 2),
    (32, 4294967311, 3),
    (35, 34359738421, 2),
    (40, 1099511627791, 3),
    (50, 1125899906842679, 11),
    (60, 1152921504606847009, 13),
    (70, 1180591620717411303449, 3),
]


# Models
class Dlog(db.Model):
    pass
class Player(db.Model):
    level = db.IntegerProperty(required=True)
# Create root element
dbroot = Dlog.get_or_insert(key_name='root')

def init(meth):
    """
    Decorator initializing common variables.
    """
    def wrapper(self, *args, **kw):
        self._player = Player.get_or_insert(self._agent_at, level=0)

        if self._solve:
            self._max_level = len(levels) - 1
        else:
            self._max_level = self._player.level

        try:
            self._level = int(self.request.get('level'))
        except (ValueError, TypeError):
            self._level = self._max_level
        self._level = max(min(self._level, self._max_level), 0)

        self._bits, self._p, self._g = levels[self._level]
        random.seed(self._agent_at + str(self._level))
        self._exp = self._p and random.randrange(2 ** (self._bits//2 + 1), 2 ** self._bits)

        return meth(self, *args, **kw)

    return wrapper

    
class DLog(TH):
    @mission(2013, 5, 10, 4)
    @init
    def get(self):
        mission = self.jinja2.render_template(
            'dlog_levels.html',
            static=self._static,
            solve=self._solve,
            agent=self._agent,
            level=self._level,
            p=self._p,
            gen=self._g,
            value=self._p and pow(self._g, self._exp, self._p),
            ).split('<!-- level -->')[self._level].split('<!-- then -->')

        message = mission[1] if len(mission) > 1 else None
        mission = mission[0]

        # This parameter means the user is playing
        log = self.request.get('log')
        if not log:
            self.cnr('dlog.html',
                     countdown=self._countdown,
                     static=self._static,
                     solve=self._solve,
                     level=self._level,
                     max_level=self._max_level,
                     exp=self._exp,
                     mission=mission,
                     )
        else:
            try:
                log = int(log)
            except ValueError, TypeError:
                advance = 0
            else:
                if (self._exp - log) % (self._p - 1):
                    advance = 0
                else:
                    advance = 1
                    if self._level == self._player.level:
                        self._player.level += 1
                        self._player.put()
                        logging.warning('%s broke level %s'
                                        % (self.session['user'].friendly(), 
                                           self._level))

            next_level = self._level + advance
            next = self.uri_for(DLog.__name__,
                            level=next_level,
                            _full=True)
            if self._static:
                next += '&static'
            if self._solve:
                next += '&solve'

            if not advance or message is None:
                self.redirect(next)
            else:
                self.response.headers.add('Refresh', '5; url=%s' % next)
                self.cnr('dlog_play.html',
                         agent=self._agent,
                         countdown=self._countdown,
                         static=self._static,
                         solve=self._solve,
                         fail=not advance,
                         message=message,
                         uri=next)

routes = [('', DLog)]
