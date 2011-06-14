from vmgInstallerBase import InstallerBase
from vmgLogging import *
import os
from runCommands import *

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
		"repo" : "path/to/google.repo" },	# requires repo in  /etc/yum.repos.d 
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
		"rpm" : "path/to/rpm"},	# TODO
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

local_cmd = " yum -y -d 0 -e 0 localinstall --nogpgcheck "
simple_cmd = " yum -y -d 0 -e 0 install "
group_cmd = " yum -y -d 0 -e 0 groupinstall "

class InstallerApt:
	def __init__(self, vmx, type, id=None, user=None, passwd=None, host=None):
		self.vmx = vmx
		if type == 'vmware':
			self.execute = executeCommand
			self.prefix = "vmrun -t ws" + " -gu " + user + " -gp " + passwd + " runProgramInGuest " + vmx
		if type == 'openvz':
			self.execute = executeCommandSSH
			self.prefix = "vzctl enter " + str(id) + " --exec"
		if type == 'lxc':
			self.execute = executeCommandSSH
			self.prefix = "lxc-execute -n " + str(id)

	def install(self, programs):
		# Show warnings for unsupported programs
		errs = [p for p in programs if not p in packages]
		[log.warning("Invalid program: " + p) for p in errs]
		s = ["Invalid program: " + p for p in errs]
		print s

		# Retrieve only the list of valid programs
		packs = [packages[p] for p in programs if p in packages]
		if packs:
			[self.execute(self.prefix + install_cmd + p['package']) for p in packs]
			for p in packs:
				if p['type'] == 'simple':
					self.execute(self.prefix + simple_cmd + p['package'])
				if p['type'] == 'group':
					self.execute(self.prefix + group_cmd + p['package'])
				if p['type'] == 'repo':
					# TODO: copy repo to /etc/yum.repos.d/
					self.execute(self.prefix + simple_cmd + p['package'])
				if p['type'] == 'local':
					# TODO: copy rpm to vm
					self.execute(self.prefix + local_cmd + p['rpm'])
					
# Testing
vmx_path = "C:\Users\Arya\Documents\Virtual Machines\Fedora-15"
vmx_file = "Fedora-15.vmx"
vmx = "\"" + os.path.join(vmx_path, vmx_file) + "\""
installer = InstallerYum(vmx, 'vmware', user='root', passwd='student')
installer.install(['valgrind', 'emacs'])