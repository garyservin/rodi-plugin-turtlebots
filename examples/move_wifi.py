#!/usr/bin/env python

import sys, os
sys.path.insert(0, os.path.abspath('../'))

import pyfirmata
import time

LEFT_SERVO  = 5
RIGHT_SERVO = 6

r = pyfirmata.Arduino("1234", address="192.168.4.1")

print r

time.sleep(1)

r.digital[LEFT_SERVO]._set_mode(pyfirmata.SERVO)
r.digital[RIGHT_SERVO]._set_mode(pyfirmata.SERVO)

r.digital[13].write(1)

print "Forward"
r.digital[LEFT_SERVO].write(0)
r.digital[RIGHT_SERVO].write(180)

time.sleep(2)
r.digital[13].write(0)

print "Reverse"
r.digital[LEFT_SERVO].write(180)
r.digital[RIGHT_SERVO].write(0)

time.sleep(2)
r.digital[13].write(1)

print "Right"
r.digital[LEFT_SERVO].write(0)
r.digital[RIGHT_SERVO].write(0)

time.sleep(2)
r.digital[13].write(0)

print "Left"
r.digital[LEFT_SERVO].write(180)
r.digital[RIGHT_SERVO].write(180)

time.sleep(2)
r.digital[13].write(1)

print "Stop"
r.digital[LEFT_SERVO]._set_mode(pyfirmata.OUTPUT)
r.digital[RIGHT_SERVO]._set_mode(pyfirmata.OUTPUT)

r.digital[13].write(0)

r.exit()
