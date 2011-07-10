from vmgInstallerBase import InstallerBase
from vmgLogging import *
import os
from runCommands import *
from vmgCommunicatorBase import CommunicatorBase
from vmgCommunicatorVmware import CommunicatorVmware
from vmgCommunicatorOpenvz import CommunicatorOpenvz
from vmgCommunicatorLxc import CommunicatorLxc

log = logging.getLogger("vmgen.vmgInstallerYum")

# checked for fedora 14 & 15
packages = {
	"mozilla-firefox" : {
		"type" : "simple",
		"package" : "firefox" },
	"mozilla-thunderbird" : {
		"type" : "simple",
		"package" : "thunderbird" },
	"google-chrome" : {
		"type" : "repo",
		"package" : "google-chrome-stable",
		"repo" : "path/to/google.repo" },	# TODO: put the repo in svn and update valid path
	"pidgin" : {
		"type" : "simple",
		"package" : "pidgin" },
	"wireshark" : {
		"type" : "simple",
		"package" : "wireshark" },
	"ftp-server" : {
		"type" : "simple",
		"package" : "vsftpd" },
	"ftp-client" : {
		"type" : "simple",
		"package" : "ftp" },
	"httpd" : {
		"type" : "simple",
		"package" : "httpd" },
	"vim" : {
		"type" : "simple",
		"package" : "vim" },
	"python" : {
		"type" : "simple",
		"package" : "python" },
	"jdk" : {
		"type" : "simple",
		"package" : "java-1.6.0-openjdk" },
	"mysql" : {
		"type" : "simple",
		"package" : "mysql-server" },
	"eclipse" : {
		"type" : "simple",
		"package" : "eclipse" },
	"emacs" : {
		"type" : "simple",
		"package" : "emacs" },
	"dynamips" : {
		"type" : "local",
		"rpm" : "path/to/rpm"},	# TODO: put the rpm in the svn and update to a valid path
	"traceroute" : {
		"type" : "simple",
		"package" : "traceroute" },
	"netcat" : {
		"type" : "simple",
		"package" : "nc" },
	"tcpdump" : {
		"type" : "simple",
		"package" : "tcpdump" },
	"nmap" : {
		"type" : "simple",
		"package" : "nmap" },
	"build-utils" : {
		"type" : "group",
		"package" : "\"Development Tools\" \"Development Libraries\"" },
	"kernel-devel" : {
		"type" : "simple",
		"package" : "kernel-devel" },
	"valgrind" : {
		"type" : "simple",
		"package" : "valgrind" },
	"openmp" : {
		"type" : "simple",
		"package" : "libgomp" },
	"mpich2" : {
		"type" : "simple",
		"package" : "mpich2" },
	"php" : {
		"type" : "simple",
		"package" : "php" },
	"tcl" : {
		"type" : "simple",
		"package" : "tcl" },
	"mail-server" : {
		"type" : "simple",
		"package" : "postfix" },
	"dhcp-server" : {
		"type" : "simple",
		"package" : "dhcp" },
	"dns-server" : {
		"type" : "simple",
		"package" : "bind" },
	"sshd" : {
		"type" : "simple",
		"package" : "openssh-server" },
	"svn" : {
		"type" : "simple",
		"package" : "subversion" },
	"git" : {
		"type" : "simple",
		"package" : "git" },
	"mercurial" : {
		"type" : "simple",
		"package" : "mercurial" },
	"ntp" : {
		"type" : "simple",
		"package" : "ntp" },
	"snmp" : {
		"type" : "simple",
		"package" : "net-snmp" },
	"radius" : {
		"type" : "simple",
		"package" : "radiusclient-ng" },
	"squid" : {
		"type" : "simple",
		"package" : "squid" },
	"bittorrent" : {
		"type" : "simple",
		"package" : "bittorrent" }
}

local_cmd = " /usr/bin/yum -y -d 0 -e 0 localinstall --nogpgcheck "
simple_cmd = " /usr/bin/yum -y -d 0 -e 0 install "
group_cmd = " /usr/bin/yum -y -d 0 -e 0 groupinstall "

class InstallerYum:
	def __init__(self, comm):
		self.comm=comm
		
	def install(self, programs):
		# Show warnings for unsupported programs
		errs = [p for p in programs if not p in packages]
		[log.warning("Invalid program: " + p) for p in errs]
		s = ["Invalid program: " + p for p in errs]
		print s

		# Retrieve only the list of valid programs
		packs = [packages[p] for p in programs if p in packages]
		if packs:
			for p in packs:
				if p['type'] == 'simple':
					print 'run simple' + p['package']
					self.comm.runCommand(simple_cmd + p['package'])
				if p['type'] == 'group':
					self.comm.runCommand(group_cmd + p['package'])
				if p['type'] == 'repo':
					# copy repo file in container
					self.comm.copyFileToVM(p['repo'], "repo.repo")
					# do the stuff
					self.comm.runCommand(simple_cmd + p['package'])
				if p['type'] == 'local':
					# copy rpm to root
					self.comm.copyFileToVM(p['rpm'], ".")
					# execute
					self.comm.runCommand(local_cmd + p['package'])
					# remove rpm
					self.comm.runCommand("rm -rf *.rpm")
					
# Testing
#vmx_path = "C:\Users\Arya\Documents\Virtual Machines\Fedora-14"
#vmx_file = "Fedora-14.vmx"
#vmx = "\"" + os.path.join(vmx_path, vmx_file) + "\""
#comm_aux = CommunicatorVmware(vmx, 'root', 'student')
#installer = InstallerYum(comm_aux)
#installer.install(['valgrind', 'emacs'])