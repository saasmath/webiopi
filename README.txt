=Features=
  * Support binary GPIOs, in both input and output.
  * HTML / Javascript / CSS client side
  * Easily [CUSTOMIZE] UI
  * REST/JSON [WEBAPI]
  * Server side available in two technologies
    * PHP 
    * Python
  * Smartphone compatible
  * Auto-refresh

=Restrictions=
  * GPIOs 0 and 1 have input pull-up resistor enabled.
  * UART is enabled but unusable for now.
    * GPIOs 14 and 15 are disabled
  * UART, SPI and I2C support will be added as soon as possible.
  * Don't forget that GPIO support only 3.3V, don't plug them to 5V !!!

=Usage=
First of all, follow [INSTALL] instructions.

If your are directly using your Raspberry Pi with keyboard/mouse/display plugged,  open a browser to http://localhost/webiopi/

_Don't forget to add :port right after raspberrypi/IP if you use a different port._

If your Raspberry Pi is connected to your network, yo can open a browser to http://raspberrypi/webiopi/ with any device of your network. 
Replace raspberrypi by its IP if DNS don't find raspberrypi.

You can even add a port redirection on your router (and/or use IPv6) to control your GPIOs over Internet !

  * Click/Tap the OUT/IN button to change GPIO direction.
  * Click/Tap pins to change the GPIO output state.

------------------------------------------------------------------------------

   Copyright 2012 Eric Ptak - trouch.com

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.


