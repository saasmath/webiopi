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

import time
from webiopi.rest import *
from webiopi.devices.i2c import *
from webiopi.devices.onewire import *

class Pressure():
    def __family__(self):
        return "Pressure"

    def __getPascal__(self):
        raise NotImplementedError
    
    @request("GET", "pressure/pa")
    @response("%d")
    def getPascal(self):
        return self.__getPascal__()
    
    @request("GET", "pressure/hpa")
    @response("%.2f")
    def getHectoPascal(self):
        return float(self.getPascal()) / 100.0

class Temperature():
    def __family__(self):
        return "Temperature"
    
    def __getCelsius__(self):
        raise NotImplementedError

    def __getFahrenheit__(self):
        raise NotImplementedError
    
    def Celsius2Fahrenheit(self):
        return 1.8*self.getCelsius() + 32

    def Fahrenheit2Celsius(self):
        return (self.getFahrenheit() - 32)/1.8

    @request("GET", "temperature/c")
    @response("%.02f")
    def getCelsius(self):
        return self.__getCelsius__()
    
    @request("GET", "temperature/f")
    @response("%.02f")
    def getFahrenheit(self):
        return self.__getFahrenheit__()
    

class TMP102(I2C, Temperature):
    def __init__(self, slave=0b1001000, name="TMP102"):
        I2C.__init__(self, toint(slave), name)
        
    def __getCelsius__(self):
        d = self.readBytes(2)
        count = ((d[0] << 4) | (d[1] >> 4)) & 0xFFF
        return signInteger(count, 12)*0.0625
    
    def __getFahrenheit__(self):
        return self.Celsius2Fahrenheit()

class TMP75(TMP102):
    def __init__(self, slave=0b1001000, resolution=12, name="TMP75"):
        TMP102.__init__(self, slave, name)
        resolution = toint(resolution)
        if not resolution in range(9,13):
            raise ValueError("%dbits resolution out of range [%d..%d]bits" % (resolution, 9, 12))
        self.resolution = resolution
        
        config  = self.readRegister(0x01)
        config &= ~0x60
        config |= (self.resolution - 9) << 5
        self.writeRegister(0x01, config)
        self.readRegisters(0x00, 2)

class TMP275(TMP75):
    def __init__(self, slave=0b1001000, resolution=12, name="TMP275"):
        TMP75.__init__(self, slave, resolution, name)


class OneWireTemp(OneWire, Temperature):
    def __init__(self, slave=None, family=0, name="1-Wire-Temp"):
        OneWire.__init__(self, slave, family, "TEMP", name)
        
    def __getCelsius__(self):
        data = self.read()
        lines = data.split("\n")
        if lines[0].endswith("YES"):
            i = lines[1].find("=")
            temp = lines[1][i+1:]
            return int(temp) / 1000.0
    
    def __getFahrenheit__(self):
        return self.Celsius2Fahrenheit()

class DS18S20(OneWireTemp):
    def __init__(self, slave=None):
        OneWireTemp.__init__(self, slave, 0x10, "DS18S20")
        
class DS1822(OneWireTemp):
    def __init__(self, slave=None):
        OneWireTemp.__init__(self, slave, 0x22, "DS1822")
        
class DS18B20(OneWireTemp):
    def __init__(self, slave=None):
        OneWireTemp.__init__(self, slave, 0x28, "DS18B20")
        
class DS1825(OneWireTemp):
    def __init__(self, slave=None):
        OneWireTemp.__init__(self, slave, 0x3B, "DS1825")
        
class DS28EA00(OneWireTemp):
    def __init__(self, slave=None):
        OneWireTemp.__init__(self, slave, 0x42, "DS28EA00")
        
class BMP085(I2C, Temperature, Pressure):
    def __init__(self, slave=0b1110111, name="BMP085"):
        I2C.__init__(self, toint(slave), name)
        self.ac1 = self.readSignedInteger(0xAA)
        self.ac2 = self.readSignedInteger(0xAC)
        self.ac3 = self.readSignedInteger(0xAE)
        self.ac4 = self.readUnsignedInteger(0xB0)
        self.ac5 = self.readUnsignedInteger(0xB2)
        self.ac6 = self.readUnsignedInteger(0xB4)
        self.b1  = self.readSignedInteger(0xB6)
        self.b2  = self.readSignedInteger(0xB8)
        self.mb  = self.readSignedInteger(0xBA)
        self.mc  = self.readSignedInteger(0xBC)
        self.md  = self.readSignedInteger(0xBE)
        
    def __family__(self):
        return [Temperature.__family__(self), Pressure.__family__(self)]

    def readUnsignedInteger(self, address):
        d = self.readRegisters(address, 2)
        return d[0] << 8 | d[1]
    
    def readSignedInteger(self, address):
        d = self.readUnsignedInteger(address)
        return signInteger(d, 16)
    
    def readUT(self):
        self.writeRegister(0xF4, 0x2E)
        time.sleep(0.01)
        return self.readUnsignedInteger(0xF6)

    def readUP(self):
        self.writeRegister(0xF4, 0x34)
        time.sleep(0.01)
        return self.readUnsignedInteger(0xF6)

    def getB5(self):
        ut = self.readUT()
        x1 = ((ut - self.ac6) * self.ac5) / 2**15
        x2 = (self.mc * 2**11) / (x1 + self.md)
        return x1 + x2
    
    def __getCelsius__(self):
        t = (self.getB5() + 8) / 2**4
        return float(t) / 10.0
    
    def __getFahrenheit__(self):
        return self.Celsius2Fahrenheit()

    def __getPascal__(self):
        b5 = self.getB5()
        up = self.readUP()
        b6 = b5 - 4000
        x1 = (self.b2 * (b6 * b6 / 2**12)) / 2**11
        x2 = self.ac2 * b6 / 2**11
        x3 = x1 + x2
        b3 = (self.ac1*4 + x3 + 2) / 4
        
        x1 = self.ac3 * b6 / 2**13
        x2 = (self.b1 * (b6 * b6 / 2**12)) / 2**16
        x3 = (x1 + x2 + 2) / 2**2
        b4 = self.ac4 * (x3 + 32768) / 2**15
        b7 = (up-b3) * 50000
        if b7 < 0x80000000:
            p = (b7 * 2) / b4
        else:
            p = (b7 / b4) * 2
        
        x1 = (p / 2**8) * (p / 2**8)
        x1 = (x1 * 3038) / 2**16
        x2 = (-7357*p) /  2**16
        p = p + (x1 + x2 + 3791) / 2**4
        return int(p)
