

## Step for running operator in our k8s cluster

### Build and push image 

```bash
docker image build . -t djkormo/op-project:latest 
docker image push djkormo/op-project:latest
```

### Deploy crd

```console 
kubectl apply -f crd/crd.yaml 
```

### Create namespace for the operator

```console 
kubectl create ns project-operator
```


### Deploy operator permission

```console 
kubectl apply -f deploy/rbac 
```

### Deploy the operator

```console 
kubectl apply -f deploy/operator.yaml 
```

### Deploy sample CR (demoweb object)

```console 
kubectl apply -f test/project.yaml 
```

### Check 

```console 
kubectl get pod,svc -n project-operator 
```

#### In case of troubles look into operator logs

```console
operator_pod=$(kubectl get pod -n project-operator -L app=op -o name | grep operator | head -n1)
kubectl -n project-operator logs ${operator_pod}
```


kubectl -n project-operator describe ${operator_pod}

```
kubectl -n project-operator exec ${operator_pod} -it -- bash
```


Based on 

https://github.com/lukasz-bielinski/project-operator

https://kopf.readthedocs.io/en/latest/walkthrough/creation/

