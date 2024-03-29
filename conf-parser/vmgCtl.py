from configobj import ConfigObj
import sys

if len(sys.argv) != 3:
    print 'Usage: vmgCtl.py infile section.key=value'
else:
    # Load the initial data file and modifiy ot accordingly
    config = ConfigObj(infile=sys.argv[1], raise_errors=True, file_error=True)
    [path, value] = sys.argv[2].strip().split('=')
    sections = path.strip().split('.')
    root = config
    # Get to the right subsection
    for index in range(len(sections)-1):
        if sections[index] in root.keys() == False:
            root[sections[index]] = {}
        root = root[sections[index]]
    root[sections[-1]] = value
    # Update
    config.write(open(sys.argv[1], 'w'))
