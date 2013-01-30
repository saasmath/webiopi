from webiopi.utils import route
from webiopi.i2c import I2C


class TMPXXX(I2C):
    def __init__(self, addr=0b1001000, name="TMPXXX"):
        I2C.__init__(self, addr, name)
        
    @route("GET", "temperature", "%.02f")
    def getTemperature(self):
        d = self.readBytes(2)
        return ((d[0] << 4) | (d[1] >> 4)) *0.0625

class TMP075(TMPXXX):
    def __init__(self, addr=0b1001000):
        TMPXXX.__init__(self, addr, "TMP075")

class TMP102(TMPXXX):
    def __init__(self, addr=0b1001000):
        TMPXXX.__init__(self, addr, "TMP102")

class TMP275(TMPXXX):
    def __init__(self, addr=0b1001000):
        TMPXXX.__init__(self, addr, "TMP275")

