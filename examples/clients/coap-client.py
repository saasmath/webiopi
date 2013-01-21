from webiopi import runLoop
from webiopi.coap import COAPClient, COAPPost
from time import sleep

client = COAPClient()
client.sendRequest(COAPPost("coap://224.0.1.123/GPIO/25/function/out"))
state = True

def loop(): 
    global client, state
    response = client.sendRequest(COAPPost("coap://224.0.1.123/GPIO/25/value/%d" % state))
    if response:
        print("Client received response")
        state = not state
    else:
        print("No response received")
    sleep(0.5)

runLoop(loop)
