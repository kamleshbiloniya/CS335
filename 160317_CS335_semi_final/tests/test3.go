// if_else if.go
package maie
import "fmt"

func main() {
    X:=2*3+7
    Y := 2+3*7
    if 7%2 == 0 {
        print("7 is even")
    }
    else {
        print("7 is odd")
    }
    x := 100
  
	if x == 50 {
		print("Germany")
	} else if x == 100 {
		print("Japan")
	} else {
		print("Canada")
	}

  // Does not work because IfStmt : IF SimpleStmtOpt Expression ... not working
  //   if x := 100; x == 100 {
	// 	print("Germany")
	// }

}
