import sys
from configobj import ConfigObj
from vmgStruct import vmgSection, vmgStruct

class vmgParser():
    def __init__(self, infile):
        self.infile = infile

    def __parse_section(self, config):
        sectDict = {}
        for key in config.keys():
            if type(config[key]) is str:
                sectDict[key] = config[key]
            else:
                sectDict[key] = vmgSection(key, self.__parse_section(config[key]))
        return sectDict

    def parse(self):
        config = ConfigObj(infile=self.infile, raise_errors=True, file_error=True)
        rootDict = {}
        for sect in config.keys():
            rootDict[sect] = vmgSection(sect, self.__parse_section(config[sect]))
        self.struct = vmgStruct(rootDict)

    def dump(self, dumpFile):
        try:
            self.struct.dump(dumpFile)
            return dumpFile
        except Exception:
            print 'Cannot dump parser structure'

    def show(self):
        try:
            print self.struct
        except Exception:
            print 'Cannot print parser structure'

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage: vmgParser.py infile'
    else:
        parser = vmgParser(sys.argv[1])
        parser.parse()
        parser.show()
        parser.dump(sys.argv[1] + '.dump')
