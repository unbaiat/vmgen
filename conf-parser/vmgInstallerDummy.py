from vmgInstallerBase import InstallerBase
from vmgLogging import *

log = logging.getLogger("vmgen.vmgInstallerDummy")
class InstallerDummy(InstallerBase):
	def install(self, program):
		log.info("\tInstaller: " + "apt-get install " + program)

#i = InstallerDummy()
#i.install("aaa")
#i.installList(["aa", "bb", "cc"])
