FROM ubuntu:18.04

RUN apt update && apt install -y socat && rm -rf /var/lib/apt/lists/*

RUN useradd -M chal

WORKDIR /opt/chal

COPY armorcheck .
COPY flag.txt .

RUN chmod 444 flag.txt && chmod 555 armorcheck

EXPOSE 5000

USER chal
CMD ["socat", "-T60", "TCP-LISTEN:5000,reuseaddr,fork","EXEC:./armorcheck"]
