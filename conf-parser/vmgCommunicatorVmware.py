log = logging.getLogger("vmgen.vmgCommunicatorVmware")

class CommunicatorVmware(CommunicatorBase):
	def __init__(self, **connData):
		"""
			Set parameters for the communicator
			Parameters are given as a dictionary of <key, value> pairs which are
			specific to each communicator
		"""
		try:
			self.vmx = connData['vmx']
			self.user = connData['user']
			self.passwd = connData['passwd']
		except KeyError:
			log.error("CommunicatorVmware: invalid parameters")

	def runCommand(self, cmd):
		"""
			Execute the specified command
		"""
		executeCommand("vmrun -t ws -gu " + self.user + " -gp " + self.passwd + " runProgramInGuest " + self.vmx + " - activeWindow " + cmd)
		
	def copyFileToVM(self, localPath, remotePath):
		"""
			Copy the specified file to the virtual machine
		"""
		executeCommand("vmrun -t ws -gu " + self.user + " -gp " + self.passwd + " copyFileFromHostToGuest " + self.vmx + " " + localPath + " " + remotePath)
	
	def deleteFileInGuest(self, remotePath):
		"""
			Delete the specified file from the virtual machine
		"""
		executeCommand("vmrun -t ws -gu " + self.user + " -gp " + self.passwd + " deleteFileInGuest " + self.vmx + " " + remotePath)
