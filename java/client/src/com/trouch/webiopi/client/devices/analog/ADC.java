package com.trouch.webiopi.client.devices.analog;

import com.trouch.webiopi.client.PiClient;
import com.trouch.webiopi.client.devices.Device;

public class ADC extends Device {

	public ADC(PiClient client, String deviceName) {
		super(client, deviceName);
	}
	
	public float readFloat(int channel) {
		return Float.parseFloat(this.sendRequest("GET", "/" + channel + "/float"));
	}

}
