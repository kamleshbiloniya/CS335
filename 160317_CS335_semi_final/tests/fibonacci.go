package main

import "fmt"
func FibonacciRecursion(m,n int) int {
    if n <= 1 {
        return n
    }
    return FibonacciRecursion(n-1) + FibonacciRecursion(n-2)
}

func main() {

    number := 5 // Change the number here

    result := FibonacciRecursion(number,2)

    // fmt.Printf("Factorial of %#v is %#v",number,result)4
    print(result)
}