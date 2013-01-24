import os
import sys
import fcntl

from .bus import *

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
    def __init__(self, channel, addr):
        Bus.__init__(self, ["i2c-bcm2708", "i2c-dev"], "/dev/i2c-%d" % channel)
        self.addr = addr
        
    def connect(self):
        self.open()
        if fcntl.ioctl(self.fd, I2C_SLAVE, self.addr) < 0:
            self.close()
            raise Exception("No I2C slave at 0x%02X" % self.addr)
    
    def read(self, size=1):
        self.connect()
        data = Bus.read(self, size)
        self.close()
        return data
    
    def write(self, bytes):
        self.connect()
        Bus.write(self, bytes)
        self.close()
        
    