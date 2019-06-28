.data

var39:
	.int	0
var40:
	.int	0
var2:
	.int	0
var3:
	.int	0
var4:
	.int	0
var5:
	.int	0
var6:
	.int	0
var7:
	.int	0
var9:
	.int	0
var8:
	.int	0
var10:
	.int	0
var11:
	.int	0
var12:
	.int	0
var13:
	.int	0
var15:
	.int	0
var14:
	.int	0
var16:
	.int	0
var17:
	.int	0
var18:
	.int	0
var19:
	.int	0
var21:
	.int	0
var20:
	.int	0
var22:
	.int	0
var23:
	.int	0
var24:
	.int	0
var25:
	.int	0
var26:
	.int	0
var27:
	.int	0
var28:
	.int	0
var29:
	.int	0
var30:
	.int	0
var31:
	.int	0
var32:
	.int	0
var33:
	.int	0
var34:
	.int	0
var35:
	.int	0
var36:
	.int	0
var37:
	.int	0
var38:
	.int	0
outFormatInt:
	.asciz	"%d\n"
outFormatStr:
	.asciz	"%s\n"
inFormat:
	.ascii	"%d"

.text

.global main

main:

	call maink
	jmp exit


maink:

	pushl %ebp
	movl %esp, %ebp
	# 1, goto, , , label0
	jmp label0
	# 2, label, , :, label0

label0:

	# 3, pop, , 0, var39
	popl var39
	# 4, pop, , 1, var40
	popl var40
	# 5, push, , , var40
	pushl var40
	# 6, push, , , var39
	pushl var39
	# 7, var2, , =, 40
	movl $40, var2
	# 8, array, , var3, var2
	subl $4, %esp
	subl (var2), %esp
	movl %esp, %eax
	# 9, var4, , =, 8
	movl $8, var4
	# 10, var5, , =, 4
	movl $4, var5
	# 11, var6, var4, x, var5
	movl (var4), %edx
	imul (var5), %edx
	# 12, var7, var3, +, var6
	movl %eax, %edi
	addl %edx, %edi
	# 13, var9, , =, 7
	movl $7, var9
	# 14, var8, , =, var9
	movl (var9), %ebx
	# 15, store, , var7, var8
	movl %ebx, (%edi)
	# 16, var10, , =, 3
	movl $3, var10
	# 17, var11, , =, 4
	movl $4, var11
	# 18, var12, var10, x, var11
	movl (var10), %esi
	imul (var11), %esi
	# 19, var13, var3, +, var12
	movl %eax, %ecx
	addl %esi, %ecx
	# 20, var15, , =, 9
	movl $9, var15
	# 21, var14, , =, var15
	movl %edx, var6
	movl (var15), %edx
	# 22, store, , var13, var14
	movl %edx, (%ecx)
	# 23, var16, , =, 5
	movl $5, var16
	# 24, var17, , =, 4
	movl $4, var17
	# 25, var18, var16, x, var17
	movl %edx, var14
	movl (var16), %edx
	imul (var17), %edx
	# 26, var19, var3, +, var18
	movl %edx, var18
	movl %eax, %edx
	addl (var18), %edx
	# 27, var21, , =, 30
	movl $30, var21
	# 28, var20, , =, var21
	movl %edx, var19
	movl (var21), %edx
	# 29, store, , var19, var20
	movl %edx, var20
	movl (var19), %edx
	pushl (var20)
	popl (%edx)
	# 30, var22, , =, 8
	movl $8, var22
	# 31, var23, , =, 4
	movl $4, var23
	# 32, var24, var22, x, var23
	movl (var22), %edx
	imul (var23), %edx
	# 33, var25, var3, +, var24
	movl %edx, var24
	movl %eax, %edx
	addl (var24), %edx
	# 34, load, , var26, var25
	movl %edx, var25
	movl (var25), %edx
	movl (%edx), %edx
	# 35, var27, , =, 3
	movl $3, var27
	# 36, var28, , =, 4
	movl $4, var28
	# 37, var29, var27, x, var28
	movl %edi, var7
	movl (var27), %edi
	imul (var28), %edi
	# 38, var30, var3, +, var29
	movl %edi, var29
	movl %eax, %edi
	addl (var29), %edi
	# 39, load, , var31, var30
	movl %edi, var30
	movl (var30), %edi
	movl (%edi), %edi
	# 40, var32, var26, -, var31
	movl %edx, var26
	subl %edi, %edx
	# 41, var33, , =, 5
	movl $5, var33
	# 42, var34, , =, 4
	movl $4, var34
	# 43, var35, var33, x, var34
	movl %edi, var31
	movl (var33), %edi
	imul (var34), %edi
	# 44, var36, var3, +, var35
	movl %eax, var3
	addl %edi, %eax
	# 45, load, , var37, var36
	movl %eax, var36
	movl (var36), %eax
	movl (%eax), %eax
	# 46, var38, var32, +, var37
	movl %edx, var32
	addl %eax, %edx
	movl %eax, var37
	movl %edx, var38
	movl %edi, var35
	movl %ebx, var8
	movl %esi, var12
	movl %ecx, var13
	# 47, printint, , , var38
	pushl var38
	pushl $outFormatInt
	call printf

exit:

	movl $0, %ebx
	movl $1, %eax
	int $0x80
