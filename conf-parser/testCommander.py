from vmgCommanderDummy import CommanderDummy
from vmgCommanderVmware import CommanderVmware
from vmgCommanderOpenvz import CommanderOpenvz
from vmgCommanderLxc import CommanderLxc
from vmgInstallerDummy import InstallerDummy

#i = InstallerDummy()
#c = CommanderVmware("sample.dump", i, None)
#c.setupVM()

class testCommander():
    def __init__(self, vmtype, dumpFile):
        cmdSwitch = {   'vmware' : CommanderVmware,
                        'openvz' : CommanderOpenvz,
                        'lxc' : CommanderLxc
                        }
        try:
            inst = InstallerDummy()
            self.cmd = cmdSwitch[vmtype](dumpFile, inst, None)
        except Exception:
            print 'Cannot create commander'

    def create(self):    
        self.cmd.setupVM()
