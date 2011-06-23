log = logging.getLogger("vmgen.vmgCommunicatorLxc")
key = "-i vmaster_key.private"

class CommunicatorLxc(CommunicatorBase):
	def __init__(self, **connData):
		"""
			Set parameters for the communicator
			Parameters are given as a dictionary of <key, value> pairs which are
			specific to each communicator
		"""
		try:
			self.vmx = connData['vmx']
			self.id = connData['id']
			self.host = connData['host']
			setUserHost(self.host)
		except KeyError:
			log.error("CommunicatorLxc: invalid parameters")

	def runCommand(self, cmd):
		"""
			Execute the specified command
		"""
		executeCommandSSH("lxc-execute -n " + self.id + " " + cmd)
		
	def copyFileToVM(self, localPath, remotePath):
		"""
			Copy the specified file to the virtual machine
		"""
		executeCommand("scp " + key + " " + localPath + " " + self.host + ":/lxc/" + self.id + remotePath)
	
	def deleteFileInGuest(self, remotePath):
		"""
			Delete the specified file from the virtual machine
		"""
		executeCommandSSH("rm -rf /lxc/" + self.id + file)