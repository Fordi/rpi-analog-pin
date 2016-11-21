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
as `Rₓ = t/C - Rᵢ - Rₘ`

Think about this when choosing your components; you can get higher
resolutions with smaller capacitance and minResistance - though, there
are limitations placed on you by the resolution of the RPi's timer.  The
defaults represent a reasonable trade-off with a readable range of
0..31 kΩ, and a time resolution of 30Hz.

To make things easier for you, I built a little [weblet](https://fordi.github.io/)
you can use to calculate what your constructor should look like given a set of
components.

After the `Pin` is initialized, it will continuously read the resistance
connected to it in the background.  Your program can simply check the
value of `aPin.resistance` as it needs to.

### Movement events

The library also supports event handling, where you can specify what sort of
behavior you're looking to capture.

#### listen(callback, low, high, signal, [samples=1])

Listen for when `resistance` enters, exits, or crosses over a given range

> callback: handler to call

> low: low end of range

> high: high end of range

> signal: One of the following values

> * Pin.RISE
>
>     Trigger when resistance rises past `high` for `samples`;
>     will not trigger again until resistance falls
>     past `low` for `samples`
>
> * Pin.FALL
>
>     Trigger when resistance falls past `low` for `samples`;
>     will not trigger again until resistance falls
>     past `low` for `samples`
>
> * Pin.ENTER
>
>       Trigger when resistance falls within the selected range for
>       `samples`; will not trigger again until resistance
>       falls outside of range for `samples`
>
> * Pin.EXIT
>
>       Trigger when resistance falls outside the selected range for
>       `samples`; will not trigger again until resistance
>       fallse within range for `samples`
>
> * Pin.BOTH: Pin.RISE | Pin.FALL
> * Pin.TRANSIT: Pin.ENTER | Pin.EXIT

> samples [default=1]: number of samples matching condition before trigger

-----

#### feel(handler, start, end, signal, [samples=1])

Listen for when resistance moves more than a starting threshold, and then
when it moves less than an ending threshold

> handler: callback to trigger

> start: change in resistance to trigger start signal

> end: change in resistance to trigger end signal

> signal: One of the following values

> * Pin.CHANGE/Pin.RISE/Pin.FALL
>
>    Trigger a `CHANGE_START` event when resistance changes by at
>    least `thresholdStart` over `samples`; trigger a `CHANGE_END` when
>    resistance changes by less than `thresholdEnd` over one sample.
>    Pin.RISE and Pin.FALL only trigger the events when the change
>    is positive and negative, respectively
>
>  Pin.STEADY
>
>    Trigger a `STEADY_START` event when resistance changes by less than
>    `thresholdStart` for at least `samples`; trigger a `STEADY_END` when
>    resistance changes by more than `thresholdEnd` over one sample

-----

#### each(handler, [rate=None])

Invoke callback on each measurement, with optional rate limit

> handler: callback to trigger
> rate: maximum rate, in Hz, at which you want to invoke the handler.
