import time
import kopf
import kubernetes
import yaml
import json
import os
from environs import Env
from kubernetes.client.rest import ApiException
from pprint import pprint
import datetime
import random
import asyncio


@kopf.on.startup()
async def startup_fn_simple(logger, **kwargs):
    logger.info('Environment variables:')
    for k, v in os.environ.items():
        logger.info(f'{k}={v}')
    logger.info('Starting in 5s...')
    await asyncio.sleep(5)

# for Kubernetes probes

@kopf.on.probe(id='now')
def get_current_timestamp(**kwargs):
    return datetime.datetime.utcnow().isoformat()

@kopf.on.probe(id='random')
def get_random_value(**kwargs):
    return random.randint(0, 1_000_000)


# check if namespace should be under operator control

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


# create namespace
def create_namespace(kopf,name,namespace,meta,spec,logger,api,filename):
  path = os.path.join(os.path.dirname(__file__), filename)
  tmpl = open(path, 'rt').read()
  text = tmpl.format(name=name, namespace=namespace)

  data = yaml.safe_load(text)
  kopf.adopt(data)

  ## Create namespace
  try:
    obj = api.create_namespace(
          body=data,
      )
    kopf.append_owner_reference(obj)
    logger.info(f"Namespace child is created: {obj}")
  except ApiException as e:
      print("Exception when calling CoreV1Api->create_namespace: %s\n" % e)  
    
  # get annotations from parent object
  annotations=meta['annotations']
  
  # get labels from parrent object 

  labels=meta['labels']

  logger.info(f"Project ANNOTATIONS {annotations} and LABELS {labels}\n")
 
  # mock data
  #labels = {"owner": "djkormo", "name": "project"}
  #annotations = {"description": "test","confirmation":"yes"}
  
  # Apply annotations to namespace
  try:
    obj = api.patch_namespace(
          name=name,
          body={"metadata": {"annotations": annotations} }
      )
  # Apply labels to namespace  
    obj = api.patch_namespace(
          name=name,
          body={"metadata": {"labels": labels}}
      )
    #logger.info(f"Namespace child is patched: {obj}")
  except ApiException as e:
      print("Exception when calling CoreV1Api->patch_namespace: %s\n" % e)  

  return {'project-name': obj.metadata.name}

# replace namespace      
def replace_namespace(kopf,name,namespace,meta,spec,logger,api,filename):

  path = os.path.join(os.path.dirname(__file__), filename)
  tmpl = open(path, 'rt').read()

  # get annotations from parent object
  annotations=meta['annotations']
  # get labels from parent object
  labels=meta['labels'] 
  logger.info(f"Project ANNOTATIONS {annotations} and LABELS {labels}\n")
 
  # mock data
  #labels = {"owner": "djkormo", "name": "project"}
  #labels = {'env': 'kubernetes', 'name': 'project', 'owner': 'djkormo', 'type': 'operator'}
  #labels=json.dump(labels)
  #annotations = {"description": "test","confirmation":"yes"}
  
  logger.info(f"Project LABELS {labels} \n")
  
  # Apply annotations to namespace
  try:
    obj = api.patch_namespace(
          name=name,
          body={"metadata": {"annotations": annotations}}
      )
  # Apply labels to namespace
    obj = api.patch_namespace(
          name=name,
          body={"metadata": {"labels": labels}  }
      )
    #logger.info(f"Namespace child is patched: {obj}")
  except ApiException as e:
      print("Exception when calling CoreV1Api->patch_namespace: %s\n" % e)  

