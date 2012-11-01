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
	this.GPIO = Array(54);
	this.ALT = {
			I2C0: {name: "I2C0", enabled: false, gpios: []},
			I2C1: {name: "I2C1", enabled: false, gpios: []},
			SPI0: {name: "SPI0", enabled: false, gpios: []},
			UART0: {name: "UART0", enabled: false, gpios: []},
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
		gpio.func = "IN";
		this.GPIO[i] = gpio;
	}
	
	
	// init ALTs
	this.addALT(this.ALT.I2C0, 0, "SDA");
	this.addALT(this.ALT.I2C0, 1, "SCL");

	this.addALT(this.ALT.I2C1, 2, "SDA");
	this.addALT(this.ALT.I2C1, 3, "SCL");

	this.addALT(this.ALT.SPI0,  7, "CE1");
	this.addALT(this.ALT.SPI0,  8, "CE0");
	this.addALT(this.ALT.SPI0,  9, "MISO");
	this.addALT(this.ALT.SPI0, 10, "MOSI");
	this.addALT(this.ALT.SPI0, 11, "SCLK");
	
	this.addALT(this.ALT.UART0, 14, "TX");
	this.addALT(this.ALT.UART0, 15, "RX");

	// GA
	_gaq.push(['_setAccount', 'UA-33979593-2']);
	_gaq.push(['_trackPageview']);
		
	var ga = document.createElement('script');
	ga.type = 'text/javascript';
	ga.async = false;
	ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';

	scripts[0].parentNode.insertBefore(ga, scripts[0]);
	
	// schedule UpdateUI and CheckVersion
	setTimeout(this.RPiHeader, 100);
	setTimeout(this.updateUI, 100);
	setTimeout(this.checkVersion, 100);
}


WebIOPi.prototype.ready = function (cb) {
	this.readyCallback = cb;
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
	if (this.GPIO[gpio].func=="OUT") {
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

WebIOPi.prototype.updateFunction = function (gpio, func) {
	this.GPIO[gpio].func = func;
	$("#function"+gpio).val(func);
}

WebIOPi.prototype.setFunction = function (gpio, func) {
	$.post(this.context + 'GPIO/' + gpio + "/function/" + func, function(data) {
		w().updateFunction(gpio, data);
	});
}

WebIOPi.prototype.toggleFunction = function (gpio) {
	var value = (this.GPIO[gpio].func == "IN") ? "OUT" : "IN";
	this.setFunction(gpio, value)
}

WebIOPi.prototype.createFunctionButton = function (gpio) {
	var button = $('<input>');
	button.attr("id", "function"+gpio);
	button.attr("type", "submit");
	button.attr("class", "DirectionEnabled");
	button.val(" ");
	button.bind("click", function(event) {
		w().toggleFunction(gpio);
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
			$("#function"+gpio).attr("class", "DirectionDisabled");
		}
		else {
			$("#description"+gpio).append("GPIO " + gpio);
			$("#gpio"+gpio).attr("class", "");
			$("#function"+gpio).attr("class", "DirectionEnabled");
		}
	}
	alt.enabled = enable;
}

WebIOPi.prototype.updateUI = function () {
	$.getJSON(w().context + "*", function(data) {
		w().updateALT(w().ALT.I2C0, data["I2C0"]);
		w().updateALT(w().ALT.I2C1, data["I2C1"]);
		w().updateALT(w().ALT.SPI0, data["SPI0"]);
		w().updateALT(w().ALT.UART0, data["UART0"]);
		
		$.each(data["GPIO"], function(gpio, data) {
	    	w().updateFunction(gpio, data["function"]);
	    	if ((data["function"] == "IN") || (data["function"] == "OUT")) { 
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

		$.get("http://webiopi.trouch.com/version.php", function(data) {
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
	if (w()._header == undefined) {
		w()._header = new RPiHeader();
	}
	return w()._header;
}

WebIOPi.prototype.Expert = function () {
	if (w()._expert == undefined) {
		w()._expert = new Expert();
	}
	return w()._expert;
}

function RPiHeader() {
	this.PINS = Array(27);

	this.TYPE = {
			GND: {value: 1, style: "GND", label: "GROUND"},
			V33: {value: 2, style: "V33", label: "3.3V"},
			V50: {value: 3, style: "V50", label: "5.0V"},
			GPIO: {value: 4, style: "GPIO", label: "GPIO"}
	};
	
	$.getJSON(w().context + "map", function(data) {
		var header = w().RPiHeader();
		var count = header.PINS.length;
		for (i = 0; i<count-1; i++) {
			var type = header.TYPE.GPIO;
			var label = data[i];
			
			if (label == "GND") {
				type = header.TYPE.GND;
			}
			else if (label == "V33") {
				type = header.TYPE.V33;
			}
			else if (label == "V50") {
				type = header.TYPE.V50;
			}
			
			if (type.value != header.TYPE.GPIO.value) {
				label = type.label;
			}
			
			header.map(i+1, type, label);
		}
		w().readyCallback();
	});
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

RPiHeader.prototype.getFunctionCell = function (pin) {
	var cell = $('<td align="center">');
	if (this.PINS[pin].type.value == this.TYPE.GPIO.value) {
		var button = w().createFunctionButton(this.PINS[pin].value);
		cell.append(button);
	}
	return cell;
}

RPiHeader.prototype.createTable = function (containerId) {
	var table = $("<table>");
	table.attr("id", "RPiHeader")
	for (var pin=1; pin<=26; pin++) {
		var line = 	$('<tr>');
		line.append(this.getFunctionCell(pin))
		line.append(this.getDescriptionCell(pin, "right"))
		line.append(this.getPinCell(pin));

		pin++;
		line.append(this.getPinCell(pin));
		line.append(this.getDescriptionCell(pin, "left"))
		line.append(this.getFunctionCell(pin))

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

function Expert() {
	
}

Expert.prototype.createGPIO = function (gpio) {
	var box = $("<div>");
	box.append(w().createFunctionButton(gpio));
	box.append(w().createGPIOButton(gpio, gpio));

	div = $('<div>');
	div.attr("id", "description"+gpio);
	div.attr("class", "Description");
	div.append("GPIO " + gpio);
	box.append(div);

	return box;
}

Expert.prototype.createList = function (containerId) {
	var box = $('<div>');
	
	$.getJSON(w().context + "*", function(data) {
		$.each(data["GPIO"], function(gpio, data) {
			var gpio = w().Expert().createGPIO(gpio);
			box.append(gpio);
		});
	});
	
	if (containerId != undefined) {
		$("#"+containerId).append(box);
	}
	
	return box;
} 


