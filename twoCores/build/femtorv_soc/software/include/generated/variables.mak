PACKAGES=libc libcompiler_rt libbase libfatfs liblitespi liblitedram libliteeth liblitesdcard liblitesata bios
PACKAGE_DIRS=/home/alexandre/litex/litex/soc/software/libc /home/alexandre/litex/litex/soc/software/libcompiler_rt /home/alexandre/litex/litex/soc/software/libbase /home/alexandre/litex/litex/soc/software/libfatfs /home/alexandre/litex/litex/soc/software/liblitespi /home/alexandre/litex/litex/soc/software/liblitedram /home/alexandre/litex/litex/soc/software/libliteeth /home/alexandre/litex/litex/soc/software/liblitesdcard /home/alexandre/litex/litex/soc/software/liblitesata /home/alexandre/litex/litex/soc/software/bios
LIBS=libc libcompiler_rt libbase libfatfs liblitespi liblitedram libliteeth liblitesdcard liblitesata
TRIPLE=riscv64-unknown-elf
CPU=femtorv
CPUFAMILY=riscv
CPUFLAGS=-march=rv32i     -mabi=ilp32 -D__femtorv__ 
CPUENDIANNESS=little
CLANG=0
CPU_DIRECTORY=/home/alexandre/litex/litex/soc/cores/cpu/femtorv
SOC_DIRECTORY=/home/alexandre/litex/litex/soc
PICOLIBC_DIRECTORY=/home/alexandre/pythondata-software-picolibc/pythondata_software_picolibc/data
COMPILER_RT_DIRECTORY=/home/alexandre/pythondata-software-compiler_rt/pythondata_software_compiler_rt/data
export BUILDINC_DIRECTORY
BUILDINC_DIRECTORY=/home/alexandre/multi-riscv-p2p/twoCores/build/femtorv_soc/software/include
LIBC_DIRECTORY=/home/alexandre/litex/litex/soc/software/libc
LIBCOMPILER_RT_DIRECTORY=/home/alexandre/litex/litex/soc/software/libcompiler_rt
LIBBASE_DIRECTORY=/home/alexandre/litex/litex/soc/software/libbase
LIBFATFS_DIRECTORY=/home/alexandre/litex/litex/soc/software/libfatfs
LIBLITESPI_DIRECTORY=/home/alexandre/litex/litex/soc/software/liblitespi
LIBLITEDRAM_DIRECTORY=/home/alexandre/litex/litex/soc/software/liblitedram
LIBLITEETH_DIRECTORY=/home/alexandre/litex/litex/soc/software/libliteeth
LIBLITESDCARD_DIRECTORY=/home/alexandre/litex/litex/soc/software/liblitesdcard
LIBLITESATA_DIRECTORY=/home/alexandre/litex/litex/soc/software/liblitesata
BIOS_DIRECTORY=/home/alexandre/litex/litex/soc/software/bios