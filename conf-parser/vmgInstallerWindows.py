from vmgInstallerBase import InstallerBase
from vmgLogging import *
import os
from zipfile import ZipFile

from runCommands import *

log = logging.getLogger("vmgen.vmgInstallerWindows")

# TODO rename the setups before running vmgen
# TODO port to pyvix

#common_prefix = "start /wait"
common_prefix = ""
install_archive_script = "archive-install.bat"
inst = {
	"simple": {
		"prefix":common_prefix,
		"args":"/S"
	},
	"msi": {
		"prefix":common_prefix + " msiexec /qb /i",
		"args":""
	},
	"script": {
		"prefix":"cmd.exe /C " + install_archive_script,
		"args":""
	}
}

programs = {
	"mozilla-firefox": {
		"type":"simple",
		"setup-file":"FirefoxSetup.exe",
		"args":"-ms"
	},
	"mozilla-thunderbird": {
		"type":"simple",
		"setup-file":"ThunderbirdSetup.exe",
		"args":"-ms"
	},
	"google-chrome": {
		"type":"msi",
		"setup-file":"GoogleChromeStandaloneEnterprise.msi"
	},
	"pidgin": {
		"type":"simple",
		"setup-file":"pidgin-setup.exe",
		"args":"/DS=1 /SMS=0 /L=1033 /S"
	},
	"wireshark":{
		"type":"simple",
		"setup-file":"wireshark-setup.exe"
	},
	"ftp-server":{
		"type":"simple",
		"setup-file":"FileZillaServer-setup.exe"
	},
	"ftp-client":{
		"type":"simple",
		"setup-file":"FileZillaClient-setup.exe"
	},
	"httpd":{
		"type":"msi",
		"setup-file":"httpd-setup.msi"
	},
	"vim":{
		"type":"simple",
		"setup-file":"gvim-setup.exe"
	},
	"python":{
		"type":"msi",
		"setup-file":"python-setup.msi"
	},
	"jdk":{
		"type":"simple",
		"setup-file":"jdk-setup.exe",
		"args":"/quiet /passive"
	},
	"mysql":{
		"type":"msi",
		"setup-file":"mysql-setup.msi"
	},
	"eclipse":{
		"type":"script",
		"setup-file":"eclipse.zip"
	},
	"emacs":{
		"type":"script",
		"setup-file":"emacs.zip"
	}

}

class InstallerWindows(InstallerBase):
	def __init__(self, communicator, setupFolder, localFolder):
		InstallerBase.__init__(self, communicator)
		self.setupFolder = setupFolder
		self.localFolder = localFolder


	def getCommand(self, prog):
		type = prog["type"]
		file = self.setupFolder + prog["setup-file"]
		print file
		try:
			args = prog["args"]
		except Exception:
			args = inst[type]["args"]
			
		cmd = inst[type]["prefix"] + " " + file + " " + args
		print cmd

		return cmd

	def makeArchive(self, archName, files):
		# TODO: not working in python 2.6 (2.7 required)
		# with ZipFile(archName, 'w') as myzip:
		myzip = ZipFile(archName, 'w')
		[myzip.write(f) for f in files]
		myzip.close()

	def getExtractArchiveCmd(self, archName):
		# TODO: add type dictionary? (zip, 7z)
		return "7z.exe x -y -o" + self.setupFolder + " " + archName

	def getRemoveCommand(self, fileName):
		# TODO: add type?
		return "del " + fileName

	def getRemotePath(self, fileName):
		return "\"" + self.setupFolder + fileName + "\""

	def install(self, progList):
		cwd = os.getcwd()
		os.chdir(self.localFolder)
		# print warnings for the unsupported programs and ignore them
		errProgs = [p for p in progList if not p in programs]
		[log.warning("Invalid program: " + p) for p in errProgs]
		s = ["Invalid program: " + p for p in errProgs]
		print s

		# get the list of valid programs and proceed only if it is not empty
		progs = [programs[p] for p in progList if p in programs]
		if progs:
			temp_file = "setup.bat"
			remote_temp_file = self.getRemotePath(temp_file)
			arch_file = "setup.zip"
			remote_arch_file = self.getRemotePath(arch_file)

			remote_install_archive = self.getRemotePath(install_archive_script)

			# create an archive file with the needed installers
			files = [p["setup-file"] for p in progs]
			self.makeArchive(arch_file, files)

			# write the install command into a temp script file (.bat)
			with open(temp_file, "w") as f:
				# add the current folder to the PATH
				f.write("set PATH=%PATH%;" + self.setupFolder + "\n")

				# extract the archive
				f.write(self.getExtractArchiveCmd(remote_arch_file) + "\n")

				# remove the archive file
				f.write(self.getRemoveCommand(remote_arch_file) + "\n")

				# execute the installers
				[f.write(self.getCommand(p) + "\n") for p in progs]
				
				# remove the installers
				[f.write(self.getRemoveCommand(
					self.getRemotePath(ff) + "\n")) for ff in files]

				# remove the install-archive script
				f.write(self.getRemoveCommand(remote_install_archive) + "\n")

#				f.write("PAUSE\n")

			# copy the archive-install script file to the guest
			self.communicator.copyFileFromHostToGuest(install_archive_script,
					remote_install_archive)

			# copy the temp script file to the guest
			self.communicator.copyFileFromHostToGuest(arch_file, 
					remote_arch_file)

			# copy the temp script file to the guest
			# execute the temp script on the guest
			# remove the temp script file from the guest
			# remove the temp script from the local machine
			self.communicator.fileCopyRunDelete(temp_file, remote_temp_file,
					"cmd.exe /C ")

			# remove the archive file from the local machine
			os.remove(arch_file)

		os.chdir(cwd)
