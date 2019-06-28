package main

import "fmt"
func fact( a int, x type person){
	if a == 1{
		return 1
	}
	return a*fact(a-1,x)
}

type person struct{
	age int
	name string
}
func main() {

    number := 5 // Change the number here

    // y type
    result := fact(number)

    print(5)
}