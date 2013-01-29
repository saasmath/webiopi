from webiopi.utils import route
from webiopi.i2c import I2C


class TMP102(I2C):
    def __init__(self, addr=0b1001000):
        I2C.__init__(self, addr, "TMP102")
        
    @route("GET", "temperature", "%.02f")
    def getTemperature(self):
        d = self.readBytes(2)
        return ((d[0] << 4) | (d[1] >> 4)) *0.0625

__all__ = [TMP102]

