from vmgCommanderDummy import CommanderDummy
from vmgCommanderVmware import CommanderVmware
#from vmgCommanderOpenvz import CommanderOpenvz
from vmgCommanderLxc import CommanderLxc
from vmgInstallerDummy import InstallerDummy

#i = InstallerDummy()
#c = CommanderVmware("sample.dump", i, None)
#c.setupVM()

class testCommander():
    def __init__(self, vmtype, dumpFile):
        cmdSwitch = {   'vmware' : CommanderVmware,
#                        'openvz' : CommanderOpenvz,
                        'lxc' : CommanderLxc
                        }
        print vmtype, cmdSwitch[vmtype]
        try:
            self.cmd = cmdSwitch[vmtype](dumpFile)
        except Exception as e:
            print 'Cannot create commander', e

    def create(self):    
        self.cmd.setupVM()
