// switch.go 
package main
import "fmt"
func main() {
	print("Go runs on ")
	os := "darwin"
	switch os {
	// case "darwin":
	// 	print("OS X.")
	case "linux":
		print("Linux.")
	default:
		// %s  %d not working
		// print("%s.\n", os)
		print("inside default")
	}
}
