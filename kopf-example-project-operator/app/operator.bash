#!/bin/bash
set -e
file="/home/worker/app/kopf_operator.py"
command="/home/worker/.local/bin/kopf run  --standalone "
cli_parameters=""

if [[ $VERBOSE = "true" ]]; then
    echo "VERBOSE is set true"
    cli_parameters="${cli_parameters} --verbose"
fi

if [[ $DEBUG = "true" ]]; then
    echo "DEBUG is set true"
    cli_parameters="${cli_parameters} --debug"
fi

if [ -z "$NAMESPACE" ]; then 
  echo "NAMESPACE is NULL"
  cli_parameters="${cli_parameters} -A"
  else 
  echo "NAMESPACE is set to ${NAMESPACE} "
  if [[ $NAMESPACE != "ALL" ]] ; then
    echo "NAMESPACE is set to ${NAMESPACE}"
    cli_parameters="${cli_parameters} --namespace ${NAMESPACE}"
  else
    cli_parameters="${cli_parameters} -A"
  fi

fi

if [[ $LIVENESS = "true" ]]; then
    echo "LIVENESS is set true"
    cli_parameters="${cli_parameters} --liveness=http://0.0.0.0:8080/healthz"
fi

echo "Parameters: ${cli_parameters}"

# add parameters and the name of operator file

command="${command} ${cli_parameters} ${file}"

USER=$(id -u)
echo "Setting USER environment variable to ${USER}"
export USER=$USER
echo " Executing ${command}"
eval "${command}"
