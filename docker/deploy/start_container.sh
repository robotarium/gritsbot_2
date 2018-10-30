#!/bin/bash

# Use the detect_serial module to get the correct serial port
docker run -d --restart=always \
	--name firmware \
	--net host \
	--device /dev/ttyACM0:/dev/ttyACM0 \
	$1
