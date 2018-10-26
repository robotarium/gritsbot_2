#!/bin/bash

# First argument is absolute file path to container start sh 
# Second argument is name of remote conatainer 
# Third argument is name of remote registry

if [ "$1" == "" ]
then
	echo "First argument should be path to start_container.sh."
	exit
fi

if [ "$2" == "" ]
then
	echo "Second argument should be remote image name (e.g., firmware)."
	exit
fi

if [ "$3" == "" ]
then
	echo "Third argument should be remote registry name (e.g., ip:5000)."
	exit
fi

docker run -d \
	-v /var/run/docker.sock:/var/run/docker.sock \
	-v $1:/start_container.sh:ro \
	--device $(python3 -m gritsbot.utils.detect_serial):/dev/ttyACM0 \
	--name=updater \
	--restart=always \
	robotarium:auto_update $2 $3
