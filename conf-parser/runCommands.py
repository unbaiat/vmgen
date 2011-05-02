from subprocess import Popen, PIPE
import shlex

""" Execute external commands. """

def executeCommand(command):
	""" 
		Execute command, and wait for its termination. 

		Return the exit code and the output of the command.
	"""
	args = shlex.split(command)
	print "Execute: ", args
	p = Popen(args, stdout=PIPE)
	s = p.communicate()
	print p.returncode
	return (p.returncode, s[0])

def executeCommandSSH(command):
	""" 
		Execute command over ssh:
		- user_host: user and hostname
		- key: private key used for ssh authentication
	"""
		
	return executeCommand("ssh " + key + " " + user_host + " " + command)

user_host = "root@vmaster"
key = "-i vmaster_key.private"
