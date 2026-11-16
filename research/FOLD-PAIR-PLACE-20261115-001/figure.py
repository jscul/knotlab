"""Plot grouping work and the paid cost of three blind strategies from the verified receipts."""
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parents[2]
first = "FOLD-PLACEMENT-20261115-001"
second = "FOLD-PAIR-PLACE-20261115-001"
first_out = root / "artifacts" / first / (first + "-E001_fixed_inputs")
second_out = Path(sys.argv[1]).resolve() if sys.argv[1:] else root / "artifacts" / second / (second + "-E001_pair_first")
initial = json.loads((first_out / "result.json").read_text())["methods"]["warm"]
latest = json.loads((second_out / "result.json").read_text())["methods"]["warm"]

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
fig, axes = plt.subplots(1, 2, figsize=(10, 3.25), layout="constrained")
for ax in axes:
    ax.spines[["right", "top", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0, pad=5)
    ax.set_axisbelow(True)
    ax.grid(axis="x", alpha=.18)

def bars(ax, labels, values, tick, colors, fmt):
    ax.barh(range(len(labels)), values, height=.57, color=colors)
    ax.set_yticks(range(len(labels)), labels)
    ax.invert_yaxis()
    ax.set_xlabel(tick)
    longest = max(values)
    ax.set_xlim(0, 1.28 * longest)
    for i, value in enumerate(values):
        ax.text(value + .025 * longest, i, format(value, fmt), va="center")

left, right = axes
left.set_title("Finding a three-input group", loc="left", fontweight="bold")
bars(left, ["Blind fold", "Fold with one hint"],
     [initial["placement-named-blind"]["tests"], initial["placement-named-hint"]["tests"]],
     "Candidate tests on 48 rules", ["#a85229", "#315f86"], ",.0f")
right.set_title("Finding a group without hints", loc="left", fontweight="bold")
keys = ["triple-primitive", "atomic-primitive", "guided-named", "guided-flat"]
bars(right, ["Primitive triples", "One primitive pair", "Pair then fold", "Pair then inline"],
     [latest[k]["paid_cpu_ns"] / 1e6 for k in keys], "Verified stream, median process CPU (ms)",
     ["#627885", "#288279", "#a85229", "#bc825b"], ".1f")
fig.savefig(second_out / "placement-comparison.png", dpi=165, facecolor="white")
