import time
import kopf
import kubernetes
import yaml
import os
from kubernetes.client.rest import ApiException
from pprint import pprint
import datetime
import random

# for Kubernetes probes

@kopf.on.probe(id='now')
def get_current_timestamp(**kwargs):
    return datetime.datetime.utcnow().isoformat()

@kopf.on.probe(id='random')
def get_random_value(**kwargs):
    return random.randint(0, 1_000_000)

# When creating object
@kopf.on.create('namespace')
def create_fn(spec, name, namespace, logger, **kwargs):
    print(f"Creating: {spec}")

# When updating object
@kopf.on.update('namespace')
def update_fn(spec, name, status, namespace, logger,diff, **kwargs):
    print(f"Updating: {spec}")
    
 # When deleting object
@kopf.on.delete('v1', 'namespace')
def delete_fn(spec, name, status, namespace, logger, **kwargs):
    print(f"Deleting: {spec}")