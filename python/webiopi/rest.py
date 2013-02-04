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

from webiopi.utils import *
from webiopi.serial import Serial

MACROS = {}

M_PLAIN = "text/plain"
M_JSON  = "application/json"

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

def findDeviceClass(name):
    for devices in PACKAGES: 
        for dev in dir(devices):
            if dev.split(".")[-1] == name:
                return getattr(devices, dev)
    return None

class RESTHandler():
    def __init__(self):
        self.device_mapping = True
        self.routes = {}
        self.gpioExport = []
        
    def stop(self):
        for name in SERIALS:
            serial = SERIALS[name]
            serial.close()

    def addMacro(self, macro):
        MACROS[macro.__name__] = macro
        
    def addSerial(self, name, device, speed):
        serial = Serial(speed, "/dev/%s" % device)
        SERIALS[name] = serial
        info("%s mapped to REST API /serial/%s" % (serial, name))
        
    def addDevice(self, name, device, args):
        devClass = findDeviceClass(device)
        if devClass == None:
            raise Exception("Device driver not found for %s" % device)
        if len(args) > 0:
            dev = devClass(*args)
        else:
            dev = devClass()
        self.addDeviceInstance(name, dev, args)

    def addDeviceInstance(self, name, dev, args):
        funcs = {"GET": {}, "POST": {}}
        for att in dir(dev):
            func = getattr(dev, att)
            if callable(func) and hasattr(func, "routed"):
                debug("Mapping %s.%s to REST %s /device/%s/%s" % (dev, att, func.method, name, func.path))
                funcs[func.method][func.path] = func
        
        DEVICES[name] = {'device': dev, 'functions': funcs}
        info("%s mapped to REST API /device/%s" % (dev, name))
        
    def addRoute(self, source, destination):
        if source[0] == "/":
            source = source[1:]
        if destination[0] == "/":
            destination = destination[1:]
        self.routes[source] = destination
        info("Added Route /%s => /%s" % (source, destination))
        
    def findRoute(self, path):
        for source in self.routes:
            if path.startswith(source):
                route = path.replace(source, self.routes[source])
                info("Routing /%s => /%s" % (path, route))
                return route
        return path
        
    def extract(self, fmtArray, pathArray, args):
        if len(fmtArray) != len(pathArray):
            return False
        if len(fmtArray) == 0:
            return True
        fmt = fmtArray[0]
        path = pathArray[0]
        if fmt == path:
            return self.extract(fmtArray[1:], pathArray[1:], args)
        if fmt.startswith("%"):
            
            fmt = fmt[1:]
            type = 's'
            if fmt[0] == '(':
                if fmt[-1] == ')':
                    name = fmt[1:-1]
                elif fmt[-2] == ')':                                   
                    name = fmt[1:-2]
                    type = fmt[-1]
                else:
                    raise Exception("Missing closing brace")
            else:
                name = fmt
            
            if type == 's':
                args[name] = path
            elif type == 'b':
                args[name] = int(path, 2)
            elif type == 'd':
                if path.startswith("0x"):
                    args[name] = int(path, 16)
                elif path.startswith("0b"):
                    args[name] = int(path, 2)
                else:
                    args[name] = int(path)
            elif type == 'x':
                args[name] = int(path, 16)
            elif type == 'f':
                args[name] = float(path)
            else:
                raise Exception("Unknown format type : %s" % type)
            
            return self.extract(fmtArray[1:], pathArray[1:], args)
            
        return False

    def getDeviceRoute(self, method, path):
        pathArray = path.split("/")
        deviceName = pathArray[0]
        if not deviceName in DEVICES:
            return (None, deviceName + " Not Found")

        pathArray = pathArray[1:]
        funcs = DEVICES[deviceName]["functions"][method]
        functionName = "/".join(pathArray)
        if functionName in funcs:
            return (funcs[functionName], {})
        
        for fname in funcs:
            func = funcs[fname]
            funcPathArray = func.path.split("/")
            args = {}
            if self.extract(funcPathArray, pathArray, args):
                return (func, args) 
        
        return (None, functionName + " Not Found")
    
    def callDeviceFunction(self, method, path):
        (func, args) = self.getDeviceRoute(method, path)
        if func == None:
            return (404, args, M_PLAIN)
        result = func(**args)
        response = None
        if result != None:
            response = func.format % result
        return (200, response, M_PLAIN)
        
    def getJSON(self, compact=False):
        if compact:
            f = 'f'
            v = 'v'
        else:
            f = 'function'
            v = 'value'
        
        json = {}
        for (alt, value) in FUNCTIONS.items():
            json[alt] = int(value["enabled"])
        
        gpios = {}
        if len(self.gpioExport) > 0:
            export = self.gpioExport
        else:
            export = range(GPIO.GPIO_COUNT)

        for gpio in export:
            gpios[gpio] = {}
            if compact:
                gpios[gpio][f] = GPIO.getFunction(gpio)
            else:
                gpios[gpio][f] = GPIO.getFunctionString(gpio)
            gpios[gpio][v] = int(GPIO.input(gpio))

            if GPIO.getFunction(gpio) == GPIO.PWM:
                (type, value) = GPIO.getPulse(gpio).split(':')
                gpios[gpio][type] = value
        
        json['GPIO'] = gpios
        return jsonDumps(json)

    def do_GET(self, relativePath, compact=False):
        relativePath = self.findRoute(relativePath)
        
        # JSON full state
        if relativePath == "*":
            return (200, self.getJSON(compact), M_JSON)
            
        # RPi header map
        elif relativePath == "map":
            json = "%s" % MAPPING[BOARD_REVISION]
            json = json.replace("'", '"')
            return (200, json, M_JSON)

        # server version
        elif relativePath == "version":
            return (200, VERSION_STRING, M_PLAIN)

        # board revision
        elif relativePath == "revision":
            revision = "%s" % BOARD_REVISION
            return (200, revision, M_PLAIN)

        # Single GPIO getter
        elif relativePath.startswith("GPIO/"):
            return self.callDeviceFunction("GET", relativePath)
        
        elif relativePath.startswith("serial/"):
            device = relativePath.replace("serial/", "")
            if device == "*":
                return (200, ("%s" % [a for a in SERIALS.keys()]).replace("'", '"'), M_JSON)
            if device in SERIALS:
                serial = SERIALS[device]
                if serial.available() > 0:
                    data = serial.read(serial.available())
                    return (200, data.decode(), M_PLAIN)
                else:
                    return (200, None, None)
                
            else:
                return (404, device + " Not Found", M_PLAIN)

        elif relativePath.startswith("device/"):
            if not self.device_mapping:
                return (404, None, None)
            path = relativePath.replace("device/", "")
            return self.callDeviceFunction("GET", path)

        else:
            return (0, None, None)

    def do_POST(self, relativePath, data, compact=False):
        relativePath = self.findRoute(relativePath)

        if relativePath.startswith("GPIO/"):
            return self.callDeviceFunction("POST", relativePath)
                
        elif relativePath.startswith("macros/"):
            (mode, mname, value) = relativePath.split("/")
            if mname in MACROS:
                macro = MACROS[mname]

                if ',' in value:
                    args = value.split(',')
                    result = macro(*args)
                elif len(value) > 0:
                    result = macro(value)
                else:
                    result = macro()
                     
                response = ""
                if result:
                    response = "%s" % result
                return (200, response, M_PLAIN)
                    
            else:
                return (404, fname + " Not Found", M_PLAIN)
                
        elif relativePath.startswith("serial/"):
            device = relativePath.replace("serial/", "")
            if device in SERIALS:
                serial = SERIALS[device]
                serial.write(data)
                return (200, None, None)
            else:
                return (404, device + " Not Found", M_PLAIN)

        elif relativePath.startswith("device/"):
            if not self.device_mapping:
                return (404, None, None)
            path = relativePath.replace("device/", "")
            return self.callDeviceFunction("POST", path)

        else: # path unknowns
            return (0, None, None)

import webiopi.devices.digital as digital
import webiopi.devices.analog as analog
import webiopi.devices.sensor as sensor

PACKAGES = [digital, analog, sensor]
