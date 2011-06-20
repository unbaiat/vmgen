from vmgConfigBase import ConfigBase

class ConfigWindows(ConfigBase):
	def __init__(self, data, vmx):
		self.data = data
		user = "Administrator"
		passwd = "pass"
		self.prefix = "vmrun -t ws" + " -gu " + user + " -gp " + passwd

		self.vmx = vmx
		self.setupFolder = "C:\""
		self.cmds = ""

	def setupSystem(self):
		""" Set the hostname. """
		section = self.data.getSection("network")
		oldName = "vmgen-pc"
		hostname = section.get("hostname"):
		self.config("wmic COMPUTERSYSTEM where name=" + oldName + 
			" call rename " + hostname)

	def setupGroups(self):
		""" Create groups. """
		section = self.data.getSection("users")
		for group in section.get("groups"):
			self.config("net localgroup " + group + " /ADD")

	def setupUsers(self):
		""" Create groups. """
		section = self.data.getSection("users")
		for user in section.get("groups"):
			name = user["name"]
			passwd = user["passwd"]

			# create the user
			self.config("net user " + name + " " + passwd + " /ADD")

			# add the user to the specified groups
			for group in user["groups"]:
				self.config("net localgroup " + group + " " + name + " /ADD")

	def setupNetwork(self):
		# TODO: MAC
		section = self.data.getSection("network")
		self.eth_list = section.get("eths").data.values()
		for i, eth in enumerate(self.eth_list):
			eth_name = "Local Area Connection"
			if i > 1:
				eth_name += " " + str(i)
			eth_name = "\"" + eth_name + "\""
			type = eth["type"]
			if type == "static":
				# static addresses
				hw_address = eth["hw_addr"]
				address = eth["address"]
				network = eth["network"]
				gateway = eth["gateway"]
				dns = eth["dns"]

				# ip, netmask, gateway
				self.config("netsh interface ip set address name=" + 
					eth_name + " static " + address + " " + network + " " + 
					gateway + " " + 1)
				# dns
				self.config("netsh interface ip set address name=" + 
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
		pass

	def config(self, cmd):
		self.cmds += cmd + "\n"

	def applySettings(self):
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
