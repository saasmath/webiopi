import os
from webiopi import rest
from webiopi import coap
from webiopi import http
from webiopi.utils import *

if PYTHON_MAJOR >= 3:
    import configparser as parser
else:
    import ConfigParser as parser

class Server():
    def __init__(self, port=8000, context="webiopi", index="index.html", login=None, password=None, passwdfile=None, coap_port=5683, configfile=None):
        self.handler = rest.RESTHandler()
        self.host = getLocalIP()
        self.http_port = port
        if port == None:
            self.http_enabled = False
        else:
            self.http_enabled = True

        self.context = context
        self.index = index
        self.auth = None
        
        self.coap_port = coap_port
        if coap_port == None:
            self.coap_enabled = False
            multicast = False
        else:
            self.coap_enabled = True
            multicast = True
        
        if configfile != None and os.path.exists(configfile):
            info("Loading configuration from %s" % configfile)
            config = parser.ConfigParser()
            config.optionxform = str
            config.read(configfile)
            
            if config.has_section("HTTP"):
                self.http_enabled = config.getboolean("HTTP", "enabled")
                self.http_port = config.getint("HTTP", "port")
                passwdfile = config.get("HTTP", "passwd-file")

            if config.has_section("COAP"):
                self.coap_enabled = config.getboolean("COAP", "enabled")
                self.coap_port = config.getint("COAP", "port")
                multicast = config.getboolean("COAP", "multicast")

            if config.has_section("SERIAL"):
                serials = config.items("SERIAL")
                for (name, params) in serials:
                    (device, speed) = params.split(" ")
                    speed = int(speed)
                    if speed > 0:
                        self.handler.addSerial(name, device, speed)
        
            if config.has_section("DEVICES"):
                serials = config.items("DEVICES")
                for (name, params) in serials:
                    values = params.split(" ")
                    self.handler.addDevice(name, values[0], values[1:])
        
        if passwdfile != None:
            if os.path.exists(passwdfile):
                f = open(passwdfile)
                self.auth = f.read().strip(" \r\n")
                f.close()
                if len(self.auth) > 0:
                    info("Access protected using %s" % passwdfile)
                else:
                    info("Passwd file %s is empty" % passwdfile)
            else:
                error("Passwd file %s not found" % passwdfile)
            
        elif login != None or password != None:
            self.auth = encodeAuth(login, password)
            info("Access protected using login/password")
            
        if self.auth == None or len(self.auth) == 0:
            warn("Access unprotected")
            
        if not self.context.startswith("/"):
            self.context = "/" + self.context
        if not self.context.endswith("/"):
            self.context += "/"

        if self.http_enabled:
            self.http_server = http.HTTPServer(self.host, self.http_port, self.context, self.index, self.handler, self.auth)
        else:
            self.http_server = None
        
        if self.coap_enabled:
            self.coap_server = coap.COAPServer(self.host, self.coap_port, self.handler)
            if multicast:
                self.coap_server.enableMulticast()
        else:
            self.coap_server = None
    
    def addMacro(self, callback):
        self.handler.addMacro(callback)
        
    def stop(self):
        if self.http_server:
            self.http_server.stop()
        if self.coap_server:
            self.coap_server.stop()
        self.handler.stop()

