

## Step for running operator in our k8s cluster

### Build and push image 

```bash
docker image build . -t djkormo/op-chaos:latest 
docker image push djkormo/op-chaos:latest
```

### Deploy crd

```console 
kubectl apply -f crd/crd.yaml 
```

### Create namespace for the operator

```console 
kubectl create ns chaos-operator
```


### Deploy operator permission

```console 
kubectl apply -f deploy/rbac 
```

### Deploy the operator

```console 
kubectl apply -f deploy/operator.yaml 
```

### Deploy sample CR (chaos object)

```console 
kubectl apply -f test/chaos.yaml 
```

### Check 

``` 
kubectl get deploy,pod -n chaos-operator 
```

#### In case of troubles look into operator logs

```
operator_pod=$(kubectl get pod -n chaos-operator -L app=chaos-operator -o name | grep operator | head -n1)
kubectl -n chaos-operator logs ${operator_pod} -f 
```

```
kubectl -n chaos-operator describe ${operator_pod}
```



Check events

```
kubectl get events -n chaos-operator --sort-by=.metadata.creationTimestamp
```

```
kubectl -n chaos-operator exec ${operator_pod} -it -- bash
curl http://localhost:8080/healthz

```


Redeploy operator
```
kubectl replace -R -f deploy/ --force
```

Based on 

https://kopf.readthedocs.io/en/latest/walkthrough/creation/

