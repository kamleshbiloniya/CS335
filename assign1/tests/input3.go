package main
import "fmt"

func main() {
	for i := 0; i < 5; i++ {
		fmt.Println(i)
	}

	// let's add while loop . It should give error since there is no while loop in golang
	j := 0

	while j<5 {
		fmt.Println(i)
		j++
	}

	k := 1
    for k <= 3 {
        fmt.Println(k)
        k = k + 1
    }
}