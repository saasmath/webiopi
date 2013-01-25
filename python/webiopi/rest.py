from webiopi.utils import *
from webiopi.serial import *
import webiopi.devices.temp

try :
    import _webiopi.GPIO as GPIO
except:
    pass

def findDevice(name):
    for dev in webiopi.devices.temp.__all__:
        if dev.__name__.split(".")[-1] == name:
            return dev
    return None

class RESTHandler():
    def __init__(self):
        self.callbacks = {}
        self.serials = {}
        self.devices = {}
        
    def stop(self):
        for name in self.serials:
            serial = self.serials[name]
            serial.close()

    def addMacro(self, callback):
        self.callbacks[callback.__name__] = callback
        
    def addSerial(self, name, device, speed):
        serial = Serial(speed, "/dev/%s" % device)
        self.serials[name] = serial
        
    def addDevice(self, name, device, args):
        devClass = findDevice(device)
        if len(args) > 0:
            dev = devClass(*args)
        else:
            dev = devClass()

        funcs = {"GET": {}, "POST": {}}
        for att in dir(dev):
            func = getattr(dev, att)
            if callable(func) and hasattr(func, "routed"):
                funcs[func.method][func.path] = func
        
        self.devices[name] = {'device': dev, 'functions': funcs}

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
        for gpio in range(GPIO.GPIO_COUNT):
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
            return (200, SERVER_VERSION, M_PLAIN)

        # board revision
        elif relativePath == "revision":
            revision = "%s" % GPIO.BOARD_REVISION
            return (200, revision, M_PLAIN)

        # Single GPIO getter
        elif relativePath.startswith("GPIO/"):
            (mode, s_gpio, operation) = relativePath.split("/")
            gpio = int(s_gpio)

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
                return (200, ("%s" % self.serials.keys()).replace("'", '"'), M_JSON)
            if device in self.serials:
                serial = self.serials[device]
                if serial.available() > 0:
                    data = serial.read(serial.available())
                    return (200, data.decode(), M_PLAIN)
                else:
                    return (200, None, None)
                
            else:
                return (404, device + " Not Found", M_PLAIN)

        elif relativePath.startswith("device/"):
            path = relativePath.replace("device/", "")
            (deviceName, functionName) = path.split("/")
            if not deviceName in self.devices:
                return (404, deviceName + " Not Found", M_PLAIN)
            funcs = self.devices[deviceName]["functions"]["GET"]
            if not functionName in funcs:
                return (404, functionName + " Not Found", M_PLAIN)
            func = funcs[functionName]
            result = func()
            response = None
            if result:
                response = str(result)
            return (200, response, M_PLAIN)

        else:
            return (0, None, None)

    def do_POST(self, relativePath, data):
        if relativePath.startswith("GPIO/"):
            (mode, s_gpio, operation, value) = relativePath.split("/")
            gpio = int(s_gpio)
            
            if operation == "value":
                if value == "0":
                    GPIO.output(gpio, GPIO.LOW)
                elif value == "1":
                    GPIO.output(gpio, GPIO.HIGH)
                else:
                    return (400, "Bad Value", M_PLAIN)
    
                return (200, value, M_PLAIN)

            elif operation == "function":
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
            (mode, fname, value) = relativePath.split("/")
            if fname in self.callbacks:
                callback = self.callbacks[fname]

                if ',' in value:
                    args = value.split(',')
                    result = callback(*args)
                elif len(value) > 0:
                    result = callback(value)
                else:
                    result = callback()
                     
                response = ""
                if result:
                    response = "%s" % result
                return (200, response, M_PLAIN)
                    
            else:
                return (404, fname + " Not Found", M_PLAIN)
                
        elif relativePath.startswith("serial/"):
            device = relativePath.replace("serial/", "")
            if device in self.serials:
                serial = self.serials[device]
                serial.write(data)
                return (200, None, None)
            else:
                return (404, device + " Not Found", M_PLAIN)

        else: # path unknowns
            return (0, None, None)
