"""Draw paired CPU differences for the two best primitive comparators."""
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator


def draw(directory):
    result = json.loads((directory / "result.json").read_bytes())
    warm = result["methods"]["primary-warm"]
    named = warm["named"]["cpu_repeats_ns"]
    fig, ax = plt.subplots(figsize=(8.1, 2.85), layout="constrained")
    for offset, arm, label, color, marker in (
        (-.10, result["benchmark"], "vs. fastest primitive", "#20657e", "o"),
        (.10, "primitive", "vs. same solver with primitives", "#854829", "D"),
    ):
        diffs = [(t - v) / 1e6 for t, v in zip(named, warm[arm]["cpu_repeats_ns"], strict=True)]
        ax.scatter([i + offset for i in range(1, len(diffs) + 1)], diffs, color=color,
                   marker=marker, s=39, label=label, zorder=3)
    ax.axhline(0, color="#404950", lw=1.1)
    ax.set(xticks=range(1, 11), xlim=(.6, 10.4), ylim=(-4.8, 17),
           xlabel="Paired repeat", ylabel="Fold CPU minus\nprimitive CPU (ms)")
    ax.yaxis.set_major_locator(MultipleLocator(5))
    ax.grid(axis="y", color="#e0e4e7", linewidth=.8)
    fig.suptitle("CPU difference for 48 verified programs", size=14, weight="bold")
    ax.legend(loc="upper left", ncols=2, frameon=False, fontsize=9)
    ax.spines[["right", "top"]].set_visible(False)
    fig.savefig(directory / "paired-cpu.png", dpi=145, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    draw(Path(sys.argv[1]))
