#   Copyright 2012-2013 Eric Ptak - trouch.com
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from webiopi.i2c import I2C
from webiopi.onewire import OneWireTemperature
from webiopi.rest import route

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