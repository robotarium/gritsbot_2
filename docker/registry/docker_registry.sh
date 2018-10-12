#!/bin/bash

docker run -d -p 192.168.1.8:5000:5000 --restart=always --name=registry registry:2
