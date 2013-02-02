from webiopi.utils import *
from webiopi.serial import Serial

MACROS = {}

M_PLAIN = "text/plain"
M_JSON  = "application/json"

try :
    import _webiopi.GPIO as GPIO
except:
    pass

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
        self.gpio_export = []
        self.gpio_post_value = True
        self.gpio_post_function = True
        self.device_mapping = True
        self.routes = {}
        
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

        funcs = {"GET": {}, "POST": {}}
        for att in dir(dev):
            func = getattr(dev, att)
            if callable(func) and hasattr(func, "routed"):
                debug("Mapping %s.%s to REST %s /device/%s/%s" % (dev, att, func.method, name, func.path))
                funcs[func.method][func.path] = func
        
        DEVICES[name] = {'device': dev, 'functions': funcs}
        info("%s mapped to REST API /device/%s" % (dev, name))
        
    def addRoute(self, source, destination):
        info("Re-Routing %s => %s" % (source, destination))
        if source[0] == "/":
            source = source[1:]
        if destination[0] == "/":
            destination = destination[1:]
        self.routes[source] = destination
        
    def findRoute(self, path):
        for source in self.routes:
            if path.startswith(source):
                return path.replace(source, self.routes[source])
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
        if len(self.gpio_export) > 0:
            gpios = self.gpio_export
        else:
            gpios = range(GPIO.GPIO_COUNT)
        for gpio in gpios:
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
        relativePath = self.findRoute(relativePath)
        
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
            return (200, VERSION_STRING, M_PLAIN)

        # board revision
        elif relativePath == "revision":
            revision = "%s" % GPIO.BOARD_REVISION
            return (200, revision, M_PLAIN)

        # Single GPIO getter
        elif relativePath.startswith("GPIO/"):
            (mode, s_gpio, operation) = relativePath.split("/")
            gpio = int(s_gpio)
            
            if len(self.gpio_export) > 0 and not gpio in self.gpio_export:
                return (403, "GPIO %d Not Authorized" % gpio, None)
            
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
            (func, args) = self.getDeviceRoute("GET", path)
            if func == None:
                return (404, args, M_PLAIN)
            result = func(**args)
            response = None
            if result != None:
                response = func.format % result
            return (200, response, M_PLAIN)

        else:
            return (0, None, None)

    def do_POST(self, relativePath, data):
        relativePath = self.findRoute(relativePath)

        if relativePath.startswith("GPIO/"):
            (mode, s_gpio, operation, value) = relativePath.split("/")
            gpio = int(s_gpio)
            if len(self.gpio_export) > 0 and not gpio in self.gpio_export:
                return (403, "GPIO %d Not Authorized" % gpio, None)
            
            if operation == "value":
                if not self.gpio_post_value:
                    return (403, None, None)
                if value == "0":
                    GPIO.output(gpio, GPIO.LOW)
                elif value == "1":
                    GPIO.output(gpio, GPIO.HIGH)
                else:
                    return (400, "Bad Value", M_PLAIN)
    
                return (200, value, M_PLAIN)

            elif operation == "function":
                if not self.gpio_post_function:
                    return (403, None, None)
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
            (func, args) = self.getDeviceRoute("POST", path)
            if func == None:
                return (404, args, M_PLAIN)
            result = func(**args)
            response = None
            if result != None:
                response = func.format % result
            return (200, response, M_PLAIN)

        else: # path unknowns
            return (0, None, None)

import webiopi.devices.digital as digital
import webiopi.devices.analog as analog
import webiopi.devices.sensor as sensor

PACKAGES = [digital, analog, sensor]
