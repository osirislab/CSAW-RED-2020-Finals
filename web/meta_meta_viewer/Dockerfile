FROM python:3.7-alpine
RUN apk update && apk add exiftool
RUN adduser -D -u 1001 -s /bin/bash app

WORKDIR /opt/app
RUN mkdir -p /opt/app

COPY src/ /opt/app/
COPY aemm-config.json /home/app/
COPY ec2-metadata-mock-linux-amd64 /usr/bin/

RUN pip install -r requirements.txt
RUN chown -R 1001:1001 /opt/app/ && \
    chmod +x /opt/app/serve.sh && \
    chmod +x /usr/bin/ec2-metadata-mock-linux-amd64

USER 1001

ENTRYPOINT ["/opt/app/serve.sh"]
