# Phlicker

Web 250(?)

Listens on port 8268, can be changed by modifying the bind in `inner/docker-compose.yml` and the port number in `/setup.sh`.

TODO: It should be safe to release everything in `inner/`, verify


## Deployment
`./setup.sh` in this folder (_not_ inner) will setup docker-in-docker to deploy it
`./reset.sh` quickly nukes everything setup setup

registry binds to 5000 on host, ensure this is FW'd off

If you run this on some domain other than `web.chal.csaw.io`, update domain in `/setup.sh`, `/inner/setup.sh`, and `/inner/config.py`

### Deets
* `/setup.sh` starts dind, in which it
    * Calls `/inner/setup.sh` (with `SECRET_KEY` to ensure that doesn't get leaked into distributed files)
        * Starts registry, grabs traefik, and pushes it to the registry
        * Builds and pushes the 2 chal docker images
    * `docker-compose` create and start
    * execs into the newly started container to seed the DB


## Solution

* Find proxy/ssrf in resizer
    * domain check can be bypassed since it doesn't check for trailing /, so you can do web.chal.csaw.io.yourdomain.whatever which redirects or resolves to registry
* Use above to get docker image from the local registry
* Extract image and acquire flask signing key
* sign auth cookie to see flag album
