var PIN_COUNT = 26;

var TYPE = {
	NONE: {value: 0, color: "Gray"},
	GND: {value: 1, color: "Black"},
	V33: {value: 2, color: "Orange"},
	V50: {value: 3, color: "Red"},
	GPIO: {value: 4, color: "Black"}
};

var ALT = {
	UART: {name: "UART", color: "DarkBlue", enabled: false, pins: []},
	I2C: {name: "I2C", color: "LightBlue", enabled: false, pins: []},
	SPI: {name: "SPI", color: "Purple", enabled: false, pins: []}
};

var PINS = Array(PIN_COUNT);
var GPIO = Array(PIN_COUNT);

function MAP(pin_number, pin_type, pin_value) {
	PINS[pin_number-1] = {type: pin_type, value: pin_value};
	if (pin_type.value == TYPE.GPIO.value) {
		GPIO[pin_value].rpin = pin_number-1;
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
	MAP(3, TYPE.GPIO, 0);		MAP(4, TYPE.NONE, "--");
	MAP(5, TYPE.GPIO, 1);		MAP(6, TYPE.GND, "GROUND");
	MAP(7, TYPE.GPIO, 4);		MAP(8, TYPE.GPIO, 14);
	MAP(9, TYPE.NONE, "--");	MAP(10, TYPE.GPIO, 15);
	MAP(11, TYPE.GPIO, 17);		MAP(12, TYPE.GPIO, 18);
	MAP(13, TYPE.GPIO, 21);		MAP(14, TYPE.NONE, "--");
	MAP(15, TYPE.GPIO, 22);		MAP(16, TYPE.GPIO, 23);
	MAP(17, TYPE.NONE, "--");	MAP(18, TYPE.GPIO, 24);
	MAP(19, TYPE.GPIO, 10);		MAP(20, TYPE.NONE, "--");
	MAP(21, TYPE.GPIO, 9);		MAP(22, TYPE.GPIO, 25);
	MAP(23, TYPE.GPIO, 11);		MAP(24, TYPE.GPIO, 8);
	MAP(25, TYPE.NONE, "--");	MAP(26, TYPE.GPIO, 7);

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

function updateGPIO(gpio, value) {
	GPIO[gpio].value = value;
	var color = value == 1 ? TYPE.V33.color : TYPE.GND.color;
	$("#pin"+GPIO[gpio].rpin).css("background-color", color);
}

function updateGPIOSetup(gpio, value) {
	GPIO[gpio].setup = value;
	$("#setup"+GPIO[gpio].rpin).val(value);
}

function postGPIO(i) {
	var gpio = PINS[i].value;
	if ((PINS[i].type.value == TYPE.GPIO.value) && (GPIO[gpio].setup=="OUT")) {
		var value = (GPIO[gpio].value == 1) ? 0 : 1;
		$.post('/GPIO/' + PINS[i].value + "/value/" + value, function(data) {
			updateGPIO(gpio, data)
		});
	}
}

function postGPIOSetup(i) {
	if (PINS[i].type.value == TYPE.GPIO.value) {
		var gpio = PINS[i].value;
		var value = (GPIO[gpio].setup == "IN") ? "OUT" : "IN";
		$.post('/GPIO/' + PINS[i].value + "/setup/" + value, function(data) {
			updateGPIOSetup(gpio, data)
		});
	}
}

function getPinCell(i) {
	var cell = $('<td align="center">');
	var button = $('<input type="submit">');
	button.attr("id", "pin"+i);
	button.val(i+1);
	button.css("background-color", PINS[i].type.color);
	button.bind("click", function(event) {
		postGPIO(i);
	});
	cell.append(button);
	return cell;
}

function getName(i) {
	if (PINS[i].type.value != TYPE.GPIO.value) {
		return PINS[i].value;
	}
	else {
		return "GPIO " + PINS[i].value;
	}
}

function getNameCell(i, align) {
	var cell = $('<td>');
	cell.attr("align", align);
	
	var div = $('<div>');
	div.attr("id", "name"+i);
	div.addClass("pinname");
	div.append(getName(i));
	
	cell.append(div);

	return cell;
}

function getSetupCell(i) {
	var cell = $('<td align="center">');
	if (PINS[i].type.value == TYPE.GPIO.value) {
		var button = $('<input>');
		button.attr("id", "setup"+i);
		button.attr("type", "submit");
		button.addClass("pinsetup");
		button.val(GPIO[PINS[i].value].setup);
		button.bind("click", function(event) {
			postGPIOSetup(i);
		});
		cell.append(button);
	}
	return cell;
}

function setALT(alt, enable) {
	for (var p in alt.pins) {
		i = alt.pins[p].pin-1;
		$("#name"+i).empty();
		if (enable) {
			$("#name"+i).append(alt.name + " " + alt.pins[p].name);
			$("#pin"+i).css("background-color", alt.color);
			$("#setup"+i).css("visibility", "hidden");
		}
		else {
			$("#name"+i).append(getName(i));
			$("#pin"+i).css("background-color", TYPE.GPIO.color);
			$("#setup"+i).css("visibility", "visible");
		}
	}
	alt.enabled = enable;
}

function buildTable() {
	$("#webiopi").append($('<table>'));
	var table = $("#webiopi > table");
	for (var i=0; i<26; i++) {
		var line = 	$('<tr>');
		line.append(getSetupCell(i))
		line.append(getNameCell(i, "right"))
		line.append(getPinCell(i));

		i++;
		line.append(getPinCell(i));
		line.append(getNameCell(i, "left"))
		line.append(getSetupCell(i))

		table.append(line);
	}
}

function updateUI() {
	$.getJSON("/*", function(data) {
		setALT(ALT.UART, data["UART"]);
		setALT(ALT.I2C, data["I2C"]);
		setALT(ALT.SPI, data["SPI"]);
		
		$.each(data["GPIO"], function(gpio, data) {
		    if (data["mode"] == "GPIO") {
		    	updateGPIOSetup(gpio, data["setup"]);
		    	updateGPIO(gpio, data["value"]);
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

