#! /usr/bin/env bash

#Get name from client
echo Please enter username: 

read varname

# Create the Client Key and CSR
openssl genrsa -aes128 -out $varname.key 2048
openssl req -new -key $varname.key -out $varname.csr

# Sign the client certificate with our CA cert.
# Serial should be different from the server one, otherwise curl will return NSS error -8054
openssl x509 -req -days 365 -in $varname.csr -CA ca.crt -CAkey ca.key -set_serial 02 -out $varname.crt

# Verify Client Certificate
openssl verify -purpose sslclient -CAfile ca.crt $varname.crt

#Move client.crt and client.key to client-configs
for f in $varname.crt
do
   mv -v "$f" /home/server/client-configs/keys/"${f%.crt}".crt
done

for f in $varname.key
do
   mv -v "$f" /home/server/client-configs/keys/"${f%.key}".key
done

