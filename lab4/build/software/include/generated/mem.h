//--------------------------------------------------------------------------------
// Auto-generated by Migen (94db729) & LiteX (3fde2512) on 2022-03-15 18:44:40
//--------------------------------------------------------------------------------
#ifndef __GENERATED_MEM_H
#define __GENERATED_MEM_H

#ifndef ROM_BASE
#define ROM_BASE 0x00000000L
#define ROM_SIZE 0x00008000
#endif

#ifndef SRAM_BASE
#define SRAM_BASE 0x10000000L
#define SRAM_SIZE 0x00002000
#endif

#ifndef MAIN_RAM_BASE
#define MAIN_RAM_BASE 0x40000000L
#define MAIN_RAM_SIZE 0x00004000
#endif

#ifndef CSR_BASE
#define CSR_BASE 0xf0000000L
#define CSR_SIZE 0x00010000
#endif

#ifndef MEM_REGIONS
#define MEM_REGIONS "ROM       0x00000000 0x8000 \nSRAM      0x10000000 0x2000 \nMAIN_RAM  0x40000000 0x4000 \nCSR       0xf0000000 0x10000 "
#endif
#endif