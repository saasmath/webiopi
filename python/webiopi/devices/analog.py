from webiopi.utils import route
from webiopi.i2c import I2C
from webiopi.spi import SPI

class MCP3X0X(SPI):
    def __init__(self, spiChannel, resolution, channelCount):
        SPI.__init__(self, spiChannel, 0, 8, 10000, "MCP3%d0%d" % (resolution-10, channelCount))
        self.resolution = resolution
        self.channelCount = channelCount
        self.MSB_MASK = 2**(resolution-8) - 1
        self.MAX = (2**resolution - 1) * 1.0 

    @route("GET", "%(mcpChannel)/value")
    def readChannel(self, mcpChannel, diff=False):
        if not mcpChannel in range(self.channelCount):
            raise Exception("Channel %d out of MCP range [%d-%d]" % (mcpChannel, 0, self.channelCount-1))

        data = self.__command__(mcpChannel, diff)
        r = self.xfer(data)
        return ((r[1] & self.MSB_MASK) << 8) | r[2]
    
    @route("GET", "%(mcpChannel)d/scale")
    def scaleChannel(self, mcpChannel, diff=False):
        return self.readChannel(mcpChannel, diff) / self.MAX
    

class MCP300X(MCP3X0X):
    def __init__(self, spiChannel, channelCount):
        MCP3X0X.__init__(self, spiChannel, 10, channelCount)

    def __command__(self, mcpChannel, diff=False):
        d = [0x00, 0x00, 0x00]
        d[0] |= 1
        d[1] |= (not diff) << 7
        d[1] |= ((mcpChannel >> 2) & 0x01) << 6
        d[1] |= ((mcpChannel >> 1) & 0x01) << 5
        d[1] |= ((mcpChannel >> 0) & 0x01) << 4
        return d
        
class MCP3004(MCP300X):
    def __init__(self, spiChannel):
        MCP300X.__init__(self, spiChannel, 4)
        
class MCP3008(MCP300X):
    def __init__(self, spiChannel):
        MCP300X.__init__(self, spiChannel, 8)
        
class MCP320X(MCP3X0X):
    def __init__(self, spiChannel, channelCount):
        MCP3X0X.__init__(self, spiChannel, 12, channelCount)

    def __command__(self, mcpChannel, diff=False):
        d = [0x00, 0x00, 0x00]
        d[0] |= 1 << 2
        d[0] |= (not diff) << 1
        d[0] |= (mcpChannel >> 2) & 0x01
        d[1] |= ((mcpChannel >> 1) & 0x01) << 7
        d[1] |= ((mcpChannel >> 0) & 0x01) << 6
        return d
    
class MCP3204(MCP320X):
    def __init__(self, spiChannel=0):
        MCP320X.__init__(self, spiChannel, 4)
        
class MCP3208(MCP320X):
    def __init__(self, spiChannel=0):
        MCP320X.__init__(self, spiChannel, 8)
        
