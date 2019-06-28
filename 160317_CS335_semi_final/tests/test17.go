// error in number of params
package main;

import "fmt";

func gcd(a,b int) int{
	if b == 0{
		return a;
	};

	return gcd(b,a%b);
};


func main() {
	var a,b,c int;
	scan a;
	scan b;
	var c =gcd(a,b,c);
	print c;
	return;
};