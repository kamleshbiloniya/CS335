
class symbolTable:

    def __init__(self, tableno):
        self.table = {}
        self.globalSymbolList = []
        self.parent = None
        self.extra = {}
        self.tableno = tableno

    def setwidth(self, name, value):
        # update the attribute "width" of the variable:
        if value == "int":
            (self.table)[name]["width"] = 4
        elif value == "float":
            (self.table)[name]["width"] = 8
        elif value == "string":
            if "value" in (self.table)[name]:
                (self.table)[name]["width"] = len((self.table)[name]["value"])
            else:
                (self.table)[name]["width"] = 0
        elif value == "bool":
            (self.table)[name]["width"] = 1
        else:
            (self.table)[name]["width"] = 0

    def maxoffset(self, name):
        # Find the max offset of the current symbol table
        maxoffset = 0
        for k in (self.table):
            # traverse the current symbol table, i.e. for each identifier present in the sybol table
            if k!=name:
                maxoffset = max(maxoffset,(self.table)[k]["offset"])
        return maxoffset

    # Checks whether "name" lies in the symbol table
    def lookUp(self, name):
        return (name in self.table)

    # Inserts if already not present
    def insert(self, name, typeOf):
        if (not self.lookUp(name)):
            (self.table)[name] = {}
            self.globalSymbolList.append(name)
            (self.table)[name]["type"] = typeOf
            self.setwidth(name,typeOf)
            (self.table)[name]["offset"] = self.maxoffset(name) + (self.table)[name]["width"]

    # Returns the argument list of the variable else returns None
    # Note that type is always a key in argument list
    def getInfo(self, name):
        if(self.lookUp(name)):
            return (self.table)[name]
        return None

    # Updates the variable of NAME name with arg list of KEY key with VALUE value
    def updateArgList(self, name, key, value):
        if (self.lookUp(name)):
            (self.table)[name][key] = value
            if key == "type":
                self.setwidth(name,value)
                (self.table)[name]["offset"] = self.maxoffset(name) + self.table[name]["width"]
        else:
            raise KeyError("Symbol " + name + " doesn't exists - Cant Update")


    def setParent(self, parent):
        self.parent = parent

    def updateExtra(self,key,value):
        self.extra[key]=value
