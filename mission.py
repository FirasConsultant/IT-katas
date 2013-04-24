from main import AuthHandler as AH
import datetime

class Mission(AH):
    '''
    Class factoring common initialization for all missions
    '''
    def __init__(self, req, res, deadline=None):
        super(Mission, self).__init__(req, res)

        boss = self.app.config.get('boss') or 'lucadefe'
        self.agent = ((self.session['userid'] == boss
                       and self.request.GET.get('studid'))
                      or self.session['userid'])
        self.solve = (self.session['userid'] == boss and
                     self.request.GET.has_key('solve'))
        self.remaining = deadline is not None and deadline - datetime.datetime.today()
        self.static = self.request.GET.has_key('static')