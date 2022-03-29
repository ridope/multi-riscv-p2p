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


# Platform

class Platform(AlteraPlatform):
	default_clk_name = "clk50"
	default_clk_period = 1e9/50e6
	create_rbf = False
	
	def __init__(self):
        	AlteraPlatform.__init__(self, "10M50DAF484C7G", _io)
        	
# Design -------------------------------------------------------------------------------------------


class CPUBase(Module):
	mem_map = {}
    
	def __init__(self, platform, sys_clk_freq,
		bus_standard         = "wishbone",
		bus_data_width       = 32,
		bus_address_width    = 32,
		bus_timeout          = 1e6,
		bus_reserved_regions = {},

		csr_data_width       = 32,
		csr_address_width    = 14,
		csr_paging           = 0x800,
		csr_ordering         = "big",
		csr_reserved_csrs    = {},

		irq_n_irqs           = 32,
		irq_reserved_irqs    = {},
		):
		
		self.logger = logging.getLogger("SoC")
    
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

	 # SoC Bus Handler-------------------------------------------------------------------------
		self.submodules.csr = SoCCSRHandler(
		    data_width    = csr_data_width,
		    address_width = csr_address_width,
		    alignment     = 32,
		    paging        = csr_paging,
		    ordering      = csr_ordering,
		    reserved_csrs = csr_reserved_csrs,
		)
		# SoC IRQ Handler --------------------------------------------------------------------------
		self.submodules.irq = SoCIRQHandler(
		    n_irqs        = irq_n_irqs,
		    reserved_irqs = irq_reserved_irqs
		)
		
		self.add_config("CLOCK_FREQUENCY", int(sys_clk_freq))
    
    # SoC Helpers ----------------------------------------------------------------------------------
    def check_if_exists(self, name):
    	if hasattr(self, name):
            self.logger.error("{} SubModule already {}.".format(
                colorer(name),
                colorer("declared", color="red")))
            raise SoCError()

    def add_constant(self, name, value=None, check_duplicate=True):
        name = name.upper()
        if name in self.constants.keys():
            if check_duplicate:
                self.logger.error("{} Constant already {}.".format(
                    colorer(name),
                    colorer("declared", color="red")))
                raise SoCError()
        self.constants[name] = SoCConstant(value)

    def add_config(self, name, value=None, check_duplicate=True):
        name = "CONFIG_" + name
        if isinstance(value, str):
            self.add_constant(name + "_" + value, check_duplicate=check_duplicate)
        else:
            self.add_constant(name, value, check_duplicate=check_duplicate)

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
        self.logger.info("Controller {} {}.".format(
            colorer(name, color="underline"),
            colorer("added", color="green")))
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
        if contents != []:
            self.add_config(f"{name}_INIT", 1)
    
    def add_csr_bridge(self, name="csr", origin=None, register=False):
        csr_bridge_cls = {
            "wishbone": wishbone.Wishbone2CSR,
            "axi-lite": axi.AXILite2CSR,
        }[self.bus.standard]
        csr_bridge_name = name + "_bridge"
        self.check_if_exists(csr_bridge_name )
        csr_bridge = csr_bridge_cls(
            bus_csr = csr_bus.Interface(
                address_width = self.csr.address_width,
                data_width    = self.csr.data_width),
            register = register)
        self.logger.info("CSR Bridge {} {}.".format(
            colorer(name, color="underline"),
            colorer("added", color="green")))
        setattr(self.submodules, csr_bridge_name, csr_bridge)
        csr_size = 2**(self.csr.address_width + 2)
        csr_region = SoCRegion(origin=origin, size=csr_size, cached=False, decode=self.cpu.csr_decode)
        bus = getattr(self.csr_bridge, self.bus.standard.replace('-', '_'))
        self.bus.add_slave(name=name, slave=bus, region=csr_region)
        self.csr.add_master(name=name, master=self.csr_bridge.csr)
        self.add_config("CSR_DATA_WIDTH", self.csr.data_width)
        self.add_config("CSR_ALIGNMENT",  self.csr.alignment)
        
	def add_cpu(self, name="vexriscv", variant="standard", reset_address=None, cfu=None):
        # Check that CPU is supported.
        if name not in cpu.CPUS.keys():
            self.logger.error("{} CPU {}, supported are: {}.".format(
                colorer(name),
                colorer("not supported", color="red"),
                colorer(", ".join(cpu.CPUS.keys()))))
            raise SoCError()

        # Add CPU.
        cpu_cls = cpu.CPUS[name]
        if (variant not in cpu_cls.variants) and (cpu_cls is not cpu.CPUNone):
            self.logger.error("{} CPU variant {}, supported are: {}.".format(
                colorer(variant),
                colorer("not supported", color="red"),
                colorer(", ".join(cpu_cls.variants))))
            raise SoCError()
        self.check_if_exists("cpu")
        self.submodules.cpu = cpu_cls(self.platform, variant)
        self.logger.info("CPU {} {}.".format(
            colorer(name, color="underline"),
            colorer("added", color="green")))  
    
        # Update SoC with CPU constraints.
        # IO regions.
        for n, (origin, size) in enumerate(self.cpu.io_regions.items()):
            self.logger.info("CPU {} {} IO Region {} at {} (Size: {}).".format(
                colorer(name, color="underline"),
                colorer("adding", color="cyan"),
                colorer(n),
                colorer(f"0x{origin:08x}"),
                colorer(f"0x{size:08x}")))
            self.bus.add_region("io{}".format(n), SoCIORegion(origin=origin, size=size, cached=False))
        # Mapping.
        if isinstance(self.cpu, cpu.CPUNone):
            # With CPUNone, give priority to User's mapping.
            self.mem_map = {**self.cpu.mem_map, **self.mem_map}
            # With CPUNone, disable IO regions check.
            self.bus.io_regions_check = False
        else:
            # Override User's mapping with CPU constrainted mapping (and warn User).
            for n, origin in self.cpu.mem_map.items():
                if n in self.mem_map.keys() and self.mem_map[n] != self.cpu.mem_map[n]:
                    self.logger.info("CPU {} {} {} mapping from {} to {}.".format(
                        colorer(name, color="underline"),
                        colorer("overriding", color="cyan"),
                        colorer(n),
                        colorer(f"0x{self.mem_map[n]:08x}"),
                        colorer(f"0x{self.cpu.mem_map[n]:08x}")))
            self.mem_map.update(self.cpu.mem_map)
            
                    # Interrupts
            if hasattr(self.cpu, "interrupt"):
                self.logger.info("CPU {} {} Interrupt(s).".format(
                    colorer(name, color="underline"),
                    colorer("adding", color="cyan")))
                self.irq.enable()
                for name, loc in self.cpu.interrupts.items():
                    self.irq.add(name, loc)
                self.add_config("CPU_HAS_INTERRUPT")
                
	 def add_timer(self, name="timer0"):
        from litex.soc.cores.timer import Timer
        self.check_if_exists(name)
        setattr(self.submodules, name, Timer())
        if self.irq.enabled:
            self.irq.add(name, use_loc_if_exists=True)
            
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
                self.comb += If(getattr(self.ctrl, "soc_rst", 0), crg_rst.eq(1))

        # SoC CSR bridge ---------------------------------------------------------------------------
        # FIXME: for now, use registered CSR bridge when SDRAM is present; find the best compromise.
        self.add_csr_bridge(
            name     = "csr",
            origin   = self.mem_map["csr"],
            register = hasattr(self, "sdram")
        )

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
        if not isinstance(self.cpu, cpu.CPUNone):
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

        # SoC Infos --------------------------------------------------------------------------------
        self.logger.info(colorer("-"*80, color="bright"))
        self.logger.info(colorer("Finalized SoC:"))
        self.logger.info(colorer("-"*80, color="bright"))
        self.logger.info(self.bus)
        if hasattr(self, "dma_bus"):
            self.logger.info(self.dma_bus)
        self.logger.info(self.csr)
        self.logger.info(self.irq)
        self.logger.info(colorer("-"*80, color="bright"))

    # SoC build ------------------------------------------------------------------------------------
    def build(self, *args, **kwargs):
        self.build_name = kwargs.pop("build_name", self.platform.name)
        if self.build_name[0].isdigit():
            self.build_name = f"_{self.build_name}"
        kwargs.update({"build_name": self.build_name})
        return self.platform.build(self, *args, **kwargs)
        
   # Add UART -------------------------------------------------------------------------------------
    def add_uart(self, name="uart", uart_name="serial", baudrate=115200, fifo_depth=16):
        # Imports.
        from litex.soc.cores.uart import UART, UARTCrossover

        # Core.
        self.check_if_exists(name)
        supported_uarts = [
            "crossover",
            "crossover+uartbone",
            "jtag_uart",
            "sim",
            "stub",
            "stream",
            "uartbone",
            "usb_acm",
            "serial(x)",
        ]
        uart_pads_name = "serial" if uart_name == "sim" else uart_name
        uart_pads      = self.platform.request(uart_pads_name, loose=True)
        uart_phy       = None
        uart           = None
        uart_kwargs    = {
            "tx_fifo_depth": fifo_depth,
            "rx_fifo_depth": fifo_depth,
        }
        if (uart_pads is None) and (uart_name not in supported_uarts):
            self.logger.error("{} UART {}, supported are: {}.".format(
                colorer(uart_name),
                colorer("not supported/found on board", color="red"),
                colorer(", ".join(supported_uarts))))
            raise SoCError()

        # Crossover.
        if uart_name in ["crossover"]:
            uart = UARTCrossover(**uart_kwargs)

        # Crossover + UARTBone.
        elif uart_name in ["crossover+uartbone"]:
            self.add_uartbone(baudrate=baudrate)
            uart = UARTCrossover(**uart_kwargs)

        # JTAG UART.
        elif uart_name in ["jtag_uart"]:
            from litex.soc.cores.jtag import JTAGPHY
            # Run JTAG-UART in sys_jtag clk domain similar to sys clk domain but without sys_rst.
            self.clock_domains.cd_sys_jtag = ClockDomain()
            self.comb += self.cd_sys_jtag.clk.eq(ClockSignal("sys"))
            uart_phy = JTAGPHY(device=self.platform.device, clock_domain="sys_jtag", platform=self.platform)
            uart     = UART(uart_phy, **uart_kwargs)

        # Sim.
        elif uart_name in ["sim"]:
            from litex.soc.cores.uart import RS232PHYModel
            uart_phy = RS232PHYModel(uart_pads)
            uart     = UART(uart_phy, **uart_kwargs)

        # Stub / Stream.
        elif uart_name in ["stub", "stream"]:
            uart = UART(tx_fifo_depth=0, rx_fifo_depth=0)
            self.comb += uart.sink.ready.eq(uart_name == "stub")

        # UARTBone.
        elif uart_name in ["uartbone"]:
            self.add_uartbone(baudrate=baudrate)

        # USB ACM (with ValentyUSB core).
        elif uart_name in ["usb_acm"]:
            import valentyusb.usbcore.io as usbio
            import valentyusb.usbcore.cpu.cdc_eptri as cdc_eptri
            usb_pads  = self.platform.request("usb")
            usb_iobuf = usbio.IoBuf(usb_pads.d_p, usb_pads.d_n, usb_pads.pullup)
            # Run USB-ACM in sys_usb clock domain similar to sys_clk domain but without sys_rst.
            self.clock_domains.cd_sys_usb = ClockDomain()
            self.comb += self.cd_sys_usb.clk.eq(ClockSignal("sys"))
            uart = ClockDomainsRenamer("sys_usb")(cdc_eptri.CDCUsb(usb_iobuf))

        # Regular UART.
        else:
            from litex.soc.cores.uart import UARTPHY
            uart_phy  = UARTPHY(uart_pads, clk_freq=self.sys_clk_freq, baudrate=baudrate)
            uart      = UART(uart_phy, **uart_kwargs)

        # Add PHY/UART.
        if uart_phy is not None:
            setattr(self.submodules, name + "_phy", uart_phy)
        if uart is not None:
            setattr(self.submodules, name, uart)

        # IRQ.
        if self.irq.enabled:
            self.irq.add(name, use_loc_if_exists=True)
        else:
            self.add_constant("UART_POLLING")

    # Add UARTbone ---------------------------------------------------------------------------------
    def add_uartbone(self, name="serial", clk_freq=None, baudrate=115200, cd="sys"):
        # Imports.
        from litex.soc.cores import uart

        # Core.
        if clk_freq is None:
            clk_freq = self.sys_clk_freq
        self.check_if_exists("uartbone")
        self.submodules.uartbone_phy = uart.UARTPHY(self.platform.request(name), clk_freq, baudrate)
        self.submodules.uartbone = uart.UARTBone(phy=self.uartbone_phy, clk_freq=clk_freq, cd=cd)
        self.bus.add_master(name="uartbone", master=self.uartbone.wishbone)

    # Add JTAGbone ---------------------------------------------------------------------------------
    def add_jtagbone(self, name="jtagbone", chain=1):
        # Imports.
        from litex.soc.cores import uart
        from litex.soc.cores.jtag import JTAGPHY

        # Core.
        self.check_if_exists(name)
        jtagbone_phy = JTAGPHY(device=self.platform.device, chain=chain, platform=self.platform)
        jtagbone = uart.UARTBone(phy=jtagbone_phy, clk_freq=self.sys_clk_freq)
        setattr(self.submodules, f"{name}_phy", jtagbone_phy)
        setattr(self.submodules,          name, jtagbone)
        self.bus.add_master(name=name, master=jtagbone.wishbone)
     

