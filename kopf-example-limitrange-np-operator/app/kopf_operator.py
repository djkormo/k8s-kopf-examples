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
def create_limitrange(kopf,name,spec,logger,api,filename):
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
    logger.info(f"LimitRange child is created: {obj}")
  except ApiException as e:
    print("Exception when calling CoreV1Api->create_namespaced_limit_range: %s\n" % e)
  kopf.adopt(data)

# replace limitrange based on yaml manifest
def replace_limitrange(kopf,name,spec,logger,api,filename):
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
    logger.info(f"LimitRange child is created: {obj}")
  except ApiException as e:
    print("Exception when calling CoreV1Api->replace_namespaced_limit_range: %s\n" % e)
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
    logger.info(f"NetworkPolicy child is created: {obj}")
  except ApiException as e:
    print("Exception when calling NetworkingV1Api->create_namespaced_network_policy: %s\n" % e)

   
# When creating or resuming object 
@kopf.on.resume('namespace')
@kopf.on.create('namespace')
def create_fn(spec, name, namespace, logger, **kwargs):
    print(f"Creating: {spec}")

    api = kubernetes.client.CoreV1Api()

    # check for excluded namespace

    if check_namespace(name=name,excluded_namespaces='EXCLUDED_NAMESPACES'):
      return {'limitrange-np-name': name}   
      # end of story 

    # create limitrange 
    api = kubernetes.client.CoreV1Api()

    try: 
      api_response = api.list_namespaced_limit_range(namespace=name) #, pretty=pretty, field_selector=field_selector, include_uninitialized=include_uninitialized, label_selector=label_selector, resource_version=resource_version, timeout_seconds=timeout_seconds, watch=watch)
      #pprint(api_response)
      for i in api_response.items:
        print("Limitrange namespace: %s\t name: %s" %
          (i.metadata.namespace, i.metadata.name))
    except ApiException as e:
      print("Exception when calling CoreV1Api->list_namespaced_limit_range: %s\n" % e)

    create_limitrange(kopf=kopf,name=name,spec=spec,logger=logger,api=api,filename='limitrange.yaml')
    
    api = kubernetes.client.NetworkingV1Api()

    try: 
      api_response = api.list_namespaced_network_policy(namespace=name) #, pretty=pretty, field_selector=field_selector, include_uninitialized=include_uninitialized, label_selector=label_selector, resource_version=resource_version, timeout_seconds=timeout_seconds, watch=watch)
      #pprint(api_response)
      for i in api_response.items:
        print("NetworkPolicy namespace: %s\t name: %s" %
          (i.metadata.namespace, i.metadata.name))
    except ApiException as e:
      print("Exception when calling NetworkingV1Api->list_namespaced_network_policy: %s\n" % e)

    create_networkpolicy(kopf=kopf,name=name,spec=spec,logger=logger,api=api,filename='networkpolicy-allow-dns-access.yaml')
    create_networkpolicy(kopf=kopf,name=name,spec=spec,logger=logger,api=api,filename='networkpolicy-default-deny-egress.yaml')
    create_networkpolicy(kopf=kopf,name=name,spec=spec,logger=logger,api=api,filename='networkpolicy-default-deny-ingress.yaml')

    return {'limitrange-np-name': name} 

# use env variable to control loop interval in seconds 
LOOP_INTERVAL = int(os.environ['LOOP_INTERVAL'])
@kopf.timer('namespace', interval=LOOP_INTERVAL,sharp=True)
def check_object_on_time(spec, name, namespace, logger, **kwargs):
    logger.info(f"Timer: {spec} is invoked")

    # check for excluded namespace

    if check_namespace(name=name,excluded_namespaces='EXCLUDED_NAMESPACES'):
      return {'limitrange-np-name': name}   

    # TODO check if limitrange is missing

    # update/patch limitrange 

    api = kubernetes.client.CoreV1Api()
    replace_limitrange(kopf=kopf,name=name,spec=spec,logger=logger,api=api,filename='limitrange.yaml')

    api = kubernetes.client.NetworkingV1Api()
    # TODO check if network policies are missing  
    try: 
      api_response = api.list_namespaced_network_policy(namespace=name) #, pretty=pretty, field_selector=field_selector, include_uninitialized=include_uninitialized, label_selector=label_selector, resource_version=resource_version, timeout_seconds=timeout_seconds, watch=watch)
      pprint(api_response.items)
      for i in api_response.items:
        print("NetworkPolicy namespace: %s\t name: %s" %
          (i.metadata.namespace, i.metadata.name))
    except ApiException as e:
      print("Exception when calling NetworkingV1Api->list_namespaced_network_policy: %s\n" % e)
    netpol=api_response.items.metadata.name
    
    # update/patch networkpolicy
    if "allow-dns-access" not in netpol:
      create_networkpolicy(kopf=kopf,name=name,spec=spec,logger=logger,api=api,filename='networkpolicy-allow-dns-access.yaml')

    if "default-deny-egress" not in netpol:
      create_networkpolicy(kopf=kopf,name=name,spec=spec,logger=logger,api=api,filename='networkpolicy-default-deny-egress.yaml')
   
    if "default-deny-ingress" not in netpol:
      create_networkpolicy(kopf=kopf,name=name,spec=spec,logger=logger,api=api,filename='networkpolicy-default-deny-ingress.yaml')
     

# When updating object
@kopf.on.update('namespace')
def update_fn(spec, name, status, namespace, logger,diff, **kwargs):
    print(f"Updating: {spec}")
    
    # check for excluded namespace

    if check_namespace(name=name,excluded_namespaces='EXCLUDED_NAMESPACES'):
      return {'limitrange-np-name': name}   

    # update/patch limitrange 

    api = kubernetes.client.CoreV1Api()
    replace_limitrange(kopf=kopf,name=name,spec=spec,logger=logger,api=api,filename='limitrange.yaml')
    
    # update/patch networkpolicy

    api = kubernetes.client.NetworkingV1Api()
    create_networkpolicy(kopf=kopf,name=name,spec=spec,logger=logger,api=api,filename='networkpolicy-allow-dns-access.yaml')
    create_networkpolicy(kopf=kopf,name=name,spec=spec,logger=logger,api=api,filename='networkpolicy-default-deny-egress.yaml')
    create_networkpolicy(kopf=kopf,name=name,spec=spec,logger=logger,api=api,filename='networkpolicy-default-deny-ingress.yaml')

    return {'limitrange-np-name': name} 



# When deleting object
@kopf.on.delete('v1', 'namespace')
def delete_fn(spec, name, status, namespace, logger, **kwargs):
    print(f"Deleting: {spec}")