#!/bin/bash

#export LOOP_INTERVAL=30
#export EXCLUDED_NAMESPACES="kube-system,kube-public,kube-node-lease"
export NAMESPACE="project-operator"
kopf run --standalone app/kopf_operator.py --namespace $NAMESPACE --liveness=http://0.0.0.0:8080/healthz