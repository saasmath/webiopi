#!/usr/bin/python

#   Copyright 2012 Eric Ptak - trouch.com
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
import sys
import time
import errno
import signal
import socket
import struct
import threading

import mimetypes as mime
import re
import base64
import codecs
import hashlib


try :
    import _webiopi.GPIO as GPIO
except:
    pass

PYTHON_MAJOR = sys.version_info.major

if PYTHON_MAJOR >= 3:
    from urllib.parse import urlparse
    import http.client as httplib
    import http.server as BaseHTTPServer
    import configparser as parser
else:
    from urlparse import urlparse
    import httplib
    import BaseHTTPServer
    import ConfigParser as parser

VERSION = '0.5.3'
SERVER_VERSION = "WebIOPi/Python%d/%s" % (PYTHON_MAJOR, VERSION)

FUNCTIONS = {
    "I2C0": {"enabled": False, "gpio": {0:"SDA", 1:"SCL"}},
    "I2C1": {"enabled": True, "gpio": {2:"SDA", 3:"SCL"}},
    "SPI0": {"enabled": False, "gpio": {7:"CE1", 8:"CE0", 9:"MISO", 10:"MOSI", 11:"SCLK"}},
    "UART0": {"enabled": True, "gpio": {14:"TX", 15:"RX"}}
}

MAPPING = [[], [], []]
MAPPING[1] = ["V33", "V50", 0, "V50", 1, "GND", 4, 14, "GND", 15, 17, 18, 21, "GND", 22, 23, "V33", 24, 10, "GND", 9, 25, 11, 8, "GND", 7]
MAPPING[2] = ["V33", "V50", 2, "V50", 3, "GND", 4, 14, "GND", 15, 17, 18, 27, "GND", 22, 23, "V33", 24, 10, "GND", 9, 25, 11, 8, "GND", 7]

M_PLAIN = "text/plain"
M_JSON  = "application/json"

__running__ = False
    
def runLoop(func=None):
    global __running__
    __running__ = True
    if func != None:
        while __running__:
            func()
    else:
        while __running__:
            time.sleep(1)

def __signalHandler__(sig, func=None):
    global __running__
    __running__ = False

def encodeAuth(login, password):
    abcd = "%s:%s" % (login, password)
    if PYTHON_MAJOR >= 3:
        b = base64.b64encode(abcd.encode())
    else:
        b = base64.b64encode(abcd)
    return hashlib.sha256(b).hexdigest()

def log(message):
    print("%s %s" % (SERVER_VERSION, message))

def warn(message):
    log("Warning - %s" % message)

def error(message):
    log("Error - %s" % message)

def printBytes(bytes):
    for i in range(0, len(bytes)):
        print("%03d: 0x%02X %03d %c" % (i, bytes[i], bytes[i], bytes[i]))

def getLocalIP():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 53))
            (host, p) = s.getsockname()
            s.close()
            return host 
        except (socket.error, e):
            return "localhost"

