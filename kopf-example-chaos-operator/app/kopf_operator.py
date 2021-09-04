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

# count all pods in namespace
def count_pods(kopf,api,namespace,logger):
    
    api_response = api.list_namespaced_pod(namespace)
    POD_COUNT = len(api_response.items)
    logger.info("Number of pods: %s in %s", POD_COUNT,namespace)

    return(POD_COUNT)  

    pod_list = v1.list_namespaced_pod("example")
    for pod in pod_list.items:
        print("%s\t%s\t%s" % (pod.metadata.name,
                              pod.status.phase,
                              pod.status.pod_ip))   

def list_pods(kopf,api,namespace,logger):
    if  False: #constants.OFFLINE_MODE == True:
        return([0],[0])
    else:
        try:
            ret = api.list_namespaced_pod(namespace)
            POD_COUNT = len(ret.items)
            logger.info("There are/is %s pods/pod in %s", POD_COUNT,namespace)

            # Select random pod
            # print(ret.items[0].metadata.namespace)
            random.shuffle(ret.items)
            #while ret.items[0].metadata.namespace in constants.EXCLUDES_LIST:
            #    logger.info("Pod in excluded namespace, shuffling")
            #    random.shuffle(ret.items)
            POD_TO_KILL = ret.items[0].metadata.name
            POD_NAMESPACE = ret.items[0].metadata.namespace
            logger.info("There is: %s in %s to kill",POD_TO_KILL,POD_NAMESPACE)
            return([POD_TO_KILL, POD_NAMESPACE])
        except Exception as e:
            logger.error("Unable to list pods: %s", (e))
            return([0],[0])


# When creating or resuming object
@kopf.on.resume('djkormo.github', 'v1alpha1', 'chaos')
@kopf.on.create('djkormo.github', 'v1alpha1', 'chaos')
def create_fn(spec, name, namespace, logger, **kwargs):
    print(f"Creating: {spec}")
    
    # check for excluded namespace

    if check_namespace(name=name,excluded_namespaces='EXCLUDED_NAMESPACES'):
      return {'chaos-operator-name': namespace}    

    # count pods in our namespace
    
    api = kubernetes.client.CoreV1Api()

    pod_count=count_pods(kopf=kopf,api=api,namespace=name,logger=logger)
    # choose one pod to delete
    if pod_count>0:
      [pod_name,pod_namespace] = list_pods(kopf=kopf,api=api,namespace=name,logger=logger)
    ## TODO  delete pod 
     

LOOP_INTERVAL = int(os.environ['LOOP_INTERVAL'])
@kopf.on.timer('djkormo.github', 'v1alpha1', 'chaos',interval=LOOP_INTERVAL,sharp=True)
def check_object_on_time(spec, name, namespace, logger, **kwargs):
    logger.info(f"Timer: for {name} with {spec} is invoked")
        # check for excluded namespace

    if check_namespace(name=name,excluded_namespaces='EXCLUDED_NAMESPACES'):
      return {'chaos-operator-name': namespace}    

    # count pods in our namespace
    
    api = kubernetes.client.CoreV1Api()

    pod_count=count_pods(kopf=kopf,api=api,namespace=name,logger=logger)
    # choose one pod to delete
    if pod_count>0:
      [pod_name,pod_namespace] = list_pods(kopf=kopf,api=api,namespace=name,logger=logger)
    ## TODO  delete pod 

@kopf.on.delete('djkormo.github', 'v1alpha1', 'chaos')
def delete_fn(spec, name, status, namespace, logger, **kwargs):
    print(f"Deleting: {spec}")
    