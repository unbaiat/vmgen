from vmgCommunicatorBase import *
from vmgLogging import *

log = logging.getLogger("vmgen.vmgCommunicatorOpenvz")
key = "-i vmaster_key.private"

class CommunicatorOpenvz(CommunicatorBase):
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
			log.error("CommunicatorOpenvz: invalid parameters")

	def runCommand(self, cmd):
		"""
			Execute the specified command
		"""
		executeCommandSSH("vzctl exec " + self.id + " " + cmd)
		#executeCommandSSH("vzctl enter " + self.id + " --exec " + cmd + ";logout")
		
	def copyFileToVM(self, localPath, remotePath):
		"""
			Copy the specified file to the virtual machine
			$VZDIR is usually /vz, but on Debian system the path is /var/lib/vz
		"""
		
		executeCommand("scp " + key + " " + localPath + " " + self.host + ":/vz/root/" + self.id + "/" + remotePath)
	
	def deleteFileInGuest(self, remotePath):
		"""
			Delete the specified file from the virtual machine
		"""
		executeCommandSSH("rm -rf /vz/root/" + self.id + "/" + remotePath)

	def updatePassword(self, passwd):
		"""
			The OpenVZ communicator does not use the password
		"""
		pass
