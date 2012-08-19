<?php
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

class GPIO {
	var $GPIO_AVAILABLE = [0, 1, 4, 7, 8, 9, 10, 11, 14, 15, 17, 18, 21, 22, 23, 24, 25];
	var $ALT = [
		"UART" =>["enabled" => true, "pins"=>[14, 15]],
		"I2C" => ["enabled" => false, "pins"=>[0, 1]],
		"SPI" => ["enabled" => false, "pins"=>[7, 8, 9, 10, 11]]
	];
	var $GPIO_ROOT = "/sys/class/gpio";
	
	function sudo($cmd) {
		return system("sudo sh -c '$cmd'");
	}
	
	function setALT($alt, $enable) {
		$alt["enabled"] = $enable;
	}

	function getPath($pin, $cmd="") {
		return $this->GPIO_ROOT . "/gpio" . $pin . "/" . $cmd;
	}

	function isEnabled($pin) {
		return file_exists($this->getPath($pin));
	}

	function enable($pin) {
		$this->sudo("echo $pin > $this->GPIO_ROOT/export");
		if ($this->isEnabled($pin)) {
			$this->setDirection($pin, "in");
			return true;
		}
		return false;
	}

	function disable($pin) {
		$this->sudo("echo $pin > $this->GPIO_ROOT/unexport");
		return $this->isEnabled($pin);
	}

	function readGPIO($pin, $file) {
		$path = $this->getPath($pin, $file);
		$f= fopen($path, "r");
		$value = fread($f, filesize($path));
		$value = substr($value, 0, strpos($value, "\n"));
		fclose($f);
		return $value;
		
	}
	
	function writeGPIO($pin, $file, $value) {
		$this->sudo("echo $value > " . $this->getPath($pin, $file));
		return $this->readGPIO($pin, $file);
	}
	
	function getDirection($pin) {
		return $this->readGPIO($pin, "direction");
	}

	function setDirection($pin, $value) {
		return $this->writeGPIO($pin, "direction", $value);
	}

	function getValue($pin) {
		return $this->readGPIO($pin, "value");
	}

	function setValue($pin, $value) {
		return $this->writeGPIO($pin, "value", $value);
	}

	function getALTPins() {
		$alt_pins = array();
		foreach($this->ALT as $alt) {
			if ($alt["enabled"]) {
				foreach($alt["pins"] as $pin) {
					$alt_pins[] = $pin;
				}
			}
		}
		return $alt_pins;
	}

	function setPINSEnabled($enable) {
		$alt_pins = $this->getALTPins();
		foreach($this->GPIO_AVAILABLE as $pin) {
			if (!in_array($pin, $alt_pins)) {
				if ($enable && !$this->isEnabled($pin)) {
					$this->enable($pin);
				}
				else if (!$enable && $this->isEnabled($pin)) {
					$this->disable($pin);
				}
			}
		}

	}

	function init() {
		$this->setPINSEnabled(true);
	}

	function release() {
		$this->setPINSEnabled(false);
	}
}

if (isset($_SERVER["SHELL"]) && !isset($_SERVER["GATEWAY_INTERFACE"])) {
	print_r($_SERVER);
	$gpio = new GPIO();
	if ($argc == 1) {
		
	}
	else if (($argc == 2) && ($argv[1] == "init")) {
		$gpio->init();
	}
	else if (($argc == 2) && ($argv[1] == "release")) {
		$gpio->release();
	}
	else {
		echo "usage:\n";
		echo "php " . $argv['0'] . " [init|release]\n";
	}
}
?>
