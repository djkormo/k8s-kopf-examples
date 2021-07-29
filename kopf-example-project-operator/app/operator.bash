#!/bin/bash
set -e
#set -u
file ="/home/worker/app/operator.py"
command="kopf run --standalone --verbose --debug --liveness=http://0.0.0.0:8080/healthz "/home/worker/app/operator.py"

USER=$(id -u)
echo "Setting USER environment variable to ${USER}"
export USER=$USER
echo " Executing ${command}"
exec "${command}
