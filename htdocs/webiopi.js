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

function isMobileUserAgent(a) {
	if (/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino/i.test(a)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0,4)))
			return true
}

var _isMobile = undefined;
function isMobile() {
	if (_isMobile == undefined) {
		_isMobile = ((navigator.userAgent != undefined && isMobileUserAgent(navigator.userAgent))
				|| (navigator.vendor != undefined && isMobileUserAgent(navigator.vendor)) 
				|| (window.opera != undefined && isMobileUserAgent(window.opera)))
	}
	return _isMobile
}

function WebIOPi() {
	this.readyCallback = null;
	this.context = "/";
	this.GPIO = Array(54);
	this.PINS = Array(27);

	this.TYPE = {
			DNC: {value: 0, style: "DNC", label: "--"},
			GND: {value: 1, style: "GND", label: "GROUND"},
			V33: {value: 2, style: "V33", label: "3.3V"},
			V50: {value: 3, style: "V50", label: "5.0V"},
			GPIO: {value: 4, style: "GPIO", label: "GPIO"}
	};
	
	this.ALT = {
			I2C: {name: "I2C", enabled: false, gpios: []},
			SPI: {name: "SPI", enabled: false, gpios: []},
			UART: {name: "UART", enabled: false, gpios: []},
			ONEWIRE: {name: "ONEWIRE", enabled: false, gpios: []}
		};
		
	// init GPIOs
	for (var i=0; i<this.GPIO.length; i++) {
		var gpio = Object();
		gpio.value = 0;
		gpio.func = "IN";
		gpio.mapped = false;
		this.GPIO[i] = gpio;
	}

	// get context
	var reg = new RegExp("http://" + window.location.host + "(.*)webiopi.js");
	var scripts = document.getElementsByTagName("script");
	for(var i = 0; i < scripts.length; i++) {
		var res = reg.exec(scripts[i].src);
		if (res && (res.length > 1)) {
			script = scripts[i];
			this.context = res[1];
			
		}
	}

	var head = document.getElementsByTagName('head')[0];

	var jquery = document.createElement('script');
	jquery.type = 'text/javascript';
	jquery.src = '/jquery.js';
	if (!isMobile()) {
		jquery.onload = function() {
			w().init();
		};
	}
//	jquery.onreadystatechange = function() {
//		alert("ready state change");
//		if (this.readyState == 'complete') {
//			alert("complete");
//			w().init();
//		}
//	};
	head.appendChild(jquery);
	
	if (isMobile()) {
		console.log("load jquery mobile");
		var mobile = document.createElement('script');
		mobile.type = 'text/javascript';
		mobile.src = '/jquery-mobile.js';
		mobile.onload = function() {
			w().initMobile()
		};
		head.appendChild(mobile);
	}

	// GA
	_gaq.push(['_setAccount', 'UA-33979593-2']);
	_gaq.push(['_trackPageview']);
		
	var ga = document.createElement('script');
	ga.type = 'text/javascript';
	ga.async = false;
	ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
	head.appendChild(ga);
	
	var style = document.createElement('link');
	style.rel = "stylesheet";
	style.type = 'text/css';
	style.href = '/webiopi.css';
	head.appendChild(style);

	if (isMobile()) {
		var style = document.createElement('link');
		style.rel = "stylesheet";
		style.type = 'text/css';
		style.href = '/jquery-mobile.css';
		head.appendChild(style);
	}
	
	// init ALTs
	this.addALT(this.ALT.I2C, 0, "SDA");
	this.addALT(this.ALT.I2C, 1, "SCL");
	this.addALT(this.ALT.I2C, 2, "SDA");
	this.addALT(this.ALT.I2C, 3, "SCL");

	this.addALT(this.ALT.SPI,  7, "CE1");
	this.addALT(this.ALT.SPI,  8, "CE0");
	this.addALT(this.ALT.SPI,  9, "MISO");
	this.addALT(this.ALT.SPI, 10, "MOSI");
	this.addALT(this.ALT.SPI, 11, "SCLK");
	
	this.addALT(this.ALT.UART, 14, "TX");
	this.addALT(this.ALT.UART, 15, "RX");
	
	this.addALT(this.ALT.ONEWIRE, 4, "");
}

