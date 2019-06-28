// errors related to array index must be integer
package main;
import "fmt";
func main(){
	var a [10]int;
	var x string = "hi"
	a[2.4] = 10
	a[x] = 14
};

 