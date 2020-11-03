#!/usr/bin/env bash

# This script could definitely be improved but I think it is good enough for our needs

python3 -m pip install flask cryptography python-dotenv

chmod 755 ./build.py
chmod 755 ./setup.sh

echo "export FLASK_ENV=development" > ./.env
echo -e "HAUNTED_TILES_API_TOKEN=\c" && read -r && [ ! -z "$REPLY" ] && echo "export HAUNTED_TILES_API_TOKEN=$REPLY" >> ./.env