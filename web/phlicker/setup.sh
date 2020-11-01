#!/bin/bash

set -ueo pipefail

SECRET_KEY="uEWnxmVIamGhVaG4Zi6nfZMFMiEtax73"
DOMAIN="web.chal.csaw.io:8268"

docker run \
    -it \
    --rm \
    -v $(pwd)/inner:/opt/chal \
    -v /var/run/docker.sock:/var/run/docker.sock \
    tiangolo/docker-with-compose \
    sh -c "cd /opt/chal/ && ./setup.sh '$SECRET_KEY' && docker-compose create && docker-compose start && docker exec chal_frontend_1 python3 seed.py '$DOMAIN' 'flag{this_is_a_flag}' && docker-compose logs -f"
