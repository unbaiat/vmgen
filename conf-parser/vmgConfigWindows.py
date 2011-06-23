from vmgConfigBase import ConfigBase
from runCommands import *

class ConfigWindows(ConfigBase):
	def __init__(self, data, vmx):
		self.data = data
		user = "Administrator"
		passwd = "pass"
		self.prefix = "vmrun -t ws" + " -gu " + user + " -gp " + passwd

		self.vmx = vmx
		self.setupFolder = "C:\\"
		self.cmds = ""

	def setupSystem(self):
		""" 
			Setup:
			- the hostname
			- the administrator password
		"""

		section = self.data.getSection("config")

		# set hostname
		oldName = "\"vmgen-pc\""
		hostname = section.get("hostname")
		self.config("wmic COMPUTERSYSTEM where name=" + oldName + 
			" call rename " + "\"" + hostname + "\"")

		# set Administrator password
		self.root_passwd = section.get("root_passwd")
		self.config("net user Administrator " + self.root_passwd)

	def setupGroups(self):
		""" Create groups. """
		section = self.data.getSection("users")
		groups = section.get("groups").data.values()
		for group in groups:
			group_name = group.get("name")
			self.config("net localgroup " + group_name + " /ADD")

	def setupUsers(self):
		""" Create groups. """
		section = self.data.getSection("users")
		users = section.get("users").data.values()
		for user in users:
			name = user.get("name")
			passwd = user.get("passwd")

			# create the user
			self.config("net user " + name + " " + passwd + " /ADD")

			# add the user to the specified groups
			# TODO: remove [ ]
			for group in [user.get("groups")]:
				self.config("net localgroup " + group + " " + name + " /ADD")

	def setupNetwork(self):
		# TODO: MAC
		section = self.data.getSection("network")
		self.eth_list = getSortedValues(section.get("eths").data)
		for i, eth in enumerate(self.eth_list):
			eth_name = "Local Area Connection"

			# TODO remove i += 1
			i += 2

			if i > 1:
				eth_name += " " + str(i)
			eth_name = "\"" + eth_name + "\""
			type = eth.get("type")
			if type == "static":
				# static addresses
				hw_address = eth.get("hw_addr")
				address = eth.get("address")
				network = eth.get("network")
				gateway = eth.get("gateway")
				dns = eth.get("dns")

				# ip, netmask, gateway
				self.config("netsh interface ip set address name=" + 
					eth_name + " static " + address + " " + network + " " + 
					gateway + " " + "1")
				# dns
				self.config("netsh interface ip set dns name=" + 
					eth_name + " static " + dns + " primary")
			elif type == "dhcp":
				# dhcp addresses
				# ip, netmask, gateway
				self.config("netsh interface ip set address name=" + 
					eth_name + " dhcp")
				# dns
				self.config("netsh interface ip set dns name=" + 
					eth_name + " dhcp")


	def setupFirewall(self):
		""" Setup the open ports in the firewall. """
		section = self.data.getSection("network")
		ports = section.get("open_ports").data.values()
		for port in ports:
			proto = port.get("proto")
			port_num = port.get("port")
			desc = port.get("description")

			# create the rule
			self.config("netsh firewall add portopening " + proto + " " + 
				port_num + " " + desc)

	def config(self, cmd):
		self.cmds += cmd + "\n"

	def applySettings(self):
		print self.cmds
#		return

		temp_file = "config.bat"
		remote_temp_file = "\"" + self.setupFolder + temp_file + "\""

		# write the install command into a temp script file (.bat)
		with open(temp_file, "w") as f:
			f.write(self.cmds)
#			f.write("PAUSE\n")

		# TODO: common code with the InstallerWindows
		# copy the temp script file to the guest
		self.copyFileFromHostToGuest(temp_file)

		# execute the temp script on the guest
		executeCommand(self.prefix + " runProgramInGuest " + self.vmx +
			" -activeWindow " +	"cmd.exe " + "/C " + remote_temp_file)

		# remove the temp script file from the guest
		self.deleteFileInGuest(remote_temp_file)

		# remove the temp script from the local machine
		os.remove(temp_file)

	def getRemoveCommand(self, fileName):
		# TODO: add type?
		return "del " + fileName

	def getRemotePath(self, fileName):
		return "\"" + self.setupFolder + fileName + "\""

	def copyFileFromHostToGuest(self, file):
		executeCommand(self.prefix + " copyFileFromHostToGuest " + self.vmx +
			" " + file + " " + self.getRemotePath(file))
	
	def deleteFileInGuest(self, file):
		executeCommand(self.prefix + " deleteFileInGuest " + self.vmx + 
			" " + file)

	def getNewRootPasswd(self):
		return self.root_passwd

def getSortedValues(d):
	return [d[k] for k in sorted(d.iterkeys())]
