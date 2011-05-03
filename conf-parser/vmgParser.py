import sys
from configobj import ConfigObj
from vmgStruct import vmgSection, vmgStruct

class vmgParser():
    '''
        Parse a configuration file (INI format) and build
        a structure containing the data.
        Comments(#), empty line, spaces are allowes
        '''
        
    def __init__(self, infile):
        self.infile = infile

    def __parse_section(self, config):
        '''
            Retrieve the subsections, recursively.
            Internal purposes.
            '''
        sectDict = {}
        for key in config.keys():
            if type(config[key]) is str:
                sectDict[key] = config[key]
            else:
                sectDict[key] = vmgSection(key, self.__parse_section(config[key]))
        return sectDict

    def parse(self):
        '''
            Use the configObj library to parse the file.
            '''
        config = ConfigObj(infile=self.infile, raise_errors=True, file_error=True)
        rootDict = {}
        for sect in config.keys():
            rootDict[sect] = vmgSection(sect, self.__parse_section(config[sect]))
        self.struct = vmgStruct(rootDict)

    def dump(self, dumpFile):
        '''
            Dump the structure to a file.
            '''
        try:
            self.struct.dump(dumpFile)
            return dumpFile
        except Exception:
            print 'Cannot dump parser structure'

    def show(self):
        '''
            Print the data structure.
            '''
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
