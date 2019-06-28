import ply.yacc as yacc
import sys
import os
from symbol import symbolTable
from lexer import *
from lexer import MyLex as mylex
from pprint import pprint
tokens=mylex.tokens
from lexer import token_t
import csv
from gtts import gTTS
language = 'en'
# ----------------------SYMBOL TABLE---------------------
scopeDict = {}   # scopeDict - dictionary - used to store all symbolTables of different scopes.
scopeDict[0] = symbolTable(0) # First entry is the main scope.
scopeStack = [0] # scopeStack - the top points to the current stack.
currScope = 0
scopeSeq = 0
varSeq = 0      # Used in keeping track of temporary variables created by compiler
firstFunc = True
labelSeq = 1    # Used in keeping track of labels generated
ifcount = 1
forcount = 1
labelDict = {}

def tell_him_error(msg):
    global language
    myobj = gTTS(text=msg, lang=language, slow=False)
    print(msg)
    myobj.save("error.mp3")
    os.system("mpg321 error.mp3")
    

def checkLineNo(pos,op):
    # print(pos,op)
    if pos+op in token_t:
        return token_t[pos+op]
    elif pos-op in token_t:
        return token_t[pos-op]
    else:
        return checkLineNo(pos,op+1)
def checkId(identifier, typeOf):
    if typeOf == "global":
        if scopeDict[0].getInfo(identifier) is not None:
            return True
        return False

    if typeOf == "*":
        if scopeDict[currScope].getInfo(identifier) is not None:
            return True
        return False

    if typeOf == "label":
    	if scopeDict[0].getInfo(identifier) is not None:
    		return True
    	return False

    if typeOf == "*!s":
        if scopeDict[currScope].getInfo(identifier) is not None:
            info = scopeDict[currScope].getInfo(identifier)
            if info['type'] != ('type'+identifier):
                return True
        return False

    for scope in scopeStack[::-1]:
        if scopeDict[scope].getInfo(identifier) is not None:
            info = scopeDict[scope].getInfo(identifier)
            if typeOf == "**" or info['type'] == typeOf:
                return True

    return False

def addScope(name=None):
    """New scope added and its parent tracked"""
    try:
        global scopeSeq
        global currScope
        scopeSeq += 1
        lastScope = currScope
        currScope = scopeSeq
        scopeStack.append(currScope)
        scopeDict[currScope] = symbolTable(currScope)
        scopeDict[currScope].setParent(lastScope)
        if name is not None:
            if type(name) is list:
                scopeDict[lastScope].insert(name[1], 'func')
                scopeDict[lastScope].updateArgList(name[1], 'child', scopeDict[currScope])
            else:
                temp = currScope
                currScope = lastScope
                if checkId(name, '*'):
                    pos = p.lexer.lexpos
                    line = checkLineNo(pos,0)
                    print("Name " + name + " already defined....",line)
                    return
                currScope = temp
                scopeDict[lastScope].insert(name, 'type'+name)
                scopeDict[lastScope].updateArgList(name, 'child', scopeDict[currScope])
        pass
    except Exception as e:
        print("WARNING:1:"+str(e))
        return


def deleteScope():
    """Last element from scopeStack is removed and currScope is updated"""
    global currScope
    scopeStack.pop()
    currScope = scopeStack[-1]

def newTemp():
    """generates new temporary variable"""
    global varSeq
    toRet = 'var'+str(varSeq)
    varSeq += 1
    scopeDict[currScope].insert(toRet,"temporary")
    return toRet

def newLabel():
    """generates new label"""
    global labelSeq
    toret = 'label' + str(labelSeq)
    labelSeq += 1
    return toret

def newFor():
    global forcount
    toret = 'for'+str(forcount)
    forcount += 1
    return toret
def newIf():
    global ifcount
    toret = 'if'+str(ifcount)
    ifcount += 1
    return toret

def findInfo(name, Scope=-1):
    if Scope > -1:
        if scopeDict[Scope].getInfo(name) is not None:
            return scopeDict[Scope].getInfo(name)
        else:
            print("Identifier " + name + " is not defined! from info")
            return
        # raise NameError("Identifier " + name + " is not defined! from info")

    for scope in scopeStack[::-1]:  #list=[1,2,3,4,5] list[::-1]=[5,4,3,2,1]
        if scopeDict[scope].getInfo(name) is not None:
            info = scopeDict[scope].getInfo(name)
            return info
    print("Identifier " + name + " is not defined! from info")
    return
    # raise NameError("Identifier " + name + " is not defined! from info")

def findScope(name):
    for scope in scopeStack[::-1]:
        if  scopeDict[scope].getInfo(name) is not None:
            return scope
    print("Identifier " + name + " is not defined! scope")
    return
    # raise NameError("Identifier " + name + " is not defined! scope")

def findLabel(name):
    for scope in scopeStack[::-1]:
        if name in scopeDict[scope].extra:
            return scopeDict[scope].extra[name]
    print("Not in any loop scope label")
    return
	# raise ValueError("Not in any loop scope label")

# ------------------------------------------------------
precedence = (
    ('right','ASSIGN', 'NOT'),
    ('left', 'LOGICAL_OR'),
    ('left', 'LOGICAL_AND'),
    ('left', 'OR'),
    ('left', 'XOR'),
    ('left', 'AND'),
    ('left', 'EQUALS', 'NOT_ASSIGN'),
    ('left', 'LESSER', 'GREATER','LESS_EQUALS','MORE_EQUALS'),
    ('left', 'LSHIFT', 'RSHIFT'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'STAR', 'DIVIDE','MOD')
)

# ------------- IR GENERATION -----------

class Node:
    def __init__(self):
        self.idList = []
        self.code = []
        self.typeList = []
        self.placeList = []
        self.valueList = []
        # extra{} is the dictionary of labels/attributes, any grammar symbol can have any number of labels/attributes.
        # Some of them will be used as labels.
        self.extra = {}
# --------------------------------------------------------
rootNode = None
csvData = []
# csvData.append([' TableId ', ' Identifier ', ' place ', ' type ', ' value ', ' width ', ' offset ', ' childTableId ', 'parentTableId'])
def traverse(t,space_count):
    for i in range(space_count):
        print(" "),
    print("------------------------------------")
    for x in t.table:
        # data = [str(t.tableno), x, ' ', ' ', ' ', ' ', ' ', ' ', str(t.parent)]
        # print "identifier: ", x
        # print "tableId:    ", t.tableno
        # print "parent:     ", t.parent

        if 'child' in t.table[x]:
            for i in range(space_count):
                print(" "),
            print("-> It has a child: ", x)
            # data[7] = t.table[x]['child'].tableno
            print(" ")
            traverse(t.table[x]['child'],space_count+5)
        else:
            for i in range(space_count):
                print(" "),
            print(x, ":", t.table[x])
        #     if "place" in t.table[x]:
        #         # print "place:      ", t.table[x]['place']
        #         data[2] = t.table[x]['place']
        #     if "type" in t.table[x]:
        #         # print "type:       ", t.table[x]['type']
        #         data[3] = t.table[x]['type']
        #     if "value" in t.table[x]:
        #         # print "value:      ", t.table[x]['value']
        #         data[4] = t.table[x]['value']
        #     if "width" in t.table[x]:
        #         # print "width:      ", t.table[x]['width']
        #         data[5] = t.table[x]['width']
        #     if "offset" in t.table[x]:
        #         # print "offset:     ", t.table[x]['offset']
        #         data[6] = t.table[x]['offset']
        # csvData.append(data)
    for i in range(space_count):
        print(" "),
    print("------------------------------------")

# ------------------------START----------------------------
def p_start(p):
    '''start : SourceFile'''
    p[0] = p[1]
    global rootNode
    rootNode = p[0]
    space_count = 0
    # for i in scopeDict:
        # print "haha: ", i, scopeDict[i]
    traverse(scopeDict[0],0)
    # with open('symbolTable.csv', mode='w') as csvFile:
    #     writer = csv.writer(csvFile)
    #     writer.writerows(csvData)
    # csvFile.close()
# -------------------------------------------------------
# -----------------------TYPES---------------------------
def p_type(p):
    '''Type : TypeName
            | TypeLit
            | LPAREN Type RPAREN'''
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = p[1]

def p_type_name(p):
    '''TypeName : TypeToken
                | QualifiedIdent'''
    p[0] = p[1]

def p_type_token(p):
    '''TypeToken : INT
                 | FLOAT
                 | UINT
                 | COMPLEX
                 | RUNE
                 | BOOL
                 | STRING
                 | TYPE IDENTIFIER'''
    if len(p) == 2:
        p[0] = Node()
        p[0].typeList.append(p[1])
    else:
        if not checkId(p[2], '**'):
            pos = p.lexer.lexpos
            line = checkLineNo(pos,0)
            print("ERROR::Typename " + p[2] + " not defined... line no ",line)
            return
            # raise TypeError("Typename " + p[2] + " not defined")
        try:
            p[0] = Node()
            info = findInfo(p[2], 0)
            # print info['type']
            p[0].typeList.append(info['type'])
            pass
        except Exception as e:
            print("WARNING:66:" + str(e))

def p_type_lit(p):
    '''TypeLit : ArrayType
               | StructType
               | PointerType'''
    p[0] = p[1]

def p_type_opt(p):
    '''TypeOpt : Type
               | epsilon'''
    p[0] = p[1]
# -------------------------------------------------------
# ------------------- ARRAY TYPE -------------------------
def p_array_type(p):
  '''ArrayType : LSQUARE ArrayLength RSQUARE ElementType'''
  try:
      # print("hello here", p[-1].idList[0])
      p[0] = Node()
      p[0].code = p[2].code
      p[0].typeList.append("*" + p[4].typeList[0])
      scopeDict[currScope].updateArgList(p[-1].idList[0],'size',p[2].placeList[0])
      pass
  except Exception as e:
      print("WARNING:2:"+str(e))
      return

def p_array_length(p):
  ''' ArrayLength : Expression '''
  pos = p.lexer.lexpos
  line = checkLineNo(pos,0)
  if p[1].typeList[0][3:] != 'int':
    message = "Array Length must be integer.....Near Line no " + str(line)
    print(message)
    tell_him_error(message)
    return
  p[0] = p[1]

def p_element_type(p):
  ''' ElementType : Type '''
  p[0] = p[1]

# --------------------------------------------------------
# ----------------- STRUCT TYPE ---------------------------
def p_struct_type(p):
  '''StructType : CreateFuncScope STRUCT LCURL FieldDeclRep RCURL EndScope'''
  try:
      p[0] = p[4]
      info = findInfo(p[-1], 0)
      p[0].typeList = [info['type']]
      pass
  except Exception as e:
      print("WARNING:3:"+str(e))
      return

