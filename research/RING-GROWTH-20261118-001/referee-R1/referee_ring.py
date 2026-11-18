"""Referee R1 for RING-GROWTH-20261118-001 (own code; the study's ring code and check.py are not imported).

  ../../../.venv/bin/python -B referee_ring.py <part> > referee_ring_<part>.json      (from this directory)

Growth: the referee's FIRST-KNOT-R1 engine (complete-round joining rule, GF(2) implied parity, the fewest rule).

Parts:
  model    the ring of four four-place knots and one five-place knot: the advisor's (v, S) model, written from the proof's
           section 2 (positions on the cylinder, sets of lifts, parents |S| + the two position steps still above S, demand
           2 + m(v) - |S|), against the grown pattern round by round: junctions per round and the joint histogram of (number of
           parents, fresh distinctions) per round, through as many rounds as the growth reaches under 40,000 junctions.
  formula  the general formula on every faster-than-power ring of the census (13) and on rings of 4, 6, 7, 8 knots with one
           five-place knot: j = the spare open distinctions (open minus two per knot), the predicted rate (root of
           x^(n + j) = (1 + x)^j), the measured rate, and whether c(t) = sum_i C(j, i) c(t - n - i) holds exactly on the computed tail.
"""
import itertools
import json
import math
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/FIRST-KNOT-20261118-001/referee-R1"))
sys.path.insert(0, str(ROOT / "research/TOUCH-CENSUS-20261118-001/referee-R1"))
import referee_first as RFK  # noqa: E402
import referee_touch as RT  # noqa: E402


def ring(sizes):
    """A clean ring: knot i shares one distinction with knot i + 1."""
    n = len(sizes)
    M = [[0] * n for _ in range(n)]
    for i in range(n):
        j = (i + 1) % n
        M[i][j] = M[j][i] = 1
    return list(sizes), M


def grown(sizes, M, maxj=40000, rounds=200):
    G = RFK.Start(RT.stars(sizes, M))
    for _ in range(rounds):
        if G.step(RFK.fewest, None, None) != "ok" or len(G.bits) > maxj:
            break
    return G


def growth_histograms(G):
    by = {}
    for j in range(len(G.bits)):
        r = G.round[j]
        if r == 0:
            continue
        by.setdefault(r, Counter())[(len(G.parents[j]), G.fresh[j])] += 1
    return by


def model_histograms(T):
    """The (v, S) model: positions v = (a, b) of height h = a + b >= 0 on the cylinder (a, b) ~ (a + 5, b - 5), represented
    by a in 0..4; lifts p_k = (5k, -5k) below v when 5k <= a and -5k <= b; a junction (v, S) has round h + |S|; parents
    |S| + [S below v - e_a] + [S below v - e_b] (for h >= 1); demand 2 + m(v) - |S|."""
    def lifts(a, b):
        return [k for k in range(-60, 60) if 5 * k <= a and -5 * k <= b]
    out = {}
    for h in range(0, T + 1):
        for a in range(5):
            b = h - a
            L = lifts(a, b)
            for s in range(0, len(L) + 1):
                t = h + s
                if t == 0 or t > T:
                    continue
                for S in itertools.combinations(L, s):
                    Sset = set(S)
                    par = len(S)
                    if h >= 1:
                        par += Sset <= set(lifts(a - 1, b))
                        par += Sset <= set(lifts(a, b - 1))
                    dem = 2 + len(L) - len(S)
                    out.setdefault(t, Counter())[(par, dem)] += 1
    return out


def part_model():
    sizes, M = ring([5, 4, 4, 4, 4])
    G = grown(sizes, M)
    T = max(G.round) - 1          # the last complete round
    gh = growth_histograms(G)
    mh = model_histograms(T)
    rows = []
    agree_counts = agree_hist = True
    for t in range(1, T + 1):
        g, m = gh.get(t, Counter()), mh.get(t, Counter())
        same_n = sum(g.values()) == sum(m.values())
        same_h = g == m
        agree_counts &= same_n
        agree_hist &= same_h
        rows.append({"round": t, "grown": sum(g.values()), "model": sum(m.values()), "histograms equal": same_h})
    c = [sum(gh[t].values()) for t in range(1, T + 1)]
    rec = all(c[t - 1] == c[t - 6] + c[t - 7] for t in range(7, T + 1))
    return {"rounds compared": T, "junctions": len(G.bits), "counts equal every round": agree_counts,
            "(parents, fresh) histograms equal every round": agree_hist,
            "c(t) = c(t - 5) + c(t - 6) for every t >= 7 computed": rec, "rounds": rows}


