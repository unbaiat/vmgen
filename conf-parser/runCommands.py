from subprocess import Popen, PIPE
import shlex

def executeCommand(command):
	args = shlex.split(command)
	p = Popen(args, stdout=PIPE)
	s = p.communicate()
	print p.returncode
	return (p.returncode, s[0])

def executeCommandSSH(command):
	return executeCommand("ssh " + user + "@" + host + " " + command)

user = "root"
host = "vmaster"
