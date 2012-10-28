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
import _webiopi.GPIO as GPIO
import re

VERSION = '0.3.x'
SERVER_VERSION = 'WebIOPi/Python/' + VERSION 

def log(message):
    print SERVER_VERSION, message

def log_socket_error(message):
    log("Socket Error: %s" % message)

class Server(BaseHTTPServer.HTTPServer, threading.Thread):
    
    def __init__(self, port=8000, context="webiopi", docroot="htdocs", index="index.html"):
        try:
            BaseHTTPServer.HTTPServer.__init__(self, ("", port), Handler)
        except socket.error, (e_no, e_str):
            if (e_no == errno.EADDRINUSE):
                raise Exception("Port %d already in use, try another one" % port)
            else:
                raise Exception(e_str)
            
        threading.Thread.__init__(self)
        self.port = port
        self.context = context
        self.docroot = os.path.realpath(docroot);
        self.index = index
        self.log_enabled = False;
        
        if not self.context.startswith("/"):
            self.context = "/" + self.context
        if not self.context.endswith("/"):
            self.context += "/"
        self.start()


    GPIO_COUNT = 54
    
    ALT = {
        "I2C": {"enabled": False, "gpio": [0, 1]},
        "SPI": {"enabled": False, "gpio": [7, 8, 9, 10, 11]},
        "UART": {"enabled": True, "gpio": [14, 15]}
    }
    
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
        for gpio in range(self.GPIO_COUNT):
            if not first:
                out.write (", \n")

            function = GPIO.getFunctionString(gpio)
            value = GPIO.input(gpio)
                
            out.write('"%d": {"function": "%s", "value": %d}' % (gpio, function, value))
            first = False
            
        out.write("\n}}")

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
        
    def do_GET(self):
        relativePath = self.path.replace(self.server.context, "")
        fullPath = self.server.docroot + os.sep + relativePath 

        if self.path == "/":
            self.send_response(301)
            self.send_header("Location", self.server.context);
            self.end_headers()

        elif not self.path.startswith(self.server.context):
            self.send_error(404, "Not Found")

        elif os.path.exists(fullPath):
            realpath = os.path.realpath(fullPath)
            if not realpath.startswith(self.server.docroot):
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
            self.server.writeJSON(self.wfile)

        elif relativePath == "version":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(SERVER_VERSION)

        elif (relativePath.startswith("GPIO/")):
            (mode, s_gpio, operation) = relativePath.split("/")
            gpio = int(s_gpio)

            value = None
            if (operation == "value"):
                value = GPIO.input(gpio)
    
            elif (operation == "function"):
                value = GPIO.getFunctionString(gpio)
    
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
            
            if (operation == "value"):
                if (value == "0"):
                    GPIO.output(gpio, GPIO.LOW)
                elif (value == "1"):
                    GPIO.output(gpio, GPIO.HIGH)
                else:
                    self.send_error(400, "Bad Value")
                    return
    
                self.send_response(200)
                self.send_header("Content-type", "text/plain");
                self.end_headers()
                self.wfile.write(value)

            elif (operation == "function"):
                value = value.lower()
                if value == "in":
                    GPIO.setFunction(gpio, GPIO.IN)
                elif value == "out":
                    GPIO.setFunction(gpio, GPIO.OUT)
                else:
                    self.send_error(400, "Bad Function")
                    return
                value = GPIO.getFunctionString(gpio)
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
