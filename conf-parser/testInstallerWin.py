from vmgInstallerWindows import *

vmx_path = "D:\My Documents 1\Virtual Machines\Windows XP Professional (base)"
vmx_file = "Windows XP Professional (base).vmx"
vmx = "\"" + os.path.join(vmx_path, vmx_file) + "\""


i = InstallerWindows(vmx, "vmgen", "pass", "e:\\")
#i.install(["mozilla-thunderbird", "pidgin", "python"])
i.install(["mozilla-thunderbird", "pidgin2", "python3"])
