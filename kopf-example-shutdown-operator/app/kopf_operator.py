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


def turn_off_deployment(name,namespace,logger,kopf,spec,api,dry_run):
  logger.info("Turning off Deployment %s in namespace %s", name,namespace)
  
  #replicas = api.read_namespaced_deployment_scale(name=name, namespace=namespace)
 
  # how many replicas we have
  replicas = spec.get('replicas')  

  logger.info("Deployment %s in %s namespace has %s replicas", name,namespace,replicas)
  
  # save replicas and timestamp to proper annotations
  
  now = datetime.datetime.utcnow()
  now = str(now.isoformat("T") + "Z")
  body = {
                'metadata': {
                    'annotations': {
                        'shutdown.djkormo.github/replicas': 1,
                        'shutdown.djkormo.github/changedAt': now
                    }
                }
    }

  body = {"metadata": {"annotations": {"shutdown.djkormo.github/replicas": "1" }}}
  if (not dry_run):
    try:
      api_response =api.patch_namespaced_deployment(name, namespace, body=body)
    except ApiException as e:
      if e.status == 404:
        logger.info("No deployment found")
      else:
        logger.info("Exception when calling AppsV1Api->patch_namespaced_deployment: %s\n" % e)

  # TODO 

  if (not dry_run):
    # set replicas to zero
    logger.info("Setting Deployment %s in %s namespace to zero replicas",name,namespace)

    body = {"spec": {"replicas": 0}}
    try:
      api_response =api.patch_namespaced_deployment_scale(name, namespace, body=body)
    except ApiException as e:
      if e.status == 404:
         logger.info("No deployment found")
      else:
        logger.info("Exception when calling AppsV1Api->patch_namespaced_deployment_scale: %s\n" % e)
  



def turn_off_daemonset(name,namespace,logger,kopf,spec,api,dry_run):
  logger.info("Turning off Daemonset %s in namespace %s", name,namespace)  
  now = datetime.datetime.utcnow()
  now = str(now.isoformat("T") + "Z")

  body = {
            'metadata': {
              'annotations': {
                  'shutdown.djkormo.github/replicas': "1",
                    'shutdown.djkormo.github/changedAt': now
                    }
                }
    }
    

  if (not dry_run):
    try:
      api_response =api.patch_namespaced_daemon_set(name, namespace, body=body)
      pprint(api_response)
    except ApiException as e:
      if e.status == 404:
        logger.info("No daemonset found")
      else:
        logger.info("Exception when calling AppsV1Api->patch_namespaced_daemonset_set: %s\n" % e)
  
 
  body={"spec": {"template": {"spec": {"nodeSelector": {"non-existing": "true"}}}}}

  if (not dry_run):
    try:
      api_response =api.patch_namespaced_daemon_set(name, namespace, body=body)
      pprint(api_response)
    except ApiException as e:
      if e.status == 404:
        logger.info("No daemonset found")
      else:
        logger.info("Exception when calling AppsV1Api->patch_namespaced_daemonset_set: %s\n" % e)


  ##kubectl -n <namespace> patch daemonset <name-of-daemon-set> -p '{"spec": {"template": {"spec": {"nodeSelector": {"non-existing": "true"}}}}}



def turn_off_statefulset(name,namespace,logger,kopf,spec,api,dry_run):
  logger.info("Turning off Statefulset %s in namespace %s", name,namespace) 
  # how many replicas we have
  replicas = spec.get('replicas')  

  logger.info("Statefulset %s in %s namespace has %s replicas", name,namespace,replicas)
  # save replicas to proper annotation 
  now = datetime.datetime.utcnow()
  now = str(now.isoformat("T") + "Z")
  body = {

                'metadata': {
                    'annotations': {
                        'shutdown.djkormo.github/replicas': replicas,
                        'shutdown.djkormo.github/changedAt': now
                    }
                }
    }
  body = {"metadata": {"annotations": {"shutdown.djkormo.github/replicas": "1" }}}
  
  if (not dry_run):
    try:
      api_response =api.patch_namespaced_stateful_set(name, namespace, body=body)
      pprint(api_response)
    except ApiException as e:
      if e.status == 404:
        logger.info("No statefulset found")
      else:
        logger.info("Exception when calling AppsV1Api->patch_namespaced_statefulset_scale: %s\n" % e)

  # TODO 
  if (not dry_run):
    # set replicas to zero
    logger.info("Setting Statefulset %s in %s namespace to zero replicas",name,namespace)
    body = {"spec": {"replicas": 0}}
    try:
      api_response =api.patch_namespaced_stateful_set_scale(name, namespace, body=body)
      pprint(api_response)
    except ApiException as e:
      if e.status == 404:
        logger.info("No deployment found")
      else:
        logger.info("Exception when calling AppsV1Api->patch_namespaced_stateful_set_scale: %s\n" % e)
     


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
  dry_run = spec.get('dry-run',False)
  deployments_enabled = spec.get('deployments',False)
  daemonsets_enabled = spec.get('daemonsets',False)
  statefulsets_enabled = spec.get('statefulsets',False)

  # check for excluded namespace
  if check_namespace(name=name,excluded_namespaces='EXCLUDED_NAMESPACES'):
    return {'shutdown-operator-name': namespace}   
     
  # check if deployment is turned on
  # TODO
  # list all deployments

  api = kubernetes.client.AppsV1Api()
  if deployments_enabled:
    try:
      api_response = api.list_namespaced_deployment(namespace=object_namespace)
      for d in api_response.items:
        logger.info("Deployment %s has %s available replicas of %s desired replicas", d.metadata.name,d.status.available_replicas,d.spec.replicas)
        if d.spec.replicas>0 :
          turn_off_deployment(name=d.metadata.name,namespace=d.metadata.namespace,logger=logger,kopf=kopf,spec=spec,api=api,dry_run=dry_run)
    except ApiException as e:
      print("Exception when calling AppsV1Api->list_namespaced_deployment: %s\n" % e)



  # check if daemonset is turned on
  # TODO
  # list all daemonsets
  if daemonsets_enabled:
    api = kubernetes.client.AppsV1Api()
    try:
      api_response = api.list_namespaced_daemon_set(namespace=object_namespace)
      for d in api_response.items:
        logger.info("Daemonset %s has %s desired replicas", d.metadata.name,d.status.desired_number_scheduled)
        if d.status.desired_number_scheduled>0 :
          turn_off_daemonset(name=d.metadata.name,namespace=d.metadata.namespace,logger=logger,kopf=kopf,spec=spec,api=api,dry_run=dry_run)
    except ApiException as e:
      print("Exception when calling AppsV1Api->list_namespaced_daemon_set: %s\n" % e)

  # check if statefulset is turned on
  # TODO
  # list all statefulset
  if statefulsets_enabled :
    api = kubernetes.client.AppsV1Api()
    try:
      api_response = api.list_namespaced_stateful_set(namespace=object_namespace)
      for d in api_response.items:
        logger.info("Statefulset %s has %s replicas", d.metadata.name,d.spec.replicas)
        if d.spec.replicas>0 :
          turn_off_statefulset(name=d.metadata.name,namespace=d.metadata.namespace,logger=logger,kopf=kopf,spec=spec,api=api,dry_run=dry_run)
    except ApiException as e:
      print("Exception when calling AppsV1Api->list_namespaced_stateful_set: %s\n" % e)


@kopf.on.delete('djkormo.github', 'v1alpha1', 'shutdown')
def delete_fn(spec, name, status, namespace, logger, **kwargs):
    print(f"Deleting: {name} with {spec}")
    