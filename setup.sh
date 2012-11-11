#!/bin/sh
SEARCH="python python3"
FOUND=""
INSTALLED=""

echo "Installing WebIOPi...\n"

cd python

for python in $SEARCH; do
	program=`which $python`
	if [ -x $program ]; then
		FOUND="$FOUND $python"
		version=`$python -V 2>&1`
		include=`$python -c "import distutils.sysconfig; print(distutils.sysconfig.get_python_inc())"`
		echo "Found $version... " 
		if [ -f "$include/Python.h" ]; then
			$python setup.py install || (echo "Build for $version failed\n" && continue) 
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
	else
		echo "ERROR: WebIOPi cannot be installed - please install python development package first"
	fi
	exit
fi

echo -n "Copying resources... " 
mkdir /usr/share/webiopi 2>/dev/null 1>/dev/null
cp -rf htdocs /usr/share/webiopi
echo "OK\n"
echo "WebIOPi successfully installed"

for python in $INSTALLED; do
	version=`$python -V 2>&1`
	echo "* You can use it with $version\t: sudo $python -m webiopi"
done 
