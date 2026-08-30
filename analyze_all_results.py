import csv
import glob
import os
import re

from analyze_batches import (
    export_vector,
    read_vectors,
    calculate_batches,
    summarize,
)


RESULT_PATTERN = (
    'simulations/results/Final_N*_*.vec'
)

LOAD_RHO = {
    "Low": 0.4,
    "Medium": 0.7,
    "High": 0.9,
}

METRICS = [
    "meanResponseTime",
    "meanWaitingTime",
    "throughput",
    "meanQueueLengthPerServer",
    "meanUtilization",
]


def parse_filename(filename):
    basename = os.path.basename(filename)

    match = re.match(
        r'Final_N(\d+)_(Low|Medium|High)_'
        r'"?([^"]+)"?\.vec$',
        basename
    )

    if match is None:
        raise ValueError(
            f"Could not parse filename: {basename}"
        )

    servers = int(match.group(1))
    load = match.group(2)
    algorithm = match.group(3)

    return servers, load, algorithm


def main():

    vec_files = sorted(
        glob.glob(RESULT_PATTERN)
    )

    print(
        f"Found {len(vec_files)} final "
        f"vector files."
    )

    if len(vec_files) != 36:
        print(
            "WARNING: expected exactly "
            "36 final scenarios."
        )

    summary_rows = []
    batch_rows = []

    for index, vec_file in enumerate(
        vec_files,
        start=1
    ):

        servers, load, algorithm = (
            parse_filename(vec_file)
        )

        rho = LOAD_RHO[load]
        arrival_rate = rho * servers

        print(
            f"[{index}/{len(vec_files)}] "
            f"N={servers}, "
            f"load={load}, "
            f"algorithm={algorithm}"
        )

        temp_csv = export_vector(vec_file)

        try:
            vectors = read_vectors(temp_csv)

            batches = calculate_batches(
                vectors
            )

        finally:
            os.remove(temp_csv)

        # -----------------------
        # Store individual batches
        # -----------------------

        for batch in batches:

            row = {
                "servers": servers,
                "load": load,
                "rho": rho,
                "arrivalRate": arrival_rate,
                "algorithm": algorithm,
            }

            row.update(batch)

            batch_rows.append(row)

        # -----------------------
        # Store scenario summary
        # -----------------------

        summary_row = {
            "servers": servers,
            "load": load,
            "rho": rho,
            "arrivalRate": arrival_rate,
            "algorithm": algorithm,
        }

        for metric in METRICS:

            result = summarize(
                batches,
                metric
            )

            summary_row[
                f"{metric}_mean"
            ] = result["mean"]

            summary_row[
                f"{metric}_stddev"
            ] = result["stddev"]

            summary_row[
                f"{metric}_ciLow"
            ] = result["ciLow"]

            summary_row[
                f"{metric}_ciHigh"
            ] = result["ciHigh"]

            summary_row[
                f"{metric}_ciHalfWidth"
            ] = result["ciHalfWidth"]

            summary_row[
                f"{metric}_lag1"
            ] = result["lag1"]

        summary_rows.append(
            summary_row
        )

    # Sort into an intuitive order.
    load_order = {
        "Low": 0,
        "Medium": 1,
        "High": 2,
    }

    algorithm_order = {
        "roundRobin": 0,
        "random": 1,
        "shortestQueue": 2,
        "powerOfTwo": 3,
    }

    summary_rows.sort(
        key=lambda r: (
            r["servers"],
            load_order[r["load"]],
            algorithm_order[
                r["algorithm"]
            ],
        )
    )

    batch_rows.sort(
        key=lambda r: (
            r["servers"],
            load_order[r["load"]],
            algorithm_order[
                r["algorithm"]
            ],
            r["batch"],
        )
    )

    summary_file = (
        "simulations/results/"
        "final_summary.csv"
    )

    batch_file = (
        "simulations/results/"
        "final_batches.csv"
    )

    with open(
        summary_file,
        "w",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=list(
                summary_rows[0].keys()
            ),
        )

        writer.writeheader()
        writer.writerows(summary_rows)

    with open(
        batch_file,
        "w",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=list(
                batch_rows[0].keys()
            ),
        )

        writer.writeheader()
        writer.writerows(batch_rows)

    print()
    print("Analysis complete.")
    print()
    print(
        f"Summary: {summary_file}"
    )
    print(
        f"Batches: {batch_file}"
    )
    print()
    print(
        f"Summary scenarios: "
        f"{len(summary_rows)}"
    )
    print(
        f"Batch observations: "
        f"{len(batch_rows)}"
    )


if __name__ == "__main__":
    main()
