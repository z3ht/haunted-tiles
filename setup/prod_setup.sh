#!/usr/bin/env bash

chmod 755 ./prod_setup.sh

adduser hauntedtiles
usermod -aG sudo hauntedtiles
su - hauntedtiles

sudo apt update
sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools
sudo apt install python3-venv python3-certbot-nginx certbot nginx

git config --global credential.helper store
git clone https://github.com/z3ht/haunted-tiles.git

python3 -m venv ~/haunted-tiles/venv
source ~/haunted-tiles/venv/bin/activate

python3 -m pip install gunicorn wheel

sudo ln -s ~/haunted-tiles/setup/config/systemd/hauntedtiles.service /etc/systemd/system
sudo ln -s ~/haunted-tiles/setup/config/nginx/hauntedtiles /etc/nginx/sites-enabled

sudo systemctl restart nginx

sudo certbot --nginx -d haunted-tiles.xyz

bash ./setup.sh
