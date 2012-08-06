WebIOPi let's you control your Pi's GPIO over a web interface.
- Python server side
- Full JavaScript client side
- Smartphone compatible
- Auto-refresh

Only support binary GPIOs for now, in both input and output.
GPIOs 0 and 1 have input pull-up resistor enabled.
UART is enabled but unusable for now.
UART, SPI and I2C support will be added as soon as possible.
Don't forget that GPIO are 3.3V TTL, don't plug them to 5V !!!

To use WebIOPi, is very simple : 
Open a terminal in the directory you extracted WebIOPi, and start the server process with root/sudo : 
$ python webiopi.py [port]
or
$ ./webiopy.py [port]
where port is the port to bind the HTTP server, default is 80, but maybe used by Apache.

Then point you browser/smartphone to your Pi's IP/hostname.
Click/Tap the OUT/IN button to change GPIO behaviours.
Click/Tap pins to change the GPIO output state.

©2012 trouch.com