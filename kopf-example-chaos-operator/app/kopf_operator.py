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
    logger.info("Number of pods %s in %s namespace", POD_COUNT,namespace)
    for pod in api_response.items:
        logger.info("Pod item: %s\t%s\t%s",pod.metadata.name,pod.status.phase,pod.status.pod_ip)  

    return(POD_COUNT)  

    pod_list = v1.list_namespaced_pod("example")
    for pod in pod_list.items:
        print("%s\t%s\t%s" % (pod.metadata.name,
                              pod.status.phase,
                              pod.status.pod_ip))   


#def get_owner_type(kopf,api,name,namespace,logger):




# https://github.com/kubernetes-client/python/issues/946

def choose_pods(kopf,api,namespace,logger):
    if  False: #constants.OFFLINE_MODE == True:
        return([0],[0])
    else:
        try:
            ret = api.list_namespaced_pod(namespace)
            POD_COUNT = len(ret.items)
            logger.info("There are/is %s pods/pod in %s", POD_COUNT,namespace)

            # Select random pod
            print(ret.items[0].metadata)
            random.shuffle(ret.items)
            # exlude not Running Pods
            while ret.items[0].status.phase not in "Running":
                logger.info("Pod in excluded phase, shuffling")
                random.shuffle(ret.items)

            # check     
            POD_NAME= ret.items[0].metadata.name
            POD_NAMESPACE = ret.items[0].metadata.namespace
            POD_PHASE = ret.items[0].status.phase
            POD_CREATED=ret.items[0].metadata.creation_timestamp
            POD_OWNER=ret.items[0].metadata.owner_references
            owner_references = ret.items[0].metadata.owner_references
            logger.info("Owner reference %s",owner_references)
            if isinstance(owner_references, list):
              owner_name = owner_references[0].name
              owner_kind = owner_references[0].kind
              # owner  StatefulSet
              if owner_kind == 'ReplicaSet':
                apis_api = kubernetes.client.AppsV1Api()  
                replica_set = apis_api.read_namespaced_replica_set(name=owner_name, namespace=namespace)
                owner_references2 = replica_set.metadata.owner_references
                if isinstance(owner_references2, list):
                  print(owner_references2[0].name)
                else:
                  print(owner_name)
                  POD_OWNER='StatefulSet'
               # owner Deployment
              else:
                 print(owner_name)
                 POD_OWNER='Deployment'

              if owner_kind == 'DaemonSet':   
                print(owner_name)
                POD_OWNER='DaemonSet'
                
            logger.info("There is %s in %s in phase %s created %s and controlled by %s to kill",POD_NAME,POD_NAMESPACE,POD_PHASE,POD_CREATED,POD_OWNER)
            return([POD_NAME, POD_NAMESPACE,POD_PHASE])
        except Exception as e:
            logger.error("Unable to list pods: %s", (e))
            return([0],[0],[0])

def delete_pod(kopf,api,name, namespace,logger):
    # Configs can be set in Configuration class directly or using helper utility
    if False: #constants.OFFLINE_MODE == True:
        logging.info("Crate destroyed! Offline mode, so not actually killing any pods")
        return(" ")
    else:
        try:
 
            logger.info("Killing random pod: %s from namespace: %s", name, namespace)
            
            # Delete random pod
            #delete_options = client.V1DeleteOptions()
            api_response = api.delete_namespaced_pod(
                name=name,
                namespace=namespace,
                #body=delete_options
                )
            return(name)  #TODO: Check response for successs? 
        except:
            logger.error("Unable to delete pod")
            return("Error")


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
      [pod_name,pod_namespace,pod_phase] = choose_pods(kopf=kopf,api=api,namespace=name,logger=logger)  
    ## TODO  delete pod 
      delete_pod(kopf=kopf,api=api,name=pod_name, namespace=pod_namespace,logger=logger)

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
      [pod_name,pod_namespace,pod_phase] = choose_pods(kopf=kopf,api=api,namespace=name,logger=logger)
      ## TODO  delete pod 
      api = kubernetes.client.CoreV1Api()

      delete_pod(kopf=kopf,api=api,name=pod_name, namespace=pod_namespace,logger=logger)

@kopf.on.delete('djkormo.github', 'v1alpha1', 'chaos')
def delete_fn(spec, name, status, namespace, logger, **kwargs):
    print(f"Deleting: {spec}")
    