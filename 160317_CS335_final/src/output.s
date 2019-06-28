.data

x:
	.int	0
0var2:
	.int	0
0var3:
	.int	0
country:
	.int	0
0var0:
	.int	0
0var1:
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
	# 3, 0var2, , =, 0
	movl $0, 0var2
	# 4, 0var3, , =, 1
	movl $1, 0var3
	# 5, 0var2, 0var3, -, 0var2
	movl (0var3), %eax
	subl (0var2), %eax
	movl %eax, 0var2
	# 6, ifgoto, , 0var2, label4
	cmp $0, (0var2)
	jne label4
	# 7, country, , =, 9
	movl $9, country
	# 8, goto, , , label5
	jmp label5
	# 9, label, , :, label4

label4:

	# 10, 0var0, , =, 0
	movl $0, 0var0
	# 11, 0var1, , =, 1
	movl $1, 0var1
	# 12, 0var0, 0var1, -, 0var0
	movl (0var1), %eax
	subl (0var0), %eax
	movl %eax, 0var0
	# 13, ifgoto, , 0var0, label2
	cmp $0, (0var0)
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
