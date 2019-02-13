import sys
import random
r = lambda: random.randint(0,255)
filename = "tokens.txt"
with open(filename) as f:
	for line in f:
		a=line.split(' ')
		# print(a)
		fd = open("5.txt","w+")
		for tok in a:
			a = (tok,'#%02X%02X%02X' % (r(),r(),r()))
			print(a)
			fd.write(str(a)+"\n")