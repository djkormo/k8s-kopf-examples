

## Step for running operator in our k8s cluster

### Build and push image 

```bash
docker image build . -t djkormo/op-demoweb:latest 
docker image push djkormo/op-demoweb:latest
```

### Deploy crd

```console kubectl apply -f crd/crd.yaml ```

### Create namespace for the operator

```console kubectl create ns demoweb-operator```


### Deploy operator permission

```console kubectl apply -f deploy/rbac ```

### Deploy the operator

```console kubectl apply -f deploy/operator.yaml ```

### Deploy sample CR (demoweb object)

```console kubectl apply -f test/demoweb.yaml ```

### Check 

```console kubectl get pod,svc -n demoweb-operator ```

In case of troubles look into operator logs
```console
operator_pod=$(kubectl get pod -n demoweb-operator -L app=op -o name)
kubectl -n demoweb-operator logs ${operator_pod}
```



Based on 

https://blog.baeke.info/2020/01/26/writing-a-kubernetes-operator-with-kopf/

