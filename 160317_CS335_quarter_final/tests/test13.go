// errors related to struct
package main;
import "fmt";
type person struct {
    name string;
    age  int;
};
func main(){
//  print(person{"Bob", 20});
//  print(person{name: "Alice", age: 30});
   s := person{name: "Sean", age: 50};
   s = person{name: "Dean"}
   var t type person;
   t.name = 13;
   t.age = "hi";
   t.gender = 6;
};
