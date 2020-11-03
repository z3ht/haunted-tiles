python3 -m pip install gunicorn

adduser hauntedtiles
usermod -aG sudo hauntedtiles
su - hauntedtiles

sudo apt update
sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools
sudo apt install python3-venv

git config --global credential.helper store
git clone https://github.com/z3ht/haunted-tiles.git

cd ~/haunted-tiles
python3 -m venv venv
source venv/bin/activate

cd setup
sudo ln -s ./config/systemd/hauntedtiles.service /etc/systemd/system
sudo ln -s ./config/nginx/hauntedtiles /etc/nginx/sites-enabled

sudo nginx -t

sudo systemctl restart nginx

sudo certbot

bash ./setup.sh