def p_field_decl_rep(p):
  ''' FieldDeclRep : FieldDeclRep FieldDecl SemiColonOpt
                  | epsilon '''
  try:
      if len(p) == 4:
        # Useless for now
        p[0] = p[1]
        p[0].idList += p[2].idList
        p[0].typeList += p[2].typeList
      else:
        p[0] = p[1]
      # pass
  except Exception as e:
      print("WARNING:4:"+str(e))
      return

def p_field_decl(p):
  ''' FieldDecl : IdentifierList Type'''
  try:
      p[0] = p[1]
      for i in p[0].idList:
        scopeDict[currScope].updateArgList(i, 'type', p[2].typeList[0])
      pass
  except Exception as e:
      print("WARNING:5:"+str(e))
      return
# ---------------------------------------------------------
# ------------------POINTER TYPES--------------------------
def p_point_type(p):
    '''PointerType : STAR BaseType'''
    try:
        p[0] = p[2]
        p[0].typeList[0] = "*"+p[0].typeList[0]
        pass
    except Exception as e:
        print("WARNING:6:"+str(e))
        return

def p_base_type(p):
    '''BaseType : Type'''
    p[0] = p[1]
# ---------------------------------------------------------
# ---------------FUNCTION TYPES----------------------------
#TODO recursion
def p_sign(p):
    '''Signature : Parameters TypeOpt'''
    try:
        p[0] = p[1]

        scopeDict[0].insert(p[-2][1],'signatureType')

        if len(p[2].typeList) == 0:
            scopeDict[0].updateArgList(p[-2][1], 'retType', 'void')
            # print "func name1 ",p[-2][1]
        else:
            scopeDict[0].updateArgList(p[-2][1], 'retType', p[2].typeList[0])
            # print "func name2 ",p[-2][1]

        info = findInfo(p[-2][1],0)
        scopeDict[0].updateArgList(p[-2][1],'num_param',len(p[1].idList))
        # print "yooooooooooo",p[-2][1],len(p[1].idList)
        if 'label' not in info:
            labeln = newLabel()
            scopeDict[0].updateArgList(p[-2][1], 'label', labeln)
            scopeDict[0].updateArgList(p[-2][1], 'child', scopeDict[currScope])
        pass
    except Exception as e:
        print("WARNING:7:"+str(e))
        return



def p_params(p):
    '''Parameters : LPAREN ParameterListOpt RPAREN'''
    p[0] = p[2]

def p_param_list_opt(p):
    '''ParameterListOpt : ParametersList
                             | epsilon'''
    p[0] = p[1]

def p_param_list(p):
    '''ParametersList : ParameterDecl
                      | ParameterDeclCommaRep'''
    p[0] = p[1]

def p_param_decl_comma_rep(p):
    '''ParameterDeclCommaRep : ParameterDeclCommaRep COMMA ParameterDecl
                             | ParameterDecl COMMA ParameterDecl'''
    try:
        p[0] = p[1]
        p[0].idList += p[3].idList
        p[0].typeList += p[3].typeList
        p[0].placeList += p[3].placeList
        pass
    except Exception as e:
        print("WARNING:8:"+str(e))
        return

def p_param_decl(p):
    '''ParameterDecl : IdentifierList Type
                     | Type'''
    try:
        if len(p) == 3:
            p[0] = p[1]
            for x in p[1].idList:
                scopeDict[currScope].updateArgList(x, 'type', p[2].typeList[0])
                p[0].typeList.append(p[2].typeList[0])
        else:
            p[0] = p[1]
        pass
    except Exception as e:
        print("WARNING:9:"+str(e))
        return
# ---------------------------------------------------------
#-----------------------BLOCKS---------------------------
def p_block(p):
    '''Block : LCURL StatementList RCURL'''
    p[0] = p[2]

def p_stat_list(p):
    '''StatementList : StatementRep'''
    p[0] = p[1]

def p_stat_rep(p):
    '''StatementRep : StatementRep Statement SemiColonOpt
                    | epsilon'''
    if len(p) == 4:
        try:
            p[0] = p[1]
            p[0].code += p[2].code
            pass
        except Exception as e:
            print("WARNING:67:"+str(e))
            pass
    else:
        p[0] = p[1]
# -------------------------------------------------------
# ------------------DECLARATIONS and SCOPE------------------------
def p_decl(p):
  '''Declaration : ConstDecl
                 | TypeDecl
                 | VarDecl'''
  p[0] = p[1]

def p_toplevel_decl(p):
  '''TopLevelDecl : Declaration
                  | FunctionDecl'''
  p[0] = p[1]
# -------------------------------------------------------
# ------------------CONSTANT DECLARATIONS----------------
def p_const_decl(p):
    '''ConstDecl : CONST ConstSpec
                 | CONST LPAREN ConstSpecRep RPAREN'''
    if len(p) == 3:
        p[0] = p[2]
    else:
        p[0] = p[3]

def p_const_spec_rep(p):
    '''ConstSpecRep : ConstSpecRep ConstSpec SemiColonOpt
                    | epsilon'''
    try:
        if len(p) == 4:
            p[0] = p[1]
            p[0].code += p[2].code
        else:
            p[0] = p[1]
        pass
    except Exception as e:
        print("WARNING:10:"+str(e))
        return

def p_const_spec(p):
    '''ConstSpec : IdentifierList Type ASSIGN ExpressionList'''
    try:
        p[0] = Node()
        p[0].code = p[1].code + p[4].code

        if(len(p[1].idList) != len(p[4].placeList)):
            pos = p.lexer.lexpos
            line = checkLineNo(pos)
            print("ERROR:: mismatch in number of identifiers and expressions for asisgnment ...Near line no",line)
            return
            # raise ValueError("WARNING: mismatch in number of identifiers and expressions for asisgnment")

        for x in range(len(p[1].idList)):
            if (p[4].typeList[x]).startswith('lit'):
                three_ac = ["=",p[1].placeList[x], p[4].placeList[x]]
                p[0].code.append(three_ac)
            p[1].placeList[x] = p[4].placeList[x]
            scope = findScope(p[1].idList[x])
            scopeDict[scope].updateArgList(p[1].idList[x], 'place', p[1].placeList[x])

            # type insertion
            scopeDict[scope].updateArgList(p[1].idList[x], 'type', p[2].typeList[0])
        pass
    except Exception as e:
        print("WARNING:11:"+str(e))
        return


    #TODO type checking

def p_identifier_list(p):
    '''IdentifierList : IDENTIFIER IdentifierRep'''
    try:
        p[0]= p[2]
        p[0].idList = [p[1]] + p[0].idList
        if checkId(p[1], "*"):
            pos = p.lexer.lexpos
            line = checkLineNo(int(pos),0)
            print("ERROR :: Name " + p[1] + " already exists, can't redefine ... Near line No ... ", line)
            # print(token_t)
            # print(token_t[p.lexer.lexpos-1])
            # raise NameError("Name " + p[1] + " already exists, can't redefine ...in line no " + str(token_t[p.lexer.lexpos-1]))
            return
        else:
            scopeDict[currScope].insert(p[1], None)
            nameTemp = newTemp()
            p[0].placeList = [nameTemp] + p[0].placeList
            scopeDict[currScope].updateArgList(p[1], 'place', nameTemp)
        pass
    except Exception as e:
        print("ERROR11::"+str(e))
        return

def p_identifier_rep(p):
    '''IdentifierRep : IdentifierRep COMMA IDENTIFIER
                     | epsilon'''
    try:
        if len(p) == 4:
            if checkId(p[3], "*"):
                pos = p.lexer.lexpos
                line = checkLineNo(pos,0)
                print("Name " + p[3] + " already exists, can't redefine ...Near line no ",line)
                return
            else:
                p[0] = p[1]
                scopeDict[currScope].insert(p[3], None)
                nameTemp = newTemp()
                p[0].placeList = p[0].placeList + [nameTemp]
                scopeDict[currScope].updateArgList(p[3], 'place', nameTemp)
                p[0].idList.append(p[3])


        else:
            p[0] = p[1]
        pass
    except Exception as e:
        print("WARNING:12:"+str(e))
        return

def p_expr_list(p):
    '''ExpressionList : Expression ExpressionRep'''
    try:
        p[0] = p[2]
        p[0].code = p[1].code+p[0].code
        p[0].placeList = p[1].placeList + p[0].placeList
        p[0].typeList = p[1].typeList + p[0].typeList
        p[0].idList = p[1].idList + p[0].idList # We need identifier list for structures
        if 'AddrList' not in p[1].extra:
            p[1].extra['AddrList'] = ['None']
        p[0].extra['AddrList'] += p[1].extra['AddrList']
        pass
    except Exception as e:
        print("WARNING:68:"+ str(e))
        pass

def p_expr_rep(p):
    '''ExpressionRep : ExpressionRep COMMA Expression
                     | epsilon'''
    try:
        if len(p) == 4:
            p[0] = p[1]
            p[0].code += p[3].code
            p[0].placeList += p[3].placeList
            p[0].typeList += p[3].typeList
            p[0].idList += p[3].idList  # We need identifier list for structures
            if 'AddrList' not in p[3].extra:
                p[3].extra['AddrList'] = ['None']
            p[0].extra['AddrList'] += p[3].extra['AddrList']
        else:
            p[0] = p[1]
            p[0].extra['AddrList'] = []
        pass
    except Exception as e:
        print("WARNING:69:" + str(e))

# ------------------------------------------------------


# ------------------TYPE DECLARATIONS-------------------
def p_type_decl(p):
    '''TypeDecl : TYPE TypeSpec
                | TYPE LPAREN TypeSpecRep RPAREN'''
    if len(p) == 5:
        p[0] = p[3]
    else:
        p[0] = p[2]
        # p[0] = ["TypeDecl", "type", p[2]]

def p_type_spec_rep(p):
    '''TypeSpecRep : TypeSpecRep TypeSpec SemiColonOpt
                   | epsilon'''
    if len(p) == 4:
        p[0] = Node()
    else:
        p[0] = p[1]

def p_type_spec(p):
    '''TypeSpec : TypeDef'''
    p[0] = p[1]
# -------------------------------------------------------


