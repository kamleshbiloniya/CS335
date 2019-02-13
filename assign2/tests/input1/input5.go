package main
import "fmt"

type person struct {
    name string
    age  int
}

func main() {
	fmt.Println(person{"kamlesh", 21})
    fmt.Println(person{name: "divya", age:19})
    fmt.Println(person{name: "harshit"})
    fmt.Println(&person{name: "biloniya", age: 21})
    p := person{name: "abc", age: 50}
    fmt.Println(p.name)
    /* G00d programmer don't do comment */
    psn := &p
    fmt.Println(psn.age)
	psn.age = 51
    fmt.Println(psn.age)
}