from vmgInstallerWindows import *

i = InstallerWindows()
i.setUserPass("vmgen", "pass")
i.setSetupFolder("e:\\")
i.install("mozilla-thunderbird")
