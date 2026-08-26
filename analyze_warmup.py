import csv
import glob
import os
import subprocess
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np


RESULT_DIR = "simulations/results"

CONFIGS = [
    "WarmupHighRoundRobin",
    "WarmupHighRandom",
    "WarmupHighShortestQueue",
    "WarmupHighPowerOfTwo",
]

RUNS = range(5)

BIN_WIDTH = 25.0
SIM_TIME = 2000.0


def export_vec_to_csv(vec_file, csv_file):
    subprocess.run(
        [
            "opp_scavetool",
            "x",
            vec_file,
            "-o",
            csv_file
        ],
        check=True
    )


def read_response_times(csv_file):
    observations = []

    with open(csv_file, newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            if row["type"] != "vector":
                continue

            if row["name"].startswith("responseTime"):
                continue

            times = row["vectime"].split()
            values = row["vecvalue"].split()

            for t, value in zip(times, values):
                observations.append(
                    (float(t), float(value))
                )

    print(f"  Found {len(observations)} response-time observations in {csv_file}")
    return observations


def calculate_binned_means(observations):
    bins = np.arange(
        0,
        SIM_TIME + BIN_WIDTH,
        BIN_WIDTH
    )

    sums = np.zeros(len(bins) - 1)
    counts = np.zeros(len(bins) - 1)

    for time, value in observations:
        index = int(time // BIN_WIDTH)

        if 0 <= index < len(sums):
            sums[index] += value
            counts[index] += 1

    means = np.full(len(sums), np.nan)

    valid = counts > 0
    means[valid] = sums[valid] / counts[valid]

    centers = (
        bins[:-1] + bins[1:]
    ) / 2.0

    return centers, means


all_config_means = {}


for config in CONFIGS:
    repetition_means = []

    for run in RUNS:
        vec_file = os.path.join(
            RESULT_DIR,
            f"{config}-#{run}.vec"
        )

        csv_file = os.path.join(
            RESULT_DIR,
            f"{config}-#{run}-warmup.csv"
        )

        if not os.path.exists(vec_file):
            raise FileNotFoundError(
                f"Missing {vec_file}"
            )

        print(
            f"Processing {config}, repetition {run}"
        )

        export_vec_to_csv(
            vec_file,
            csv_file
        )

        observations = read_response_times(
            csv_file
        )

        centers, means = (
            calculate_binned_means(
                observations
            )
        )

        repetition_means.append(means)

    repetition_means = np.array(
        repetition_means
    )

    config_mean = np.nanmean(
        repetition_means,
        axis=0
    )

    all_config_means[config] = (
        centers,
        config_mean
    )


for config, (centers, means) in all_config_means.items():

    plt.figure(figsize=(10, 5))

    plt.plot(
        centers,
        means
    )

    plt.xlabel("Simulation time (s)")
    plt.ylabel("Mean response time (s)")
    plt.title(
        f"Warm-up diagnostic: {config}"
    )

    plt.grid(True)

    plt.tight_layout()

    output_file = (
        f"{config}_warmup.png"
    )

    plt.savefig(
        output_file,
        dpi=150
    )

    plt.close()

    print(
        f"Saved {output_file}"
    )


print("Warm-up analysis complete.")
