from vmgInstallerBase import InstallerBase
from vmgLogging import *
import os

from runCommands import *

log = logging.getLogger("vmgen.vmgInstallerWindows")

# TODO rename the setups before running vmgen
# TODO copy the setups to the machine before installing
# TODO install multiple programs with one temp script
# TODO port to pyvix

vmx_path = "D:\My Documents 1\Virtual Machines\Windows XP Professional (base)"
vmx_file = "Windows XP Professional (base).vmx"
vmx = "\"" + os.path.join(vmx_path, vmx_file) + "\""

#common_prefix = "start /wait"
common_prefix = ""
inst = {
	"simple": {
		"prefix":common_prefix,
		"args":"/S"
	},
	"msi": {
		"prefix":common_prefix + " msiexec /qb /i",
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
		"setup-file":"" #TODO
	},
	"emacs":{
		"type":"script",
		"setup-file":"" #TODO
	}

}

class InstallerWindows(InstallerBase):
	def setUserPass(self, user, passwd):
		self.user = user
		self.passwd = passwd
		self.prefix = "vmrun -t ws" + " -gu " + self.user + " -gp " + self.passwd

	def setSetupFolder(self, folder):
		self.setupFolder = folder

	def getCommand(self, progName):
		prog = programs[progName]
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

	def install(self, prog):
		temp_file = "setup.bat"
		remote_temp_file = "\"" + self.setupFolder + temp_file + "\""

		# write the install command into a temp script file (.bat)
		with open(temp_file, "w") as f:
			f.write(self.getCommand(prog) + "\n")

		# copy the temp script file to the guest
		executeCommand(self.prefix + " copyFileFromHostToGuest " + vmx +
			" " + temp_file + " " + remote_temp_file)

		# execute the temp script on the guest
		executeCommand(self.prefix + " runProgramInGuest " + vmx +
			" -activeWindow " +	"cmd.exe " + "/C " + remote_temp_file)

		# remove the temp script file from the guest
		executeCommand(self.prefix + " deleteFileInGuest " + vmx + " " + 
			remote_temp_file)

		# remove the temp script from the local machine
		os.remove(temp_file)

