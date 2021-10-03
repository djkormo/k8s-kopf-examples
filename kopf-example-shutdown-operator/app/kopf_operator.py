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
import json

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


def turn_off_deployment(name,namespace,logger,kopf,spec,api):
  logger.info("Turning off Deployment %s in namespace %s", name,namespace)
  pass

def turn_off_daemonset(name,namespace,logger,kopf,spec,api):
  logger.info("Turning off Daemonset %s in namespace %s", name,namespace)    
  pass

def turn_off_statefulset(name,namespace,logger,kopf,spec,api):
  logger.info("Turning off Statefulset %s in namespace %s", name,namespace)    
  pass

# When creating or resuming object
@kopf.on.resume('djkormo.github', 'v1alpha1', 'shutdown')
@kopf.on.create('djkormo.github', 'v1alpha1', 'shutdown')
def create_fn(spec, name, namespace, logger, **kwargs):
    print(f"Creating or resuming: {name} with {spec}")
    
    # check for excluded namespace
    if check_namespace(name=name,excluded_namespaces='EXCLUDED_NAMESPACES'):
      return {'shutdown-operator-name': namespace}    


LOOP_INTERVAL = int(os.environ['LOOP_INTERVAL'])
@kopf.on.timer('djkormo.github', 'v1alpha1', 'shutdown',interval=LOOP_INTERVAL,sharp=True)
def check_object_on_time(spec, name, namespace, logger, **kwargs):
  logger.info(f"Timer: for {name} with {spec} is invoked")
        
  object_namespace = spec.get('namespace')   

  # check for excluded namespace
  if check_namespace(name=name,excluded_namespaces='EXCLUDED_NAMESPACES'):
    return {'shutdown-operator-name': namespace}   
     
  # check if deployment is turned on
  # TODO
  # list all deployments

  api = kubernetes.client.AppsV1Api()

  try:
    api_response = api.list_namespaced_deployment(namespace=object_namespace)
    for d in api_response.items:
        logger.info("Deployment %s has %s available replicas of %s replicas", d.metadata.name,d.status.available_replicas,d.spec.replicas)
        if d.spec.replicas>0 :
          turn_off_deployment(name=d.metadata.name,namespace=d.metadata.namespace,logger=logger,logger=logger,kopf=kopf,spec=spec,api=api)
  except ApiException as e:
    print("Exception when calling AppsV1Api->list_namespaced_deployment: %s\n" % e)



  # check if daemonset is turned on
  # TODO
  # list all daemonsets

  api = kubernetes.client.AppsV1Api()
  try:
    api_response = api.list_namespaced_daemon_set(namespace=object_namespace)
    for d in api_response.items:
        logger.info("Daemonset %s ", d.metadata.name)
        turn_off_daemonset(name=d.metadata.name,namespace=d.metadata.namespace,logger=logger,kopf=kopf,spec=spec,api=api)
  except ApiException as e:
    print("Exception when calling AppsV1Api->list_namespaced_daemon_set: %s\n" % e)

  # check if statefulset is turned on
  # TODO
  # list all statefulset
  api = kubernetes.client.AppsV1Api()
  try:
    api_response = api.list_namespaced_stateful_set(namespace=object_namespace)
    for d in api_response.items:
      logger.info("Statefulset %s has %s replicas", d.metadata.name,d.spec.replicas)
      if d.spec.replicas>0 :
        turn_off_statefulset(name=d.metadata.name,namespace=d.metadata.namespace,logger=logger,kopf=kopf,spec=spec,api=api)
  except ApiException as e:
    print("Exception when calling AppsV1Api->list_namespaced_stateful_set: %s\n" % e)


@kopf.on.delete('djkormo.github', 'v1alpha1', 'shutdown')
def delete_fn(spec, name, status, namespace, logger, **kwargs):
    print(f"Deleting: {name} with {spec}")
    