import math

from DinoPad.gba import AARCH32_WORD, ptr_to_rom

class DinoFSInode(object):
    """Represents a DinoFS file record."""

    def __init__(self, dirid, fileid, base, length):
        self.dirid = dirid
        self.fileid = fileid
        self.base = base
        self.length = length

    def __repr__(self):
        return "DinoFSInode(%d, %d, 0x%x, 0x%x)" % (self.dirid, self.fileid, self.base, self.length)

def extract_file_meta(rom, dirid = None, fileid = None, base = 0xBBDE8):
    """Given a DinoFS directory at the given base address, extract file metadata.

    The dirid and fileid parameters are optional; if unpopulated the function
    will scan all files and/or all directories. You may provide an integer or
    a slice to restrict the file scan. The number of directories scanned is
    limited to the number of directories in the original ROM (3); the number of
    files is limited to the size of each directory.

    Returned metadata consists of a list of all DinoFSInode objects matching the
    given directory and file IDs."""

    last = rom.tell()
    result = []

    base = ptr_to_rom(base)

    if dirid is None:
        dirid = slice(None)
    elif type(dirid) is int:
        dirid = slice(dirid, (dirid) + 1)

    if fileid is None:
        fileid = slice(None)
    elif type(fileid) is int:
        fileid = slice(fileid, (fileid) + 1)

    for d in range(3)[dirid]:
        rom.seek(base + (4 * d), 0)
        (dirbase,) = AARCH32_WORD.unpack(rom.read(AARCH32_WORD.size))
        dirbase = ptr_to_rom(dirbase)

        rom.seek(dirbase)
        (dirsize,) = AARCH32_WORD.unpack(rom.read(AARCH32_WORD.size))
        dirsize = math.floor(dirsize / AARCH32_WORD.size)

        #Some directories list a file at offset 0 at the end.
        #This lists the directory itself as a file, which makes no sense, so
        #we'll ignore those.
        while dirsize > 0:
            rom.seek(dirbase + ((dirsize - 1) * AARCH32_WORD.size))
            (fileoffset,) = AARCH32_WORD.unpack(rom.read(AARCH32_WORD.size))

            if fileoffset != 0:
                break

            dirsize -= 1

        for f in range(dirsize)[fileid]:
            rom.seek(dirbase + (4 * f))
            (fileoffset,) = AARCH32_WORD.unpack(rom.read(AARCH32_WORD.size))
            filebase = dirbase + fileoffset

            if f < (dirsize - 1):
                (next_fileoffset,) = AARCH32_WORD.unpack(rom.read(AARCH32_WORD.size))
                next_fileoffset = ptr_to_rom(next_fileoffset)
                filesize = next_fileoffset - fileoffset
            else:
                #All DinoFS directories end with a 3 byte file containing the
                #ASCII string "end".
                filesize = 3

            result.append(DinoFSInode(d, f, filebase, filesize))

    rom.seek(last, 0)

    return result
