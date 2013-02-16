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

from webiopi.protocols.rest import *

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
    
class Luminosity():
    def __family__(self):
        return "Luminosity"
    
    def __getLux__(self):
        raise NotImplementedError

    @request("GET", "luminosity/lx")
    @response("%.02f")
    def getLux(self):
        return self.__getLux__()
    

from webiopi.devices.sensor.bmp085 import BMP085
from webiopi.devices.sensor.onewiretemp import DS1822, DS1825, DS18B20, DS18S20, DS28EA00
from webiopi.devices.sensor.tmpXXX import TMP75, TMP102, TMP275
from webiopi.devices.sensor.tsl2561 import TSL2561
