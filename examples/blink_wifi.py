#!/usr/bin/env python

import sys, os
sys.path.insert(0, os.path.abspath('../'))

import pyfirmata
import time

r = pyfirmata.Arduino("1234", address="192.168.4.1")

print r

blink = True
for i in range(10):
    r.digital[13].write(blink)
    blink = not blink
    time.sleep(0.5)

r.exit()
