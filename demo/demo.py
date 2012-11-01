import webiopi
import time

GPIO = webiopi.GPIO

def myFunction(data):
    print "myFunction (%s)" % data
    return "OK"

server = webiopi.Server()
server.addFunction("myFunction", myFunction)

GPIO.setFunction(7, GPIO.OUT)

try:
    while True:
        GPIO.output(7, 1)
        time.sleep(5)
        GPIO.output(7, 0)
        time.sleep(5)
except KeyboardInterrupt:
    pass

server.stop()
GPIO.setFunction(7, GPIO.IN)
