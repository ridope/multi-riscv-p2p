#!/usr/bin/env python3

# Copyright (c) 2022 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
import argparse

from litex.build.altera import AlteraPlatform
from litex.build.altera.programmer import USBBlaster

#from litex_boards.platforms import digilent_arty
#from litex.build.xilinx.vivado import vivado_build_args, vivado_build_argdict

from litex.soc.cores.clock import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.uart import * 

from litex.build.generic_platform import *
from migen.genlib.io import CRG

from ios import Led, Button, Switch
from display import SevenSegmentDisplay

from litex.soc.cores.uart import UARTWishboneBridge

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
    
    ("user_btn", 1, Pins("A7"), IOStandard("3.3-V LVTTL")), #last: user_btn_2

	#user switchs
    ("user_sw", 0, Pins("C10"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 1, Pins("C11"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 2, Pins("D12"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 3, Pins("C12"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 4, Pins("A12"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 5, Pins("B12"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 6, Pins("A13"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 7, Pins("A14"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 8, Pins("B14"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 9, Pins("F15"), IOStandard("3.3-V LVTTL")),

	#7 seg display  
    ("display_1", 0, Pins("C14 E15 C15 C16 E16 D17 C17 D15"), IOStandard("3.3-V LVTTL")),
    ("display_2", 0, Pins("C18 D18 E18 B16 A17 A18 B17 A16"), IOStandard("3.3-V LVTTL")),
    ("display_3", 0, Pins("B20 A20 B19 A21 B21 C22 B22 A19"), IOStandard("3.3-V LVTTL")),
    ("display_4", 0, Pins("F21 E22 E21 C19 C20 D19 E17 D22"), IOStandard("3.3-V LVTTL")),
    ("display_5", 0, Pins("F18 E20 E19 J18 H19 F19 F20 F17"), IOStandard("3.3-V LVTTL")),
    ("display_6", 0, Pins("J20 K20 L18 N18 M20 N19 N20 L19"), IOStandard("3.3-V LVTTL")),
    
    # spi / accelerometer
    
    ("adxl362_spi", 0,
        Subsignal("cs_n", Pins("AB16")), #GSENSOR_CS_n
        Subsignal("clk", Pins("AB15")), #GSENSOR_SCLK
        Subsignal("mosi", Pins("V11")), #GSENSOR_DI
        Subsignal("miso", Pins("V12")), #GSENSOR_SDO
        IOStandard("3.3-V LVTTL")
    ),
    
    # uart
    
    ("serial", 0,
        Subsignal("tx", Pins("V10"), IOStandard("3.3-V LVTTL")), #  GPIO[0]
        Subsignal("rx", Pins("W10"), IOStandard("3.3-V LVTTL"))  #  GPIO[1]
    ),
    
    
     ("acc_spi", 0,
        Subsignal("mosi", Pins("V11")),
        Subsignal("miso", Pins("V12")),
        Subsignal("clk", Pins("AB15")),
        Subsignal("cs_n", Pins("AB16")),   #mode selection (master or slave)
        IOStandard("3.3-V LVTTL")
    )
    
        
]


# Platform

class Platform(AlteraPlatform):
	default_clk_name = "clk50"
	default_clk_period = 1e9/50e6
	create_rbf = False
	
	def __init__(self):
        	AlteraPlatform.__init__(self, "10M50DAF484C7G", _io)
        	
# Design -------------------------------------------------------------------------------------------

# Create our platform (fpga interface)
platform = Platform()




# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq, with_rst=False):
        self.rst = Signal()
        self.clock_domains.cd_sys = ClockDomain()

        # # #

        # Clk/Rst.
        clk100 = platform.request("clk50")
        rst    = ~platform.request("cpu_reset") if with_rst else 0

        # Update: PLL deleted


# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCMini):
    mem_map = {**SoCCore.mem_map, **{
        "csr": 0x10000000,
    }}
    def __init__(self, platform, toolchain="quartus", sys_clk_freq=int(50e6), with_led_chaser=True):
        platform = Platform() #(toolchain = toolchain)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # SoCMini ----------------------------------------------------------------------------------
        SoCMini.__init__(self, platform, sys_clk_freq, ident="LiteX standalone SoC generator on Arty A7")

        # JTAGBone ---------------------------------------------------------------------------------
        self.add_jtagbone()

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)


        # Standalone SoC Generation/Re-Integration -------------------------------------------------


        # Standalone SoC Generation/Re-Integration -------------------------------------------------

        # Shared UART.
        uart_pads = platform.request("serial")
        uart_sel  = platform.request("user_sw", 0)
        uart_mux_pads = [UARTPads() for _ in range(2)]
        uart_mux      = UARTMultiplexer(uart_mux_pads, uart_pads)
        self.comb += uart_mux.sel.eq(uart_sel)
        self.submodules += uart_mux

        # Shared RAM.
        self.add_ram("shared_ram", 0x0000_0000, 0x1000, contents=[i for i in range(16)])

        # FemtoRV SoC.
        # ------------

        # Generate standalone SoC.
        os.system("litex_soc_gen --cpu-type=femtorv --bus-standard=wishbone --sys-clk-freq=50e6 --name=femtorv_soc --build")

        # Add standalone SoC sources.
        platform.add_source("build/femtorv_soc/gateware/femtorv_soc.v")
        platform.add_source("build/femtorv_soc/gateware/femtorv_soc_rom.init", copy=True)

        # Add CPU sources.
        from litex.soc.cores.cpu.femtorv import FemtoRV
        FemtoRV.add_sources(platform, "standard")

        # Do standalone SoC instance.
        mmap_wb = wishbone.Interface()
        self.specials += Instance("femtorv_soc",
            # Clk/Rst.
            i_clk     = ClockSignal("sys"),
         #  i_rst     = ResetSignal("sys"),

            # UART.
            o_uart_tx = uart_mux_pads[0].tx,
            i_uart_rx = uart_mux_pads[0].rx,

            # MMAP.
            o_mmap_m_adr   = mmap_wb.adr[:24], # CHECKME/FIXME: Base address
            o_mmap_m_dat_w = mmap_wb.dat_w,
            i_mmap_m_dat_r = mmap_wb.dat_r,
            o_mmap_m_sel   = mmap_wb.sel,
            o_mmap_m_cyc   = mmap_wb.cyc,
            o_mmap_m_stb   = mmap_wb.stb,
            i_mmap_m_ack   = mmap_wb.ack,
            o_mmap_m_we    = mmap_wb.we,
            o_mmap_m_cti   = mmap_wb.cti,
            o_mmap_m_bte   = mmap_wb.bte,
            i_mmap_m_err   = mmap_wb.err,
        )
        self.bus.add_master(master=mmap_wb)

        # Litescope.
     #   from litescope import LiteScopeAnalyzer
     #   self.submodules.analyzer = LiteScopeAnalyzer([mmap_wb],
     #       depth        = 512,
     #       clock_domain = "sys",
     #       samplerate   = sys_clk_freq,
     #       csr_csv      = "analyzer.csv"
     #   )

        # FireV SoC.
        # ----------

        # Generate standalone SoC.
        os.system("litex_soc_gen --cpu-type=firev --bus-standard=wishbone --sys-clk-freq=50e6 --name=firev_soc --build")

        # Add standalone SoC sources.
        platform.add_source("build/firev_soc/gateware/firev_soc.v")
        platform.add_source("build/firev_soc/gateware/firev_soc_rom.init", copy=True)

        # Add CPU sources.
        from litex.soc.cores.cpu.firev import FireV
        FireV.add_sources(platform, "standard")

        # Do standalone SoC instance.
        mmap_wb = wishbone.Interface()
        self.specials += Instance("firev_soc",
            # Clk/Rst.
            i_clk     = ClockSignal("sys"),
        #   i_rst     = ResetSignal("sys"),

            # UART.
            o_uart_tx = uart_mux_pads[1].tx,
            i_uart_rx = uart_mux_pads[1].rx,

            # MMAP.
            o_mmap_m_adr   = mmap_wb.adr[:24], # CHECKME/FIXME: Base address.
            o_mmap_m_dat_w = mmap_wb.dat_w,
            i_mmap_m_dat_r = mmap_wb.dat_r,
            o_mmap_m_sel   = mmap_wb.sel,
            o_mmap_m_cyc   = mmap_wb.cyc,
            o_mmap_m_stb   = mmap_wb.stb,
            i_mmap_m_ack   = mmap_wb.ack,
            o_mmap_m_we    = mmap_wb.we,
            o_mmap_m_cti   = mmap_wb.cti,
            o_mmap_m_bte   = mmap_wb.bte,
            i_mmap_m_err   = mmap_wb.err,
        )
        self.bus.add_master(master=mmap_wb)


# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX standalone SoC generator")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--toolchain",    default="quartus",    help="FPGA toolchain")
    target_group.add_argument("--build",        action="store_true", help="Build bitstream.")
    target_group.add_argument("--load",         action="store_true", help="Load bitstream.")
    target_group.add_argument("--flash",        action="store_true", help="Flash bitstream.")
    target_group.add_argument("--sys-clk-freq", default=50e6,       help="System clock frequency.")
    builder_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
    	platform       = Platform(),
        toolchain      = args.toolchain,
        sys_clk_freq   = int(float(args.sys_clk_freq)),
    )

    builder = Builder(soc, **builder_argdict(args))
    builder_kwargs = {}
    builder.build(**builder_kwargs, run=args.build)

#    if args.load:
#        prog = soc.platform.create_programmer()
#        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

#    if args.flash:
#        prog = soc.platform.create_programmer()
#        prog.flash(0, builder.get_bitstream_filename(mode="flash"))

if __name__ == "__main__":
    main()
