#!/bin/bash
# read filename 
filename='try.go'
python parser_x.py ../tests/$filename
echo 'parser done'
python codegen.py
echo 'codegen done'
gcc -m32 output.S -o output
echo 'gcc done'
./output

echo "everything DOne "
# rm ThreeAdressCode.csv output.o output.S