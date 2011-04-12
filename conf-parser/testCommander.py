from vmgCommanderDummy import CommanderDummy
from vmgCommanderVmware import CommanderVmware
from vmgInstallerDummy import InstallerDummy

i = InstallerDummy()
c = CommanderVmware("sample.dump", i, None)
c.setupVM()
