import sys
import zipfile

# integer const to string
ZIPFILE_CONSTANTS = {}
for attrname in dir(zipfile):
    if attrname.startswith('ZIP_'):
        ZIPFILE_CONSTANTS[getattr(zipfile, attrname)] = attrname


def list_zipfile_compression(zipname):
    n_problem_files = 0
    with zipfile.ZipFile(zipname, 'r') as zip:
        for info in zip.infolist():
            if info.compress_type not in ZIPFILE_CONSTANTS:
                n_problem_files += 1
                problem = "PROBLEM"
            else:
                problem = "OK     "
            print(zipfile.compressor_names[info.compress_type] + "\t",
                  problem, info.filename)

    print("\nNumber of files compressed with unsupported codecs:",
          n_problem_files)
    if n_problem_files:
        sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python check_zipfile_compression.py zipfile")
        sys.exit(1)

    list_zipfile_compression(sys.argv[1])