WebIOPi.prototype.init = function() {
	$.getJSON(w().context + "map", function(data) {
		var count = w().PINS.length;
		for (i = 0; i<count-1; i++) {
			var type = w().TYPE.GPIO;
			var label = data[i];
			
			if (label == "DNC") {
				type = w().TYPE.DNC;
			}
			else if (label == "GND") {
				type = w().TYPE.GND;
			}
			else if (label == "V33") {
				type = w().TYPE.V33;
			}
			else if (label == "V50") {
				type = w().TYPE.V50;
			}
			
			if (type.value != w().TYPE.GPIO.value) {
				label = type.label;
			}
			
			w().map(i+1, type, label);
		}
		if (w().readyCallback != null) {
			w().readyCallback();
		}

		w().checkVersion();
	});
}

WebIOPi.prototype.initMobile = function() {
	webiopi().init();
}

WebIOPi.prototype.ready = function (cb) {
	w().readyCallback = cb;
}

WebIOPi.prototype.map = function (pin, type, value) {
	w().PINS[pin] = Object();
	w().PINS[pin].type = type
	w().PINS[pin].value = value;
	
	if (type.value == w().TYPE.GPIO.value) {
		w().GPIO[value].mapped = true;
	}
}

WebIOPi.prototype.addALT = function (alt, gpio, name) {
	var o = Object();
	o.gpio = gpio;
	o.name = name;
	alt.gpios.push(o);
}

WebIOPi.prototype.updateValue = function (gpio, value) {
	w().GPIO[gpio].value = value;
	var style = (value == 1) ? "HIGH" : "LOW";
	$("#gpio"+gpio).attr("class", style);
}

WebIOPi.prototype.updateFunction = function (gpio, func) {
	w().GPIO[gpio].func = func;
	$("#function"+gpio).val(func);
	$("#function"+gpio).text(func);
}

WebIOPi.prototype.updateSlider = function (gpio, slider, value) {
	$("#"+slider+gpio).val(value);
}

WebIOPi.prototype.updateALT = function (alt, enable) {
	for (var p in alt.gpios) {
		gpio = alt.gpios[p].gpio;
		$("#description"+gpio).empty();
		if (enable) {
			$("#description"+gpio).append(alt.name + " " + alt.gpios[p].name);
			$("#gpio"+gpio).attr("class", alt.name);
			$("#function"+gpio).attr("class", "FunctionSpecial");
		}
		else {
			$("#description"+gpio).append("GPIO " + gpio);
			$("#gpio"+gpio).attr("class", "");
			$("#function"+gpio).attr("class", "FunctionBasic");
		}
	}
	alt.enabled = enable;
}

WebIOPi.prototype.refreshGPIO = function (repeat) {
	$.getJSON(w().context + "*", function(data) {
		w().updateALT(w().ALT.I2C, data["I2C"]);
		w().updateALT(w().ALT.SPI, data["SPI"]);
		w().updateALT(w().ALT.UART, data["UART"]);
		w().updateALT(w().ALT.ONEWIRE, data["ONEWIRE"]);
		
		$.each(data["GPIO"], function(gpio, data) {
	    	w().updateFunction(gpio, data["function"]);
	    	if ( ((gpio != 4) && ((data["function"] == "IN") || (data["function"] == "OUT"))
	    		|| ((gpio == 4) && (w().ALT.ONEWIRE["enabled"] == false)))){
	    		w().updateValue(gpio, data["value"]);
	    	}
	    	else if (data["function"] == "PWM") {
	    		w().updateSlider(gpio, "ratio", data["ratio"]);
	    		w().updateSlider(gpio, "angle", data["angle"]);
	    	}
	    	
		});
	});
	if (repeat === true) {
		setTimeout(function(){w().refreshGPIO(repeat)}, 1000);
	}
}


WebIOPi.prototype.checkVersion = function () {
	var version;
	
	$.get(w().context + "version", function(data) {
		_gaq.push(['_trackEvent', 'version', data]);
//		version = data.split("/")[2];
//
//		$.get("http://webiopi.trouch.com/version.php", function(data) {
//			var lines = data.split("\n");
//			var c = version.split(".");
//			var n = lines[0].split(".");
//			var updated = false;
//			for (i=0; i<Math.min(c.length, n.length); i++) {
//				if (n[i]>c[i]) {
//					updated = true;
//				}
//			}
//			if (updated || (n.length > c.length)) {
//				var div = $('<div id="update"><a href="' + lines[1] + '">Update available</a></div>');
//				$("body").append(div);
//			}
//		});
	});
}

