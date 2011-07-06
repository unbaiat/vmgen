from vmgStruct import *

class ConfigBase:
	def __init__(self, data, comm):
		self.data = data
		self.communicator = comm

	def setupConfig(self):
		""" 
			Call all the setup methods and apply the settings. 
		"""
		self.setupSystem()
		self.setupGroups()
		self.setupUsers()
		self.setupNetwork()
		self.setupFirewall()

		self.applySettings()

	def setupSystem(self):
		pass

	def setupGroups(self):
		pass

	def setupUsers(self):
		pass

	def setupNetwork(self):
		pass

	def setupFirewall(self):
		pass

	def applySettings(self):
		pass

	def getNewRootPasswd():
		return None
