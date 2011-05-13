from vmgCommanderBase import CommanderBase
from vmgInstallerDummy import InstallerDummy
from runCommands import *
import shutil
import os
import time
from vmgLogging import *

""" Functions to write lines in a .vmx file. """
log = logging.getLogger("vmgen.vmgCommanderVmware")

def writeNewLine(f):
	""" Write a new line in the file f. """
	f.write("\n")

def writeComment(f, text):
	""" Write text in the file f, as a comment. """
	f.write("# " + text + "\n")

def writeHeader(f, text):
	""" Write text in the file f, as the interpreter path. """
	f.write("#!" + text + "\n")

def writeOption(f, key, value):
	""" Write a line of the form "key = value" in the file f. """
	f.write(key + ' = "' + value + '"\n')

def tryWriteOption(f, key, section, conf_key):
	""" 
		Check if there exists the key conf_key in section and if does, get the
		value of it and write a corresponding option line in the file f.
	"""
	if (section.contains(conf_key)):
		writeOption(f, key, section.get(conf_key))

#vmaster_vmx_orig = "F:\\Virtual Machines\\VMaster\\VMaster.vmx"
#vmaster_vmx = "F:\\Virtual Machines\\VMaster\\VMaster_modified.vmx"
#base_install_dir = "F:\\Virtual Machines\\so-vm-linux-neon\\so_gentoo\\"
#new_machine_dir = os.getcwd() + "\\"
""" Path to the original VMaster machine. """
vmaster_vmx_orig = "/home/vmgen/VMaster/VMaster.vmx"

""" Path to the modified VMaster machine. """
vmaster_vmx = "/home/vmgen/VMaster/VMaster_modified.vmx"

""" Path where the base installations are stored. """
base_install_dir = "/iso-images/"

""" Path where the created machines are stored. """
new_machine_dir = os.getcwd() + "/machines/"

"""
	Filesystem utilities parameters:
	- executable name
	- fdisk filesystem ID
"""
mkfs = { 
		"ntfs":{
			"cmd":"mkfs.ntfs", 
			"id":"7"},
		"ext2":{
			"cmd":"mkfs.ext2",
			"id":"83"},
		"ext3":{
			"cmd":"mkfs.ext3",
			"id":"83"},
		"ext4":{
			"cmd":"mkfs.ext4",
			"id":"83"},
		"swap":{
			"cmd":"mkswap",
			"id":"82"}
		}

""" 
	Base installations parameters:
	- disk name
	- disk type (ide, SCSI LsiLogic, SCSI LsiSas1068, ...)
	- MBR (Grub2, Grub, Windows, ...
	- filesystem (ntfs, ext3, ext4, ...)
"""
base_disks = {
			"debian5-64":{ 
				"name":"so_gentoo.vmdk",
				"type":"lsilogic",
				"mbr":"grub2",
				"fs":"ext4"},
			"ubuntu-64":{
				"name":"ubuntu-64.vmdk",
				"type":"lsilogic",
				"mbr":"grub2",
				"fs":"ext4"},
			"windows7-64":{
				"name":"Win7-64.vmdk",
				"type":"lsisas1068",
				"mbr":"win",
				"fs":"ntfs"},
			"winxppro":{
				"name":"WinXP.vmdk",
				"type":"ide",
				"mbr":"win",
				"fs":"ntfs"}
			}

