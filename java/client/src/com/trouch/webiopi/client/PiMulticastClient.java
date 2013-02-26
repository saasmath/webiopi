package com.trouch.webiopi.client;

public class PiMulticastClient extends PiCoapClient {

	public PiMulticastClient() {
		super("224.0.1.123", PiMulticastClient.DEFAULT_PORT);
	}

	public PiMulticastClient(int port) {
		super("224.0.1.123", port);
	}

}
