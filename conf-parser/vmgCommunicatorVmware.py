from vmgCommunicatorBase import *

log = logging.getLogger("vmgen.vmgCommunicatorVmware")

class CommunicatorVmware(CommunicatorBase):
	def __init__(self, vmx, user, passwd):
		"""
			Set parameters for the communicator
			Parameters are given as a dictionary of <key, value> pairs which are
			specific to each communicator
		"""
		self.vmx = vmx
		self.user = user
		self.passwd = passwd

		self.prefix = "vmrun -t ws" + " -gu " + self.user + " -gp " + self.passwd

	def runCommand(self, cmd):
		"""
			Execute the specified command
		"""
		executeCommand(self.prefix + " runProgramInGuest " + self.vmx + " -activeWindow " + cmd)
		
	def copyFileToVM(self, localPath, remotePath):
		"""
			Copy the specified file to the virtual machine
		"""
		executeCommand(self.prefix + " copyFileFromHostToGuest " + self.vmx + " " + localPath + " " 
				+ remotePath)
	
	def deleteFileInGuest(self, remotePath):
		"""
			Delete the specified file from the virtual machine
		"""
		executeCommand(self.prefix + " deleteFileInGuest " + self.vmx + " " + remotePath)

	def updatePassword(self, passwd):
		self.passwd = passwd
		self.prefix = "vmrun -t ws" + " -gu " + self.user + " -gp " + self.passwd
