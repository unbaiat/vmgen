from vmgCommanderBase import CommanderBase
from vmgInstallerDummy import InstallerDummy
from runCommands import *
import shutil
import os
import time

class CommanderOpenvz(CommanderBase):
	def startVM(self):
		print "\nStarting the VM..."
		try:
                        start_cmd = "vzctl start " + section.get("vm_id")
                        executeCommand(start_cmd)
                except Exception:
                        print "Cannot start container"

	def shutdownVM(self):
		print "\nShutting down the VM..."
		try:
                        stop_cmd = "vzctl stop " + section.get("vm_id")
                        executeCommand(stop_cmd)
                except Exception:
                        print "Cannot stop container"

	def connectToVM(self):
		print "\nEstablishing connection to the VM..."

	def disconnectFromVM(self):
		print "\nTerminating connection to the VM..."

	def setupHardware(self):
		print "\nCreating the hardware configuration..."
		section = self.data.getSection("hardware")

                try:
                        # create container
                        vm_id = section.get("vm_id")
                        create_cmd = "vzctl create " + vm_id
                        create_cmd += " --ostemplate " + section.get("os")
                        executeCommand(create_cmd)
                        # set container parameters
                        setup_cmd = "vzctl set " + vm_id
                        # cpu numbers
                        executeCommand(setup_cmd + " --numproc " + section.get("num_cpu"))
                        # memory size
                        # TODO: recheck this
                        executeCommand(setup_cmd + " --vmguargpages " + section.get("ram"))
                        # harddisk size: get the size of the first entry in hdd list
                        hdd = section.get("hdds").values[0]
                        executeCommand(setup_cmd + " --diskspace " + hdd.get("size"))
                        # interfaces
                except Exception:
                        print "Cannot setup hardware"
		
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
			print "Add user #"+i
			print "\tName: ", u["name"]
			print "\tPassword: ", u["passwd"]
			print "\tGroup: ", u["group"]
			print "\tHome directory: ", u["home_dir"]
			print "\tPermissions: ", u["perm"]
                        adduser = "vzctl set " + section.get("vm_id")
                        adduser += " --userpasswd " + u["name"] + ":" + u["passwd"]
                        executeCommand(adduser)
	
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
	
