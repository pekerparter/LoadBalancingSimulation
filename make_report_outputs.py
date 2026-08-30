import os

import matplotlib.pyplot as plt
import pandas as pd


INPUT_FILE = "simulations/results/final_summary.csv"

OUTPUT_DIR = "simulations/results/report_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

df = pd.read_csv(INPUT_FILE)


ALGORITHMS = [
    "roundRobin",
    "random",
    "shortestQueue",
    "powerOfTwo",
]

LABELS = {
    "roundRobin": "Round Robin",
    "random": "Random",
    "shortestQueue": "Shortest Queue",
    "powerOfTwo": "Power of Two",
}

# Different markers and line styles also make the plots
# easier to read in grayscale and help with overlapping lines.
STYLES = {
    "roundRobin": {
        "marker": "o",
        "linestyle": "-",
    },
    "random": {
        "marker": "s",
        "linestyle": "--",
    },
    "shortestQueue": {
        "marker": "^",
        "linestyle": "-",
    },
    "powerOfTwo": {
        "marker": "D",
        "linestyle": "-.",
    },
}

LOADS = [0.4, 0.7, 0.9]

LOAD_LABELS = [
    "Low\n(0.4)",
    "Medium\n(0.7)",
    "High\n(0.9)",
]


def plot_algorithm(
    ax,
    data,
    algorithm,
    mean_column,
    ci_column,
    servers,
):
    style = STYLES[algorithm].copy()

    extra = {}

    # Special treatment for N=2:
    # SQ and Po2 are almost identical, so use visible
    # marker differences and plotting order.
    if servers == 2:
        if algorithm == "shortestQueue":
            extra = {
                "markersize": 8,
                "markerfacecolor": "none",
                "markeredgewidth": 1.8,
                "zorder": 5,
            }

        elif algorithm == "powerOfTwo":
            extra = {
                "markersize": 6,
                "zorder": 6,
            }

    ax.errorbar(
        data["rho"],
        data[mean_column],
        yerr=data[ci_column],
        label=LABELS[algorithm],
        linewidth=2,
        capsize=3,
        **style,
        **extra,
    )


def add_overlap_annotation(
    ax,
    subset,
    mean_column,
):
    sq = subset[
        subset["algorithm"] == "shortestQueue"
    ].sort_values("rho")

    po2 = subset[
        subset["algorithm"] == "powerOfTwo"
    ].sort_values("rho")

    sq_high = sq[
        sq["rho"] == 0.9
    ][mean_column].iloc[0]

    po2_high = po2[
        po2["rho"] == 0.9
    ][mean_column].iloc[0]

    overlap_y = (sq_high + po2_high) / 2

    ax.annotate(
        "Shortest Queue ≈ Power of Two\n"
        "(curves overlap for N = 2)",
        xy=(0.9, overlap_y),
        xycoords="data",
        xytext=(0.45, 0.62),
        textcoords="axes fraction",
        fontsize=9,
        ha="center",
        arrowprops={
            "arrowstyle": "->",
            "linewidth": 1,
        },
        bbox={
            "boxstyle": "round,pad=0.3",
            "facecolor": "white",
            "alpha": 0.9,
        },
    )


def combined_metric_plot(
    mean_column,
    ci_column,
    ylabel,
    title,
    filename,
):
    fig, axes = plt.subplots(
        1,
        3,
        figsize=(15.5, 5),
        sharey=True,
    )

    for index, servers in enumerate([2, 4, 8]):
        ax = axes[index]

        subset = df[
            df["servers"] == servers
        ]

        for algorithm in ALGORITHMS:
            data = subset[
                subset["algorithm"] == algorithm
            ].sort_values("rho")

            plot_algorithm(
                ax,
                data,
                algorithm,
                mean_column,
                ci_column,
                servers,
            )

        ax.set_title(
            f"({chr(97 + index)}) N = {servers}"
        )

        ax.set_xticks(
            LOADS,
            LOAD_LABELS,
        )

        ax.grid(
            True,
            alpha=0.25,
        )

        if index == 0:
            ax.set_ylabel(ylabel)

        if servers == 2:
            add_overlap_annotation(
                ax,
                subset,
                mean_column,
            )

    fig.supxlabel(
    "Offered load per server (ρ)",
    y=0.095,
    )

    fig.suptitle(
        title,
        fontsize=15,
    )

    handles, labels = axes[0].get_legend_handles_labels()

    fig.legend(
        handles,
        labels,
        loc="lower center",
        ncol=4,
        bbox_to_anchor=(0.5, 0.015),
        frameon=True,
    )

    fig.tight_layout(
        rect=[0, 0.15, 1, 0.93]
    )

    output = os.path.join(
        OUTPUT_DIR,
        filename,
    )

    fig.savefig(
        output,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)

    print(f"Saved {output}")


# --------------------------------------------------
# Combined report figures
# --------------------------------------------------

combined_metric_plot(
    mean_column="meanResponseTime_mean",
    ci_column="meanResponseTime_ciHalfWidth",
    ylabel="Mean response time (s)",
    title="Mean Response Time vs Offered Load",
    filename="response_time_combined.png",
)

