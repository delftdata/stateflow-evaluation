# Stateflow Evaluation
This repository contains all code and results for the evaluation of the [stateflow framework](https://github.com/wzorgdrager/stateful_dataflows).
This evaluation is part of the master thesis by [Wouter Zorgdrager](https://github.com/wzorgdrager).

## Setup
To setup this repository, you need to have the stateflow framework installed locally. 

### Specification
**Reserve a hotel room.**
1. Login a user.
2. Finds an available room based on a checkin date, checkout date and room size.
3. If room is available, let the user pay for it.
4. Make the room reservation, if this fails refund the user.