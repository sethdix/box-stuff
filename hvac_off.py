#!/usr/bin/python3

import RPi.GPIO as GPIO

relay_pin = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(relay_pin, GPIO.OUT)
GPIO.output(relay_pin, GPIO.LOW)
GPIO.cleanup()
