# Stateflow Evaluation
This repository contains all code and results for the evaluation of the [stateflow framework](https://github.com/wzorgdrager/stateful_dataflows).
This evaluation is part of the master thesis by [Wouter Zorgdrager](https://github.com/wzorgdrager).

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

### Deathstar benchmark specification
Coming soon