class Server():
    def __init__(self, port=8000, context="webiopi", index="index.html", login=None, password=None, passwdfile=None, coap=5683, configfile=None):
        self.log_enabled = False
        self.handler = RESTHandler()
        self.host = getLocalIP()
        self.http_port = port
        if port == None:
            self.http_enabled = False
        else:
            self.http_enabled = True

        self.context = context
        self.index = index
        self.auth = None
        
        self.coap_port = coap
        if coap == None:
            self.coap_enabled = False
            multicast = False
        else:
            self.coap_enabled = True
            multicast = True
        
        if configfile != None:
            config = parser.ConfigParser()
            config.read(configfile)
            self.http_enabled = config.getboolean("HTTP", "enabled")
            self.http_port = config.getint("HTTP", "port")
            passwdfile = config.get("HTTP", "passwd-file")
            self.coap_enabled = config.getboolean("COAP", "enabled")
            self.coap_port = config.getint("COAP", "port")
            multicast = config.getboolean("COAP", "multicast")
        
        if passwdfile != None:
            if os.path.exists(passwdfile):
                f = open(passwdfile)
                self.auth = f.read().strip(" \r\n")
                f.close()
                if len(self.auth) > 0:
                    log("Access protected using %s" % passwdfile)
                else:
                    log("Passwd file is empty : %s" % passwdfile)
            else:
                error("Passwd file not found : %s" % passwdfile)
            
        elif login != None or password != None:
            self.auth = encodeAuth(login, password)
            log("Access protected using login/password")
            
        if self.auth == None or len(self.auth) == 0:
            warn("Access unprotected")
            
        if not self.context.startswith("/"):
            self.context = "/" + self.context
        if not self.context.endswith("/"):
            self.context += "/"

        if self.http_enabled:
            self.http_server = HTTPServer(self.host, self.http_port, self.context, self.index, self.handler, self.auth)
            self.http_server.log_enabled = self.log_enabled
        else:
            self.http_server = None
        
        if self.coap_enabled:
            self.coap_server = COAPServer(self.host, self.coap_port, self.handler)
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

class HTTPServer(BaseHTTPServer.HTTPServer, threading.Thread):
    def __init__(self, host, port, context, index, handler, auth=None):
        BaseHTTPServer.HTTPServer.__init__(self, ("", port), HTTPHandler)
        threading.Thread.__init__(self)

        self.docroot = "/usr/share/webiopi/htdocs"
        self.log_enabled = False
        self.host = host
        self.port = port
        self.context = context
        self.index = index
        self.handler = handler
        self.auth = auth

        self.start()
            
    def run(self):
        log("HTTP Server binded on http://%s:%s%s" % (self.host, self.port, self.context))
        self.running = True
        try:
            self.serve_forever()
        except Exception as e:
            if self.running:
                error("%s" % e)
        log("HTTP Server stopped")

    def stop(self):
        self.running = False
        self.server_close()

