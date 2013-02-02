from webiopi.coap import COAPClient, COAPGet, COAPPost, COAPPut, COAPDelete
from webiopi.utils import LOGGER, PYTHON_MAJOR

if PYTHON_MAJOR >= 3:
    import http.client as httplib
else:
    import httplib

class Client():
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

    def getFunction(self, channel):
        return self.sendRequest("GET", "/GPIO/%d/function" % channel)

    def setFunction(self, channel, func):
        return self.sendRequest("POST", "/GPIO/%d/function/%s" % (channel, func))
        
    def input(self, channel):
        return int(self.sendRequest("GET", "/GPIO/%d/value" % channel))

    def output(self, channel, value):
        return self.sendRequest("POST", "/GPIO/%d/value/%d" % (channel, value))

class MulticastClient(Client):
    def __init__(self, port=5683):
        Client.__init__(self, "224.0.1.123", -1, port)
