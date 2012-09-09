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
import RPi.GPIO as RPi

VERSION = '0.3.x'

SERVER_VERSION = 'WebIOPi/' + VERSION 
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def log(message):
    print SERVER_VERSION, message

def log_socket_error(message):
    log("Socket Error: %s" % message)

class GPIO:
    DISABLED=0
    ENABLED=1
    ALT=2
        
    IN = RPi.IN
    OUT = RPi.OUT
    ALT0 = RPi.ALT0
    
    LOW = RPi.LOW
    HIGH = RPi.HIGH

    GPIO_MODE = []
    GPIO_AVAILABLE = [0, 1, 4, 7, 8, 9, 10, 11, 14, 15, 17, 18, 21, 22, 23, 24, 25]
    ALT = {
        "I2C": {"enabled": False, "gpio": [0, 1]},
        "SPI": {"enabled": False, "gpio": [7, 8, 9, 10, 11]},
        "UART": {"enabled": False, "gpio": [14, 15]}
    }
    
    def __init__(self):
        RPi.setmode(RPi.BCM)
        
        for i in range(self.GPIO_AVAILABLE[len(self.GPIO_AVAILABLE)-1]+1):
            self.GPIO_MODE.append(GPIO.DISABLED)
    
        self.setALT("UART", True)
    
        for gpio in self.GPIO_AVAILABLE:
            if self.GPIO_MODE[gpio] != GPIO.ALT:
                self.GPIO_MODE[gpio] = GPIO.ENABLED
                self.setDirection(gpio, GPIO.IN)

    def isAvailable(self, gpio):
        return gpio in self.GPIO_AVAILABLE
    
    def isEnabled(self, gpio):
        return self.GPIO_MODE[gpio] == GPIO.ENABLED
    
    def setValue(self, gpio, value):
        RPi.output(gpio, value)
    
    def getValueInteger(self, gpio):
        if (RPi.input(gpio)):
            return 1
        else:
            return 0
        
    def setDirection(self, gpio, direction):
        RPi.setup(gpio, direction, force=1)
                
    def getDirectionString(self, gpio):
        if RPi.gpio_function(gpio) == GPIO.IN:
            return "in"
        else:
            return "out"
            
    def setALT(self, alt, enable):
        for gpio in self.ALT[alt]["gpio"]:
            if enable:
                self.GPIO_MODE[gpio] = GPIO.ALT
            else:
                self.GPIO_MODE[gpio] = GPIO.ENABLED
                self.setDirection(gpio, GPIO.OUT)
                self.setValue(gpio, False)
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

            if (self.GPIO_MODE[pin] == GPIO.ALT):
                mode = "ALT"
            else:
                direction = self.getDirectionString(pin)
                value = self.getValueInteger(pin)
                
            out.write('"%d": {"mode": "%s", "direction": "%s", "value": %d}' % (pin, mode, direction, value))
            first = False
            
        out.write("\n}}")
                
class Server(BaseHTTPServer.HTTPServer, threading.Thread):
    def __init__(self, port=8000, context="webiopi", index="index.html"):
        try:
            BaseHTTPServer.HTTPServer.__init__(self, ("", port), Handler)
        except socket.error, (e_no, e_str):
            if (e_no == errno.EADDRINUSE):
                log_socket_error("Port %d already in use, try another one" % port)
            else:
                log_socket_error(e_str)
            sys.exit()
            
        threading.Thread.__init__(self)
        self.port = port
        self.context = context
        self.index = index
        self.gpio = GPIO()
        self.log_enabled = False;
        
        if not self.context.startswith("/"):
            self.context = "/" + self.context
        if not self.context.endswith("/"):
            self.context += "/"
        self.start()


    def run(self):
        host = "[RaspberryIP]"
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 53))
            (host, p) = s.getsockname()
            s.close()
        except socket.error, e:
            pass

        self.running = True
        log("Started at http://%s:%s%s" % (host, self.port, self.context))
        try:
            self.serve_forever()
        except socket.error, (e_no, e_str):
            if self.running:
                log_socket_error(e_str)
        log("Stopped")

    def stop(self):
        self.running = False
        self.server_close()
    
        
class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        if self.server.log_enabled:
            BaseHTTPServer.BaseHTTPRequestHandler.log_message(self, format, args)

    def version_string(self):
        return SERVER_VERSION + ' ' + self.sys_version
        
    def checkGPIO(self, gpio):
        if not self.server.gpio.isAvailable(gpio):
            self.send_error(403, "GPIO " + gpio + " Not Available")
            return False
        if not self.server.gpio.isEnabled(gpio):
            self.send_error(403, "GPIO " + gpio + " Disabled")
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
            self.send_error(404, "Not Found")

        elif os.path.exists(fullPath):
            realpath = os.path.realpath(fullPath)
            if not realpath.startswith(SCRIPT_DIR):
                self.send_error(403, "Not Authorized")
                return
                
            if (os.path.isdir(realpath)):
                realpath += os.sep + self.server.index;
                if not os.path.exists(realpath):
                    self.send_error(403, "Not Authorized")
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

        elif relativePath == "version":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(SERVER_VERSION)

        elif (relativePath.startswith("GPIO/")):
            (mode, s_gpio, operation) = relativePath.split("/")
            gpio = int(s_gpio)
            if not self.checkGPIO(gpio):
                return
            value = None
            if (operation == "value"):
                value = self.server.gpio.getValueInteger(gpio)
    
            elif (operation == "direction"):
                value = self.server.gpio.getDirectionString(gpio)
    
            else:
                self.send_error(404, operation + " Not Found")
                return
                
            self.send_response(200)
            self.send_header("Content-type", "text/plain");
            self.end_headers()
            self.wfile.write(value)

        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        relativePath = self.path.replace(self.server.context, "")
        if (relativePath.startswith("GPIO/")):
            (mode, s_gpio, operation, value) = relativePath.split("/")
            gpio = int(s_gpio)
            if not self.checkGPIO(gpio):
                return
            
            if (operation == "value"):
                if (value == "0"):
                    self.server.gpio.setValue(gpio, False)
                elif (value == "1"):
                    self.server.gpio.setValue(gpio, True)
                else:
                    self.send_error(400, "Bad Value")
                    return
    
                self.send_response(200)
                self.send_header("Content-type", "text/plain");
                self.end_headers()
                self.wfile.write(value)

            elif (operation == "direction"):
                if value == "in":
                    self.server.gpio.setDirection(gpio, GPIO.IN)
                elif value == "out":
                    self.server.gpio.setDirection(gpio, GPIO.OUT)
                else:
                    self.send_error(400, "Bad Direction")
                    return
    
                self.send_response(200)
                self.send_header("Content-type", "text/plain");
                self.end_headers()
                self.wfile.write(value)
            else: # operation unknown
                self.send_error(404, operation + " Not Found")
        else: # path unknowns
            self.send_error(404, "Not Found")
            
def main(argv):
    port = 8000

    if len(argv)  == 2:
        port = int(argv[1])
    
    server = Server(port)
    try:
        while True:
            time.sleep(10)
            
    except KeyboardInterrupt:
        pass
    
    server.stop()

if __name__ == "__main__":
    main(sys.argv)
