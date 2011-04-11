from vmgStruct import *

class CommanderBase:
	def __init__(self, dumpFile, installer, connection):
		self.loadStruct(dumpFile)
		self.installer = installer
		self.connection = connection

	def loadStruct(self, dumpFile):
		'''
			Load a vmgStruct from the file 'dumpFile'
		'''

		with open(dumpFile, 'rb') as f:
			self.data = pickle.load(f)

	def setupVM(self):
		self.setupHardware()
		self.setupPartitions()
		self.setupOperatingSystem()

		self.startVM()
		self.connectToVM()
		self.setupConfigurations()
		self.setupNetwork()
#		self.setupUsers()
		self.setupServices()
		self.setupDeveloperTools()
		self.setupGuiTools()
		self.disconnectFromVM()

		self.shutdownVM()

	def startVM(self):
		pass

	def shutdownVM(self):
		pass

	def connectToVM(self):
		pass

	def disconnectFromVM(self):
		pass
		
	def setupHardware(self):
		pass

	def setupPartitions(self):
		pass

	def setupOperatingSystem(self):
		pass

	def setupConfigurations(self):
		pass

	def setupNetwork(self):
		pass

	def setupUsers(self):
		pass

	def setupServices(self):
		pass

	def setupDeveloperTools(self):
		pass

	def setupGuiTools(self):
		pass


	def installPrograms(self, section):
		for k, v in section.items():
			if v == "1":
				# single program
				self.installer.install(k)
			elif v == "0":
				pass
			else:
				# a list of programs
				l = [p.strip() for p in v.split(',')]
				self.installer.installList(l)
	

#c = CommanderBase()
#c.loadStruct("conf.dump")
