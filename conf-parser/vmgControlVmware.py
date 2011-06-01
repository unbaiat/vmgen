import pyvix.vix
from threading import Thread
import time

from runCommands import *

def connect_to_vm(vmx_path):
	"""Connect to the VmWare virtual machine specified by the
	vmx_path.

	Returns a pair: (a handle for the connection to the host, a
	virtual machine handle)"""


	try:
		# try defaults
		host = pyvix.vix.Host()
	except pyvix.vix.VIXException:
		print "error host"

	try:
		vm = host.openVM(vmx_path)
	except pyvix.vix.VIXException:
		print "error openVM"

	return (host, vm)


def _wait_for_tools(vm):
	"""Called by the thread that waits for the VMWare Tools to
	   start. If the Tools do not start, there is no direct way of
	   ending the Thread.  As a result, on powerOff(), the Thread
	   would throw a VIXException on account of the VM not being
	   powered on.
	"""
	try:
		vm.waitForToolsInGuest()
	except pyvix.vix.VIXException:
		pass


def wait_for_tools_with_timeout(vm, timeout):
	"""Wait for VMWare Tools to start.

	Returns True on success and False when the VMWare tools did not
	start properly in the given timeout. Writes error messages to
	`error_fname`.
	"""

	tools_thd = Thread(target = _wait_for_tools, args=(vm,))
	tools_thd.start()
	# normally the thread will end before the timeout expires, so a high timeout
	tools_thd.join(timeout)


	if not tools_thd.isAlive():
		return True

	return False


def power_on(vm):
	"""Powers on virtual machine and answers any input
	   messages that might appear. """
	# vm.powerOn()
	power_thd = Thread(target = vm.powerOn)
	power_thd.start()
	power_thd.join()

def try_power_on_vm(vmx_path):
	"""Power on the virtual machine taking care of possbile messages
	   and handle the case in which the virtual machine doesn't have
	   VMWare Tools installed or the username and password given are
	   wrong."""

	global host, vm

	tools_timeout = 120

	(host, vm) = connect_to_vm(vmx_path)

	power_on(vm)
	if not wait_for_tools_with_timeout(vm, tools_timeout):
		# no tools, nothing to do.
		return False

	time.sleep(5)
	return True
