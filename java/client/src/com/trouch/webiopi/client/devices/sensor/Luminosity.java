package com.trouch.webiopi.client.devices.sensor;

import com.trouch.webiopi.client.PiClient;
import com.trouch.webiopi.client.devices.Device;

public class Luminosity extends Device {

	public Luminosity(PiClient client, String deviceName) {
		super(client, deviceName);
	}

	public float getLux() {
		return Float.parseFloat(this.sendRequest("GET", "/luminosity/lx"));
	}

}
