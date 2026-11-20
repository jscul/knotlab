"""Draw one measured displacement using its occupied least-response locations."""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


HERE = Path(__file__).resolve().parent
DATA = HERE.parents[2] / "artifacts" / HERE.parent.name / HERE.name


def main():
    result = json.loads((DATA / "minimality_check.json").read_text())["bare_thirty_one"]
    occupied = {0, 1, 4}
    changes = [2, 5, 4, 0]
    rows = [occupied.copy()]
    for change in changes:
        occupied.symmetric_difference_update([change])
        rows.append(occupied.copy())
    assert rows[-1] == {v+1 for v in rows[0]}
    weights = result["phase_weights"] + result["phase_weights"][:1]
    fig, ax = plt.subplots(figsize=(7.3, 3.0))
    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.05, top=0.83)
    fig.suptitle("One place forward in four local changes", x=0.055, ha="left",
                 fontsize=16, fontweight="bold", color="#1c2b34")
    for i, sites in enumerate(rows):
        y = 4 - i
        ax.plot([0, 5], [y, y], color="#d6dce0", linewidth=1, zorder=0)
        ax.text(-0.45, y, ["Start", "Change 1", "Change 2", "Change 3", "Shifted"][i],
                ha="right", va="center", color="#273943", fontsize=10)
        ax.text(5.6, y, f"{weights[i]} distinctions", ha="left", va="center",
                fontsize=9, color="#3b4e58")
        for x in range(6):
            ax.scatter(x, y, s=85, color="#176e76" if x in sites else "#ffffff",
                       edgecolor="#176e76" if x in sites else "#a8b3b8",
                       linewidths=1.1, zorder=2)
    ax.set(xlim=(-1.85, 7.8), ylim=(-0.5, 4.55))
    ax.axis("off")
    fig.savefig(DATA / "one_place.png", dpi=150, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main()
