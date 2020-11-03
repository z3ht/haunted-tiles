#!/usr/bin/env bash

# This script could definitely be improved but I think it is good enough for our needs

python3 -m pip install flask cryptography python-dotenv

chmod 755 ./build.py
chmod 755 ./setup.sh

openssl genrsa -des3 -out ./server.key 2048
openssl req -new -key ./server.key -out ./server.csr
cp ./server.key ./server.key.org
openssl rsa -in ./server.key.org -out ./server.key
openssl x509 -req -days 365 -in ./server.csr -signkey ./server.key -out ./server.crt
rm ./server.key.org

echo "export FLASK_ENV=development" > ./.env
echo -e "HAUNTED_TILES_API_TOKEN=\c" && read -r && [ ! -z "$REPLY" ] && echo "export HAUNTED_TILES_API_TOKEN=$REPLY" >> ./.env