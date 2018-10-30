#!/bin/bash

docker run -d \
	--name watchtower_firmware \
	-v /var/run/docker.sock:/var/run/docker.sock \
	v2tec/watchtower:armhf-latest robotarium/firmware -i 60 --debug 