class CommanderVmware(CommanderBase):
	def startVM(self):
		"""Override"""
		log.info("Starting the VM...")

	def shutdownVM(self):
		"""Override"""
		log.info("Shutting down the VM...")

	def connectToVM(self):
		"""Override"""
		log.info("Establishing connection to the VM...")

	def disconnectFromVM(self):
		"""Override"""
		log.info("Terminating connection to the VM...")

	def setupHardware(self):
		"""Override"""
		log.info("Creating the hardware configuration...")
		section = self.data.getSection("hardware")
		self.os = section.get("os")
		vmx_file = new_machine_dir + "machine.vmx"
		with open(vmx_file, "w") as f:
			# write header in the .vmx file
			writeHeader(f, "/usr/bin/vmware")
			writeOption(f, "config.version", "8")
			writeOption(f, "virtualHW.version", "7")
			tryWriteOption(f, "guestOs", section, "os")
			tryWriteOption(f, "displayName", section, "vm_id")
			tryWriteOption(f, "numvcpus", section, "num_cpu")
			tryWriteOption(f, "memsize", section, "ram")
			writeNewLine(f)
			
			# create hard disks
			log.info("\tCreating the hard disks...")
			writeComment(f, "hard-disk")
			self.hdd_list = section.get("hdds").data.values()
			for hdd in self.hdd_list:
				hdd_type = hdd.get("type")
				if hdd_type == "scsi":
					# only for scsi
					adapter = disk_type = base_disks[self.os]["type"]
					hdd_idx = hdd.get("scsi_index")
					writeOption(f, hdd_type+hdd_idx + ".present", "TRUE")
					writeOption(f, hdd_type+hdd_idx + ".virtualDev", adapter)
				else:
					adapter = "ide"

				hdd_size = hdd.get("size")
				hdd_pos = hdd.get("pos")
				hdd_name = hdd.get("name")
				writeOption(f, hdd_type+hdd_pos + ".present", "TRUE")
				writeOption(f, hdd_type+hdd_pos + ".fileName", hdd_name)

				executeCommand("vmware-vdiskmanager -c -s " + hdd_size +
						" -a " + adapter + " -t 0 " + 
						new_machine_dir + hdd_name)

			writeNewLine(f)

			# create cd drives
			log.info("\tCreating the cd-drives...")
			writeComment(f, "cd-rom")
			self.cd_list = section.get("cd_drives").data.values()
			for cd in self.cd_list:
				cd_type = "ide"
				cd_pos = cd.get("pos")
				cd_path = cd.get("path")
				writeOption(f, cd_type+cd_pos + ".present", "TRUE")
				writeOption(f, cd_type+cd_pos + ".deviceType", "cdrom-image")
				writeOption(f, cd_type+cd_pos + ".fileName", cd_path)
				tryWriteOption(f, cd_type+cd_pos + ".startConnected", cd, 
						"connected")
			writeNewLine(f)

			# create network interfaces
			log.info("\tCreating the network interfaces...")
			writeComment(f, "ethernet")
			self.eth_list = section.get("eths").data.values()
			for i, eth in enumerate(self.eth_list):
				i = str(i)
				eth_name = "ethernet" + i
				eth_type = eth.get("type")
				writeOption(f, eth_name + ".present", "TRUE")
				writeOption(f, eth_name + ".virtualDev", "e1000")
				writeOption(f, eth_name + ".connectionType", eth_type)
				tryWriteOption(f, eth_name + ".startConnected", eth, 
						"connected")
			writeNewLine(f)

			# create pci-bridges to be able to add more devices
			writeComment(f, "pci-bridges")
			writeOption(f, "pciBridge1.present", "TRUE");
			writeOption(f, "pciBridge1.virtualDev", "pcieRootPort");
			writeNewLine(f)

			writeComment(f, "auto generated by VMware")

	def setupPartitions(self):
		"""Override"""
		# attach the hdds to VMaster
		log.info("\tAttach the new hard disks to the VMaster...")
##		shutil.copy2(vmaster_vmx_orig, vmaster_vmx)
##		with open(vmaster_vmx, "a") as f:
##			# attach the base_system hdd
##			disk_name = base_install_dir + base_disks[self.os]["name"]
##			disk_type = base_disks[self.os]["type"]
##
##			if disk_type == "ide":
##				prefix = "ide0:0"
##			else:
##				prefix = "scsi0:1"
##
##			writeOption(f, prefix + ".present", "TRUE")
##			writeOption(f, prefix + ".fileName", disk_name)
##			for i, hdd in enumerate(self.hdd_list):
##				hdd_type = hdd.get("type")
##				if hdd_type == "scsi":
##					hdd_pos = "0:" + str(i + 2)
##				else:
##					hdd_pos = "0:" + str(i + 1)
##				writeOption(f, hdd_type+hdd_pos + ".present", "TRUE")
##				writeOption(f, hdd_type+hdd_pos + ".fileName", 
##						new_machine_dir + hdd.get("name"))

		# start VMaster
		log.info("\tPowering up the VMaster machine...")
		executeCommand("vmrun start " + '"' + vmaster_vmx + '"')
