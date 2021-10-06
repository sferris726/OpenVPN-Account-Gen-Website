# !/usr/bin/env bash

# Sign the client certificate with our CA cert.
# Serial should be different from the server one, otherwise curl will return NSS error -8054
openssl x509 -req -days 365 -in client.csr -CA ca.crt -CAkey ca.key -set_serial 02 -out client.crt

# Verify Client Certificate
openssl verify -purpose sslclient -CAfile ca.crt client.crt

for f in client.crt
do
   mv -v "$f" /home/server/client-configs/keys/"${f%.crt}".crt
done

