# Stateflow Evaluation
This repository contains all code and results for the evaluation of the [stateflow framework](https://github.com/wzorgdrager/stateful_dataflows).

## Setup
To setup this repository, you need to have the stateflow framework installed locally. 
```bash
git clone https://github.com/wzorgdrager/stateful_dataflows
pip install path_to_this_repo
```

## Experiments
We run multiple types of experiments:
- Overhead experiments: we show the overhead of different components. Results can be found in `results/overhead/overhead_results_with_runtime.ipynb` and `results/overhead/overhead_results_without_runtime.ipynb`.
- Performance experiments: the setups and deployments can be found in `deployment/[aws|flink|pyflink]` folders. Results can be found in `results/performance`. 

### Deathstar benchmark
The performance experiments are conducted with a workload from the [Deathstar benchmark](https://www.csl.cornell.edu/~delimitrou/papers/2019.asplos.microservices.pdf). We cover the hotel reservation service and all source code can be found under the `benchmark/hotel` folder.  
**Note:** We made a copy of the benchmark specifically for the PyFlink deployment. This is the exact same code, but has some different imports and and locations to make it work with Flink.