package com.trouch.webiopi.client.devices.analog;

import com.trouch.webiopi.client.PiClient;

public class DAC extends ADC {

	public DAC(PiClient client, String deviceName) {
		super(client, deviceName);
	}

	public float writeFloat(int channel, float value) {
		return Float.parseFloat(this.sendRequest("POST", "/" + channel + "/float/" + value));
	}

}