# -------------------TYPE DEFINITIONS--------------------
def p_type_def(p):
    '''TypeDef : IDENTIFIER Type'''
    if checkId(p[1], "*!s"):
        pos = p.lexer.lexpos
        line = checkLineNo(pos,0)
        print("ERROR::Name " + p[1] + " already exists, can't redefine... line no ", line)
        return
        # raise NameError("Name " + p[1] + " already exists, can't redefine")
    else:
        try:
            scopeDict[currScope].insert(p[1], p[2].typeList[0])
            p[0] = Node()
            pass
        except Exception as e:
            print("WARNING:13:"+str(e))
        return
        # print findInfo(p[1])
# -------------------------------------------------------


# ----------------VARIABLE DECLARATIONS------------------
def p_var_decl(p):
    '''VarDecl : VAR VarSpec
               | VAR LPAREN VarSpecRep RPAREN'''
    if len(p) == 3:
        p[0] = p[2]
    else:
        p[0] = p[3]

def p_var_spec_rep(p):
    '''VarSpecRep : VarSpecRep VarSpec SemiColonOpt
                  | epsilon'''
    try:
        if len(p) == 4:
            p[0] = p[1]
            p[0].code += p[2].code
        else:
            p[0] = p[1]
        pass
    except Exception as e:
        print("WARNING:14:"+str(e))
        return

def p_var_spec(p):
    '''VarSpec : IdentifierList Type ExpressionListOpt
               | IdentifierList ASSIGN ExpressionList'''
    try:
        if p[2] == '=':
            # x,y,z = 12, "hello", 4.67
            # The variables on LHS would have been inserted in the symbol table when p[1] would have reduced.
            pos = p.lexer.lexpos
            line = checkLineNo(pos,0)
            p[0] = Node()
            p[0].code = p[1].code + p[3].code

            if(len(p[1].placeList) != len(p[3].placeList)):
                # raise ValueError("WARNING: mismatch in number of identifiers and expressions for asisgnment")
                print("WARNING XX: mismatch in number of identifiers and expressions for asisgnment ...Near line no ",line)
                return

            for x in range(len(p[1].placeList)):
                scope = findScope(p[1].idList[x])
                three_ac = ["=",p[1].placeList[x], p[3].placeList[x]]
                p[0].code.append(three_ac)
                if (p[3].typeList[x]).startswith('lit'):
                    # Remove the 'lit' from the beginning if present
                    t = p[3].typeList[x][3:]
                else:
                    t = p[3].typeList[x]
                scopeDict[scope].updateArgList(p[1].idList[x], 'type', t)
                scopeDict[scope].updateArgList(p[1].placeList[x], 'type', t)

                p[1].placeList[x] = p[3].placeList[x]
                scopeDict[scope].updateArgList(p[1].idList[x], 'place', p[1].placeList[x])
        else:
            if len(p[3].placeList) == 0:
                p[0] = p[1]
                print("*********************: ", p[0].idList, "length: ", len(p[1].idList))
                for x in range(len(p[1].idList)):
                    print("********************IFFF", x, p[1].idList[x])
                    scope = findScope(p[1].idList[x])
                    scopeDict[scope].updateArgList(p[1].idList[x], 'type', p[2].typeList[0])
                    scopeDict[scope].updateArgList(p[1].placeList[x], 'type', p[2].typeList[0])
                return

            p[0] = Node()
            p[0].code = p[1].code + p[3].code
            if(len(p[1].placeList) != len(p[3].placeList)):
                pos = p.lexer.lexpos
                line = checkLineNo(pos,0)
                # raise ValueError("WARNING: mismatch in number of identifiers and expressions for asisgnment")
                print("WARNING: mismatch in number of identifiers and expressions for asisgnment ... Near Line no",line)
                return

            for x in range(len(p[1].placeList)):
               # print("----------->>>>>>>>>>>>>>>>>>>>>>>>>>",len(p[1].placeList))
                scope = findScope(p[1].idList[x])
                if not (p[3].typeList[x]).startswith('lit'):
                    three_ac = ["=",p[1].placeList[x], p[3].placeList[x]]
                    p[0].code.append(three_ac)

                scopeDict[scope].updateArgList(p[3].placeList[x], 'type', p[2].typeList[0])
                # scopeDict[scope].delete(p[1].placeList[x])
                p[1].placeList[x] = p[3].placeList[x]

                #TODO typelist check required
                scope = findScope(p[1].idList[x])
                scopeDict[scope].updateArgList(p[1].idList[x], 'place', p[1].placeList[x])
                scopeDict[scope].updateArgList(p[1].idList[x], 'type', p[2].typeList[0])

        pass
    except Exception as e:
        print("WARNING:15:"+str(e))
        return

def p_expr_list_opt(p):
    '''ExpressionListOpt : ASSIGN ExpressionList
                         | epsilon'''

    if len(p) == 3:
        p[0] = p[2]
    else:
        p[0] = p[1]
# -------------------------------------------------------


# ----------------SHORT VARIABLE DECLARATIONS-------------

#(divya)
def p_short_var_decl(p):
  ''' ShortVarDecl : IDENTIFIER QUICK_ASSIGN Expression'''
  try:
      if checkId(p[1], "*"):
        raise NameError("Name " + p[1] + " already exists, can't redefine")
      scopeDict[currScope].insert(p[1], None)   # set data type as none, it will be inferred from Expression.data_type
      p[0] = Node()
      newVar = newTemp()
      p[0].code = p[3].code
      if 'structName' in p[3].extra:
          # s := Person{name: "Sean", age: 16};
          # p[3].idList[name,age], p[3].typelist[litstring,litint], p[3].placeList["Sean", 16]
          # p[1] = s, p[3].extra['structName'][0] = Person
          scopeDict[currScope].updateArgList(p[1], 'place', newVar)
        #  scopeDict[currScope].updateArgList(p[1], 'value', p[3].valueList[0])
          scopeDict[currScope].updateArgList(p[1], 'type', 'type'+p[3].extra['structName'])
          for i in range(len(p[3].idList)):
              fname = p[3].idList[i]
              typeinfo = p[3].typeList[i][3:]
              placevalue = p[3].placeList[i]
              s = p[1] + '.' + fname
              three_ac = ['=',s,placevalue]
              p[0].code.append(three_ac)
              # print "--------------------s: , ",s
              if checkId(s,'*'):
                  # if s.name is already present in symbol table, we only need to update it's placevalue
                  scopeDict[currScope].updateArgList(s,'place',placevalue)
              else:
                  # if s.name is not present in symbol table then insert it with it's data type and placevalue
                  scopeDict[currScope].insert(s,typeinfo)
                  scopeDict[currScope].updateArgList(s,'place',placevalue)
      else:
          three_ac = ["=", newVar,p[3].placeList[0]]
          p[0].code.append(three_ac)
          scopeDict[currScope].updateArgList(p[1], 'place', newVar)
          if(p[3].typeList[0]).startswith('lit'):
            scopeDict[currScope].updateArgList(newVar, 'type', p[3].typeList[0][3:])
            scopeDict[currScope].updateArgList(p[1], 'type', p[3].typeList[0][3:])
          else:
            scopeDict[currScope].updateArgList(newVar, 'type', p[3].typeList[0])
            scopeDict[currScope].updateArgList(p[1], 'type', p[3].typeList[0])
          scopeDict[currScope].updateArgList(p[1], 'value', p[3].valueList[0])
      pass
  except Exception as e:
      print("WARNING:16:"+str(e))
      return
# -------------------------------------------------------
# ----------------FUNCTION DECLARATIONS------------------
def p_func_decl(p):
    '''FunctionDecl : FUNC FunctionName CreateScope Function EndScope
                    | FUNC FunctionName CreateScope Signature EndScope'''
    try:
        if not len(p[4].code):
            p[0] = Node()
            return

        p[0] = Node()
        global firstFunc
        if firstFunc:
            firstFunc = False
            p[0].code = [["goto", " ", " ", "label0"]]
        info = findInfo(p[2][1])
        label = info['label']

        p[0].code.append(['label', label])
        p[0].code += p[4].code
        pass
    except Exception as e:
        print("WARNING:17:"+str(e))
        return

def p_create_func_scope(p):
    '''CreateFuncScope : '''
    # print(" .....................create 1")
    # print(p[-1],p[0])
    addScope(p[-1])


def p_create_scope(p):
    '''CreateScope : '''
    # print(".........................create 2")
    # print(p[-1])
    addScope()

def p_delete_scope(p):
    '''EndScope : '''
    deleteScope()

def p_func_name(p):
    '''FunctionName : IDENTIFIER'''
    p[0] = ["FunctionName", p[1]]


def p_func(p):
    '''Function : Signature FunctionBody'''
    # TODO typechecking of return type. It should be same as defined in signature
    try:
        p[0] = p[2]
        for x in range(len(p[1].idList)):
            info = findInfo(p[1].idList[x])
            p[0].code = [['pop', ' ', len(p[1].idList) - x - 1, info['place']]] + p[0].code

        if checkId(p[-2][1], "signatureType") or checkId(p[-2][1], "package"):
            if p[-2][1] == "main":
                scopeDict[0].updateArgList("main", "label", "label0")
                scopeDict[0].updateArgList("main", 'child', scopeDict[currScope])

            info = findInfo(p[-2][1])
            info['type'] = 'func'
        else:
            # raise NameError('no signature for ' + p[-2][1] + '!')
            pos = p.lexer.lexpos
            line = checkLineNo(pos,0)
            print('ERROR::no signature for ' + p[-2][1] + '!.... near line no ',line)
            return
        # pass
    except Exception as e:
        print("WARNING:18:"+str(e))
        return


def p_func_body(p):
    '''FunctionBody : Block'''
    p[0] = p[1]
# -------------------------------------------------------
def p_bool_const(p):
    '''BoolConstant : TRUE
                    | FALSE'''
    try:
        p[0] = Node()
        name = newTemp()
        p[0].code.append(["=",name, p[1]])
        p[0].placeList.append(name)
        p[0].typeList.append('bool')
        p[0].valueList = [1] if p[1] == "true" else [0]
        pass
    except Exception as e:
        print("WARNING:19:"+str(e))
        return

# ----------------------OPERAND----------------------------
def p_operand(p):
    '''Operand : Literal
               | OperandName
               | LPAREN Expression RPAREN'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]

def p_literal(p):
    '''Literal : BasicLit'''
               #| CompositeLit'''
    p[0] = p[1]

def p_basic_lit(p):
    '''BasicLit : I INTEGER
                | I OCTAL
                | I HEX
                | F FLOAT
                | C IMAGINARY
                | I RUNE
                | S STRING'''
    try:
        p[0] = Node()
        name = newTemp()
        p[0].code.append(["=",name, p[2]])
        p[0].placeList.append(name)
        p[0].valueList.append(p[2])
        p[0].typeList.append('lit' + p[1])
        pass
    except Exception as e:
        print("WARNING:20:"+str(e))
        return

