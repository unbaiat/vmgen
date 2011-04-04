class InstallerBase:
	def __init__(self):
		pass

	def install(self, program):
		pass

	def installList(self, progList):
		[self.install(p) for p in progList]

