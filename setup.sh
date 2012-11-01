#!/bin/sh
cd python
python setup.py install || exit
cd ..
rm -rf /usr/share/webiopi
mkdir /usr/share/webiopi
cp -v -r htdocs /usr/share/webiopi/htdocs
cp -v -r doc /usr/share/webiopi/doc
cp -v python/webiopi.py.init /etc/init.d/webiopi
chmod a+x /etc/init.d/webiopi
