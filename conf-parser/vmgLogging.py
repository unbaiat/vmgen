import logging

def initLogging():
#	FORMAT = '%(levelname)-8s: %(name)-15s: %(message)s'
	FORMAT = '%(levelname)-8s: %(message)s'
	logging.basicConfig(format=FORMAT)

	log = logging.getLogger("vmgen")
	log.setLevel(logging.DEBUG)
#	log.setLevel(logging.INFO)

#log = logging.getLogger("test")
#log.warning("testing")
#
#
#log1 = logging.getLogger("test.abc")
#log1.error("testing 2")
