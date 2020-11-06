.PHONY: main
main:
	cobc -free -Wall -Wcolumn-overflow -g -x -o main main.cobol

debug: main
	socat -v -T60 TCP-LISTEN:5000,reuseaddr,fork EXEC:./main,stderr
