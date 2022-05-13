#!/usr/bin/env python3

from litex.build.altera.programmer import USBBlaster
prog = USBBlaster()
prog.load_bitstream("build/base/gateware/base.sof")

