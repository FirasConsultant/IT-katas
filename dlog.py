from main import TemplateHandler as TH
from webapp2 import RequestHandler, abort
from almost_secure_cookie import Session
from mission import mission
import logging
from google.appengine.ext import db
from datetime import datetime

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
        random = self.session.permarandom(self._agent_at, self._level)
        if self._level == 3:
            check = 10
            while check == 10:
                isbn = random.randrange(10 ** 8, 10 ** 9)
                check = reduce(lambda x,(y,z): (x-int(y)*z)%11, zip(str(isbn), range(10,1,-1)), 0)
            self._exp = isbn*10 + check
        elif self._level == 5:
            self._exp = random.randrange(2 ** (self._bits//2 + 1), 10**12)
        else:
            self._exp = random.randrange(2 ** (self._bits//2 + 1), 2 ** self._bits)

        if self._level == 1:
            self._exp2 = random.randrange(2 ** (self._bits//2 + 1), 2 ** self._bits)
        else:
            self._exp2 = None

        return meth(self, *args, **kw)

    return wrapper

    
class DLog(TH):
    @mission(2013, 5, 10, 4)
    @init
    def get(self):
        mission = self.jinja2.render_template(
            'dlog_levels.html',
            countdown=self._countdown,
            today=datetime.now(),
            static=self._static,
            solve=self._solve,
            agent=self._agent,
            realname=self.session['user'].friendly(),
            level=self._level,
            p=self._p,
            gen=self._g,
            exp=self._exp,
            value=pow(self._g, self._exp, self._p),
            value2=self._exp2 and pow(self._g, self._exp2, self._p),
            ).split('<!-- level -->')[self._level]

        mission = mission.split('<!-- then -->')
        message = mission[1] if len(mission) > 1 else None
        mission = mission[0].split('<!-- fail -->')
        fail_msg = mission[1] if len(mission) > 1 else None
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
                if self._level == 1:
                    advance = int((pow(self._g, self._exp*self._exp2, self._p) - log) % self._p == 0)
                elif (self._exp - log) % (self._p - 1) == 0:
                    advance = 1
                else:
                    advance = 0
                    
            if advance and self._level == self._player.level:
                self._player.level += 1
                self._player.put()
                logging.warning('%s broke level %s'
                                % (self.session['user'].friendly(), 
                                   self._level))
            elif not advance and self._level == len(levels) - 1:
                self._player.level = 0
                self._player.put()
                logging.warning('%s game over'
                                % self.session['user'].friendly())

            next_level = self._level + advance
            if next_level < len(levels):
                next = self.uri_for(DLog.__name__,
                                    level=next_level,
                                    _full=True)
                if self._static:
                    next += '&static'
                if self._solve:
                    next += '&solve'
            else:
                next = None

            if advance and message is None:
                self.redirect(next)
            else:
                self.cnr('dlog_play.html',
                         agent=self._agent,
                         countdown=self._countdown,
                         static=self._static,
                         solve=self._solve,
                         fail=not advance,
                         message=(advance and message) or fail_msg,
                         uri=next)

routes = [('', DLog)]
