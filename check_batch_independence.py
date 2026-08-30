import csv
import glob
import math
import os
import re

from analyze_batches import (
    export_vector,
    read_vectors,
    calculate_batches,
    summarize,
)


FILES = sorted(
    glob.glob(
        'simulations/results/Final_N*_High_*.vec'
    )
)

METRICS = [
    ("Response", "meanResponseTime"),
    ("Waiting", "meanWaitingTime"),
    ("Throughput", "throughput"),
    ("Queue", "meanQueueLengthPerServer"),
    ("Utilization", "meanUtilization"),
]

# Approximate 95% significance band for an
# autocorrelation when n = 20 batch means.
N_BATCHES = 64
ROUGH_LIMIT = 1.96 / math.sqrt(N_BATCHES)


def parse_filename(filename):
    basename = os.path.basename(filename)

    match = re.match(
        r'Final_N(\d+)_High_"?([^"]+)"?\.vec$',
        basename
    )

    if not match:
        raise ValueError(
            f"Cannot parse filename: {basename}"
        )

    return int(match.group(1)), match.group(2)


rows = []

print()
print(
    f"Approximate reference band: "
    f"±{ROUGH_LIMIT:.3f}"
)
print()

for vec_file in FILES:

    n_servers, algorithm = parse_filename(
        vec_file
    )

    print(
        f"Processing N={n_servers}, "
        f"{algorithm}..."
    )

    temp_csv = export_vector(vec_file)

    try:
        vectors = read_vectors(temp_csv)
        batches = calculate_batches(vectors)
    finally:
        os.remove(temp_csv)

    result = {
        "servers": n_servers,
        "algorithm": algorithm,
    }

    for display_name, metric in METRICS:
        summary = summarize(
            batches,
            metric
        )

        result[display_name] = summary["lag1"]

    rows.append(result)


rows.sort(
    key=lambda row: (
        row["servers"],
        row["algorithm"]
    )
)


print()
print(
    f"{'N':>3} "
    f"{'Algorithm':<15} "
    f"{'Resp':>8} "
    f"{'Wait':>8} "
    f"{'Thrpt':>8} "
    f"{'Queue':>8} "
    f"{'Util':>8} "
    f"{'Max |r1|':>10}"
)

print("-" * 83)

for row in rows:

    correlations = [
        row["Response"],
        row["Waiting"],
        row["Throughput"],
        row["Queue"],
        row["Utilization"],
    ]

    maximum = max(
        abs(value)
        for value in correlations
    )

    print(
        f"{row['servers']:>3} "
        f"{row['algorithm']:<15} "
        f"{row['Response']:>8.3f} "
        f"{row['Waiting']:>8.3f} "
        f"{row['Throughput']:>8.3f} "
        f"{row['Queue']:>8.3f} "
        f"{row['Utilization']:>8.3f} "
        f"{maximum:>10.3f}"
    )


output_file = (
    "simulations/results/"
    "high_load_batch_independence.csv"
)

with open(
    output_file,
    "w",
    newline=""
) as f:

    fieldnames = [
        "servers",
        "algorithm",
        "Response",
        "Waiting",
        "Throughput",
        "Queue",
        "Utilization",
    ]

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()

    for row in rows:
        writer.writerow(row)


print()
print(
    f"Saved table to {output_file}"
)