def p_I(p):
    ''' I : '''
    p[0] = 'int'


def p_F(p):
    ''' F : '''
    p[0] = 'float'

def p_C(p):
    ''' C : '''
    p[0] = 'complex'

def p_S(p):
    ''' S : '''
    p[0] = 'string'


def p_operand_name(p):
    '''OperandName : IDENTIFIER'''
    try:
        if not checkId(p[1], "**"):
            # raise NameError("Identifier " + p[1] + " not defined p_operand_name")
            pos = p.lexer.lexpos
            line = checkLineNo(pos,0)
            print("ERROR:21:Identifier " + p[1] + " not defined p_operand_name ... line no " , line)
            return
        p[0] = Node()
        info = findInfo(p[1])
        if info['type'] == 'func' or info['type'] == 'signatureType':
            p[0].typeList = [info['retType']]
            p[0].placeList.append(info['label'])
        else:
            p[0].typeList = [info['type']]
            p[0].placeList.append(info['place'])
            if 'value' in info:
                p[0].valueList.append(info['value'])
            # print "tttttttttttttttttype-else3"
        p[0].idList = [p[1]]
        pass
    except Exception as e:
        print("WARNING:22:"+str(e))
        return
# ---------------------------------------------------------


# -------------------QUALIFIED IDENTIFIER----------------
def p_quali_ident(p):
    '''QualifiedIdent : IDENTIFIER DOT TypeName'''
    try:
        if not checkId(p[1], "package"):
            pos = p.lexer.lexpos
            line = checkLineNo(pos,0)
            print("ERROR::Package " + p[1] + " not included ... line no " ,line)
            # raise NameError("Package " + p[1] + " not included ... line no " + str(token_t[p.lexer.lexpos-1]))
            return
        p[0] = Node()
        p[0].typeList.append(p[1]+p[2]+p[3].typeList[0])
        pass
    except Exception as e:
        print("WARNING:23:"+str(e))
        return

# -------------------------------------------------------


# ------------------PRIMARY EXPRESSIONS--------------------
def p_prim_expr(p):
    '''PrimaryExpr : Operand
                   | BoolConstant
                   | PrimaryExpr Selector
                   | Conversion
                   | PrimaryExpr LSQUARE Expression RSQUARE
                   | PrimaryExpr Slice
                   | PrimaryExpr TypeAssertion
                   | PrimaryExpr LPAREN ExpressionListTypeOpt RPAREN
                   | IDENTIFIER LCURL StructFieldList RCURL SemiColonOpt'''
    try:
        pos = p.lexer.lexpos
        line = checkLineNo(pos,0)
        # print "hiiiii"
        if len(p) == 2:
            p[0] = p[1]
        elif p[2] == '{':
        # Handle Structure initialisation
        # First thing is to check if IDENTIFIER has been declared before - struct
            p[0] = Node()
            info = findInfo(p[1])
            structName = info['type'][4:]   #info['type'] = 'typePerson', structName = Person
            if info['type'][:4] != 'type':
                raise TypeError(p[1]+" is not a structure. ")
            infoStruct = findInfo(structName, 0)
            newScopeTable = infoStruct['child'] # Get the symbol table of Person
            for i in range(len(p[3].idList)):
                fname = p[3].idList[i]
                typeinfo = p[3].typeList[i][3:]
                placevalue = p[3].placeList[i]
                if fname not in newScopeTable.table:
                    # raise NameError(fname + " is not a valid field in struct " + structName)
                    print(fname , " is not a valid field in struct " , structName , "near Line no ..",line)
                typedata = newScopeTable.getInfo(fname)
                print("--------------------,typedata: ",typedata)
                if typedata['type'] != typeinfo:
                    # raise TypeError(fname + ' of the struct is not of type ' + typeinfo)
                    print(fname , ' of the struct is not of type ' , typeinfo , "Near Line no ....", line)
                p[0].placeList.append(placevalue)
                p[0].typeList.append(typeinfo)
                p[0].idList.append(fname)
            p[0].extra['structName'] = structName
        elif p[2] == '[':
            print("hello there " , p[1].idList[0])
            info = findInfo(p[1].idList[0],currScope)
            # print info['type'][0]
            if info['type'][0] != "*":
                print ("ERROR:24:", p[1].idList[0],"is not Array Type ...Near line no ",line)
                return;
                # raise TypeError("Not array")
            if p[3].typeList[0][3:] != "int":
                pos = p.lexer.lexpos
                line = checkLineNo(pos,0)
                message = "ERROR:70: Index Must be integer type ...Near line no " + str(line)
                print (message)
                tell_him_error(message)
                return
            # print "type here",p[3].typeList[0]
            p[0] = p[1]
            p[0].code += p[3].code

            newPlace4 = newTemp()
            p[0].code.append(["=", newPlace4,'4'])

            newPlace3 = newTemp()
            p[0].code.append(['x',newPlace3, p[3].placeList[0],  newPlace4])

            newPlace = newTemp()
            p[0].code.append([ '+',newPlace, p[0].placeList[0], newPlace3])

            newPlace2 = newTemp()
            p[0].code.append(['*', newPlace2,newPlace])


            p[0].extra['AddrList'] = [newPlace]
            p[0].placeList = [newPlace2]
            p[0].typeList = [p[1].typeList[0][1:]]

        elif p[2] == '(':
            p[0] = p[1]
            p[0].code += p[3].code
            info = findInfo(p[1].idList[0])
            expected_params = info['num_param']
            return_type = info['retType']
            if len(p[3].placeList) != expected_params:
                print("number of Parameters are not same as expected ...Near Line no .." + str(line))
                return
            if p[-1] == '=':
                variable_type_info = findInfo(p[-3].idList[0])
                if variable_type_info['type'] is not None:
                    if variable_type_info['type'] != return_type:
                        print("Are bhai bahi .. function ka return type ", return_type,"Hai ! check line no ",line)
	                    # print variable_type_info['type']
                        return

            if len(p[3].placeList):
                for x in p[3].placeList:
                    p[0].code.append(['push',x])

            info = findInfo(p[1].idList[0], 0)
            if info['retType'] == 'void':
                p[0].code.append(['callvoid',info['label']])
            else:
                newPlace = newTemp()
                p[0].placeList = [newPlace]
                p[0].code.append(['callint',newPlace, info['label']])
            #TODO type checking
            p[0].typeList = [p[1].typeList[0]]
        else:
            if not len(p[2].placeList):
                p[0] = Node()
            else:
                p[0] = p[1]
                p[0].placeList = p[2].placeList
                p[0].typeList = p[2].typeList
                p[0].idList = p[2].idList
        pass
    except Exception as e:
        print("WARNING:25:"+str(e))
        return

