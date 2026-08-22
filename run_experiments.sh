#!/bin/bash

set -e

EXEC="./out/clang-release/src/LoadBalancingSimulation"
INI="simulations/omnetpp.ini"

configs=(
    LowRoundRobin
    LowRandom
    LowShortestQueue
    LowPowerOfTwo
    MediumRoundRobin
    MediumRandom
    MediumShortestQueue
    MediumPowerOfTwo
    HighRoundRobin
    HighRandom
    HighShortestQueue
    HighPowerOfTwo
)

for config in "${configs[@]}"; do
    for run in {0..9}; do
        echo "Running $config repetition $run"

        "$EXEC" \
            -u Cmdenv \
            -n . \
            -f "$INI" \
            -c "$config" \
            -r "$run"
    done
done

echo "All experiments completed successfully."
