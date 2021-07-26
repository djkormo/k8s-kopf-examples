import time
import kopf
import kubernetes
import yaml
import os
from kubernetes.client.rest import ApiException
from pprint import pprint
import datetime
import random
@kopf.on.probe(id='now')
def get_current_timestamp(**kwargs):
    return datetime.datetime.utcnow().isoformat()

@kopf.on.probe(id='random')
def get_random_value(**kwargs):
    return random.randint(0, 1_000_000)

@kopf.on.create('djkormo.github', 'v1alpha1', 'project')
def create_fn(spec, name, namespace, logger, **kwargs):
    print(f"Creating: {spec}")
    logger.info(f"Object project is created: {spec}")

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
    resourcequotapersistentvolumeclaims=spec.get('resourcequotapersistentvolumeclaims',1),
    resourcequotareplicationcontrollers=spec.get('resourcequotareplicationcontrollers',1)
    resourcequotasecrets=spec.get('resourcequotasecrets',1)
    resourcequotaservicesloadbalancers=spec.get('resourcequotaservicesloadbalancers',1)

    # get context of yaml manifest for namespace

    path = os.path.join(os.path.dirname(__file__), 'namespace.yaml')
    tmpl = open(path, 'rt').read()
    text = tmpl.format(name=name, namespace=namespace)

    data = yaml.safe_load(text)
    kopf.adopt(data)
    logger.info(f"Namespace child definition: {data}")
    api = kubernetes.client.CoreV1Api()

    ## Create namespace
    try:
      obj = api.create_namespace(
          body=data,
      )
      pprint(obj)
      logger.info(f"Namespace child is created: {obj}")
    except ApiException as e:
      print("Exception when calling CoreV1Api->create_namespace: %s\n" % e)  
    
    # get context of yaml manifest for resource quota

    path = os.path.join(os.path.dirname(__file__), 'resourcequota.yaml')
    tmpl = open(path, 'rt').read()
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
    
    logger.info(f"ResourceQuota child definition: {data}")

    kopf.adopt(data)


    # Create resourcequota

  #  kopf.adjust_namespace(obj,name, forced=True)

    try:
      obj = api.create_namespaced_resource_quota(
          namespace=name,
          body=data,
      )
      pprint(obj)
      logger.info(f"ResourceQuota child is created: {obj}")
    except ApiException as e:
      print("Exception when calling CoreV1Api->create_namespaced_resource_quota: %s\n" % e)  

    return {'project-name': obj.metadata.name}


@kopf.on.update('djkormo.github', 'v1alpha1', 'project')
def update_fn(spec, name, status, namespace, logger, **kwargs):
    print(f"Updating: {spec}")

    resourcequotarequestscpu = spec.get('resourcequotarequestscpu',1)
    if not resourcequotarequestscpu:
      raise kopf.PermanentError(f"resourcequotarequestscpu must be set. Got {resourcequotarequestscpu!r}.")


    project_name = status['create_fn']['project-name']
    project_patch = {'spec': {'hard': {'requests.cpu': resourcequotarequestscpu}}}
    logger.info(f"Object project is updated: {spec}")
    api = kubernetes.client.CoreV1Api()

    try:
      obj = api.patch_namespaced_resource_quota(
          namespace=name,
          name=project_name,
          body=project_patch,
      )
      pprint(obj)
      logger.info(f"ResourceQuota child is updated: {obj}")
    except ApiException as e:
      print("Exception when calling CoreV1Api->patch_namespaced_resource_quota: %s\n" % e)  
    
    return {'project-name': obj.metadata.name}
    
@kopf.on.field('djkormo.github', 'v1alpha1', 'project', field='spec.hard')
def relabel(diff, status,name, namespace, logger, **kwargs):
    project_patch = {field[0]: new for op, field, old, new in diff}
    project_name = status['relabel']['project-name']
    project_path = {'spec': {'hard': project_patch}}

    logger.info(f"Object project is updated: {project_path}")

    api = kubernetes.client.CoreV1Api()

    try:
      obj = api.patch_namespaced_resource_quota(
          namespace=name,
          name=project_name,
          body=project_patch,
      )
      pprint(obj)
      logger.info(f"ResourceQuota child is updated: {obj}")
    except ApiException as e:
      print("Exception when calling CoreV1Api->patch_namespaced_resource_quota: %s\n" % e)  

    return {'project-name': obj.metadata.name}

@kopf.on
.delete('djkormo.github', 'v1alpha1', 'project')
def update_fn(spec, name, status, namespace, logger, **kwargs):
    print(f"Deleting: {spec}")