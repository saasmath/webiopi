from webiopi import MulticastClient, runLoop
from time import sleep

client = MulticastClient()
client.setFunction(25, "out")
state = True

def loop():
    global client, state
    client.output(25, state)
    state = not state
    sleep(0.5)

runLoop(loop)
