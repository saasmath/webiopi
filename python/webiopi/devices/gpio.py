from webiopi.rest import route
from webiopi.utils import *

class GPIODriver():
    def __init__(self):
        self.export = []
        self.post_value = True
        self.post_function = True
        
    def __str__(self):
        return "GPIODriver"
    
    def checkChannelAllowed(self, channel):
        if len(self.export) > 0 and not channel in self.export:
            raise ValueError("GPIO %d Not Authorized" % channel)
        
    def checkPostingFunctionAllowed(self):
        if not self.post_function:
            raise ValueError("POSTing function not allowed")
    
    def checkPostingValueAllowed(self):
        if not self.post_value:
            raise ValueError("POSTing value not allowed")
    
    @route("GET", "%(channel)d/function", "%s")
    def getFunctionString(self, channel):
        self.checkChannelAllowed(channel)
        return GPIO.getFunctionString(channel)
    
    @route("POST", "%(channel)d/function/%(value)s", "%s")
    def setFunction(self, channel, value):
        self.checkPostingFunctionAllowed()
        self.checkChannelAllowed(channel)
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
    
    @route("GET", "%(channel)d/value", "%d")
    def getValue(self, channel):
        self.checkChannelAllowed(channel)
        return GPIO.input(channel)
    
    @route("GET", "%(channel)d/pulse", "%s")
    def getPulse(self, channel):
        self.checkChannelAllowed(channel)
        return GPIO.getPulse(channel)
    
    @route("POST", "%(channel)d/value/%(value)d", "%d")
    def setValue(self, channel, value):
        self.checkPostingValueAllowed()
        self.checkChannelAllowed(channel)
        GPIO.output(channel, value)
        return GPIO.input(channel)

    @route("POST", "%(channel)d/sequence/%(args)s", "%d")
    def outputSequence(self, channel, args):
        self.checkPostingValueAllowed()
        self.checkChannelAllowed(channel)
        (period, sequence) = args.split(",")
        period = int(period)
        GPIO.outputSequence(channel, period, sequence)
        return int(sequence[-1])
        
    @route("POST", "%(channel)d/pulse/", "%s")
    def pulse(self, channel):
        self.checkPostingValueAllowed()
        self.checkChannelAllowed(channel)
        GPIO.pulse(channel)
        return "OK"
        
    @route("POST", "%(channel)d/pulseRatio/%(value)f", "%s")
    def pulseRatio(self, channel, value):
        self.checkPostingValueAllowed()
        self.checkChannelAllowed(channel)
        GPIO.pulseRatio(channel, value)
        return GPIO.getPulse(channel)
        
    @route("POST", "%(channel)d/pulseAngle/%(value)f", "%s")
    def pulseAngle(self, channel, value):
        self.checkPostingValueAllowed()
        self.checkChannelAllowed(channel)
        GPIO.pulseAngle(channel, value)
        return GPIO.getPulse(channel)
        
    def setup(self):
        pass
    
    def close(self):
        pass