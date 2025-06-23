#!/bin/bash
# Generate self-signed certificate for development
mkdir -p certs
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout certs/server.key -out certs/server.crt \
  -subj "/C=US/ST=NA/L=Local/O=Dev/CN=localhost"
chmod 600 certs/server.key
