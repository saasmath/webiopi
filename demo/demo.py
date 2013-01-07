# Imports
import webiopi
import time

# Retrieve GPIO lib
GPIO = webiopi.GPIO

# -------------------------------------------------- #
# Macro definition part                              #
# -------------------------------------------------- #

# A custom macro which prints out the arg received and return OK
def myMacroWithArgs(arg1, arg2, arg3):
    print("myMacroWithArgs(%s, %s, %s)" % (arg1, arg2, arg3))
    return "OK"

# A custom macro without args which return nothing
def myMacroWithoutArgs():
    print("myMacroWithoutArgs()")

# Example loop which toggle GPIO 7 each 5 seconds
def loop():
    GPIO.output(7, not GPIO.input(7))
    time.sleep(5)        

# -------------------------------------------------- #
# Initialization part                                #
# -------------------------------------------------- #

# Setup GPIOs
GPIO.setFunction(1, GPIO.IN)
GPIO.setFunction(7, GPIO.OUT)
GPIO.setFunction(8, GPIO.PWM)
GPIO.setFunction(9, GPIO.PWM)

GPIO.pulseRatio(8, 0.5) # init to 50% duty cycle ratio
GPIO.pulseAngle(9, 0)   # init to neutral

# -------------------------------------------------- #
# Main server part                                   #
# -------------------------------------------------- #

# Instantiate the server on the port 8000, it starts immediately in its own thread
server = webiopi.Server(port=8000, login="webiopi", password="raspberry")
# or     webiopi.Server(port=8000, passwdfile="/etc/webiopi/passwd")

# Register the macros so you can call it with Javascript and/or REST API
server.addMacro(myMacroWithArgs)
server.addMacro(myMacroWithoutArgs)


# -------------------------------------------------- #
# Loop execution part                                #
# -------------------------------------------------- #

# Run our loop until CTRL-C is pressed or SIGTERM received
webiopi.runLoop(loop)

# If no specific loop is needed and defined above, just use 
# webiopi.runLoop()
# here instead

# -------------------------------------------------- #
# Termination part                                   #
# -------------------------------------------------- #

# Cleanly stop the server
server.stop()

# Reset GPIO functions
GPIO.setFunction(1, GPIO.IN)
GPIO.setFunction(7, GPIO.IN)
GPIO.setFunction(8, GPIO.IN)
GPIO.setFunction(9, GPIO.IN)
