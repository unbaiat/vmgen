import ConfigParser
from configobj import ConfigObj
from vmgStruct import vmgSection, vmgStruct

def parse_section(config):
    sectDict = {}
    for key in config.keys():
        if type(config[key]) is str:
            sectDict[key] = config[key]
        else:
            sectDict[key] = vmgSection(key, parse_section(config[key]))
    return sectDict

def parse(fileName):
    config = ConfigObj(infile=fileName, raise_errors=True, file_error=True)
    rootDict = {}
    for sect in config.keys():
        rootDict[sect] = vmgSection(sect, parse_section(config[sect]))
    return vmgStruct(rootDict)

vmgStruct = parse('sample.conf')
print vmgStruct
vmgStruct.dump('sample.dump')
