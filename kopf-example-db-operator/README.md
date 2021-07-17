

## Step for running operator in our k8s cluster

### Build and push image 

```bash
docker image build . -t djkormo/op-db:latest 
docker image push djkormo/op-db:latest
```

### Deploy crd

```console 
kubectl apply -f crd/crd.yaml 
```

### Create namespace for the operator

```console 
kubectl create ns db-operator
```


### Deploy operator permission

```console 
kubectl apply -f deploy/rbac 
```

### Deploy the operator

```console 
kubectl apply -f deploy/operator.yaml 
```

### Deploy sample CR (dababase object)

```console 
kubectl apply -f test/database.yaml 
```

### Check 

```console 
kubectl get pod,svc -n db-operator 
```

#### In case of troubles look into operator logs

```console
operator_pod=$(kubectl get pod -n db-operator -L app=op -o name)
kubectl -n db-operator logs ${operator_pod}
```
