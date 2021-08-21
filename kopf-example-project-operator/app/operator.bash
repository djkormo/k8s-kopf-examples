#!/bin/bash
set -e
#set -u
file="/home/worker/app/kopf_operator.py"
command="/home/worker/.local/bin/kopf run --standalone /home/worker/app/kopf_operator.py"
#[[ "$VERBOSE" = "true" ]] && command+=("--verbose")

if [[ "$VERBOSE" -eq "true" ]]; then
    echo "VERBOSE is set true"
    #cli=" --verbose "
    #command+=${cli}
fi

# [[ "$DEBUG" = "true" ]] && command+=("--debug")

if [[ "$DEBUG" -eq "true" ]]; then
    echo "DEBUG is set true"
    #cli=" --debug "
    #command+=${cli}
fi

#[ -n "$NAMESPACE" ] && [ "$NAMESPACE" != "ALL" ] && echo "Only watching resources from the ${NAMESPACE} namespace" && command+=("--namespace=${NAMESPACE}")

#[[ "$LIVENESS" = "true" ]] && echo "Liveness /healthz endpoint has been explicitely enabled!" || command+=("--liveness=http://0.0.0.0:8080/healthz")

if [[ "$LIVENESS" -eq "true" ]]; then
    echo "LIVENESS is set true"
    #cli=" --liveness=http://0.0.0.0:8080/healthz "
    #command+=${cli}
fi

# add the name of operator file
#command+=${file}"

USER=$(id -u)
echo "Setting USER environment variable to ${USER}"
export USER=$USER
echo " Executing ${command}"
eval "${command}"
