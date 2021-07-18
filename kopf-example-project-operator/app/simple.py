import kopf
import kubernetes
import yaml
import os

@kopf.on.create('djkormo', 'v1alpha1', 'project')
def create_fn(spec, **kwargs):
    print(f"Creating: {spec}")
    return {'message': 'done'}  # will be the new status