class RESTHandler():
    def __init__(self):
        self.callbacks = {}

    def addMacro(self, callback):
        self.callbacks[callback.__name__] = callback

    def getJSON(self):
        json = "{"
        first = True
        for (alt, value) in FUNCTIONS.items():
            if not first:
                json += ", "
            json += '"%s": %d' % (alt, value["enabled"])
            first = False
        
        json += ', "GPIO":{\n'
        first = True
        for gpio in range(GPIO.GPIO_COUNT):
            if not first:
                json += ", \n"

            function = GPIO.getFunctionString(gpio)
            value = GPIO.input(gpio)
                    
            json += '"%d": {"function": "%s", "value": %d' % (gpio, function, value)
            if GPIO.getFunction(gpio) == GPIO.PWM:
                (type, value) = GPIO.getPulse(gpio).split(':')
                json  += ', "%s": %s' %  (type, value)
            json += '}'
            first = False
            
        json += "\n}}"
        return json

    def do_GET(self, relativePath):
        # JSON full state
        if relativePath == "*":
            return (200, self.getJSON(), M_JSON)
            
        # RPi header map
        elif relativePath == "map":
            json = "%s" % MAPPING[GPIO.BOARD_REVISION]
            json = json.replace("'", '"')
            return (200, json, M_JSON)

        # server version
        elif relativePath == "version":
            return (200, SERVER_VERSION, M_PLAIN)

        # board revision
        elif relativePath == "revision":
            revision = "%s" % GPIO.BOARD_REVISION
            return (200, revision, M_PLAIN)

        # Single GPIO getter
        elif relativePath.startswith("GPIO/"):
            (mode, s_gpio, operation) = relativePath.split("/")
            gpio = int(s_gpio)

            value = None
            if operation == "value":
                if GPIO.input(gpio):
                    value = "1"
                else:
                    value = "0"
    
            elif operation == "function":
                value = GPIO.getFunctionString(gpio)
    
            elif operation == "pwm":
                if GPIO.isPWMEnabled(gpio):
                    value = "enabled"
                else:
                    value = "disabled"
                
            elif operation == "pulse":
                value = GPIO.getPulse(gpio)
                
            else:
                return (404, operation + " Not Found", M_PLAIN)
                
            return (200, value, M_PLAIN)

        else:
            return (0, None, None)

    def do_POST(self, relativePath):
        if relativePath.startswith("GPIO/"):
            (mode, s_gpio, operation, value) = relativePath.split("/")
            gpio = int(s_gpio)
            
            if operation == "value":
                if value == "0":
                    GPIO.output(gpio, GPIO.LOW)
                elif value == "1":
                    GPIO.output(gpio, GPIO.HIGH)
                else:
                    return (400, "Bad Value", M_PLAIN)
    
                return (200, value, M_PLAIN)

            elif operation == "function":
                value = value.lower()
                if value == "in":
                    GPIO.setFunction(gpio, GPIO.IN)
                elif value == "out":
                    GPIO.setFunction(gpio, GPIO.OUT)
                elif value == "pwm":
                    GPIO.setFunction(gpio, GPIO.PWM)
                else:
                    return (400, "Bad Function", M_PLAIN)

                value = GPIO.getFunctionString(gpio)
                return (200, value, M_PLAIN)

            elif operation == "sequence":
                (period, sequence) = value.split(",")
                period = int(period)
                GPIO.outputSequence(gpio, period, sequence)
                return (200, sequence[-1], M_PLAIN)
                
            elif operation == "pwm":
                if value == "enable":
                    GPIO.enablePWM(gpio)
                elif value == "disable":
                    GPIO.disablePWM(gpio)
                
                if GPIO.isPWMEnabled(gpio):
                    result = "enabled"
                else:
                    result = "disabled"
                
                return (200, result, M_PLAIN)
                
            elif operation == "pulse":
                GPIO.pulse(gpio)
                return (200, "OK", M_PLAIN)
                
            elif operation == "pulseRatio":
                ratio = float(value)
                GPIO.pulseRatio(gpio, ratio)
                return (200, value, M_PLAIN)
                
            elif operation == "pulseAngle":
                angle = float(value)
                GPIO.pulseAngle(gpio, angle)
                return (200, value, M_PLAIN)
                
            else: # operation unknown
                return (404, operation + " Not Found", M_PLAIN)
                
        elif relativePath.startswith("macros/"):
            (mode, fname, value) = relativePath.split("/")
            if fname in self.callbacks:
                callback = self.callbacks[fname]

                if ',' in value:
                    args = value.split(',')
                    result = callback(*args)
                elif len(value) > 0:
                    result = callback(value)
                else:
                    result = callback()
                     
                response = ""
                if result:
                    response = "%s" % result
                return (200, response, M_PLAIN)
                    
            else:
                return (404, fname + " Not Found", M_PLAIN)
                
        else: # path unknowns
            return (0, None, None)
        
class HTTPHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        if self.server.log_enabled:
            log(format % args)

    def version_string(self):
        return SERVER_VERSION + ' ' + self.sys_version
    
    def checkAuthentication(self):
        if self.server.auth == None or len(self.server.auth) == 0:
            return True
        
        authHeader = self.headers.get('Authorization')
        if authHeader == None:
            return False
        
        if not authHeader.startswith("Basic "):
            return False
        
        auth = authHeader.replace("Basic ", "")
        if PYTHON_MAJOR >= 3:
            hash = hashlib.sha256(auth.encode()).hexdigest()
        else:
            hash = hashlib.sha256(auth).hexdigest()
            
        if hash == self.server.auth:
            return True
        return False

    def requestAuthentication(self):
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="webiopi"')
        self.end_headers();
    
    def sendResponse(self, code, body=None, type="text/plain"):
        if code >= 400:
            if body != None:
                self.send_error(code, body)
            else:
                self.send_error(code)
        else:
            self.send_response(code)
            self.send_header("Content-type", type);
            self.end_headers();
            self.wfile.write(body.encode())
            
    def serveFile(self, relativePath):
        if relativePath == "":
            relativePath = self.server.index
                        
        realPath = relativePath;
        
        if not os.path.exists(realPath):
            realPath = self.server.docroot + os.sep + relativePath
            
        if not os.path.exists(realPath):
            return self.sendResponse(404, "Not Found")

        realPath = os.path.realpath(realPath)
        
        if realPath.endswith(".py"):
            return self.sendResponse(403, "Not Authorized")
        
        if not (realPath.startswith(self.server.docroot) or realPath.startswith(os.getcwd())):
            return self.sendResponse(403, "Not Authorized")
            
        if os.path.isdir(realPath):
            realPath += os.sep + self.server.index;
            if not os.path.exists(realPath):
                return self.sendResponse(403, "Not Authorized")
            
        (type, encoding) = mime.guess_type(realPath)
        f = codecs.open(realPath, encoding=encoding)
        data = f.read()
        f.close()
        self.send_response(200)
        self.send_header("Content-type", type);