##		time.sleep(30)

		# setup the partitions
		log.info("\tPartitioning the new disks...")
		for i, hdd in enumerate(self.hdd_list):
			hdd_name = "/dev/sd" + chr(ord("c") + i)
			i = str(i)
			idx_primary = 0
			idx_logical = 4
			last_off = 1
			executeCommandSSH("parted -s " + hdd_name + " mklabel msdos")
			self.part_list = hdd.get("partitions").data.values()
			for j, part in enumerate(self.part_list):
				# create partitions
				j = str(j)
				part_size = int(part.get("size"))
				part_type = part.get("type")

				# update the next index
				if part_type == "primary" or part_type == "extended":
					idx_primary += 1
					crt_idx = idx_primary
				elif part_type == "logical":
					idx_logical += 1
					crt_idx = idx_logical

				executeCommandSSH("parted -s " + hdd_name + " mkpart " + 
						part_type + " " + str(last_off) + " " + 
						str(last_off + part_size))

				executeCommandSSH("hdparm -z " + hdd_name)

				if part_type != "extended":
					last_off += part_size
					part_fs = part.get("fs")
					executeCommandSSH("sfdisk --change-id " + hdd_name + " "
							+ str(crt_idx) + " " + mkfs[part_fs]["id"])
					executeCommandSSH(mkfs[part_fs]["cmd"] + " " + hdd_name 
							+ str(crt_idx))


	def setupOperatingSystem(self):
		"""Override"""
		log.info("Installing the operating system...")
		executeCommandSSH("parted -s /dev/sdc set 1 boot on")
		log.info("\tCloning the base system partition...")
		if base_disks[self.os]["fs"] == "ntfs":
			# ntfs
			executeCommandSSH("ntfsclone --overwrite /dev/sdc1 /dev/sdb1")
			executeCommandSSH("ntfsresize --force /dev/sdc1")
		else:
			# other (ext*)
			executeCommandSSH("mount /dev/sdb1 /mnt/old_hdd")
			executeCommandSSH("mount /dev/sdc1 /mnt/new_hdd")
			executeCommandSSH("cp -ax /mnt/old_hdd/* /mnt/new_hdd/")

			# clone the UUID of the base partition to the new one
			uuid_old = "aa" #executeCommandSSH('blkid /dev/sdb1')[1].split('"')[1]
			executeCommandSSH("tune2fs -U " + uuid_old + " /dev/sdc1")

		log.info("\tUpdate the MBR on the new system disk...")
		# setup the MBR on the new system
		if base_disks[self.os]["mbr"] == "grub2":
			# GRUB2
			executeCommandSSH("grub-setup -d /mnt/new_hdd/boot/grub /dev/sdc")
		else:
			# Windows or GRUB1
			executeCommandSSH("dd if=/dev/sdb of=/dev/sdc bs=446 count=1")
		
		

	def setupConfigurations(self):
		"""Override"""
		log.info("Configuring system settings...")
		section = self.data.getSection("config")
		for k, v in section.items():
			log.info(str(k) + "=" + str(v))

	def setupNetwork(self):	
		"""Override"""
		log.info("Setting up the network configurations...")
		section = self.data.getSection("network")
		for k, v in section.items():
			log.info(str(k) + "=" + str(v))

	def setupUsers(self):
		"""Override"""
		log.info("Adding users...")
		section = self.data.getSection("users")
		for i, u in enumerate(section.get("users")):
			log.info("Add user #"+i)
			log.info("\tName: " + u["name"])
			log.info("\tPassword: ", u["passwd"])
			log.info("\tGroup: " + u["group"])
			log.info("\tHome directory: " + u["home_dir"])
			log.info("\tPermissions: " + u["perm"])
	
	def setupServices(self):
		"""Override"""
		log.info("Installing services...")
		section = self.data.getSection("services")
		self.installPrograms(section)

	def setupDeveloperTools(self):
		"""Override"""
		log.info("Installing developer tools...")
		section = self.data.getSection("devel")
		self.installPrograms(section)

	def setupGuiTools(self):
		"""Override"""
		log.info("Installing GUI tools...")
		section = self.data.getSection("gui")
		self.installPrograms(section)
	
