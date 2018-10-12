#!/bin/bash

# Use the detect_serial module to get the correct serial port
docker run -d --restart=always \
	--name firmware \
	--net host \
	--device /dev/ttyACM0:/dev/ttyACM0 \
	$1 \
	python3 gritsbot_2/gritsbot/firmware.py -host 192.168.1.8 -port 1884 gritsbot_2/config/mac_list.json
