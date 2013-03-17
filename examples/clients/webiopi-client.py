from webiopi import runLoop
from webiopi.clients import *
from time import sleep

client = PiHttpClient("192.168.1.234")
#client = PiMixedClient("192.168.1.234")
#client = PiCoapClient("192.168.1.234")

client.setCredentials("webiopi", "raspberry")

gpio = NativeGPIO(client)
gpio.setFunction(25, "out")
state = True

def loop(): 
    global gpio, state
    gpio.digitalWrite(25, state)
    state = not state
    sleep(0.5)

runLoop(loop)