#            self.send_header("Content-length", os.path.getsize(realPath))
        self.end_headers()
        self.wfile.write(data)
        
    def processRequest(self):
        if not self.checkAuthentication():
            return self.requestAuthentication()
        
        relativePath = self.path.replace(self.server.context, "/")
        if relativePath.startswith("/"):
            relativePath = relativePath[1:];

        try:
            result = (None, None, None)
            if self.command == "GET":
                result = self.server.handler.do_GET(relativePath)
            elif self.command == "POST":
                result = self.server.handler.do_POST(relativePath)
            else:
                result = (405, None, None)
                
            (code, body, type) = result
            
            if code > 0:
                self.sendResponse(code, body, type)
            else:
                if self.command == "GET":
                    self.serveFile(relativePath)
                else:
                    self.sendResponse(404)

        except (GPIO.InvalidDirectionException, GPIO.InvalidChannelException, GPIO.SetupException) as e:
            self.sendResponse(403, "%s" % e)
        except Exception as e:
            self.sendResponse(500)
            raise e
            
    def do_GET(self):
        self.processRequest()

    def do_POST(self):
        self.processRequest()

class COAPOption():
    OPTIONS = {1: "If-Match",
               3: "Uri-Host",
               4: "ETag",
               5: "If-None-Match",
               7: "Uri-Port",
               8: "Location-Path",
               11: "Uri-Path",
               12: "Content-Format",
               14: "Max-Age",
               15: "Uri-Query",
               16: "Accept",
               20: "Location-Query",
               35: "Proxy-Uri",
               39: "Proxy-Scheme"
               }
    
    IF_MATCH = 1
    URI_HOST = 3
    ETAG = 4
    IF_NONE_MATCH = 5
    URI_PORT = 7
    LOCATION_PATH = 8
    URI_PATH = 11
    CONTENT_FORMAT = 12
    MAX_AGE = 14
    URI_QUERY = 15
    ACCEPT = 16
    LOCATION_QUERY = 20
    PROXY_URI = 35
    PROXY_SCHEME = 39
    
    
