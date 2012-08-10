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
import BaseHTTPServer
import mimetypes as mime
import RPi.GPIO as GPIO


HOST_NAME = '0.0.0.0'
PORT_NUMBER = 80
INDEX_FILE = "webiopi.html"

PIN_COUNT = 26
GPIO_PINS = []
GPIO_AVAILABLE = [0, 1, 4, 7, 8, 9, 10, 11, 14, 15, 17, 18, 21, 22, 23, 24, 25]

ALT = {
    "I2C": {"enabled": False, "pins": [0, 1]},
    "SPI": {"enabled": False, "pins": [7, 8, 9, 10, 11]},
    "UART": {"enabled": False, "pins": [14, 15]}
}

class MODE:
    DISABLED=0
    GPIO=1
    ALT=2
    

def setGPIOValue(pin, value):
    GPIO.output(pin, value)
    GPIO_PINS[pin]["value"] = value
      
def setGPIODirection(pin, direction):
    GPIO.setup(pin, direction)
    GPIO_PINS[pin]["direction"] = direction
    if (direction == GPIO.OUT):
        setGPIOValue(pin, False)

def initGPIO(pin):
    setGPIODirection(pin, GPIO.IN)
    GPIO_PINS[pin]["mode"] = MODE.GPIO

def setALT(alt, enable):
    for pin in ALT[alt]["pins"]:
        p = GPIO_PINS[pin];
        if enable:
            p["mode"] = MODE.ALT
        else:
            p["mode"] = MODE.GPIO
            setGPIODirection(pin, GPIO.OUT)
            setGPIOValue(pin, False)
    ALT[alt]["enabled"] = enable
            
def writeJSON(out):
    out.write("{")
    first = True
    for (alt, value) in ALT.items():
        if not first:
            out.write (", ")
        out.write('"%s": %d' % (alt, value["enabled"]))
        first = False
    
    out.write(', "GPIO":{\n')
    first = True
    for pin in GPIO_AVAILABLE:
        if not first:
            out.write (", \n")
        mode = "GPIO"
        if (GPIO_PINS[pin]["mode"] == MODE.ALT):
            mode = "ALT"
        direction = "out"
        if (GPIO_PINS[pin]["direction"] == GPIO.IN):
            direction = "in"
            GPIO_PINS[pin]["value"] = GPIO.input(pin)
            
        value = 0
        if (GPIO_PINS[pin]["value"] == True):
            value = 1
        out.write('"%d": {"mode": "%s", "direction": "%s", "value": %d}' % (pin, mode, direction, value))
        first = False
        
    out.write("\n}}")
        
class WebPiHandler(BaseHTTPServer.BaseHTTPRequestHandler):
        
    def sendError(s, code, message):
        s.send_response(code)
        s.end_headers()
        s.wfile.write("<html><head><title>%d - %s</title></head><body><h1>%d - %s</h1></body></html>" % (code, message, code, message))

    def do_GET(s):
        if s.path == "/": 
            f = open(INDEX_FILE)
            s.send_response(200)
            (type, encoding) = mime.guess_type(INDEX_FILE)
            s.send_header("Content-type", type);
            s.end_headers()
            s.wfile.write(f.read())
            f.close()
        elif s.path == "/*":
            s.send_response(200)
            s.send_header("Content-type", "application/json")
            s.end_headers()
            writeJSON(s.wfile)
        elif os.path.exists(os.getcwd() + s.path):
            f = open(os.getcwd() + s.path)
            s.send_response(200)
            (type, encoding) = mime.guess_type(s.path)
            s.send_header("Content-type", type);
            s.end_headers()
            s.wfile.write(f.read())
            f.close()
        else:
            WebPiHandler.sendError(s, 404, "Not Found")

    def do_POST(s):
        (root, mode, pin, operation, value) = s.path.split("/")
        i = int(pin)
        if (mode == "GPIO"):
            if (operation == "value"):
                if (value == "1"):
                    setGPIOValue(i, True)
                else:
                    setGPIOValue(i , False)
    
                s.send_response(200)
                s.send_header("Content-type", "text/plain");
                s.end_headers()
                s.wfile.write(value)
            elif (operation == "direction"):
                if value == "in":
                    setGPIODirection(i, GPIO.IN)
                else:
                    setGPIODirection(i, GPIO.OUT)
    
                s.send_response(200)
                s.send_header("Content-type", "text/plain");
                s.end_headers()
                s.wfile.write(value)
        else:
            WebPiHandler.sendError(s, 404, "Not Found")

if __name__ == '__main__':
    args = sys.argv
    if len(args)  == 2:
        PORT_NUMBER = int(args[1])

    GPIO.setmode(GPIO.BCM)

    for i in range(PIN_COUNT):
        GPIO_PINS.append({"mode": 0, "direction": None, "value": None})

    setALT("UART", True)

    for pin in GPIO_AVAILABLE:
        if GPIO_PINS[pin]["mode"] != MODE.ALT:
            initGPIO(pin)

    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), WebPiHandler)
    print time.asctime(), "WebIOPi Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        running = False
        pass
    httpd.server_close()
    print time.asctime(), "WebIOPi Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
