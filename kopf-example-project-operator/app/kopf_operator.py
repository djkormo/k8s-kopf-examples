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


# create namespace
def create_namespace(kopf,name,namespace,spec,logger,api,filename):
  path = os.path.join(os.path.dirname(__file__), filename)
  tmpl = open(path, 'rt').read()
  text = tmpl.format(name=name, namespace=namespace)

  data = yaml.safe_load(text)
  kopf.adopt(data)

  ## Create namespace
  try:
    obj = api.create_namespace(namespace=name,
          body=data,
      )
    pprint(obj)
    kopf.append_owner_reference(obj)
    logger.info(f"Namespace child is created: {obj}")
  except ApiException as e:
      print("Exception when calling CoreV1Api->create_namespace: %s\n" % e)  
    
  return {'project-name': obj.metadata.name}

# replace namespace      
def replace_namespace(kopf,name,namespace,spec,logger,api,filename):
  path = os.path.join(os.path.dirname(__file__), filename)
  tmpl = open(path, 'rt').read()

# create resourcequota based on yaml manifest
def create_resourcequota(kopf,name,spec,logger,api,filename):
  path = os.path.join(os.path.dirname(__file__), filename)
  tmpl = open(path, 'rt').read()
  limitrangemaxcpu = spec.get('limitrangemaxcpu',"20000m")
  limitrangemaxmem = spec.get('limitrangemaxmem',"30Gi")
  limitrangemincpu = spec.get('limitrangemincpu',"50m")
  limitrangeminmem = spec.get('limitrangeminmem',"50Mi")
  limitrangedefaultcpu = spec.get('limitrangedefaultcpu',"1000m")
  limitrangedefaultmem = spec.get('limitrangedefaultmem',"1000Mi")
  limitrangedefaultrequestcpu = spec.get('limitrangedefaultrequestcpu',"100m")
  limitrangedefaultrequestmem = spec.get('limitrangedefaultrequestmem',"100Mi")

  text = tmpl.format(name=name,limitrangemaxmem=limitrangemaxmem,
           limitrangemaxcpu=limitrangemaxcpu, 
           limitrangemincpu=limitrangemincpu,
           limitrangeminmem=limitrangeminmem,
           limitrangedefaultcpu=limitrangedefaultcpu,
           limitrangedefaultmem=limitrangedefaultmem,
           limitrangedefaultrequestcpu=limitrangedefaultrequestcpu,
           limitrangedefaultrequestmem=limitrangedefaultrequestmem,
    )

  data = yaml.safe_load(text)
  try:
    obj = api.create_namespaced_resource_quota(
        namespace=name,
        body=data,
      )
    kopf.append_owner_reference(obj)
    #logger.info(f"LimitRange child is created: {obj}")
  except ApiException as e:
    print("Exception when calling CoreV1Api->create_namespaced_resource_quota: %s\n" % e)
  kopf.adopt(data)

# replace resourcequota based on yaml manifest
def replace_resourcequota(kopf,name,spec,logger,api,filename):
  path = os.path.join(os.path.dirname(__file__), filename)
  tmpl = open(path, 'rt').read()
  limitrangemaxcpu = spec.get('limitrangemaxcpu',"20000m")
  limitrangemaxmem = spec.get('limitrangemaxmem',"30Gi")
  limitrangemincpu = spec.get('limitrangemincpu',"50m")
  limitrangeminmem = spec.get('limitrangeminmem',"50Mi")
  limitrangedefaultcpu = spec.get('limitrangedefaultcpu',"1000m")
  limitrangedefaultmem = spec.get('limitrangedefaultmem',"1000Mi")
  limitrangedefaultrequestcpu = spec.get('limitrangedefaultrequestcpu',"100m")
  limitrangedefaultrequestmem = spec.get('limitrangedefaultrequestmem',"100Mi")

  text = tmpl.format(name=name,limitrangemaxmem=limitrangemaxmem,
           limitrangemaxcpu=limitrangemaxcpu, 
           limitrangemincpu=limitrangemincpu,
           limitrangeminmem=limitrangeminmem,
           limitrangedefaultcpu=limitrangedefaultcpu,
           limitrangedefaultmem=limitrangedefaultmem,
           limitrangedefaultrequestcpu=limitrangedefaultrequestcpu,
           limitrangedefaultrequestmem=limitrangedefaultrequestmem,
    )

  data = yaml.safe_load(text)
  try:
    obj = api.replace_namespaced_resource_quota(
        namespace=name,
        name=name,
        body=data,
      )
    kopf.append_owner_reference(obj)
    #logger.info(f"LimitRange child is created: {obj}")
  except ApiException as e:
    print("Exception when calling CoreV1Api->replace_namespaced_resource_quota: %s\n" % e)
  kopf.adopt(data)  
  