class COAPMessage():
    TYPES = ["CON", "NON", "ACK", "RST"]
    CON = 0
    NON = 1
    ACK = 2
    RST = 3

    def __init__(self, type=0, code=0, uri=None):
        self.version = 1
        self.type    = type
        self.code    = code
        self.id      = 0
        self.token   = None
        self.options = []
        self.host    = ""
        self.port    = 5683
        self.uri_path = ""
        self.payload = None
        
        if uri != None:
            p = urlparse(uri)
            self.host = p.hostname
            if p.port:
                self.port = int(p.port)
            self.uri_path = p.path
        
    def __getOptionHeader__(self, byte):
        delta  = (byte & 0xF0) >> 4
        length = byte & 0x0F
        return (delta, length)  
        
    def printString(self):
        print("Version: %s" % self.version)
        print("Type: %s" % self.TYPES[self.type])
        print("code: %s" % self.CODES[self.code])
        print("Id: %s" % self.id)
        print("Token: %s" % self.token)
        print("Options: %s" % len(self.options))
        for option in self.options:
            print("+ %d: %s" % (option["number"], option["value"]))
        
        print("Uri-Path: %s" % self.uri_path)
        print("Payload: %s" % self.payload)
        print("")
        
    def getOptionHeaderValue(self, value):
        if value > 268:
            return 14
        if value > 12:
            return 13
        return value
    
    def getOptionHeaderExtension(self, value):
        buff = bytearray()
        v = self.getOptionHeaderValue(value)
        
        if v == 14:
            value -= 269
            buff.append((value & 0xFF00) >> 8)
            buff.append(value & 0x00FF)

        elif v == 13:
            value -= 13
            buff.append(value)

        return buff
    
    def appendOption(self, buff, lastnumber, option, data):
        delta = option - lastnumber
        length = len(data)
        
        d = self.getOptionHeaderValue(delta)
        l = self.getOptionHeaderValue(length)
        
        b  = 0
        b |= (d << 4) & 0xF0  
        b |= l & 0x0F
        buff.append(b)
        
        ext = self.getOptionHeaderExtension(delta);
        for b in ext:
            buff.append(b)

        ext = self.getOptionHeaderExtension(length);
        for b in ext:
            buff.append(b)

        for b in data:
            buff.append(b)

        return option

    def getBytes(self):
        buff = bytearray()
        byte  = (self.version & 0x03) << 6
        byte |= (self.type & 0x03) << 4
        if self.token:
            token_len = min(len(self.token), 8);
        else:
            token_len = 0
        byte |= token_len
        buff.append(byte)
        buff.append(self.code)
        buff.append((self.id & 0xFF00) >> 8)
        buff.append(self.id & 0x00FF)
        
        if self.token:
            for c in self.token:
                buff.append(c)

        lastnumber = 0
        
        if len(self.uri_path) > 0:
            paths = self.uri_path.split("/")
            for p in paths:
                if len(p) > 0:
                    if PYTHON_MAJOR >= 3:
                        data = p.encode()
                    else:
                        data = bytearray(p)
                    lastnumber = self.appendOption(buff, lastnumber, COAPOption.URI_PATH, data)
            
        buff.append(0xFF)
        
        if self.payload:
            if PYTHON_MAJOR >= 3:
                data = self.payload.encode()
            else:
                data = bytearray(self.payload)
            for c in data:
                buff.append(c)
        
        return buff
    
    def parseByteArray(self, bytes):
        self.version = (bytes[0] & 0xC0) >> 6
        self.type    = (bytes[0] & 0x30) >> 4
        token_length = bytes[0] & 0x0F
        index = 4
        if token_length > 0:
            self.token = bytes[index:index+token_length]

        index += token_length
        self.code    = bytes[1]
        self.id      = (bytes[2] << 8) | bytes[3]
        
        number = 0

        # process options
        while index < len(bytes) and bytes[index] != 0xFF:
            (delta, length) = self.__getOptionHeader__(bytes[index])
            offset = 1

            # delta extended with 1 byte
            if delta == 13:
                delta += bytes[index+offset]
                offset += 1
            # delta extended with 2 bytes
            elif delta == 14:
                delta += 255 + ((bytes[index+offset] << 8) | bytes[index+offset+1])
                offset += 2
            
            # length extended with 1 byte
            if length == 13:
                length += bytes[index+offset]
                offset += 1
                
            # length extended with 2 bytes
            elif length == 14:
                length += 255 + ((bytes[index+offset] << 8) | bytes[index+offset+1])
                offset += 2

            number += delta
            valueBytes = bytes[index+offset:index+offset+length]
            # opaque option value
            if number in [COAPOption.IF_MATCH, COAPOption.ETAG]:
                value = valueBytes
            # integer option value
            elif number in [COAPOption.URI_PORT, COAPOption.CONTENT_FORMAT, COAPOption.MAX_AGE, COAPOption.ACCEPT]:
                value = 0
                for b in valueBytes:
                    value <<= 8
                    value |= b
            # string option value
            else:
                if PYTHON_MAJOR >= 3:
                    value = valueBytes.decode()
                else:
                    value = str(valueBytes)
            self.options.append({'number': number, 'value': value})
            index += offset + length

        index += 1 # skip 0xFF / end-of-options
        
        if len(bytes) > index:
            self.payload = bytes[index:]
        
        for option in self.options:
            (number, value) = option.values()
            if number == COAPOption.URI_PATH:
                self.uri_path += "/%s" % value


