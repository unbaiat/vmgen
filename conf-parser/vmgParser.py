import re
from vmgStruct import *

class vmgconfParser:
    def __init__(self):
        self.data = {}
        self.vmgStruct = None

    def getStruct(self):
        return self.vmgStruct

    def parse(self, fileName=None, delim='='):
        '''
            Parse a vmgen configuration file formatted like:
            [section]
                field=value
                ...
            - comments (#), empty lines, spaces allowed

        '''

        sectionName = None
        sectionDict = {}

        for line in open(fileName, 'r'):
            # skip empty or space padded lines
            line = line.strip()
            if not line:
                continue
            
            # skip commented lines
            if re.compile('^#').search(line) is not None:
                continue

            # new section start
            if re.compile('^\[[a-zA-Z]+]$').search(line) is not None:
                if sectionName is None:
                    if len(sectionDict.items()) > 0 :
                        print "Config file must start with a section"
                        return
                else:
                    newSection = vmgSection(sectionName, sectionDict)
                    self.data[sectionName] = newSection
                    sectionDict = {}
                sectionName = line[1:-1]
                continue

            # identify attributes and values
            kv = line.split(delim)
            if len(kv) != 2:
                print 'Parse error: ' + line
                return None
            key = kv[0].strip()
            value = kv[1].strip().split('#')
            if value is not None:
                sectionDict[key] = value[0].strip()

        # add the last section to the root structure
        newSection = vmgSection(sectionName, sectionDict)
        self.data[sectionName] = newSection
        self.vmgStruct = vmgStruct(self.data)

parser = vmgconfParser()
parser.parse('vmg.conf')
root = parser.getStruct()
print root
root.dump('conf.dump')
