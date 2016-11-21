# coding=utf-8
# Derived from circuit and code at:
# http://www.raspberrypi-spy.co.uk/2012/08/reading-analogue-sensors-with-one-gpio-pin/

import RPi.GPIO as GPIO
import time
from threading import Timer

class Pin:
    # From http://www.mosaic-industries.com/embedded-systems/microcontroller-projects/raspberry-pi/gpio-pin-electrical-specifications
    PI_INTERNAL_RESISTANCE = 100 # Ω
    # Defaul capacitance is 1 μF
    def __init__(self, pin, minResistance=2200, capacitance=0.0000001, timeout=0.03333):
        # Setup state variables
        self.pin = pin
        self.open = True
        self.time = None
        self.resistance = None
        self.minResistance = minResistance
        self.capacitance = capacitance
        self.now = None
        self.timeout = timeout
        self.timer = None
        # Calculate max resistance from timeout
        # Given:
        #    T = self.timeout >= RC
        #    R = Rᵢ + Rₘ + Rₛ
        # Solve for Rₛ:
        #    T >= (Rᵢ + Rₘ + Rₛ) C
        #    T/C >= Rᵢ + Rₘ + Rₛ
        #    T/C - Rᵢ - Rₘ >= Rₛ
        self.maxResistance = self.timeout / self.capacitance - self.PI_INTERNAL_RESISTANCE - self.minResistance

        # Reset the pin, and listen for the change
        self.reset()
        # Ensure we have at least one measurement before returning control
        self.next(timeout=self.timeout)


    def reset(self):
        # Pull the pin's voltage to ground
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)
        # Hold voltage there long enough to discharge the capacitor
        #  Where:
        #      S: time to Drop from 2V to ~0.02V over RPi's internal resistance of 100 Ω
        #      T: Capacitor time to discharge by 63%
        #      Rᵢ: Raspberry Pi GPIO Internal resistance (100 ohms)
        #      N: Number of time constants to get to desired ratio
        #  S = T * N
        #  T = Rᵢ * C
        #  N = log(Vₗ / Vₕ) / log(63%)
        #  N = log(0.01) / log(0.63)
        #  N ≈ 10
        #  S = Rᵢ * C * 10
        start = time.time()
        sleepTime = self.PI_INTERNAL_RESISTANCE * 10 * self.capacitance
        time.sleep(sleepTime)
        # From python docs:
        # "The actual suspension time may be less than that requested because
        #  any caught signal will terminate the sleep() following execution of
        #  that signal’s catching routine."
        # So, make sure we wait _at least_ the allotted time; circuit discharge
        #  don't care about your processes.
        end = time.time()
        while end - start < sleepTime:
            time.sleep(sleepTime - now + end)
        # Reset the state timer
        self.now = time.time()
        # Switch the pin back to input mode
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        # Listen for the rising edge event
        # Minimum bouncetime, as a capacitor isn't going to bounce, and we want fast results
        GPIO.add_event_detect(self.pin, GPIO.RISING, callback=self.pinWentHigh, bouncetime=1)

        # Set a timer; if it times out, the the circuit is considered open
        self.timer = Timer(self.timeout, self.pinTimedOut)
        self.timer.start();

    def recordMeasurement(self, time):
        GPIO.remove_event_detect(self.pin)
        if time is None:
            self.open = True
            self.time = None
            self.resistance = None

        else:
            self.open = False
            self.time = time
            # Estimate the circuit resistance
            # Given:
            #   t = self.time = RC
            #   R = self.resistance = Rᵢ + Rₘ + Rₛ
            #   C = self.capacitance
            #   Rᵢ = PI_INTERNAL_RESISTANCE
            #   Rₘ = self.minResistance
            # Solve for Rₛ:
            #   t = (Rᵢ + Rₘ + Rₛ)C
            #   t / C = Rᵢ + Rₘ + Rₛ
            #   t / C - Rₘ - Rᵢ = Rₛ
            self.resistance = self.time / self.capacitance - self.minResistance - self.PI_INTERNAL_RESISTANCE

        # Reset the pin
        self.reset()

    # Pin timed out, meaning that the resistance across the sensor is over the
    # maximum; consider it an open circuit
    def pinTimedOut(self):
        self.recordMeasurement(None)

    # The pin went high, meaning that the resistance across the sensor is below
    # the maximum, and could charge the capacitor to 2V
    def pinWentHigh(self):
        # Cancel the timer, so as to avoid hitting the timeout
        self.timer.cancel()
        self.recordMeasurement(time.time() - self.now)

    def next(self, timeout=None):
        # Cancel the async events; they conflict, and would double-tap
        GPIO.remove_event_detect(self.pin)
        self.timer.cancel()

        if timeout is None:
            timeout = self.timeout
        if GPIO.wait_for_edge(self.pin, GPIO.RISING, timeout=int(timeout * 1000)) is None:
            self.pinTimedOut();
        else:
            self.pinWentHigh();
