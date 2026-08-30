import csv
import os
import subprocess

import matplotlib.pyplot as plt
import numpy as np


RESULT_DIR = "simulations/results"

CONFIG_GROUPS = {
    2: {
        "Round Robin": "WarmupHighRoundRobin",
        "Random": "WarmupHighRandom",
        "Shortest Queue": "WarmupHighShortestQueue",
        "Power of Two": "WarmupHighPowerOfTwo",
    },

    4: {
        "Round Robin": "WarmupN4RoundRobin",
        "Random": "WarmupN4Random",
        "Shortest Queue": "WarmupN4ShortestQueue",
        "Power of Two": "WarmupN4PowerOfTwo",
    },

    8: {
        "Round Robin": "WarmupN8RoundRobin",
        "Random": "WarmupN8Random",
        "Shortest Queue": "WarmupN8ShortestQueue",
        "Power of Two": "WarmupN8PowerOfTwo",
    },
}

RUNS = range(5)

SIM_TIME = 2000.0

# Larger than before to smooth the curves more clearly.
BIN_WIDTH = 50.0


def export_vec_to_csv(vec_file, csv_file):
    subprocess.run(
        [
            "opp_scavetool",
            "x",
            vec_file,
            "-o",
            csv_file
        ],
        check=True,
        stdout=subprocess.DEVNULL
    )


def read_response_times(csv_file):
    observations = []

    with open(csv_file, newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            if row["type"] != "vector":
                continue

            if not row["name"].startswith("responseTime"):
                continue

            times = row["vectime"].split()
            values = row["vecvalue"].split()

            for time, value in zip(times, values):
                observations.append(
                    (float(time), float(value))
                )

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


def process_configuration(config):
    repetition_means = []

    for run in RUNS:

        vec_file = os.path.join(
            RESULT_DIR,
            f"{config}-#{run}.vec"
        )

        csv_file = os.path.join(
            RESULT_DIR,
            f"{config}-#{run}-warmup-temp.csv"
        )

        if not os.path.exists(vec_file):
            raise FileNotFoundError(
                f"Missing result file: {vec_file}"
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

        print(
            f"  Found {len(observations)} "
            f"response-time observations"
        )

        centers, means = calculate_binned_means(
            observations
        )

        repetition_means.append(means)

        # The CSV is temporary.
        os.remove(csv_file)

    repetition_means = np.array(
        repetition_means
    )

    mean_across_repetitions = np.nanmean(
        repetition_means,
        axis=0
    )

    return centers, mean_across_repetitions


for number_of_servers, algorithms in CONFIG_GROUPS.items():

    plt.figure(figsize=(11, 6))

    for algorithm_name, config_name in algorithms.items():

        centers, means = process_configuration(
            config_name
        )

        plt.plot(
            centers,
            means,
            label=algorithm_name
        )

    plt.xlabel("Simulation time (s)")
    plt.ylabel("Mean response time (s)")

    plt.title(
        f"Warm-up diagnostic - "
        f"{number_of_servers} servers - high load"
    )

    plt.legend()
    plt.grid(True)

    plt.tight_layout()

    output_file = (
        f"Warmup_N{number_of_servers}_comparison.png"
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