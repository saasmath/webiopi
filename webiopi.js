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

var _gaq = _gaq || [];
var _webiopi;

function w() {
	if (_webiopi == undefined) {
		_webiopi = new WebIOPi();
	}
	
	return _webiopi;
}

function webiopi() {
	return w();
}

function WebIOPi() {
	this.context = "/webiopi/";
	this.GPIO = Array(26);
	this.ALT = {
			UART: {name: "UART", enabled: false, gpios: []},
			I2C: {name: "I2C", enabled: false, gpios: []},
			SPI: {name: "SPI", enabled: false, gpios: []}
		};
		
	// get context
	var scripts = document.getElementsByTagName("script");
	var reg = new RegExp("http://" + window.location.host + "(.*)webiopi.js");
	for(var i = 0; i < scripts.length; i++) {
		var res = reg.exec(scripts[i].src);
		if (res && (res.length > 1)) {
			this.context = res[1];
			
		}
	}

	// init GPIOs
	for (var i=0; i<this.GPIO.length; i++) {
		var gpio = Object();
		gpio.value = 0;
		gpio.direction = "in";
		this.GPIO[i] = gpio;
	}
	
	
	// init ALTs
	this.addALT(this.ALT.UART, 14, "TX");
	this.addALT(this.ALT.UART, 15, "RX");

	this.addALT(this.ALT.I2C, 0, "SDA");
	this.addALT(this.ALT.I2C, 1, "SCL");

	this.addALT(this.ALT.SPI, 10, "MOSI");
	this.addALT(this.ALT.SPI,  9, "MISO");
	this.addALT(this.ALT.SPI, 11, "SCLK");
	this.addALT(this.ALT.SPI,  8, "CE0");
	this.addALT(this.ALT.SPI,  7, "CE1");
	
	// GA
	_gaq.push(['_setAccount', 'UA-33979593-2']);
	_gaq.push(['_trackPageview']);
		
	var ga = document.createElement('script');
	ga.type = 'text/javascript';
	ga.async = false;
	ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';

	scripts[0].parentNode.insertBefore(ga, scripts[0]);
	
	// schedule UpdateUI and CheckVersion
	setTimeout(this.updateUI, 100);
	setTimeout(this.checkVersion, 100);
}

WebIOPi.prototype.addALT = function (alt, gpio, name) {
	var o = Object();
	o.gpio = gpio;
	o.name = name;
	alt.gpios.push(o);
}

WebIOPi.prototype.updateValue = function (gpio, value) {
	this.GPIO[gpio].value = value;
	var style = (value == 1) ? "HIGH" : "LOW";
	$("#gpio"+gpio).attr("class", style);
}

WebIOPi.prototype.setValue = function (gpio, value) {
	if (this.GPIO[gpio].direction=="out") {
		$.post(this.context + 'GPIO/' + gpio + "/value/" + value, function(data) {
			w().updateValue(gpio, data);
		});
	}
}

WebIOPi.prototype.toggleValue = function (gpio) {
	var value = (this.GPIO[gpio].value == 1) ? 0 : 1;
	this.setValue(gpio, value);
}

WebIOPi.prototype.createGPIOButton = function (gpio, label) {
	var button = $('<input type="submit">');
	button.attr("id", "gpio"+gpio);
	button.val(label);
	button.bind("click", function(event) {
		w().toggleValue(gpio);
	});
	return button;
}

WebIOPi.prototype.setLabel = function (gpio, label) {
	$("#gpio" + gpio).val(label);
}

WebIOPi.prototype.updateDirection = function (gpio, direction) {
	this.GPIO[gpio].direction = direction;
	$("#direction"+gpio).val(direction.toUpperCase());
}

WebIOPi.prototype.setDirection = function (gpio, value) {
	$.post(this.context + 'GPIO/' + gpio + "/direction/" + value, function(data) {
		w().updateDirection(gpio, data);
	});
}

WebIOPi.prototype.toggleDirection = function (gpio) {
	var value = (this.GPIO[gpio].direction == "in") ? "out" : "in";
	this.setDirection(gpio, value)
}

WebIOPi.prototype.createDirectionButton = function (gpio) {
	var button = $('<input>');
	button.attr("id", "direction"+gpio);
	button.attr("type", "submit");
	button.attr("class", "DirectionEnabled");
	button.val("");
	button.bind("click", function(event) {
		w().toggleDirection(gpio);
	});
	return button;
}

WebIOPi.prototype.updateALT = function (alt, enable) {
	for (var p in alt.gpios) {
		gpio = alt.gpios[p].gpio;
		$("#description"+gpio).empty();
		if (enable) {
			$("#description"+gpio).append(alt.name + " " + alt.gpios[p].name);
			$("#gpio"+gpio).attr("class", alt.name);
			$("#direction"+gpio).attr("class", "DirectionDisabled");
		}
		else {
			$("#description"+gpio).append("GPIO " + gpio);
			$("#gpio"+gpio).attr("class", "");
			$("#direction"+gpio).attr("class", "DirectionEnabled");
		}
	}
	alt.enabled = enable;
}

