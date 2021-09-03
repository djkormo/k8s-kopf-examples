import time
import kopf
import kubernetes
import yaml
import os
from environs import Env
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


# check if namespace should be under operator controll

def check_namespace(name,excluded_namespaces):
  env = Env()
  env.read_env()  # read .env file, if it exists
  namespace_list = env.list(excluded_namespaces)
  if name in namespace_list:
    print(f"Excluded namespace list: {namespace_list} ")    
    print(f"Excluded namespace found: {name}")
    return True
  else:
     return False  

# When creating or resuming object
@kopf.on.resume('djkormo.github', 'v1alpha1', 'chaos')
@kopf.on.create('djkormo.github', 'v1alpha1', 'chaos')
def create_fn(spec, name, namespace, logger, **kwargs):
    print(f"Creating: {spec}")

LOOP_INTERVAL = int(os.environ['LOOP_INTERVAL'])
@kopf.on.timer('djkormo.github', 'v1alpha1', 'chaos',interval=LOOP_INTERVAL,sharp=True)
def check_object_on_time(spec, name, namespace, logger, **kwargs):
    logger.info(f"Timer: {spec} is invoked")

@kopf.on.delete('djkormo.github', 'v1alpha1', 'chaos')
def delete_fn(spec, name, status, namespace, logger, **kwargs):
    print(f"Deleting: {spec}")
    