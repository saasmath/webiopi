from webiopi.devices.i2c import *
from webiopi.devices.sensor import Luminosity

class TSL2561(I2C, Luminosity):
    def __init__(self, slave=0b0111001):
        I2C.__init__(self, toint(slave), "TSL2561")

    def __getLux__(self):
        return 0

