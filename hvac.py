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
import signal
import sys
from datetime import datetime
from time import sleep

debug = False
if len(sys.argv) > 1:
  debug = True

min_temp = 26.5 if debug else 21.1 # ~70°F
max_temp = 27 if debug else 23.3 # ~74°F
relay_pin = 22 # GPIO22
base_path = os.path.dirname(os.path.abspath(__file__))

"""
Parts:
  [Pi] Zero W
  Ximimark [SHT31-D] temp/humidity sensor board, connect to Rapsberry Pi 0W:
  Auber SRDA25-LD 25A AC solid state relay [LRSSR-DA]
  [2N3904] NPN transistor
  1W [10kΩ] resistor
  1W [1kΩ] resistor
  1W [470Ω] resistor

Connections:
  Pi GND → SHT31-D GND
  Pi GND → 10kΩ → 2N3904 base → 1kΩ → Pi GPIO22
  Pi GND → 2N3904 emitter
  Pi 3V3+ → SHT31-D VIN
  Pi SCL → SHT31-D SCL
  Pi SDA → SHT31-D SDA
  Pi 5V+ → 470Ω → LRSSR-DA Input 3 (3-32VDC+)
  LRSSR-DA Input 4 (3-32VDC-) → 2N3904 collector
  LRSSR-DA Output 1 → 120V AC hot
  LRSSR-DA Output 2 → 120V AC neutral
"""

def sig_figs(num, figs):
  """Return <figs> number of significant figures passed in for <num> passed in."""
  return float(f'''{float(f"{num:.{figs}g}"):g}''')

def c_to_f(c):
  """Convert °C to °F."""
  return sig_figs(float(c) * 9 / 5 + 32, 3)

def log(msg):
  """Log message to file."""
  with open(os.path.join(base_path, 'hvac_messages.log'), 'a+') as hvac_logs:
    msg = f"\n{datetime.now()} {msg}"
    hvac_logs.write(msg)
    if debug:
      print(msg.strip('\n'))

i2c = board.I2C()
sht31d = adafruit_sht31d.SHT31D(i2c)

GPIO.setmode(GPIO.BCM)
GPIO.setup(relay_pin, GPIO.OUT)

class Hvac:
  time_to_exit = False

  def __init__(self):
    signal.signal(signal.SIGINT, self.end_script)
    signal.signal(signal.SIGTERM, self.end_script)
  
  def end_script(self):
    GPIO.output(relay_pin, GPIO.LOW)
    GPIO.cleanup()
    msg = f"[STOP]: Stopping service."
    log(msg)
    self.time_to_exit = True

  msg = f"[START]: Started service; minimum temp: {min_temp}°C ({c_to_f(min_temp)}°F), maximum temp: {max_temp}°C ({c_to_f(max_temp)}°F)."
  log(msg)

if __name__ == '__main__':
  looper = Hvac()
  checks = 0
  try:
    while not looper.time_to_exit:
      temp = sig_figs(sht31d.temperature, 3)
      hum = sig_figs(sht31d.relative_humidity, 3)
      msg = f"[LOG]: {temp}°C ({c_to_f(temp)}°F), {hum}%RH"

      if checks == 0 or debug:
        log(msg)
      checks = 0 if checks == 5 else checks + 1

      if temp <= min_temp and not GPIO.input(relay_pin):
        msg = f"[RELAY]: Temperature is currently {temp}°C ({c_to_f(temp)}°F) and relay circuit is currently open; closing relay."
        log(msg)
        GPIO.output(relay_pin, GPIO.HIGH)
      elif temp >= max_temp and GPIO.input(relay_pin):
        msg = f"[RELAY]: Temperature is currently {temp}°C ({c_to_f(temp)}°F) and relay circuit is currently closed; opening relay."
        log(msg)
        GPIO.output(relay_pin, GPIO.LOW)
      sleep(5 if debug else 10)
  except KeyboardInterrupt:
    msg = f"[ERROR]: Caught keyboard interrupt, cleaning up and exiting now."
    log(msg)
