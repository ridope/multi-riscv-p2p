#!/usr/bin/env python3

from litex import RemoteClient

wb = RemoteClient()
wb.open()

# # #

# get identifier

print("fpga_id: De10-Lite")

# # #

wb.close()