def p_struct_initialise(p):
    ''' StructFieldList : IDENTIFIER COLON Expression StructFieldRep
                        | epsilon '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[4]
        p[0].idList.append(p[1])
        p[0].typeList.append(p[3].typeList[0])
        p[0].placeList.append(p[3].placeList[0])

def p_struct_initialise_rep(p):
    ''' StructFieldRep : COMMA IDENTIFIER COLON Expression StructFieldRep
                       | epsilon '''
    if len(p) == 6:
        p[0]=p[5]
        p[0].idList.append(p[2])
        p[0].typeList.append(p[4].typeList[0])
        p[0].placeList.append(p[4].placeList[0])
    else:
        p[0] = p[1] # p[0] will be declared as a fresh class Node object

def p_selector(p):
    '''Selector : DOT IDENTIFIER'''
    try:
        pos = p.lexer.lexpos
        line = checkLineNo(pos,0)
        p[0] = Node()
        info = findInfo(p[-1].idList[0])    # p[-1].idList[0] = 's' [not Person]
        structName = info['type'][4:]       # info['type'] = 'typePerson'
        infoStruct = findInfo(structName, 0)
        newScopeTable = infoStruct['child'] # Get the symbol table of Person
        p[0].extra['structName'] = structName
        if p[2] not in newScopeTable.table:
            # raise NameError("Identifier " + p[2] + " is not a valid field in struct " + structName)
            print("ERROR::Identifier " + p[2] + " is not defined in struct " + structName + "...Near line no",line)
            return
        s = p[-1].idList[0] + "." + p[2]    # s = s.name
        p[0].idList = [s]
        if checkId(s,'*'):
            # if s.name is already present in symbol table, extract it's current information and store in p[0]
            info = findInfo(s)
            p[0].placeList = [info['place']]
            p[0].typeList = [info['type']]
        else:
            # s.name is not present in symbol table, insert it with it's correct data type
            p[0].placeList = [newTemp()]
            typedata = newScopeTable.getInfo(p[2])  # typedata['type'] is actual data_type of s.name
            p[0].typeList = [typedata['type']]
            # example var Person struct{name string; age int;}; var p Person; p.age = 19;
            # Update Symbol Table :- s - p.age, p[0].typeList[0] - int
            # In the symboltable after insert() call ->  (self.table)[p.age] = {}; (self.table)[p.age]["type"] = int; (self.table)[p.age]["place"] = var1
            scopeDict[currScope].insert(s,p[0].typeList[0])
            scopeDict[currScope].updateArgList(s,'place',p[0].placeList[0])
        pass
    except Exception as e:
        print("ERROR:72:"+str(e))
        return


def p_slice(p):
    '''Slice : LSQUARE ExpressionOpt COLON ExpressionOpt RSQUARE
             | LSQUARE ExpressionOpt COLON Expression COLON Expression RSQUARE'''
    if len(p) == 6:
        p[0] = ["Slice", "[", p[2], ":", p[4], "]"]
    else:
        p[0] = ["Slice", "[", p[2], ":", p[4], ":", p[6], "]"]

def p_type_assert(p):
    '''TypeAssertion : DOT LPAREN Type RPAREN'''
    p[0] = ["TypeAssertion", ".", "(", p[3], ")"]

def p_expr_list_type_opt(p):
    '''ExpressionListTypeOpt : ExpressionList
                             | epsilon'''
    p[0] = p[1]
# ---------------------------------------------------------


#----------------------OPERATORS-------------------------

def p_expr(p):
    '''Expression : UnaryExpr
                  | Expression LOGICAL_OR Expression
                  | Expression LOGICAL_AND Expression
                  | Expression EQUALS Expression
                  | Expression NOT_ASSIGN Expression
                  | Expression LESSER Expression
                  | Expression GREATER Expression
                  | Expression LESS_EQUALS Expression
                  | Expression MORE_EQUALS Expression
                  | Expression OR Expression
                  | Expression XOR Expression
                  | Expression DIVIDE Expression
                  | Expression MOD Expression
                  | Expression LSHIFT Expression
                  | Expression RSHIFT Expression
                  | Expression PLUS Expression
                  | Expression MINUS Expression
                  | Expression STAR Expression
                  | Expression AND Expression'''
    try:
        if len(p) == 4:
            p[0] = Node()
            p[0].code += p[1].code
            p[0].code +=p[3].code
            print(p[0].code)
            newPlace = newTemp()
            p[0].placeList.append(newPlace)
            scope = findScope(newPlace)
            if (p[1].typeList[0]).startswith('lit'):
                p[1].typeList[0] = p[1].typeList[0][3:]
            if (p[3].typeList[0]).startswith('lit'):
                p[3].typeList[0] = p[3].typeList[0][3:]
            # Start -----------------------------------------------------------
            if p[2] == '+':
                if p[1].typeList[0]=='int' and p[3].typeList[0]=='int':
                    p[0].typeList = ['int']
                    if(len(p[1].valueList) and len(p[3].valueList)):
                        p[0].valueList.append(p[1].valueList[0] + p[3].valueList[0])
                    p[0].code.append([p[0].placeList[0],p[1].placeList[0],'+int',p[3].placeList[0] ])
                    scopeDict[scope].updateArgList(p[0].placeList[0], 'value', p[3].valueList[0])
                    scopeDict[scope].updateArgList(p[0].placeList[0], 'type', "int")
                    # p[0].valuelist = [p[1].valuelist[0]+p[3].valuelist[0]]
                elif p[1].typeList[0]=='string' and p[3].typeList[0]=='string':
                    p[0].typeList = ['string']
                    if(len(p[1].valueList) and len(p[3].valueList)):
                        p[0].valueList.append(p[1].valueList[0] + p[3].valueList[0])
                    p[0].code.append([p[0].placeList[0],p[1].placeList[0],'+string',p[3].placeList[0] ])
                    scopeDict[scope].updateArgList(p[0].placeList[0], 'value', p[3].valueList[0])
                    scopeDict[scope].updateArgList(p[0].placeList[0], 'type', "string")
                    # p[0].valuelist = [p[1].valuelist[0]+p[3].valuelist[0]]
                elif (p[1].typeList[0]=='int' and p[3].typeList[0]=='float') or (p[1].typeList[0]=='float' and p[3].typeList[0]=='int') or (p[1].typeList[0]=='float' and p[3].typeList[0]=='float'):
                    p[0].typeList = ['float']
                    if(len(p[1].valueList) and len(p[3].valueList)):
                        p[0].valueList.append(p[1].valueList[0] + p[3].valueList[0])
                    p[0].code.append([p[0].placeList[0],p[1].placeList[0],'+float',p[3].placeList[0] ])
                    scopeDict[scope].updateArgList(p[0].placeList[0], 'value', p[3].valueList[0])
                    scopeDict[scope].updateArgList(p[0].placeList[0], 'type', "float")
                    # p[0].valuelist = [p[1].valuelist[0]+p[3].valuelist[0]]
                else:
                    raise TypeError("+ operator does not allow "+p[1].typeList[0]+" and "+p[3].typeList[0]+" operand.")
            elif p[2] == '-':
                if p[1].typeList[0]=='int' and p[3].typeList[0]=='int':
                    p[0].typeList = ['int']
                    if(len(p[1].valueList) and len(p[3].valueList)):
                        p[0].valueList.append(p[1].valueList[0] - p[3].valueList[0])
                    p[0].code.append([p[0].placeList[0],p[1].placeList[0],'-int',p[3].placeList[0] ])
                    # print "hhhhhhhhhhhh",p[0].code
                    scopeDict[scope].updateArgList(p[0].placeList[0], 'value', p[3].valueList[0])
                    scopeDict[scope].updateArgList(p[0].placeList[0], 'type', "int")
                    # p[0].valuelist = [p[1].valuelist[0]-p[3].valuelist[0]]
                elif (p[1].typeList[0]=='int' and p[3].typeList[0]=='float') or (p[1].typeList[0]=='float' and p[3].typeList[0]=='int') or (p[1].typeList[0]=='float' and p[3].typeList[0]=='float'):
                    p[0].typeList = ['float']
                    if(len(p[1].valueList) and len(p[3].valueList)):
                        p[0].valueList.append(p[1].valueList[0] - p[3].valueList[0])
                    p[0].code.append([p[0].placeList[0],p[1].placeList[0],'-float',p[3].placeList[0] ])
                    scopeDict[scope].updateArgList(p[0].placeList[0], 'value', p[3].valueList[0])
                    scopeDict[scope].updateArgList(p[0].placeList[0], 'type', "float")
                    # p[0].valuelist = [p[1].valuelist[0]-p[3].valuelist[0]]
                else:
                    raise TypeError("- operator only allows int and float operand. ")
            elif p[2] == '*':
                if p[1].typeList[0]=='int' and p[3].typeList[0]=='int':
                    p[0].typeList = ['int']
                    if(len(p[1].valueList) and len(p[3].valueList)):
                        p[0].valueList.append(p[1].valueList[0] * p[3].valueList[0])
                    p[0].code.append([p[0].placeList[0],p[1].placeList[0],p[2]+'*int',p[3].placeList[0] ])
                    scopeDict[scope].updateArgList(p[0].placeList[0], 'value', p[3].valueList[0])
                    scopeDict[scope].updateArgList(p[0].placeList[0], 'type', "int")
                    # p[0].valuelist = ([p[1].valuelist[0]*p[3].valuelist[0]]) if p[2]=='*' else ([p[1].valuelist[0]/p[3].valuelist[0]])
                elif (p[1].typeList[0]=='int' and p[3].typeList[0]=='float') or (p[1].typeList[0]=='float' and p[3].typeList[0]=='int') or (p[1].typeList[0]=='float' and p[3].typeList[0]=='float'):
                    p[0].typeList = ['float']
                    if(len(p[1].valueList) and len(p[3].valueList)):
                        p[0].valueList.append(p[1].valueList[0] * p[3].valueList[0])
                    p[0].code.append([p[0].placeList[0],p[1].placeList[0],p[2]+'*float',p[3].placeList[0] ])
                    scopeDict[scope].updateArgList(p[0].placeList[0], 'value', p[3].valueList[0])
                    scopeDict[scope].updateArgList(p[0].placeList[0], 'type', "float")
                    # p[0].valuelist = ([p[1].valuelist[0]*p[3].valuelist[0]]) if p[2]=='*' else ([p[1].valuelist[0]/p[3].valuelist[0]])
                else:
                    raise TypeError(p[2]+" operator only allows int and float operand. ")
            elif p[2] == '/':
                if p[1].typeList[0]=='int' and p[3].typeList[0]=='int':
                    p[0].typeList = ['int']
                    if(len(p[1].valueList) and len(p[3].valueList)):
                        p[0].valueList.append(p[1].valueList[0] / p[3].valueList[0])
                    p[0].code.append([p[0].placeList[0],p[1].placeList[0],p[2]+'/int',p[3].placeList[0] ])
                    scopeDict[scope].updateArgList(p[0].placeList[0], 'value', p[3].valueList[0])
                    scopeDict[scope].updateArgList(p[0].placeList[0], 'type', "int")
                    # p[0].valuelist = ([p[1].valuelist[0]*p[3].valuelist[0]]) if p[2]=='*' else ([p[1].valuelist[0]/p[3].valuelist[0]])
                elif (p[1].typeList[0]=='int' and p[3].typeList[0]=='float') or (p[1].typeList[0]=='float' and p[3].typeList[0]=='int') or (p[1].typeList[0]=='float' and p[3].typeList[0]=='float'):
                    p[0].typeList = ['float']
                    if(len(p[1].valueList) and len(p[3].valueList)):
                        p[0].valueList.append(p[1].valueList[0] / p[3].valueList[0])
                    p[0].code.append([p[0].placeList[0],p[1].placeList[0],p[2]+'/float',p[3].placeList[0] ])
                    scopeDict[scope].updateArgList(p[0].placeList[0], 'value', p[3].valueList[0])
                    scopeDict[scope].updateArgList(p[0].placeList[0], 'type', "float")
                    # p[0].valuelist = ([p[1].valuelist[0]*p[3].valuelist[0]]) if p[2]=='*' else ([p[1].valuelist[0]/p[3].valuelist[0]])
                else:
                    raise TypeError(p[2]+" operator only allows int and float operand. ")
            elif p[2] == '%':
                if p[1].typeList[0]=='int' and p[3].typeList[0]=='int':
                    p[0].typeList = ['int']
                    if(len(p[1].valueList) and len(p[3].valueList)):
                        p[0].valueList.append(p[1].valueList[0] % p[3].valueList[0])
                    p[0].code.append([p[0].placeList[0],p[1].placeList[0],'%int',p[3].placeList[0] ])
                    scopeDict[scope].updateArgList(p[0].placeList[0], 'value', p[3].valueList[0])
                    scopeDict[scope].updateArgList(p[0].placeList[0], 'type', "int")
                    # p[0].valuelist.append(p[1].valuelist[0]%p[3].valuelist[0])
                else:
                    raise TypeError("% operator only allows integer operand. ")
            elif p[2] == '||':
                if p[1].typeList[0]=='bool' and p[3].typeList[0]=='bool':
                    p[0].typeList = ['bool']
                    if(len(p[1].valueList) and len(p[3].valueList)):
                        p[0].valueList.append(p[1].valueList[0] or p[3].valueList[0])
                    p[0].code.append([p[0].placeList[0], p[1].placeList[0], p[2]+'bool', p[3].placeList[0]])
                    scopeDict[scope].updateArgList(p[0].placeList[0], 'value', p[3].valueList[0])
                    scopeDict[scope].updateArgList(p[0].placeList[0], 'type', "bool")

            elif p[2] == '&&':
                if p[1].typeList[0]=='bool' and p[3].typeList[0]=='bool':
                    p[0].typeList = ['bool']
                    if(len(p[1].valueList) and len(p[3].valueList)):
                        p[0].valueList.append(p[1].valueList[0] and p[3].valueList[0])
                    p[0].code.append([p[0].placeList[0], p[1].placeList[0], p[2]+'bool', p[3].placeList[0]])
                    scopeDict[scope].updateArgList(p[0].placeList[0], 'value', p[3].valueList[0])
                    scopeDict[scope].updateArgList(p[0].placeList[0], 'type', "bool")

            elif p[2] == '==':
                if p[1].typeList[0]!=p[3].typeList[0]:
                    print(p[1].typeList[0],p[3].typeList[0])
                    raise TypeError("invalid operation: "+p[1].idList[0]+p[2]+p[3].idList[0]+" (mismatched types " + p[1].typeList[0]+" and "+ p[3].typeList[0]+")")
                p[0].typeList = ['bool']
                # p[0].valueList.append(int(p[1].valueList[0] == p[3].valueList[0]))
                p[0].code.append(["condition", p[1].placeList[0], p[2], p[3].placeList[0] ])
                scopeDict[scope].updateArgList(p[0].placeList[0], 'value', p[3].valueList[0])
                scopeDict[scope].updateArgList(p[0].placeList[0], 'type', "bool")

            elif p[2] == '!=':
                if p[1].typeList[0]!=p[3].typeList[0]:
                    raise TypeError("invalid operation: "+p[1].idList[0]+p[2]+p[3].idList[0]+" (mismatched types " + p[1].typeList[0]+" and "+ p[3].typeList[0]+")")
                p[0].typeList = ['bool']
                # p[0].valueList.append(int(p[1].valueList[0] != p[3].valueList[0]))
                p[0].code.append(["condition", p[1].placeList[0], p[2], p[3].placeList[0] ])
                scopeDict[scope].updateArgList(p[0].placeList[0], 'value', p[3].valueList[0])
                scopeDict[scope].updateArgList(p[0].placeList[0], 'type', "bool")

            elif p[2] == '>':
                if p[1].typeList[0]!=p[3].typeList[0]:
                    raise TypeError("invalid operation: "+p[1].idList[0]+p[2]+p[3].idList[0]+" (mismatched types " + p[1].typeList[0]+" and "+ p[3].typeList[0]+")")
                p[0].typeList = ['bool']
                # p[0].valueList.append(int(p[1].valueList[0] > p[3].valueList[0]))
                p[0].code.append(["condition", p[1].placeList[0], p[2], p[3].placeList[0] ])
                scopeDict[scope].updateArgList(p[0].placeList[0], 'value', p[3].valueList[0])
                scopeDict[scope].updateArgList(p[0].placeList[0], 'type', "bool")

            elif p[2] == '<':
                if p[1].typeList[0]!=p[3].typeList[0]:
                    raise TypeError("invalid operation: "+p[1].idList[0]+p[2]+p[3].idList[0]+" (mismatched types " + p[1].typeList[0]+" and "+ p[3].typeList[0]+")")
                p[0].typeList = ['bool']
                # p[0].valueList.append(int(p[1].valueList[0] < p[3].valueList[0]))
                p[0].code.append(["condition", p[1].placeList[0], p[2], p[3].placeList[0] ])
                scopeDict[scope].updateArgList(p[0].placeList[0], 'value', p[3].valueList[0])
                scopeDict[scope].updateArgList(p[0].placeList[0], 'type', "bool")

            elif p[2] == '>=':
                if p[1].typeList[0]!=p[3].typeList[0]:
                    raise TypeError("invalid operation: "+p[1].idList[0]+p[2]+p[3].idList[0]+" (mismatched types " + p[1].typeList[0]+" and "+ p[3].typeList[0]+")")
                p[0].typeList = ['bool']
                # p[0].valueList.append(int(p[1].valueList[0] >= p[3].valueList[0]))
                p[0].code.append(["condition", p[1].placeList[0], p[2], p[3].placeList[0] ])
                scopeDict[scope].updateArgList(p[0].placeList[0], 'value', p[3].valueList[0])
                scopeDict[scope].updateArgList(p[0].placeList[0], 'type', "bool")

            elif p[2] == '<=':
                if p[1].typeList[0]!=p[3].typeList[0]:
                    raise TypeError("invalid operation: "+p[1].idList[0]+p[2]+p[3].idList[0]+" (mismatched types " + p[1].typeList[0]+" and "+ p[3].typeList[0]+")")
                p[0].typeList = ['bool']
                # p[0].valueList.append(int(p[1].valueList[0] <= p[3].valueList[0]))
                p[0].code.append(["condition", p[1].placeList[0], p[2], p[3].placeList[0] ])
                scopeDict[scope].updateArgList(p[0].placeList[0], 'value', p[3].valueList[0])
                scopeDict[scope].updateArgList(p[0].placeList[0], 'type', "bool")

            else:
                p[0].code.append(["condition", newPlace,p[2],p[1].placeList[0], p[3].placeList[0] ])

        else:
            p[0] = p[1]
        pass
    except Exception as e:
        print("WARNING:23:"+str(e))
        return
def p_expr_opt(p):
    '''ExpressionOpt : Expression
                     | epsilon'''
    p[0] = p[1]

def p_unary_expr(p):
    '''UnaryExpr : PrimaryExpr
                 | UnaryOp UnaryExpr
                 | NOT UnaryExpr'''
    try:
        if len(p) == 2:
       	    p[0] = p[1]

        elif p[1] == "!":
            p[0] = p[2]
            newPlace = newTemp()
            p[0].code.append([newPlace, " ", "!", p[2].placeList[0]])
            p[0].placeList = [newPlace]
        else:
            p[0] = p[2]
            newPlace = newTemp()
            if p[1] == "-" or p[1] == '+':
                newPlace2 = newTemp()
                p[0].code.append([newPlace2, " ", '=', 0])
                p[0].code.append([newPlace, newPlace2, p[1], p[2].placeList[0]])

            else:
                p[0].code.append([newPlace, " ", p[1], p[2].placeList[0]])
            p[0].placeList = [newPlace]
        pass
    except Exception as e:
        print("WARNING:27:"+str(e))
        return

def p_unary_op(p):
    '''UnaryOp : PLUS
               | MINUS
               | STAR
               | AND '''
    if p[1] == '+':
        p[0] = ["UnaryOp", "+"]
    elif p[1] == '-':
        p[0] = ["UnaryOp", "-"]
    elif p[1] == '*':
        p[0] = ["UnaryOp", "*"]
    elif p[1] == '&':
        p[0] = ["UnaryOp", "&"]
# -------------------------------------------------------
# -----------------CONVERSIONS-----------------------------
def p_conversion(p):
    '''Conversion : TYPECAST Type LPAREN Expression RPAREN'''
    try:
        p[0] = p[4]
        p[0].typeList = [p[1].typeList[0]]
        pass
    except Exception as e:
        print("WARNING:28:"+str(e))
        return
# ---------------------------------------------------------
# ---------------- STATEMENTS -----------------------
def p_statement(p):
    '''Statement : Declaration
                 | LabeledStmt
                 | SimpleStmt
                 | ReturnStmt
                 | BreakStmt
                 | ContinueStmt
                 | GotoStmt
                 | CreateScope Block EndScope
                 | IfStmt
                 | SwitchStmt
                 | ForStmt
                 | PrintStmt
                 | ScanStmt'''

    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]


def p_print_stmt(p):
    ''' PrintStmt : PRINT Expression'''
    try:
        p[0] = p[2]
        p[0].code.append(['print', ' ', ' ', p[2].placeList[0]])
        pass
    except Exception as e:
        print("WARNING:29:"+str(e))
        return

def p_scan_stmt(p):
    ''' ScanStmt : SCAN Expression'''
    try:
        p[0] = Node()
        p[0].code.append(['scan', ' ' , ' ', p[2].placeList[0]])
        pass
    except Exception as e:
        print("WARNING:30:"+str(e))
        return



def p_simple_stmt(p):
  ''' SimpleStmt : epsilon
                 | ExpressionStmt
                 | IncDecStmt
                 | Assignment
                 | ShortVarDecl '''
  p[0] = p[1]


def p_labeled_statements(p):
  ''' LabeledStmt : Label COLON Statement '''
  try:
      if checkId(p[1][1], "label"):
        pos = p.lexer.lexpos
        line = checkLineNo(pos,0)
        print("Label " + p[1][1] + " already exists, can't redefine....Near line no",line)

      newl = ''
      if p[1][1] in labelDict:
      	scopeDict[0].insert(p[1][1], "label")
      	scopeDict[0].updateArgList(p[1][1], 'label', labelDict[p[1][1]][1])
      	labelDict[p[1][1]][0] = True
      	newl = labelDict[p[1][1]][1]
      else:
      	newl = newLabel()
      	scopeDict[0].insert(p[1][1], "label")
      	scopeDict[0].updateArgList(p[1][1], 'label', newl)
      	labelDict[p[1][1]] = [True, newl]

      p[0] = p[3]
      p[0].code = [['label', ' ', ' ', newl]] + p[0].code
      pass
  except Exception as e:
      print("WARNING:31:"+str(e))
      return

def p_label(p):
  ''' Label : IDENTIFIER '''
  p[0] = ["Label", p[1]]



def p_expression_stmt(p):
  ''' ExpressionStmt : Expression '''
  try:
      p[0] = Node()
      p[0].code = p[1].code
      pass
  except Exception as e:
      print("WARNING::"+str(e))
      return

def p_inc_dec(p):
  ''' IncDecStmt : Expression INCR
                 | Expression DECR '''
  try:
      p[0] = Node()
      p[0].code = p[1].code
      newtemp = newTemp()
      p[0].code.append([newtemp, p[1].placeList[0], p[2][0], 1])
      p[0].placeList.append(newtemp)
      p[0].typeList.append(p[1].typeList[0])
      pass
  except Exception as e:
      print("WARNING:32:"+str(e))
      return


# (divya)

def p_assignment(p):
  ''' Assignment : ExpressionList assign_op ExpressionList'''


  try:
      pos = p.lexer.lexpos
      line = checkLineNo(pos,0)
      if len(p[1].placeList) != len(p[3].placeList):
        print("ERROR:33:Number of expressions are not equal...Near Line No",line)
        return
          # raise ValueError("Number of expressions are not equal")
      p[0] = Node()
      p[0].code = p[1].code
      p[0].code += p[3].code
      for x in range(len(p[1].placeList)):
          # p[3].idList[x] need not be present
          # print "rrrrrrrrrrrrrrrrrrrrrr1:", p[1].idList[x]
          # print "rrrrrrrrrrrrrrrrrrrrrr2:", p[3].typeList
          # print "rrrrrrrrrrrrrrrrrrrrrr3:", p[1].typeList
          typeinfo = findInfo(p[1].idList[x])['type']
          # if p[1].idList[x] is a structure then typeinfo will be 'typePerson'
          if len(typeinfo)>4 and typeinfo[:4] == 'type':
              # print "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII"
              # s Person{name: "Sean"}
              # find the data_type of s.name by checking symbolTable of Person
              structName = typeinfo[4:]
              infoStruct = findInfo(structName, 0)
              newScopeTable = infoStruct['child']
              typedata = newScopeTable.getInfo(p[3].idList[x])
            #   if p[3].typeList[x] != typedata['type']:
            #       raise TypeError("types are not compatible")
              scopeDict[currScope].updateArgList(p[1].idList[x]+'.'+p[3].idList[x],'place',p[3].placeList[x])
          else:
              # print "JJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJ"
              # print p[1].idList[x], p[3].typeList[x], p[1].typeList[x]
              if 'lit' in p[3].typeList[x]:
                  p[3].typeList[x] = p[3].typeList[x][3:]
              if 'lit' in p[1].typeList[x]:
                  p[1].typeList[x] = p[1].typeList[x][3:]
              # print p[1].idList[x], p[3].typeList[x], p[1].typeList[x]
              if p[3].typeList[x]!=p[1].typeList[x]:
                print("ERROR:71: " , p[1].placeList[x]," is not of type" ,p[3].typeList[x][3:] ,"...Near Line No",line)
                return
                  # raise TypeError(p[1].idList[x] + " is assigned incorrect type!")
              if p[2][0] != '=':
                p[0].code.append([p[1].placeList[x], p[1].placeList[x], p[2][0], p[3].placeList[x]])
                print("yoooooooooooooooooooo",[p[1].placeList[x], p[1].placeList[x], p[2][0], p[3].placeList[x]])
              else:
                p[0].code.append([p[1].placeList[x], '', p[2], p[3].placeList[x]])
              scopeDict[currScope].updateArgList(p[1].idList[x],'place',p[3].placeList[x])
              # print "seeeeeeeeeee ->",p[1].placeList[x] , p[2], p[3].placeList[x]
              if(p[3].valueList[0]):
              	p[1].valueList.append(p[3].valueList[0])
              if p[1].extra['AddrList'][x] != 'None':
                  p[0].code.append(['load', ' ', p[1].extra['AddrList'][x], p[1].placeList[x]])
      pass
  except Exception as e:
      print("WARNING:34:"+str(e))
      return


def p_assign_op(p):
  ''' assign_op : AssignOp'''
  p[0] = p[1]

def p_AssignOp(p):
  ''' AssignOp : PLUS_ASSIGN
               | MINUS_ASSIGN
               | STAR_ASSIGN
               | DIVIDE_ASSIGN
               | MOD_ASSIGN
               | AND_ASSIGN
               | OR_ASSIGN
               | XOR_ASSIGN
               | LSHIFT_ASSIGN
               | RSHIFT_ASSIGN
               | ASSIGN '''
  p[0] = p[1]


def p_if_statement(p):
  ''' IfStmt : IF Expression CreateScopeIf Block EndScope ElseOpt'''
  try:
      p[0] = Node()
      p[0].code = p[2].code
      label1 = newLabel()
      newVar = newTemp()
      p[0].code += [[newVar, ' ', '=', p[2].placeList[0]]]
      newVar2 = newTemp()
      p[0].code += [[newVar2, ' ', '=', '1']]
      p[0].code += [[newVar,newVar2, '-', newVar]]
      p[0].code += [['ifgoto',' ', newVar, label1]]
      p[0].code += p[4].code
      label2 = newLabel()
      p[0].code += [['goto', ' ', ' ', label2]]
      p[0].code += [['label', ' ', ':', label1]]
      p[0].code += p[6].code
      p[0].code += [['label', ' ', ':', label2]]
      pass
  except Exception as e:
      print("WARNING:35:"+str(e))
      return

def p_createscopeif(p):
    '''CreateScopeIf : '''
    nextif = newIf()
    addScope(['0',nextif])

def p_else_opt(p):
  ''' ElseOpt : ELSE IfStmt
              | ELSE CreateScope Block EndScope
              | epsilon '''

  if len(p) == 3:
    p[0] = p[2]
  elif len(p) == 5:
    p[0] = p[3]
  else:
    p[0] = p[1]
# ----------------------------------------------------------------
# ----------- SWITCH STATEMENTS ---------------------------------

def p_switch_statement(p):
  ''' SwitchStmt : ExprSwitchStmt '''
  p[0] = p[1]

def p_expr_switch_stmt(p):
  ''' ExprSwitchStmt : SWITCH Expression CreateScope LCURL StartSwitch ExprCaseClauseRep RCURL EndScope '''
  try:
      p[0] = p[2]
      defaultLabel = None
      labnew = newLabel()
      p[0].code += [['goto', ' ', ' ', labnew]]
      p[0].code += p[6].code
      p[0].code += [['label', ' ', ':', labnew]]
      p[0].code += p[6].extra['exprList']

      for i in range(len(p[6].extra['labelList'])):

        if p[6].extra['labelType'][i] == 'default':
            defaultLabel = p[6].extra['labelList'][i]
        else:
            varNew = newTemp()
            p[0].code +=  [[varNew, p[2].placeList[0], '==', p[6].placeList[i]]]
            p[0].code += [['ifgoto', varNew, p[6].extra['labelList'][i]]]

      if defaultLabel is not None:
          p[0].code += [['goto', defaultLabel]]


      else:
          l = newLabel()
          p[0].code += [['goto', ' ', ' ', l]]
          p[0].code += [['label', ' ', ':', l]]

      p[0].code += [['label', ' ', ':', p[5].extra['end']]]
      pass
  except Exception as e:
      print("WARNING:36:"+str(e))
      return

def p_start_switch(p):
    ''' StartSwitch : '''
    try:
        p[0] = Node()
        label2 = newLabel()
        scopeDict[currScope].updateExtra('endFor',label2);
        p[0].extra['end'] = label2
        pass
    except Exception as e:
        print("WARNING:37:"+str(e))
        return

def p_expr_case_clause_rep(p):
  ''' ExprCaseClauseRep : ExprCaseClauseRep ExprCaseClause
                        | epsilon'''
  try:
      if len(p) == 3:
        p[0] = p[1]
        p[0].code += p[2].code
        p[0].placeList += p[2].placeList
        p[0].extra['labelList'] += p[2].extra['labelList']
        p[0].extra['labelType'] += p[2].extra['labelType']
        p[0].extra['exprList'] += p[2].extra['exprList']
      else:
        p[0] = p[1]
        p[0].extra['labelList'] = []
        p[0].extra['labelType'] = []
        p[0].extra['exprList'] = [[]]
      pass
  except Exception as e:
      print("WARNING:38:"+str(e))
      return

def p_expr_case_clause(p):
  ''' ExprCaseClause : ExprSwitchCase COLON StatementList '''
  try:
      p[0] = Node()
      label = newLabel()
      p[0].code = [['label', ' ', label]]
      p[0].code += p[3].code
      p[0].extra['labelList'] = [label]
      lab = findLabel('endFor')
      p[0].code.append(['goto', ' ', ' ', lab])
      p[0].extra['exprList'] = p[1].extra['exprList']
      p[0].placeList = p[1].placeList
      p[0].extra['labelType'] = p[1].extra['labelType']
      pass
  except Exception as e:
      print("WARNING:39:"+str(e))
      return


def p_expr_switch_case(p):
  ''' ExprSwitchCase : CASE Expression
                     | DEFAULT '''
  try:
      if len(p) == 3:
        p[0] = p[2]
        p[0].extra['labelType'] = ['case']
        p[0].extra['exprList'] = p[2].code

      else:
        p[0] = Node()
        p[0].extra['labelType'] = ['default']
        p[0].placeList = ['heya']
        p[0].extra['exprList'] = [[]]
      pass
  except Exception as e:
      print("WARNING:40:"+str(e))
      return

# -----------------------------------------------------------
# --------- FOR STATEMENTS ---------------
def p_for(p):
  '''ForStmt : FOR CreateScopeFor ConditionBlockOpt Block EndScope'''
  try:
      p[0] = Node()
      if 'forInc' in p[3].extra:
          # It implies that ConditionBlockOpt -> ForClause
          label1 = p[3].extra['before']
          p[0].code = p[3].code + p[4].code
          p[0].code += p[3].extra['forInc']
          p[0].code += [['goto', ' ', ' ', label1]]
          label2 = p[3].extra['after']
      else:  # elif p[3]!="" # What if the ConditionBlockOpt -> epsilon, what will be p[3].code?
          # ConditionBlockOpt -> Condition
          t1 = newTemp()
          t2 = newTemp()
          label1 = newLabel()
          label2 = newLabel()
          three_address_code_jump = ['=', t1, p[3].placeList[0]],['=',t2,'1'],['-',t1,t2,t1],['ifgoto', t1, label2]
          p[0].code = [['label', ' ', ':', label1]]
          p[0].code += p[3].code
          p[0].code += three_address_code_jump
          p[0].code += p[4].code
      p[0].code += [['label', ' ', ':', label2]]
      # scopeDict[currScope].updateArgList('for','child','for')
      pass
  except Exception as e:
      print("WARNING:41:"+str(e))
      return

def  p_createscopefor(p):
    ''' CreateScopeFor : '''
    nextfor = newFor()
    addScope(['0',nextfor])

def p_conditionblockopt(p):
  '''ConditionBlockOpt : epsilon
             | Condition
             | ForClause'''
             # | RangeClause'''
  p[0] = p[1]

