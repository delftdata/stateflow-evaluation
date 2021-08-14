# Performance experiments using AWS Lambda as runtime
Similar to the PyFlink and Statefun experiments we setup a FastAPI frontend. However, we don't use Kafka 
since invocations are directly done using AWS API Gateway. This guide assumes there is already a running K8s cluster
with enough resources. Moreover, you can access your cluster using the `kubectl` command. Lastly, the K8s cluster can
provide LoadBalancers through its cloudprovider (e.g. AWS or GCP).

### Deploy AWS Lambda function
Make sure you have the latest version of [serverless](https://www.serverless.com/) installed and sure you have the correct
IAM roles configured. The serverless.yml has one pre-configured, but you can update it with your own. Ensure you select
your preferred region (i.e. `eu-west-1`). 

First ensure that `runtime_aws.py` and `serverless.yml` are in the root directory of this repo. 
This is necessary for packaging.
```bash
mv /benchmark/runtime_aws.py ..
mv /deployment/aws/serverless.yml ../../
```
Then deploy the Lambda function:
```bash
serverless deploy
```

Finally, create two DynamoDB tables. Make sure its the same region as your Lambda function 
and your Lambda function has permission to access it.
1. Create one DynamoDB table with the name `stateflow` and primary key `key`. Configure it in `on-demand` mode. 
2. Create another DynamoDB table with the name `DynamoDBLockTable` and primary key `lock_key` and sort key `sort_key`. 
   Configure it in `on-demand` mode.
   
Finally, find the API Gateway URL that is assigned by AWS. It is in the form of:
`https://r2q5pdxa8e.execute-api.eu-west-2.amazonaws.com/dev/stateflow` You can find this in the AWS Lambda dashboard.

AWS Lambda is configured to use 1GB of memory. Max concurrency is fixed to **1000**. 
Therefore, AWS Lambda has burst capacity of providing **1TB RAM**.
## Deploy frontend
We assume there is already a published Docker image. In our case, we use `wzorgdrager/stateflow-frontend:LATEST`.
In `deployment/frontend/` you can find a Dockerfile to build it yourself. Make sure to update the image in the 
K8s files. First add the API Gateway url to `deployment/frontend/stateflow-frontend-aws.yaml` 
under the `ADDRESS` environment variable. Then deploy it using:
```bash
cd ../frontend/
kubectl apply -f stateflow-frontend-aws.yaml 
kubectl apply -f stateflow-frontend-loadbalancer.yaml 
```
Somewhere in the K8s environment/dashboard or AWS, you will find a loadbalancer url which points to the frontend.
We need this for the benchmark script.

This will deploy 20 replicas of the frontend with 1 CPU and 1GB RAM **each**. 
In total we have **20 CPUs** and **20GB RAM** for the frontend.

## Deploy and run benchmark
Please read the benchmark (deployment) in `workload/README.md`. This is the same for all runtimes. 