from main import TemplateHandler as TH
from webapp2 import RequestHandler
from mission import mission
import logging
from itertools import *
from codecs import open
from collections import namedtuple
from bitstream import BitInStream, BitOutStream, np
from cStringIO import StringIO

def init(meth):
    """
    Decorator initializing common variables.
    """
    def wrapper(self, *args, **kw):
        with open('misc/poe.txt', 'r', 'utf-8') as f:
            text = f.readlines()
            n = len(text)
            start = self.session.permarandom(self._agent_at).randrange(0, n-20);
            self._text = ''.join(text[start:start+20])
            self._zip = _zip(self._text)

        return meth(self, *args, **kw)

    return wrapper

    
class LZ78(TH):
    @mission(2014, 3, 6, 4)
    @init
    def get(self):
        self.cnr('lz78.html',
                 agent=self._agent,
                 text=self._text,
                 size=(str(len(self._text)), str(len(self._zip))),
                 unzip=self._solve and _unzip(self._zip),
                 countdown=self._countdown,
                 static=self._static,
                 uri_dnld=self.uri_for(LZ78Download.__name__)
                 )

class LZ78Download(RequestHandler):
    @mission()
    @init
    def get(self):
        self.response.content_type = 'text/plain'
        self.response.content_disposition = 'attachment;filename="lz78.bin"'
        self.response.write(self._zip)

routes = [('', LZ78),
          ('download', LZ78Download)]

Node = namedtuple('Node', ('id', 'children'))

def _zip(text, block_size=8, max_size=None):
    in_stream = BitInStream(text.encode('utf-8'), block_size)
    out_stream = BitOutStream()
    dictionary = Node(0, {})
    current = dictionary
    count = 0
    log2count = 0

    for symbol in in_stream:
        sym = symbol.tostring()
        if sym in current.children:
            current = current.children[sym]
        else:
            prefix = ('{:0%db}' % log2count).format(current.id)[:log2count]
            out_stream.write(prefix)
            out_stream.write(symbol)
            
            if not max_size or count < max_size:
                count += 1
                if 1 << log2count <= count:
                    log2count += 1
                current.children[sym] = Node(count, {})

            current = dictionary
            
    if current != dictionary:
        prefix = ('{:0%db}' % log2count).format(current.id)[:log2count]
        out_stream.write(prefix)
        out_stream.write('0' * block_size)

    logging.info('Zip dictionary size: %d', count)
    return out_stream.close()

def _unzip(code, block_size=8, max_size=None):
    in_stream = BitInStream(code)
    out_stream = BitOutStream()
    count = 0
    log2count = 0
    dictionary = [np.empty(0, np.ubyte)]

    while True:
        try:
            token = in_stream.next(log2count + block_size)
        except StopIteration:
            break
        cw = int(''.join(map(str, token[:log2count])), 2) if log2count else 0
        prefix = dictionary[cw]
        symbol = token[log2count:]
        dictionary.append(np.concatenate((prefix, symbol)).view(dtype=np.ubyte))

        if not max_size or count < max_size:
            count += 1
            if 1 << log2count <= count:
                log2count += 1

        out_stream.write(dictionary[-1])
    
    logging.info('Unzip dictionary size: %d', count)
    return out_stream.close().decode('utf-8').rstrip('\0')
