#!/usr/bin/python3

# SPDX-FileCopyrightText: 2023 Seth Dix
# SPDX-License-Identifier: 0BSD

"""
Zero-Clause BSD
=============

Permission to use, copy, modify, and/or distribute this software for
any purpose with or without fee is hereby granted.

THE SOFTWARE IS PROVIDED “AS IS” AND THE AUTHOR DISCLAIMS ALL
WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES
OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE
FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY
DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN
AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
"""

import adafruit_sht31d
import board
import RPi.GPIO as GPIO
import sys
from time import sleep

min_temp = 21.1 # ~70°C
max_temp = 23.3 # ~74°C
relay_pin = 22 # GPIO22

"""
I2C (inter-integrated circuit) bus uses SDL (serial data line) and SCL (serial
clock line) to read data from peripheral boards.

Using Ximimark SHT31-D temp/humidity sensor board, connect to Rapsberry Pi 0W:
  VIN → Pi 3V3+
  GND → Pi GND
  SCL → Pi SCL
  SDA → Pi SDA

Connections for Auber SRDA25-LD 25A AC solid state relay (LRSSR-DA 25A) using
2N3904 NPN transistor:
  Output 1 → 120V AC hot
  Output 2 → 120V AC neutral
  Input 3 (3-32VDC+) → 200Ω series resistor → Pi 3V3+
  Input 4 (3-32VDC-) → 2N3904 emitter pin (E)

Additional connections for 2N3904 transistor:
  2N3904 base (B) pin → 200Ω series resistor → Pi BCM relay_pin
  2N3904 collector (C) pin → GND
"""
i2c = board.I2C()
sht31d = adafruit_sht31d.SHT31D(i2c)

GPIO.setmode(GPIO.BCM)
GPIO.setup(relay_pin, GPIO.OUT)

def sig_figs(num, figs):
  return float(f'''{float(f"{num:.{figs}g}"):g}''')

def c_to_f(c):
  """Convert °C to °F."""
  return sig_figs(float(c) * 9 / 5 + 32, 3)

try:
  while True:
    temp = sig_figs(sht31d.temperature, 3)
    hum = sig_figs(sht31d.relative_humidity, 3)
    print(f"temperature: {temp}°C ({c_to_f(temp)}°F), humidity: {hum}%RH")
    if temp <= min_temp and not GPIO.input(relay_pin):
      print(f"Temperature is currently {temp}°C ({c_to_f(temp)}°F) and relay circuit is currently open; closing relay.")
      GPIO.output(relay_pin, GPIO.HIGH)
    elif temp >= max_temp and GPIO.input(relay_pin):
      print(f"Temperature is currently {temp}°C ({c_to_f(temp)}°F) and relay circuit is currently closed; opening relay.")
      GPIO.output(relay_pin, GPIO.LOW)
    sleep(10)
except KeyboardInterrupt:
  print(f"\nCaught keyboard interrupt, cleaning up and exiting now.")
  GPIO.output(relay_pin, GPIO.LOW)
  GPIO.cleanup()
  sys.exit()
