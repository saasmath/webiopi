package com.trouch.webiopi.client;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

public class PiHttpClient extends PiClient {
	public final static int DEFAULT_PORT = 8000;

	public PiHttpClient(String host) {
		super("http", host, DEFAULT_PORT);
	}

	public PiHttpClient(String host, int port) {
		super("http", host, port);
	}

	@Override
	public String sendRequest(String method, String path) throws Exception {
		BufferedReader reader = null;
		try {
			URL url = new URL(this.urlBase + path);
			HttpURLConnection connection = (HttpURLConnection) url.openConnection();
			connection.setRequestMethod(method);

			// read the output from the server
			reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
			StringBuilder stringBuilder = new StringBuilder();

			String line = null;
			while ((line = reader.readLine()) != null) {
				stringBuilder.append(line).append('\n');
			}
			return stringBuilder.toString();
		} catch (Exception e) {
			e.printStackTrace();
			throw e;
		} finally {
			if (reader != null) {
				try {
					reader.close();
				} catch (IOException ioe) {
					ioe.printStackTrace();
				}
			}
		}
	}

}
