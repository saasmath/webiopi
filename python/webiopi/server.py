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

import os
from webiopi.utils import *
from webiopi import rest
from webiopi import coap
from webiopi import http
from webiopi.devices.gpio import GPIODriver

if PYTHON_MAJOR >= 3:
    import configparser as parser
else:
    import ConfigParser as parser

class Server():
    def __init__(self, port=8000, coap_port=5683, login=None, password=None, passwdfile=None, configfile=None):
        self.host = getLocalIP()
        self.gpioDriver = GPIODriver()
        self.restHandler = rest.RESTHandler()
        self.restHandler.addDeviceInstance("GPIO", self.gpioDriver, [])

        http_port = port
        if http_port != None and http_port > 0:
            http_enabled = True
        else:
            http_enabled = False

        if coap_port != None and coap_port > 0:
            coap_enabled = True
            multicast = True
        else:
            coap_enabled = False
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
            
            if config.has_section("GPIO"):
                gpios = config.items("GPIO")
                for (gpio, params) in gpios:
                    addGPIOSetup(gpio, params)
            
            if config.has_section("~GPIO"):
                gpios = config.items("~GPIO")
                for (gpio, params) in gpios:
                    addGPIOReset(gpio, params)
            
            GPIOSetup()
            
            if config.has_section("SCRIPTS"):
                scripts = config.items("SCRIPTS")
                for (name, source) in scripts:
                    loadScript(name, source, self.restHandler)
            
            if config.has_section("REST"):
                if config.has_option("REST", "gpio-export"):
                    exports = config.get("REST", "gpio-export")
                    self.gpioDriver.export = [int(i) for i in exports.split(",")]
                    self.restHandler.gpioExport = self.gpioDriver.export
                if config.has_option("REST", "gpio-post-value"):
                    self.gpioDriver.post_value = config.getboolean("REST", "gpio-post-value")
                if config.has_option("REST", "gpio-post-function"):
                    self.gpioDriver.post_function = config.getboolean("REST", "gpio-post-function")
                if config.has_option("REST", "device-mapping"):
                    self.restHandler.device_mapping = config.getboolean("REST", "device-mapping")
            
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

            if config.has_section("DEVICES"):
                devices = config.items("DEVICES")
                for (name, params) in devices:
                    values = params.split(" ")
                    self.restHandler.addDevice(name, values[0], values[1:])
                    
            if config.has_section("ROUTES"):
                routes = config.items("ROUTES")
                for (source, destination) in routes:
                    self.restHandler.addRoute(source, destination)
        
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
            self.http_server = http.HTTPServer(self.host, http_port, self.restHandler, context, docroot, index, auth)
        else:
            self.http_server = None
        
        if coap_enabled:
            self.coap_server = coap.COAPServer(self.host, coap_port, self.restHandler)
            if multicast:
                self.coap_server.enableMulticast()
        else:
            self.coap_server = None
    
    def addMacro(self, macro):
        self.restHandler.addMacro(macro)
        
    def stop(self):
        if self.http_server:
            self.http_server.stop()
        if self.coap_server:
            self.coap_server.stop()
        self.restHandler.stop()



