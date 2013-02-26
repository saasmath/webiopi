package com.trouch.webiopi.client.devices.digital;

import com.trouch.webiopi.client.PiClient;

public class NativeGPIO extends GPIO {

	public NativeGPIO(PiClient client) {
		super(client, "");
		this.path = "/GPIO";
	}

}
