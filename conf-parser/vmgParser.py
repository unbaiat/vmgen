import ConfigParser
from configobj import ConfigObj
from vmgStruct import vmgSection, vmgStruct

def parse_hardware(config):
    sectDict = {}
    for key in config['hardware'].keys():
        if type(config['hardware'][key]) is str:
            sectDict[key] = config['hardware'][key]
        
    if 'num_hdd' in config['hardware'].keys():
        num_hdd = int(config['hardware']['num_hdd'])
        if num_hdd > 0:
            list_hdd = []
            for hindex in range(num_hdd):
                hdict = {}
                hname = 'hdd' + str(hindex)
                for key in config['hardware'][hname].keys():
                    if type(config['hardware'][hname][key]) is str:
                        hdict[key] = config['hardware'][hname][key]
                if 'num_partitions' in config['hardware'][hname]:
                    num_parts = int(config['hardware'][hname]['num_partitions'])
                    if num_parts > 0:
                        list_part = []
                        for pindex in range(num_parts):
                            pname = 'partition' + str(pindex)
                            list_part.append(config['hardware'][hname][pname])
                hdict['partitions'] = list_part
                list_hdd.append(hdict)
        sectDict['hdds'] = list_hdd
    if 'num_cd_drive' in config['hardware'].keys():
        num_cdd = int(config['hardware']['num_cd_drive'])
        if num_cdd > 0:
            list_cdd = []
            for index in range(num_cdd):
                name = 'cd_drive' + str(index)
                list_cdd.append(config['hardware'][name])
        sectDict['cd_drives'] = list_cdd
    if 'num_eth' in config['hardware'].keys():
        num_eth = int(config['hardware']['num_eth'])
        if num_eth > 0:
            list_eth = []
            for index in range(num_eth):
                name = 'eth' + str(index)
                list_eth.append(config['hardware'][name])
        sectDict['eths'] = list_eth
    return vmgSection('hardware', sectDict)

def parse_network(config):
    sectDict = {}
    for key in config['network'].keys():
        if type(config['network'][key]) is str:
            sectDict[key] = config['network'][key]
        else:
            if key == 'firewall_rules':
                sectDict['firewall_rules'] = config['network'][key].values()
    return vmgSection('network', sectDict)

def parse_users(config):
    sectDict = {}
    for key in config['users'].keys():
        if type(config['users'][key]) is str:
            sectDict[key] = config['users'][key]
    if 'num_user' in config['users'].keys():
        num_user = int(config['users']['num_user'])
        if num_user > 0:
            list_user = []
            for index in range(num_user):
                name = 'user' + str(index)
                list_user.append(config['users'][name])
        sectDict['users'] = list_user
    return vmgSection('users', sectDict)

def parse_config(config):
    sectDict = {}
    for key in config['config'].keys():
        if type(config['config'][key]) is str:
            sectDict[key] = config['config'][key]
        else:
            if key == 'repos':
                sectDict['repos'] = config['config'][key].values()    
    return vmgSection('config', sectDict)

def parse_devel(config):
    sectDict = {}
    for key in config['devel'].keys():
        if type(config['devel'][key]) is str:
            sectDict[key] = config['devel'][key]

    return vmgSection('devel', sectDict)

def parse_services(config):
    sectDict = {}
    for key in config['services'].keys():
        if type(config['services'][key]) is str:
            sectDict[key] = config['services'][key]

    return vmgSection('gui', sectDict)

def parse_gui(config):
    sectDict = {}
    for key in config['gui'].keys():
        if type(config['gui'][key]) is str:
            sectDict[key] = config['gui'][key]

    return vmgSection('gui', sectDict)

def parse(fileName):
    config = ConfigObj(infile=fileName, raise_errors=True, file_error=True)
    rootDict = {}
    for sect in config.keys():
        methodName = 'parse_' + str(sect)
        rootDict[sect] = globals()[methodName](config)
    return vmgStruct(rootDict)

vmgStruct = parse('sample.conf')
print vmgStruct
vmgStruct.dump('sample.dump')
