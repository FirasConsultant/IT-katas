from main import loggedin
import datetime
import logging

def mission(*ymdh):
    '''
    Decorator factoring common initialization for all missions
    '''
    def decorator(meth):
        try:
            remaining = datetime.datetime(*ymdh) - datetime.datetime.today()
        except:
            remaining = None

        def wrapper(self, *args, **kw):
            self._agent = ((self.request.registry['user'].is_boss
                            and self.request.GET.get('studid'))
                           or str(self.request.registry['user']))
            self._agent_at = ((self.request.registry['user'].is_boss
                               and self.request.GET.get('studid'))
                              or repr(self.request.registry['user']))
            self._solve = (self.request.registry['user'].is_boss and
                           self.request.GET.has_key('solve'))
            self._countdown = remaining and {
                'rem': remaining,
                'expired': remaining <= datetime.timedelta(0),
                }
            self._static = self.request.GET.has_key('static')

            logging.info('Request from %s, user %s, as %s' % (str(self.request.remote_addr),
                                                             str(self.request.registry['user']),
                                                             self._agent_at))
            
            return meth(self, *args, **kw)

        return loggedin(wrapper)

    return decorator