# create resourcequota based on yaml manifest
def create_resourcequota(kopf,name,meta,spec,logger,api,filename):

  path = os.path.join(os.path.dirname(__file__), filename)
  tmpl = open(path, 'rt').read()

  resourcequotarequestscpu = spec.get('resourcequotarequestscpu',1)
  if not resourcequotarequestscpu:
    raise kopf.PermanentError(f"resourcequotarequestscpu must be set. Got {resourcequotarequestscpu!r}.")

  resourcequotarequestsmemory = spec.get('resourcequotarequestsmemory',1)
  if not resourcequotarequestsmemory:
    raise kopf.PermanentError(f"resourcequotarequestsmemory must be set. Got {resourcequotarequestsmemory!r}.")
    
  resourcequotalimitscpu=spec.get('resourcequotalimitscpu',1)
    
  resourcequotalimitsmemory=spec.get('resourcequotalimitsmemory',1)
  resourcequotacountjobsbatch=spec.get('resourcequotacountjobsbatch',1)
  resourcequotacountingresses=spec.get('resourcequotacountingresses',1)
  resourcequotapods=spec.get('resourcequotapods',1)
  resourcequotaservices=spec.get('resourcequotaservices',1)
  resourcequotaconfigmaps=spec.get('resourcequotaconfigmaps',1)
  resourcequotapersistentvolumeclaims=spec.get('resourcequotapersistentvolumeclaims',1)
  resourcequotareplicationcontrollers=spec.get('resourcequotareplicationcontrollers',1)
  resourcequotasecrets=spec.get('resourcequotasecrets',1)
  resourcequotaservicesloadbalancers=spec.get('resourcequotaservicesloadbalancers',1)

  text = tmpl.format(name=name,resourcequotarequestscpu=resourcequotarequestscpu,
           resourcequotarequestsmemory=resourcequotarequestsmemory, 
           resourcequotalimitscpu=resourcequotalimitscpu,
           resourcequotalimitsmemory=resourcequotalimitsmemory,
           resourcequotacountjobsbatch=resourcequotacountjobsbatch,
           resourcequotacountingresses=resourcequotacountingresses,
           resourcequotapods=resourcequotapods,
           resourcequotaservices=resourcequotaservices,
           resourcequotaconfigmaps=resourcequotaconfigmaps,
           resourcequotapersistentvolumeclaims=resourcequotapersistentvolumeclaims,
           resourcequotareplicationcontrollers=resourcequotareplicationcontrollers,
           resourcequotasecrets=resourcequotasecrets,
           resourcequotaservicesloadbalancers=resourcequotaservicesloadbalancers
    )

  #pprint(text)
    
  data = yaml.safe_load(text)
  try:
    obj = api.create_namespaced_resource_quota(
        namespace=name,
        body=data,
      )
    kopf.append_owner_reference(obj)
    #logger.info(f"ResourceQuota child is created: {obj}")
  except ApiException as e:
    print("Exception when calling CoreV1Api->create_namespaced_resource_quota: %s\n" % e)
  kopf.adopt(data)

# replace resourcequota based on yaml manifest
def replace_resourcequota(kopf,name,meta,spec,logger,api,filename):

  path = os.path.join(os.path.dirname(__file__), filename)
  tmpl = open(path, 'rt').read()

  resourcequotarequestscpu = spec.get('resourcequotarequestscpu',1)
  if not resourcequotarequestscpu:
    raise kopf.PermanentError(f"resourcequotarequestscpu must be set. Got {resourcequotarequestscpu!r}.")

  resourcequotarequestsmemory = spec.get('resourcequotarequestsmemory',1)
  if not resourcequotarequestsmemory:
    raise kopf.PermanentError(f"resourcequotarequestsmemory must be set. Got {resourcequotarequestsmemory!r}.")
    
  resourcequotalimitscpu=spec.get('resourcequotalimitscpu',1)
    
  resourcequotalimitsmemory=spec.get('resourcequotalimitsmemory',1)
  resourcequotacountjobsbatch=spec.get('resourcequotacountjobsbatch',1)
  resourcequotacountingresses=spec.get('resourcequotacountingresses',1)
  resourcequotapods=spec.get('resourcequotapods',1)
  resourcequotaservices=spec.get('resourcequotaservices',1)
  resourcequotaconfigmaps=spec.get('resourcequotaconfigmaps',1)
  resourcequotapersistentvolumeclaims=spec.get('resourcequotapersistentvolumeclaims',1)
  resourcequotareplicationcontrollers=spec.get('resourcequotareplicationcontrollers',1)
  resourcequotasecrets=spec.get('resourcequotasecrets',1)
  resourcequotaservicesloadbalancers=spec.get('resourcequotaservicesloadbalancers',1)

  text = tmpl.format(name=name,resourcequotarequestscpu=resourcequotarequestscpu,
           resourcequotarequestsmemory=resourcequotarequestsmemory, 
           resourcequotalimitscpu=resourcequotalimitscpu,
           resourcequotalimitsmemory=resourcequotalimitsmemory,
           resourcequotacountjobsbatch=resourcequotacountjobsbatch,
           resourcequotacountingresses=resourcequotacountingresses,
           resourcequotapods=resourcequotapods,
           resourcequotaservices=resourcequotaservices,
           resourcequotaconfigmaps=resourcequotaconfigmaps,
           resourcequotapersistentvolumeclaims=resourcequotapersistentvolumeclaims,
           resourcequotareplicationcontrollers=resourcequotareplicationcontrollers,
           resourcequotasecrets=resourcequotasecrets,
           resourcequotaservicesloadbalancers=resourcequotaservicesloadbalancers
    )
    
  data = yaml.safe_load(text)
  try:
    obj = api.replace_namespaced_resource_quota(
        namespace=name,
        name=name,
        body=data,
      )
    kopf.append_owner_reference(obj)
    #logger.info(f"ResurceQuota child is replaced: {obj}")
  except ApiException as e:
    print("Exception when calling CoreV1Api->replace_namespaced_resource_quota: %s\n" % e)
  kopf.adopt(data)  
  


    
