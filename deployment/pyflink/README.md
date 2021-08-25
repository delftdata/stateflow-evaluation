# Performance experiments using PyFlink as runtime
Similar to the AWS Lamdba and Statefun experiments we setup a FastAPI frontend. This guide assumes there is already a running K8s cluster
with enough resources and a Kafka cluster. We deployed a Kafka cluster using [Confluent Cloud](https://www.confluent.io/confluent-cloud/).  Moreover, you should be able to access your cluster using the `kubectl` command. Lastly, the K8s cluster can
provide LoadBalancers through its cloudprovider (e.g. AWS or GCP).

### Deploy Flink Cluster
First we build a Flink image which contains all (Python) resources. Ensure you have a zipped version of your `venv` in this folder.
This `venv` should include the `stateflow` repostory. Once cloned, this can be build using `pip install ../stateful_dataflows/`.
Moreover, remove binaries from this `venv.zip` to decrease the size. To build the Docker image:
```bash
docker build -f Dockerfile . -t wzorgdrager/stateflow-pyflink
```
Then we can deploy it on Kubernetes:
```bash
kubectl apply -f flink-master.yaml
kubectl apply -f flink-worker.yaml
```
From a local Flink distribution we submit the job to the remote cluster. Ensure you have [Flink 1.13](https://flink.apache.org/downloads.html#apache-flink-1132) on your computer.
Enable your `venv` from this repository: `source /venv/bin/active` and move to the `bin` folder of the Flink release.
```sh
export PYFLINK_CLIENT_EXECUTABLE=~.. goede venv
export PYTHONPATH=~ .. goede venv

./flink run \
  --jobmanager {JOBMANAGER_URL} \
  -pyarch ~/Documents/stateflow-evaluation/benchmark/pyflink/data.zip#/ \
  --python ~/Documents/stateflow-evaluation/benchmark/pyflink/runtime_pyflink.py \
  --pyFiles ~/Documents/stateflow-evaluation/benchmark/pyflink \
  --parallelism 40 \
  #--jarfile ~/Documents/stateflow-evaluation/benchmark/bin/combined.jar
```

This assumes that the repository is located at `~/Documents/stateflow-evaluation/`. Replace the `{ADDRESS}` with the
address of the Flink Jobmanager.

## Deploy frontend
We assume there is already a published Docker image. In our case, we use `wzorgdrager/stateflow-frontend-pyflink:LATEST`.
In `deployment/frontend/` you can find a Dockerfile to build it yourself. Make sure to update the image in the 
K8s files. Fill in the Kafka details in the `stateflow-frontend-pyflink` file. The reason we use a different frontend image 
for PyFlink is because PyFlink has some limitations with regard to packaging. Finally, deploy it using:
```bash
cd ../frontend/
kubectl apply -f stateflow-frontend-pyflink.yaml 
kubectl apply -f stateflow-frontend-loadbalancer.yaml 
```
Somewhere in the K8s environment/dashboard or AWS, you will find a loadbalancer url which points to the frontend.
We need this for the benchmark script.

This will deploy 20 replicas of the frontend with 1 CPU and 1GB RAM **each**. 
In total we have **20 CPUs** and **20GB RAM** for the frontend.

## Deploy and run benchmark
Please read the benchmark (deployment) in `workload/README.md`. This is the same for all runtimes. 
