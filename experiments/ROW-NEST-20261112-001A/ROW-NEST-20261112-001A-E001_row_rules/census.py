"""ROW-NEST-20261112-001A: rows that grow by one at each depth, the smallest escape from bounded ends.

A definition's ends are a row of k distinctions; its body makes a new row of k + 1 and holds itself on it. Between the rows a fixed
window-1 rule: for each new position i, the rule's knots among the relative positions old i-1, old i, old i+1, new i-1, new i (a
knot touching a missing position at a row end is left out). The first row has 3 distinctions; at depth t the bottom row (length
3 + t) is closed by a knot on every three consecutive distinctions, as a self-holding knot is closed by a knot at depth 1.
Rules: the 1,024 subsets of the 10 possible relative knots. Weight: 2^-(gamma(#knots + 1) + log2 C(10, #knots)) bits.
Readings for t = 1..40: alive(t); the top relation T_t (states of the first row extendable, as a set of complement classes).
Classification of each sequence: constant; eventually periodic (smallest period p <= 10 holding from some depth a <= 20 to 40);
else unexplained within 40 (a candidate counter).
Run from the repository root:  census.py --run WORKER WORKERS  |  census.py --summary
"""
import itertools, json, math, os, sys
from collections import Counter
from pysat.solvers import Solver

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("RN_OUT") or os.path.join(HERE, "../../../artifacts/ROW-NEST-20261112-001A/ROW-NEST-20261112-001A-E001_row_rules")
POS = [("o", -1), ("o", 0), ("o", 1), ("n", -1), ("n", 0)]
TRIPLES = list(itertools.combinations(range(5), 3))
K0, TMAX, PMAX, AMAX = 3, 40, 10, 20


def weight_bits(m):
    g = 2 * int(math.floor(math.log2(m + 1))) + 1
    return g + math.log2(math.comb(10, m))


def triangle(rule, t):
    rows, nv = [], 0
    for r in range(t + 1):
        rows.append(list(range(nv, nv + K0 + r)))
        nv += K0 + r
    knots = set()
    for r in range(1, t + 1):
        old, new = rows[r - 1], rows[r]
        for i in range(len(new)):
            for tr in rule:
                vs = []
                for j in tr:
                    side, off = POS[j]
                    row = old if side == "o" else new
                    p = i + off
                    vs.append(row[p] if 0 <= p < len(row) else None)
                if None not in vs:
                    knots.add(tuple(sorted(vs)))
    bottom = rows[-1]
    for i in range(len(bottom) - 2):
        knots.add((bottom[i], bottom[i + 1], bottom[i + 2]))
    return rows, sorted(knots)


def read(rule):
    alive, top = [], []
    for t in range(1, TMAX + 1):
        rows, knots = triangle(rule, t)
        with Solver(name="cadical153", bootstrap_with=[c for k in knots for c in ([v + 1 for v in k], [-(v + 1) for v in k])]) as s:
            a = s.solve()
            alive.append(a)
            cls = []
            if a:
                f = rows[0]
                for bits in ((0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1)):    # complement classes of the first row
                    if s.solve(assumptions=[(v + 1) if b else -(v + 1) for v, b in zip(f, bits)]):
                        cls.append("".join(map(str, bits)))
            top.append("|".join(cls))
    return alive, top


def classify(seq):
    if all(x == seq[0] for x in seq):
        return "constant", 1, 0
    n = len(seq)
    for p in range(1, PMAX + 1):
        for a in range(AMAX):
            if all(seq[t] == seq[t + p] for t in range(a, n - p)):
                return ("eventually constant" if p == 1 else "periodic"), p, a + 1
    return "unexplained", None, None


def run(worker, workers):
    os.makedirs(OUT, exist_ok=True)
    f = open(os.path.join(OUT, f"runs_{worker}.jsonl"), "w")
    for mask in range(1024):
        if mask % workers != worker:
            continue
        rule = [TRIPLES[j] for j in range(10) if (mask >> j) & 1]
        alive, top = read(rule)
        ca, cb = classify(alive), classify(top)
        f.write(json.dumps(dict(mask=mask, knots=len(rule), bits=round(weight_bits(len(rule)), 4), alive=alive, top=top,
                                alive_class=ca, top_class=cb)) + "\n")
        f.flush()
    f.close()


def summarize():
    import glob
    rows = [json.loads(x) for n in sorted(glob.glob(os.path.join(OUT, "runs_*.jsonl"))) for x in open(n)]
    S = dict(rules=len(rows))
    W = lambda r: 2 ** -r["bits"]
    tot = sum(W(r) for r in rows if r["knots"] >= 1)
    for key in ("alive_class", "top_class"):
        c = Counter(r[key][0] for r in rows)
        S[key] = dict(c)
        S[key + "_weight_given_knots"] = {k: round(sum(W(r) for r in rows if r["knots"] >= 1 and r[key][0] == k) / tot, 4) for k in c}
        S[key + "_periods"] = dict(Counter(r[key][1] for r in rows if r[key][0] == "periodic"))
    S["Q2_unexplained"] = [r["mask"] for r in rows if "unexplained" in (r["alive_class"][0], r["top_class"][0])]
    S["harmonies"] = sorted([(r["knots"], r["mask"], r["alive_class"][1]) for r in rows if r["alive_class"][0] == "periodic"])[:12]
    S["dead_at_40_weight_given_knots"] = round(sum(W(r) for r in rows if r["knots"] >= 1 and not r["alive"][-1]) / tot, 4)
    S["by_knots"] = {m: dict(n=sum(r["knots"] == m for r in rows), periodic_alive=sum(r["knots"] == m and r["alive_class"][0] == "periodic" for r in rows),
                             dead40=sum(r["knots"] == m and not r["alive"][-1] for r in rows)) for m in range(11)}
    S["last_change"] = dict(Counter(max([t for t in range(1, len(r["top"])) if r["top"][t] != r["top"][t - 1]] + [0]) for r in rows))
    return S


if __name__ == "__main__":
    if sys.argv[1] == "--run":
        run(int(sys.argv[2]), int(sys.argv[3]))
    elif sys.argv[1] == "--summary":
        S = summarize()
        json.dump(S, open(os.path.join(OUT, "summary.json"), "w"), indent=1)
        print(json.dumps(S, indent=1))