def p_condition(p):
  '''Condition : Expression '''
  p[0] = p[1]

def p_forclause(p):
  '''ForClause : SimpleStmt SEMICOLON ConditionOpt SEMICOLON SimpleStmt'''
  try:
      p[0] = p[1]
      label1 = newLabel()
      p[0].code += [['label', ' ', ':', label1]]
      p[0].extra['before'] = label1
      p[0].code += p[3].code
      label2 = newLabel()
      scopeDict[currScope].updateExtra('beginFor',label1)
      scopeDict[currScope].updateExtra('endFor',label2)
      p[0].extra['after'] = label2
      if len(p[3].placeList) != 0:
        newVar = newTemp()
        newVar2 = newTemp()
        p[0].code += [[newVar, ' ', '=', p[3].placeList[0]],[newVar2, ' ', '=', '1'],[newVar,newVar2,'-',newVar],['ifgoto', newVar, label2]]
      # p[0].code += p[5].code
      p[0].extra['forInc'] = p[5].code
      pass
  except Exception as e:
      print("WARNING:42:"+str(e))
      return

def p_conditionopt(p):
  '''ConditionOpt : epsilon
          | Condition '''
  p[0] = p[1]

def p_return(p):
  '''ReturnStmt : RETURN ExpressionPureOpt'''
  try:
      p[0] = p[2]
      if len(p[2].placeList) != 0:
        p[0].code.append(["retint", ' ', ' ', p[2].placeList[0]])
      else:
        p[0].code.append(["retvoid", ' ', ' ', ' '])
  except Exception as e:
      print("WARNING:43:"+str(e))
      return

