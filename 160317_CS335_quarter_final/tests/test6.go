// struct ops
package math;
import "fmt";

type Vertex struct{
	x int;
	y int;
};

func main() {
	var d,e type Vertex;
	d.x = 3;
	d.y = 5;
	e.x = 2;
	e.y = 2;
	//d.x = d.x+2;
	print(d.x);
	print(-e.x);
	var x int = 3;
	print(+x);
	print(d.x+e.x)
	print(d.y-e.y)
	type Vertex struct{
		p int;
		q int;
		label string;
	};
};
