from vmgConfigBase import ConfigBase
from runCommands import *
from os import *

class ConfigLinux(ConfigBase, communicator):
	def __init__(self, data, comm):
		self.data = data
		self.cmds = ""
		self.comm = comm
	
	def setupSystem(self):
		""" 
			Setup:
			- the hostname
			- the administrator password
		"""

		section = self.data.getSection("config")

		# set hostname
		hostname = section.get("hostname")
		self.config("sysctl kernel.hostname=\"" + hostname + "\"")

		# set Administrator password
		rootPasswd = section.get("root_passwd")
		self.config("echo " + rootPasswd + " | passwd --stdin root")

	def setupGroups(self):
		""" Create groups. """
		section = self.data.getSection("users")
		groups = section.get("groups").data.values()
		for group in groups:
			group_name = group.get("name")
			self.config("groupadd " + group_name)

	def setupUsers(self):
		""" Create groups. """
		section = self.data.getSection("users")
		users = section.get("users").data.values()
		for user in users:
			name = user.get("name")
			passwd = user.get("passwd")

			# create the user
			groups = ""
			if len(user.get('groups')) > 0:
				groups = "-G " + ", ".join(user.get('groups'))
			self.config("useradd " + groups + " " + name)
			
			# hmm
			self.config("echo " + passwd + " | passwd --stdin " + name)

	def setupNetwork(self):
		section = self.data.getSection("network")
		self.eth_list = section.get("eths").data.values()
		for i, eth in enumerate(self.eth_list):
			pass

	def setupFirewall(self):
		""" Setup the open ports in the firewall. """
		section = self.data.getSection("network")
		pass

	def config(self, cmd):
		self.cmds += cmd + "\n"

	def applySettings(self):
		print self.cmds

		temp_file = "config.sh"

		# write the install command into a temp script file (.bat)
		with open(temp_file, "w") as f:
			f.write(self.cmds)

		# copy the temp script file to the guest
		self.comm.copyFileToVM(temp_file, temp_file)

		# execute the temp script on the guest
		self.comm.runCommand("./" + temp_file)

		# remove the temp script file from the guest
		self.comm.deleteFileInGuest(temp_file)

		# remove the temp script from the local machine
		os.remove(temp_file)