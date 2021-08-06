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
@kopf.on.create('djkormo.github', 'v1alpha1', 'project')
def create_fn(spec, name, namespace, logger, **kwargs):
    print(f"Creating: {spec}")
    api = kubernetes.client.CoreV1Api()

# get context of yaml manifest for namespace

    path = os.path.join(os.path.dirname(__file__), 'namespace.yaml')
    tmpl = open(path, 'rt').read()
    text = tmpl.format(name=name, namespace=namespace)

    data = yaml.safe_load(text)
    kopf.adopt(data)

    ## Create namespace
    try:
      obj = api.create_namespace(
          body=data,
      )
      pprint(obj)
      kopf.append_owner_reference(obj)
      logger.info(f"Namespace child is created: {obj}")
    except ApiException as e:
      print("Exception when calling CoreV1Api->create_namespace: %s\n" % e)  
    
    return {'project-name': obj.metadata.name}

# When updating object
@kopf.on.update('djkormo.github', 'v1alpha1', 'project')
def update_fn(spec, name, status, namespace, logger,diff, **kwargs):
    print(f"Updating: {spec}")
 
@kopf.on.delete('djkormo.github', 'v1alpha1', 'project')
def delete_fn(spec, name, status, namespace, logger, **kwargs):
    print(f"Deleting: {spec}")