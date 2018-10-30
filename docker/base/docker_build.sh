#!/bin/bash

docker build --build-arg ROBO_HOST=$1 --build-arg ROBO_PORT=$2 --tag robotarium:firmware .
