# Dockerfile for nginx with GOST TLS support

Contains nginx, openssl and gost-engine.

## How to build

You can pull my docker container: `docker pull rnix/nginx-gost`. if you want to build a docker image yourself or build it into your host mashine, see the instructions below.

* Dockerfile_gost_example_com - based on main
* gen_demo_gost_certs.sh - generates demo certificats
* nginx.conf - custom nginx.conf

### Build docker
```bash
docker build -t nginx-gost .
```

### Build form sh script

```bash
chmod +x build-nginx-gost.sh
sh build-nginx-gost.sh
```

## Run with docker

To run demo gost.example.com:

```bash
docker network create gost-network

# to use your serificates
docker build -f Dockerfile_gost_example_com -t gost-example-com .
docker run --rm --network=gost-network -v ./conf/:/etc/nginx/ --name gost.example.com gost-example-com

# to generate new sertificates
# uncomment lines in Dockerfile_gost_example_com and run 
docker build -f Dockerfile_gost_example_com -t gost-example-com .
docker run --rm --network=gost-network --name gost.example.com gost-example-com
```

To test it you need something with GOST-support, for example, curl:
```bash
docker run --rm -t --network=gost-network gosha20777/openssl-gost:dev curl https://gost.example.com -k
```

Example should contain response from Google, usually, it is `302 Moved`.

## Run on your host

To run demo gost.example.com:

```bash
# copy nginx.conf and configure it
cp ./conf/nginx.conf /etc/nginx/nginx.conf

# use your sert and key or generate it by
chmod +x gen_demo_gost_certs.sh
sh gen_demo_gost_certs.sh

# start nginx
nginx -g daemon off;
```