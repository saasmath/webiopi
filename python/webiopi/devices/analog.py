from webiopi.i2c import I2C
from webiopi.spi import SPI
from webiopi.rest import route

class MCP3X0X(SPI):
    def __init__(self, chip, resolution, channelCount):
        SPI.__init__(self, chip, 0, 8, 10000, "MCP3%d0%d" % (resolution-10, channelCount))
        self.resolution = resolution
        self.channelCount = channelCount
        self.MSB_MASK = 2**(resolution-8) - 1
        self.MAX = (2**resolution - 1) * 1.0 

    def __str__(self):
        return "%s(chip=%d)" % (self.name, self.chip)

    @route("GET", "%(adcChannel)d/integer", "%d")
    def readInteger(self, adcChannel, diff=False):
        if not adcChannel in range(self.channelCount):
            raise Exception("Channel %d out of range [%d-%d]" % (adcChannel, 0, self.channelCount-1))

        data = self.__command__(adcChannel, diff)
        r = self.xfer(data)
        return ((r[1] & self.MSB_MASK) << 8) | r[2]
    
    @route("GET", "%(adcChannel)d/float", "%.02f")
    def readFloat(self, adcChannel, diff=False):
        return self.readInteger(adcChannel, diff) / self.MAX
    

class MCP300X(MCP3X0X):
    def __init__(self, chip, channelCount):
        MCP3X0X.__init__(self, chip, 10, channelCount)

    def __command__(self, mcpChannel, diff=False):
        d = [0x00, 0x00, 0x00]
        d[0] |= 1
        d[1] |= (not diff) << 7
        d[1] |= ((mcpChannel >> 2) & 0x01) << 6
        d[1] |= ((mcpChannel >> 1) & 0x01) << 5
        d[1] |= ((mcpChannel >> 0) & 0x01) << 4
        return d
        
class MCP3004(MCP300X):
    def __init__(self, chip):
        MCP300X.__init__(self, chip, 4)
        
class MCP3008(MCP300X):
    def __init__(self, chip):
        MCP300X.__init__(self, chip, 8)
        
class MCP320X(MCP3X0X):
    def __init__(self, chip, channelCount):
        MCP3X0X.__init__(self, chip, 12, channelCount)

    def __command__(self, mcpChannel, diff=False):
        d = [0x00, 0x00, 0x00]
        d[0] |= 1 << 2
        d[0] |= (not diff) << 1
        d[0] |= (mcpChannel >> 2) & 0x01
        d[1] |= ((mcpChannel >> 1) & 0x01) << 7
        d[1] |= ((mcpChannel >> 0) & 0x01) << 6
        return d
    
class MCP3204(MCP320X):
    def __init__(self, chip=0):
        MCP320X.__init__(self, chip, 4)
        
class MCP3208(MCP320X):
    def __init__(self, chip=0):
        MCP320X.__init__(self, chip, 8)
        
class MCP492X(SPI):
    def __init__(self, chip, channelCount):
        SPI.__init__(self, chip, 0, 8, 10000, "MCP492%d" % channelCount)
        self.channelCount = channelCount
        self.buffered=False
        self.gain=False
        self.shutdown=False

    def __str__(self):
        return "%s(chip=%d)" % (self.name, self.chip)

    @route("POST", "%(dacChannel)d/integer/%(value)d")        
    def writeInteger(self, dacChannel, value):
        if not dacChannel in range(self.channelCount):
            raise Exception("Channel %d out of range [%d-%d]" % (dacChannel, 0, self.channelCount-1))

        d = bytearray(2)
        d[0]  = 0
        d[0] |= (dacChannel & 0x01) << 7
        d[0] |= (self.buffered & 0x01) << 6
        d[0] |= (not self.gain & 0x01) << 5
        d[0] |= (not self.shutdown & 0x01) << 4
        d[0] |= (value >> 8) & 0x0F
        d[1]  = value & 0xFF
        self.writeBytes(d)
    
    @route("POST", "%(dacChannel)d/float/%(value)f")        
    def writeFloat(self, dacChannel, value):
        self.writeInteger(dacChannel, int(value * 4095))
        
class MCP4921(MCP492X):
    def __init__(self, chip=0):
        MCP492X.__init__(self, chip, 1)

class MCP4922(MCP492X):
    def __init__(self, chip=0):
        MCP492X.__init__(self, chip, 2)
