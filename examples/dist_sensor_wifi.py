#!/usr/bin/env python

import sys, os
sys.path.insert(0, os.path.abspath('../'))

import pyfirmata
import time

sensor = 0
r = pyfirmata.Arduino("1234", address="192.168.4.1")
it = pyfirmata.util.Iterator(r)
it.start()

print r

blink = True
r.analog[sensor].enable_reporting()
for i in range(50):
    r.digital[13].write(blink)
    dist = r.analog[sensor].read()
    try:
        print(dist * 1023 / 29)
    except:
        pass
    blink = not blink
    time.sleep(0.1)

r.analog[sensor].disable_reporting()
r.exit()
