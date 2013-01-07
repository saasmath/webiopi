#!/bin/sh
# WebIOPi PiStore launch script

# Start WebIOPi service
sudo /etc/init.d/webiopi start

# Launch the browser
midori http://localhost:8000/

# Stop WebIOPi service
sudo /etc/init.d/webiopi stop
