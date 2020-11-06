FROM debian:stretch

RUN apt update && apt install -y socat libc6-i386 libssl-dev && rm -rf /var/lib/apt/lists/*

RUN useradd -M chal

WORKDIR /opt/chal

COPY vega .
COPY flagpart_never .
COPY flagpart_gonna .
COPY flagpart_give .
COPY flagpart_you .
COPY flagpart_up .

RUN chmod 444 flagpart_never && chmod 444 flagpart_gonna && chmod 444 flagpart_give && chmod 444 flagpart_you && chmod 444 flagpart_up && chmod 555 vega

EXPOSE 5000

USER chal
CMD ["socat", "-T60", "TCP-LISTEN:5000,reuseaddr,fork","EXEC:./vega"]