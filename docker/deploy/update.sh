#!/bin/bash

set -e
BASE_IMAGE=$1
REGISTRY=$2

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
	set -e
	BASE_IMAGE=$1
	REGISTRY=$2
	if [ "$REGISTRY" != "" ]
	then
		echo "setting"
		IMAGE="$REGISTRY/$BASE_IMAGE"
	else
		IMAGE=$BASE_IMAGE
	fi
	CID=$(docker ps | awk '{print $1 " " $2}' | grep $IMAGE | awk '{print $1}')
	docker ps
	echo "$CID"
	docker pull $IMAGE
	
	for im in $CID
	do
		LATEST=$(docker inspect --format "{{.Id}}" $IMAGE)
		RUNNING=$(docker inspect --format "{{.Image}}" $im)
		NAME=$(docker inspect --format "{{.Name}}" $im | sed "s/\///g")
	    	echo "Latest:" $LATEST
	    	echo "Running:" $RUNNING
	    	if [ "$RUNNING" != "$LATEST" ];then
	    		echo "upgrading $NAME"
			docker stop $NAME
			docker rm -f $NAME
			./start_container.sh $IMAGE
		
			# Stop, kill, and restart container
	        	#stop docker-$NAME
	        	#docker rm -f $NAME
	        	#start docker-$NAME
	    	else
	    		echo "$NAME up to date"
	    	fi
	done

	# Sleep for 30 seconds
	sleep 30
done

