from vmgCommanderBase import CommanderBase
from vmgInstallerDummy import InstallerDummy
from runCommands import *
import shutil
import os
import time
from vmgLogging import *
from writeFormat import *
from vmgControlVmware import *
from vmgUtils import *


from vmgInstallerWindows import *
#from vmgInstallerApt import *
#from vmgInstallerYum import *

from vmgConfigWindows import *
#from vmgConfigLinux import *

from vmgCommunicatorVmware import *

""" Functions to write lines in a .vmx file. """
log = logging.getLogger("vmgen.vmgCommanderVmware")

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

aux_modules = {
#			"debian5-64":{ 
#				"config":ConfigLinux,
#				"installer":InstallerApt
#			},
#			"ubuntu-64":{
#				"config":ConfigLinux,
#				"installer":InstallerApt
#			},
			"windows7-64":{
				"config":ConfigWindows,
				"installer":InstallerWindows,
				"user":"Administrator",
				"passwd":"pass"
			},
			"winxppro":{
				"config":ConfigWindows,
				"installer":InstallerWindows,
				"user":"Administrator",
				"passwd":"pass"
			}
		}

class CommanderVmware(CommanderBase):
	def startVM(self):
		"""Override"""
		log.info("Starting the VM...")
		self.vm = try_power_on_vm(self.vmx_file)

	def shutdownVM(self):
		"""Override"""
		log.info("Shutting down the VM...")

	def connectToVM(self):
		"""Override"""
		log.info("Establishing connection to the VM...")

	def disconnectFromVM(self):
		"""Override"""
		log.info("Terminating connection to the VM...")
		power_off_vm(self.vm)

	def setupHardware(self):
		"""Override"""
		log.info("Creating the hardware configuration...")
		section = self.data.getSection("hardware")
		self.os = section.get("os")
		self.id = section.get("vm_id")
		self.vmx_file = new_machine_dir + self.id + ".vmx"

		self.communicator = CommunicatorVmware(self.vmx_file, 
				aux_modules[self.os]["user"], aux_modules[self.os]["passwd"])

		shutil.rmtree(new_machine_dir)
		os.makedirs(new_machine_dir)

		with open(self.vmx_file, "w") as f:
			# write header in the .vmx file
			writeHeader(f, "/usr/bin/vmware")
			writeOption(f, "config.version", "8")
			writeOption(f, "virtualHW.version", "7")
			tryWriteOption(f, "guestOs", section, "os")
			writeOption(f, "displayName", self.id)
			tryWriteOption(f, "numvcpus", section, "num_cpu")
			tryWriteOption(f, "memsize", section, "ram")
			writeNewLine(f)
			
			# create hard disks
			log.info("\tCreating the hard disks...")
			self.hdds = []
			writeComment(f, "hard-disk")
			self.hdd_list = getSortedValues(section.get("hdds").data)
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

				self.hdds.append(hdd_name)

			writeNewLine(f)

			# create cd drives
			log.info("\tCreating the cd-drives...")
			writeComment(f, "cd-rom")
			self.cd_list = getSortedValues(section.get("cd_drives").data)
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
			self.eth_list = getSortedValues(section.get("eths").data)
			for i, eth in enumerate(self.eth_list):
				i = str(i)
				eth_name = "ethernet" + i
				eth_type = eth.get("type")
				writeOption(f, eth_name + ".present", "TRUE")
				#writeOption(f, eth_name + ".virtualDev", "e1000")
				writeOption(f, eth_name + ".connectionType", eth_type)
				tryWriteOption(f, eth_name + ".startConnected", eth, 
						"connected")

				# set the MAC address (if present)
				mac = eth.get("hw_addr")
				if mac:
					writeOption(f, eth_name + ".addressType", "static")
					writeOption(f, eth_name + ".address", mac)
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
		shutil.copy2(vmaster_vmx_orig, vmaster_vmx)
		with open(vmaster_vmx, "a") as f:
			# attach the base_system hdd
			disk_name = base_install_dir + base_disks[self.os]["name"]
			disk_type = base_disks[self.os]["type"]

			if disk_type == "ide":
				prefix = "ide0:0"
			else:
				prefix = "scsi0:1"

			writeOption(f, prefix + ".present", "TRUE")
			writeOption(f, prefix + ".fileName", disk_name)
			for i, hdd in enumerate(self.hdd_list):
				hdd_type = hdd.get("type")
				if hdd_type == "scsi":
					hdd_pos = "0:" + str(i + 2)
				else:
					hdd_pos = "0:" + str(i + 1)
				writeOption(f, hdd_type+hdd_pos + ".present", "TRUE")
				writeOption(f, hdd_type+hdd_pos + ".fileName", 
						new_machine_dir + hdd.get("name"))

		# start VMaster
		log.info("\tPowering up the VMaster machine...")
		self.vmaster = try_power_on_vm(vmaster_vmx)

		# setup the partitions
		log.info("\tPartitioning the new disks...")
		for i, hdd in enumerate(self.hdd_list):
			hdd_name = "/dev/sd" + chr(ord("c") + i)
			i = str(i)
			idx_primary = 0
			idx_logical = 4
			last_off = 1
			executeCommandSSH("parted -s " + hdd_name + " mklabel msdos")
			self.part_list = getSortedValues(hdd.get("partitions").data)
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
			uuid_old = executeCommandSSH('blkid /dev/sdb1')[1].split('"')[1]
			executeCommandSSH("tune2fs -U " + uuid_old + " /dev/sdc1")

		log.info("\tUpdate the MBR on the new system disk...")
		# setup the MBR on the new system
		if base_disks[self.os]["mbr"] == "grub2":
			# GRUB2
			executeCommandSSH("grub-setup -d /mnt/new_hdd/boot/grub /dev/sdc")
		else:
			# Windows or GRUB1
			executeCommandSSH("dd if=/dev/sdb of=/dev/sdc bs=446 count=1")

		power_off_vm(self.vmaster)
#		executeCommandSSH("shutdown -h now")

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

	def createArchive(self):
		cwd = os.getcwd()
		os.chdir(new_machine_dir)
		files = self.id + ".vmx"
		for d in self.hdds:
			files += " " + d

		arch_name = self.id + ".zip"

		executeCommand("zip -r " + arch_name + " " + files)

		os.chdir(cwd)

		log.info("Archive " + arch_name + " was created.")
		return [arch_name, new_machine_dir]

	def getConfigInstance(self):
		config = aux_modules[self.os]["config"]
		if issubclass(config, ConfigWindows):
			return config(self.data, self.communicator)
		elif issubclass(config, ConfigLinux):
			# return config(self.comm)
			return None

		return None

	def getInstallerInstance(self):
		installer = aux_modules[self.os]["installer"]
		if issubclass(installer, InstallerWindows):
			return installer(self.communicator, "C:\\", "kits/")
		elif issubclass(installer, InstallerApt):
			# return InstallerApt(self.comm)
			return None
		elif issubclass(installer, InstallerYum):
			# return InstallerYum(self.comm)
			return None

		return None
	
	def getModuleName(self):
		return "vmware"
