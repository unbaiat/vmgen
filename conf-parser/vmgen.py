import sys
from testCommander import testCommander
from vmgParser import vmgParser

def main(vmtype, infile):
    # call parser
    parser = vmgParser(infile)
    parser.parse()
    dumpFile = infile + '.dump'
    parser.dump(dumpFile)

    # call commander
    cmd = testCommander(vmtype, dumpFile)
    cmd.create()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Usage: vmgen.py [vmware|openvz|lxc] infile'
    else:
        main(sys.argv[1], sys.argv[2])