# When creating or resuming object
@kopf.on.resume('djkormo.github', 'v1alpha1', 'project')
@kopf.on.create('djkormo.github', 'v1alpha1', 'project')
def create_fn(spec, name, namespace, logger, **kwargs):
    print(f"Creating: {spec}")
    api = kubernetes.client.CoreV1Api()
    
    # check for excluded namespace

    if check_namespace(name=namespace,excluded_namespaces='EXCLUDED_NAMESPACES'):
      return {'project-operator-name': namespace}    


    # create namespace 
    api = kubernetes.client.CoreV1Api()

    try: 
      api_response = api.list_namespace() 
      #pprint(api_response)
      l_namespace=[]
      for i in api_response.items:
        print("Namespaces list: %s\t name:" %
          (i.metadata.name))
        l_namespace.append(i.metadata.name)
    except ApiException as e:
      print("Exception when calling CoreV1Api->list_namespaced_limit_range: %s\n" % e)

    if name not in l_namespace:
      create_namespace(kopf=kopf,name=name,namespace=namespace,spec=spec,logger=logger,api=api,filename='namespace.yaml')
    else:
      replace_namespace(kopf=kopf,name=name,spec=spec,logger=logger,api=api,filename='namespace.yaml')
    

# When updating object
@kopf.on.update('djkormo.github', 'v1alpha1', 'project')
def update_fn(spec, name, status, namespace, logger,diff, **kwargs):
    print(f"Updating: {spec}")
    api = kubernetes.client.CoreV1Api()
    
    # check for excluded namespace

    if check_namespace(name=namespace,excluded_namespaces='EXCLUDED_NAMESPACES'):
      return {'project-operator-name': namespace} 

    try: 
      api_response = api.list_namespace() 
      #pprint(api_response)
      l_namespace=[]
      for i in api_response.items:
        print("Namespaces list: %s\t name:" %
          (i.metadata.name))
        l_namespace.append(i.metadata.name)
    except ApiException as e:
      print("Exception when calling CoreV1Api->list_namespace: %s\n" % e)

    if name not in l_namespace:
      create_namespace(kopf=kopf,name=name,spec=spec,logger=logger,api=api,filename='namespace.yaml')
    else:
      replace_namespace(kopf=kopf,name=name,spec=spec,logger=logger,api=api,filename='namespace.yaml')
    
LOOP_INTERVAL = int(os.environ['LOOP_INTERVAL'])
@kopf.on.timer('djkormo.github', 'v1alpha1', 'project',interval=LOOP_INTERVAL,sharp=True)
def check_object_on_time(spec, name, namespace, logger, **kwargs):
    logger.info(f"Timer: {spec} is invoked")

    api = kubernetes.client.CoreV1Api()

    # check for excluded namespace

    if check_namespace(name=namespace,excluded_namespaces='EXCLUDED_NAMESPACES'):
      return {'project-operator-name': namespace} 

    try: 
      api_response = api.list_namespace() 
      #pprint(api_response)
      l_namespace=[]
      for i in api_response.items:
        print("Namespaces list: %s\t name:" %
          (i.metadata.name))
        l_namespace.append(i.metadata.name)
    except ApiException as e:
      print("Exception when calling CoreV1Api->list_namespace: %s\n" % e)

    if name not in l_namespace:
      create_namespace(kopf=kopf,name=name,spec=spec,logger=logger,api=api,filename='namespace.yaml')
    else:
      replace_namespace(kopf=kopf,name=name,spec=spec,logger=logger,api=api,filename='namespace.yaml')
    

@kopf.on.delete('djkormo.github', 'v1alpha1', 'project')
def delete_fn(spec, name, status, namespace, logger, **kwargs):
    print(f"Deleting: {spec}")