class CPUBlock(CPUBase):

    # Default register/interrupt/memory mappings (can be redefined by user)
    csr_map       = {}
    interrupt_map = {}
    mem_map       = {
        "sram":     0x00000000,
        "main_ram": 0x40000000,
    }
	def __init__(self, platform, clk_freq,
        # Bus parameters
        bus_standard             = "wishbone",
        bus_data_width           = 32,
        bus_address_width        = 32,
        bus_timeout              = 1e6,

        # CPU parameters
        cpu_type                 = "vexriscv",
        cpu_reset_address        = None,
        cpu_variant              = None,
        cpu_cfu                  = None,
        
        #Others
        clk_freq                 = 50e6,
        ident                    = "LiteX CPU Test SoC", ident_version=True,
        integrated_main_ram_size = 0x4000,

        # CFU parameters
        cfu_filename             = None,

        # SRAM parameters
        integrated_sram_size     = 0x1000,
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

        # Others
        **kwargs):

        # New CPUBase class ----------------------------------------------------------------------------
        CPUBase.__init__(self, platform, clk_freq,
            bus_standard         = bus_standard,
            bus_data_width       = bus_data_width,
            bus_address_width    = bus_address_width,
            bus_timeout          = bus_timeout,
            bus_reserved_regions = {},

            csr_data_width       = csr_data_width,
            csr_address_width    = csr_address_width,
            csr_paging           = csr_paging,
            csr_ordering         = csr_ordering,
            csr_reserved_csrs    = self.csr_map,

            irq_n_irqs           = irq_n_irqs,
            irq_reserved_irqs    = {},
        )

        # Attributes
        self.mem_regions = self.bus.regions
        self.clk_freq    = self.sys_clk_freq
        self.mem_map     = self.mem_map
        self.config      = {}

        # Parameters management --------------------------------------------------------------------

        # CPU.
        cpu_type          = None if cpu_type == "None" else cpu_type
        cpu_reset_address = None if cpu_reset_address == "None" else cpu_reset_address

        self.cpu_type     = cpu_type
        self.cpu_variant  = cpu_variant

        # SRAM.
        self.integrated_sram_size = integrated_sram_size

        # MAIN RAM.
        self.integrated_main_ram_size = integrated_main_ram_size

        # CSRs.
        self.csr_data_width = csr_data_width

        # Wishbone Slaves.
        self.wb_slaves = {}

        # Modules instances ------------------------------------------------------------------------

        # Add SoCController
        if with_ctrl:
            self.add_controller("ctrl")

        # Add CPU
        self.add_cpu(
            name          = str(cpu_type),
            variant       = "standard" if cpu_variant is None else cpu_variant,
            reset_address = None if integrated_rom_size else cpu_reset_address,
            cfu           = cpu_cfu)

        # Add User's interrupts
        if self.irq.enabled:
            for name, loc in self.interrupt_map.items():
                self.irq.add(name, loc)

        # Add integrated SRAM
        if integrated_sram_size:
            self.add_ram("sram",
                origin = self.mem_map["sram"],
                size   = integrated_sram_size,
            )

        # Add integrated MAIN_RAM (only useful when no external SRAM/SDRAM is available)
        if integrated_main_ram_size:
            self.add_ram("main_ram",
                origin   = self.mem_map["main_ram"],
                size     = integrated_main_ram_size,
                contents = integrated_main_ram_init,
            )

        # Add Identifier
        if ident != "":
            self.add_identifier("identifier", identifier=ident, with_build_time=ident_version)

        # Add UART
        if with_uart:
            self.add_uart(name="uart", uart_name=uart_name, baudrate=uart_baudrate, fifo_depth=uart_fifo_depth)

        # Add Timer
        if with_timer:
            self.add_timer(name="timer0")
            if timer_uptime:
                self.timer0.add_uptime()
                
        # Connect UART (pending)

    # Methods --------------------------------------------------------------------------------------

    def add_interrupt(self, interrupt_name, interrupt_id=None, use_loc_if_exists=False):
        self.irq.add(interrupt_name, interrupt_id, use_loc_if_exists=use_loc_if_exists)

    def add_csr(self, csr_name, csr_id=None, use_loc_if_exists=False):
        self.csr.add(csr_name, csr_id, use_loc_if_exists=use_loc_if_exists)

    def initialize_rom(self, data):
        self.init_rom(name="rom", contents=data)

    def add_wb_master(self, wbm):
        self.bus.add_master(master=wbm)

    def add_wb_slave(self, address, interface, size=None):
        wb_name = None
        for name, region in self.bus.regions.items():
            if address == region.origin:
                wb_name = name
                break
        if wb_name is None:
            self.wb_slaves[address] = interface
        else:
            self.bus.add_slave(name=wb_name, slave=interface)

    def add_memory_region(self, name, origin, length, type="cached"):
        self.bus.add_region(name, SoCRegion(origin=origin, size=length,
            cached="cached" in type,
            linker="linker" in type))

    def register_mem(self, name, address, interface, size=0x10000000):
        self.bus.add_slave(name, interface, SoCRegion(origin=address, size=size))

    def add_csr_region(self, name, origin, busword, obj):
        self.csr_regions[name] = SoCCSRRegion(origin, busword, obj)

    # Finalization ---------------------------------------------------------------------------------

    def do_finalize(self):
        # Retro-compatibility
        for address, interface in self.wb_slaves.items():
            wb_name = None
            for name, region in self.bus.regions.items():
                if address == region.origin:
                    wb_name = name
                    break
            self.bus.add_slave(name=wb_name, slave=interface)

        SoC.do_finalize(self)
        # Retro-compatibility
        for region in self.bus.regions.values():
            region.length = region.size
            region.type   = "cached" if region.cached else "io"
            if region.linker:
                region.type += "+linker"
        self.csr_regions = self.csr.regions
        for name, value in self.config.items():
            self.add_config(name, value)