def p_expression_pure_opt(p):
  '''ExpressionPureOpt : Expression
             | epsilon'''
  p[0] = p[1]

def p_break(p):
  '''BreakStmt : BREAK LabelOpt'''
  try:
      if type(p[2]) is list:
      	if p[2][1] not in labelDict:
      		newl = newLabel()
      		labelDict[p[2][1]] = [False, newl]
      	p[0] = Node()
      	p[0].code = [['goto', ' ', ' ', labelDict[p[2][1]][1]]]
      else:
      	lab = findLabel('endFor')
      	p[0] = Node()
      	p[0].code.append(['goto', ' ', ' ', lab])
      pass
  except Exception as e:
      print("WARNING:44:"+str(e))
      return

def p_continue(p):
  '''ContinueStmt : CONTINUE LabelOpt'''
  try:
      if type(p[2]) is list:
      	if p[2][1] not in labelDict:
      		newl = newLabel()
      		labelDict[p[2][1]] = [False, newl]
      	p[0] = Node()
      	p[0].code = [['goto', ' ', ' ', labelDict[p[2][1]][1]]]
      else:
      	lab = findLabel('beginFor')
      	p[0] = Node()
      	p[0].code.append(['goto', ' ', ' ', lab])
      pass
  except Exception as e:
      print("WARNING:45:"+str(e))
      return

