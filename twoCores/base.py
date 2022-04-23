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
from litex.soc.cores.cpu import *
from litex.soc.integration.soc import *


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
        	
# Design -------------------------------------------------------------------------------------------

class CPUBlock():

    csr_map       = {}
    interrupt_map = {}
    mem_map       = {
        "rom":      0x00000000,
        "sram":     0x01000000,
        "main_ram": 0x40000000,
    }

    def __init__(self, platform, sys_clk_freq,
        # Bus parameters
        bus_standard             = "wishbone",
        bus_data_width           = 32,
        bus_address_width        = 32,
        bus_timeout              = 1e6,
        bus_reserved_regions	 = {},

        # CPU parameters
        cpu_type                 = "vexriscv",
        cpu_reset_address        = None,
        cpu_variant              = None,
        cpu_cls                  = None,
        cpu_cfu                  = None,

        # CFU parameters
        cfu_filename             = None,

        # ROM parameters
        integrated_rom_size      = 0,
        integrated_rom_mode      = "r",
        integrated_rom_init      = [],

        # SRAM parameters
        integrated_sram_size     = 0x2000,
        integrated_sram_init     = [],

        # MAIN_RAM parameters
        integrated_main_ram_size = 0,
        integrated_main_ram_init = [],

        # CSR parameters
        csr_data_width           = 32,
        csr_address_width        = 14,
        csr_paging               = 0x800,
        csr_ordering             = "big",

        # Interrupt parameters
        irq_n_irqs               = 32,

        # Identifier parameters
        ident                    = "",
        ident_version            = False,

        # UART parameters
        with_uart                = True,
        uart_name                = "serial",
        uart_baudrate            = 115200,
        uart_fifo_depth          = 16,

        # Timer parameters
        with_timer               = True,
        timer_uptime             = False,

        # Controller parameters
        with_ctrl                = True,
        
        irq_reserved_irqs    = {},
		
        # Others
        **kwargs):
        

        self.logger = logging.getLogger("SoC")
        self.logger.info(colorer("        __   _ __      _  __  ", color="bright"))
        self.logger.info(colorer("       / /  (_) /____ | |/_/  ", color="bright"))
        self.logger.info(colorer("      / /__/ / __/ -_)>  <    ", color="bright"))
        self.logger.info(colorer("     /____/_/\\__/\\__/_/|_|  ", color="bright"))
        self.logger.info(colorer("  Build your hardware, easily!", color="bright"))

        self.logger.info(colorer("-"*80, color="bright"))
        self.logger.info(colorer("Creating SoC... ({})".format(build_time())))
        self.logger.info(colorer("-"*80, color="bright"))
        self.logger.info("FPGA device : {}.".format(platform.device))
        self.logger.info("System clock: {:3.3f}MHz.".format(sys_clk_freq/1e6))

        # SoC attributes ---------------------------------------------------------------------------
        self.platform     = platform
        self.sys_clk_freq = sys_clk_freq
        self.constants    = {}
        self.csr_regions  = {}

        # SoC Bus Handler --------------------------------------------------------------------------
        self.submodules.bus = SoCBusHandler(
            standard         = bus_standard,
            data_width       = bus_data_width,
            address_width    = bus_address_width,
            timeout          = bus_timeout,
            reserved_regions = bus_reserved_regions,
           )

        # SoC Bus Handler --------------------------------------------------------------------------
        self.submodules.csr = SoCCSRHandler(
            data_width    = csr_data_width,
            address_width = csr_address_width,
            alignment     = 32,
            paging        = csr_paging,
            ordering      = csr_ordering,
            reserved_csrs = self.csr_map,
        )

        # SoC IRQ Handler --------------------------------------------------------------------------
        self.submodules.irq = SoCIRQHandler(
            n_irqs        = irq_n_irqs,
            reserved_irqs = irq_reserved_irqs
        )

        self.logger.info(colorer("-"*80, color="bright"))
        self.logger.info(colorer("Initial SoC:"))
        self.logger.info(colorer("-"*80, color="bright"))
        self.logger.info(self.bus)
        self.logger.info(self.csr)
        self.logger.info(self.irq)
        self.logger.info(colorer("-"*80, color="bright"))

        self.add_config("CLOCK_FREQUENCY", int(sys_clk_freq))

    # SoC Helpers ----------------------------------------------------------------------------------
    def check_if_exists(self, name):
        if hasattr(self, name):
            self.logger.error("{} SubModule already {}.".format(
                colorer(name),
                colorer("declared", color="red")))
            raise SoCError()

    def add_constant(self, name, value=None):
        name = name.upper()
        if name in self.constants.keys():
            self.logger.error("{} Constant already {}.".format(
                colorer(name),
                colorer("declared", color="red")))
            raise SoCError()
        self.constants[name] = SoCConstant(value)

    def add_config(self, name, value=None):
        name = "CONFIG_" + name
        if isinstance(value, str):
            self.add_constant(name + "_" + value)
        else:
            self.add_constant(name, value)

    def check_bios_requirements(self):
        # Check for required Peripherals.
        for periph in [ "timer0"]:
            if periph not in self.csr.locs.keys():
                self.logger.error("BIOS needs {} peripheral to be {}.".format(
                    colorer(periph),
                    colorer("used", color="red")))
                self.logger.error(self.bus)
                raise SoCError()

        # Check for required Memory Regions.
        for mem in ["rom", "sram"]:
            if mem not in self.bus.regions.keys():
                self.logger.error("BIOS needs {} Region to be {} as Bus or Linker Region.".format(
                    colorer(mem),
                    colorer("defined", color="red")))
                self.logger.error(self.bus)
                raise SoCError()

    # SoC Main Components --------------------------------------------------------------------------
    def add_controller(self, name="ctrl", **kwargs):
        self.check_if_exists(name)
        setattr(self.submodules, name, SoCController(**kwargs))

    def add_ram(self, name, origin, size, contents=[], mode="rw"):
        ram_cls = {
            "wishbone": wishbone.SRAM,
            "axi-lite": axi.AXILiteSRAM,
        }[self.bus.standard]
        interface_cls = {
            "wishbone": wishbone.Interface,
            "axi-lite": axi.AXILiteInterface,
        }[self.bus.standard]
        ram_bus = interface_cls(data_width=self.bus.data_width)
        ram     = ram_cls(size, bus=ram_bus, init=contents, read_only=(mode == "r"))
        self.bus.add_slave(name, ram.bus, SoCRegion(origin=origin, size=size, mode=mode))
        self.check_if_exists(name)
        self.logger.info("RAM {} {} {}.".format(
            colorer(name),
            colorer("added", color="green"),
            self.bus.regions[name]))
        setattr(self.submodules, name, ram)

    def add_rom(self, name, origin, size, contents=[], mode="r"):
        self.add_ram(name, origin, size, contents, mode=mode)

    def init_rom(self, name, contents=[], auto_size=True):
        self.logger.info("Initializing ROM {} with contents (Size: {}).".format(
            colorer(name),
            colorer(f"0x{4*len(contents):x}")))
        getattr(self, name).mem.init = contents
        if auto_size and self.bus.regions[name].mode == "r":
            self.logger.info("Auto-Resizing ROM {} from {} to {}.".format(
                colorer(name),
                colorer(f"0x{self.bus.regions[name].size:x}"),
                colorer(f"0x{4*len(contents):x}")))
            getattr(self, name).mem.depth = len(contents)

    def add_csr_bridge(self, origin, register=False):
        csr_bridge_cls = {
            "wishbone": wishbone.Wishbone2CSR,
            "axi-lite": axi.AXILite2CSR,
        }[self.bus.standard]
        self.check_if_exists("csr_bridge")
        self.submodules.csr_bridge = csr_bridge_cls(
            bus_csr       = csr_bus.Interface(
            address_width = self.csr.address_width,
            data_width    = self.csr.data_width),
            register      = register)
        csr_size   = 2**(self.csr.address_width + 2)
        csr_region = SoCRegion(origin=origin, size=csr_size, cached=False)
        bus = getattr(self.csr_bridge, self.bus.standard.replace('-', '_'))
        self.bus.add_slave("csr", bus, csr_region)
        self.csr.add_master(name="bridge", master=self.csr_bridge.csr)
        self.add_config("CSR_DATA_WIDTH", self.csr.data_width)
        self.add_config("CSR_ALIGNMENT",  self.csr.alignment)

    def add_cpu(self, name="vexriscv", variant="standard", cls=None, reset_address=None, cfu=None):
        # Check that CPU is supported.
        if name not in cpu.CPUS.keys():
            self.logger.error("{} CPU {}, supporteds: {}.".format(
                colorer(name),
                colorer("not supported", color="red"),
                colorer(", ".join(cpu.CPUS.keys()))))
            raise SoCError()

        # Add CPU.
        if name == "external" and cls is None:
            self.logger.error("{} CPU requires {} to be specified.".format(
                colorer(name),
                colorer("cpu_cls", color="red")))
            raise SoCError()
        cpu_cls = cls if cls is not None else cpu.CPUS[name]
        if (variant not in cpu_cls.variants) and (cpu_cls is not cpu.CPUNone):
            self.logger.error("{} CPU variant {}, supporteds: {}.".format(
                colorer(variant),
                colorer("not supported", color="red"),
                colorer(", ".join(cpu_cls.variants))))
            raise SoCError()
        self.check_if_exists("cpu")
        self.submodules.cpu = cpu_cls(self.platform, variant)

        # Add optional CFU plugin.
        if "cfu" in variant and hasattr(self.cpu, "add_cfu"):
            self.cpu.add_cfu(cfu_filename=cfu)

        # Update SoC with CPU constraints.
        # IOs regions.
        for n, (origin, size) in enumerate(self.cpu.io_regions.items()):
            self.bus.add_region("io{}".format(n), SoCIORegion(origin=origin, size=size, cached=False))
        # Mapping.
        if isinstance(self.cpu, cpu.CPUNone):
            # With CPUNone, give priority to User's mapping.
            self.mem_map = {**self.cpu.mem_map, **self.mem_map}
        else:
            # Override User's mapping with CPU constrainted mapping (and warn User).
            for n, origin in self.cpu.mem_map.items():
                if n in self.mem_map.keys():
                    self.logger.info("CPU {} {} mapping from {} to {}.".format(
                        colorer("overriding", color="cyan"),
                        colorer(n),
                        colorer(f"0x{self.mem_map[n]:x}"),
                        colorer(f"0x{self.cpu.mem_map[n]:x}")))
            self.mem_map.update(self.cpu.mem_map)

        # Add Bus Masters/CSR/IRQs.
        if not isinstance(self.cpu, (cpu.CPUNone, cpu.Zynq7000)):
            if hasattr(self.cpu, "set_reset_address"):
                if reset_address is None:
                    reset_address = self.mem_map["rom"]
                self.cpu.set_reset_address(reset_address)
            for n, cpu_bus in enumerate(self.cpu.periph_buses):
                self.bus.add_master(name="cpu_bus{}".format(n), master=cpu_bus)
            if hasattr(self.cpu, "interrupt"):
                self.irq.enable()
                for name, loc in self.cpu.interrupts.items():
                    self.irq.add(name, loc)
                self.add_config("CPU_HAS_INTERRUPT")

            # Create optional DMA Bus (for Cache Coherence).
            if hasattr(self.cpu, "dma_bus"):
                self.submodules.dma_bus = SoCBusHandler(
                    name             = "SoCDMABusHandler",
                    standard         = "wishbone",
                    data_width       = self.bus.data_width,
                    address_width    = self.bus.address_width,
                )
                dma_bus = wishbone.Interface(data_width=self.bus.data_width)
                self.dma_bus.add_slave("dma", slave=dma_bus, region=SoCRegion(origin=0x00000000, size=0x100000000)) # FIXME: covers lower 4GB only
                self.submodules += wishbone.Converter(dma_bus, self.cpu.dma_bus)

            # Connect SoCController's reset to CPU reset.
            if hasattr(self, "ctrl"):
                self.comb += self.cpu.reset.eq(
                    # Reset the CPU on...
                    getattr(self.ctrl, "soc_rst", 0) | # Full SoC Reset command...
                    getattr(self.ctrl, "cpu_rst", 0)   # or on CPU Reset command.
                )
            self.add_config("CPU_RESET_ADDR", reset_address)

        # Add CPU's SoC components (if any).
        if hasattr(self.cpu, "add_soc_components"):
            self.cpu.add_soc_components(soc=self, soc_region_cls=SoCRegion) # FIXME: avoid passing SoCRegion.

        # Add constants.
        self.add_config("CPU_TYPE",    str(name))
        self.add_config("CPU_VARIANT", str(variant.split('+')[0]))
        self.add_constant("CONFIG_CPU_HUMAN_NAME", getattr(self.cpu, "human_name", "Unknown"))
        if hasattr(self.cpu, "nop"):
            self.add_constant("CONFIG_CPU_NOP", self.cpu.nop)

    def add_timer(self, name="timer0"):
        from litex.soc.cores.timer import Timer
        self.check_if_exists(name)
        setattr(self.submodules, name, Timer())
        if self.irq.enabled:
            self.irq.add(name, use_loc_if_exists=True)
            
    def add_identifier(self, name="identifier", identifier="LiteX SoC", with_build_time=True):
        from litex.soc.cores.identifier import Identifier
        self.check_if_exists(name)
        if with_build_time:
            identifier += " " + build_time()
            self.add_config("WITH_BUILD_TIME")
        setattr(self.submodules, name, Identifier(identifier))
            

    # Add UART -------------------------------------------------------------------------------------
    def add_uart(self, name, baudrate=115200, fifo_depth=16):
        from litex.soc.cores import uart
        self.check_if_exists("uart")

        # Stub / Stream.
        if name in ["stub", "stream"]:
            self.submodules.uart = uart.UART(tx_fifo_depth=0, rx_fifo_depth=0)
            if name == "stub":
                self.comb += self.uart.sink.ready.eq(1)

        # UARTBone / Bridge.
        elif name in ["uartbone", "bridge"]:
            self.add_uartbone(baudrate=baudrate)

        # Crossover.
        elif name in ["crossover"]:
            self.submodules.uart = uart.UARTCrossover(
                tx_fifo_depth = fifo_depth,
                rx_fifo_depth = fifo_depth)

        # Crossover + Bridge.
        elif name in ["crossover+bridge"]:
            self.add_uartbone(baudrate=baudrate)
            self.submodules.uart = uart.UARTCrossover(
                tx_fifo_depth = fifo_depth,
                rx_fifo_depth = fifo_depth)

        # Model/Sim.
        elif name in ["model", "sim"]:
            self.submodules.uart_phy = uart.RS232PHYModel(self.platform.request("serial"))
            self.submodules.uart = uart.UART(self.uart_phy,
                tx_fifo_depth = fifo_depth,
                rx_fifo_depth = fifo_depth)

        # JTAG Atlantic.
        elif name in ["jtag_atlantic"]:
            from litex.soc.cores.jtag import JTAGAtlantic
            self.submodules.uart_phy = JTAGAtlantic()
            self.submodules.uart = uart.UART(self.uart_phy,
                tx_fifo_depth = fifo_depth,
                rx_fifo_depth = fifo_depth)

        # JTAG UART.
        elif name in ["jtag_uart"]:
            from litex.soc.cores.jtag import JTAGPHY
            self.clock_domains.cd_sys_jtag = ClockDomain()          # Run JTAG-UART in sys_jtag clock domain similar to
            self.comb += self.cd_sys_jtag.clk.eq(ClockSignal("sys")) # sys clock domain but with rst disconnected.
            self.submodules.uart_phy = JTAGPHY(device=self.platform.device, clock_domain="sys_jtag")
            self.submodules.uart = uart.UART(self.uart_phy,
                tx_fifo_depth = fifo_depth,
                rx_fifo_depth = fifo_depth)

        # USB ACM (with ValentyUSB core).
        elif name in ["usb_acm"]:
            import valentyusb.usbcore.io as usbio
            import valentyusb.usbcore.cpu.cdc_eptri as cdc_eptri
            usb_pads = self.platform.request("usb")
            usb_iobuf = usbio.IoBuf(usb_pads.d_p, usb_pads.d_n, usb_pads.pullup)
            self.clock_domains.cd_sys_usb = ClockDomain()           # Run USB ACM in sys_usb clock domain similar to
            self.comb += self.cd_sys_usb.clk.eq(ClockSignal("sys")) # sys clock domain but with rst disconnected.
            self.submodules.uart = ClockDomainsRenamer("sys_usb")(cdc_eptri.CDCUsb(usb_iobuf))

        # Classical UART.
        else:
            self.submodules.uart_phy = uart.UARTPHY(
                pads     = self.platform.request(name),
                clk_freq = self.sys_clk_freq,
                baudrate = baudrate)
            self.submodules.uart = uart.UART(self.uart_phy,
                tx_fifo_depth = fifo_depth,
                rx_fifo_depth = fifo_depth)

        if self.irq.enabled:
            self.irq.add("uart", use_loc_if_exists=True)
        else:
            self.add_constant("UART_POLLING")

    # Add UARTbone ---------------------------------------------------------------------------------
    def add_uartbone(self, name="serial", clk_freq=None, baudrate=115200, cd="sys"):
        from litex.soc.cores import uart
        if clk_freq is None:
            clk_freq = self.sys_clk_freq
        self.check_if_exists("uartbone")
        self.submodules.uartbone_phy = uart.UARTPHY(self.platform.request(name), clk_freq, baudrate)
        self.submodules.uartbone = uart.UARTBone(phy=self.uartbone_phy, clk_freq=clk_freq, cd=cd)
        self.bus.add_master(name="uartbone", master=self.uartbone.wishbone)

    # Add JTAGbone ---------------------------------------------------------------------------------
    def add_jtagbone(self, chain=1):
        from litex.soc.cores import uart
        from litex.soc.cores.jtag import JTAGPHY
        self.check_if_exists("jtagbone")
        self.submodules.jtagbone_phy = JTAGPHY(device=self.platform.device, chain=chain)
        self.submodules.jtagbone = uart.UARTBone(phy=self.jtagbone_phy, clk_freq=self.sys_clk_freq)
        self.bus.add_master(name="jtagbone", master=self.jtagbone.wishbone)

            
            

    # SoC finalization -----------------------------------------------------------------------------
    def do_finalize(self):
        interconnect_p2p_cls = {
            "wishbone": wishbone.InterconnectPointToPoint,
            "axi-lite": axi.AXILiteInterconnectPointToPoint,
        }[self.bus.standard]
        interconnect_shared_cls = {
            "wishbone": wishbone.InterconnectShared,
            "axi-lite": axi.AXILiteInterconnectShared,
        }[self.bus.standard]

        # SoC Reset --------------------------------------------------------------------------------
        # Connect soc_rst to CRG's rst if presents.
        if hasattr(self, "ctrl") and hasattr(self, "crg"):
            crg_rst = getattr(self.crg, "rst", None)
            if isinstance(crg_rst, Signal):
                self.comb += crg_rst.eq(getattr(self.ctrl, "soc_rst", 0))

        # SoC CSR bridge ---------------------------------------------------------------------------
        # FIXME: for now, use registered CSR bridge when SDRAM is present; find the best compromise.
        self.add_csr_bridge(self.mem_map["csr"], register=hasattr(self, "sdram"))

        # SoC Bus Interconnect ---------------------------------------------------------------------
        if len(self.bus.masters) and len(self.bus.slaves):
            # If 1 bus_master, 1 bus_slave and no address translation, use InterconnectPointToPoint.
            if ((len(self.bus.masters) == 1)  and
                (len(self.bus.slaves)  == 1)  and
                (next(iter(self.bus.regions.values())).origin == 0)):
                self.submodules.bus_interconnect = interconnect_p2p_cls(
                    master = next(iter(self.bus.masters.values())),
                    slave  = next(iter(self.bus.slaves.values())))
            # Otherwise, use InterconnectShared.
            else:
                self.submodules.bus_interconnect = interconnect_shared_cls(
                    masters        = list(self.bus.masters.values()),
                    slaves         = [(self.bus.regions[n].decoder(self.bus), s) for n, s in self.bus.slaves.items()],
                    register       = True,
                    timeout_cycles = self.bus.timeout)
                if hasattr(self, "ctrl") and self.bus.timeout is not None:
                    if hasattr(self.ctrl, "bus_error"):
                        self.comb += self.ctrl.bus_error.eq(self.bus_interconnect.timeout.error)
            self.bus.logger.info("Interconnect: {} ({} <-> {}).".format(
                colorer(self.bus_interconnect.__class__.__name__),
                colorer(len(self.bus.masters)),
                colorer(len(self.bus.slaves))))
        self.add_constant("CONFIG_BUS_STANDARD",      self.bus.standard.upper())
        self.add_constant("CONFIG_BUS_DATA_WIDTH",    self.bus.data_width)
        self.add_constant("CONFIG_BUS_ADDRESS_WIDTH", self.bus.address_width)

        # SoC DMA Bus Interconnect (Cache Coherence) -----------------------------------------------
        if hasattr(self, "dma_bus"):
            if len(self.dma_bus.masters) and len(self.dma_bus.slaves):
                # If 1 bus_master, 1 bus_slave and no address translation, use InterconnectPointToPoint.
                if ((len(self.dma_bus.masters) == 1)  and
                    (len(self.dma_bus.slaves)  == 1)  and
                    (next(iter(self.dma_bus.regions.values())).origin == 0)):
                    self.submodules.dma_bus_interconnect = wishbone.InterconnectPointToPoint(
                        master = next(iter(self.dma_bus.masters.values())),
                        slave  = next(iter(self.dma_bus.slaves.values())))
                # Otherwise, use InterconnectShared.
                else:
                    self.submodules.dma_bus_interconnect = wishbone.InterconnectShared(
                        masters        = list(self.dma_bus.masters.values()),
                        slaves         = [(self.dma_bus.regions[n].decoder(self.dma_bus), s) for n, s in self.dma_bus.slaves.items()],
                        register       = True)
                self.bus.logger.info("DMA Interconnect: {} ({} <-> {}).".format(
                    colorer(self.dma_bus_interconnect.__class__.__name__),
                    colorer(len(self.dma_bus.masters)),
                    colorer(len(self.dma_bus.slaves))))
            self.add_constant("CONFIG_CPU_HAS_DMA_BUS")

        # SoC CSR Interconnect ---------------------------------------------------------------------
        self.submodules.csr_bankarray = csr_bus.CSRBankArray(self,
            address_map        = self.csr.address_map,
            data_width         = self.csr.data_width,
            address_width      = self.csr.address_width,
            alignment          = self.csr.alignment,
            paging             = self.csr.paging,
            ordering           = self.csr.ordering,
            soc_bus_data_width = self.bus.data_width)
        if len(self.csr.masters):
            self.submodules.csr_interconnect = csr_bus.InterconnectShared(
                masters = list(self.csr.masters.values()),
                slaves  = self.csr_bankarray.get_buses())

        # Add CSRs regions.
        for name, csrs, mapaddr, rmap in self.csr_bankarray.banks:
            self.csr.add_region(name, SoCCSRRegion(
                origin   = (self.bus.regions["csr"].origin + self.csr.paging*mapaddr),
                busword  = self.csr.data_width,
                obj      = csrs))

        # Add Memory regions.
        for name, memory, mapaddr, mmap in self.csr_bankarray.srams:
            self.csr.add_region(name + "_" + memory.name_override, SoCCSRRegion(
                origin  = (self.bus.regions["csr"].origin + self.csr.paging*mapaddr),
                busword = self.csr.data_width,
                obj     = memory))

        # Sort CSR regions by origin.
        self.csr.regions = {k: v for k, v in sorted(self.csr.regions.items(), key=lambda item: item[1].origin)}

        # Add CSRs / Config items to constants.
        for name, constant in self.csr_bankarray.constants:
            self.add_constant(name + "_" + constant.name, constant.value.value)

        # SoC CPU Check ----------------------------------------------------------------------------
        if not isinstance(self.cpu, (cpu.CPUNone, cpu.EOS_S3)):
            cpu_reset_address_valid = False
            for name, container in self.bus.regions.items():
                if self.bus.check_region_is_in(
                    region    = SoCRegion(origin=self.cpu.reset_address, size=self.bus.data_width//8),
                    container = container):
                    cpu_reset_address_valid = True
                    if name == "rom":
                        self.cpu.use_rom = True
            if not cpu_reset_address_valid:
                self.logger.error("CPU needs {} to be in a {} Region.".format(
                    colorer("reset address 0x{:08x}".format(self.cpu.reset_address)),
                    colorer("defined", color="red")))
                self.logger.error(self.bus)
                raise SoCError()

        # SoC IRQ Interconnect ---------------------------------------------------------------------
        if hasattr(self, "cpu") and hasattr(self.cpu, "interrupt"):
            for name, loc in sorted(self.irq.locs.items()):
                if name in self.cpu.interrupts.keys():
                    continue
                if hasattr(self, name):
                    module = getattr(self, name)
                    ev = None
                    if hasattr(module, "ev"):
                        ev = module.ev
                    elif isinstance(module, EventManager):
                        ev = module
                    else:
                        self.logger.error("EventManager {} in {} SubModule.".format(
                            colorer("not found", color="red"),
                            colorer(name)))
                        raise SoCError()
                    self.comb += self.cpu.interrupt[loc].eq(ev.irq)
                self.add_constant(name + "_INTERRUPT", loc)


# Platform

class Platform(AlteraPlatform):
	default_clk_name = "clk50"
	default_clk_period = 1e9/50e6
	create_rbf = False
	
def __init__(self):
	AlteraPlatform.__init__(self, "10M50DAF484C7G", _io)

# Create our platform (fpga interface)

platform = Platform()

class AMP():

	def __init__(self, platform, sys_clk_freq,
		csr_map       = {},
		interrupt_map = {},
		mem_map       = {
				"rom":      0x00000000,
				"sram":     0x01000000,
				"main_ram": 0x40000000,
		 	},

		# Bus parameters
		bus_standard             = "wishbone",
		bus_data_width           = 32,
		bus_address_width        = 32,
		bus_timeout              = 1e6,
		bus_reserved_regions	 = {},

		# CPU parameters
		cpu_type                 = "vexriscv",
		cpu_reset_address        = None,
		cpu_variant              = None,
		cpu_cls                  = None,
		cpu_cfu                  = None,

		# CFU parameters
		cfu_filename             = None,

		# ROM parameters
		integrated_rom_size      = 0,
		integrated_rom_mode      = "r",
		integrated_rom_init      = [],

		# SRAM parameters
		integrated_sram_size     = 0x2000,
		integrated_sram_init     = [],

		# MAIN_RAM parameters
		integrated_main_ram_size = 0,
		integrated_main_ram_init = [],

		# CSR parameters
		csr_data_width           = 32,
		csr_address_width        = 14,
		csr_paging               = 0x800,
		csr_ordering             = "big",

		# Interrupt parameters
		irq_n_irqs               = 32,

		# Identifier parameters
		ident                    = "",
		ident_version            = False,

		# UART parameters
		with_uart                = True,
		uart_name                = "serial",
		uart_baudrate            = 115200,
		uart_fifo_depth          = 16,

		# Timer parameters
		with_timer               = True,
		timer_uptime             = False,

		# Controller parameters
		with_ctrl                = True,

		irq_reserved_irqs    = {},
			
		# Others
		**kwargs):
        
		self.platform = platform
		self.sys_clk_freq = sys_clk_freq

		core0 = CPUBlock(self.platform, self.sys_clk_freq)
			
		
		core1 = CPUBlock(self.platform, self.sys_clk_freq)
		
		# Memory regions for CPU 0
		# ROM parameters
		core0.integrated_rom_size      = 0x2000
		core0.integrated_rom_mode      = "r"
		core0.integrated_rom_init      = 0x0000

		# SRAM parameters
		core0.integrated_sram_size     = 0x1000
		core0.integrated_sram_init     = 0x3000

		# MAIN_RAM parameters
		core0.integrated_main_ram_size = 0x1000
		core0.integrated_main_ram_init = 0x9000
		
		# Memory regions for CPU 1
		
			# ROM parameters
		core1.integrated_rom_size      = 0x2000
		core1.integrated_rom_mode      = "r"
		core1.integrated_rom_init      = 0x16000

		# SRAM parameters
		core1.integrated_sram_size     = 0x1000
		core1.integrated_sram_init     = 0x18000

		# MAIN_RAM parameters
		core1.integrated_main_ram_size = 0x1000
		core1.integrated_main_ram_init = 0x19000
		
		core0.mem_regions = core0.bus.regions
		core0.clk_freq    = core0.sys_clk_freq
		core0.config      = {}	
		core0.wb_slaves = {}
		
		core1.mem_regions = Core1.bus.regions
		core1.clk_freq    = Core1.sys_clk_freq
		core1.config      = {}	
		core1.wb_slaves = {}
		
		core0.mem_map       = {
		"rom":      0x00000000,
		"sram":     0x00000000,
		"main_ram": 0x10000000,
		}
		
		core1.mem_map       = {
		"rom":      0x00000000,
		"sram":     0x00000000,
		"main_ram": 0x00000000,
		}
		
		ident                    = ""
		ident_version            = False

		# Modules instances ------------------------------------------------------------------------
		
		
		# Add SoCController
		core0.add_controller("ctrl0")
		
		core0.add_cpu(
			name          = "vexriscv",
			variant       = "standard",
			reset_address = None,
			cls           = None,
			cfu           = None)
		    
		core0.add_rom("rom_core0",
			origin   = core0.cpu.reset_address,
			size     = core0.integrated_rom_size,
			contents = core0.integrated_rom_init,
			mode     = core0.integrated_rom_mode)
		    
		core0.add_ram("sram_core0",
			origin = core0.mem_map["sram"],
			size   = core0.integrated_sram_size)
		    
		core0.add_ram("main_ram_core0",
			origin = core0.mem_map["main_ram"],
			size   = core0.integrated_main_ram_size,
			contents = core0.integrated_main_ram_init)
		
		core0.uart_name                = "serial"
		core0.uart_baudrate            = 115200
		core0.uart_fifo_depth          = 16
		
		core0.add_identifier("identifier", identifier=ident, with_build_time=ident_version)
		core0.add_uart(name=core0.uart_name, baudrate=core0.uart_baudrate, fifo_depth=core0.uart_fifo_depth) #or add as a submodule?
		uart_tx_core0 = platform.request("uart_tx")
		uart_rx_core0 = platform.request("uart_rx")
		core0.add_timer(name="timer0")
		    
		    
		#Core 1 main components
		
		core1.add_controller("ctrl1")
		
		core1.add_cpu(
			name          = "vexriscv",
			variant       = "standard",
			reset_address = None,
			cls           = None,
			cfu           = None)
		    
		core1.add_rom("rom_core1",
			origin   = Core1.cpu.reset_address,
			size     = Core1.integrated_rom_size,
			contents = Core1.integrated_rom_init,
			mode     = Core1.integrated_rom_mode)
		    
		core1.add_ram("sram_core1",
			origin = Core1.mem_map["sram"],
			size   = Core1.integrated_sram_size)
		    
		core1.add_ram("main_ram_core1",
			origin = Core1.mem_map["main_ram"],
			size   = Core1.integrated_main_ram_size,
			contents = Core1.integrated_main_ram_init)
		
		core1.uart_name                = "serial"
		core1.uart_baudrate            = 115200
		core1.uart_fifo_depth          = 16
		
		core1.add_identifier("identifier", identifier=ident, with_build_time=ident_version)
		#Core1.add_uart(name=Core1.uart_name, baudrate=Core1.uart_baudrate, fifo_depth=Core1.uart_fifo_depth) as submodule?
		core1.add_timer(name="timer1")
		
		
		self.comb += [
		# UART connection
	    	#Core0.uart_tx_core0.eq(Core1.uart_rx_core1),
		#Core0.uart_rx_core0.eq(Core1.uart_tx_core1)
        ]

module = AMP()
platform.build(module)
# Build --------------------------------------------------------------------------------------------

#builder = Builder(soc, output_dir="build", csr_csv="test/csr.csv")
#builder.build(build_name="top")
