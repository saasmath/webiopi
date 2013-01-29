# Imports
import webiopi
webiopi.setDebug()

# Retrieve GPIO lib
GPIO = webiopi.GPIO
SWITCH = 21
LED    = 23
SERVO  = 24
RELAY  = 25

# -------------------------------------------------- #
# Initialization part - WebIOPi will call setup()    #
# -------------------------------------------------- #
def setup():
    # Setup GPIOs
    GPIO.setFunction(SWITCH, GPIO.IN)
    GPIO.setFunction(LED, GPIO.PWM)
    GPIO.setFunction(SERVO, GPIO.PWM)
    GPIO.setFunction(RELAY, GPIO.OUT)
    
    GPIO.pulseRatio(LED, 0.5) # init to 50% duty cycle ratio
    GPIO.pulseAngle(SERVO, 0)   # init to neutral
    GPIO.output(RELAY, GPIO.HIGH)

# -------------------------------------------------- #
# Termination part - WebIOPi will call destroy()     #
# -------------------------------------------------- #
def destroy():
    # Reset GPIO functions
    GPIO.setFunction(SWITCH, GPIO.IN)
    GPIO.setFunction(LED, GPIO.IN)
    GPIO.setFunction(SERVO, GPIO.IN)
    GPIO.setFunction(RELAY, GPIO.IN)
