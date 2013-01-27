import os

from webiopi.utils import *

class Bus():
    def __init__(self, name, device, flag=os.O_RDWR):
        self.name = name
        loadModules(self.name)
        self.fd = 0
        self.device = device
        self.flag = flag
        self.open()
        
    def open(self):
        self.fd = os.open(self.device, self.flag)
        if self.fd < 0:
            raise Exception("Cannot open %s" % self.device)
        info("Using %s with %s" % (self.name, self.device))

    def close(self):
        if self.fd > 0:
            os.close(self.fd)
    
    def available(self):
        raise Exception("Not supported")
    
    def read(self, size=1):
        if self.fd > 0:
            return os.read(self.fd, size)
        return []
    
    def readBytes(self, size=1):
        return bytearray(self.read(size))
    
    def readByte(self):
        return self.readBytes()[0]

    def write(self, string):
        if self.fd > 0:
            return os.write(self.fd, string)
        return 0
    
    def writeBytes(self, *bytes):
        return self.write(bytearray(bytes))
    