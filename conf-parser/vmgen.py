#!/usr/bin/env python

import sys
from vmgParser import vmgParser
import vmgLogging
import posix_ipc

from vmgCommanderVmware import CommanderVmware
from vmgCommanderOpenvz import CommanderOpenvz
from vmgCommanderLxc import CommanderLxc

cmdSwitch = {   'vmware' : CommanderVmware,
				'openvz' : CommanderOpenvz,
				'lxc' : CommanderLxc
}

def main(vmtype, infile):
	# init logger
	vmgLogging.initLogging()

	# init semaphore
	sem_name = "/" + vmtype
	sem = posix_ipc.Semaphore(sem_name, flags = posix_ipc.O_CREAT,
			initial_value = 1)
	# acquire exclusive lock on the commander
	print "Requesting exclusive access to the commander..."
	sem.acquire()
	print "Exclusive access granted"

	# call parser
	parser = vmgParser(infile)
	parser.parse()
	dumpFile = "[" + vmtype + "]" + infile + ".dump"
	parser.dump(dumpFile)

	# call commander
	try:
		cmd = cmdSwitch[vmtype](dumpFile)
	except Exception as e:
		print "Cannot create commander: ", e

	try:
		cmd.setupVM()
	except Exception as e:
		print "Error creating the machine: ", e

	# release the exclusive lock
	sem.release()
	print "Lock released."
	sem.close()


if __name__ == '__main__':
	if len(sys.argv) != 3:
		print 'Usage: vmgen.py [vmware|openvz|lxc] infile'
	else:
		main(sys.argv[1], sys.argv[2])
