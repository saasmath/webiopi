#!/bin/sh
# WebIOPi PiStore launch script

# Start WebIOPi service
sudo /etc/init.d/webiopi start

# Launch the browser
midori -c `pwd`/midori -a http://localhost:8000/

# Stop WebIOPi service
sudo /etc/init.d/webiopi stop
