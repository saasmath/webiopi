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
    def __init__(self, port=8000, coap_port=5683, login=None, password=None, passwdfile=None, configfile=None):
        self.handler = rest.RESTHandler()
        self.host = getLocalIP()

        http_port = port
        if http_port != None and http_port > 0:
            http_enabled = True
        else:
            http_enabled = False

        if coap_port != None and coap_port > 0:
            self.coap_enabled = True
            multicast = True
        else:
            self.coap_enabled = False
            multicast = False
        
        context = None
        docroot = None
        index = None
        auth = None

        if configfile != None and os.path.exists(configfile):
            info("Loading configuration from %s" % configfile)
            config = parser.ConfigParser()
            config.optionxform = str
            config.read(configfile)
            
            if config.has_section("SCRIPTS"):
                scripts = config.items("SCRIPTS")
                for (name, source) in scripts:
                    loadScript(name, source, self.handler)
            
            if config.has_section("HTTP"):
                if config.has_option("HTTP", "enabled"):
                    http_enabled = config.getboolean("HTTP", "enabled")
                if config.has_option("HTTP", "port"):
                    http_port = config.getint("HTTP", "port")
                if config.has_option("HTTP", "passwd-file"):
                    passwdfile = config.get("HTTP", "passwd-file")
                if config.has_option("HTTP", "doc-root"):
                    docroot = config.get("HTTP", "doc-root")
                if config.has_option("HTTP", "welcome-file"):
                    index = config.get("HTTP", "welcome-file")
                

            if config.has_section("COAP"):
                if config.has_option("COAP", "enabled"):
                    coap_enabled = config.getboolean("COAP", "enabled")
                if config.has_option("COAP", "port"):
                    coap_port = config.getint("COAP", "port")
                if config.has_option("COAP", "multicast"):
                    multicast = config.getboolean("COAP", "multicast")

            if config.has_section("SERIAL"):
                serials = config.items("SERIAL")
                for (name, params) in serials:
                    (device, speed) = params.split(" ")
                    speed = int(speed)
                    if speed > 0:
                        self.handler.addSerial(name, device, speed)
        
            if config.has_section("DEVICES"):
                devices = config.items("DEVICES")
                for (name, params) in devices:
                    values = params.split(" ")
                    self.handler.addDevice(name, values[0], values[1:])
        
        if passwdfile != None:
            if os.path.exists(passwdfile):
                f = open(passwdfile)
                auth = f.read().strip(" \r\n")
                f.close()
                if len(auth) > 0:
                    info("Access protected using %s" % passwdfile)
                else:
                    info("Passwd file %s is empty" % passwdfile)
            else:
                error("Passwd file %s not found" % passwdfile)
            
        elif login != None or password != None:
            auth = encodeAuth(login, password)
            info("Access protected using login/password")
            
        if auth == None or len(auth) == 0:
            warn("Access unprotected")
        
        if http_enabled:
            self.http_server = http.HTTPServer(self.host, http_port, self.handler, context, docroot, index, auth)
        else:
            self.http_server = None
        
        if coap_enabled:
            self.coap_server = coap.COAPServer(self.host, coap_port, self.handler)
            if multicast:
                self.coap_server.enableMulticast()
        else:
            self.coap_server = None
    
    def addMacro(self, macro):
        self.handler.addMacro(macro)
        
    def stop(self):
        if self.http_server:
            self.http_server.stop()
        if self.coap_server:
            self.coap_server.stop()
        self.handler.stop()



