
from parser import 

f = open('outputfile.s', 'w')

def initializeGlobals():
    # symbolList = ST.globalSymbolList
    f.write('section .rodatan\n')
    genInstr("msg: db \"Hello, world!\", 10")
    genInstr("msglen: equ $ - msg")
    f.write('section .text\n')
    f.write('global _start\n')
    f.write('_start:\n')
    genInstr("mov rax, 1;")
    genInstr("mov rdi, 1;")
    genInstr("mov rsi, msg;")
    genInstr("mov rdx, msglen;")
    genInstr("syscall;")
    genInstr("jmp gcd;")
    genLabel("gcd")
    genInstr("push rbp;")
    genInstr("mov rsp,rbp;")
    genInstr("syscall;")

def genInstr(instr):
    f.write('\t' + instr + '\n')


def genLabel(label):
    f.write('\n' + label + ":\n\n")

def closeFile():
	genLabel("exit")
	genInstr("mov rax, 60;")
	genInstr("mov rdi, 0;")
	genInstr("syscall;")
	f.close()

initializeGlobals()
closeFile();