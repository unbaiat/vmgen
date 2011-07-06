import socket
import struct

def getSortedValues(d):
	return [d[k] for k in sorted(d.iterkeys())]

def getNetmaskCIDR(mask):
	n = socket.ntohl(struct.unpack("I", socket.inet_aton("255.255.255.0"))[0])
	return "/" + str(len([b for b in bin(n)[2:] if b is '1']))

def splitList(s):
	return s.replace(" ", "").split(",")
