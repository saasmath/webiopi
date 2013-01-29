# Imports
import webiopi
webiopi.setInfo()

# Retrieve GPIO lib
GPIO = webiopi.GPIO

# -------------------------------------------------- #
# Initialization part                                #
# -------------------------------------------------- #

# Setup GPIOs
GPIO.setFunction(21, GPIO.IN)
GPIO.setFunction(22, GPIO.OUT)
GPIO.setFunction(23, GPIO.PWM)
GPIO.setFunction(24, GPIO.PWM)

GPIO.output(22, GPIO.HIGH)
GPIO.pulseRatio(23, 0.5) # init to 50% duty cycle ratio
GPIO.pulseAngle(24, 0)   # init to neutral

# -------------------------------------------------- #
# Main server part                                   #
# -------------------------------------------------- #

# Instantiate the server on the port 8000, it starts immediately in its own thread
server = webiopi.Server(port=8000, login="webiopi", password="raspberry")
# or     webiopi.Server(port=8000, passwdfile="/etc/webiopi/passwd")

# -------------------------------------------------- #
# Loop execution part                                #
# -------------------------------------------------- #

# Run our loop until CTRL-C is pressed or SIGTERM received
webiopi.runLoop()

# -------------------------------------------------- #
# Termination part                                   #
# -------------------------------------------------- #

# Cleanly stop the server
server.stop()

# Reset GPIO functions
GPIO.setFunction(21, GPIO.IN)
GPIO.setFunction(22, GPIO.IN)
GPIO.setFunction(23, GPIO.IN)
GPIO.setFunction(24, GPIO.IN)
