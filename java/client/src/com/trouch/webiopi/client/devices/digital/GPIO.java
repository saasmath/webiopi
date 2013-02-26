package com.trouch.webiopi.client.devices.digital;

import com.trouch.webiopi.client.PiClient;
import com.trouch.webiopi.client.devices.Device;

public class GPIO extends Device {
	
	public final static String OUT = "OUT";
	public final static String IN = "IN";

	public GPIO(PiClient client, String deviceName) {
		super(client, deviceName);
	}
	
	public String getFunction(int channel) {
		return this.sendRequest("GET", "/" + channel + "/function");
	}

	public String setFunction(int channel, String function) {
		return this.sendRequest("POST", "/" + channel + "/function/" + function);
	}
	
	public boolean input(int channel) {
		String res = this.sendRequest("GET", "/" + channel + "/value");
		if (res.equals("1")) {
			return true;
		}
		return false;
	}

	public boolean output(int channel, boolean value) {
		String res = this.sendRequest("POST", "/" + channel + "/value/" + (value ? "1" : "0"));
		if (res.equals("1")) {
			return true;
		}
		return false;
	}

}
