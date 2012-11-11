# First import webiopi
import webiopi
import time

# I use the integrated GPIO lib, but you can use RPi.GPIO
GPIO = webiopi.GPIO

# A custom macro which prints out the arg received and return OK
def myMacro(arg):
    print("myMacro(%s)" % arg)
    return "OK"

# Instantiate the server on the port 8000, it starts immediately in its own thread
server = webiopi.Server(port=8000, login="webiopi", password="raspberry")

# Register the macro so you can call it through the [RESTAPI] or [JAVASCRIPT]
server.addMacro(myMacro)

# Setup GPIOs
GPIO.setFunction(1, GPIO.IN)
GPIO.setFunction(7, GPIO.OUT)
GPIO.setFunction(8, GPIO.PWM)
GPIO.setFunction(9, GPIO.PWM)

GPIO.pulseRatio(8, 0.5) # 50% duty cycle ratio
GPIO.pulseAngle(9, 0)   # neutral

# Example loop which toggle GPIO 9 each 5 seconds
try:
    while True:
        GPIO.output(7, not GPIO.input(7))
        time.sleep(5)        

# Break the loop by pressing CTRL-C
except KeyboardInterrupt:
    pass

# Stop the server
server.stop()

# Reset GPIO functions
GPIO.setFunction(1, GPIO.IN)
GPIO.setFunction(7, GPIO.IN)
GPIO.setFunction(8, GPIO.IN)
GPIO.setFunction(9, GPIO.IN)
