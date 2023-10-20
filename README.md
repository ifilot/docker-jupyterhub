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