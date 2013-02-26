package com.trouch.webiopi.client;

public abstract class PiClient {
	
	protected String urlBase;

	public PiClient(String protocol, String host, int port) {
		this.urlBase = protocol + "://" + host + ":" + port; 
	}
	
	public abstract String sendRequest(String method, String path) throws Exception;

}
