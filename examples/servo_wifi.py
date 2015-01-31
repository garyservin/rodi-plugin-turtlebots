#!/usr/bin/env python

import sys, os
sys.path.insert(0, os.path.abspath('../'))

import pyfirmata
import time

r = pyfirmata.Arduino("1234", address="192.168.4.1")
print r

SERVO_TEST = 5

r.digital[SERVO_TEST]._set_mode(pyfirmata.SERVO)

r.digital[SERVO_TEST].write(0)

time.sleep(2)

r.digital[SERVO_TEST].write(180)

time.sleep(2)

r.digital[SERVO_TEST]._set_mode(pyfirmata.OUTPUT)

r.exit()
