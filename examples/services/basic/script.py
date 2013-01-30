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
    GPIO.setup(SWITCH, GPIO.IN)
    GPIO.setup(SERVO, GPIO.PWM)
    GPIO.setup(LED0, GPIO.PWM)
    GPIO.setup(LED1, GPIO.OUT)
    
    GPIO.pulseAngle(SERVO, 0)   # init to neutral
    GPIO.pulseRatio(LED0, 0.5)  # init to 50% duty cycle ratio
    GPIO.output(LED1, GPIO.HIGH)

# -------------------------------------------------- #
# Termination part - WebIOPi will call destroy()     #
# -------------------------------------------------- #
def destroy():
    # Reset GPIO functions
    GPIO.setup(SWITCH, GPIO.IN)
    GPIO.setup(SERVO, GPIO.IN)
    GPIO.setup(LED0, GPIO.IN)
    GPIO.setup(LED1, GPIO.IN)
