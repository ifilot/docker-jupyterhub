# Jupyterhub Container

## Purpose

This is a self-contained Jupyter Hub instance that allows for self-signup of users and which
can be used by end-users to supply pre-defined Jupyter Notebooks to the users. By default,
no data is retained between instances (with exception of the notebooks), ensuring that
this instance can be taken down and re-initialized between courses or even classes. If you 
however want to retain the data between classes, you can make use of docker volumes.

## Running locally

### Accessing Docker registry

Ensure you can access the Docker registry

```bash
docker login -u __token__ -p <TOKEN> gitlab.tue.nl:5050/ifilot/tue-jupyterhub
```

### Command-line

Use the following one-liner to launch the (base) container

```bash
docker run -d --privileged -p 8000:8000 gitlab.tue.nl:5050/ifilot/tue-jupyterhub/tue-jupyter:latest
```

### Docker-compose

Use the following `docker-compose.yml` file to run the container locally.

```yaml
version: "3"

services:
  jupyterhub:
    image: gitlab.tue.nl:5050/ifilot/tue-jupyterhub/tue-jupyter:latest
    restart: always
    container_name: jupyterhub
    privileged: true
    ports:
      - "8000:8000"
```

If you want retention of data, use the following instructions

```bash
docker volume create jupyterhub-userdata
docker volume create jupyterhub-etcdata
```

```yaml
version: "3"

services:
  jupyterhub:
    build: .
    restart: always
    container_name: jupyterhub
    privileged: true
    volumes:
      - jupyterhub-userdata:/home
      - jupyterhub-etcdata:/etc
    ports:
      - "8000:8000"

volumes:
  jupyterhub-userdata:
    external: true
  jupyterhub-etcdata:
    external: true
```

## Running from a server

This configuration assumes that [nginx-proxy](https://hub.docker.com/r/jwilder/nginx-proxy)
and its [letsencrypt companion container](https://hub.docker.com/r/jrcs/letsencrypt-nginx-proxy-companion/)
are installed and properly configured.

Use the following `docker-compose.yml` file to run the service on a server. We assume here that you want
to retain user data between instances.

```yaml
version: "3"

services:
  jupyterhub:
    image: gitlab.tue.nl:5050/ifilot/tue-jupyterhub/tue-jupyter:latest
    restart: always
    container_name: jupyterhub
    volumes:
      - jupyterhub-userdata:/home
      - jupyterhub-etcdata:/etc
    privileged: true
    networks:
      - backend

  nginx:
    image: nginx:latest
    container_name: nginx-jupyterhub
    expose:
      - 80
    volumes:
      - ./nginx:/etc/nginx/conf.d:ro
    depends_on:
      - jupyterhub
    environment:
      VIRTUAL_HOST:
      LETSENCRYPT_HOST:
      LETSENCRYPT_EMAIL:
    restart: "unless-stopped"
    networks:
      - nginx-proxy
      - backend

volumes:
  jupyterhub-userdata:
    external: true
  jupyterhub-etcdata:
    external: true

networks:
  nginx-proxy:
    external: true
  backend:
```

and ensure you have placed the file `nginx/jupyter.conf` in the same folder as wherein the `docker-compose.yml`
file resides

```conf
upstream jupyterhub {
  ip_hash;
  server jupyterhub:8000;
}

server {

    location / {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;

        proxy_pass http://jupyterhub/;

        # enable WebSockets
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

    }

    listen 80;
    server_name localhost;
}
```