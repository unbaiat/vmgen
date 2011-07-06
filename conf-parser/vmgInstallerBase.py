"""
	Abstract base class for the application installers.
	Install the programs requested using a program installation method:
		- apt-get
		- yum
		- from sources
		- Windows installer
	Each concrete class corresponds to one of the above methods and has a
	dictionary to map the universal name for the program (from the .conf file)
	to the name used by the implemented method.
"""

class InstallerBase:
	def __init__(self):
		pass

	def install(self, programList):
		""" Install program. """
		pass
