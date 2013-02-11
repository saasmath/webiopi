from webiopi.rest import *
from webiopi.utils import *
from webiopi.devices.digital import *

class NativeGPIO(GPIOPort):
    def __init__(self):
        GPIOPort.__init__(self, 54)
        self.export = []
        self.post_value = True
        self.post_function = True
        
    def __str__(self):
        return "GPIO"
    
    def checkPostingFunctionAllowed(self):
        if not self.post_function:
            raise ValueError("POSTing function not allowed")
    
    def checkPostingValueAllowed(self):
        if not self.post_value:
            raise ValueError("POSTing value not allowed")
    
    def __input__(self, channel):
        return GPIO.input(channel)
    
    def __output__(self, channel, value):
        self.checkPostingValueAllowed()
        GPIO.output(channel, value)

    @request("GET", "%(channel)d/function")
    def getFunctionString(self, channel):
        self.checkChannel(channel)
        return GPIO.getFunctionString(channel)
    
    @request("POST", "%(channel)d/function/%(value)s")
    def setFunction(self, channel, value):
        self.checkPostingFunctionAllowed()
        self.checkChannel(channel)
        value = value.lower()
        if value == "in":
            GPIO.setFunction(channel, GPIO.IN)
        elif value == "out":
            GPIO.setFunction(channel, GPIO.OUT)
        elif value == "pwm":
            GPIO.setFunction(channel, GPIO.PWM)
        else:
            raise ValueError("Bad Function")
        return GPIO.getFunctionString(channel)
    
    @request("GET", "%(channel)d/pulse", "%s")
    def getPulse(self, channel):
        self.checkChannel(channel)
        return GPIO.getPulse(channel)
    
    @request("POST", "%(channel)d/sequence/%(args)s")
    @response("%d")
    def outputSequence(self, channel, args):
        self.checkPostingValueAllowed()
        self.checkChannel(channel)
        (period, sequence) = args.split(",")
        period = int(period)
        GPIO.outputSequence(channel, period, sequence)
        return int(sequence[-1])
        
    @request("POST", "%(channel)d/pulse/")
    def pulse(self, channel):
        self.checkPostingValueAllowed()
        self.checkChannel(channel)
        GPIO.pulse(channel)
        return "OK"
        
    @request("POST", "%(channel)d/pulseRatio/%(value)f")
    def pulseRatio(self, channel, value):
        self.checkPostingValueAllowed()
        self.checkChannel(channel)
        GPIO.pulseRatio(channel, value)
        return GPIO.getPulse(channel)
        
    @request("POST", "%(channel)d/pulseAngle/%(value)f")
    def pulseAngle(self, channel, value):
        self.checkPostingValueAllowed()
        self.checkChannel(channel)
        GPIO.pulseAngle(channel, value)
        return GPIO.getPulse(channel)
        
    def setup(self):
        pass
    
    def close(self):
        pass
