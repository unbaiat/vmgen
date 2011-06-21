from vmgConfigWindows import *
from vmgParser import *
import os
import pickle

vmx_path = "D:\My Documents 1\Virtual Machines\Windows XP Professional (base)"
vmx_file = "Windows XP Professional (base).vmx"
vmx = "\"" + os.path.join(vmx_path, vmx_file) + "\""

conf_file = "sample-winxp.conf"

# call parser
parser = vmgParser(conf_file)
parser.parse()
dumpFile = conf_file + '.dump'
parser.dump(dumpFile)

with open(dumpFile, 'rb') as f:
	data = pickle.load(f)

c = ConfigWindows(data, vmx)
c.setupConfig()
