/*
   Copyright 2012 Eric Ptak - trouch.com

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/

var PIN_COUNT = 26;

var TYPE = {
	DNC: {value: 0, style: "DNC"},
	GND: {value: 1, style: "GND"},
	V33: {value: 2, style: "V33"},
	V50: {value: 3, style: "V50"},
	GPIO: {value: 4, style: "GPIO"}
};

var ALT = {
	UART: {name: "UART", style: "UART", enabled: false, pins: []},
	I2C: {name: "I2C", style: "I2C", enabled: false, pins: []},
	SPI: {name: "SPI", style: "SPI", enabled: false, pins: []}
};

var PINS = Array(PIN_COUNT+1);
var GPIO = Array(PIN_COUNT);

function MAP(pin, pin_type, pin_value) {
	PINS[pin] = {type: pin_type, value: pin_value};
	if (pin_type.value == TYPE.GPIO.value) {
		GPIO[pin_value].rpin = pin;
	}
}

function MAP_ALT(alt, alt_pin, alt_gpio, alt_name) {
	alt.pins.push({pin: alt_pin, gpio: alt_gpio, name: alt_name});
}

function init_pinout() {
	for (var i=0; i<PIN_COUNT; i++) {
		GPIO[i] = Object();
	}

	MAP(1, TYPE.V33, "3.3V");	MAP(2, TYPE.V50, "5V");
	MAP(3, TYPE.GPIO, 0);		MAP(4, TYPE.DNC, "--");
	MAP(5, TYPE.GPIO, 1);		MAP(6, TYPE.GND, "GROUND");
	MAP(7, TYPE.GPIO, 4);		MAP(8, TYPE.GPIO, 14);
	MAP(9, TYPE.DNC, "--");	MAP(10, TYPE.GPIO, 15);
	MAP(11, TYPE.GPIO, 17);		MAP(12, TYPE.GPIO, 18);
	MAP(13, TYPE.GPIO, 21);		MAP(14, TYPE.DNC, "--");
	MAP(15, TYPE.GPIO, 22);		MAP(16, TYPE.GPIO, 23);
	MAP(17, TYPE.DNC, "--");	MAP(18, TYPE.GPIO, 24);
	MAP(19, TYPE.GPIO, 10);		MAP(20, TYPE.DNC, "--");
	MAP(21, TYPE.GPIO, 9);		MAP(22, TYPE.GPIO, 25);
	MAP(23, TYPE.GPIO, 11);		MAP(24, TYPE.GPIO, 8);
	MAP(25, TYPE.DNC, "--");	MAP(26, TYPE.GPIO, 7);

	MAP_ALT(ALT.UART, 8, 14, "TX");
	MAP_ALT(ALT.UART, 10, 15, "RX");

	MAP_ALT(ALT.I2C, 3, 0, "SDA");
	MAP_ALT(ALT.I2C, 5, 1, "SCL");

	MAP_ALT(ALT.SPI, 19, 10, "MOSI");
	MAP_ALT(ALT.SPI, 21, 9, "MISO");
	MAP_ALT(ALT.SPI, 23, 11, "SCLK");
	MAP_ALT(ALT.SPI, 24, 8, "CE0");
	MAP_ALT(ALT.SPI, 26, 7, "CE1");
	
}

function setPinLabel(pin, label) {
	$("#pin" + pin).val(label);
}

function updateGPIOValue(gpio, value) {
	GPIO[gpio].value = value;
	var style = (value == 1) ? "HIGH" : "LOW";
	$("#pin"+GPIO[gpio].rpin).attr("class", style);
}

function updateGPIODirection(gpio, direction) {
	GPIO[gpio].direction = direction;
	$("#direction"+GPIO[gpio].rpin).val(direction.toUpperCase());
}

function setGPIOValue(gpio, value) {
	$.post('GPIO/' + gpio + "/value/" + value, function(data) {
		updateGPIOValue(gpio, data);
	});
}

function setPinValue(pin, value) {
	if (PINS[pin].type.value == TYPE.GPIO.value) {
		var gpio = PINS[pin].value;
		setGPIOValue(gpio, value);
	}
}

function toggleValue(pin) {
	var gpio = PINS[pin].value;
	if ((PINS[pin].type.value == TYPE.GPIO.value) && (GPIO[gpio].direction=="out")) {
		var value = (GPIO[gpio].value == 1) ? 0 : 1;
		setGPIOValue(gpio, value);
	}
}

function setGPIODirection(gpio, value) {
	$.post('GPIO/' + gpio + "/direction/" + value, function(data) {
		updateGPIODirection(gpio, data);
	});
}

function setPinDirection(pin, value) {
	if (PINS[pin].type.value == TYPE.GPIO.value) {
		var gpio = PINS[pin].value;
		setGPIODirection(gpio, value);
	}
}

function toggleDirection(pin) {
	if (PINS[pin].type.value == TYPE.GPIO.value) {
		var gpio = PINS[pin].value;
		var value = (GPIO[gpio].direction == "in") ? "out" : "in";
		setGPIODirection(gpio, value)
	}
}

function getPinCell(pin) {
	var cell = $('<td align="center">');
	var button = $('<input type="submit">');
	button.attr("id", "pin"+pin);
	button.val(pin);
	button.attr("class", PINS[pin].type.style);
	button.bind("click", function(event) {
		toggleValue(pin);
	});
	cell.append(button);
	return cell;
}

function getName(pin) {
	if (PINS[pin].type.value != TYPE.GPIO.value) {
		return PINS[pin].value;
	}
	else {
		return "GPIO " + PINS[pin].value;
	}
}

function getNameCell(pin, align) {
	var cell = $('<td>');
	cell.attr("align", align);
	
	var div = $('<div>');
	div.attr("id", "name"+pin);
	div.attr("class", "pinName");
	div.append(getName(pin));
	
	cell.append(div);

	return cell;
}

function getDirectionCell(pin) {
	var cell = $('<td align="center">');
	if (PINS[pin].type.value == TYPE.GPIO.value) {
		var button = $('<input>');
		button.attr("id", "direction"+pin);
		button.attr("type", "submit");
		button.attr("class", "pinDirection_Enabled");
		button.val(GPIO[PINS[pin].value].direction);
		button.bind("click", function(event) {
			toggleDirection(pin);
		});
		cell.append(button);
	}
	return cell;
}

function setALT(alt, enable) {
	for (var p in alt.pins) {
		pin = alt.pins[p].pin;
		$("#name"+pin).empty();
		if (enable) {
			$("#name"+pin).append(alt.name + " " + alt.pins[p].name);
			$("#pin"+pin).attr("class", alt.style);
			$("#direction"+pin).attr("class", "pinDirection_Disabled");
		}
		else {
			$("#name"+pin).append(getName(pin));
			$("#pin"+pin).attr("class", TYPE.GPIO.style);
			$("#direction"+pin).attr("class", "pinDirection_Enabled");
		}
	}
	alt.enabled = enable;
}

function buildTable() {
	$("#webiopi").append($('<table>'));
	var table = $("#webiopi > table");
	for (var pin=1; pin<=26; pin++) {
		var line = 	$('<tr>');
		line.append(getDirectionCell(pin))
		line.append(getNameCell(pin, "right"))
		line.append(getPinCell(pin));

		pin++;
		line.append(getPinCell(pin));
		line.append(getNameCell(pin, "left"))
		line.append(getDirectionCell(pin))

		table.append(line);
	}
}

function updateUI() {
	$.getJSON("*", function(data) {
		setALT(ALT.UART, data["UART"]);
		setALT(ALT.I2C, data["I2C"]);
		setALT(ALT.SPI, data["SPI"]);
		
		$.each(data["GPIO"], function(gpio, data) {
		    if (data["mode"] == "GPIO") {
		    	updateGPIODirection(gpio, data["direction"]);
		    	updateGPIOValue(gpio, data["value"]);
		    }
		});
	});
	setTimeout(updateUI, 1000);
}

function webpi_init() {
	init_pinout();
	buildTable();
	updateUI();
}

$(document).ready(webpi_init);

var _gaq = _gaq || [];
_gaq.push(['_setAccount', 'UA-33979593-2']);
_gaq.push(['_trackPageview']);

(function() {
	var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
	ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
	var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
})();

