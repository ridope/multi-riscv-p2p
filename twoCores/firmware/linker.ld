INCLUDE ../build/litex_soc/software/include/generated/output_format.ld
ENTRY(_start)

__DYNAMIC = 0;

INCLUDE ../build/litex_soc/software/include/generated/regions.ld

SECTIONS
{

	.bss :
	{
		. = ALIGN(4);
		_fbss = .;
		*(.dynsbss)
		*(.sbss .sbss.* .gnu.linkonce.sb.*)
		*(.scommon)
		*(.dynbss)
		*(.bss .bss.* .gnu.linkonce.b.*)
		*(COMMON)
		. = ALIGN(4);
		_ebss = .;
		_end = .;
	} > sram
}

PROVIDE(_fstack = ORIGIN(sram) + LENGTH(sram) - 4);

PROVIDE(_fdata_rom = LOADADDR(.data));
PROVIDE(_edata_rom = LOADADDR(.data) + SIZEOF(.data));
