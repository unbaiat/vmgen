from vmgConfigBase import ConfigBase
from runCommands import *
from os import *

class ConfigLinux(ConfigBase, communicator):
	def __init__(self, data, comm):
		self.data = data
		self.cmds = ""
		self.comm = comm
	
	def setupSystem(self):
		""" 
			Setup:
			- the hostname
			- the administrator password
		"""

		section = self.data.getSection("config")

		# set hostname
		hostname = section.get("hostname")
		self.config("sysctl kernel.hostname=\"" + hostname + "\"")

		# set Administrator password
		rootPasswd = section.get("root_passwd")
		self.config("echo " + rootPasswd + " | passwd --stdin root")

	def setupGroups(self):
		""" Create groups. """
		section = self.data.getSection("users")
		groups = section.get("groups").data.values()
		for group in groups:
			group_name = group.get("name")
			self.config("groupadd " + group_name)

	def setupUsers(self):
		""" Create groups. """
		section = self.data.getSection("users")
		users = section.get("users").data.values()
		for user in users:
			name = user.get("name")
			passwd = user.get("passwd")

			# create the user
			groups = ""
			if len(user.get('groups')) > 0:
				groups = "-G " + ", ".join(user.get('groups'))
			self.config("useradd " + groups + " " + name)
			
			# hmm
			self.config("echo " + passwd + " | passwd --stdin " + name)

	def setupNetwork(self):
		section = self.data.getSection('network')
		nameservers = section.getSection('nameservers')
		# nameservers
		# clear the current nameservers
		self.comm.runCommand("echo \" \" > /etc/resolv.conf")
		for ns in nameservers.data.values():
			self.config("echo nameserver " + ns + " >> /etc/resolv.conf")
			
		# gateway
		gateway = section.get('gateway')
		self.config("ip route del default")
		self.config("ip route add default via " + gateway)
		
		self.eth_list = section.get('eths').data.values()
		for i, eth in enumerate(self.eth_list):
			type = eth.get('type')
			if type == 'static':
				# static addresses
				hw_address = eth.get('hw_addr')
				address = eth.get('address')
				network = eth.get('network')

				# ip
				self.config("ip addr add " + address + " dev " + i)
				# mac
				self.config("ip link set dev " + i + " address " + hw_address)
				# TODO: netmask
			if type == 'dhcp':
				hw_address = eth.get('hw_addr')
				# mac
				self.config("ip link set dev " + i + " address " + hw_address)
				# TODO: config eth to dhcp (edit /etc/network/interfaces)

	def setupFirewall(self):
		""" Setup the open ports in the firewall. """
		section = self.data.getSection("network")
		ports = section.get("open_ports").data.values()
		for port in ports:
			proto = port.get("proto")
			port_num = port.get("port")
			desc = port.get("description")

			# create the rule
			self.config("iptables -A INPUT -p " + proto + " --sport " + port_num + " -m state --state NEW,ESTABLISHED -j ACCEPT")
			
		extra_rules = section.get('firewall_rules').data.values()
		for rule in extra_rules:
			self.config(rule)

	def config(self, cmd):
		self.cmds += cmd + "\n"

	def applySettings(self):
		print self.cmds

		temp_file = "config.sh"

		# write the install command into a temp script file (.bat)
		with open(temp_file, "w") as f:
			f.write(self.cmds)

		# copy the temp script file to the guest
		self.comm.copyFileToVM(temp_file, temp_file)

		# execute the temp script on the guest
		self.comm.runCommand("./" + temp_file)

		# remove the temp script file from the guest
		self.comm.deleteFileInGuest(temp_file)

		# remove the temp script from the local machine
		os.remove(temp_file)