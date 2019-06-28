#!/usr/bin/env python
import input_ir
import blocks
import symbol
import nextUse
import genAsm
import codeGenerator
import dataStructures
from config import *

raw_ir = input_ir.dutta_input()

# Intitialize data structures to be used throught out the code - ir = [], declared in the config.py file.
for i in raw_ir:
    # Read each instruction of 3AC and set its type, dest, src1 and src2. The ST object is also updated.
    info_object = dataStructures.instruction3AC(i) # It is an object of class instruction3AC, its data fields mentioned above are used throughout the code.
    ir.append(info_object)

# addrDes{} initialized.
dataStructures.createAddrDesc()

# Intitialize the global variables, .S file created and .data section written with the help of ST object updated before.
genAsm.initializeGlobals()

# Find the block's - start and end index.
bbl = blocks.findBlocks()

# Code generation - CRUX - .text part of .S file
for x in bbl:
    # x is a tuple(start,end) both inclusive!
    # For each instruction, for each temporary, set its live value and nextUse.
    nextUseTable = nextUse.nextUseTable(x)
    codeGenerator.codeGen(x,nextUseTable)

print "nextUseTable: "
for i in nextUseTable:
    print "Instruction Number: ", i
    for j in nextUseTable[i]:
        # if nextUseTable[i][j]['live'] == True:
        print j, ":", nextUseTable[i][j]

if x[1]!=len(ir):
    print "one statement is missing!"
    if ir[-1].type == 'label':
        labelNumber = ir[-1].instr.split(',')[-1].strip()
        print "labelNumber", labelNumber
        genAsm.genLabel(labelNumber)

# Close the .S file
genAsm.closeFile()
print "WOOH"
