#! /usr/bin/env bash

# Create the CA Key and Certificate for signing Client Certs
openssl genrsa -aes128 -out ca.key 4096
openssl req -new -x509 -days 365 -key ca.key -out ca.crt

# Create the Client Key and CSR
openssl genrsa -aes128 -out client.key 2048
openssl req -new -key client.key -out client.csr

# Sign the client certificate with our CA cert.
# Serial should be different from the server one, otherwise curl will return NSS error -8054
openssl x509 -req -days 365 -in client.csr -CA ca.crt -CAkey ca.key -set_serial 02 -out client.crt

# Verify Client Certificate
openssl verify -purpose sslclient -CAfile ca.crt client.crt

