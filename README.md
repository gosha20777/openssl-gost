# Docker image with OpenSSL 1.1.1, GOST engine and cURL

This image was built to have ability to connect to servers with GOST SSL certificates.
In addition, it helps to encrypt, decrypt, hash messages with GOST algorithms.

Since version 1.1.1 OpenSSL does not contain GOST-engine anymore, but it can be compiled and used separately.
This image does this work.

Output of `openssl ciphers` supports:

```
GOST2012-GOST8912-GOST8912
GOST2001-GOST89-GOST89
```

Take a look at GOST-engine documentation: https://github.com/gost-engine/engine/blob/master/README.gost

There are some issues with OpenSSL 1.1.1 and GOST-engine (GOST ciphers are not in list), so versions are fixed in default docker's build args.

## How to build

You can pull my docker container: `docker pull gosha20777/openssl-gost:dev`. if you want to build a docker image yourself or build it into your host mashine, see the instructions below.

### Build docker
```bash
docker build -t openssl-gost .
```

### Build form sh script

```
chmod +x build-openssl-gost.sh
sh build-openssl-gost.sh
```

## Usage

The image has been built and pushed into https://hub.docker.com/repository/docker/gosha20777/openssl-gost.
In examples below I use image *rnix/openssl-gost* from Docker Hub, but you can build this image for you own and use your tag.

As usual, you can run commands directly from host or you can use 'interactive mode' with `-i`.
Pull the image and run a container with mounted current dir in interactive mode:

```
docker run --rm -i -t -v `pwd`:`pwd` -w `pwd` gosha20777/openssl-gost:dev bash
```
Run command with mounted current dir without interactive mode:

```
docker run --rm -v `pwd`:`pwd` -w `pwd` gosha20777/openssl-gost:dev openssl version
```

If you use Windows, `pwd` is incorrect. Use absolute path instead, for example:
```
docker run --rm -i -t -v /c/workspace/:/certs/ -w /certs/ gosha20777/openssl-gost:dev bash
```
    
In the container you run commands.

## Examples

To show certificate of host with GOST
```
openssl s_client -connect gost.example.com:443 -showcerts
```

To send a file to host with POST and save the response into new file
```
curl -X POST --data-binary @file.txt https://gost.example.com --output response.txt
```

To generate new key and certificate with Signature Algorithm: GOST R 34.11-94 with GOST R 34.10-2001
```
openssl req -x509 -newkey gost2001 -pkeyopt paramset:A -nodes -keyout key.pem -out cert.pem
```

To sign file with electronic signature by GOST using public certificate (-signer cert.pem),
private key (-inkey key.pem), with opaque signing (-nodetach),
DER as output format without including certificate and attributes (-nocerts -noattr):
```
openssl cms -sign -signer cert.pem -inkey key.pem -binary -in file.txt -nodetach -outform DER -nocerts -noattr -out signed.sgn
```

To extract data (verify) from signed file (DER-format) using public certificate (-certfile cert.pem) 
issued by CA (-CAfile cert.pem) (the same because cert.pem is self-signed):
```
openssl cms -verify -in signed.sgn -certfile cert.pem -CAfile cert.pem -inform der -out data.txt
```

More examples with GOST can be found here: https://github.com/gost-engine/engine/blob/master/README.gost

## Certification authority (CA)

In Russia, it is common to issue GOST-certificates signed by CA which are not worldwide trusted.
In this case you get error. For example, `curl: (60) SSL certificate problem: unable to get local issuer certificate`.
To solve this problem you have two options: 1) do not verify CA (not recommended), 2) find and use CA.

1. To ignore security error use `-k` with curl and `-noverify` with openssl. 
For example `curl https://gost.examples.com -k` or `openssl cms -verify -noverify`.

2. Find and download CA-certificate file. 
For example, [CryptoPRO CA](http://cpca.cryptopro.ru/cacer.p7b). It is PKCS7, but you need PEM.
Run command to extract all certificates from p7b and write them as a chain of certificates in one file:
```
openssl pkcs7 -inform DER -outform PEM -in cacer.p7b -print_certs > crypto_pro_ca_bundle.crt
```

When you have CA-file you can: 

* Install it in default CA certificate store
* Specify it in every openssl or curl command

To install it in default CA certificate store use commands:
```
cp crypto_pro_ca_bundle.crt /usr/local/share/ca-certificates/
update-ca-certificates
```

To specify it in curl:
```
curl https://gost.example.com/ --cacert crypto_pro_ca_bundle.crt
```

To specify it in openssl with verifying signature:
```
openssl cms -verify -in signed.txt -signer cert.pem -inform DER -CAfile crypto_pro_ca_bundle.crt -out unsigned.txt
```

## Usage in other Dockerfiles

Compiled libraries can be used in other Dockerfiles with multi-stage approach. Basic template is in `any-gost` directory.
Working example with PHP is in `php-fpm-gost` directory.

There some notices:

* OpenSSL and cURL are build in custom directory `/usr/local/ssl` and `usr/local/curl` 
  which contain `bin`, `include`, `lib`.
* Before compiling the main Dockerfile folders `/usr/local/ssl` and `usr/local/curl` should be copied into new image.
* During building packages openssl and curl can be installed and overwrite new `/usr/bin/openssl` and `/usr/bin/curl`.
* Specify paths of libraries in configuring scripts to new locations.

## License

MIT License.

It's a fork of https://github.com/rnixik/docker-openssl-gost