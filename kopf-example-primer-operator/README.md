

## Step for running operator in our k8s cluster

### Build and push image 

```bash
docker image build . -t djkormo/op-primer:latest 
docker image push djkormo/op-primer:latest
```

### Deploy crd

```console 
kubectl apply -f crd/crd.yaml 
```

### Create namespace for the operator

```console 
kubectl create ns primer-operator
```


### Deploy operator permission

```console 
kubectl apply -f deploy/rbac 
```

### Deploy the operator

```console 
kubectl apply -f deploy/operator.yaml 
```

### Deploy sample CR (primer object)

```console 
kubectl apply -f test/primer.yaml 
```

### Check 

``` 
kubectl get deploy,pod -n primer-operator 
```

#### In case of troubles look into operator logs

```
operator_pod=$(kubectl get pod -n primer-operator -L app=primer-operator -o name | grep operator | head -n1)
kubectl -n chaos-operator logs ${operator_pod} -f 
```

```
kubectl -n primer-operator describe ${operator_pod}
```



Check events

```
kubectl get events -n primer-operator --sort-by=.metadata.creationTimestamp
```

```
kubectl -n primer-operator exec ${operator_pod} -it -- bash
curl http://localhost:8080/healthz

```


Redeploy operator
```
kubectl replace -R -f deploy/ --force
```

Based on 

https://kopf.readthedocs.io/en/latest/walkthrough/creation/


