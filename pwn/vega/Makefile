all: vega

vega:
	gcc -m32 -fno-pie -no-pie -fno-stack-protector vega.c -o vega 
	strip vega

clean:
	rm vega