def spare(sizes, M):
    n = len(sizes)
    return sum(sizes[i] - sum(M[i]) - 2 for i in range(n))


def predicted_rate(n, j):
    if j == 0:
        return 1.0
    lo, hi = 1.0, 3.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if mid ** (n + j) < (1 + mid) ** j:
            lo = mid
        else:
            hi = mid
    return round(lo, 4)


def check_formula(c, n, j):
    """Does c(t) = sum_i C(j, i) c(t - n - i) hold on the tail (the last 2(n + j) terms)?"""
    L = n + j
    if len(c) < L + 2 * L:
        return None
    tail_start = len(c) - 2 * L
    ok = all(c[t] == sum(math.comb(j, i) * c[t - n - i] for i in range(j + 1)) for t in range(tail_start, len(c)))
    first = None
    for s in range(L, len(c)):
        if all(c[t] == sum(math.comb(j, i) * c[t - n - i] for i in range(j + 1)) for t in range(s, len(c))):
            first = s + 1
            break
    return {"holds on the last 2(n + j) rounds": ok, "holds from round": first}


def part_formula():
    rows = RT.study_rows()
    census = [r["key"] for r in rows if r["dim"] == 6 or (r["dim"] is None and r["outcome"] not in ("stall", "closed"))]
    keys = set(map(lambda k: (tuple(k[0]), tuple(k[1])), census))
    # the arrangements the run had not read (grown by the TOUCH-CENSUS referee); add the exponential ones
    miss = json.load(open(ROOT / "research/TOUCH-CENSUS-20261118-001/referee-R1/referee_touch_missing.json"))["rows"]
    for r in miss:
        if r["dim"] == "unsettled":
            keys.add((tuple(r["key"][0]), tuple(r["key"][1])))
    out = {"census rings": len(keys), "rings": []}
    for sizes, flat in sorted(keys):
        s, M = RT.key_to(sizes, flat)
        n = len(s)
        j = spare(s, M)
        G = grown(s, M, maxj=40000)
        c = G.counts()[1:-1] if len(G.counts()) > 2 else G.counts()[1:]
        meas = round(c[-1] / c[-2], 4) if len(c) > 1 and c[-2] else None
        cyc = sorted(sum(1 for x in row if x) for row in M)
        out["rings"].append({"key": [list(sizes), list(flat)], "neighbours per knot": cyc, "double shares": sum(1 for i in range(n) for x in M[i][i + 1:] if x > 1),
                             "spare j": j, "predicted rate": predicted_rate(n, j), "measured ratio (last round)": meas,
                             "rounds": len(c), "formula": check_formula(c, n, j)})
        print(sizes, flat, j, predicted_rate(n, j), meas, out["rings"][-1]["formula"], file=sys.stderr, flush=True)
    others = {}
    for sizes in ([5, 4, 4, 4], [5, 4, 4, 4, 4, 4], [5, 4, 4, 4, 4, 4, 4], [5, 4, 4, 4, 4, 4, 4, 4]):
        s, M = ring(sizes)
        G = grown(s, M, maxj=30000, rounds=60)
        c = G.counts()[1:-1]
        n = len(sizes)
        rec = None
        if n == 7:
            rec = all(c[t] == c[t - 7] + c[t - 8] for t in range(len(c) - 16, len(c)))
        if n == 8:
            g = [x - 4 for x in c]
            rec = all(g[t] == g[t - 4] + g[t - 5] for t in range(len(g) - 10, len(g)))
        d2 = [c[i + 2] - 2 * c[i + 1] + c[i] for i in range(len(c) - 2)][-6:]
        others[f"ring of {n}"] = {"per-round counts (last 10)": c[-10:], "rounds": len(c), "stated recurrence holds on the tail": rec,
                                  "second differences (last 6)": d2}
    out["rings of other lengths, one five-place knot"] = others
    return out


if __name__ == "__main__":
    part = sys.argv[1]
    print(json.dumps({"model": part_model, "formula": part_formula}[part](), indent=1, default=str))
