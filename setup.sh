#!/usr/bin/env bash

# This script could definitely be improved but I think it is good enough for our needs

python -m pip install flask cryptography python-dotenv
chmod 755 ./build.py

echo "export FLASK_ENV=development" > ./.env
for ENV_VAR in HAUNTED_TILES_TARGET HAUNTED_TILES_API_TOKEN
do
  echo -e "$ENV_VAR=\c" && read -r && [ ! -z "$REPLY" ] && echo "export $ENV_VAR=$REPLY" >> ./.env
done