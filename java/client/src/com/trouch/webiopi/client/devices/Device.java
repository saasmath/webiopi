package com.trouch.webiopi.client.devices;

import com.trouch.webiopi.client.PiClient;

public class Device {
	
	private PiClient client;
	protected String path;

	public Device(PiClient client, String deviceName) {
		this.client = client;
		this.path = "/devices/" + deviceName;
	}
	
	public String sendRequest(String method, String subPath) {
		try {
			return this.client.sendRequest(method, this.path + subPath);
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			return null;
		}
	}

}
