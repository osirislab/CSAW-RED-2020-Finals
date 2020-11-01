#!/bin/sh

docker kill chal_frontend_1 chal_resizer_1 traefik registry
docker rm chal_frontend_1 chal_resizer_1 traefik registry
