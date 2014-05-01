from main import TemplateHandler as TH
from webapp2 import RequestHandler
from mission import mission
from algorithms import next_probable_prime as npp, miller_rabin_witness as mrw
from random import randrange

class MillerRabin(TH):
    @mission(2012, 5, 8, 2)
    def get(self):
        self.numbers = [npp(randrange(10**19, 10**20)) for i in range(19)]
        self.pos = randrange(0,20)
        c = npp(randrange(2*10**9, 10**10)) * npp(randrange(5*10**9, 10**10))
        self.numbers.insert(self.pos, c)
        try:
            n = int(self.request.get('n'))
        except:
            n = None
        self.cnr('miller-rabin.html',
                 agent=self._agent,
                 numbers=self.numbers,
                 pos=self.pos if self._solve else None,
                 countdown=self._countdown,
                 static=self._static,
                 uri_test=self.uri_for(MillerRabinTest.__name__),
                 n=n)
            

class MillerRabinTest(RequestHandler):
    def get(self):
        self.response.content_type = 'text/plain'
        try:
            n, a = int(self.request.get('n')), int(self.request.get('a'))
        except:
            self.response.write('ERROR')
        else:
            if mrw(n, a):
                self.response.write('Composite')
            else:
                self.response.write('No witness')

routes = [('', MillerRabin),
          ('test', MillerRabinTest)]
