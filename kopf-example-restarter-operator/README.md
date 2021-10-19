## gfff

## Step for running operator in our k8s cluster

### Build and push image 

```bash
docker image build . -t djkormo/restarter-op:latest
docker image push djkormo/restarter-op:latest 
```

### Deploy crd 

```console 
# kubectl apply -f crd/
```

### Create namespace for the operator

```console 
kubectl create ns restarter-operator
```

### Deploy operator permission

```console 
kubectl apply -f deploy/rbac 
```

### Deploy the operator

```console 
kubectl apply -f deploy/operator.yaml 
```

### Deploy sample CR (project object)

```console 
kubectl apply -f test/logstash-restarter.yaml 
```

### Check 

``` 
kubectl get deploy,pod -n restarter-operator
```

#### In case of troubles look into operator logs

```
operator_pod=$(kubectl get pod -n restarter-operator -L app=restarter-operator -o name | grep operator | head -n1)
echo ${operator_pod}
kubectl -n restarter-operator logs ${operator_pod} -f 
```

```
kubectl -n restarter-operator describe ${operator_pod}
```

```
kubectl -n restarter-operator exec ${operator_pod} -it -- bash
curl http://localhost:8080/healthz

```
Redeploy operator

```
kubectl replace -R -f deploy/ --force
```

Check RBAC

```
kubectl auth can-i -n cluster-operators list restarters --as=system:serviceaccount:restarter-operator:restarter-operator

```


Based on 

https://kopf.readthedocs.io/en/latest/walkthrough/creation/


