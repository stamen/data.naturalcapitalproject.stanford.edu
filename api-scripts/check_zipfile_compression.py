import sys
import zipfile

# integer const to string
ZIPFILE_CONSTANTS = {}
for attrname in dir(zipfile):
    if attrname.startswith('ZIP_'):
        ZIPFILE_CONSTANTS[getattr(zipfile, attrname)] = attrname


def list_zipfile_compression(zipname):
    with zipfile.ZipFile(zipname, 'r') as zip:
        for info in zip.infolist():
            if info.compress_type not in ZIPFILE_CONSTANTS:
                problem = "PROBLEM"
            else:
                problem = "OK     "
            print(zipfile.compressor_names[info.compress_type] + "\t",
                  problem, info.filename)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python check_zipfile_compression.py zipfile")
        sys.exit(1)

    list_zipfile_compression(sys.argv[1])
