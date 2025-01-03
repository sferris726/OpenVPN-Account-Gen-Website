#! /usr/bin/env bash

# Create the Client Key and CSR
openssl genrsa -out client.key 2048
openssl req -new -key client.key -out client.csr

for f in client.key
do
   mv -v "$f" /var/www/FlaskApps/client-configs/keys/"${f%.key}".key
done

for f in client.csr
do
   mv -v "$f" /var/www/FlaskApps/client-configs/"${f%.csr}".csr
done

