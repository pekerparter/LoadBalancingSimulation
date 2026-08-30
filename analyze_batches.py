import csv
import math
import os
import re
import subprocess
import sys
import tempfile

import numpy as np

csv.field_size_limit(sys.maxsize)

WARMUP = 500.0
BATCH_WIDTH = 4000.0
NUMBER_OF_BATCHES = 64

MEASUREMENT_END = (
    WARMUP
    + BATCH_WIDTH * NUMBER_OF_BATCHES
)


def export_vector(vec_file):
    temp = tempfile.NamedTemporaryFile(
        suffix=".csv",
        delete=False
    )

    temp.close()

    subprocess.run(
        [
            "opp_scavetool",
            "x",
            vec_file,
            "-o",
            temp.name
        ],
        check=True,
        stdout=subprocess.DEVNULL
    )

    return temp.name


def read_vectors(csv_file):
    vectors = {}

    with open(csv_file, newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            if row["type"] != "vector":
                continue

            module = row["module"]

            # OMNeT++ names can look like:
            # responseTime:vector
            name = row["name"].split(":")[0]

            times = [
                float(x)
                for x in row["vectime"].split()
            ]

            values = [
                float(x)
                for x in row["vecvalue"].split()
            ]

            vectors[(module, name)] = list(
                zip(times, values)
            )

    return vectors


def server_index(module):
    match = re.search(
        r"server\[(\d+)\]",
        module
    )

    if match is None:
        return None

    return int(match.group(1))


def event_values_in_batch(
    vectors,
    metric,
    start,
    end
):
    values = []

    for (module, name), observations in vectors.items():

        if server_index(module) is None:
            continue

        if name != metric:
            continue

        for time, value in observations:

            if start <= time < end:
                values.append(value)

    return values


def state_average(
    observations,
    start,
    end,
    default_state=0.0
):
    """
    Time-weighted average of a state vector.

    Example:
        queue length = 2 from t=600 to t=650
    contributes:
        2 * 50
    to the area.
    """

    observations = sorted(observations)

    current_state = default_state

    # Find state immediately before batch start.
    for time, value in observations:
        if time <= start:
            current_state = value
        else:
            break

    current_time = start
    area = 0.0

    for time, value in observations:

        if time <= start:
            continue

        if time >= end:
            break

        area += (
            current_state
            * (time - current_time)
        )

        current_state = value
        current_time = time

    area += (
        current_state
        * (end - current_time)
    )

    return area / (end - start)


def state_metric_for_batch(
    vectors,
    metric,
    start,
    end
):
    per_server = []

    for (module, name), observations in vectors.items():

        if server_index(module) is None:
            continue

        if name != metric:
            continue

        average = state_average(
            observations,
            start,
            end
        )

        per_server.append(average)

    if not per_server:
        return math.nan

    # Average across all servers.
    return float(np.mean(per_server))


def calculate_batches(vectors):
    rows = []

    for batch in range(NUMBER_OF_BATCHES):

        start = (
            WARMUP
            + batch * BATCH_WIDTH
        )

        end = start + BATCH_WIDTH

        response_times = event_values_in_batch(
            vectors,
            "responseTime",
            start,
            end
        )

        waiting_times = event_values_in_batch(
            vectors,
            "waitingTime",
            start,
            end
        )

        mean_response = (
            float(np.mean(response_times))
            if response_times
            else math.nan
        )

        mean_waiting = (
            float(np.mean(waiting_times))
            if waiting_times
            else math.nan
        )

        # One responseTime observation corresponds
        # to one completed measured job.
        throughput = (
            len(response_times)
            / BATCH_WIDTH
        )

        mean_queue = state_metric_for_batch(
            vectors,
            "queueLength",
            start,
            end
        )

        utilization = state_metric_for_batch(
            vectors,
            "busy",
            start,
            end
        )

        rows.append({
            "batch": batch + 1,
            "start": start,
            "end": end,
            "meanResponseTime": mean_response,
            "meanWaitingTime": mean_waiting,
            "throughput": throughput,
            "meanQueueLengthPerServer": mean_queue,
            "meanUtilization": utilization,
            "completedJobs": len(response_times),
        })

    return rows


def lag1_autocorrelation(values):
    values = np.array(
        [
            x for x in values
            if not math.isnan(x)
        ],
        dtype=float
    )

    if len(values) < 3:
        return math.nan

    x = values[:-1]
    y = values[1:]

    if np.std(x) == 0 or np.std(y) == 0:
        return 0.0

    return float(
        np.corrcoef(x, y)[0, 1]
    )


def summarize(rows, metric):
    values = np.array(
        [
            row[metric]
            for row in rows
            if not math.isnan(row[metric])
        ],
        dtype=float
    )

    n = len(values)

    mean = float(np.mean(values))

    stddev = float(
        np.std(values, ddof=1)
    )

    standard_error = (
        stddev / math.sqrt(n)
    )

    t_critical = 1.998

    half_width = (
        t_critical
        * standard_error
    )

    return {
        "n": n,
        "mean": mean,
        "stddev": stddev,
        "ciLow": mean - half_width,
        "ciHigh": mean + half_width,
        "ciHalfWidth": half_width,
        "lag1": lag1_autocorrelation(values),
    }


def main():
    if len(sys.argv) != 2:
        print(
            "Usage: python3 analyze_batches.py "
            "<result.vec>"
        )
        sys.exit(1)

    vec_file = sys.argv[1]

    if not os.path.exists(vec_file):
        raise FileNotFoundError(vec_file)

    print(f"Processing {vec_file}")

    csv_file = export_vector(vec_file)

    try:
        vectors = read_vectors(csv_file)
        rows = calculate_batches(vectors)
    finally:
        os.remove(csv_file)

    output_csv = (
        os.path.splitext(vec_file)[0]
        + "_batches.csv"
    )

    with open(
        output_csv,
        "w",
        newline=""
    ) as f:

        fieldnames = list(rows[0].keys())

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(rows)

    print()
    print(f"Saved batch results to:")
    print(output_csv)
    print()

    metrics = [
        "meanResponseTime",
        "meanWaitingTime",
        "throughput",
        "meanQueueLengthPerServer",
        "meanUtilization",
    ]

    print("Batch-means summary")
    print("===================")

    for metric in metrics:

        result = summarize(
            rows,
            metric
        )

        print()
        print(metric)
        print(
            f"  Mean:       "
            f"{result['mean']:.6f}"
        )
        print(
            f"  Std dev:    "
            f"{result['stddev']:.6f}"
        )
        print(
            f"  95% CI:     "
            f"[{result['ciLow']:.6f}, "
            f"{result['ciHigh']:.6f}]"
        )
        print(
            f"  CI ±:       "
            f"{result['ciHalfWidth']:.6f}"
        )
        print(
            f"  Lag-1 corr: "
            f"{result['lag1']:.4f}"
        )


if __name__ == "__main__":
    main()
