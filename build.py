#!/usr/bin/python
import os

from api.haunted_tiles import begin_app

os.system("source ./secrets.env")
begin_app()
