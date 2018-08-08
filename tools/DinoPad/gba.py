import struct

AARCH32_WORD = struct.Struct("<i")
AARCH32_HALFWORD = struct.Struct("<h")
AARCH32_BYTE = struct.Struct("<h")

def ptr_to_rom(ptr):
    return ptr & 0xFFFFFF
