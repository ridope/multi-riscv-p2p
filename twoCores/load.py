#!/usr/bin/env python3

from litex.build.altera.programmer import USBBlaster
prog = USBBlaster()
prog.load_bitstream("build/gateware/top.sof")
prog.load_bitstream("build2/gateware/top2.sof")

