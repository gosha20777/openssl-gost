#/bin/sh
# Generate new CA cert and key
openssl req -x509 -newkey gost2012_256 -pkeyopt paramset:A -nodes -days 10000 -keyout /etc/nginx/ca_key.pem -out /etc/nginx/ca_cert.crt -subj "/C=RU/L=Kemerovo/O=TEST GOST/CN=Test GOST CA"

# Generate new key for site
openssl genpkey -algorithm gost2012_256 -pkeyopt paramset:A -out /etc/nginx/key.pem

# Generate new request for site
openssl req -new -key /etc/nginx/gost.example.com.key -out /etc/nginx/gost.example.com.csr -subj "/C=RU/L=Kemerovo/O=My site with GOST/CN=gost.example.com"

# Sign request with CA
openssl x509 -req -in /etc/nginx/gost.example.com.csr -CA /etc/nginx/ca_cert.crt -CAkey /etc/nginx/ca_key.pem -CAcreateserial -out /etc/nginx/cert.pem -days 5000

echo "key.pem and cert.pem was created in /etc/nginx/"