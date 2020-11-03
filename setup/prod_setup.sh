python3 -m pip install gunicorn

adduser hauntedtiles
usermod -aG sudo hauntedtiles
su - hauntedtiles
git config --global user.name "haunted-tiles"
git config --global user.password "haunt3d-T1les"
git clone https://github.com/z3ht/haunted-tiles.git
cd ~/haunted-tiles/setup

sudo ln -s ./config/systemd/hauntedtiles.service /etc/systemd/system
sudo ln -s ./config/nginx/hauntedtiles /etc/nginx/sites-enabled

sudo nginx -t

sudo systemctl restart nginx

sudo certbot

bash ./setup.sh
