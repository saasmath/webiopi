<?php

class GPIO {
	var $GPIO_AVAILABLE = [0, 1, 4, 7, 8, 9, 10, 11, 14, 15, 17, 18, 21, 22, 23, 24, 25];
	var $ALT = [
		"UART" =>["enabled" => true, "pins"=>[14, 15]],
		"I2C" => ["enabled" => false, "pins"=>[0, 1]],
		"SPI" => ["enabled" => false, "pins"=>[7, 8, 9, 10, 11]]
	];
	var $GPIO_ROOT = "/sys/class/gpio";

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
		system("sudo sh -c 'echo $pin > $this->GPIO_ROOT/export'");
		return $this->isEnabled($pin);
	}

	function disable($pin) {
		system("sudo sh -c 'echo $pin > $this->GPIO_ROOT/unexport'");
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
	
	function getDirection($pin) {
		return $this->readGPIO($pin, "direction");
	}

	function setDirection($pin, $value) {
		system("sudo sh -c 'echo $value > " . $this->getPath($pin, "direction") . "'");
		return $this->getDirection($pin);
	}

	function getValue($pin) {
		return $this->readGPIO($pin, "value");
	}

	function setValue($pin, $value) {
		system("sudo sh -c 'echo $value > " . $this->getPath($pin, "value") . "'");
		return $this->getValue($pin);
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
					echo "enabling " . $pin . "</br>";
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

?>
