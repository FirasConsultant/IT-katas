from main import TemplateHandler as TH
from mission import Mission
import datetime
import random
from itertools import *

class VigCommon(Mission):
    def __init__(self, req, res):
        super(VigCommon, self).__init__(req, res,
                                        datetime.datetime(2013, 4, 11, 4))

        print 'Request for %s from %s, user %s' % (self.request.path_qs, 
                                                   str(self.request.remote_addr),
                                                   self.agent)

        with open('misc/jangada.txt') as f:
            self.text = ''.join(f.readlines())

            self.key = self._gen_key(self.agent)
            self.ciph = self._do_vig(self.text, self.key)

    @staticmethod
    def _gen_key(salt):
        random.seed(salt)
        length = random.randrange(10, 20)
        return [random.randrange(26) for i in range(length)]

    @staticmethod
    def _do_vig(text, key, cipher=1):
        return ''.join(imap(lambda (c, k) : chr(((ord(c) - ord('a')) + cipher*k) % 26 + ord('a')),
                            izip(ifilter(lambda c: c >= 'a' and c <= 'z', text.lower()),
                                 cycle(key))))
    
    @staticmethod
    def _compute_freq(text, start=0, step=1):
        return [text[start::step].count(chr(c))
                for c in range(ord('a'), ord('z')+1)]

    @staticmethod
    def _coincidence(freqs):
        n = sum(freqs) + 0.0
        return reduce(lambda x,y:x+y*(y-1), freqs) / (n*(n-1))

    @staticmethod
    def _cryptanalysis(ciph):
        for length in range(10, 20):
            coincs = [VigCommon._coincidence(VigCommon._compute_freq(ciph, i, length))
                      for i in range(length)]
            if sum(coincs)/len(coincs) > 0.06:
                break
        else:
            return 'Could not find key length'
    
        key = [max(enumerate(VigCommon._compute_freq(ciph, i, length)), 
                   key=lambda x:x[1])[0] - ord('e') + ord('a')
               for i in range(length)]

        return VigCommon._do_vig(ciph, key, -1)
    
class Vigenere(VigCommon, TH):
    def get(self):
        self.cnr('vigenere.html', {
                'agent': self.agent,
                'ciphertext': self.ciph,
                'decrypt': self.solve,
                'cleartext': self.solve and self.text,
                'deciphertext': self.solve and self._do_vig(self.ciph, self.key, cipher=-1),
                'decryptext': self.solve and self._cryptanalysis(self.ciph),
                'countdown': {
                    'rem': self.remaining,
                    'expired': self.remaining <= datetime.timedelta(0),
                    },
                'static': self.static,
                'uri': self.uri_for(self.__class__.__name__)
                })

class VigenereDownload(VigCommon):
    def get(self):
        self.response.content_type = 'text/plain'
        self.response.content_disposition = 'attachment;filename="cipher.txt"'
        self.response.write(self.ciph)



