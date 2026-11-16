"""Plot the two marginally indistinguishable records in the saved braid census."""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    root = Path(__file__).resolve().parents[2]
    ticket = "STRAND-RETURN-20261114-001"
    directory = root / "artifacts" / ticket / (ticket + "-E002_braid_readers")
    rows = [json.loads(line) for line in (directory / "results.jsonl").read_text().splitlines()]
    case = next(row for row in rows if row["case"] == "ternary-mixing" and row["status"] == "ok")
    fixtures = case["result"]["allowed_relations"]["held_x_examples"]
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.4), layout="constrained")
    for ax, fixture, color in zip(axes, fixtures, ("#006d70", "#714291")):
        xs, ys = zip(*fixture["crossed_pairs"])
        ax.scatter(xs, ys, s=170, color=color, zorder=3)
        ax.set(xlim=(-0.45, 2.45), ylim=(-0.45, 2.45), aspect="equal",
               xticks=(0, 1, 2), yticks=(0, 1, 2), xlabel="First value after crossing")
        ax.set_title(f"Started with first value {fixture['initial_x']}", fontsize=13, pad=9)
        ax.grid(color="#d7dde1", linewidth=1)
        ax.tick_params(length=0, pad=4)
        for spine in ax.spines.values():
            spine.set_visible(False)
    axes[0].set_ylabel("Second value after crossing")
    fig.savefig(directory / "allowed_pairs.png", dpi=150, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main()
