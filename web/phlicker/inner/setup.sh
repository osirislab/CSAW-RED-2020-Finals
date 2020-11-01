#!/bin/sh

#REGISTRY="localhost:5000"
REGISTRY="web.chal.csaw.io:5000"

if ! docker ps | grep -q registry; then
    docker run -d -p 5000:5000 --restart=always --name registry registry:2
    docker pull traefik:v2.3
    docker tag traefik:v2.3 ${REGISTRY}/traefik:v2.3
    docker push ${REGISTRY}/traefik:v2.3
fi

docker build --build-arg "SECRET_KEY=$1" -t ${REGISTRY}/frontend:latest -f Dockerfile-frontend .
docker push ${REGISTRY}/frontend:latest

docker build -t ${REGISTRY}/resizer:latest -f Dockerfile-resizer .
docker push ${REGISTRY}/resizer:latest
