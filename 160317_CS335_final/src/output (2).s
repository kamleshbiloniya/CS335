.data

x:
	.int	0
var2:
	.int	0
var3:
	.int	0
country:
	.int	0
var0:
	.int	0
var1:
	.int	0
outFormatInt:
	.asciz	"%d\n"
outFormatStr:
	.asciz	"%s\n"
inFormat:
	.ascii	"%d"

.text

.global _start

_start:

	call mainfunc
	jmp exit


mainfunc:

	pushl %ebp
	movl %esp, %ebp
	# 0, goto, , , label0
	jmp label0
	# 1, label, , :, label0

label0:

	# 2, x, , =, 99
	movl $99, x
	# 3, var2, , =, 0
	movl $0, var2
	# 4, var3, , =, 1
	movl $1, var3
	# 5, var2, var3, -, var2
	movl (var3), %eax
	subl (var2), %eax
	movl %eax, var2
	# 6, ifgoto, , var2, label4
	cmp $0, (var2)
	jne label4
	# 7, country, , =, 9
	movl $9, country
	# 8, goto, , , label5
	jmp label5
	# 9, label, , :, label4

label4:

	# 10, var0, , =, 0
	movl $0, var0
	# 11, var1, , =, 1
	movl $1, var1
	# 12, var0, var1, -, var0
	movl (var1), %eax
	subl (var0), %eax
	movl %eax, var0
	# 13, ifgoto, , var0, label2
	cmp $0, (var0)
	jne label2
	# 14, country, , =, 8
	movl $8, country
	# 15, goto, , , label3
	jmp label3
	# 16, label, , :, label2

label2:

	# 17, country, , =, 7
	movl $7, country
	# 18, label, , :, label3

label3:


exit:

	movl $0, %ebx
	movl $1, %eax
	int $0x80
