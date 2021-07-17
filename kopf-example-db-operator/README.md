docker image build . -t djkormo/op-db:latest 

docker image push djkormo/op-db:latest



kubectl apply -f crd/crd.yaml
kubectl create ns db-operator
kubectl apply -f deploy/rbac


kubectl apply -f deploy/deployment.yaml 

kubectl apply -f test/database.yaml 



kubectl get pod,svc -n db-operator