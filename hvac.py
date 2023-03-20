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
import os
import RPi.GPIO as GPIO
import sys
from datetime import datetime
from time import sleep

#min_temp = 25 # debugging
#max_temp = 26 # debugging
min_temp = 21.1 # ~70°C
max_temp = 23.3 # ~74°C
relay_pin = 22 # GPIO22

base_path = os.path.dirname(os.path.abspath(__file__))

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
  """Return <figs> number of significant figures passed in for <num> passed in."""
  return float(f'''{float(f"{num:.{figs}g}"):g}''')

def c_to_f(c):
  """Convert °C to °F."""
  return sig_figs(float(c) * 9 / 5 + 32, 3)

def log(msg):
  """Log message to file."""
  with open(os.path.join(base_path, 'hvac_messages.log'), 'a+') as hvac_logs:
    hvac_logs.write(f"\n{datetime.now()} {msg}")

msg = f"[START]: Started service; minimum temp: {min_temp}°C ({c_to_f(min_temp)}°F), maximum temp: {max_temp}°C ({c_to_f(max_temp)}°F)."
# print(msg)
log(msg)

try:
  checks = 0
  while True:
    temp = sig_figs(sht31d.temperature, 3)
    hum = sig_figs(sht31d.relative_humidity, 3)
    msg = f"[LOG]: {temp}°C ({c_to_f(temp)}°F), {hum}%RH"

    if checks == 0:
      log(msg)
    checks = 0 if checks == 5 else checks + 1

    if temp <= min_temp and not GPIO.input(relay_pin):
      msg = f"[RELAY]: Temperature is currently {temp}°C ({c_to_f(temp)}°F) and relay circuit is currently open; closing relay."
      # print(msg)
      log(msg)
      GPIO.output(relay_pin, GPIO.HIGH)
    elif temp >= max_temp and GPIO.input(relay_pin):
      msg = f"[RELAY]: Temperature is currently {temp}°C ({c_to_f(temp)}°F) and relay circuit is currently closed; opening relay."
      # print(msg)
      log(msg)
      GPIO.output(relay_pin, GPIO.LOW)
    sleep(10)
except KeyboardInterrupt:
  msg = f"[ERROR]: Caught keyboard interrupt, cleaning up and exiting now."
  # print(msg)
  log(msg)
  GPIO.output(relay_pin, GPIO.LOW)
  GPIO.cleanup()
  msg = f"[STOP]: Stopped service."
  # print(msg)
  log(msg)
  sys.exit()
