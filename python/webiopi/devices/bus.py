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
import time
import threading

from webiopi.utils import *


def loadModule(module):
    debug("Loading module : %s" % module)
    subprocess.call(["modprobe", module])
    
def unloadModule(module):
    subprocess.call(["modprobe", "-r", module])
    
def loadModules(bus):
    if FUNCTIONS[bus]["enabled"] == False and not modulesLoaded(bus):
        info("Loading %s modules" % bus)
        for module in FUNCTIONS[bus]["modules"]:
            loadModule(module)
        if "wait" in FUNCTIONS[bus]:
            info("Sleeping %ds to let %s modules load" % (FUNCTIONS[bus]["wait"], bus))
            time.sleep(FUNCTIONS[bus]["wait"])

    FUNCTIONS[bus]["enabled"] = True

def unloadModules(bus):
    info("Unloading %s modules" % bus)
    for module in FUNCTIONS[bus]["modules"]:
        unloadModule(module)
    FUNCTIONS[bus]["enabled"] = False
        
def __modulesLoaded__(modules, lines):
    if len(modules) == 0:
        return True
    for line in lines:
        if modules[0].replace("-", "_") == line.split(" ")[0]:
            return __modulesLoaded__(modules[1:], lines)
    return False

def modulesLoaded(bus):
    if not bus in FUNCTIONS or not "modules" in FUNCTIONS[bus]:
        return True

    f = open("/proc/modules")
    c = f.read()
    f.close()
    lines = c.split("\n")
    return __modulesLoaded__(FUNCTIONS[bus]["modules"], lines)

def checkAllBus():
    for bus in FUNCTIONS:
        if modulesLoaded(bus):
            FUNCTIONS[bus]["enabled"] = True

class Bus():
    def __init__(self, busName, device, flag=os.O_RDWR):
        loadModules(busName)
        self.busName = busName
        self.device = device
        self.flag = flag
        self.fd = 0
        self.open()
        
    def __str__(self):
        return "Bus(%s, %s)" % (self.busName, self.device)
        
    def open(self):
        self.fd = os.open(self.device, self.flag)
        if self.fd < 0:
            raise Exception("Cannot open %s" % self.device)

    def close(self):
        if self.fd > 0:
            os.close(self.fd)
    
    def available(self):
        raise NotImplementedError
    
    def read(self, size=1):
        if self.fd > 0:
            return os.read(self.fd, size)
        raise Exception("Device %s not open" % self.device)
    
    def readBytes(self, size=1):
        return bytearray(self.read(size))
    
    def readByte(self):
        return self.readBytes()[0]

    def write(self, string):
        if self.fd > 0:
            return os.write(self.fd, string)
        raise Exception("Device %s not open" % self.device)
    
    def writeBytes(self, data):
        return self.write(bytearray(data))

    def writeByte(self, value):
        self.writeBytes([value])
        
