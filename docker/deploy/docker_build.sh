#!/bin/bash

# First argument is repo.  Like arm32v6/ on the PI

docker build --build-arg REPO=$1 --tag robotarium:auto_update .
