from webiopi.i2c import I2C
from webiopi.rest import route
from webiopi.onewire import *

class TMPXXX(I2C):
    def __init__(self, slave=0b1001000, name="TMPXXX"):
        I2C.__init__(self, slave, name)
        
    @route("GET", "temperature", "%.02f")
    def getTemperature(self):
        d = self.readBytes(2)
        return ((d[0] << 4) | (d[1] >> 4)) *0.0625

class TMP075(TMPXXX):
    def __init__(self, slave=0b1001000):
        TMPXXX.__init__(self, slave, "TMP075")

class TMP102(TMPXXX):
    def __init__(self, slave=0b1001000):
        TMPXXX.__init__(self, slave, "TMP102")

class TMP275(TMPXXX):
    def __init__(self, slave=0b1001000):
        TMPXXX.__init__(self, slave, "TMP275")

class DS18B20(OneWireTemperature):
    def __init__(self, slave=None):
        OneWireTemperature.__init__(self, slave, 0x28, "DS18B20")