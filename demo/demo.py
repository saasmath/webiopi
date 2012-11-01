import webiopi
import RPi.GPIO as gpio
import time

def myFunction(data):
    print "myFunction (%s)" % data
    return "OK"

if __name__ == "__main__":
    server = webiopi.Server()
    server.addFunction("myFunction", myFunction)
    
    gpio.setmode(gpio.BCM)
    gpio.setup(7, gpio.OUT)
    
    try:
        while True:
            gpio.output(7, 1)
            time.sleep(5)
            gpio.output(7, 0)
            time.sleep(5)
    except KeyboardInterrupt:
        pass
    
    server.stop()
    gpio.setup(7, gpio.IN)

