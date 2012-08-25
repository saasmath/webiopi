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
import threading
import errno
import socket
import BaseHTTPServer
import mimetypes as mime
import RPi.GPIO

VERSION = '0.2.1'

SERVER_VERSION = 'WebIOPi/' + VERSION 
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

class GPIO:
    DISABLED=0
    ENABLED=1
    ALT=2
        
    IN = RPi.GPIO.IN
    OUT = RPi.GPIO.OUT
    
    LOW = RPi.GPIO.LOW
    HIGH = RPi.GPIO.HIGH

    GPIO_PINS = []
    GPIO_AVAILABLE = [0, 1, 4, 7, 8, 9, 10, 11, 14, 15, 17, 18, 21, 22, 23, 24, 25]
    ALT = {
        "I2C": {"enabled": False, "pins": [0, 1]},
        "SPI": {"enabled": False, "pins": [7, 8, 9, 10, 11]},
        "UART": {"enabled": False, "pins": [14, 15]}
    }
    
    def __init__(self):
        RPi.GPIO.setmode(RPi.GPIO.BCM)
        
        for i in range(self.GPIO_AVAILABLE[len(self.GPIO_AVAILABLE)-1]+1):
            self.GPIO_PINS.append({"mode": 0, "direction": None, "value": None})
    
        self.setALT("UART", True)
    
        for pin in self.GPIO_AVAILABLE:
            if self.GPIO_PINS[pin]["mode"] != GPIO.ALT:
                self.GPIO_PINS[pin]["mode"] = GPIO.ENABLED
                self.setDirection(pin, GPIO.IN)

    def isAvailable(self, gpio):
        return gpio in self.GPIO_AVAILABLE
    
    def isEnabled(self, gpio):
        return self.GPIO_PINS[gpio]["mode"] == GPIO.ENABLED
    
    def setValue(self, pin, value):
        RPi.GPIO.output(pin, value)
        self.GPIO_PINS[pin]["value"] = value
    
    def getValue(self, pin):
        if (self.GPIO_PINS[pin]["direction"] == GPIO.IN):
            self.GPIO_PINS[pin]["value"] = RPi.GPIO.input(pin)
        if (self.GPIO_PINS[pin]["value"] == GPIO.HIGH):
            return 1
        else:
            return 0
        
    def setDirection(self, pin, direction):
        if self.GPIO_PINS[pin]["direction"] != direction:
            RPi.GPIO.setup(pin, direction)
            self.GPIO_PINS[pin]["direction"] = direction
            if (direction == GPIO.OUT):
                self.setValue(pin, False)
                
    def getDirection(self, pin):
        if self.GPIO_PINS[pin]["direction"] == GPIO.IN:
            return "in"
        else:
            return "out"
            
    def setALT(self, alt, enable):
        for pin in self.ALT[alt]["pins"]:
            p = self.GPIO_PINS[pin];
            if enable:
                p["mode"] = GPIO.ALT
            else:
                p["mode"] = GPIO.ENABLED
                self.setDirection(pin, GPIO.OUT)
                self.setValue(pin, False)
        self.ALT[alt]["enabled"] = enable
                
    def writeJSON(self, out):
        out.write("{")
        first = True
        for (alt, value) in self.ALT.items():
            if not first:
                out.write (", ")
            out.write('"%s": %d' % (alt, value["enabled"]))
            first = False
        
        out.write(', "GPIO":{\n')
        first = True
        for pin in self.GPIO_AVAILABLE:
            if not first:
                out.write (", \n")

            mode = "GPIO"
            direction = "out"
            value = 0

            if (self.GPIO_PINS[pin]["mode"] == GPIO.ALT):
                mode = "ALT"
            else:
                direction = self.getDirection(pin)
                value = self.getValue(pin)
                
            out.write('"%d": {"mode": "%s", "direction": "%s", "value": %d}' % (pin, mode, direction, value))
            first = False
            
        out.write("\n}}")
                
                
class WebIOPiServer(BaseHTTPServer.HTTPServer):
    def __init__(self, binding, handler, context, index):
        BaseHTTPServer.HTTPServer.__init__(self, binding, handler)
        self.context = context
        self.index = index
        self.gpio = GPIO()
            
class WebIOPiHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def version_string(self):
        return SERVER_VERSION + ' ' + self.sys_version
        
    def sendError(self, code, message):
        self.send_response(code)
        self.end_headers()
        self.wfile.write("<html><head><title>%d - %s</title></head><body><h1>%d - %s</h1></body></html>" 
                         % (code, message, code, message))
   
    def checkGPIOPin(self, pin):
        i = int(pin)
        if not self.server.gpio.isAvailable(i):
            self.sendError(403, "GPIO " + pin + " Not Available")
            return False
        if not self.server.gpio.isEnabled(i):
            self.sendError(403, "GPIO " + pin + " Disabled")
            return False
        return True


    def do_GET(self):
        relativePath = self.path.replace(self.server.context, "")
        fullPath = SCRIPT_DIR + os.sep + relativePath 
        if self.path == "/":
            self.send_response(301)
            self.send_header("Location", self.server.context);
            self.end_headers()
        elif not self.path.startswith(self.server.context):
            self.sendError(404, "Not Found")
        elif os.path.exists(fullPath):
            realpath = os.path.realpath(fullPath)
            if not realpath.startswith(SCRIPT_DIR):
                self.sendError(403, "Not Authorized")
                return
                
            if (os.path.isdir(realpath)):
                realpath += os.sep + self.server.index;
                if not os.path.exists(realpath):
                    self.sendError(403, "Not Authorized")
                    return
                
            (type, encoding) = mime.guess_type(realpath)
            f = open(realpath);
            self.send_response(200)
            self.send_header("Content-type", type);
            self.end_headers()
            self.wfile.write(f.read())
            f.close()
        elif relativePath == "*":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.server.gpio.writeJSON(self.wfile)
        elif (relativePath.startswith("GPIO/")):
            (mode, pin, operation) = relativePath.split("/")
            i = int(pin)
            if not self.checkGPIOPin(pin):
                return
            value = ""
            if (operation == "value"):
                value = self.server.gpio.getValue(i)
    
            elif (operation == "direction"):
                value = self.server.gpio.getDirection(i)
    
            else:
                self.sendError(404, operation + " Not Found")
                return
                
            self.send_response(200)
            self.send_header("Content-type", "text/plain");
            self.end_headers()
            self.wfile.write(value)

        else:
            self.sendError(404, "Not Found")

    def do_POST(self):
        relativePath = self.path.replace(self.server.context, "")
        if (relativePath.startswith("GPIO/")):
            (mode, pin, operation, value) = relativePath.split("/")
            i = int(pin)
            if not self.checkGPIOPin(pin):
                return
            
            if (operation == "value"):
                if (value == "0"):
                    self.server.gpio.setValue(i, False)
                elif (value == "1"):
                    self.server.gpio.setValue(i , True)
                else:
                    self.sendError(400, "Bad Value")
                    return
    
                self.send_response(200)
                self.send_header("Content-type", "text/plain");
                self.end_headers()
                self.wfile.write(value)
            elif (operation == "direction"):
                if value == "in":
                    self.server.gpio.setDirection(i, GPIO.IN)
                elif value == "out":
                    self.server.gpio.setDirection(i, GPIO.OUT)
                else:
                    self.sendError(400, "Bad Direction")
                    return
    
                self.send_response(200)
                self.send_header("Content-type", "text/plain");
                self.end_headers()
                self.wfile.write(value)
            else:
                self.sendError(404, operation + " Not Found")
        else:
            self.sendError(404, "Not Found")
            
def main(argv):
    host = '0.0.0.0'
    port = 80
    context = "/webiopi/"
    index = "index.html"

    if len(argv)  == 2:
        port = int(argv[1])
    
    try:
        server = WebIOPiServer((host, port), WebIOPiHandler, context, index)
        print time.asctime(), "WebIOPi Started at http://%s:%s%s" % (host, port, context)
        server.serve_forever()
    except socket.error, e:
        if (e[0] == errno.EADDRINUSE):
            print "Address already in use, try another port"
        else:
            print "Unknown socket error %d" % e[0]
    except KeyboardInterrupt:
        server.server_close()
        print time.asctime(), "WebIOPi Stopped"

if __name__ == "__main__":
    main(sys.argv)
