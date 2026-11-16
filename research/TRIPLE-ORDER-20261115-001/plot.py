"""Draw exact search work and the cumulative cost of training and deployment."""
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


def draw(out):
    result = json.loads((out / "result.json").read_bytes())
    fig, (counts, money) = plt.subplots(1, 2, figsize=(10.0, 3.35),
                                       width_ratios=(1, 1.4), layout="constrained")
    colors = {"lex":"#79909b", "learned":"#1a6266"}
    for label, arm, shift in (("Lexical order","lex",-.18), ("Learned order","learned",.18)):
        groups = result["methods"][arm]["groups"]
        values = [groups[k]["trials"] for k in ("shared","rewired")]
        bars = counts.bar([shift,1+shift], values, width=.34, label=label, color=colors[arm])
        counts.bar_label(bars, labels=[f"{v:,.0f}" for v in values], padding=2, fontsize=8)
    counts.set(xticks=[0,1], xticklabels=["Shared","Rewired"], ylabel="Exact triple checks",
               title="Which checks the ordering saved")
    counts.margins(y=.19)
    counts.yaxis.set_major_formatter(FuncFormatter(lambda v,_: f"{v:,.0f}"))
    counts.legend(frameon=False, ncols=2, loc="upper center", fontsize=8)
    for key, name, color in (("fully_paid","Training and deployment","#115e64"),
                             ("raw_training_tables_available","Raw training tables supplied","#a05a20"),
                             ("frozen_policy_available","Deployment alone","#596a78")):
        gaps = result["trajectories"][key]["cumulative_gap_ns"]
        money.plot(range(len(gaps)), [v/1e6 for v in gaps], color=color, label=name, lw=1.9)
    money.axhline(0, color="#343a3f", linewidth=.8)
    money.set(xlim=(0,result["tasks"]), xticks=[0,48,96,144,192],
              xlabel="Verified rules returned", ylabel="Extra CPU vs. best untrained method (ms)",
              title="When the training cost is paid")
    money.legend(frameon=False, fontsize=8)
    for ax in (counts,money):
        ax.set_axisbelow(True)
        ax.grid(axis="y",color="#e5e8ea",lw=.8)
        ax.spines[["top","right"]].set_visible(False)
    fig.savefig(out / "ranking-cost.png", dpi=145, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    draw(Path(sys.argv[1]))