class COAPRequest(COAPMessage):
    CODES = {0: None,
             1: "GET",
             2: "POST",
             3: "PUT",
             4: "DELETE"
             }

    GET    = 1
    POST   = 2
    PUT    = 3
    DELETE = 4

    def __init__(self, type=0, code=0, uri=None):
        COAPMessage.__init__(self, type, code, uri)

class COAPGet(COAPRequest):
    def __init__(self, uri):
        COAPRequest.__init__(self, COAPMessage.CON, COAPRequest.GET, uri)

class COAPPost(COAPRequest):
    def __init__(self, uri):
        COAPRequest.__init__(self, COAPMessage.CON, COAPRequest.POST, uri)

class COAPPut(COAPRequest):
    def __init__(self, uri):
        COAPRequest.__init__(self, COAPMessage.CON, COAPRequest.PUT, uri)

class COAPDelete(COAPRequest):
    def __init__(self, uri):
        COAPRequest.__init__(self, COAPMessage.CON, COAPRequest.DELETE, uri)

class COAPResponse(COAPMessage):    
    CODES = {0: None,
             64: "2.00 OK",
             65: "2.01 Created",
             66: "2.02 Deleted",
             67: "2.03 Valid",
             68: "2.04 Changed",
             69: "2.05 Content",
             128: "4.00 Bad Request",
             129: "4.01 Unauthorized",
             130: "4.02 Bad Option",
             131: "4.03 Forbidden",
             132: "4.04 Not Found",
             133: "4.05 Method Not Allowed",
             134: "4.06 Not Acceptable",
             140: "4.12 Precondition Failed",
             141: "4.13 Request Entity Too Large",
             143: "4.15 Unsupported Content-Format",
             160: "5.00 Internal Server Error",
             161: "5.01 Not Implemented",
             162: "5.02 Bad Gateway",
             163: "5.03 Service Unavailable",
             164: "5.04 Gateway Timeout",
             165: "5.05 Proxying Not Supported"            
            }

    # 2.XX
    OK      = 64
    CREATED = 65
    DELETED = 66
    VALID   = 67
    CHANGED = 68
    CONTENT = 69
    
     # 4.XX
    BAD_REQUEST         = 128
    UNAUTHORIZED        = 129
    BAD_OPTION          = 130
    FORBIDDEN           = 131
    NOT_FOUND           = 132
    NOT_ALLOWED         = 133
    NOT_ACCEPTABLE      = 134
    PRECONDITION_FAILED = 140
    ENTITY_TOO_LARGE    = 141
    UNSUPPORTED_CONTENT = 143
    
    # 5.XX
    INTERNAL_ERROR          = 160
    NOT_IMPLEMENTED         = 161
    BAD_GATEWAY             = 162
    SERVICE_UNAVAILABLE     = 163
    GATEWAY_TIMEOUT         = 164
    PROXYING_NOT_SUPPORTED  = 165
    
    def __init__(self):
        COAPMessage.__init__(self)

class COAPClient():
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(1.0)
        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        
    def sendRequest(self, message):
        data = message.getBytes();
        sent = 0
        while sent<4:
            try:
                self.socket.sendto(data, (message.host, message.port))
                data = self.socket.recv(1500)
                response = COAPResponse()
                response.parseByteArray(bytearray(data))
                return response
            except socket.timeout:
                sent+=1
        return None

