Based on [this article](http://www.raspberrypi-spy.co.uk/2012/08/reading-analogue-sensors-with-one-gpio-pin/),
this tiny library encapsulates the basics needed to quickly and easily 
read a pin off the Raspberry Pi in an analog way, using just a capacitor 
and resistor as extra components.

The circuit diagram:

![Circuit](https://cdn.rawgit.com/Fordi/rpi-analog-pin/master/circuit.svg)

To initialize, pass the pin number, minimum resistance (R1) and 
capacitance (C1), and a sampling timeout into the constructor for Pin 
(defaults are shown):

	# Remember to set your GPIO pin addressing mode
	RPI_PIN_NUM = 17
	GPIO.setmode(GPIO.BCM)
	aPin = Pin(RPI_PIN_NUM, minResistance=2200, capacitance=0.000001, timeout=0.03333)

The sampling timeout is important; the smaller the value, the better
the sampling time resolution is going to be, but the smaller your 
resistance range:

	t = (Rᵢ + Rₘ + Rₓ)C

Where:

 * t  - timeout
 * Rᵢ - the Raspberry Pi's internal resistance, assumed to be 100 Ω
 * Rₘ - passed as minResistance, the value of R1
 * C  - passed as capacitance, the value of C1
 * Rₓ - the max resistance your configuration can read

`Pin` calculates this as its maxResistance field, for your convenience, 
as `Rₓ = t/C - Rᵢ - Rₘ

Think about this when choosing your components; you can get higher 
resolutions with smaller capacitance and minResistance - though, there 
are limitations placed on you by the resolution of the RPi's timer.  The
defaults represent a reasonable trade-off with a readable range of 
0..31 kΩ, and a time resolution of 30Hz.
