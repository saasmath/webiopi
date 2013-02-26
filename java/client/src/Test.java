import com.trouch.webiopi.client.PiClient;
import com.trouch.webiopi.client.PiCoapClient;
import com.trouch.webiopi.client.PiHttpClient;
import com.trouch.webiopi.client.PiMixedClient;
import com.trouch.webiopi.client.PiMulticastClient;
import com.trouch.webiopi.client.devices.analog.ADC;
import com.trouch.webiopi.client.devices.analog.DAC;
import com.trouch.webiopi.client.devices.analog.PWM;
import com.trouch.webiopi.client.devices.digital.GPIO;
import com.trouch.webiopi.client.devices.digital.NativeGPIO;
import com.trouch.webiopi.client.devices.sensor.Temperature;

public class Test {

	public static void main(String[] args) {
		String host = "192.168.1.234";
//		PiClient client = new PiHttpClient(host, PiHttpClient.DEFAULT_PORT);
//		PiClient client = new PiCoapClient(host, PiCoapClient.DEFAULT_PORT);
		PiClient client = new PiMixedClient(host, PiHttpClient.DEFAULT_PORT, PiCoapClient.DEFAULT_PORT);
//		PiClient client = new PiMulticastClient(PiMulticastClient.DEFAULT_PORT);

		Temperature temp0 = new Temperature(client, "temp0");
		System.out.println(temp0.getCelsius() + "¡C");

		NativeGPIO gpio = new NativeGPIO(client);
		GPIO gpio0 = new GPIO(client, "gpio0");
		GPIO gpio2 = new GPIO(client, "gpio2");

		gpio.setFunction(25, GPIO.OUT);
		gpio0.setFunction(0, GPIO.OUT);
		gpio2.setFunction(12, GPIO.OUT);

		DAC dac = new DAC(client, "dac");
		ADC adc = new ADC(client, "adc");
		PWM pwm = new PWM(client, "pwm0");

		boolean value = true;
		for (int i = 0; i <= 100; i++) {
			gpio.output(25, value);
			gpio0.output(0, value);
			gpio2.output(12, value);

			dac.writeFloat(0, (float) (i / 100.0));
			System.out.println("" + (adc.readFloat(1) * 3.3) + "V");
			pwm.writeAngle(7, i - 50);
			value = !value;
		}
	}

}