combined_metric_plot(
    mean_column="meanWaitingTime_mean",
    ci_column="meanWaitingTime_ciHalfWidth",
    ylabel="Mean waiting time (s)",
    title="Mean Waiting Time vs Offered Load",
    filename="waiting_time_combined.png",
)

combined_metric_plot(
    mean_column="meanQueueLengthPerServer_mean",
    ci_column="meanQueueLengthPerServer_ciHalfWidth",
    ylabel="Mean queue length per server",
    title="Mean Queue Length vs Offered Load",
    filename="queue_length_combined.png",
)


# --------------------------------------------------
# High-load scaling figure
# --------------------------------------------------

high = df[
    df["load"] == "High"
]

fig, ax = plt.subplots(
    figsize=(8, 5.5)
)

for algorithm in ALGORITHMS:
    data = high[
        high["algorithm"] == algorithm
    ].sort_values("servers")

    ax.errorbar(
        data["servers"],
        data["meanResponseTime_mean"],
        yerr=data[
            "meanResponseTime_ciHalfWidth"
        ],
        label=LABELS[algorithm],
        linewidth=2,
        capsize=4,
        **STYLES[algorithm],
    )


# Explicitly note the N=2 equivalence.
n2 = high[
    high["servers"] == 2
]

sq_n2 = n2[
    n2["algorithm"] == "shortestQueue"
]["meanResponseTime_mean"].iloc[0]

po2_n2 = n2[
    n2["algorithm"] == "powerOfTwo"
]["meanResponseTime_mean"].iloc[0]

ax.annotate(
    "SQ ≈ Po2 at N = 2",
    xy=(
        2,
        (sq_n2 + po2_n2) / 2,
    ),
    xytext=(3.0, 4.7),
    arrowprops={
        "arrowstyle": "->",
        "linewidth": 1,
    },
    bbox={
        "boxstyle": "round,pad=0.3",
        "facecolor": "white",
        "alpha": 0.9,
    },
)

ax.set_xticks([2, 4, 8])

ax.set_xlabel(
    "Number of servers"
)

ax.set_ylabel(
    "Mean response time (s)"
)

ax.set_title(
    "High-Load Response Time vs Number of Servers"
)

ax.grid(
    True,
    alpha=0.25,
)

ax.legend()

fig.tight_layout()

output = os.path.join(
    OUTPUT_DIR,
    "high_load_scaling.png",
)

fig.savefig(
    output,
    dpi=300,
    bbox_inches="tight",
)

plt.close(fig)

print(f"Saved {output}")


# --------------------------------------------------
# Response-time summary table
# --------------------------------------------------

load_order = pd.CategoricalDtype(
    ["Low", "Medium", "High"],
    ordered=True,
)

table_df = df.copy()
table_df["load"] = table_df[
    "load"
].astype(load_order)

response_table = table_df.pivot_table(
    index=[
        "servers",
        "load",
        "rho",
    ],
    columns="algorithm",
    values="meanResponseTime_mean",
    observed=True,
).reset_index()

response_table = response_table[
    [
        "servers",
        "load",
        "rho",
        "random",
        "roundRobin",
        "powerOfTwo",
        "shortestQueue",
    ]
]

response_table.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "response_time_summary.csv",
    ),
    index=False,
)


# --------------------------------------------------
# Percentage improvements
# --------------------------------------------------

improvement_rows = []

for _, row in response_table.iterrows():

    random_value = row["random"]
    rr_value = row["roundRobin"]

    sq_value = row["shortestQueue"]
    po2_value = row["powerOfTwo"]

    improvement_rows.append(
        {
            "servers": row["servers"],
            "load": row["load"],
            "rho": row["rho"],

            "shortestQueue_response": sq_value,
            "powerOfTwo_response": po2_value,

            "SQ_vs_Random_percent":
                100
                * (random_value - sq_value)
                / random_value,

            "Po2_vs_Random_percent":
                100
                * (random_value - po2_value)
                / random_value,

            "SQ_vs_RoundRobin_percent":
                100
                * (rr_value - sq_value)
                / rr_value,

            "Po2_vs_RoundRobin_percent":
                100
                * (rr_value - po2_value)
                / rr_value,
        }
    )

improvements = pd.DataFrame(
    improvement_rows
)

improvements.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "response_time_improvements.csv",
    ),
    index=False,
)


# --------------------------------------------------
# Validation table
# --------------------------------------------------

validation = (
    df.groupby(
        [
            "servers",
            "load",
            "rho",
            "arrivalRate",
        ]
    )
    .agg(
        measuredThroughput=(
            "throughput_mean",
            "mean",
        ),
        measuredUtilization=(
            "meanUtilization_mean",
            "mean",
        ),
    )
    .reset_index()
)

validation["throughputErrorPercent"] = (
    100
    * (
        validation["measuredThroughput"]
        - validation["arrivalRate"]
    )
    / validation["arrivalRate"]
)

validation["utilizationErrorPercent"] = (
    100
    * (
        validation["measuredUtilization"]
        - validation["rho"]
    )
    / validation["rho"]
)

validation.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "validation_summary.csv",
    ),
    index=False,
)


print()
print("Report outputs generated successfully.")
print(f"Directory: {OUTPUT_DIR}")
