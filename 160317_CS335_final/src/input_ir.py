import os
import sys

# Returns error if file doesn't exists, else returns a list of list that is already parsed


def dutta_input():

    # if (len(sys.argv) != 2):
    #     raise LookupError("Please enter only 1 file name as input!")
    # fileName = 'test/test4.go'

    # if (not os.path.isfile(fileName)):
    #     raise LookupError("File doesn't exists!")
    fileName = 'ThreeAdressCode.csv'
    lines = tuple(open(fileName, 'r'))
    toRet = []

    for x in lines:
        appendList = x.strip().split(",")
        for i in range(len(appendList)):
            appendList[i] = appendList[i].replace(" ", "")
        toRet.append(appendList)

    return toRet
