WebIOPi let's you control your Pi's GPIO over a web interface.

Features :
----------
- REST/JSON API
- Server side available in differents technologies
	- PHP
	- Python (use RPi.GPIO)
- Full JavaScript client side (use jQuery)
- Smartphone compatible
- Auto-refresh

Restrictions :
--------------
- Only support binary GPIOs for now, in both input and output.
- GPIOs 0 and 1 have input pull-up resistor enabled.
- UART is enabled but unusable for now.
- UART, SPI and I2C support will be added as soon as possible.
- Don't forget that GPIO are 3.3V TTL, don't plug them to 5V !!!


Web App :
---------
To use WebIOPi, install it, then open your browser to your Pi's IP/hostname.
Click/Tap the OUT/IN button to change GPIO direction.
Click/Tap pins to change the GPIO output state.

Web API :
---------
You can use the API to make your own GUI or WebApp.
The API is currently limited to 3 features :
- Retrieve GPIO state/configuration :
	HTTP GET /*
	Returns full GPIO state in JSON
	{"UART": 1, "I2C": 0, "SPI": 0, "GPIO":{
"0": {"mode": "GPIO", "direction": "in", "value": 1}, 
"1": {"mode": "GPIO", "direction": "in", "value": 0}, 
"4": {"mode": "GPIO", "direction": "out", "value": 1}, 
"7": {"mode": "GPIO", "direction": "out", "value": 0}, 
"8": {"mode": "GPIO", "direction": "out", "value": 0}, 
"9": {"mode": "GPIO", "direction": "ou", "value": 0}, 
"10": {"mode": "GPIO", "direction": "out", "value": 0}, 
"11": {"mode": "GPIO", "direction": "out", "value": 0}, 
"14": {"mode": "ALT", "direction": "out", "value": 0}, 
"15": {"mode": "ALT", "direction": "out", "value": 0}, 
"17": {"mode": "GPIO", "direction": "out", "value": 0}, 
"18": {"mode": "GPIO", "direction": "out", "value": 0}, 
"21": {"mode": "GPIO", "direction": "out", "value": }, 
"22": {"mode": "GPIO", "direction": "out", "value": 0}, 
"23": {"mode": "GPIO", "direction": "out", "value": 0}, 
"24": {"mode": "GPIO", "direction": "out", "value": 0}, 
"25": {"mode": "GPIO", "direction": "out", "value": 0}
}}

- Setup GPIO direction :
	HTTP POST /GPIO/(pinNumber)/direction/("in" or "out")
	Returns new direction : "in" or "out"
	Examples:
		To set GPIO 0 in input : HTTP POST /GPIO/0/direction/in
			Returns "in"
		To set GPIO 1 in output : HTTP POST /GPIO/1/direction/out
			Returns "out"


- Change GPIO value :
	HTTP POST /GPIO/(pinNumber)/value/(0 or 1)
	Returns new value : 0 or 1
	Examples:
		To raise GPIO 0 : HTTP POST /GPIO/0/value/1
			Returns 1
		To fall GPIO 1 : HTTP POST /GPIO/1/value/0
			Return 0


------------------------------------------------------------------------------

   Copyright 2012 trouch.com

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.


