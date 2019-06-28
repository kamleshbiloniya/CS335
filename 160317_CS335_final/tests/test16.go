package main;

import "fmt";

func gcd(a,b int) int{
	if b == 0{
		g := 60
		return a;
	};

	return gcd(b,a%b);
};


func main() {
	var a,b int;
	scan a;
	scan b;
	var c =gcd(a,b);
	print c;
	return;
};