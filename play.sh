#!/bin/sh
# WebIOPi PiStore launch script

VERSION=`python -c "import webiopi; print(webiopi.VERSION)"`
if [ "$VERSION" != "0.5.3" ]; then
	echo "Update required..."
	sudo ./setup.sh
fi

# Start WebIOPi service
sudo /etc/init.d/webiopi start

# Launch the browser
midori -c `pwd`/midori -a http://localhost:8000/

# Stop WebIOPi service
sudo /etc/init.d/webiopi stop
