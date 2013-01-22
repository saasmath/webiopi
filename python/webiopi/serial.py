import os
import sys
import fcntl
import struct
import termios

TIOCINQ   = hasattr(termios, 'FIONREAD') and termios.FIONREAD or 0x541B
TIOCM_zero_str = struct.pack('I', 0)

class Serial:
    def __init__(self, baudrate=9600, port="/dev/ttyAMA0"):
        aname = "B%d" % baudrate
        if not hasattr(termios, aname):
            raise Exception("Unsupported baudrate")
        speed = getattr(termios, aname)

        self.fd = os.open(port, os.O_RDWR | os.O_NOCTTY)# | os.O_NDELAY)
        
        if self.fd < 0:
            raise Exception("Cannot open %s" % port)
        
        fcntl.fcntl(self.fd, fcntl.F_SETFL, os.O_NDELAY)
        
        backup  = termios.tcgetattr(self.fd)
        options = termios.tcgetattr(self.fd)
        
        options[4] = speed # ispeed
        options[5] = speed # ospeed
        
        # cflags
        options[2] |= (termios.CLOCAL | termios.CREAD)
        options[2] &= ~termios.PARENB
        options[2] &= ~termios.CSTOPB
        options[2] &= ~termios.CSIZE
        options[2] |= termios.CS8
        
        termios.tcsetattr(self.fd, termios.TCSADRAIN, options)
    
    def close(self):
        os.close(self.fd)

    def available(self):
        s = fcntl.ioctl(self.fd, TIOCINQ, TIOCM_zero_str)
        return struct.unpack('I',s)[0]
        
    def read(self, size=1):
        return os.read(self.fd, size)
        
    def write(self, string):
        os.write(self.fd, string)
        
