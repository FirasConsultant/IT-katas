import numpy as np
from cStringIO import StringIO

class BitInStream(object):
    def __init__(self, byte_stream, step=1):
        self.stream = np.frombuffer(byte_stream, dtype=np.ubyte)
        self.it = np.nditer(self.stream)
        self.buf = np.empty(0, np.ubyte)
        self.step = step

    def next(self, n=None):
        if n is None:
            n = self.step
        out = self.buf
        n -= len(out)
        while n > 0:
            out = np.asarray(np.concatenate((
                        out, np.unpackbits(self.it.next())
                        )), dtype=np.ubyte)
            n -= 8
        if n == 0:
            n = len(out)
        self.buf = out[n:]
        return out[:n]

    def __len__(self):
        return len(self.stream) * 8

    def __iter__(self):
        return self

    
class BitOutStream(object):
    def __init__(self):
        self.stream = StringIO()
        self.buf = np.empty(0, np.ubyte)

    def write(self, bits):
        tmp = np.asarray(np.concatenate(
                (self.buf, 
                 np.fromiter(map(int, bits), dtype=np.ubyte))
                ), dtype=np.ubyte)
        bytes = np.array_split(tmp, range(8, len(tmp), 8))
        for b in bytes[:-1]:
            self.stream.write(np.packbits(b))
        if len(bytes[-1]) == 8:
            self.stream.write(np.packbits(bytes[-1]))
            self.buf = np.empty(0, np.ubyte)
        else:
            self.buf = bytes[-1]

        return len(tmp) // 8

    def close(self):
        self.write('0'*(-len(self.buf) % 8))
        tmp = self.stream.getvalue()
        self.stream.close()
        return tmp

