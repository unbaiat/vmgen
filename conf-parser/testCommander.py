from vmgCommanderDummy import CommanderDummy
from vmgInstallerDummy import InstallerDummy

i = InstallerDummy()
c = CommanderDummy("conf.dump", i, None)
c.setupVM()
