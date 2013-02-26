package com.trouch.webiopi.client;

import com.trouch.coap.client.CoapClient;
import com.trouch.coap.messages.CoapRequest;
import com.trouch.coap.messages.CoapResponse;
import com.trouch.coap.methods.CoapGet;
import com.trouch.coap.methods.CoapPost;


public class PiCoapClient extends PiClient {
	public final static int DEFAULT_PORT = 5683;
	private CoapClient client;

	public PiCoapClient(String host) {
		super("coap", host, DEFAULT_PORT);
		client = new CoapClient();
	}

	public PiCoapClient(String host, int port) {
		super("coap", host, port);
		client = new CoapClient();
	}

	@Override
	public String sendRequest(String method, String path) throws Exception {
		CoapRequest request;
		if (method == "GET") {
			request = new CoapGet(this.urlBase + path);
		}
		else if (method == "POST") {
			request = new CoapPost(this.urlBase + path);
		}
		else throw new Exception("Method not supported: " + method);
		
		CoapResponse response = client.sendRequest(request);
		if (response != null) {
			return response.getPayload();
		}
		
		return null;
	}

}
