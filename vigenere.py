from main import TemplateHandler as TH
from mission import Mission
import datetime

class Vigenere(Mission, TH):
    def secure_get(self):
        self.start_mission(datetime.datetime(2013, 4, 11, 4))

        self.cnr('vigenere.html', {
                'agent': self.agent,
                'ciphertext': 'a',
                'decrypt': self.solve,
                'cleartext': self.solve and 'a',
                'deciphertext': self.solve and 'a',
                'decryptext': self.solve and 'a',
                'countdown': {
                    'rem': self.remaining,
                    'expired': self.remaining <= datetime.timedelta(0),
                    },
                'static': self.static,
                'uri': self.uri_for(self.__class__.__name__)
                })

class VigenereDownload(Mission):
    def secure_get(self):
        pass
