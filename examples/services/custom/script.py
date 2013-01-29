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
    GPIO.setFunction(SERVO, GPIO.PWM)
    GPIO.setFunction(LED0, GPIO.PWM)
    GPIO.setFunction(LED1, GPIO.OUT)
    
    GPIO.pulseAngle(SERVO, 0)   # init to neutral
    GPIO.pulseRatio(LED0, 0.5)  # init to 50% duty cycle ratio
    GPIO.output(LED1, GPIO.HIGH)

# -------------------------------------------------- #
# Loop execution part - WebIOPi will call loop()     #
# -------------------------------------------------- #
# Example loop which toggle LED each 5 seconds
def loop():
    GPIO.output(LED1, not GPIO.input(LED1))
    webiopi.sleep(5)        

# -------------------------------------------------- #
# Termination part - WebIOPi will call destroy()     #
# -------------------------------------------------- #
def destroy():
    # Reset GPIO functions
    GPIO.setFunction(SWITCH, GPIO.IN)
    GPIO.setFunction(SERVO, GPIO.IN)
    GPIO.setFunction(LED0, GPIO.IN)
    GPIO.setFunction(LED1, GPIO.IN)
