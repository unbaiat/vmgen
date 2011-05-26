from vmgCommanderBase import CommanderBase

from runCommands import *
import shutil
import os
import time
from vmgLogging import *

log = logging.getLogger("vmgen.vmgCommanderLxc")

distro = {
	"debian":{
		"vm":"/home/vmgen/vmware/Debian (lxc)/Debian (lxc).vmx",
		"hostname":"root@debian-lxc",
		"script":"my-lxc-debian.sh",
		"scripts-folder":"../scripts-lxc/debian/"},
	"fedora":{
		"vm":"/home/vmgen/vmware/Fedora 64-bit/Fedora 64-bit.vmx",
		"hostname":"root@fedora-lxc",
		"script":"my-lxc-fedora.sh",
		"scripts-folder":"../scripts-lxc/fedora/"}
}

os_params = { 
		"fedora-64":{
			"os":"fedora",
			"version":"14", 
			"arch":"amd64"},
		"fedora":{
			"os":"fedora",
			"version":"14", 
			"arch":"x86"},
		"debian5-64":{
			"os":"debian",
			"version":"lenny", 
			"arch":"amd64"},
		"debian5":{
			"os":"debian",
			"version":"lenny", 
			"arch":"x86"},
}

path = "/lxc"

class CommanderLxc(CommanderBase):

	def setupHardware(self):
		self.os = self.data.getSection("hardware").get("os")
		self.id = self.data.getSection("hardware").get("vm_id")

		os_type = os_params[self.os]["os"]
		ver = os_params[self.os]["version"]
		arch = os_params[self.os]["arch"]

		self.vm = distro[os_type]["vm"]
		self.host = distro[os_type]["hostname"]
		folder = distro[os_type]["scripts-folder"]
		script = distro[os_type]["script"]

		self.config = path + "/" + self.id + "/" + "config." + self.id

		setUserHost(self.host)

		executeCommand("vmrun start " + '"' + self.vm + '"')
##		time.sleep(30)

		# TODO: get root passwd
		passwd = "pass"

		files = os.listdir(folder)
		paths = [os.path.join(folder, f) for f in files]
		 
		print files
		copyFilesToVM(paths, self.host)

		for f in files:
			executeCommandSSH("chmod a+x " + f)

		executeCommandSSH("./" + script + " " + path + " " + self.id + " " + 
			ver + " " + arch + " " + passwd)

	def setupOperatingSystem(self):
		pass
		
	def startVM(self):
		executeCommandSSH("lxc-create" + " -n " + self.id + " -f " + self.config)
		executeCommandSSH("lxc-start" + " -n " + self.id + " -f " + self.config)

	def shutdownVM(self):
		executeCommandSSH("lxc-stop" + " -n " + self.id)
		executeCommandSSH("lxc-destroy" + " -n " + self.id)
#		executeCommandSSH("shutdown -h now")

	def connectToVM(self):
		print "\nEstablishing connection to the VM..."

	def disconnectFromVM(self):
		print "\nTerminating connection to the VM..."

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
	

