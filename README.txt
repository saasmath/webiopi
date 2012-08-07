WebIOPi let's you control your Pi's GPIO over a web interface.
- REST/JSON API
- Server side available in differents technologies
	- PHP
	- Python server side (use RPi.GPIO)
- Full JavaScript client side (use jQuery)
- Smartphone compatible
- Auto-refresh

Only support binary GPIOs for now, in both input and output.
GPIOs 0 and 1 have input pull-up resistor enabled.
UART is enabled but unusable for now.
UART, SPI and I2C support will be added as soon as possible.
Don't forget that GPIO are 3.3V TTL, don't plug them to 5V !!!


WEB APP
-------
To use WebIOPi, install it, then open your browser/smartphone to your Pi's IP/hostname.
Click/Tap the OUT/IN button to change GPIO direction.
Click/Tap pins to change the GPIO output state.

WEB API
-------
You can use the API to make your own GUI or WebApp.
The API is currently limited to 3 features :
- Retrieve GPIO state/configuration :
	HTTP GET /*

- Setup GPIO pin :
	HTTP POST /GPIO/{pinNumber}/setup/{"in", "out"}
	Returns new setup : {"in", "out"}
	Examples:
		To set GPIO 0 in input : HTTP POST /GPIO/0/setup/out
		To set GPIO 1 in output : HTTP POST /GPIO/1/setup/out


- Change GPIO value :
	HTTP POST /GPIO/{pinNumber}/value/{0, 1}
	Return new value : {0, 1}
	Examples:
		To raise GPIO 0 : HTTP POST /GPIO/0/value/1
		To fall GPIO 1 : HTTP POST /GPIO/1/value/0


©2012 trouch.com
