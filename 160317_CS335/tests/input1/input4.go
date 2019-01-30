package main

import "fmt"
import "time"

func main() {

    // Switch example
    i := 2
    switch i {
    case 1:
        fmt.Println("one")
    case 2:
        fmt.Println("two")
    case 3:
        fmt.Println("three")
    }

		// Loop example
		for n := 0; n <= 5; n++ {
        if n%2 == 0 {
            continue
        }
        fmt.Println(n)
    }

		// String concatenation
    fmt.Println("CS335" + "Compilers")

    // Integers and floats.
    fmt.Println("1+1 =", 1+1)
    fmt.Println("10.0/2.0 =", 10.0/2.0)

    // Boolean operators
    fmt.Println(true && false)
    fmt.Println(true || false)
    fmt.Println(!true)

		fmt.Println("This statement has `ERRORS`')
}
