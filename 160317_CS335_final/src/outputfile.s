section .rodatan
	msg: db "Hello, world!", 10
	msglen: equ $ - msg
section .text
global _start
_start:
	mov rax, 1;
	mov rdi, 1;
	mov rsi, msg;
	mov rdx, msglen;
	syscall;
	jmp gcd;

gcd:

	push rbp;
	mov rsp,rbp;
	syscall;

exit:

	mov rax, 60;
	mov rdi, 0;
	syscall;
