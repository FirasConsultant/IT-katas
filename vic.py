from main import TemplateHandler as TH
from webapp2 import RequestHandler
from mission import mission
from itertools import *

def init(meth):
    """
    Decorator initializing common variables.
    """
    def wrapper(self, *args, **kw):
        with open('misc/jangada.txt') as f:
            self._prng = self.session.permarandom(self._agent_at)

            text = f.readlines()
            print text
            n = len(text)
            start = self._prng.randrange(0, n-7)
            self._text = ''.join(text[start:start+7])

            self._board = _board_derivation(self._prng)
            self._vig_key = ''.join(str(self._prng.randrange(0, 10)) for i in range(8))
            self._ciph = _encrypt(_encode(self._text.lower(), self._board),
                                  self._vig_key)

        return meth(self, *args, **kw)

    return wrapper

    
class Vic(TH):
    @mission(2014, 4, 7, 18)
    @init
    def get(self):
        self.cnr('vic.html',
                 agent=self._agent,
                 board=self._board,
                 vig_key=self._vig_key,
                 ciphertext=self._ciph,
                 decrypt=self._solve,
                 cleartext=self._solve and self._text,
                 deciphertext=self._solve and _decode(_decrypt(self._ciph, self._vig_key), self._board),
                 countdown=self._countdown,
                 static=self._static,
                 uri_dnld=self.uri_for(VicDownload.__name__)
                 )

class VicDownload(RequestHandler):
    @mission()
    @init
    def get(self):
        self.response.content_type = 'text/plain'
        self.response.content_disposition = 'attachment;filename="cipher.txt"'
        self.response.write(self._ciph)

routes = [('', Vic),
          ('download', VicDownload)]

def _board_derivation(random):
    'derive a boardboard'
    from collections import OrderedDict as OD
    
    board = OD()

    board[''] = list('rustinea  ')
    random.shuffle(board[''])
    
    rest = list(set([chr(i + ord('a')) for i in range(26)]) - set(board[''])) + ['.', "'"]
    random.shuffle(rest)
    
    board[str(board[''].index(' '))] = rest[:10]
    board[str(9 - board[''][::-1].index(' '))] = rest[10:]
    print board, board[''][::-1].index(' ')

    return board
    
def _encode(text, board):
    return ''.join(i + str(l.index(c)) for c in text if c != ' ' 
                   for i, l in board.iteritems() if c in l)

def _decode(code, board):
    keys = board.keys()
    text = ''
    nextline = ''
    for c in code:
        if nextline == '' and c in keys:
            nextline = c
        else:
            text += board[nextline][int(c)]
            nextline = ''
    return text

def _encrypt(code, key, mode=1):
    return ''.join([str((int(c) + mode*int(k)) % 10) for c,k in izip(code, cycle(key))])

def _decrypt(code, key):
    return _encrypt(code, key, -1)
