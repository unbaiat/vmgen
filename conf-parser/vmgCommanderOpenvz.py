from vmgCommanderBase import CommanderBase
from vmgCommunicatorOpenvz import *
from vmgInstallerDummy import InstallerDummy
from runCommands import *
from vmgLogging import *
from vmgControlVmware import *
import shutil
import os
import time

vm="/home/vmgen/vmware/Fedora-32/Fedora-32.vmx"
host="root@fedora-32"
script_folder="../scripts-openvz/"
get_template="get_template.sh"

log = logging.getLogger("vmgen.vmgCommanderOpenvz")

installer = {
	'debian' : InstallerApt,
	'ubuntu' : InstallerApt,
	'fedora' : InstallerYum
}

class CommanderOpenvz(CommanderBase):
	def __init__(self):
		vm_id = self.data.getSection("hardware").get("vm_id")
		connParam = { 	'vmx' : vm,
						'host' : host,
						'id' : vm_id
					}
		self.comm = CommunicatorOpenvz(connParam)

	def startVM(self):
		try:
			vm_id = self.data.getSection("hardware").get("vm_id")
			log.debug("Start container ...")
			executeCommandSSH("vzctl start " + vm_id)
		except Exception:
			log.error("Cannot start container ...")

	def shutdownVM(self):
		try:
			vm_id = self.data.getSection("hardware").get("vm_id")
			log.debug("Stop container ...")
			executeCommandSSH("vzctl stop " + vm_id)
			# Build archive and retrieve it
			executeCommandSSH("tar czf fs.tar $VZDIR/private/" + vm_id)
			executeCommandSSH("tar czf " + vm_id + ".tar /etc/vz/conf/" + vm_id + ".conf fs.tar")
			copyFileFromVM(vm_id + ".tar", host)
			#log.debug("Destroy container ...")
			#executeCommandSSH("vzctl destroy " + vm_id)
		except Exception as exc:
			log.error("Cannot stop container: " + str(exc))

	def connectToVM(self):
		print "Establishing connection to the VM..."

	def disconnectFromVM(self):
		print "Terminating connection to the VM..."

	def setupHardware(self):
		log.debug("Creating the hardware configuration...")
		try:
			section = self.data.getSection("hardware")
			vm_id = section.get("vm_id")
			setup_cmd = "vzctl set " + vm_id

			# set the user and host used for the SSH connection
			setUserHost(host)

			# power on VMware machine
			log.debug("\tStarting the virtual machine...")
			try_power_on_vm(vm)

			# run script in vm to retrieve template
			paths = [ os.path.join(script_folder, get_template) ]
			print paths
			copyFilesToVM(paths, host)
			executeCommandSSH("chmod a+x " + get_template)
			executeCommandSSH("./" + get_template + " -t " + section.get("os"))
			
			# create container
			log.debug("Create container ...")
			executeCommandSSH("vzctl create " + vm_id + " --ostemplate " + section.get("os"))

			# start container to apply settings
			self.startVM()

			# cpu number
			if section.contains("num_cpu"):
				executeCommandSSH(setup_cmd + " --cpus " + section.get("num_cpu") + " --save")

			# memory size
			if section.contains("ram"):
				executeCommandSSH(setup_cmd + " --privvmpages " + section.get("ram") + ":" + section.get("ram") + " --save")

			# harddisk size: get the size of the first entry in hdd list
			if section.contains("hdds"):
				diskspace = section.get("hdds").items()[0][1].get("size")
				executeCommandSSH(setup_cmd + " --diskspace " + diskspace + ":" + diskspace + " --save")

			# interfaces
			if section.contains("eths"):
				for k, v in section.get("eths").items():
					executeCommandSSH("vzctl stop " + vm_id)
					executeCommandSSH(setup_cmd + " --netif_add " + k + " --save")
					self.startVM()

					# TODO: add this to a script to run at container start
					# on host vm
					executeCommandSSH("echo 1 > /proc/sys/net/ipv4/conf/veth" + vm_id + ".0/forwarding")
					executeCommandSSH("echo 1 > /proc/sys/net/ipv4/conf/veth" + vm_id + ".0/proxy_arp")
					executeCommandSSH("echo 1 > /proc/sys/net/ipv4/conf/" + k + "/forwarding")
					executeCommandSSH("echo 1 > /proc/sys/net/ipv4/conf/" + k + "/proxy_arp")
					executeCommandSSH("ip r add " + "192.168.0.123" + " dev veth" + vm_id + ".0")
					
					# in container
					executeCommandSSH("vzctl exec " + vm_id + " ip link set dev " + k + " up")
					executeCommandSSH("vzctl exec " + vm_id + " ip a add " + "192.168.0.123" + " dev " + k)
					executeCommandSSH("vzctl exec " + vm_id + " ip r add default dev " + k)
					
			# simple venet interface
			executeCommandSSH("vzctl set " + vm_id + " --ipadd " + 172.16.30.23 + " --save")
			
		except Exception as exc:
			log.error("Cannot complete hardware configuration: " + str(exc))

	def setupServices(self):
		print "Installing services..."
		section = self.data.getSection("services")
		#self.installPrograms(section)

	def setupDeveloperTools(self):
		print "Installing developer tools..."
		section = self.data.getSection("devel")
		#self.installPrograms(section)

	def setupGuiTools(self):
		print "Installing GUI tools..."
		section = self.data.getSection("gui")
		#self.installPrograms(section)

	def getConfigInstance(self):
		return ConfigLinux(self.data, self.comm)

	def getInstallerInstance(self):
		vm_id = self.data.getSection("hardware").get("vm_id")
		for k in installer.keys():
			if str(k) in vm_id:
				return installer[k](self.comm)
		return None