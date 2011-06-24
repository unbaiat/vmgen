from vmgInstallerBase import InstallerBase
from vmgLogging import *
import os
from runCommands import *

log = logging.getLogger("vmgen.vmgInstallerApt")

# checked for debian 5 & 6 and ubuntu 10.10
packages = {
	"mozilla-firefox" : { "package" : "iceweasel firefox" },
	"mozilla-thunderbird" : { "package" : "icedove thunderbird" },
	"google-chrome" : { "package" : "? chromium-browser" },	# requires repo for debian 5
	"pidgin" : { "package" : "pidgin" },
	"wireshark" : { "package" : "wireshark" },
	"ftp-server" : { "package" : "vsftpd" },
	"ftp-client" : { "package" : "ftp" },
	"httpd" : { "package" : "apache2" },
	"vim" : { "package" : "vim" },
	"python" : { "package" : "python" },
	"jdk" : { "package" : "openjdk-6-jdk openjsk-6-jre" },
	"mysql" : { "package" : "mysql-server" },
	"eclipse" : { "package" : "? eclipse" },	# debian repo?
	"emacs" : { "package" : "emacs" },
	"dynamips" : { "package" : "dynamips" },	# no repo for debian !?
	"traceroute" : { "package" : "traceroute" },
	"netcat" : { "package" : "netcat" },
	"tcpdump" : { "package" : "tcpdump" },
	"nmap" : { "package" : "nmap" },
	"build-utils" : { "package" : "build-essential" },
	"kernel-devel" : { "package" : "kernel-package" },
	"valgrind" : { "package" : "valgrind" },
	"openmp" : { "package" : "libgomp1 lib64gomp1" },
	"mpich2" : { "package" : "mpich2" },	# not in debian repo !! only mpich1
	"php" : { "package" : "php5" },
	"tcl" : { "package" : "tcl" },
	"mail-server" : { "package" : "postfix" },
	"dhcp-server" : { "package" : "dhcp3-server" },
	"dns-server" : { "package" : "bind9" },
	"sshd" : { "package" : "openssh-server" },
	"svn" : { "package" : "subversion" },
	"git" : { "package" : "git" },
	"mercurial" : { "package" : "mercurial" },
	"ntp" : { "package" : "ntp" },
	"snmp" : { "package" : "snmp" },
	"radius" : { "package" : "radiusclient1" },
	"squid" : { "package" : "squid" },
	"bittorrent" : { "package" : "bittorrent" }
}

install_cmd = " /usr/bin/apt-get install -y -q "

runners = {
	'vmware' : __executeVmware,
	'openvz' : __executeOpenvz,
	'lxc' : __executeLxc
}

class InstallerApt:
	def __init__(self, vmx, type, id=None, user=None, passwd=None, host=None):
		self.vmx = str(vmx)
		self.id = str(id)
		self.user = str(user)
		self.passwd = str(passwd)
		
		self.runCmd = runners[type]
		if host is not None:
			setUserHost(host)
		
	def __executeVmware(self, cmd):
		executeCommand("vmrun -t ws" + " -gu " + self.user + " -gp " + self.passwd + " runProgramInGuest " + self.vmx + " " + cmd)
	
	def __executeOpenvz(self, cmd):
		executeCommandSSH("vzctl enter " + self.id + " --exec " + cmd + ";logout")
		
	def __executeLxc(self, cmd):
		executeCommandSSH("lxc-execute -n " + self.id + " " + cmd)
		
	def install(self, programs):
		# Show warnings for unsupported programs
		errs = [p for p in programs if not p in packages]
		[log.warning("Invalid program: " + p) for p in errs]
		s = ["Invalid program: " + p for p in errs]
		print s

		# invalidate a line in sources.list that checks packages on cd-rom,
		# causing the installer to block
		self.runCmd("sed -i '/cdrom/s/^/# /' /etc/apt/sources.list")
		
		# Retrieve only the list of valid programs
		packs = [packages[p] for p in programs if p in packages]
		if packs:
			[self.runCmd(install_cmd + p['package']) for p in packs]
			
# Testing
vmx_path = "C:\Users\Arya\Documents\Virtual Machines\Debian-6"
vmx_file = "Debian-6.vmx"
vmx = "\"" + os.path.join(vmx_path, vmx_file) + "\""
installer = InstallerApt(vmx, 'vmware', user='root', passwd='student')
installer.install(['valgrind', 'httpd'])