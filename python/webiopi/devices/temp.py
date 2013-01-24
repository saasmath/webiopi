from ..utils  import route
from ..i2c import I2C


class TMP102(I2C):
    def __init__(self, addr=0b1001000):
        I2C.__init__(self, addr)
        
    @route("GET", "temperature")
    def getTemperature(self):
        d = bytearray(self.read(2))
        return int(((d[0] << 4) | (d[1] >> 4)) *0.625) / 10.0

__all__ = [TMP102]

