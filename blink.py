#!/usr/bin/env python
import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
led = 4
GPIO.setup(led, GPIO.OUT)
while (1):
    print "on"
    GPIO.output(led, 1)
    time.sleep(1)
    print "off"
    GPIO.output(led, 0)
    time.sleep(1)

