//--------------------------------------------------------------------------------
// Auto-generated by Migen (94db729) & LiteX (3fde2512) on 2022-05-10 17:11:51
//--------------------------------------------------------------------------------
#ifndef __GENERATED_MEM_H
#define __GENERATED_MEM_H

#ifndef ROM_BASE
#define ROM_BASE 0x00000000L
#define ROM_SIZE 0x00020000
#endif

#ifndef SRAM_BASE
#define SRAM_BASE 0x10000000L
#define SRAM_SIZE 0x00002000
#endif

#ifndef MMAP_M_BASE
#define MMAP_M_BASE 0xa0000000L
#define MMAP_M_SIZE 0x10000000
#endif

#ifndef CSR_BASE
#define CSR_BASE 0xf0000000L
#define CSR_SIZE 0x00010000
#endif

#ifndef MEM_REGIONS
#define MEM_REGIONS "ROM       0x00000000 0x20000 \nSRAM      0x10000000 0x2000 \nMMAP_M    0xa0000000 0x10000000 \nCSR       0xf0000000 0x10000 "
#endif
#endif