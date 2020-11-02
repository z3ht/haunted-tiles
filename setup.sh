#!/usr/bin/env zsh

# This script could definitely be improved but I think it is good enough for our needs

python -m pip install flask cryptography
chmod 755 ./build.py

: > ./secrets.env
for ENV_VAR in HAUNTED_TILES_TARGET HAUNTED_TILES_API_KEY GITHUB_USER GITHUB_PASS
do
  echo -e "$ENV_VAR=\c" && read -r && [ ! -z "$REPLY" ] && echo "export $ENV_VAR=$REPLY" >> ./secrets.env
done