# SoCCore arguments --------------------------------------------------------------------------------

def soc_core_args(parser):
    soc_group = parser.add_argument_group(title="SoC options")
    # Bus parameters
    soc_group.add_argument("--bus-standard",      default="wishbone",                help="Select bus standard: {}.".format(", ".join(SoCBusHandler.supported_standard)))
    soc_group.add_argument("--bus-data-width",    default=32,         type=auto_int, help="Bus data-width.")
    soc_group.add_argument("--bus-address-width", default=32,         type=auto_int, help="Bus address-width.")
    soc_group.add_argument("--bus-timeout",       default=int(1e6),   type=float,    help="Bus timeout in cycles.")

    # CPU parameters
    soc_group.add_argument("--cpu-type",          default="vexriscv",               help="Select CPU: {}.".format(", ".join(iter(cpu.CPUS.keys()))))
    soc_group.add_argument("--cpu-variant",       default=None,                     help="CPU variant.")
    soc_group.add_argument("--cpu-reset-address", default=None,      type=auto_int, help="CPU reset address (Boot from Integrated ROM by default).")
    soc_group.add_argument("--cpu-cfu",           default=None,                     help="Optional CPU CFU file/instance to add to the CPU.")

    # Controller parameters
    soc_group.add_argument("--no-ctrl", action="store_true", help="Disable Controller.")

    # SRAM parameters
    soc_group.add_argument("--integrated-sram-size", default=0x2000, type=auto_int, help="Size/Enable the integrated SRAM.")

    # MAIN_RAM parameters
    soc_group.add_argument("--integrated-main-ram-size", default=None, type=auto_int, help="size/enable the integrated main RAM.")

    # CSR parameters
    soc_group.add_argument("--csr-data-width",    default=32  ,  type=auto_int, help="CSR bus data-width (8 or 32).")
    soc_group.add_argument("--csr-address-width", default=14,    type=auto_int, help="CSR bus address-width.")
    soc_group.add_argument("--csr-paging",        default=0x800, type=auto_int, help="CSR bus paging.")
    soc_group.add_argument("--csr-ordering",      default="big",                help="CSR registers ordering (big or little).")

    # Identifier parameters
    soc_group.add_argument("--ident",             default=None,  type=str, help="SoC identifier.")
    soc_group.add_argument("--no-ident-version",  action="store_true",     help="Disable date/time in SoC identifier.")

    # UART parameters
    soc_group.add_argument("--no-uart",         action="store_true",                help="Disable UART.")
    soc_group.add_argument("--uart-name",       default="serial",    type=str,      help="UART type/name.")
    soc_group.add_argument("--uart-baudrate",   default=115200,      type=auto_int, help="UART baudrate.")
    soc_group.add_argument("--uart-fifo-depth", default=16,          type=auto_int, help="UART FIFO depth.")

    # Timer parameters
    soc_group.add_argument("--no-timer",        action="store_true", help="Disable Timer.")
    soc_group.add_argument("--timer-uptime",    action="store_true", help="Add an uptime capability to Timer.")

    # L2 Cache
    soc_group.add_argument("--l2-size", default=8192, type=auto_int, help="L2 cache size.")

def soc_core_argdict(args):
    r = dict()
    # Iterate on all arguments.
    soc_args  = inspect.getfullargspec(SoCCore.__init__).args
    full_args = soc_args + ["l2_size"]
    for a in full_args:
        # Exclude specific arguments.
        if a in ["self", "platform"]:
            continue
        # Handle specific with_xy case (--no_xy is exposed).
        if a in ["with_uart", "with_timer", "with_ctrl"]:
            arg = not getattr(args, a.replace("with", "no"), True)
        # Handle specific ident_version case (--no-ident-version is exposed).
        elif a in ["ident_version"]:
            arg = not getattr(args, "no_ident_version")
        # Regular cases.
        else:
            arg = getattr(args, a, None)
        # Fill Dict.
        if arg is not None:
            r[a] = arg
    return r
    
    
class MySoC():
	Core0 = CPUBlock
	Core1 = CPUBlock #Fix ram regios
	
    #self.comb #UART Connection
    


# Create our platform (fpga interface)
platform = Platform()



soc = MySoC(platform)

# Build --------------------------------------------------------------------------------------------

builder = Builder(soc, output_dir="build", csr_csv="test/csr.csv")
builder.build(build_name="top")