WebIOPi.prototype.getValue = function (gpio, callback) {
	if (callback != undefined) {
		$.get(w().context + 'GPIO/' + gpio + "/value", function(data) {
			w().updateValue(gpio, data);
			callback(gpio, data);
		});
	}
	return w().GPIO[gpio].value;
}

WebIOPi.prototype.setValue = function (gpio, value, callback) {
	if (w().GPIO[gpio].func.toUpperCase()=="OUT") {
		$.post(w().context + 'GPIO/' + gpio + "/value/" + value, function(data) {
			w().updateValue(gpio, data);
			if (callback != undefined) {
				callback(gpio, data);
			}
		});
	}
	else {
		//console.log(w().GPIO[gpio].func);
	}
}

WebIOPi.prototype.getFunction = function (gpio, callback) {
	if (callback != undefined) {
		$.get(w().context + 'GPIO/' + gpio + "/function", function(data) {
			w().updateFunction(gpio, data);
			callback(gpio, data);
		});
	}
	return w().GPIO[gpio].func;
}
WebIOPi.prototype.setFunction = function (gpio, func, callback) {
	$.post(w().context + 'GPIO/' + gpio + "/function/" + func, function(data) {
		w().updateFunction(gpio, data);
		if (callback != undefined) {
			callback(gpio, data);
		}
	});
}

WebIOPi.prototype.toggleValue = function (gpio) {
	var value = (w().GPIO[gpio].value == 1) ? 0 : 1;
	w().setValue(gpio, value);
}

WebIOPi.prototype.toggleFunction = function (gpio) {
	var value = (w().GPIO[gpio].func == "IN") ? "OUT" : "IN";
	w().setFunction(gpio, value)
}

WebIOPi.prototype.outputSequence = function (gpio, period, sequence, callback) {
	$.post(w().context + 'GPIO/' + gpio + "/sequence/" + period + "," + sequence, function(data) {
		w().updateValue(gpio, data);
		if (callback != undefined) {
			callback(gpio, data);
		}
	});
}

WebIOPi.prototype.callMacro = function (macro, args, callback) {
	if (args == undefined) {
		args = "";
	}
	$.post(w().context + 'macros/' + macro + "/" + args, function(data) {
		if (callback != undefined) {
			callback(macro, args, data);
		}
	});
}

WebIOPi.prototype.enablePWM = function(gpio, callback) {
	$.post(w().context + 'GPIO/' + gpio + "/pwm/enable", function(data) {
		if (callback != undefined) {
			callback(gpio, data);
		}
	});
}

WebIOPi.prototype.disablePWM = function(gpio, callback) {
	$.post(w().context + 'GPIO/' + gpio + "/pwm/disable", function(data) {
		if (callback != undefined) {
			callback(gpio, data);
		}
	});
}

WebIOPi.prototype.pulse = function(gpio, callback) {
	$.post(w().context + 'GPIO/' + gpio + "/pulse/", function(data) {
		if (callback != undefined) {
			callback(gpio, data);
		}
	});
}

WebIOPi.prototype.pulseRatio = function(gpio, ratio, callback) {
	$.post(w().context + 'GPIO/' + gpio + "/pulseRatio/" + ratio, function(data) {
		if (callback != undefined) {
			callback(gpio, data);
		}
	});
}

WebIOPi.prototype.pulseAngle = function(gpio, angle, callback) {
	$.post(w().context + 'GPIO/' + gpio + "/pulseAngle/" + angle, function(data) {
		if (callback != undefined) {
			callback(gpio, data);
		}
	});
}

WebIOPi.prototype.setLabel = function (id, label) {
	$("#" + id).val(label);
	$("#" + id).text(label);
}

WebIOPi.prototype.createButton = function (id, label, callback, callbackUp) {
	var button = $('<button type="button" class="Default">');
	button.attr("id", id);
	button.text(label);
	if ((callback != undefined) && (callbackUp == undefined)) {
		button.bind("click", callback);
	}
	else if ((callback != undefined) && (callbackUp != undefined)) {
		if (isMobile()) {
			button.bind("vmousedown", callback);
			button.bind("vmouseup", callbackUp);
		}
		else {
			button.bind("mousedown", callback);
			button.bind("mouseup", callbackUp);
		}
	}
	return button;
}

