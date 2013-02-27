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

from webiopi.utils import LOGGER, PYTHON_MAJOR
from webiopi.protocols.coap import COAPClient, COAPGet, COAPPost, COAPPut, COAPDelete

if PYTHON_MAJOR >= 3:
    import http.client as httplib
else:
    import httplib

class PiMixedClient():
    def __init__(self, host, port=8000, coap=5683):
        self.host = host
        self.coapport = coap
        self.coapclient = COAPClient()
        if port > 0:
            self.httpclient = httplib.HTTPConnection(host, port)
        else:
            self.httpclient = None
        self.forceHttp = False
        self.coapfailure = 0
        self.maxfailure = 2
        
    def sendRequest(self, method, uri):
        if not self.forceHttp or self.httpclient == None:
            if method == "GET":
                response = self.coapclient.sendRequest(COAPGet("coap://%s:%d%s" % (self.host, self.coapport, uri)))
            elif method == "POST":
                response = self.coapclient.sendRequest(COAPPost("coap://%s:%d%s" % (self.host, self.coapport, uri)))

            if response:
                return response.payload
            elif self.httpclient:
                self.coapfailure += 1
                print("No CoAP response, fall-back to HTTP")
                if (self.coapfailure > self.maxfailure):
                    self.forceHttp = True
                    self.coapfailure = 0
                    print("Too many CoAP failure forcing HTTP")
            else:
                return None

        self.httpclient.request(method, uri)
        response = self.httpclient.getresponse()
        if response:
            data = response.read()
            return data
        return None

class PiHttpClient(PiMixedClient):
    def __init__(self, host, port=8000):
        PiMixedClient.__init__(self, host, port, -1)

class PiCoapClient(PiMixedClient):
    def __init__(self, host, port=5683):
        PiMixedClient.__init__(self, host, -1, port)

class PiMulticastClient(PiMixedClient):
    def __init__(self, port=5683):
        PiMixedClient.__init__(self, "224.0.1.123", -1, port)

class Device():
    def __init__(self, client, name):
        self.client = client
        self.path = "/devices/" + name
    
    def sendRequest(self, method, path):
        return self.client.sendRequest(method, self.path + path)
    

class GPIO(Device):
    def getFunction(self, channel):
        return self.sendRequest("GET", "/%d/function" % channel)

    def setFunction(self, channel, func):
        return self.sendRequest("POST", "/%d/function/%s" % (channel, func))
        
    def input(self, channel):
        return int(self.sendRequest("GET", "/%d/value" % channel))

    def output(self, channel, value):
        return int(self.sendRequest("POST", "/%d/value/%d" % (channel, value)))
    
    def readInteger(self):
        return int(self.sendRequest("GET", "/integer"))

    def writeInteger(self, value):
        return int(self.sendRequest("POST", "/integer/%d" % value))

class NativeGPIO(GPIO):
    def __init__(self, client):
        Device.__init__(self, client, "")
        self.path = "/GPIO"

class ADC(Device):
    def readFloat(self, channel):
        return float(self.sendRequest("GET", "/%d/float" % channel))

class DAC(ADC):
    def writeFloat(self, channel, value):
        return float(self.sendRequest("POST", "/%d/float/%f" % (channel, value)))
                     
class PWM(DAC):
    def writeAngle(self, channel, value):
        return float(self.sendRequest("POST", "/%d/angle/%f" % (channel, value)))
                     
class Temperature(Device):
    def getCelsius(self):
        return float(self.sendRequest("GET", "/temperature/c"))

    def getFahrenheit(self):
        return float(self.sendRequest("GET", "/temperature/f"))
    
class Pressure(Device):
    def getPascal(self):
        return float(self.sendRequest("GET", "/pressure/pa"))

    def getHectoPascal(self):
        return float(self.sendRequest("GET", "/pressure/hpa"))
    
class Luminosity(Device):
    def getLux(self):
        return float(self.sendRequest("GET", "/luminosity/lux"))
    
class Distance(Device):
    def getMillimeter(self):
        return float(self.sendRequest("GET", "/distance/mm"))

    def getCentimeter(self):
        return float(self.sendRequest("GET", "/distance/cm"))

    def getInch(self):
        return float(self.sendRequest("GET", "/distance/in"))

