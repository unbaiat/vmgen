from vmgCommanderDummy import CommanderDummy
from vmgCommanderVmware import CommanderVmware
from vmgInstallerDummy import InstallerDummy

i = InstallerDummy()
c = CommanderVmware("conf.dump", i, None)
c.setupVM()
