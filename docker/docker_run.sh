#!/bin/bash

docker run -d --restart=always \
	--net host \
	--device /dev/ttyACM0:/dev/ttyACM0 \
	robotarium:firmware \
	python3 gritsbot_2/gritsbot/firmware.py -host 192.168.1.8 -port 1884 gritsbot_2/config/mac_list.json
