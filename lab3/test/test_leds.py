#!/usr/bin/env python3

import time
import random

from litex import RemoteClient

wb = RemoteClient()
wb.open()

# # #

# Test led
print("Testing Led...")

wb.regs.leds_out.write(1)
time.sleep(0.5)
wb.regs.leds_out.write(2)
time.sleep(0.5)
wb.regs.leds_out.write(4)
time.sleep(0.5)
wb.regs.leds_out.write(8)
time.sleep(0.5)
wb.regs.leds_out.write(16)
time.sleep(0.5)
wb.regs.leds_out.write(32)
time.sleep(0.5)
wb.regs.leds_out.write(64)
time.sleep(0.5)


for i in range(64):
		wb.regs.leds_out.write(i)
		time.sleep(0.5)
    

wb.close()
