#!/bin/bash

# First argument is absolute file path to container start sh 
# Second argument is name of remote conatainer 
# Third argument is name of remote registry

if [ "$1" == "" ]
then
	echo "First argument should be remote image name (e.g., firmware)."
	exit
fi

if [ "$2" == "" ]
then
	echo "Second argument should be remote registry name (e.g., ip:5000)."
	exit
fi

# Process is this container launches the other one, with certain environment variables set

docker run -d \
	-v /var/run/docker.sock:/var/run/docker.sock \
	--device $(python3 -m gritsbot.utils.detect_serial):/dev/ttyACM0 \
	--name=updater \
	--restart=always \
	robotarium:auto_update
