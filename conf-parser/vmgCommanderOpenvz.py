from vmgCommanderBase import CommanderBase
from vmgInstallerDummy import InstallerDummy
from runCommands import *
from vmgLogging import *
from vmgControlVmware import *
import shutil
import os
import time

vm="/home/vmgen/vmware/Fedora-32/Fedora-32.vmx"
host="root@fedora-32"

log = logging.getLogger("vmgen.vmgCommanderOpenvz")

class CommanderOpenvz(CommanderBase):
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

			# TODO: interfaces
			#if section.contains("eths"):
			#	for k, v in section.get("eths").items():
			#		executeCommandSSH("vzctl set " + vm_id + " --netif_add " + k + ",,,,br0 --save")
			executeCommandSSH("vzctl set " + vm_id + " --ipadd " + 172.16.30.23 + " --save")
			
		except Exception as exc:
			log.error("Cannot complete hardware configuration: " + str(exc))

	def setupConfigurations(self):
		print "Configuring system settings..."
		section = self.data.getSection("config")
		#for k, v in section.items():
		#	print k, "=", v

	def setupNetwork(self):	
		print "Setting up the network configurations..."
		vm_id = self.data.getSection("hardware").get("vm_id")
		section = self.data.getSection("network")
		if section.contains('hostname'):
			executeCommandSSH("vzctl set " + vm_id + " --hostname " + section.get('hostname') + " --save")
		if section.contains('nameservers'):
			print section.get('nameservers')
			for k,v in section.get('nameservers').items():
				executeCommandSSH("vzctl set " + vm_id + " --nameserver " + v + " --save")
		
	def setupUsers(self):
		if self.data.contains("users") is False:
			log.debug("No users to add ...")
			return
		log.debug("Adding users ...")
		section = self.data.getSection("users")
		vm_id = self.data.getSection("hardware").get("vm_id")

		for i, u in enumerate(section.get("users")):
			if u.contains('name') is False:
				log.error("Cannot add user #" + str(i) + ": missing name")
				continue
			log.debug("Add user #" + str(i) + ": " + u['name'])

			# User name & password
			if u.contains('name') is False:
				log.error("Cannot add user #" + str(i) + ": missing password")
			executeCommandSSH("vzctl set " + vm_id + " --userpasswd " + u["name"] + ":" + u["passwd"])

			# User group
			if u.contains('group'):
				# make sure the group exists
				executeCommandSSH("vzctl exec groupadd " + u['group'])
				# set user group
				executeCommandSSH("vzctl exec usermod -g " + u['group'] + " " + u['name'])

			# User home directory
			if u.contains('home_dir'):
				executeCommandSSH("vzctl exec usermod -d " + u['home_dir'] + " " + u['name'])

			# TODO: User permissions
			if u.contains('perm'):
				print "\tPermissions: ", u["perm"]

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

