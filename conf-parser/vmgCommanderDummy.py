from vmgCommanderBase import CommanderBase

class CommanderDummy(CommanderBase):
	def startVM(self):
		print "\nStarting the VM..."

	def shutdownVM(self):
		print "\nShutting down the VM..."

	def connectToVM(self):
		print "\nEstablishing connection to the VM..."

	def disconnectFromVM(self):
		print "\nTerminating connection to the VM..."

	def setupHardware(self):
		print "\nCreating the hardware configuration..."
		section = self.data.getSection("hardware")
		for k, v in section.items():
			print k, "=", v

	def setupOperatingSystem(self):
		print "\nInstalling the operating system..."

	def setupConfigurations(self):
		print "\nConfiguring system settings..."
		section = self.data.getSection("config")
		for k, v in section.items():
			print k, "=", v

	def setupNetwork(self):	
		print "\nSetting up the network configurations..."
		section = self.data.getSection("network")
		for k, v in section.items():
			print k, "=", v

	def setupUsers(self):
		print "\nAdding users..."
		section = self.data.getSection("users")
		for i, u in enumerate(section.get("users")):
			print "Add user #", i
			print "\tName: ", u["name"]
			print "\tPassword: ", u["passwd"]
			print "\tGroups: ", u["groups"]
			print "\tHome directory: ", u["directory"]
			print "\tPermissions: ", u["perm"]
	
	def setupServices(self):
		print "\nInstalling services..."
		section = self.data.getSection("services")
		self.installPrograms(section)

	def setupDeveloperTools(self):
		print "\nInstalling developer tools..."
		section = self.data.getSection("devel")
		self.installPrograms(section)

	def setupGuiTools(self):
		print "\nInstalling GUI tools..."
		section = self.data.getSection("gui")
		self.installPrograms(section)
	