# use env variable to control loop interval in seconds
try:
  LOOP_INTERVAL = int(os.environ['LOOP_INTERVAL'])
except:
  LOOP_INTERVAL=30
  print(f"Variable LOOP_INTERVAL is not set, using {LOOP_INTERVAL}s as default")    

@kopf.on.resume('djkormo.github', 'v1alpha1', 'project')
@kopf.on.create('djkormo.github', 'v1alpha1', 'project')
# When updating object
@kopf.on.update('djkormo.github', 'v1alpha1', 'project')
@kopf.on.timer('djkormo.github', 'v1alpha1', 'project',interval=LOOP_INTERVAL,sharp=True)
def check_object_on_loop(spec, name, status, namespace,meta, logger, **kwargs):
    logger.info(f"Timer: {spec} is invoked")

    api = kubernetes.client.CoreV1Api()

    # check for excluded namespace

    if check_namespace(name=namespace,excluded_namespaces='EXCLUDED_NAMESPACES'):
      return {'project-operator-name': namespace} 

    try: 
      api_response = api.list_namespace() 
      l_namespace=[]
      for i in api_response.items:
        logger.debug("Namespaces list: %s\t name:" %(i.metadata.name))
        l_namespace.append(i.metadata.name)
    except ApiException as e:
      print("Exception when calling CoreV1Api->list_namespace: %s\n" % e)

    if name not in l_namespace:
      create_namespace(kopf=kopf,name=name,namespace=namespace,meta=meta,spec=spec,logger=logger,api=api,filename='namespace.yaml')
    else:
      replace_namespace(kopf=kopf,name=name,namespace=namespace,meta=meta,spec=spec,logger=logger,api=api,filename='namespace.yaml')
    

    # create or update resourcequota
    
    api = kubernetes.client.CoreV1Api()

    try: 
      api_response = api.list_namespaced_resource_quota(namespace=name) 
      #pprint(api_response)
      l_resoucequota=[]
      for i in api_response.items:
        logger.debug("ResourceQuota namespace: %s\t name: %s" %
          (i.metadata.namespace, i.metadata.name))
        l_resoucequota.append(i.metadata.name)
    except ApiException as e:
      print("Exception when calling CoreV1Api->list_namespaced_resource_quota: %s\n" % e)

    if name not in l_resoucequota:
      create_resourcequota(kopf=kopf,name=name,meta=meta,spec=spec,logger=logger,api=api,filename='resourcequota.yaml')
    else:
      replace_resourcequota(kopf=kopf,name=name,meta=meta,spec=spec,logger=logger,api=api,filename='resourcequota.yaml')
 

@kopf.on.delete('djkormo.github', 'v1alpha1', 'project')
def delete_fn(spec, name, status, namespace, logger, **kwargs):
    print(f"Deleting: {spec}")
    