WebIOPi.prototype.updateUI = function () {
	$.getJSON(w().context + "*", function(data) {
		w().updateALT(w().ALT.UART, data["UART"]);
		w().updateALT(w().ALT.I2C, data["I2C"]);
		w().updateALT(w().ALT.SPI, data["SPI"]);
		
		$.each(data["GPIO"], function(gpio, data) {
		    if (data["mode"] == "GPIO") {
		    	w().updateDirection(gpio, data["direction"]);
		    	w().updateValue(gpio, data["value"]);
		    }
		});
	});
	setTimeout(w().updateUI, 1000);
}


WebIOPi.prototype.checkVersion = function () {
	var version;
	
	$.get(w().context + "version", function(data) {
		_gaq.push(['_trackEvent', 'version', data]);
		version = data.split("/")[2];

		$.get("http://trouch.com/version.php", function(data) {
			var lines = data.split("\n");
			var c = version.split(".");
			var n = lines[0].split(".");
			var updated = false;
			for (i=0; i<Math.min(c.length, n.length); i++) {
				if (n[i]>c[i]) {
					updated = true;
				}
			}
			if (updated || (n.length > c.length)) {
				var div = $('<div id="update"><a href="' + lines[1] + '">Update available</a></div>');
				$("body").append(div);
			}
		});
	});
}

WebIOPi.prototype.RPiHeader = function () {
	if (this._header == undefined) {
		this._header = new RPiHeader();
	}
	return this._header;
}

function RPiHeader() {
	this.PINS = Array(27);

	this.TYPE = {
			DNC: {value: 0, style: "DNC"},
			GND: {value: 1, style: "GND"},
			V33: {value: 2, style: "V33"},
			V50: {value: 3, style: "V50"},
			GPIO: {value: 4, style: "GPIO"}
	};

	this.map(1, this.TYPE.V33, "3.3V");	this.map(2, this.TYPE.V50, "5V");
	this.map(3, this.TYPE.GPIO, 0);		this.map(4, this.TYPE.DNC, "--");
	this.map(5, this.TYPE.GPIO, 1);		this.map(6, this.TYPE.GND, "GROUND");
	this.map(7, this.TYPE.GPIO, 4);		this.map(8, this.TYPE.GPIO, 14);
	this.map(9, this.TYPE.DNC, "--");	this.map(10, this.TYPE.GPIO, 15);
	this.map(11, this.TYPE.GPIO, 17);	this.map(12, this.TYPE.GPIO, 18);
	this.map(13, this.TYPE.GPIO, 21);	this.map(14, this.TYPE.DNC, "--");
	this.map(15, this.TYPE.GPIO, 22);	this.map(16, this.TYPE.GPIO, 23);
	this.map(17, this.TYPE.DNC, "--");	this.map(18, this.TYPE.GPIO, 24);
	this.map(19, this.TYPE.GPIO, 10);	this.map(20, this.TYPE.DNC, "--");
	this.map(21, this.TYPE.GPIO, 9);	this.map(22, this.TYPE.GPIO, 25);
	this.map(23, this.TYPE.GPIO, 11);	this.map(24, this.TYPE.GPIO, 8);
	this.map(25, this.TYPE.DNC, "--");	this.map(26, this.TYPE.GPIO, 7);
}

RPiHeader.prototype.getPinCell = function (pin) {
	var cell = $('<td align="center">');
	var button;
	if (this.PINS[pin].type.value == this.TYPE.GPIO.value) {
		button = w().createGPIOButton(this.PINS[pin].value, pin);
	}
	else {
		var button = $('<input type="submit">');
		button.val(pin);
		button.attr("class", this.PINS[pin].type.style);
	}
	cell.append(button);
	return cell;
}

RPiHeader.prototype.getDescriptionCell = function (pin, align) {
	var cell = $('<td>');
	cell.attr("align", align);
	
	var div = $('<div>');
	div.attr("class", "Description");
	if (this.PINS[pin].type.value != this.TYPE.GPIO.value) {
		div.append(this.PINS[pin].value);
	}
	else {
		div.attr("id", "description"+this.PINS[pin].value);
		div.append("GPIO " + this.PINS[pin].value);
	}
	
	cell.append(div);

	return cell;
}

RPiHeader.prototype.getDirectionCell = function (pin) {
	var cell = $('<td align="center">');
	if (this.PINS[pin].type.value == this.TYPE.GPIO.value) {
		var button = w().createDirectionButton(this.PINS[pin].value);
		cell.append(button);
	}
	return cell;
}

RPiHeader.prototype.createTable = function (containerId) {
	var table = $("<table>");
	table.attr("id", "RPiHeader")
	for (var pin=1; pin<=26; pin++) {
		var line = 	$('<tr>');
		line.append(this.getDirectionCell(pin))
		line.append(this.getDescriptionCell(pin, "right"))
		line.append(this.getPinCell(pin));

		pin++;
		line.append(this.getPinCell(pin));
		line.append(this.getDescriptionCell(pin, "left"))
		line.append(this.getDirectionCell(pin))

		table.append(line);
	}
	
	if (containerId != undefined) {
		$("#"+containerId).append(table);
	}
	
	return table;
}

RPiHeader.prototype.map = function (pin, type, value) {
	this.PINS[pin] = Object();
	this.PINS[pin].type = type
	this.PINS[pin].value = value;
}

