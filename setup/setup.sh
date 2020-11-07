#!/usr/bin/env bash

# This script could definitely be improved but I think it is good enough for our needs
# If you don't want your /usr/bin/python3 env to become bloated make sure you use a venv

python3 -m pip install flask python-dotenv cryptography expiringdict

chmod 755 ../deploy.sh
chmod 755 ./setup.sh

echo -e "HAUNTED_TILES_API_TOKEN=\c" && read -r && [ ! -z "$REPLY" ] && echo "export HAUNTED_TILES_API_TOKEN=$REPLY" >> ../.env