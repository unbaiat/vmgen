from vmgStruct import *

"""
	A base commander class (abstract), which uses the data parsed from the
	input .conf file and executes the steps to create a new VM according to the
	user's request.

	The concrete actions for each step are implemented in the derived
	commanders:
		- vmgCommanderVmware
		- vmgCommanderOpenVz
		- vmgCommanderLxc
		- vmgCommanderVirtualBox

	Fro modularity, an instance of an installer (for program installation) is 
	provided:
		- apt-get
		- yum
		- install from sources
		- Windows installer
"""

class CommanderBase:
	def __init__(self, dumpFile, installer, connection):
		"""
			Load the parsed data from dumpFile.
			Set installer as the current installer
			Use connection as the current method to interract with the machine:
				- ssh
				- VIX
				- libvirt
				- ...
		"""
		self.loadStruct(dumpFile)
		self.installer = installer
		self.connection = connection

	def loadStruct(self, dumpFile):
		"""
			Load a vmgStruct from the file 'dumpFile'
		"""

		with open(dumpFile, 'rb') as f:
			self.data = pickle.load(f)

	def setupVM(self):
		"""	
			Execute all the steps needed to create a virtual machine.
			Each step is implemented by each type of commander.
		"""

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
		""" Power on the VM. """
		pass

	def shutdownVM(self):
		""" Shutdown the VM. """
		pass

	def connectToVM(self):
		""" Connect to the new VM. """
		pass

	def disconnectFromVM(self):
		""" Disconnect from the new VM. """
		pass
		
	def setupHardware(self):
		""" Create the hardware for the new VM. """
		pass

	def setupPartitions(self):
		""" Create the partitions on the new VM disks. """
		pass

	def setupOperatingSystem(self):
		""" Install the OS on the new VM. """
		pass

	def setupConfigurations(self):
		""" Configure the requested system settings. """
		pass

	def setupNetwork(self):
		""" Configure the network on the guest OS. """
		pass

	def setupUsers(self):
		""" Add the requested users to the guest OS. """
		pass

	def setupServices(self):
		""" Configure the requested services on the guest OS. """
		pass

	def setupDeveloperTools(self):
		""" Install the tools needed for development on the guest OS. """
		pass

	def setupGuiTools(self):
		""" Install graphical applications on the guest OS. """
		pass


	def installPrograms(self, section):
		""" Install the programs in section using the configured installer. """
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
	
