from vmgConfigBase import ConfigBase
from runCommands import *
from vmgUtils import *
from vmgLogging import *

log = logging.getLogger("vmgen.vmgConfigWindows")

class ConfigWindows(ConfigBase):
	def __init__(self, data, communicator):
		ConfigBase.__init__(self, data, communicator)
		self.data = data

		self.setupFolder = "C:\\"
		self.cmds = ""

		log.info("Configuring the OS...")

	def setupSystem(self):
		""" 
			Setup:
			- the hostname
			- the administrator password
		"""
		log.info("\tSetting up system settings...")

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
		log.info("\tSetting up groups...")
		section = self.data.getSection("users")
		groups = section.get("groups").data.values()
		for group_name in groups:
			self.config("net localgroup " + group_name + " /ADD")

	def setupUsers(self):
		""" Create groups. """
		log.info("\tSetting up users...")
		section = self.data.getSection("users")
		users = section.get("users").data.values()
		for user in users:
			name = user.get("name")
			passwd = user.get("passwd")

			# create the user
			self.config("net user " + name + " " + passwd + " /ADD")

			# add the user to the specified groups
			for group in splitList(user.get("groups")):
				self.config("net localgroup " + group + " " + name + " /ADD")

	def setupNetwork(self):
		log.info("\tSetting up network...")
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
		log.info("\tSetting up firewall...")
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
		log.info("\tApplying settings...")

		temp_file = "config.bat"
		remote_temp_file = "\"" + self.setupFolder + temp_file + "\""

		# write the install command into a temp script file (.bat)
		with open(temp_file, "w") as f:
			f.write(self.cmds)
#			f.write("PAUSE\n")

		# copy the temp script file to the guest
		# execute the temp script on the guest
		# remove the temp script file from the guest
		# remove the temp script from the local machine
		self.communicator.fileCopyRunDelete(temp_file, remote_temp_file,
				"cmd.exe /C ")

	def getRemoveCommand(self, fileName):
		# TODO: add type?
		return "del " + fileName

	def getRemotePath(self, fileName):
		return "\"" + self.setupFolder + fileName + "\""

	def getNewRootPasswd(self):
		return self.root_passwd
