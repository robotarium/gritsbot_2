#!/bin/bash

# First argument is repo.  Like arm32v6/ on the PI

docker build --tag robotarium:auto_update .
