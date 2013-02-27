from webiopi import runLoop
from webiopi.clients import *
from time import sleep

client = PiMixedClient("192.168.1.234")

gpio = NativeGPIO(client)
gpio.setFunction(25, "out")
state = True

def loop(): 
    global gpio, state
    gpio.output(25, state)
    state = not state
    sleep(0.5)

runLoop(loop)