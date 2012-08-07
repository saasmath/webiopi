WebIOPi let's you control your Pi's GPIO over a web interface.
- REST/JSON API
- Python server side (use RPi.GPIO)
- Full JavaScript client side (use jQuery)
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


You can use the API to make your own GUI or WebApp.
The API is currently limited to 3 features :
- Retrieve GPIO state/configuration :
	HTTP GET /*

- Setup GPIO pin :
	HTTP POST /GPIO/{pinNumber}/setup/{"IN", "OUT"}
	Returns new setup : {"IN", "OUT"}
	Examples:
		To set GPIO 0 in INPUT : HTTP POST /GPIO/0/setup/IN
		To set GPIO 1 in OUTPUT : HTTP POST /GPIO/1/setup/OUT


- Change GPIO value :
	HTTP POST /GPIO/{pinNumber}/value/{0, 1}
	Return new value : {0, 1}
	Examples:
		To raise GPIO 0 : HTTP POST /GPIO/0/value/1
		To fall GPIO 1 : HTTP POST /GPIO/1/value/0


©2012 trouch.com
