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
    ("user_sw", 3, Pins("C12"), IOStandard("3.3-V LVTTL")),
    

	#7 seg display  
 	("seven_seg", 0, Pins("C14 E15 C15 C16 E16 D17 C17 D15"), IOStandard("3.3-V LVTTL")),
    ("seven_seg", 1, Pins("C18 D18 E18 B16 A17 A18 B17 A16"), IOStandard("3.3-V LVTTL")),
    ("seven_seg", 2, Pins("B20 A20 B19 A21 B21 C22 B22 A19"), IOStandard("3.3-V LVTTL")),
    ("seven_seg", 3, Pins("F21 E22 E21 C19 C20 D19 E17 D22"), IOStandard("3.3-V LVTTL")),
    ("seven_seg", 4, Pins("F18 E20 E19 J18 H19 F19 F20 F17"), IOStandard("3.3-V LVTTL")),
    ("seven_seg", 5, Pins("J20 K20 L18 N18 M20 N19 N20 L19"), IOStandard("3.3-V LVTTL")),
    
]


# Platform

class Platform(AlteraPlatform):
	default_clk_name = "clk50"
	default_clk_period = 1e9/50e6
	create_rbf = False
	
	def __init__(self):
        	AlteraPlatform.__init__(self, "10M50DAF484C7G", _io)
        	
# Design


# Creating the platform (fpga interface)        
platform = Platform()

class Switches(Module):
    def __init__(self, platform):
        # synchronous assignments
        self.sync += []
        # combinatorial assignements
        for i in range(4):
            led = platform.request("user_led", i)
            sw = platform.request("user_sw", i)
            self.comb += led.eq(sw)

# OR and AND gate to toggle a led using the switches

class GateTesting(Module):
    def __init__(self, platform):
        # synchronous assignments
        self.sync += []
        # combinatorial assignements
        led1 = platform.request("user_led", 0)
        led2 = platform.request("user_led", 1)
        led3 = platform.request("user_led", 2)
        led4 = platform.request("user_led", 3)
        
        sw1 = platform.request("user_sw", 0)
        sw2 = platform.request("user_sw", 1)
        sw3 = platform.request("user_sw", 2)
        sw4 = platform.request("user_sw", 3)        
        
        
        self.comb += led1.eq(sw1 | sw2)
        self.comb += led2.eq(~(sw1 | sw2))
        self.comb += led3.eq(sw3 & sw4)
        self.comb += led4.eq(~(sw3 & sw4))
        
module = GateTesting(platform)


platform.build(module)
	
