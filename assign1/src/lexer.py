#!/usr/bin/python
import ply.lex as lex
import sys
from ply.lex import TOKEN


############################ reg exps are taken from https://github.com/pkhrag/cs335/blob/master/assign1/src/lexer.py ########################################################

class MyLex(object):
	# wspace = {'WSPACE'}

	keywords = {'STRUCT', 'FUNC', 'CONST', 'TYPE', 'VAR', 'IF', 'ELSE', 'SWITCH', 'CASE', 'DEFAULT', 'FOR', 'RANGE', 'RETURN', 'BREAK', 'CONTINUE', 'GOTO', 'PACKAGE', 'IMPORT' }
	operators = {'PLUS', 'MINUS', 'STAR', 'DIVIDE', 'MOD', 'ASSIGN', 'AND', 'LOGICAL_AND', 'INCR', 'DECR', 'LPAREN', 'RPAREN', 'OR', 'XOR', 'LSHIFT', 'RSHIFT', 'PLUS_ASSIGN', 'MINUS_ASSIGN', 'STAR_ASSIGN', 'DIVIDE_ASSIGN', 'MOD_ASSIGN', 'AND_XOR', 'AND_ASSIGN', 'OR_ASSIGN', 'XOR_ASSIGN', 'LSHIFT_ASSIGN', 'RSHIFT_ASSIGN', 'AND_XOR_ASSIGN', 'LOGICAL_OR', 'EQUALS', 'LESSER', 'GREATER', 'NOT', 'NOT_ASSIGN', 'LESS_EQUALS', 'MORE_EQUALS', 'QUICK_ASSIGN', 'LSQUARE', 'RSQUARE', 'LCURL', 'RCURL',  'COMMA', 'DOT', 'SEMICOLON', 'COLON'}

	reserved = {}
	for r in keywords:
		reserved[r.lower()] = r

	types = {'INTEGER', 'OCTAL', 'HEX', 'FLOAT', 'STRING', 'IMAGINARY', 'RUNE'}

	identity = {'IDENTIFIER'}
	comments = {'COMMENT'}

	tokens =  list(comments) + list(operators) + list(types) + \
	              list(identity)  + list(reserved.values())

	# Token definitions

	t_COMMENT = r'(/\*([^*]|\n|(\*+([^*/]|\n])))*\*+/)|(//.*)'
	t_ignore = ' \t'
	# t_WSPACE = r'\s'
	t_PLUS = r'\+'
	t_MINUS = r'-'
	t_STAR = r'\*'
	t_DIVIDE = r'/'
	t_MOD = r'%'
	t_ASSIGN = r'='
	t_AND = r'&'
	t_LOGICAL_AND = r'&&'
	t_INCR = r'\+\+'
	t_DECR = r'--'
	t_LPAREN = r'\('
	t_RPAREN = r'\)'
	t_OR = r'\|'
	t_XOR = r'\^'
	t_LSHIFT = r'<<'
	t_RSHIFT = r'>>'
	t_PLUS_ASSIGN = r'\+='
	t_MINUS_ASSIGN = r'-='
	t_STAR_ASSIGN = r'\*='
	t_DIVIDE_ASSIGN = r'/='
	t_MOD_ASSIGN = r'%='
	t_AND_XOR = r'&\^'
	t_AND_ASSIGN = r'&='
	t_OR_ASSIGN = r'\|='
	t_XOR_ASSIGN = r'\^='
	t_LSHIFT_ASSIGN = r'<<='
	t_RSHIFT_ASSIGN = r'>>='
	t_AND_XOR_ASSIGN = r'&\^='
	t_LOGICAL_OR = r'\|\|'
	t_EQUALS = r'=='
	t_LESSER = r'<'
	t_GREATER = r'>'
	t_NOT = r'!'
	t_NOT_ASSIGN = r'!='
	t_LESS_EQUALS = r'<='
	t_MORE_EQUALS = r'>='
	t_QUICK_ASSIGN = r':='
	t_LSQUARE = r'\['
	t_RSQUARE = r'\]'
	t_LCURL = r'\{'
	t_RCURL = r'\}'
	t_COMMA = r','
	t_DOT = r'\.'
	t_SEMICOLON = r';'
	t_COLON = r':'

	# Integer based reg variables
	newline = "\\n"
	# wspace = "\s"

	decimal_lit = "(0|([1-9][0-9]*))"
	octal_lit = "(0[0-7]*)"
	hex_lit = "(0x|0X)[0-9a-fA-F]+"

	# Float based reg variables
	float_lit = "[0-9]*\.[0-9]+([eE][-+]?[0-9]+)?"

	# string_lit = """("[^"]*")|(\'[^\']*\')"""
	string_lit = """("[^"]*")"""
	imaginary_lit = "(" + decimal_lit + "|" + float_lit + ")i"

	rune_lit = "\'(.|(\\[abfnrtv]))\'"

	identifier_lit = "[_a-zA-Z]+[a-zA-Z0-9_]*"
	# @TOKEN(newline)
	# def t_NEWLINE(self,t):
	# # 	print("hello")
	# @TOKEN(wspace)
	# def t_WSPACE(self,t):
	# 	self.f.write("&nbsp")
	# 	print("hiiii")
		# print("ok")
	# @TOKEN(comments)
	# def t_COMMENT(self,t):
	# 	# r'(/\*([^*]|\n|(\*+([^*/]|\n])))*\*+/)|(//.*)'
	# 	r'(/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/)|(//.*)'
	# 	print("comment..")
	@TOKEN(identifier_lit)
	def t_IDENTIFIER(self,t):
		t.type = self.reserved.get(t.value, 'IDENTIFIER')
		return t
	@TOKEN(rune_lit)
	def t_RUNE(self,t):
	    t.value = ord(t.value[1:-1])
	    return t


	@TOKEN(string_lit)
	def t_STRING(self,t):
	    t.value = t.value[1:-1]
	    return t


	@TOKEN(imaginary_lit)
	def t_IMAGINARY(self,t):
	    t.value = complex(t.value.replace('i', 'j'))
	    return t


	@TOKEN(float_lit)
	def t_FLOAT(self,t):
	    t.value = float(t.value)
	    return t


	@TOKEN(hex_lit)
	def t_HEX(self,t):
	    t.value = int(t.value, 16)
	    return t


	@TOKEN(octal_lit)
	def t_OCTAL(self,t):
	    t.value = int(t.value, 8)
	    return t


	@TOKEN(decimal_lit)
	def t_INTEGER(self,t):
	    # re.escape(decimal_lit)
	    t.value = int(t.value)
	    return t



	# def t_ignore(self,t):
	# 	r' \t'
	# 	self.f.write("</br>")

    # track line numbers
	@TOKEN(newline)
	def t_NEWLINE(self, t):
		# r'\n'
		self.row = t.lexpos
		self.col = 1;
		print("hello at %d"% self.row)
		self.f.write("</br>")
		t.lexer.lineno +=1

    # handle Error
	def t_error(self, t):
		self.f.write("<br>Line :: %d  Illegal entry '%s'<br>" %(t.lexer.lineno, t.value))
		t.lexer.skip(1)

    # Build the lexer
	def build(self, **kwargs):
		self.lexer = lex.lex(module=self, **kwargs)

    # Test it output
	def test(self, data):
		self.lexer.input(data)
		# global f
		# outfile = "out.html"
		# f = open(outfile,"w+")
		self.f.write(" <!DOCTYPE html> \r\n<html>\r\n<head>\r\n\t<title>CS335-Assignment1</title>\r\n</head>\r\n<body>\r\n")
		self.f.write("<p>")
		line_num = 1;

		while True:
			tok = self.lexer.token()
			print(tok)
			if not tok:
				self.f.write("</p>\r\n</body>\r\n</html>\r\n")
				break
			else:
				if(tok.lineno != line_num):
					line_num = tok.lineno
					tmp = tok.lexpos - self.row
					while (tmp>self.col):
						self.f.write("&nbsp")
						self.col+=1
					self.col += len(str(tok.value))
					# self.f.write("</p>\r\n<p>")
					if(tok.type == 'STRING'):
						# self.f.write("\"%s\""%tok.value)
						self.f.write("<label style='color:")
						self.f.write("%s% self.dict[str(tok.type)])
						self.f.write("'>\"%s\"</label> "%tok.value)
					else:
						# self.f.write("%s"%tok.value)
						self.f.write("<label style='color:")
						self.f.write("%s"% self.dict[str(tok.type)])
						self.f.write("'>\"%s\"</label> "%tok.value)
				else:
					tmp = tok.lexpos - self.row
					while (tmp>self.col):
						self.f.write("&nbsp")
						self.col+=1
					self.col += len(str(tok.value))
					if(tok.type == 'STRING'):
						# self.f.write("\"%s\""%tok.value)
						self.f.write("<label style='color:")
						self.f.write("%s"% self.dict[str(tok.type)])
						self.f.write("'>\"%s\"</label> "%tok.value)
					else:
						# self.f.write("%s"%tok.value)
						self.f.write("<label style='color:")
						self.f.write("%s"% self.dict[str(tok.type)])
						self.f.write("'>\"%s\"</label> "%tok.value)
            # print(tok)

	def __init__(self):
		self.Num_Keyword=0
		outfile = sys.argv[3].split("=")[1]
		self.f=open(outfile,"w+")
		self.dict = {}
		self.row=0;
		self.col=0;
		# self.dict['hello'] = 'world'
		# self.dict['hi'] = 'hello'
		self.configfile = sys.argv[1].split("=")[1]
		with open(self.configfile) as f:
			for line in f:
				a,b=line.split(',')
				b=b.split('\n')
				self.dict[a]=b[0]
				# <lable style='background:green'>I am red</lable>
				self.f.write("<lable style='background:")
				self.f.write("%s"% str(b[0]))
				self.f.write("'>%s</lable>"% str(a))

			# s1=f.readlines()
			# print(s1)
		# print(self.dict['PACKAGE'],self.dict['IMPORT'])
		# self.outfile = "out.html"
		# print(self.f.read)


        # self.Num_Literals=0
        # self.Num_Operator=0
        # self.Num_Separator=0
        # self.Num_Identifier=0
		# self.ReservedWords=["TRUE","true","FALSE","false","null"]



# Build the lexer and try it out
# outfile = "out.html"
# f = open(outfile,"w+")
myLexer = MyLex()
myLexer.build()           # Build the lexer
# m.Num_Keyword=0
inlen = len(sys.argv)
if(inlen < 4 ):
	print("Usages:python lexer.py --cfg=tests/cfg1/some-cfg tests/input1/some-input --output=some.html")
	exit()
try:
	configfile = sys.argv[1].split("=")[1]
	filename = sys.argv[2]
	outfile = sys.argv[3].split("=")[1]

	f = open(filename, 'r')
	data = f.read()
	print(data)
	# myLexer.openfile()
	myLexer.test(data)     # Test it
except IndexError:
	print("Usages:python lexer.py --cfg=tests/cfg1/some-cfg tests/input1/some-input --output=some.html")
