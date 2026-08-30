# Performance Evaluation of Load-Balancing Algorithms

OMNeT++ discrete-event simulation project for comparing the performance of several load-balancing algorithms under different system sizes and offered loads.

The project evaluates:

- Random
- Round Robin
- Shortest Queue
- Power of Two Choices

The main performance metrics are response time, waiting time, throughput, server utilization, and queue length.

## Simulation Model

The simulated system consists of:

1. A `JobGenerator` that creates jobs according to a stochastic arrival process.
2. A `LoadBalancer` that assigns each arriving job to one of the available servers.
3. Multiple `Server` modules, each with its own FIFO queue and service process.

Jobs store their creation time, server arrival time, and service requirement, allowing response time and queueing delay to be measured.

The number of servers is configurable.

## Load-Balancing Algorithms

### Random

Each incoming job is assigned uniformly at random to one of the available servers.

### Round Robin

Jobs are assigned cyclically across all servers.

### Shortest Queue

The load balancer observes the current system length of every server and assigns the job to a server with the smallest number of jobs.

The system length includes both queued jobs and the job currently being served.

Ties are broken randomly.

### Power of Two Choices

Two distinct servers are sampled randomly. The incoming job is assigned to the less loaded of the two.

Ties are broken randomly.

For two-server systems, Power of Two Choices is effectively equivalent to Shortest Queue because both available servers are inspected.

## Experimental Design

Three server-pool sizes are evaluated:

- N = 2
- N = 4
- N = 8

Three offered-load levels per server are evaluated:

- Low: rho = 0.4
- Medium: rho = 0.7
- High: rho = 0.9

The mean service requirement is:

```text
E[S] = 1 s
```

Therefore, each server has a mean service rate of approximately:

```text
mu = 1 job/s
```

The total arrival rate is selected according to:

```text
lambda = rho * N
```

This keeps the offered load per server constant when the number of servers changes.

The resulting experiment matrix contains:

```text
3 server counts
x 3 load levels
x 4 algorithms
= 36 scenarios
```

## Random Number Streams

Separate pseudo-random-number streams are used for independent random processes:

- RNG 0: interarrival times
- RNG 1: service requirements
- RNG 2: load-balancer random decisions

The final experiments use:

```ini
seed-set = ${repetition}
```

so competing algorithms within the same workload use the same arrival and service-demand random streams.

This common-random-number design improves the fairness of algorithm comparisons while keeping routing randomness separate.

## Steady-State Output Analysis

The system starts empty, so an initialization transient is present.

A warm-up study was performed using high-load scenarios and multiple replications. Based on the observed transient behavior, the first:

```text
500 s
```

are excluded from steady-state measurements.

The final simulation duration is:

```text
256500 s
```

consisting of:

```text
500 s warm-up
+ 256000 s measurement interval
```

The measurement interval is divided into:

```text
64 batches x 4000 s
```

Batch means are used for statistical analysis.

Lag-1 autocorrelation of the batch means is checked as an independence diagnostic.

For each metric, a 95% confidence interval is calculated using the Student-t distribution with 63 degrees of freedom.

## Performance Metrics

The following metrics are collected:

- Mean response time
- Mean waiting time
- Throughput
- Mean queue length per server
- Mean server utilization

Queue length and utilization are computed as time-weighted state averages.

Response time and waiting time are event-based observations.

## Project Structure

```text
.
├── src/
│   ├── Job.msg
│   ├── JobGenerator.cc
│   ├── JobGenerator.h
│   ├── JobGenerator.ned
│   ├── LoadBalancer.cc
│   ├── LoadBalancer.h
│   ├── LoadBalancer.ned
│   ├── LoadBalancingNetwork.ned
│   ├── Server.cc
│   ├── Server.h
│   └── Server.ned
│
├── simulations/
│   └── omnetpp.ini
│
├── analyze_warmup.py
├── analyze_batches.py
├── check_batch_independence.py
├── analyze_all_results.py
├── make_report_outputs.py
├── run_experiments.sh
└── README.md
```

