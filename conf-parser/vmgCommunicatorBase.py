from runCommands import *
import os

"""
	A base communicator class (abstract), which provides a generic interface for
	executing commands in the virtual machine and file transfers to and from the
	virtual machine.
"""

class CommunicatorBase:
	def __init__(self, **connData):
		"""
			Set parameters for the communicator
			Parameters are given as a dictionary of <key, value> pairs which are
			specific to each communicator
		"""
		pass

	def runCommand(self, cmd):
		"""
			Execute the specified command
		"""
		pass
		
	def copyFileToVM(self, localPath, remotePath):
		"""
			Copy the specified file to the virtual machine
		"""
		pass
	
	def deleteFileInGuest(self, remotePath):
		"""
			Delete the specified file from the virtual machine
		"""
		pass

	def updatePassword(self, passwd):
		pass

	def fileCopyRunDelete(self, localPath, remotePath, runPrefix):
		self.copyFileToVM(localPath, remotePath)
		self.runCommand(runPrefix + remotePath)
		self.deleteFileInGuest(remotePath)
		os.remove(localPath)
