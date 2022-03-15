#!/usr/bin/env python3

import time
import datetime

from litex import RemoteClient

wb = RemoteClient()
wb.open()

# # #


def display1_write(value):
	wb.regs.display1_value.write(value)
	wb.regs.display1_write.write(1)
    
def display2_write(value):
	wb.regs.display2_value.write(value)
	wb.regs.display2_write.write(1)

def display3_write(value):
	wb.regs.display3_value.write(value)
	wb.regs.display3_write.write(1)

def display4_write(value):
	wb.regs.display4_value.write(value)
	wb.regs.display4_write.write(1)

def display5_write(value):
	wb.regs.display5_value.write(value)
	wb.regs.display5_write.write(1)

def display6_write(value):
	wb.regs.display6_value.write(value)
	wb.regs.display6_write.write(1)          


def display_time(hour, minute, second):
    display1_write(second%10)
    display2_write((second//10)%10)
    display3_write(minute%10)
    display4_write((minute//10)%10)
    display5_write(hour%10)
    display6_write((hour//10)%10)

print("Testing SevenSegmentDisplay...")
while True:
    t = datetime.datetime.now()
    display_time(t.hour, t.minute, t.second)
    time.sleep(0.2)

# # #

wb.close()
