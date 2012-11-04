import webiopi
import time

GPIO = webiopi.GPIO

def myMacro(data):
    print "myMacro (%s)" % data
    return "OK"

server = webiopi.Server()
server.addMacro("myMacro", myMacro)

GPIO.setFunction(0, GPIO.IN)
GPIO.setFunction(7, GPIO.OUT)

try:
    while True:
        GPIO.output(7, not GPIO.input(7))
        time.sleep(5)
except KeyboardInterrupt:
    pass

server.stop()
GPIO.setFunction(7, GPIO.IN)
