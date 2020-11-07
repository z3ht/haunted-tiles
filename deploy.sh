#!/usr/bin/env bash

ssh root@haunted-tiles.xyz  << EOF
  su - hauntedtiles
  cd ~/haunted-tiles
  echo "ubuntu_sucks" | sudo -S systemctl stop hauntedtiles
  git pull
  sudo systemctl start hauntedtiles
EOF