import os
import subprocess

class Bus():
    def __init__(self, modules, device, flag=os.O_RDWR):
        global modules_loaded
        self.modules = modules
        self.loadModules()
        self.fd = 0
        self.device = device
        self.flag = flag
        self.open()
        
        
    def loadModules(self):
        for module in self.modules:
            subprocess.call(["modprobe", module])
    
    def unloadModules(self):
        for module in self.modules:
            subprocess.call(["modprobe", "-r", module])
            
    def __moduleLoaded__(self, modules, lines):
        if len(modules) == 0:
            return True
        for line in lines:
            if modules[0].replace("-", "_") in line:
                return self.__moduleLoaded__(modules[1:], lines)
        return False
    
    def modulesLoaded(self):
        f = open("/proc/modules")
        c = f.read()
        f.close()
        lines = c.split("\n")
        return self.__moduleLoaded__(self.modules, lines)

    def open(self):
        self.fd = os.open(self.device, self.flag)
        if self.fd < 0:
            raise Exception("Cannot open %s" % self.device)

    def close(self):
        if self.fd > 0:
            os.close(self.fd)
    
    def available(self):
        raise Exception("Not supported")
    
    def read(self, size=1):
        if self.fd > 0:
            return os.read(self.fd, size)
        return []

    def write(self, bytes):
        if self.fd > 0:
            return os.write(self.fd, bytes)
        return 0
