# Dockerfile for pyrhon server with gost support

It'is server to connect with resriestr site.

## How to build

```bash
docker build -t pyhton-gost-server .
```

## Run with docker

```bash
docker run --rm -p 80:80 -v openssl-gost/python-gost:/app -w /app python-gost-server
```

## Run with sh
```bash
cd openssl-gost/python-gost
pip3 install flask
python3 server.py
```
