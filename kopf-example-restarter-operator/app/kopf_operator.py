import time
import kopf
import kubernetes
import yaml
from environs import Env
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

@kopf.on.resume('k8s.plusnet', 'v1alpha1', 'restarter')
@kopf.on.create('k8s.plusnet', 'v1alpha1', 'restarter')
def create_resume_restarter(spec, name,meta, namespace, logger, **kwargs):
    logger.info(f"Creating or resuming: {spec} is invoked")

    # check for excluded namespace

    if check_namespace(name=name,excluded_namespaces='EXCLUDED_NAMESPACES'):
      return {'restarter-name': name}   

    api = kubernetes.client.CoreV1Api()
    

def restart_deployment(name,namespace,logger,kopf,metadata,spec,api,dry_run,time_to_live):
  logger.info("Restarting Deployment %s in namespace %s", name,namespace)
  if (not dry_run):
    now = datetime.datetime.utcnow()
    now = str(now.isoformat("T") + "Z")
    body = {
        'spec': {
            'template':{
                'metadata': {
                    'annotations': {
                        'kubectl.kubernetes.io/restartedAt': now,
                        'restarter.k8s.plusnet/changedAt': now
                    }
                }
            }
        }
    }
  
    try:
      api_response =api.patch_namespaced_deployment(name, namespace, body=body,pretty='true')
    except ApiException as e:
      print("Exception when calling AppsV1Api->patch_namespaced_deployment: %s\n" % e)

def restart_daemonset(name,namespace,logger,kopf,metadata,spec,status,api,dry_run,time_to_live):
  logger.info("Restarting Daemonset %s in namespace %s", name,namespace)
  if (not dry_run):

    # check last restart time
    restart_time=datetime.datetime(spec.template.metadata.annotations['restarter.k8s.plusnet/changedAt'])
    #if not restart_time:
    #  restart_time=datetime.datetime('1900-01-01T11:54:40Z')

    now = datetime.datetime.utcnow()

    pprint(restart_time,now)

    if (now-restart_time).seconds > time_to_live:
      
      now = str(now.isoformat("T") + "Z")
      body = {
        'spec': {
            'template':{
                'metadata': {
                    'annotations': {
                        'kubectl.kubernetes.io/restartedAt': now,
                        'restarter.k8s.plusnet/changedAt': now
                    }
                }
            }
        }
      }
  
      try:

        api_response =api.patch_namespaced_daemon_set(name, namespace, body=body,pretty='true')
      except ApiException as e:
        print("Exception when calling AppsV1Api->patch_namespaced_daemon_set: %s\n" % e)



def restart_statefulset(name,namespace,logger,kopf,metadata,spec,api,dry_run,time_to_live):
  logger.info("Restarting Statefulset %s in namespace %s", name,namespace)

# use env variable to control loop interval in seconds 
LOOP_INTERVAL = int(os.environ['LOOP_INTERVAL'])
@kopf.timer('k8s.plusnet', 'v1alpha1', 'restarter', interval=LOOP_INTERVAL,sharp=True)
def check_object_on_time(spec, name,meta, namespace, logger, **kwargs):
    logger.info(f"Timer: {spec} is invoked")

    object_namespace = spec.get('namespace')   
    dry_run = spec.get('dry-run',False)
    deployments_enabled = spec.get('deployments',False)
    daemonsets_enabled = spec.get('daemonsets',False)
    statefulsets_enabled = spec.get('statefulsets',False)
    time_to_live = spec.get('ttl',600)
    filter=spec.get('filter','*')

    # check for excluded namespace

    if check_namespace(name=name,excluded_namespaces='EXCLUDED_NAMESPACES'):
      return {'restarter-name': name}   

    # Deployments are under control

    if deployments_enabled:
      try:
        api = kubernetes.client.AppsV1Api()
        api_response = api.list_namespaced_deployment(namespace=object_namespace)
        for d in api_response.items:
          logger.info("Deployment %s has %s available replicas of %s desired replicas", d.metadata.name,d.status.available_replicas,d.spec.replicas)
          if d.spec.replicas>0 :
            restart_deployment(name=d.metadata.name,namespace=d.metadata.namespace,logger=logger,kopf=kopf,metadata=d.metadata,spec=d.spec,api=api,dry_run=dry_run,time_to_live=time_to_live)
      except ApiException as e:
        print("Exception when calling AppsV1Api->list_namespaced_deployment: %s\n" % e)
    
    # Daemonsets are under control
    if daemonsets_enabled:
      try:
        api = kubernetes.client.AppsV1Api()
        api_response = api.list_namespaced_daemon_set(namespace=object_namespace)
        for d in api_response.items:
          logger.info("Daemonset %s has %s desired replicas", d.metadata.name,d.status.desired_number_scheduled)
          if d.status.desired_number_scheduled>0 :
            restart_daemonset(name=d.metadata.name,namespace=d.metadata.namespace,logger=logger,kopf=kopf,metadata=d.metadata,spec=d.spec,status=d.status,api=api,dry_run=dry_run,time_to_live=time_to_live)
      except ApiException as e:
        print("Exception when calling AppsV1Api->list_namespaced_daemon_set: %s\n" % e)


    # Statefulsets are under control
    if statefulsets_enabled:
      try:
        api = kubernetes.client.AppsV1Api()
        api_response = api.list_namespaced_stateful_set(namespace=object_namespace)
        for d in api_response.items:
          logger.info("Statefulset %s has %s available replicas of %s desired replicas", d.metadata.name,d.status.available_replicas,d.spec.replicas)
          if d.spec.replicas>0 :
            restart_statefulset(name=d.metadata.name,namespace=d.metadata.namespace,logger=logger,kopf=kopf,metadata=d.metadata,spec=d.spec,api=api,dry_run=dry_run,time_to_live=time_to_live)
      except ApiException as e:
        print("Exception when calling AppsV1Api->list_namespaced_stateful_set: %s\n" % e)

# When deleting object
@kopf.on.delete('k8s.plusnet', 'v1alpha1', 'restarter')
def delete_fn(spec, name, status, namespace, logger, **kwargs):
    logger.info(f"Deleting: {spec} is invoked")