def p_labelopt(p):
  '''LabelOpt : Label
        | epsilon '''
  p[0] = p[1]

def p_goto(p):
  '''GotoStmt : GOTO Label '''
  try:
      if p[2][1] not in labelDict:
      	newl = newLabel()
      	labelDict[p[2][1]] = [False, newl]
      p[0] = Node()
      p[0].code = [['goto', ' ', ' ', labelDict[p[2][1]][1]]]
      pass
  except Exception as e:
      print("WARNING:46:"+str(e))
      return

# -----------------------------------------------------------
# ----------------  SEMICOLON is optional --------------------------------
def p_semicolon_opt(p):
    '''SemiColonOpt : SEMICOLON
                    | epsilon'''
    p[0] = p[1]
# ----------------  SOURCE FILE --------------------------------
def p_source_file(p):
    '''SourceFile : PackageClause SemiColonOpt ImportDeclRep TopLevelDeclRep'''
    try:
        p[0] = p[1]
        p[0].code += p[3].code
        p[0].code += p[4].code
        pass
    except Exception as e:
        print("WARNING:47:"+str(e))
        return

def p_import_decl_rep(p):
  '''ImportDeclRep : epsilon
           | ImportDeclRep ImportDecl SemiColonOpt'''
  try:
      if len(p) == 4:
        p[0] = p[1]
        p[0].code += p[2].code
      else:
        p[0] = p[1]
      pass
  except Exception as e:
      print("WARNING:48:"+str(e))
      return

def p_toplevel_decl_rep(p):
  '''TopLevelDeclRep : TopLevelDeclRep TopLevelDecl SemiColonOpt
                     | epsilon'''
  try:
    if len(p) == 4:
        p[0] = p[1]
        p[0].code += p[2].code
    else:
        p[0] = p[1]
    pass
  except Exception as e:
      print("WARNING:49:"+str(e))
      return
  # if len(p) == 4:
  #   p[0] = p[1]
  #   p[0].code += p[2].code
  # else:
  #   p[0] = p[1]
  #   '''p[0] = ["TopLevelDeclRep", p[1], p[2], p[3]]
  # else:
  #   p[0] = ["TopLevelDeclRep", p[1]]'''
# --------------------------------------------------------
# ---------- PACKAGE CLAUSE --------------------
def p_package_clause(p):
    '''PackageClause : PACKAGE PackageName'''
    # p[0] = ["PackageClause", "package", p[2]]
    p[0] = p[2]
    # p[0].code = [["package",str(p[2].idList[0])]]

def p_package_name(p):
    '''PackageName : IDENTIFIER'''
    try:
        p[0] = Node()
        p[0].idList.append(str(p[1]))
        if checkId(p[1], "*"):
            pos = p.lexer.lexpos
            line = checkLineNo(pos,0)
            print("Name " + p[1] + " already defined....near line no",line)
            return
        else:
            scopeDict[0].insert(p[1], "package")
        pass
    except Exception as e:
        print("WARNING:50:"+str(e))
        return
# -----------------------------------------------
# --------- IMPORT DECLARATIONS ---------------
def p_import_decl(p):
  '''ImportDecl : IMPORT ImportSpec
          | IMPORT LPAREN ImportSpecRep RPAREN '''
  if len(p) == 3:
    # p[0] = ["ImportDecl", "import", p[2]]
    p[0] = p[2]
    # p[0].code = [["import"] + p[2].idList]

  else:
    p[0] = Node()
    # for i in p[3].idList:
    #   p[0].code.append(["import", i])

def p_import_spec_rep(p):
  ''' ImportSpecRep : ImportSpecRep ImportSpec SemiColonOpt
            | epsilon '''
  try:
      if len(p) == 4:
        # p[0] = ["ImportSpecRep", p[1], p[2], p[3]]
        p[0] = p[1]
        # p[0].code += p[2].code
        p[0].idList += p[2].idList

      else:
        p[0] = p[1]
      pass
  except Exception as e:
      print("WARNING:51:"+str(e))
      return

def p_import_spec(p):
  ''' ImportSpec : PackageNameDotOpt ImportPath '''
  # p[0] = ["ImportSpec", p[1], p[2]]
  try:
      p[0] = p[1]
      if len(p[1].idList) != 0:
        p[0].idList =  p[1].idList[0] + " " + p[2].idList[0]
      else:
        p[0].idList += p[2].idList
      pass
  except Exception as e:
      print("WARNING:52:"+str(e))
      return

def p_package_name_dot_opt(p):
  ''' PackageNameDotOpt : DOT
                        | PackageName
                        | epsilon'''
  try:
      if p[1]== '.':
        p[0] = Node()
        p[0].idList.append(".")
      else:
        p[0] = p[1]
      pass
  except Exception as e:
      print("WARNING:53:"+str(e))
      return

def p_import_path(p):
  ''' ImportPath : STRING '''
  # p[0] = ["ImportPath", p[1]]
  p[0] = Node()
  p[0].idList.append(str(p[1]))
# -------------------------------------------------------
def p_empty(p):
  '''epsilon : '''
  p[0] = Node()

# Error rule for syntax errors
def p_error(p):
  print("Syntax error in input!")
  # print(p,p.lexpos,p.lineno)
  # print(token_t)
  print("Error in line no ",token_t[p.lexpos])
  exit()

# Build the parser
parser = yacc.yacc()

nonTerminals = []

def toFindNonTerminals(graph):
  try:
      if type(graph) is list:
        nonTerminals.append(graph[0])
        for i in range(1,len(graph),1):
          toFindNonTerminals(graph[i])
      pass
  except Exception as e:
      print("WARNING:54:"+str(e))
      return

def printResult(graph, prev, after):
  try:
      word = ""

      if type(graph) is list:

        lastFound = 0
        for i in range (len(graph)-1,0,-1):
          if type(graph[i]) is list:
            if word != "":
              if lastFound==1:
                word = graph[i][0]+ " " + word
              else:
                lastFound = 1
                word =  "<b style='color:red'>" + graph[i][0]+ "</b>" + " " + word
            else:
              if lastFound == 1:
                word = graph[i][0]
              else:
                lastFound = 1
                word = "<b style='color:red'>" + graph[i][0] + "</b>"
          else:
            if word != "":
              word =  graph[i] + " " + word
            else:
              word = graph[i]

        # word = '<span style="color:red">' + word + "</span>"

        if prev != "" and after != "":
          final = prev + " " + word + " "+ after
        elif prev == "" and after == "":
          final = word
        elif prev == "":
          final = word + " " + after
        else :
          final = prev + " " +word

        final = (final.replace(" epsilon", ""))
        toFindNT = final.split()
        # print toFindNT


        # print lastFound
        if lastFound == 0:
          for kk in range(len(toFindNT)-1,-1,-1):
            if toFindNT[kk] in nonTerminals:
              lastFound = 1
              toFindNT[kk] = "<b style='color:red'>" + toFindNT[kk] + "</b>"
              break
        final = ' '.join(toFindNT)
        print  (final + "<br/>")
        for i in range(len(graph)-1,0,-1):
          prevNew = prev

          for j in range (1,i):
            if type(graph[j]) is list:
              if prevNew != "":
                prevNew += " " + graph[j][0]
              else :
                prevNew = graph[j][0]
            else:
              if prevNew != "":
                prevNew += " " + graph[j]
              else:
                prevNew = graph[j]
          # print "prev " + prevNew
          afterNew = after
          # print "after " + afterNew
          afterNew = printResult(graph[i],prevNew,afterNew)
          # print "afterNew " + afterNew
          after = afterNew
        return after
      word = graph
      # print "after String " + word + after

      if word != "":
        return word+" "+after
      return after
      pass
  except Exception as e:
      print("WARNING:55:"+str(e))
      return

def checkLabel():
    try:
    	for x in labelDict:
    		if labelDict[x][0] == False:
    			print("Label " + x + " is not defined but is directed using Goto !")
                # return
        # pass
    except Exception as e:
        print("WARNING:57:"+str(e))
        return

try:
  s = data
  print(s)
except EOFWARNING:
  print("ABCD")
if not s:
  print("XYZ")

result = parser.parse(s)

lineNo = 1
def redirect_3ac(node):
  try:
      global lineNo
      three_adr_code = []
      for i in range(0,len(rootNode.code)):
        if len(rootNode.code[i]) > 0:
            data = []
            data += [str(lineNo)]
            for j in range(len(rootNode.code[i])):
              data += [str(rootNode.code[i][j])]
            three_adr_code += [data]
            lineNo += 1
      return three_adr_code
      pass
  except Exception as e:
      print("WARNING:56:"+str(e))
      return

checkLabel()
file_name = "ThreeAdressCode.csv"
three_adr_code = redirect_3ac(rootNode)
# print(three_adr_code)
with open(file_name, mode='w') as csvFile:
    writer = csv.writer(csvFile)
    writer.writerows(three_adr_code)
csvFile.close()
# sys.stdout = open(file_name, "w")
