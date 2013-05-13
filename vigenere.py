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
            self._text = ''.join(f.readlines())

            self._key = _gen_key(self.session.permarandom(self._agent_at))
            self._ciph = _do_vig(self._text, self._key)

        return meth(self, *args, **kw)

    return wrapper

    
class Vigenere(TH):
    @mission(2013, 4, 11, 4)
    @init
    def get(self):
        self.cnr('vigenere.html',
                 agent=self._agent,
                 ciphertext=self._ciph,
                 decrypt=self._solve,
                 cleartext=self._solve and self._text,
                 deciphertext=self._solve and _do_vig(self._ciph, self._key, cipher=-1),
                 decryptext=self._solve and _cryptanalysis(self._ciph),
                 countdown=self._countdown,
                 static=self._static,
                 uri_dnld=self.uri_for(VigenereDownload.__name__)
                 )

class VigenereDownload(RequestHandler):
    @mission()
    @init
    def get(self):
        self.response.content_type = 'text/plain'
        self.response.content_disposition = 'attachment;filename="cipher.txt"'
        self.response.write(self._ciph)

routes = [('', Vigenere),
          ('download', VigenereDownload)]

def _gen_key(random):
    length = random.randrange(10, 20)
    return [random.randrange(26) for i in range(length)]

def _do_vig(text, key, cipher=1):
    return ''.join(imap(lambda (c, k) : chr(((ord(c) - ord('a')) + cipher*k) % 26 + ord('a')),
                        izip(ifilter(lambda c: c >= 'a' and c <= 'z', text.lower()),
                             cycle(key))))
    
def _compute_freq(text, start=0, step=1):
    return [text[start::step].count(chr(c))
            for c in range(ord('a'), ord('z')+1)]

def _coincidence(freqs):
    n = sum(freqs) + 0.0
    return reduce(lambda x,y:x+y*(y-1), freqs) / (n*(n-1))

def _cryptanalysis(ciph):
    for length in range(10, 20):
        coincs = [_coincidence(_compute_freq(ciph, i, length))
                  for i in range(length)]
        if sum(coincs)/len(coincs) > 0.06:
            break
    else:
        return 'Could not find key length'
    
    key = [max(enumerate(_compute_freq(ciph, i, length)), 
               key=lambda x:x[1])[0] - ord('e') + ord('a')
           for i in range(length)]
    
    return _do_vig(ciph, key, -1)
