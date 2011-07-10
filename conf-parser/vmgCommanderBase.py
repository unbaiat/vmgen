from vmgStruct import *
import shutil
import datetime

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

	For modularity, an instance of an installer (for program installation) is 
	provided:
		- apt-get
		- yum
		- install from sources
		- Windows installer
"""

finished_dir = "finished/"
url = "http://10.38.135.232/machines/"

class CommanderBase:
	def __init__(self, dumpFile):
		"""
			Load the parsed data from dumpFile.
			Set installer as the current installer
			Set config module
		"""
		self.loadStruct(dumpFile)

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

		# instantiate and run Config module
		try:
			self.config = self.getConfigInstance()
			self.config.setupConfig()
			root_passwd = self.config.getNewRootPasswd()
			if root_passwd is not None:
				self.communicator.updatePassword(root_passwd)
		except Exception:
			print "Error executing Config"

		# instantiate and run Installer module
		try:
			self.installer = self.getInstallerInstance()
			self.setupServices()
			self.setupDeveloperTools()
			self.setupGuiTools()
		except Exception:
			print "Error executing Installer"

		self.disconnectFromVM()

		self.shutdownVM()

		arch_name, arch_dir = self.createArchive()

		now = datetime.datetime.now()
		new_name = "[" + now.strftime("%Y-%m-%d %H:%M") + "][" + \
				self.getModuleName() + "] " + arch_name 

		print
		print "Done. " + new_name + " was created."
		shutil.move(arch_dir + arch_name, finished_dir + new_name)
		print "You can download the created machine from " + url

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

	def setupServices(self):
		""" Configure the requested services on the guest OS. """
		pass

	def setupDeveloperTools(self):
		""" Install the tools needed for development on the guest OS. """
		pass

	def setupGuiTools(self):
		""" Install graphical applications on the guest OS. """
		pass

	def createArchive(self):
		""" Create an archive containing the VM. """
		pass


	def installPrograms(self, section):
		""" Install the programs in section using the configured installer. """
		prog_list = []
		for k, v in section.items():
			if v == "1":
				# single program
				prog_list.append(k)
			elif v == "0":
				pass
			else:
				# a list of programs
				# TODO: multiple programs separation?
				l = [p.strip() for p in v.split(',')]
				prog_list.extend(l)

		self.installer.install(prog_list)
	
	def getConfigInstance(self):
		return None

	def getInstallerInstance(self):
		return None

	def getModuleName(self):
		return ""
