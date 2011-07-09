from subprocess import Popen, PIPE
import shlex
from vmgLogging import *
import os

""" Execute external commands. """
log = logging.getLogger("vmgen.runCommands")

def executeCommand(command):
	""" 
		Execute command, and wait for its termination. 

		Return the exit code and the output of the command.
	"""
	args = shlex.split(command)
	log.debug("Executing command: " + command)
#	print "Execute: ", args
	p = Popen(args, stdout=PIPE)
	s = p.communicate()
	log.debug("\tReturn code: " + str(p.returncode))
	return (p.returncode, s[0])

	return (0, "")

def executeCommandSSH(command):
	""" 
		Execute command over ssh:
		- user_host: user and hostname
		- key: private key used for ssh authentication
	"""
		
	return executeCommand("ssh " + key + " " + user_host + " " + command)

def copyFilesToVM(files, host):
	src = ""
	for f in files:
		src += f + " "
	return executeCommand("scp " + key + " " + src + host + ":")

def copyFileToVM(f, host):
	return executeCommand("scp " + key + " " + f + " " + host + ":")

def copyFileFromVM(remotePath, localPath, host):
	return executeCommand("scp " + key + " " + host + ":" + remotePath + " " + localPath)

def setUserHost(s):
	global user_host
	user_host = s

user_host = "root@vmaster"
key = "-i vmaster_key.private"
