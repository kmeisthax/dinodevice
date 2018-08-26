from DinoPad.dinofs.extract import extract_file_meta, extract_file_data

import argparse, os.path, pathlib

def dinofs_ext(argv):
    parser = argparse.ArgumentParser(description="Parse files from a ROM containing one or more DinoFS images.")
    
    parser.add_argument("--rombase", type=int, metavar="NNNNNN", default=0xBBDE8, help="The offset of a DinoFS master listing within a Dino Device ROM image.")
    parser.add_argument("rom", type=str, nargs=1, metavar="dd1rom.gba", help="The location of a Dino Device 1 ROM image.")
    parser.add_argument("extract_target", type=str, nargs=1, metavar="files_dir/", help="A directory to store extracted files in.")
    
    args = parser.parse_args(argv)
    
    with open(args.rom[0], "rb") as rom:
        inodes = extract_file_meta(rom, None, None, args.rombase)
        
        for inode in inodes:
            outpath = pathlib.Path(args.extract_target[0], "%0x" % (inode.dirid,))
            outpath.mkdir(parents=True, exist_ok=True)
            
            outfile = pathlib.Path(outpath, "%0x.bin" % (inode.fileid,))
            
            with open(outfile, "wb") as extfile:
                data = extract_file_data(rom, inode)
                extfile.write(data)
            
            print("Extracted file %s" % (outfile,))