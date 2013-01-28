import os
import sys
import fcntl

from webiopi.bus import *
from webiopi.utils import *

# /dev/i2c-X ioctl commands.  The ioctl's parameter is always an
# unsigned long, except for:
#    - I2C_FUNCS, takes pointer to an unsigned long
#    - I2C_RDWR, takes pointer to struct i2c_rdwr_ioctl_data
#    - I2C_SMBUS, takes pointer to struct i2c_smbus_ioctl_data

I2C_RETRIES = 0x0701    # number of times a device address should
                        # be polled when not acknowledging
I2C_TIMEOUT = 0x0702    # set timeout in units of 10 ms

# NOTE: Slave address is 7 or 10 bits, but 10-bit addresses
# are NOT supported! (due to code brokenness)

I2C_SLAVE       = 0x0703    # Use this slave address
I2C_SLAVE_FORCE = 0x0706    # Use this slave address, even if it
                            # is already in use by a driver!
I2C_TENBIT      = 0x0704    # 0 for 7 bit addrs, != 0 for 10 bit

I2C_FUNCS       = 0x0705    # Get the adapter functionality mask

I2C_RDWR        = 0x0707    # Combined R/W transfer (one STOP only)

I2C_PEC         = 0x0708    # != 0 to use PEC with SMBus
I2C_SMBUS       = 0x0720    # SMBus transfer */


class I2C(Bus):
    def __init__(self, addr, name="I2C"):
        if isinstance(addr, str):
            if addr.startswith("0b"):
                addr = int(addr, 2)
            elif addr.startswith("0x"):
                addr = int(addr, 16)
            else:
                addr = int(addr)
        self.channel = 0
        if BOARD_REVISION > 1:
            self.channel = 1
        self.addr = addr
        self.name = name

        Bus.__init__(self, "I2C", "/dev/i2c-%d" % self.channel)
        
        if fcntl.ioctl(self.fd, I2C_SLAVE, self.addr):
            raise Exception("Error binding %s to I2C slave 0x%02X" % (self.name, self.addr))
        
    def __str__(self):
        return "%s(addr=0x%02X)" % (self.name, self.addr)
