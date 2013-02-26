package com.trouch.webiopi.client.devices.sensor;

import com.trouch.webiopi.client.PiClient;
import com.trouch.webiopi.client.devices.Device;

public class Temperature extends Device {

	public Temperature(PiClient client, String deviceName) {
		super(client, deviceName);
	}

	public float getCelsius() {
		return Float.parseFloat(this.sendRequest("GET", "/temperature/c"));
	}

	public float getFahrenheit() {
		return Float.parseFloat(this.sendRequest("GET", "/temperature/f"));
	}

}
