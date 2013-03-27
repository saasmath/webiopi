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

import sys
import imp
import time
import json
import signal
import socket
import base64
import hashlib
import logging
import threading
import subprocess
import _webiopi.GPIO as GPIO

BOARD_REVISION = GPIO.BOARD_REVISION

PYTHON_MAJOR = sys.version_info.major

VERSION = '0.6.0'
VERSION_STRING = "WebIOPi/%s/Python%d.%d" % (VERSION, sys.version_info.major, sys.version_info.minor)

MAPPING = [[], [], []]
MAPPING[1] = ["V33", "V50", 0, "V50", 1, "GND", 4, 14, "GND", 15, 17, 18, 21, "GND", 22, 23, "V33", 24, 10, "GND", 9, 25, 11, 8, "GND", 7]
MAPPING[2] = ["V33", "V50", 2, "V50", 3, "GND", 4, 14, "GND", 15, 17, 18, 27, "GND", 22, 23, "V33", 24, 10, "GND", 9, 25, 11, 8, "GND", 7]

FUNCTIONS = {
    "I2C": {"enabled": False, "gpio": {0:"SDA", 1:"SCL", 2:"SDA", 3:"SCL"}, "modules": ["i2c-bcm2708", "i2c-dev"]},
    "SPI": {"enabled": False, "gpio": {7:"CE1", 8:"CE0", 9:"MISO", 10:"MOSI", 11:"SCLK"}, "modules": ["spi-bcm2708", "spidev"]},
    "UART": {"enabled": False, "gpio": {14:"TX", 15:"RX"}},
    "ONEWIRE": {"enabled": False, "gpio": {4:"DATA"}, "modules": ["w1-gpio"], "wait": 2}
}

GPIO_SETUP = []
GPIO_RESET = []
DEVICES = {}
SCRIPTS = {}
TASKS = []
        
LOG_FORMATTER = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt="%Y-%m-%d %H:%M:%S")        
ROOT_LOGGER = logging.getLogger()
ROOT_LOGGER.setLevel(logging.WARN)

CONSOLE_HANDLER = logging.StreamHandler()
CONSOLE_HANDLER.setFormatter(LOG_FORMATTER)
ROOT_LOGGER.addHandler(CONSOLE_HANDLER)

LOGGER = logging.getLogger("WebIOPi")

RUNNING = False

class Task(threading.Thread):
    def __init__(self, func, loop=False):
        threading.Thread.__init__(self)
        self.func = func
        self.loop = loop
        self.running = True
        self.start()
    
    def stop(self):
        self.running = False

    def run(self):
        if self.loop:
            while self.running == True:
                self.func()
        else:
            self.func()

def stop(signum=0, frame=None):
    global RUNNING
    if RUNNING:
        info("Stopping...")
        RUNNING = False
        for task in TASKS:
            task.stop()
    
        for name in SCRIPTS:
            script = SCRIPTS[name]
            if hasattr(script, "destroy"):
                script.destroy()
        
        for name in DEVICES:
            device = DEVICES[name]["device"]
            device.close()
                
        GPIOReset()

def runLoop(func=None, async=False):
    global RUNNING
    RUNNING = True
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    if func != None:
        if async:
            TASKS.append(Task(func, True))
        else:
            while RUNNING:
                func()
    else:
        while RUNNING:
            time.sleep(1)


def addGPIO(lst, gpio, params):
    gpio = int(gpio)
    params = params.split(" ")
    func = params[0].lower()
    if func == "in":
        func = GPIO.IN
    elif func == "out":
        func = GPIO.OUT
    else:
        raise Exception("Unknown function")
    
    value = -1
    if len(params) > 1:
        value = int(params[1])
    lst.append({"gpio": gpio, "func": func, "value": value})

def addGPIOSetup(gpio, params):
    addGPIO(GPIO_SETUP, gpio, params)
    
def addGPIOReset(gpio, params):
    addGPIO(GPIO_RESET, gpio, params)

def GPIOSetup():
    for g in GPIO_SETUP:
        gpio = g["gpio"]
        debug("Setup GPIO %d" % gpio)
        GPIO.setFunction(gpio, g["func"])
        if g["value"] >= 0 and GPIO.getFunction(gpio) == GPIO.OUT:
            GPIO.output(gpio, g["value"])

def GPIOReset():
    for g in GPIO_RESET:
        gpio = g["gpio"]
        debug("Reset GPIO %d" % gpio)
        GPIO.setFunction(gpio, g["func"])
        if g["value"] >= 0 and GPIO.getFunction(gpio) == GPIO.OUT:
            GPIO.output(gpio, g["value"])
    
def deviceInstance(name):
    if name in DEVICES:
        return DEVICES[name]["device"]
    else:
        return None

def loadScript(name, source, handler = None):
    info("Loading %s from %s" % (name, source))
    script = imp.load_source(name, source)
    SCRIPTS[name] = script

    if hasattr(script, "setup"):
        script.setup()
    if handler:
        for aname in dir(script):
            attr = getattr(script, aname)
            if callable(attr) and hasattr(attr, "macro"):
                handler.addMacro(attr)
    if hasattr(script, "loop"):
        runLoop(script.loop, True)

def encodeCredentials(login, password):
    abcd = "%s:%s" % (login, password)
    if PYTHON_MAJOR >= 3:
        b = base64.b64encode(abcd.encode())
    else:
        b = base64.b64encode(abcd)
    return b

def encrypt(value):
    return hashlib.sha256(value).hexdigest()

def encryptCredentials(login, password):
    return encrypt(encodeCredentials(login, password))

def getLocalIP():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 53))
            host = s.getsockname()[0]
            s.close()
            return host 
        except socket.error:
            return "localhost"
        
def setInfo():
    ROOT_LOGGER.setLevel(logging.INFO)

def setDebug():
    ROOT_LOGGER.setLevel(logging.DEBUG)

def logToFile(filename):
    FILE_HANDLER = logging.FileHandler(filename)
    FILE_HANDLER.setFormatter(LOG_FORMATTER)
    ROOT_LOGGER.addHandler(FILE_HANDLER)

def debug(message):
    LOGGER.debug(message)

def info(message):
    LOGGER.info(message)

def warn(message):
    LOGGER.warn(message)

def error(message):
    LOGGER.error(message)

def exception(message):
    LOGGER.exception(message)

def printBytes(buff):
    for i in range(0, len(buff)):
        print("%03d: 0x%02X %03d %c" % (i, buff[i], buff[i], buff[i]))
        
def jsonDumps(obj):
    if ROOT_LOGGER.level == logging.DEBUG:
        return json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': '))
    else:
        return json.dumps(obj)
    
def str2bool(value):
    return (value == "1") or (value == "true") or (value == "True") or (value == "yes") or (value == "Yes")

def toint(value):
    if isinstance(value, str):
        if value.startswith("0b"):
            return int(value, 2)
        elif value.startswith("0x"):
            return int(value, 16)
        else:
            return int(value)
    return value

        
def signInteger(value, bitcount):
    if value & (1<<(bitcount-1)):
        return value - (1<<bitcount)
    return value
