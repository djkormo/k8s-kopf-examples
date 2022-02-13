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

# create limitrange based on yaml manifest
def create_limitrange(kopf,name,meta,spec,logger,api,filename):
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
    obj = api.create_namespaced_limit_range(
        namespace=name,
        body=data,
      )
    kopf.append_owner_reference(obj)
    #logger.info(f"LimitRange child is created: {obj}")
  except ApiException as e:
    logger.error("Exception when calling CoreV1Api->create_namespaced_limit_range: %s\n" % e)
  kopf.adopt(data)

# replace limitrange based on yaml manifest
def replace_limitrange(kopf,name,meta,spec,logger,api,filename):
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
    obj = api.replace_namespaced_limit_range(
        namespace=name,
        name=name,
        body=data,
      )
    kopf.append_owner_reference(obj)
    #logger.info(f"LimitRange child is created: {obj}")
  except ApiException as e:
    logger.error("Exception when calling CoreV1Api->replace_namespaced_limit_range: %s\n" % e)
  kopf.adopt(data)  
  
# create networkpolicy based on yaml manifest  
def create_networkpolicy(kopf,name,spec,logger,api,filename):
  path = os.path.join(os.path.dirname(__file__), filename)
  tmpl = open(path, 'rt').read()
  #pprint(tmpl)
  data = yaml.safe_load(tmpl)
  kopf.adopt(data)
  try:
    obj = api.create_namespaced_network_policy(
        namespace=name,
        body=data,
      )
    #pprint(obj)
    kopf.append_owner_reference(obj)
    #logger.info(f"NetworkPolicy child is created: {obj}")
  except ApiException as e:
    logger.error("Exception when calling NetworkingV1Api->create_namespaced_network_policy: %s\n" % e)

# replace networkpolicy based on yaml manifest  
def replace_networkpolicy(kopf,name,spec,logger,api,filename,policyname):
  path = os.path.join(os.path.dirname(__file__), filename)
  tmpl = open(path, 'rt').read()
  #pprint(tmpl)
  data = yaml.safe_load(tmpl)
  kopf.adopt(data)
  try:
    obj = api.replace_namespaced_network_policy(
        namespace=name,
        name=policyname,
        body=data,
      )
    #pprint(obj)
    kopf.append_owner_reference(obj)
    #logger.info(f"NetworkPolicy child is created: {obj}")
  except ApiException as e:
    logger.error("Exception when calling NetworkingV1Api->replace_namespaced_network_policy: %s\n" % e)
   
os.environ['LOOP_INTERVAL']="30"
# use env variable to control loop interval in seconds 
LOOP_INTERVAL = int(os.environ['LOOP_INTERVAL'])


# When creating, updating or resuming object 
@kopf.on.resume('namespace')
@kopf.on.create('namespace')
@kopf.on.update('namespace')
# Endless reconcilation loop
@kopf.timer('namespace', interval=LOOP_INTERVAL,sharp=True)
def check_object_on_loop(spec, name, namespace,meta, logger, **kwargs):
    logger.info(f"Creating: {spec}")

    api = kubernetes.client.CoreV1Api()

    # check for excluded namespace

    if check_namespace(name=name,excluded_namespaces='EXCLUDED_NAMESPACES'):
      return {'limitrange-np-name': name}   
      # end of story 

    # create limitrange 
    api = kubernetes.client.CoreV1Api()

    try: 
      api_response = api.list_namespaced_limit_range(namespace=name) 
      l_limitrange=[]
      for i in api_response.items:
        logger.debug("Limitrange namespace: %s\t name: %s" %
          (i.metadata.namespace, i.metadata.name))
        l_limitrange.append(i.metadata.name)
    except ApiException as e:
      logger.error("Exception when calling CoreV1Api->list_namespaced_limit_range: %s\n" % e)

    if name not in l_limitrange:
      create_limitrange(kopf=kopf,name=name,meta=meta,spec=spec,logger=logger,api=api,filename='limitrange.yaml')
    else:
      replace_limitrange(kopf=kopf,name=name,meta=meta,spec=spec,logger=logger,api=api,filename='limitrange.yaml')

    api = kubernetes.client.NetworkingV1Api()

    try: 
      api_response = api.list_namespaced_network_policy(namespace=name) 
      l_netpol=[]
      for i in api_response.items:
        logger.debug("NetworkPolicy namespace: %s\t name: %s" %
          (i.metadata.namespace, i.metadata.name))
        l_netpol.append(i.metadata.name) 
    except ApiException as e:
      logger.error("Exception when calling NetworkingV1Api->list_namespaced_network_policy: %s\n" % e)

      
    # update/patch networkpolicy
    
    if "allow-dns-access" not in l_netpol:
      create_networkpolicy(kopf=kopf,name=name,spec=spec,logger=logger,api=api,filename='networkpolicy-allow-dns-access.yaml')
    else:
      replace_networkpolicy(kopf=kopf,name=name,spec=spec,logger=logger,api=api,filename='networkpolicy-allow-dns-access.yaml',policyname='allow-dns-access')   
    
    if "default-deny-egress" not in l_netpol:
      create_networkpolicy(kopf=kopf,name=name,spec=spec,logger=logger,api=api,filename='networkpolicy-default-deny-egress.yaml')
    else:
      replace_networkpolicy(kopf=kopf,name=name,spec=spec,logger=logger,api=api,filename='networkpolicy-default-deny-egress.yaml',policyname='default-deny-egress')   
    

    if "default-deny-ingress" not in l_netpol:
      create_networkpolicy(kopf=kopf,name=name,spec=spec,logger=logger,api=api,filename='networkpolicy-default-deny-ingress.yaml')
    else:
      replace_networkpolicy(kopf=kopf,name=name,spec=spec,logger=logger,api=api,filename='networkpolicy-default-deny-ingress.yaml',policyname='default-deny-ingress')   
    
    if "allow-all-in-namespace" not in l_netpol:
      create_networkpolicy(kopf=kopf,name=name,spec=spec,logger=logger,api=api,filename='networkpolicy-allow-all-in-namespace.yaml') 
    else:
      replace_networkpolicy(kopf=kopf,name=name,spec=spec,logger=logger,api=api,filename='networkpolicy-allow-all-in-namespace.yaml',policyname="allow-all-in-namespace")
  
      
    return {'limitrange-np-name': name} 
   


# When deleting object
@kopf.on.delete('v1', 'namespace')
def delete_fn(spec, name, status, namespace,meta, logger, **kwargs):
    logger.info(f"Deleting: {spec}")