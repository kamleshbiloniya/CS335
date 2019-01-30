package main
import "fmt"

func add(a int , b int) int {
	return a+b
}

func main() {
	res := add(1, 2)
    fmt.Println("1+2 =", res) // adding two numbers
    		//this is comment after 3 tabs

	// Array, curly braces, square brackets
	var a [5]int
	fmt.Println("array:", a)
	a[4] = 123
  fmt.Println("set:", a)
  fmt.Println("get:", a[4])
	b := [5]int{1, 2, 3, 4, 5}
  fmt.Println("another array:", b)
	var twoD [2][3]int
  for i := 0; i < 2; i++ {
      for j := 0; j < 3; j++ {
          twoD[i][j] = i + j
      }
  }
  fmt.Println("Example of 2-D array ", twoD)
}
