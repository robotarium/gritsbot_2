#!/bin/bash

docker build --tag robotarium:auto_update \
	--build-arg BASE_IMAGE=$1 \
	--build-arg REGISTRY=$2 .
