from subprocess import Popen, PIPE
import shlex

def executeCommand(command):
	args = shlex.split(command)
	print "Execute: ", args
	p = Popen(args, stdout=PIPE)
	s = p.communicate()
	print p.returncode
	return (p.returncode, s[0])

def executeCommandSSH(command):
	return executeCommand("ssh " + key + " " + user_host + " " + command)

user_host = "root@vmaster"
key = "-i vmaster_key.private"
