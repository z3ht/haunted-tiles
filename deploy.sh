#!/usr/bin/env bash

ssh root@haunted-tiles.xyz  << EOF
  su - hauntedtiles
  cd ~/haunted-tiles
  sudo systemctl stop hauntedtiles
  git pull
  sudo systemctl start hauntedtiles
EOF