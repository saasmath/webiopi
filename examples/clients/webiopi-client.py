from webiopi import Client, runLoop
from time import sleep

client = Client("192.168.1.234")
client.setFunction(25, "out")
state = True

def loop(): 
    global client, state
    client.output(25, state)
    state = not state
    sleep(0.5)

runLoop(loop)