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
server = webiopi.Server(port=8000, login="demo", password="demo")

# Register the macro so you can call it through the [RESTAPI] or [JAVASCRIPT]
server.addMacro(myMacro)

# Setup GPIOs
GPIO.setFunction(7, GPIO.IN)
GPIO.setFunction(9, GPIO.OUT)
GPIO.setFunction(10, GPIO.OUT)
GPIO.setFunction(11, GPIO.OUT)

# Enable PWM
GPIO.enablePWM(10)
GPIO.enablePWM(11)

# output PWM
GPIO.pulseRatio(10, 0.25) # 25% duty cycle on GPIO 10 (float ratio from 0.0 to 1.0)
GPIO.pulseAngle(11, 0)    # servo neutral on GPIO 11 (float angle from -45 to +45)

# Example loop which toggle GPIO 9 each 5 seconds
try:
    while True:
        GPIO.output(9, not GPIO.input(9))
        time.sleep(5)        

# Break the loop by pressing CTRL-C
except KeyboardInterrupt:
    pass

# Stops the server
server.stop()

# Disable PWM
GPIO.disablePWM(10)
GPIO.disablePWM(11)

# Reset GPIO functions
GPIO.setFunction(7, GPIO.IN)
GPIO.setFunction(9, GPIO.IN)
GPIO.setFunction(10, GPIO.IN)
GPIO.setFunction(11, GPIO.IN)
