from webiopi import runLoop
from webiopi.clients import *
from time import sleep

client = PiMulticastClient()

gpio = NativeGPIO(client)
gpio.setFunction(25, "out")
state = True

def loop(): 
    global gpio, state
    gpio.digitalWrite(25, state)
    state = not state
    sleep(0.5)

runLoop(loop)
