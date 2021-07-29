#!/bin/bash
set -e
set -u
command=("kopf" "run" "--standalone" "/home/worker/app/operator.bash")
[[ "$VERBOSE" = "true" ]] && command+=("--verbose")
[[ "$DEBUG" = "true" ]] && command+=("--debug")
[ -n "$NAMESPACE" ] && [ "$NAMESPACE" != "ALL" ] && echo "Only watching resources from the ${NAMESPACE} namespace" && command+=("--namespace=${NAMESPACE}")
[[ "$LIVENESS" = "false" ]] && echo "Liveness /healthz endpoint has been explicitely disabled!" || command+=("--liveness=http://0.0.0.0:8080/healthz")

USER=$(id -u)
echo "Setting USER environment variable to ${USER}"
export USER=$USER

exec ${command}
