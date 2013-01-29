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
# Macro definition part - Mapped to REST API         #
# -------------------------------------------------- #
# A custom macro which prints out the arg received and return OK
@webiopi.macro
def myMacroWithArgs(arg1, arg2, arg3):
    webiopi.debug("myMacroWithArgs(%s, %s, %s)" % (arg1, arg2, arg3))
    return "OK"

# A custom macro without args which return nothing
@webiopi.macro
def myMacroWithoutArgs():
    webiopi.debug("myMacroWithoutArgs()")


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
# Loop execution part - WebIOPi will call loop()     #
# -------------------------------------------------- #
# Example loop which toggle RELAY each 5 seconds
def loop():
    GPIO.output(RELAY, not GPIO.input(RELAY))
    webiopi.sleep(5)        

# -------------------------------------------------- #
# Termination part - WebIOPi will call destroy()     #
# -------------------------------------------------- #
def destroy():
    # Reset GPIO functions
    GPIO.setFunction(SWITCH, GPIO.IN)
    GPIO.setFunction(LED, GPIO.IN)
    GPIO.setFunction(SERVO, GPIO.IN)
    GPIO.setFunction(RELAY, GPIO.IN)