Simulation results, generated plots, and compiled binaries are intentionally excluded from version control.

## Software Environment

The project was developed and tested primarily with:

```text
OMNeT++ 6.3.0
INET 4.6.0 environment
Linux / WSL
Python 3
```
Compatibility was additionally verified using the course-provided OMNeT++ 6.2.0 virtual machine.
The project successfully builds and executes the validation scenario under OMNeT++ 6.2.0.

The simulation itself uses standard OMNeT++ modules and messages.

Python analysis requires:

```bash
pip install numpy pandas matplotlib
```

## Building

From an OMNeT++ environment, the project can be built using the OMNeT++ IDE or the generated project Makefiles.

For a release build:

```bash
make MODE=release
```

The release executable used during the experiments was:

```text
out/clang-release/src/LoadBalancingSimulation
```

## Running the Final Experiments

For example:

```bash 6.3
./out/clang-release/src/LoadBalancingSimulation \
    -u Cmdenv \
    -n . \
    -f simulations/omnetpp.ini \
    -c Final_N4_High
```
```bash 6.2
./out/gcc-release/src/LoadBalancingSimulation \
    -u Cmdenv \
    -n . \
    -f simulations/omnetpp.ini \
    -c Final_N4_High
```

Each final configuration iterates automatically over the four load-balancing algorithms.

To execute the complete final experiment matrix:

Either:

```./run_experiments.sh```

Or:

```bash 6.3
for config in \
    Final_N2_Low Final_N2_Medium Final_N2_High \
    Final_N4_Low Final_N4_Medium Final_N4_High \
    Final_N8_Low Final_N8_Medium Final_N8_High
do
    ./out/clang-release/src/LoadBalancingSimulation \
        -u Cmdenv \
        -n . \
        -f simulations/omnetpp.ini \
        -c "$config"
done
```
```bash 6.2
for config in \
    Final_N2_Low Final_N2_Medium Final_N2_High \
    Final_N4_Low Final_N4_Medium Final_N4_High \
    Final_N8_Low Final_N8_Medium Final_N8_High
do
    ./out/gcc-release/src/LoadBalancingSimulation \
        -u Cmdenv \
        -n . \
        -f simulations/omnetpp.ini \
        -c "$config"
done
```

## Analysis

### Warm-up analysis

```bash
python3 analyze_warmup.py
```

### Batch analysis of an individual vector file

```bash
python3 analyze_batches.py <result.vec>
```

### Batch-independence diagnostic

```bash
python3 check_batch_independence.py
```

### Analyze all final scenarios

```bash
python3 analyze_all_results.py
```

This generates the combined summary and batch-level data inside the ignored simulation-results directory.

### Generate report figures and tables

```bash
python3 make_report_outputs.py
```

This generates:

- combined response-time figure
- combined waiting-time figure
- combined queue-length figure
- high-load scaling figure
- response-time summary
- percentage-improvement table
- validation summary

## Main Findings

The experiments show that queue-aware load balancing provides increasingly large benefits as the system becomes more heavily loaded.

Shortest Queue produces the lowest response times and queue lengths overall.

Power of Two Choices provides a substantial portion of the benefit of Shortest Queue while inspecting only two servers. With two servers, the two algorithms are effectively equivalent.

Random assignment performs worst under high load, while Round Robin performs better than Random but does not react to differences in instantaneous server queue lengths.

The advantage of queue-aware policies becomes increasingly pronounced as the server pool grows.

## Generated Files

Simulation results and generated artifacts are intentionally excluded from the repository, including:

```text
*.sca
*.vec
*.vci
*.anf
simulations/results/
```

Compiled binaries and Python cache files are also excluded.

This keeps the repository focused on source code, configuration files, and reproducible analysis scripts.
