def writeNewLine(f):
	""" Write a new line in the file f. """
	f.write("\n")

def writeComment(f, text):
	""" Write text in the file f, as a comment. """
	f.write("# " + text + "\n")

def writeHeader(f, text):
	""" Write text in the file f, as the interpreter path. """
	f.write("#!" + text + "\n")

def writeOption(f, key, value, quotes=True):
	""" Write a line of the form "key = value" in the file f. """
	if quotes:
		value = '"' + value + '"'
	f.write(key + ' = ' + value + '\n')

def tryWriteOption(f, key, section, conf_key):
	""" 
		Check if there exists the key conf_key in section and if does, get the
		value of it and write a corresponding option line in the file f.
	"""
	if (section.contains(conf_key)):
		writeOption(f, key, section.get(conf_key))
