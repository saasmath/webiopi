package com.trouch.webiopi.client.devices.analog;

import com.trouch.webiopi.client.PiClient;

public class PWM extends DAC {

	public PWM(PiClient client, String deviceName) {
		super(client, deviceName);
	}

	public float readAngle(int channel) {
		return Float.parseFloat(this.sendRequest("GET", "/" + channel + "/angle"));
	}

	public float writeAngle(int channel, float angle) {
		return Float.parseFloat(this.sendRequest("POST", "/" + channel + "/angle/" + angle));
	}

}
