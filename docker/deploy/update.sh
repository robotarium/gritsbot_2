#!/bin/bash

# This script uses the environment variables BASE_IMAGE and REGISTRY which should be set
# during the build process
set -e 
if [ "$BASE_IMAGE" == "" ]
then
	echo "Must supply base image in first argument."
	exit
fi

echo "Monitoring image: ($BASE_IMAGE) from registry ($REGISTRY)"
if [ "$REGISTRY" != "" ]
then
	IMAGE="$REGISTRY/$BASE_IMAGE"
else
	IMAGE=$BASE_IMAGE
fi


# First arg image, second arg repo
while :
do
	docker ps
	CID=$(docker ps | awk '{print $1 " " $2}' | grep $IMAGE | awk '{print $1}')

	if [ "$CID" == "" ]
	then
		echo "Container not running.  Starting."
		./start_container.sh $IMAGE
	fi

docker pull $IMAGE
	
	for im in $CID
	do
		LATEST=$(docker inspect --format "{{.Id}}" $IMAGE)
		RUNNING=$(docker inspect --format "{{.Image}}" $im)
		NAME=$(docker inspect --format "{{.Name}}" $im | sed "s/\///g")
	    	echo "Latest:" $LATEST
	    	echo "Running:" $RUNNING
	    	if [ "$RUNNING" != "$LATEST" ]
		then
	    		echo "upgrading $NAME"
			docker stop $NAME
			docker rm -f $NAME
			./start_container.sh $IMAGE
	    	else
	    		echo "$NAME up to date"
	    	fi
	done

	# Sleep for 30 seconds
	sleep 30
done