WebIOPi.prototype.createGPIOButton = function (gpio, label) {
	var button = w().createButton("gpio" + gpio, label);
	button.bind("click", function(event) {
		w().toggleValue(gpio);
	});
	return button;
}

WebIOPi.prototype.createFunctionButton = function (gpio) {
	var button = w().createButton("function" + gpio, " ");
	button.attr("class", "FunctionBasic");
	button.bind("click", function(event) {
		w().toggleFunction(gpio);
	});
	return button;
}

WebIOPi.prototype.createPulseButton = function (id, label, gpio) {
    var button = webiopi().createButton(id, label);
    button.bind("click", function(event) {
        webiopi().pulse(gpio);
    });
    return button;
}

WebIOPi.prototype.createMacroButton = function (id, label, macro, args) {
    var button = webiopi().createButton(id, label);
    button.bind("click", function(event) {
        webiopi().callMacro(macro, args);
    });
    return button;
}

WebIOPi.prototype.createSequenceButton = function (id, label, gpio, period, sequence) {
    var button = webiopi().createButton(id, label);
    button.bind("click", function(event) {
        webiopi().outputSequence(gpio, period, sequence);
    });
    return button;
}

WebIOPi.prototype.createRatioSlider = function(gpio) {
	var slider = $('<input type="range" min="0.0" max="1.0" step="0.01">');
	slider.attr("id", "ratio"+gpio);
	slider.bind("change", function() {
		w().pulseRatio(gpio, slider.val());
	});
	return slider;
}

WebIOPi.prototype.createAngleSlider = function(gpio) {
	var slider = $('<input type="range" min="-45" max="45" step="1">');
	slider.attr("id", "angle"+gpio);
	slider.bind("change", function() {
		w().pulseAngle(gpio, slider.val());
	});
	return slider;
}

WebIOPi.prototype.RPiHeader = function () {
	if (w()._header == undefined) {
		w()._header = new RPiHeader();
	}
	return w()._header;
}

function RPiHeader() {

}

RPiHeader.prototype.getPinCell = function (pin) {
	var cell = $('<td align="center">');
	var button;
	if (w().PINS[pin].type.value == w().TYPE.GPIO.value) {
		button = w().createGPIOButton(w().PINS[pin].value, pin);
	}
	else {
		var button = $('<button type="button">');
		button.val(pin);
		button.text(pin);
		button.attr("class", w().PINS[pin].type.style);
	}
	cell.append(button);
	return cell;
}

RPiHeader.prototype.getDescriptionCell = function (pin, align) {
	var cell = $('<td>');
	cell.attr("align", align);
	
	var div = $('<div>');
	div.attr("class", "Description");
	if (w().PINS[pin].type.value != w().TYPE.GPIO.value) {
		div.append(w().PINS[pin].value);
	}
	else {
		div.attr("id", "description"+w().PINS[pin].value);
		div.append("GPIO " + w().PINS[pin].value);
	}
	
	cell.append(div);

	return cell;
}

RPiHeader.prototype.getFunctionCell = function (pin) {
	var cell = $('<td align="center">');
	if (w().PINS[pin].type.value == w().TYPE.GPIO.value) {
		var button = w().createFunctionButton(w().PINS[pin].value);
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

WebIOPi.prototype.Expert = function () {
	if (w()._expert == undefined) {
		w()._expert = new Expert();
	}
	return w()._expert;
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
	
	for (i = 0; i<w().GPIO.length; i++) {
		if (w().GPIO[i].mapped == true) {
			var gpio = w().Expert().createGPIO(i);
			box.append(gpio);
		}
	}
		
	if (containerId != undefined) {
		$("#"+containerId).append(box);
	}
	
	return box;
} 

WebIOPi.prototype.Serial = function(device) {
	return new Serial(device);
}

function Serial(device) {
	this.device = device;
	this.url = "/devices/" + device
}

Serial.prototype.write = function(data) {
	$.post(this.url, data);
} 

Serial.prototype.read = function(callback) {
	$.get(this.url, callback);
}

