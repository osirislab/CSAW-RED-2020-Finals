FROM debian:buster

#global stuff
RUN apt-get update
RUN apt-get install -y python3 python3-pip socat

#gmpy2 prereqs
RUN apt-get install -y libgmp3-dev libmpfr-dev libmpc-dev

#to shrink image size??
RUN rm -rf /var/lib/apt/lists/*

RUN pip3 install gmpy2

RUN useradd -mN -k /home/chal chal

#local stuff
WORKDIR /home/chal

COPY server.py ./
COPY flag SECRET.py ./
RUN chown -R chal:users .

EXPOSE 5000

USER chal

#TODO change to route to C binary instead
CMD ["socat", "-T60", "TCP-LISTEN:5000,reuseaddr,fork", "EXEC:/usr/bin/python3 /home/chal/server.py,pty,echo=0"]
