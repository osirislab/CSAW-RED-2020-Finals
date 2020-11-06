FROM debian:sid

WORKDIR /opt/app
RUN apt update && apt install -y gnucobol socat

COPY flag.txt /flag.txt
COPY index.html index.html
COPY css css
COPY main.cobol main.cobol

RUN cobc -free -Wall -Wcolumn-overflow -g -x -o main main.cobol

CMD socat -T60 TCP-LISTEN:5000,reuseaddr,fork EXEC:./main,stderr
