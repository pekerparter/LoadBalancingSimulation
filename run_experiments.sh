#!/bin/bash

set -e

EXEC="./out/clang-release/src/LoadBalancingSimulation"
INI="simulations/omnetpp.ini"

configs=(
    Final_N2_Low
    Final_N2_Medium
    Final_N2_High
    Final_N4_Low
    Final_N4_Medium
    Final_N4_High
    Final_N8_Low
    Final_N8_Medium
    Final_N8_High
)

for config in "${configs[@]}"; do
    echo
    echo "======================================"
    echo "Running $config"
    echo "======================================"

    "$EXEC" \
        -u Cmdenv \
        -n . \
        -f "$INI" \
        -c "$config"
done

echo
echo "All 36 final scenarios completed successfully."