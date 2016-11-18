# coding=utf-8
# Usage sample

from AnalogPin import Pin
from RPi import GPIO

USE_PIN = 17
GPIO.setmode(GPIO.BCM)
aPin = Pin(USE_PIN, minResistance=2200, capacitance=0.000001, timeout=0.03333)
while True:
    try:
        if aPin.open:
            print "Sensor not connected"
        else:
            print str(aPin.measurement) + 's, ' + str(aPin.resistance) + 'Ω'
        # Wait for next measurement
        aPin.next()
    except:
        print "Exiting!"
        break

GPIO.cleanup()
