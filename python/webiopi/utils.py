import sys
import time
import signal
import socket
import base64
import hashlib

from _webiopi.GPIO import BOARD_REVISION

PYTHON_MAJOR = sys.version_info.major

VERSION = '0.5.4'
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

def signalHandler(sig, func=None):
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

signal.signal(signal.SIGINT, signalHandler)
signal.signal(signal.SIGTERM, signalHandler)


