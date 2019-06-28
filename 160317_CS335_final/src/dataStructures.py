from config import *
# Creates IR table

class instruction3AC:
    def __init__(self, instr):

        print("Instruction: ", instr)
    	if (instr[3] in type_4):
    		insType = instr[3] 
    	else:
    		insType = instr[1]
        if instr[3] == '=':
            insType = '='
        print("insType", insType)
        # if not(insType in instr_types):
        #     raise ValueError('Instruction ' + insType + ' not defined')

        self.type = insType
        self.instr = ', '.join(i for i in instr)

        if insType in type_4:
            self.dst = instr[1]

            ST.insert(self.dst, "int")

            self.src1 = instr[2]
            self.src2 = instr[4]

        elif insType in type_3:
            if insType=='=':
                self.dst = instr[1]
            else:
                self.dst = instr[3]
            self.src1 = instr[4]

            # callint var_name function_name
            if (self.type == 'callint'):
                if ST.lookUp(self.src1):
                    ST.updateArgList(self.src1, "type", "func")
                else:
                    ST.insert(self.src1, "func")
            if (self.type != 'ifgoto'):
                ST.insert(self.dst, "int")


        elif insType in type_2:
            self.dst = instr[4]
            if(self.type == 'callvoid'):
                if ST.lookUp(self.dst):
                    ST.updateArgList(self.dst, "type", "func")
                else:
                    ST.insert(self.dst, "func")

            elif (self.type == 'label'):
                if ST.lookUp(self.dst) is False:
                    ST.insert(self.dst, "void")
     #        elif (self.type == 'printint'):
     #        	print("hellolllllllllll",self.dst)
     #        	if ST.lookUp(self.dst) is False:
					# ST.insert(self.dst, "printint")
					# print(ST.lookUp(self.dst))
            elif(self.type != 'goto'):
            	if ST.lookUp(self.dst) is False:
					ST.insert(self.dst, "int")
		else:
			print("Inside else: .....")

# Initializes addrDes
def createAddrDesc():
    table = ST.globalSymbolList
    for symbol in table:
        if ST.table[symbol]['type'] != 'void':
            addrDes[symbol] = {"register": None, "memory": False}
