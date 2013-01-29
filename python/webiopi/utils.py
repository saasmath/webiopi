import sys
import imp
import time
import signal
import socket
import base64
import hashlib
import logging
import threading
import subprocess

from _webiopi.GPIO import BOARD_REVISION

PYTHON_MAJOR = sys.version_info.major

VERSION = '0.5.4'
VERSION_STRING = "WebIOPi/%s/Python%d.%d" % (VERSION, sys.version_info.major, sys.version_info.minor)

MAPPING = [[], [], []]
MAPPING[1] = ["V33", "V50", 0, "V50", 1, "GND", 4, 14, "GND", 15, 17, 18, 21, "GND", 22, 23, "V33", 24, 10, "GND", 9, 25, 11, 8, "GND", 7]
MAPPING[2] = ["V33", "V50", 2, "V50", 3, "GND", 4, 14, "GND", 15, 17, 18, 27, "GND", 22, 23, "V33", 24, 10, "GND", 9, 25, 11, 8, "GND", 7]

FUNCTIONS = {
    "I2C": {"enabled": False, "gpio": {0:"SDA", 1:"SCL", 2:"SDA", 3:"SCL"}, "modules": ["i2c-bcm2708", "i2c-dev"]},
    "SPI": {"enabled": False, "gpio": {7:"CE1", 8:"CE0", 9:"MISO", 10:"MOSI", 11:"SCLK"}, "modules": ["spi-bcm2708", "spidev"]},
    "UART": {"enabled": True, "gpio": {14:"TX", 15:"RX"}, "modules": []},
    "ONEWIRE": {"enabled": False, "gpio": {4:"DATA"}, "modules": ["w1-gpio"]}
}

SERIALS = {}
DEVICES = {}
SCRIPTS = {}
        
LOG_FORMATTER = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt="%Y-%m-%d %H:%M:%S")        
ROOT_LOGGER = logging.getLogger()
ROOT_LOGGER.setLevel(logging.WARN)

CONSOLE_HANDLER = logging.StreamHandler()
CONSOLE_HANDLER.setFormatter(LOG_FORMATTER)
ROOT_LOGGER.addHandler(CONSOLE_HANDLER)

LOGGER = logging.getLogger("WebIOPi")

M_PLAIN = "text/plain"
M_JSON  = "application/json"

__running__ = False

TASKS = []

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
    global __running__
    info("Stopping...")
    __running__ = False
    for task in TASKS:
        task.stop()

    for name in SCRIPTS:
        script = SCRIPTS[name]
        if hasattr(script, "destroy"):
            script.destroy()
        
def runLoop(func=None, async=False):
    global __running__
    global __lock__
    __running__ = True

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    if func != None:
        if async:
            TASKS.append(Task(func, True))
        else:
            while __running__:
                func()
    else:
        signal.pause()

def waitForSignal():
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    signal.pause()
    
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

def encodeAuth(login, password):
    abcd = "%s:%s" % (login, password)
    if PYTHON_MAJOR >= 3:
        b = base64.b64encode(abcd.encode())
    else:
        b = base64.b64encode(abcd)
    return hashlib.sha256(b).hexdigest()

def getLocalIP():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 53))
            (host, p) = s.getsockname()
            s.close()
            return host 
        except (socket.error, e):
            return "localhost"
        
def route(method="POST", path=None, format="%s"):
    def wrapper(func):
        func.routed = True
        func.method = method
        func.format = format
        if path:
            func.path = path
        else:
            func.path = func.__name__
        return func
    return wrapper

def macro(func):
    func.macro = True
    return func

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

def printBytes(bytes):
    for i in range(0, len(bytes)):
        print("%03d: 0x%02X %03d %c" % (i, bytes[i], bytes[i], bytes[i]))

def loadModules(bus):
    if len(FUNCTIONS[bus]["modules"]) == 0:
        return
    
    if FUNCTIONS[bus]["enabled"] == False and not modulesLoaded(bus):
        info("Loading %s modules" % bus)
        for module in FUNCTIONS[bus]["modules"]:
            subprocess.call(["modprobe", module])
        FUNCTIONS[bus]["enabled"] = True

def unloadModules(bus):
    if len(FUNCTIONS[bus]["modules"]) == 0:
        return

    info("Unloading %s modules" % bus)
    for module in FUNCTIONS[bus]["modules"]:
        subprocess.call(["modprobe", "-r", module])
    FUNCTIONS[bus]["enabled"] = False
        
def __moduleLoaded__(modules, lines):
    if len(modules) == 0:
        return True
    for line in lines:
        if modules[0].replace("-", "_") == line.split(" ")[0]:
            return __moduleLoaded__(modules[1:], lines)
    return False

def modulesLoaded(bus):
    if not bus in FUNCTIONS or len(FUNCTIONS[bus]["modules"]) == 0:
        return True

    f = open("/proc/modules")
    c = f.read()
    f.close()
    lines = c.split("\n")
    return __moduleLoaded__(FUNCTIONS[bus]["modules"], lines)

def checkAllBus():
    for bus in FUNCTIONS:
        if modulesLoaded(bus):
            FUNCTIONS[bus]["enabled"] = True
            
def deviceInstance(name):
    if name in DEVICES:
        return DEVICES[name]["device"]
    else:
        return None

checkAllBus()
