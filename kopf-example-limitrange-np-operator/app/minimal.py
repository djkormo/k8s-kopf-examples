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

# When creating or resuming object 
@kopf.on.resume('namespace')
@kopf.on.create('namespace')
def create_fn(spec, name, namespace, logger, **kwargs):
    print(f"Creating: {spec}")

    api = kubernetes.client.CoreV1Api()

    # check for excluded namespace

    env = Env()
    env.read_env()  # read .env file, if it exists
    namespace_list = env.list('EXCLUDED_NAMESPACES')
    if name in namespace_list:
      print(f"Excluded namespace list: {namespace_list} ")    
      print(f"Excluded namespace found: {name}")
      return {'limitrange-np-name': name}   
      # end of story 

    # create limitrange 
    
    # get context of yaml manifest for limitrange
     
    path = os.path.join(os.path.dirname(__file__), 'limitrange.yaml')
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
    #return {'project-name': obj.metadata.name}

    # create network policy

    api = kubernetes.client.NetworkingV1Api()

    path = os.path.join(os.path.dirname(__file__), 'networkpolicy-allow-dns-access.yaml')
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
    

    #return {'project-name': obj.metadata.name}

    path = os.path.join(os.path.dirname(__file__), 'networkpolicy-default-deny-ingress.yaml')
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
    
    #return {'project-name': obj.metadata.name}


    path = os.path.join(os.path.dirname(__file__), 'networkpolicy-default-deny-egress.yaml')
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
    
    kopf.adopt(data)

@kopf.timer('namespace', interval=60.0,sharp=True)
def check_object_on_time(spec, name, namespace, logger, **kwargs):
    logger.info(f"Timer: {spec} is invoked")
    env = Env()
    env.read_env()  # read .env file, if it exists
    namespace_list = env.list('EXCLUDED_NAMESPACES')
    if name in namespace_list:
      print(f"Excluded namespace list: {namespace_list} ")    
      print(f"Excluded namespace found: {name}")
      return {'limitrange-np-name': name} 

    # TODO check if limitrange is missing

    # TODO check if network policies are missing  



# When updating object
@kopf.on.update('namespace')
def update_fn(spec, name, status, namespace, logger,diff, **kwargs):
    print(f"Updating: {spec}")

    # update/patch limitrange 

    api = kubernetes.client.CoreV1Api()

    path = os.path.join(os.path.dirname(__file__), 'limitrange.yaml')
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
      obj = api.patch_namespaced_limit_range(
          namespace=name,
          name=name,
          body=data,
      )
      kopf.append_owner_reference(obj)
      logger.info(f"LimitRange child is patched/updated: {obj}")
    except ApiException as e:
      print("Exception when calling CoreV1Api->patch_namespaced_limit_range: %s\n" % e)
    kopf.adopt(data)
        

# When deleting object
@kopf.on.delete('v1', 'namespace')
def delete_fn(spec, name, status, namespace, logger, **kwargs):
    print(f"Deleting: {spec}")