class COAPServer(threading.Thread):
    def __init__(self, host, port, handler):
        threading.Thread.__init__(self)
        self.handler = COAPHandler(handler)
        self.host = host
        self.port = port
        self.multicast_ip = '224.0.1.123'
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', port))
        self.socket.settimeout(1)
        self.running = False
        self.start()
        
    def run(self):
        log("CoAP Server binded on coap://%s:%s/" % (self.host, self.port))
        self.running = True
        while self.running == True:
            try:
                (request, client) = self.socket.recvfrom(1500)
            except Exception as e:
                continue
            
#            log("Parsing request...")
            requestBytes = bytearray(request)
#            printBytes(requestBytes)
            coapRequest = COAPRequest()
            coapRequest.parseByteArray(requestBytes)
            
#            log("Processing request...")
#            coapRequest.printString()
            coapResponse = COAPResponse()
            self.processMessage(coapRequest, coapResponse)
            
#            log("Sending response...")
#            coapResponse.printString()
            responseBytes = coapResponse.getBytes()
#            printBytes(responseBytes)
            self.socket.sendto(responseBytes, client)
            
        log("CoAP Server stopped")
    
    def enableMulticast(self):
        while not self.running:
            pass
        mreq = struct.pack("4sl", socket.inet_aton(self.multicast_ip), socket.INADDR_ANY)
        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        log("CoAP Server binded on coap://%s:%s/ (MULTICAST)" % (self.multicast_ip, self.port))
                
    def stop(self):
        self.running = False
        self.socket.close()
        
    def processMessage(self, request, response):
        if request.type == COAPMessage.CON:
            response.type = COAPMessage.ACK
        else:
            response.type = COAPMessage.NON

        if request.token:
            response.token = request.token

        response.id = request.id
        response.uri_path = request.uri_path
        
        if request.code == COAPRequest.GET:
            self.handler.do_GET(request, response)
        elif request.code == COAPRequest.POST:
            self.handler.do_POST(request, response)
        
class COAPHandler():
    def __init__(self, handler):
        self.handler = handler
    
    def do_GET(self, request, response):
        try:
            (code, body, type) = self.handler.do_GET(request.uri_path[1:])
            if code == 0:
                response.code = COAPResponse.NOT_FOUND
            elif code == 200:
                response.code = COAPResponse.CONTENT
            elif (code / 100) == 4:
                response.code = 128 + (code % 100)
            elif (code / 100) == 5:
                response.code = 160 + (code % 100)
            response.payload = body
        except (GPIO.InvalidDirectionException, GPIO.InvalidChannelException, GPIO.SetupException) as e:
            response.code = COAPResponse.FORBIDDEN
            response.payload = "%s" % e
        except Exception as e:
            response.code = COAPResponse.INTERNAL_ERROR
            raise e
        
    def do_POST(self, request, response):
        try:
            (code, body, type) = self.handler.do_POST(request.uri_path[1:])
            if code == 0:
                response.code = COAPResponse.NOT_FOUND
            elif code == 200:
                response.code = COAPResponse.CHANGED
            elif (code / 100) == 4:
                response.code = 128 + (code % 100)
            elif (code / 100) == 5:
                response.code = 160 + (code % 100)
                
            response.payload = body
        except (GPIO.InvalidDirectionException, GPIO.InvalidChannelException, GPIO.SetupException) as e:
            response.code = COAPResponse.FORBIDDEN
            response.payload = "%s" % e
        except Exception as e:
            response.code = COAPResponse.INTERNAL_ERROR
            raise e
        
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

def main(argv):
    port = 8000
    configfile = "/etc/webiopi/config"

    if len(argv)  == 2:
        port = int(argv[1])
    
    server = Server(port=port, configfile=configfile)
    runLoop()
    server.stop()

signal.signal(signal.SIGINT, __signalHandler__)
signal.signal(signal.SIGTERM, __signalHandler__)

if __name__ == "__main__":
    main(sys.argv)
