from vmgInstallerBase import InstallerBase

class InstallerDummy(InstallerBase):
	def install(self, program):
		print "apt-get install", program

#i = InstallerDummy()
#i.install("aaa")
#i.installList(["aa", "bb", "cc"])
