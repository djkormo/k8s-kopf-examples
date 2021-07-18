import kopf
import kubernetes
import yaml
import os
from kubernetes.client.rest import ApiException
from pprint import pprint

@kopf.on.create('djkormo.github', 'v1alpha1', 'project')
def create_fn(spec, name, namespace, logger, **kwargs):
    print(f"Creating: {spec}")
    logger.info(f"Object is created: {spec}")
    resourcequotarequestscpu = spec.get('resourcequotarequestscpu')
    if not resourcequotarequestscpu:
      raise kopf.PermanentError(f"resourcequotarequestscpu must be set. Got {resourcequotarequestscpu!r}.")

    resourcequotarequestsmemory = spec.get('resourcequotarequestsmemory')
    if not resourcequotarequestsmemory:
      raise kopf.PermanentError(f"resourcequotarequestsmemory must be set. Got {resourcequotarequestsmemory!r}.")
    
    resourcequotalimitscpu=spec.get('resourcequotalimitscpu')
    resourcequotalimitsmemory=spec.get('resourcequotalimitsmemory')
    resourcequotacountjobsbatch=spec.get('resourcequotacountjobsbatch')
    resourcequotacountingresses=spec.get('resourcequotacountingresses')
    resourcequotapods=spec.get('resourcequotapods')
    resourcequotaservices=spec.get('resourcequotaservices')
    resourcequotaconfigmaps=spec.get('resourcequotaconfigmaps')
    resourcequotapersistentvolumeclaims=spec.get('resourcequotapersistentvolumeclaims'),
    resourcequotareplicationcontrollers=spec.get('resourcequotareplicationcontrollers')
    resourcequotasecrets=spec.get('resourcequotasecrets')
    resourcequotaservicesloadbalancers=spec.get('resourcequotaservicesloadbalancers')

    api = kubernetes.client.CoreV1Api()

    # get context of yaml manifest for namespace

    path = os.path.join(os.path.dirname(__file__), 'namespace.yaml')
    tmpl = open(path, 'rt').read()
    text = tmpl.format(name=name, namespace=namespace
    )
    data = yaml.safe_load(text)

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
    text = tmpl.format(name=name, resourcequotarequestscpu=resourcequotarequestscpu,
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
    
    # Create resourcequota

    try:
      obj = api.create_namespaced_resource_quota(
          namespace=namespace,
          body=data,
      )
      pprint(obj)
      logger.info(f"ResourceQuota child is created: {obj}")
    except ApiException as e:
      print("Exception when calling CoreV1Api->create_namespaced_resource_quota: %s\n" % e)  

    return {'message': 'done'}  # will be the new status


