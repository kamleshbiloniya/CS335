.data

outFormatInt:
	.asciz	"%d\n"
outFormatStr:
	.asciz	"%s\n"
inFormat:
	.ascii	"%d"

.text

.global main

main:

	call mainMandal
	jmp exit


mainMandal:

	pushl %ebp
	movl %esp, %ebp
