wmic COMPUTERSYSTEM where name="gigi" call rename "xp-gen"
net user Administrator pass2
net localgroup vmg /ADD
net localgroup julius /ADD
net user caesar alesia /ADD
net localgroup julius caesar /ADD
net user vv pass /ADD
net localgroup vmg vv /ADD
netsh interface ip set address name="Local Area Connection" static 192.168.1.2 255.255.255.0 192.168.1.1 1
netsh interface ip set dns name="Local Area Connection" static 192.168.1.254 primary
netsh firewall add portopening tcp 22 ssh
netsh firewall add portopening all 65000 myport
PAUSE
