#!/usr/bin/env python3

from migen import *

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.altera.programmer import USBBlaster

# IO's

_io = [

	#50 Mhz clock
    ("clk50",  0, Pins("N14"), IOStandard("3.3-V LVTTL")),

	#board leds
    ("user_led", 0, Pins("A8"), IOStandard("3.3-V LVTTL")),
    ("user_led", 1, Pins("A9"), IOStandard("3.3-V LVTTL")),
    ("user_led", 2, Pins("A10"), IOStandard("3.3-V LVTTL")),
    ("user_led", 3, Pins("B10"), IOStandard("3.3-V LVTTL")),
    ("user_led", 4, Pins("D13"), IOStandard("3.3-V LVTTL")),
    ("user_led", 5, Pins("C13"), IOStandard("3.3-V LVTTL")),
    ("user_led", 6, Pins("E14"), IOStandard("3.3-V LVTTL")),
    ("user_led", 7, Pins("D14"), IOStandard("3.3-V LVTTL")),
    ("user_led", 8, Pins("A11"), IOStandard("3.3-V LVTTL")),
    ("user_led", 9, Pins("B11"), IOStandard("3.3-V LVTTL")),

	#buttons
    ("user_btn", 0, Pins("B8"), IOStandard("3.3-V LVTTL")),
    ("user_btn", 1, Pins("A7"), IOStandard("3.3-V LVTTL")),

	#user switchs
    ("user_sw", 0, Pins("C10"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 1, Pins("C11"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 2, Pins("D12"), IOStandard("3.3-V LVTTL")),

	#7 seg display  
    ("seven_seg", 1, Pins("C18 D18 E18 B16 A17 A18 B17 A16"), IOStandard("3.3-V LVTTL")),
]


# Platform

class Platform(AlteraPlatform):
	default_clk_name = "clk50"
	default_clk_period = 1e9/50e6
	create_rbf = False
	
	def __init__(self):
        	AlteraPlatform.__init__(self, "10M50DAF484C7G", _io)

    #	def create_programmer(self):
    #    	return USBBlaster()
        	
# Design


# Creating the platform (fpga interface)        
platform = Platform()

# Creating the module (fpga description)
class Blink(Module):
    def __init__(self, blink_freq, sys_clk_freq, led):
        counter = Signal(32)     
        # synchronous assignments
        self.sync += [
            counter.eq(counter + 1),
            If(counter == int((sys_clk_freq/blink_freq)/2 - 1),
                counter.eq(0),
                led.eq(~led) #toggle the led
            )
        ]
        # combinatorial assignements
        self.comb += []

module = Blink(1, 100e6, platform.request("user_led"))


# build


platform.build(module)

# load

# prog = USBBlaster
# prog.load_bitstream("bitstream.sof")
	









