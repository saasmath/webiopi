package com.trouch.webiopi.client;

public class PiMixedClient extends PiClient {
	private PiHttpClient http;
	private PiCoapClient coap;
	
	private int tries 	 = 0;
	private int maxTries = 3;
	
	public PiMixedClient(String host) {
		super("", "", 0);
		this.http = new PiHttpClient(host);
		this.coap = new PiCoapClient(host);
	}
	
	public PiMixedClient(String host, int httpPort, int coapPort) {
		super("", "", 0);
		this.http = new PiHttpClient(host, httpPort);
		this.coap = new PiCoapClient(host, coapPort);
	}
	
	@Override
	public String sendRequest(String method, String path) throws Exception {
		if (tries < maxTries) {
			String response = coap.sendRequest(method, path);
			if (response != null) {
				tries = 0;
				return response;
			}
			tries++;
		}
		
		return http.sendRequest(method, path);
	}
	
}
