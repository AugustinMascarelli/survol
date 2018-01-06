# import capstone

import pefile
from capstone import *
from capstone.arm import *

def TestHeavy():
	CODE = b"\x55\x48\x8b\x05\xb8\x13\x00\x00"
	md = Cs(CS_ARCH_X86, CS_MODE_64)
	for i in md.disasm(CODE, 0x1000):
		print("0x%x:\t%s\t%s" %(i.address, i.mnemonic, i.op_str))

def TestLight():
	CODE = b"\x55\x48\x8b\x05\xb8\x13\x00\x00"

	md = Cs(CS_ARCH_X86, CS_MODE_64)
	for (address, size, mnemonic, op_str) in md.disasm_lite(CODE, 0x1000):
		print("0x%x:\t%s\t%s" %(address, mnemonic, op_str))

def TestThree():
	CODE = b"\xf1\x02\x03\x0e\x00\x00\xa0\xe3\x02\x30\xc1\xe7\x00\x00\x53\xe3"
	md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
	md.detail = True

	for i in md.disasm(CODE, 0x1000):
		if i.id in (ARM_INS_BL, ARM_INS_CMP):
			print("0x%x:\t%s\t%s" %(i.address, i.mnemonic, i.op_str))

		if len(i.regs_read) > 0:
			print("\tImplicit registers read: "),
			for r in i.regs_read:
				print("%s " %i.reg_name(r)),
			print

		if len(i.groups) > 0:
			print("\tThis instruction belongs to groups:"),
			for g in i.groups:
				print("%u" %g),
			print


# https://stackoverflow.com/questions/37439627/which-bytes-should-i-pass-to-capstone-to-disassemble-the-executable-code-of-a-pe
def TestDisassembleFile(file_path):
    print("File=%s"%file_path)
    pe = pefile.PE(file_path)

    eop = pe.OPTIONAL_HEADER.AddressOfEntryPoint
    code_section = pe.get_section_by_rva(eop)

    code_dump = code_section.get_data()

    code_addr = pe.OPTIONAL_HEADER.ImageBase + code_section.VirtualAddress

    md = Cs(CS_ARCH_X86, CS_MODE_64)

    for i in md.disasm(code_dump, code_addr):
        print("0x%x:\t%s\t%s" %(i.address, i.mnemonic, i.op_str))

# https://stackoverflow.com/questions/37439627/which-bytes-should-i-pass-to-capstone-to-disassemble-the-executable-code-of-a-pe
def TestDisassembleFileGroups(file_path):
    print("File=%s"%file_path)
    pe = pefile.PE(file_path)

    eop = pe.OPTIONAL_HEADER.AddressOfEntryPoint
    code_section = pe.get_section_by_rva(eop)

    code_dump = code_section.get_data()

    code_addr = pe.OPTIONAL_HEADER.ImageBase + code_section.VirtualAddress

    md = Cs(CS_ARCH_X86, CS_MODE_64)
    md.detail = True

    for i in md.disasm(code_dump, code_addr):
        print("0x%x:\t%-20s\t%-40s\t%10s" %(i.address, i.mnemonic, i.op_str, i.id))


def SplitPE(file_path):
	pe = pefile.PE(file_path)

	for section in pe.sections:
		# ('.bss\x00\x00\x00\x00', '0xf000', '0x14c', 0)
		# ('.data\x00\x00\x00', '0x5e000', '0x3a24', 11264)
		# ('.edata\x00\x00', '0x10000', '0x2067', 8704)
		# ('.idata\x00\x00', '0x18000', '0x76c', 2048)
		# ('.rdata\x00\x00', '0x15000', '0x1972', 6656)
		# ('.reloc\x00\x00', '0x63000', '0x53c0', 21504)
		# ('.rsrc\x00\x00\x00', '0x62000', '0x3d8', 1024)
		# ('.stab\x00\x00\x00', '0x15000', '0x33660', 210944)
		# ('.stabstr', '0x49000', '0xa2d5f', 667136)
		# ('.text\x00\x00\x00', '0x1000', '0x5cd75', 380416)
		# ('.textbss', '0x1000', '0x10000', 0)

		# typedef struct _IMAGE_SECTION_HEADER {
		#   BYTE  Name[IMAGE_SIZEOF_SHORT_NAME];
		#   union {
		# 	DWORD PhysicalAddress;
		# 	DWORD VirtualSize;
		#   } Misc;
		#   DWORD VirtualAddress;
		#   DWORD SizeOfRawData;
		#   DWORD PointerToRawData;
		#   DWORD PointerToRelocations;
		#   DWORD PointerToLinenumbers;
		#   WORD  NumberOfRelocations;
		#   WORD  NumberOfLinenumbers;
		#   DWORD Characteristics;
		# } IMAGE_SECTION_HEADER, *PIMAGE_SECTION_HEADER;
		print (section.Name, hex(section.VirtualAddress), hex(section.Misc_VirtualSize), section.SizeOfRawData )
		print ( str(section.Name), section.VirtualAddress, section.Misc_VirtualSize, section.SizeOfRawData )


if False:
	TestHeavy()
	TestLight()
	TestThree()

for file_path in [
	#r"C:\Program Files (x86)\Git\bin\libaprutil-0-0.dll",
	r"C:\Program Files (x86)\Hewlett-Packard\Energy Star\ClearSysReg.exe",
	#r"C:\Program Files (x86)\Hewlett-Packard\Energy Star\Estar.dll",
	#r"C:\Program Files (x86)\Hewlett-Packard\Energy Star\msvcp100.dll",
]:
	#SplitPE(file_path)
	#TestDisassembleFile(file_path)
	TestDisassembleFileGroups(file_path)

rr = raw_input("Press return:")

#name = input("What's your name? ")
#print("Nice to meet you " + name + "!")
#age = input("Your age? ")
#print("So, you are already " + str(age) + " years old, " + name + "!")