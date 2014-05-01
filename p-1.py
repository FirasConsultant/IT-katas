from main import TemplateHandler as TH
from webapp2 import RequestHandler
from mission import mission
from algorithms import rand_smooth_prime as rsp, next_probable_prime as npp
    
class Pminus1(TH):
    @mission(2014, 5, 8, 2)
    def get(self):
        random = self.session.permarandom(self._agent_at)
        self.p = rsp(random, 100, 2)
        self.q = npp(random.randrange(2**500, 2**503))

        self.cnr('p-1.html',
                 agent=self._agent,
                 p=self._solve and self.p,
                 q=self._solve and self.q,
                 n=self.p*self.q,
                 countdown=self._countdown,
                 static=self._static,
                 uri_test=self.uri_for(DivisibilityTest.__name__),
                 )
            

class DivisibilityTest(RequestHandler):
    def get(self):
        self.response.content_type = 'text/plain'
        try:
            n, m = int(self.request.get('n')), int(self.request.get('m'))
        except:
            self.response.write('ERROR')
        else:
            if 1 < m < n and n % m == 0:
                self.response.write('Yes')
            else:
                self.response.write('No')

routes = [('', Pminus1),
          ('divisible', DivisibilityTest)]
