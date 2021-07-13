# Setup Flink on Kubernetes cluster
**Note:** This has only been tested on a local Minikube cluster.

```bash
kubectl create serviceaccount flink-service-account
kubectl create clusterrolebinding flink-role-binding-flink --clusterrole=edit --serviceaccount=default:flink-service-account
```
```bash
./kubernetes-session.sh -Dkubernetes.cluster-id=stateflow-flink-cluster -Dkubernetes.service-account=flink-service-account
```
```bash
docker build --tag pyflink:latest .
```
```bash
./flink run-application \
--target kubernetes-application \
-Dkubernetes.cluster-id=stateflow-flink-cluster \
-Dtaskmanager.memory.process.size=4096m \
-Dkubernetes.taskmanager.cpu=2 \
-Dkubernetes.service-account=flink-service-account \
-Dtaskmanager.numberOfTaskSlots=4 \
-Dkubernetes.container.image=pyflink:latest \
-pyarch venv.zip \
-pyexec venv.zip/venv/bin/python \
--parallelism 4 -py ~/Documents/stateflow-evaluation/benchmark/runtime.py --jarfile ~/Documents/stateflow-evaluation/benchmark/bin/combined.jar
```