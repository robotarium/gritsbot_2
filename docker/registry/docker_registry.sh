#!/bin/bash

docker run -d ---restart=always \
	   -p 192.168.1.8:5000:5000 \
	   --name=registry \
	   registry:2
