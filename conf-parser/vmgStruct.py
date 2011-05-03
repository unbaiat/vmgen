import pickle

class vmgSection:
    '''
        Defines a section of the config file.
        The pairs (key, value) are stored in a dictionary.
        Use contains and get to access data.
    '''
    def __init__(self, sectionName, sectionDict):
        self.name = sectionName
        self.data = sectionDict

    def __stringRepr(self, tab):
        '''
            String representation of the current section.
            Used internally for the actual print function.
            '''
        s = self.name + ":\n"
        for k,v in self.data.items():
            if type(v) is str:
                s += tab + str(k) + " = " + str(v)
            else:
                s += tab + v.__stringRepr(tab + "\t")
            s += "\n"
        return s

    def __str__(self):
        return self.__stringRepr("\t")
        
    def contains(self, keyName):
        return keyName in self.data.keys()
       
    def get(self, keyName):
        if self.contains(keyName) == False:
            return None
        return self.data[keyName]

    def items(self):
        '''
            Retrieve the data dictionary.
            '''
	return self.data.items()
    

class vmgStruct:
    '''
        Defines the structure containing the entire data from the
        config file as a dictionary of sections.
    '''
    def __init__(self, dataDict):
        self.data = dataDict

    def __str__(self):
        res = ""
        for s in self.data.values():
            res += str(s)
        return res

    def contains(self, section, option):
        try:
            return self.data[section].contains(option)
        except KeyError, ValueError:
            return False

    def getSection(self, section):
        try:
            return self.data[section]
        except KeyError, ValueError:
            return None

    def get(self, section, option):
        try:
            return self.data[section].get(option)
        except KeyError, ValueError:
            return None
       
    def dump(self, dumpFile):
        '''
            Dump the serialized representation of the data
            in a specified file
        '''
        with open(dumpFile, 'wb') as f:
            pickle.dump(self, f)
        f.close()

    def dumps(self):
        '''
            Return the serialized representation of the data
            as a string instead of writing to a file
        '''
        return pickle.dumps(self)
