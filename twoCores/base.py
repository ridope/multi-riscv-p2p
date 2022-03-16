#!/usr/bin/env python3

from migen import *

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.altera.programmer import USBBlaster
from migen.genlib.cdc import MultiReg

from migen.genlib.io import CRG

from ios import Led, Button, Switch
from display import SevenSegmentDisplay

from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.uart import UARTWishboneBridge
from litex.soc.cores.spi import SPIMaster


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

	#buttons
    ("user_btn", 0, Pins("B8"), IOStandard("3.3-V LVTTL")),

	#user switchs
    ("user_sw", 0, Pins("C10"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 1, Pins("C11"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 2, Pins("D12"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 3, Pins("C12"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 4, Pins("A12"), IOStandard("3.3-V LVTTL")),

	#7 seg display  
    ("display_1", 0, Pins("C14 E15 C15 C16 E16 D17 C17 D15"), IOStandard("3.3-V LVTTL")),
    ("display_2", 0, Pins("C18 D18 E18 B16 A17 A18 B17 A16"), IOStandard("3.3-V LVTTL")),
    ("display_3", 0, Pins("B20 A20 B19 A21 B21 C22 B22 A19"), IOStandard("3.3-V LVTTL")),
    
    
    # uart
    
    ("serial", 0,
        Subsignal("tx", Pins("V10"), IOStandard("3.3-V LVTTL")), #  GPIO[0]
        Subsignal("rx", Pins("W10"), IOStandard("3.3-V LVTTL"))  #  GPIO[1]
    ),
        
]


_io_2 = [

	#50 Mhz clock
    ("clk50_2",  0, Pins("P11"), IOStandard("3.3-V LVTTL")),

	#board leds
    ("user_led", 5, Pins("C13"), IOStandard("3.3-V LVTTL")),
    ("user_led", 6, Pins("E14"), IOStandard("3.3-V LVTTL")),
    ("user_led", 7, Pins("D14"), IOStandard("3.3-V LVTTL")),
    ("user_led", 8, Pins("A11"), IOStandard("3.3-V LVTTL")),
    ("user_led", 9, Pins("B11"), IOStandard("3.3-V LVTTL")),

	#buttons
    
    ("user_btn", 1, Pins("A7"), IOStandard("3.3-V LVTTL")), #last: user_btn_2

	#user switchs
    ("user_sw", 5, Pins("B12"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 6, Pins("A13"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 7, Pins("A14"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 8, Pins("B14"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 9, Pins("F15"), IOStandard("3.3-V LVTTL")),

	#7 seg display  
    ("display_4", 0, Pins("F21 E22 E21 C19 C20 D19 E17 D22"), IOStandard("3.3-V LVTTL")),
    ("display_5", 0, Pins("F18 E20 E19 J18 H19 F19 F20 F17"), IOStandard("3.3-V LVTTL")),
    ("display_6", 0, Pins("J20 K20 L18 N18 M20 N19 N20 L19"), IOStandard("3.3-V LVTTL")),
    
        ("serial", 0,
        Subsignal("tx", Pins("V10"), IOStandard("3.3-V LVTTL")), #  GPIO[0]
        Subsignal("rx", Pins("W10"), IOStandard("3.3-V LVTTL"))  #  GPIO[1]
    ),
        
]


# Platform

class Platform(AlteraPlatform):
	default_clk_name = "clk50"
	default_clk_period = 1e9/50e6
	create_rbf = False
	
	def __init__(self):
        	AlteraPlatform.__init__(self, "10M50DAF484C7G", _io)
        	
# Design -------------------------------------------------------------------------------------------

# Create our soc (fpga description)
class BaseSoC(SoCCore):
    def __init__(self, platform):
        sys_clk_freq = int(50e6)

        # SoC with CPU
        SoCCore.__init__(self, platform,
            cpu_type                 = "vexriscv",
            clk_freq                 = 50e6,
            ident                    = "LiteX CPU Test SoC", ident_version=True,
            integrated_rom_size      = 0x8000,
            integrated_main_ram_size = 0x4000)

        # Led
        user_leds = Cat(*[platform.request("user_led", i) for i in range(5)])
        self.submodules.leds = Led(user_leds)
        self.add_csr("leds")

        # Switches
        user_switches = Cat(*[platform.request("user_sw", i) for i in range(5)])
        self.submodules.switches = Switch(user_switches)
        self.add_csr("switches")

        # Buttons
        user_buttons = platform.request("user_btn")
        self.submodules.buttons = Button(user_buttons)
        self.add_csr("buttons")
        

        # SevenSegmentDisplay
        self.submodules.display1 = SevenSegmentDisplay(sys_clk_freq)
        self.add_csr("display1")
        self.submodules.display2 = SevenSegmentDisplay(sys_clk_freq)
        self.add_csr("display2")
        self.submodules.display3 = SevenSegmentDisplay(sys_clk_freq)
        self.add_csr("display3")

        self.comb += [
            platform.request("display_1").eq(~self.display1.abcdefg),
            platform.request("display_2").eq(~self.display2.abcdefg),
            platform.request("display_3").eq(~self.display3.abcdefg)
            
        ]

# Create our soc (fpga description)
class SecondSoC(SoCCore):
    def __init__(self, platform):
        sys_clk_freq = int(50e6)

        # SoC with CPU
        SoCCore.__init__(self, platform,
            cpu_type                 = "vexriscv",
            clk_freq                 = 50e6,
            ident                    = "LiteX CPU Test SoC", ident_version=True,
            integrated_rom_size      = 0x8000,
            integrated_main_ram_size = 0x4000)


        # Buttons
        user_buttons_2 = platform.request("user_btn")
        self.submodules.buttons = Button(user_buttons_2)
        self.add_csr("buttons_2")
        

        # SevenSegmentDisplay
        self.submodules.display4 = SevenSegmentDisplay(sys_clk_freq)
        self.add_csr("display4")
        self.submodules.display5 = SevenSegmentDisplay(sys_clk_freq)
        self.add_csr("display5")
        self.submodules.display6 = SevenSegmentDisplay(sys_clk_freq)
        self.add_csr("display6")

        self.comb += [
            platform.request("display_4").eq(~self.display4.abcdefg),
            platform.request("display_5").eq(~self.display5.abcdefg),
            platform.request("display_6").eq(~self.display6.abcdefg)
            
        ]

class Platform2(AlteraPlatform):
	default_clk_name = "clk50_2"
	default_clk_period = 1e9/50e6
	create_rbf = False
	
	def __init__(self):
        	AlteraPlatform.__init__(self, "10M50DAF484C7G", _io_2)
        	
# Design -------------------------------------------------------------------------------------------

# Create our platform (fpga interface)
platform = Platform()
platform2 = Platform2()



soc = BaseSoC(platform)
soc2 = SecondSoC(platform2)

# Build --------------------------------------------------------------------------------------------

builder = Builder(soc, output_dir="build", csr_csv="test/csr.csv")
builder.build(build_name="top")
builder = Builder(soc2, output_dir="build2", csr_csv="test/csr2.csv")
builder.build(build_name="top2")


