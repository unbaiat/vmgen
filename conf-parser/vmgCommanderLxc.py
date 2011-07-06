from vmgCommanderBase import CommanderBase

from runCommands import *
import shutil
import os
import time
from vmgLogging import *
from writeFormat import *
from vmgControlVmware import *
from vmgUtils import *

""" Functions to write lines in a .vmx file. """
log = logging.getLogger("vmgen.vmgCommanderLxc")

"""	The distribution used for container creation parameters. """
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

""" Container operating system parameters. """
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

"""	The path in the VMware machine where the container is created. """
path = "/lxc"

class CommanderLxc(CommanderBase):

	def setupHardware(self):
		log.info("Creating the hardware configuration...")

		self.os = self.data.getSection("hardware").get("os")
		self.id = self.data.getSection("hardware").get("vm_id")

		# extract the os parameters from the config file
		os_type = os_params[self.os]["os"]
		ver = os_params[self.os]["version"]
		arch = os_params[self.os]["arch"]

		self.vm = distro[os_type]["vm"]
		self.host = distro[os_type]["hostname"]
		folder = distro[os_type]["scripts-folder"]
		script = distro[os_type]["script"]

		self.config = path + "/" + self.id + "/" + "config." + self.id

		# set the user and host used for the SSH connection
		setUserHost(self.host)

		# power on the auxiliary VMware machine
		log.info("\tStarting the virtual machine...")
		try_power_on_vm(self.vm)

		# set default root password
		passwd = "pass" 
		#self.data.getSection("config").get("root_passwd")

		# copy the needed scripts to the virtual machine
		log.info("\tCopying the scripts to the virtual machine...")
		files = os.listdir(folder)
		paths = [os.path.join(folder, f) for f in files]
		copyFilesToVM(paths, self.host)
		for f in files:
			executeCommandSSH("chmod a+x " + f)

		# create a temp file containing lines to be appended to the container
		# config file
		log.info("\tFilling up the network section in the config file...")
		temp_file = "eth.tmp"
		with open(temp_file, "w") as f:
			log.info("\Setting memory and CPUs...")
			section = self.data.getSection("hardware")
			ram = section.get("ram") + "M"
			num_cpu = int(section.get("num_cpu"))

			if num_cpu == 1:
				cpus = "0"
			else:
				cpus = "0" + "-" + str(num_cpu - 1)

			# TODO: the kernel needs support for the memory controller
			writeOption(f, "#lxc.cgroup.memory.limit_in_bytes", ram, False)
			writeOption(f, "lxc.cgroup.cpuset.cpus", cpus, False)

			# create network interfaces
			log.info("\tCreating the network interfaces...")
			self.eth_list = getSortedValues(section.get("eths").data)
			eth_config = getSortedValues(
					self.data.getSection("network").get("eths").data)
			for i, eth_pair in enumerate(zip(self.eth_list, eth_config)):
				i = str(i)
				eth, eth_c = eth_pair

				eth_name = eth.get("name")
				writeOption(f, "lxc.network.type", "veth", False)

				writeOption(f, "lxc.network.link", "br0", False)

				writeOption(f, "lxc.network.name", eth_name, False)
				writeOption(f, "lxc.network.mtu", "1500", False)

				# set IP address
				ip_type = eth_c.get("type")
				if ip_type == "static":
					ip = eth_c.get("address")
					mask = getNetmaskCIDR(eth_c.get("network"))
				else:
					ip = "0.0.0.0"
					mask = ""

				writeOption(f, "lxc.network.ipv4", ip+mask, False)

				if eth.contains("connected"):
					writeOption(f, "lxc.network.flags", "up", False)

				# set MAC address, if present
				mac = eth.get("hw_address")
				if mac:
					writeOption(f, "lxc.network.hwaddr", mac)

		# copy the temp file to the virtual machine
		copyFileToVM(temp_file, self.host)
		os.remove(temp_file)

		# run the script on the virtual machine, to create the container
		log.info("\tRun the container creation script...")
		executeCommandSSH("./" + script + " " + path + " " + self.id + " " + 
			ver + " " + arch + " " + passwd)


	def setupOperatingSystem(self):
		pass
		
	def startVM(self):
		""" Start the container. """
		log.info("\tStarting the container...")
		executeCommandSSH("pushd " + path)
		executeCommandSSH("lxc-create" + " -n " + self.id + " -f " + self.config)
#		executeCommandSSH("lxc-start" + " -n " + self.id + " -f " + self.config)

	def shutdownVM(self):
		""" Shutdown the container and the virtual machine. """
		log.info("\tStopping the container...")
#		executeCommandSSH("lxc-stop" + " -n " + self.id)
		executeCommandSSH("lxc-destroy" + " -n " + self.id)
		executeCommandSSH("shutdown -h now")

	def connectToVM(self):
		print "\nEstablishing connection to the VM..."

	def disconnectFromVM(self):
		print "\nTerminating connection to the VM..."

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
