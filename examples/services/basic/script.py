# Imports
import webiopi
webiopi.setDebug()

# Retrieve GPIO lib
GPIO = webiopi.GPIO
SWITCH = 21
SERVO  = 23
LED0   = 24
LED1   = 25

# -------------------------------------------------- #
# Initialization part - WebIOPi will call setup()    #
# -------------------------------------------------- #
def setup():
    # Setup GPIOs
    GPIO.setFunction(SWITCH, GPIO.IN)
    GPIO.setFunction(SERVO, GPIO.PWM)
    GPIO.setFunction(LED0, GPIO.PWM)
    GPIO.setFunction(LED1, GPIO.OUT)
    
    GPIO.pulseAngle(SERVO, 0)   # init to neutral
    GPIO.pulseRatio(LED0, 0.5)  # init to 50% duty cycle ratio
    GPIO.output(LED1, GPIO.HIGH)

# -------------------------------------------------- #
# Termination part - WebIOPi will call destroy()     #
# -------------------------------------------------- #
def destroy():
    # Reset GPIO functions
    GPIO.setFunction(SWITCH, GPIO.IN)
    GPIO.setFunction(SERVO, GPIO.IN)
    GPIO.setFunction(LED0, GPIO.IN)
    GPIO.setFunction(LED1, GPIO.IN)
