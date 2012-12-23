#!/bin/sh
SEARCH="python python3"
FOUND=""
INSTALLED=""

echo "Installing WebIOPi...\n"

cd python

for python in $SEARCH; do
	program="/usr/bin/$python"
	if [ -x $program ]; then
		FOUND="$FOUND $python"
		version=`$python -V 2>&1`
		include=`$python -c "import distutils.sysconfig; print(distutils.sysconfig.get_python_inc())"`
		echo "Found $version... "

		if [ ! -f "$include/Python.h" ]; then
			echo "Trying to install $python-dev using apt-get"
			apt-get install -y "$python-dev"
		fi

		if [ -f "$include/Python.h" ]; then
			echo "Trying to install WebIOPi for $version"
			$python setup.py install
			if [ "$?" -ne "0" ]; then
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

cd ..

if [ -z "$INSTALLED" ]; then
	if [ -z "$FOUND" ]; then
		echo "ERROR: WebIOPi cannot be installed - neither python or python3 found"
		exit 1
	else
		echo "ERROR: WebIOPi cannot be installed - please check errors above"
		exit 2
	fi
fi

for python in $INSTALLED; do
	echo $python > /dev/null
done 

echo "Copying resources..."
mkdir /usr/share/webiopi 2>/dev/null 1>/dev/null
cp -rf htdocs /usr/share/webiopi
cp -rf python/webiopi.py.init /etc/init.d/webiopi
echo
echo "Setting up startup script..."
chmod 0755 /etc/init.d/webiopi
sed -i "s/python/$python/g" /etc/init.d/webiopi
update-rc.d webiopi defaults
echo
echo "Starting WebIOPi..."
/etc/init.d/webiopi restart
echo
echo "WebIOPi successfully installed, open a browser to http://localhost:8000/"
