package com.trouch.webiopi.client.devices.sensor;

import com.trouch.webiopi.client.PiClient;
import com.trouch.webiopi.client.devices.Device;

public class Distance extends Device {

	public Distance(PiClient client, String deviceName) {
		super(client, deviceName);
	}

	public float getMillimeter() {
		return Float.parseFloat(this.sendRequest("GET", "/distance/mm"));
	}

}
