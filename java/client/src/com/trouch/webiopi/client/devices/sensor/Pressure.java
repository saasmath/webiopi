package com.trouch.webiopi.client.devices.sensor;

import com.trouch.webiopi.client.PiClient;
import com.trouch.webiopi.client.devices.Device;

public class Pressure extends Device {

	public Pressure(PiClient client, String deviceName) {
		super(client, deviceName);
	}

	public float getHectoPascal() {
		return Float.parseFloat(this.sendRequest("GET", "/pressure/hpa"));
	}

	public float getPascal() {
		return Float.parseFloat(this.sendRequest("GET", "/pressure/pa"));
	}

}
