"""The second, independent code for METRIC-GROW-20261110-001A-E001: balance, hearing lags and time lengths on READ-GROW-20261110-001A-
E001's grid_lib (written without choose_lib, net_lib or territory_lib), with the time length's route reach written here afresh: a
cell is reached at lag t + 1 when a cell it reads (itself and its left neighbour for an own cell, the two left neighbours for a
contact) was reached at lag t; a doubling keeps the reach of the old rings' own cells and nothing else."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments/READ-GROW-20261110-001A/READ-GROW-20261110-001A-E001_reading_distance_while_growing"))
import grid_lib as G2  # noqa: E402


def reach_step(G, R):
    g = G.g
    new = [False] * G.ncell
    for (i, r, p), b in G.own_index.items():
        new[b] = R[b] or R[G.cell(i, r, p - 1)]
    for (i, r), c in G.h.items():
        new[c] = R[G.cell(i, r, -1)] or R[G.cell(i + 1, r, 2 * g - 1)]
    for (i, r), c in G.v.items():
        new[c] = R[G.cell(i, r, g - 1)] or R[G.cell(i, r + 1, 3 * g - 1)]
    return new


def play(n, g, runs, read_balance=True):
    G = G2.Grid(n, g)
    G.double()
    stages = []
    if read_balance:
        f, per = G.read()
        stages.append({"lag": 0, "side": G.side, "balanced": not f, "period": per})
    R = [False] * G.ncell
    for p in G.own_pos:
        R[G.own_index[(0, 0, p)]] = True
    R1 = [False] * G.ncell
    R1[G.own_index[(0, 0, 1)]] = True
    Tl, T1l, Ll, t = {}, {}, {}, 0
    for P in runs:
        for _ in range(P):
            G.step()
            R = reach_step(G, R)
            R1 = reach_step(G, R1)
            t += 1
            k = G.side // n
            for a in range(n):
                for b in range(n):
                    if (a, b) != (0, 0) and (a, b) not in Tl and any(R[G.own_index[(a * k, b * k, p)]] for p in G.own_pos):
                        Tl[(a, b)] = t
                    if (a, b) != (0, 0) and (a, b) not in T1l and R1[G.own_index[(a * k, b * k, 1)]]:
                        T1l[(a, b)] = t
            for Y in G.hearers():
                Ll.setdefault(Y, t)
        old_index, oldR, oldR1 = G.own_index, R, R1
        G.double()
        R, R1 = [False] * G.ncell, [False] * G.ncell
        for (i, r, p), b in old_index.items():
            R[G.own_index[(2 * i, 2 * r, p)]] = oldR[b]
            R1[G.own_index[(2 * i, 2 * r, p)]] = oldR1[b]
        if read_balance:
            f, per = G.read()
            stages.append({"lag": t, "side": G.side, "balanced": not f, "period": per,
                           "first failure": min(f.values()) if f else None})
            if f:
                break
    return {"n": n, "g": g, "runs": list(runs), "stages": stages,
            "every stage balanced": bool(read_balance and all(s["balanced"] for s in stages) and len(stages) == len(runs) + 1),
            "T": Tl, "T1": T1l, "L": Ll}
