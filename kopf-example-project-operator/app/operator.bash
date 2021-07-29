#!/bin/bash
set -e
set -u
command="kopf run --standalone /home/worker/app/operator.py "
#[[ "$VERBOSE" = "true" ]] && command+=("--verbose")

if [[ "$VERBOSE" -eq "true" ]]; then
    command+= " --verbose"
  fi

#[[ "$DEBUG" = "true" ]] && command+=("--debug")
if [[ "$DEBUG" -eq "true" ]]; then
    command+=" --debug"
fi

#[ -n "$NAMESPACE" ] && [ "$NAMESPACE" != "ALL" ] && echo "Only watching resources from the ${NAMESPACE} namespace" && command+=("--namespace=${NAMESPACE}")

#[[ "$LIVENESS" = "true" ]] && echo "Liveness /healthz endpoint has been explicitely enabled!" || command+=("--liveness=http://0.0.0.0:8080/healthz")

if [[ "$LIVENESS" -eq "true" ]]; then
    command+=" --liveness=http://0.0.0.0:8080/healthz"
fi

USER=$(id -u)
echo "Setting USER environment variable to ${USER}"
export USER=$USER
echo " Executing ${command}"
exec ${command}