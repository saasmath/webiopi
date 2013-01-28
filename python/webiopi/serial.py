import os
import sys
import fcntl
import struct
import termios

from webiopi.bus import *

TIOCINQ   = hasattr(termios, 'FIONREAD') and termios.FIONREAD or 0x541B
TIOCM_zero_str = struct.pack('I', 0)

class Serial(Bus):
    def __init__(self, baudrate=9600, device="/dev/ttyAMA0"):
        aname = "B%d" % baudrate
        if not hasattr(termios, aname):
            raise Exception("Unsupported baudrate")
        self.baudrate = baudrate

        Bus.__init__(self, "UART", device, os.O_RDWR | os.O_NOCTTY)
        fcntl.fcntl(self.fd, fcntl.F_SETFL, os.O_NDELAY)
        
        backup  = termios.tcgetattr(self.fd)
        options = termios.tcgetattr(self.fd)
        # iflag
        options[0] = 0

        # oflag
        options[1] = 0

        # cflag
        options[2] |= (termios.CLOCAL | termios.CREAD)
        options[2] &= ~termios.PARENB
        options[2] &= ~termios.CSTOPB
        options[2] &= ~termios.CSIZE
        options[2] |= termios.CS8

        # lflag
        options[3] = 0

        speed = getattr(termios, aname)
        # input speed
        options[4] = speed
        # output speed
        options[5] = speed
        
        termios.tcsetattr(self.fd, termios.TCSADRAIN, options)
        
    def __str__(self):
        return "Serial(%s, %dbps)" % (self.device, self.baudrate)
    
    def available(self):
        s = fcntl.ioctl(self.fd, TIOCINQ, TIOCM_zero_str)
        return struct.unpack('I',s)[0]
        
