#!/bin/sh
# WebIOPi setup script

SEARCH="python python3"
FOUND=""
INSTALLED=""

echo "Installing WebIOPi...\n"

# Install Python library
cd python

# Look up for installed python
for python in $SEARCH; do
	program="/usr/bin/$python"
	if [ -x $program ]; then
		FOUND="$FOUND $python"
		version=`$python -V 2>&1`
		include=`$python -c "import distutils.sysconfig; print(distutils.sysconfig.get_python_inc())"`
		echo "Found $version... "

		# Install required dev header if not present
		if [ ! -f "$include/Python.h" ]; then
			echo "Trying to install $python-dev using apt-get"
			apt-get update
			apt-get install -y "$python-dev"
		fi

		# Try to compile and install for the current python
		if [ -f "$include/Python.h" ]; then
			echo "Trying to install WebIOPi for $version"
			$python setup.py install
			if [ "$?" -ne "0" ]; then
				# Sub setup error, continue with next python
				echo "Build for $version failed\n"
				continue
			fi
			echo "WebIOPi installed for $version\n"
			INSTALLED="$INSTALLED $python"
		else
			echo "Cannot install for $version : missing development headers\n"
		fi
	fi
done

# Go back to the root folder
cd ..

# Ensure WebIOPi is installed to continue
if [ -z "$INSTALLED" ]; then
	if [ -z "$FOUND" ]; then
		echo "ERROR: WebIOPi cannot be installed - neither python or python3 found"
		exit 1
	else
		echo "ERROR: WebIOPi cannot be installed - please check errors above"
		exit 2
	fi
fi

# Select greater python version
for python in $INSTALLED; do
	echo $python > /dev/null
done

echo "Copying resources..."
mkdir /usr/share/webiopi 2>/dev/null 1>/dev/null
cp -rfv htdocs /usr/share/webiopi

# Add config file if it does not exist
if [ ! -f "/etc/webiopi/config" ]; then
	echo "Config file not found, copying..."
	mkdir /etc/webiopi 2>/dev/null 1>/dev/null
	cp -v python/config /etc/webiopi/config
fi
echo

# Add passwd file if it does not exist
if [ ! -f "/etc/webiopi/passwd" ]; then
	echo "Passwd file not found, copying..."
	mkdir /etc/webiopi 2>/dev/null 1>/dev/null
	cp -v python/passwd /etc/webiopi/passwd
fi
echo

# Add service/daemon script
#if [ ! -f "/etc/init.d/webiopi" ]; then
echo "Setting up startup script..."
cp -rf python/webiopi.py.init /etc/init.d/webiopi
chmod 0755 /etc/init.d/webiopi
sed -i "s/python/$python/g" /etc/init.d/webiopi
echo

# Add webiopi-passwd command
cp -rf python/webiopi-passwd.py /usr/bin/webiopi-passwd
sed -i "s/python/$python/g" /usr/bin/webiopi-passwd
chmod 0755 /usr/bin/webiopi-passwd

# Display WebIOPi usages
echo "WebIOPi successfully installed"
for python in $INSTALLED; do
        echo "* To start WebIOPi with $python\t: sudo $python -m webiopi [-v] [-h] [-c config] [-l log] [port]"
done
echo
echo "* To start WebIOPi at boot\t: sudo update-rc.d webiopi defaults"
echo "* To start WebIOPi service\t: sudo /etc/init.d/webiopi start"
echo
echo "* Look in `pwd`/examples for Python library usage examples"
echo
