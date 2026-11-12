"""TWO-BIT-ROWS-20261112-001A: generations that grow by one place, two distinctions per place, flat against hopping reach.

A generation (the literature's "row") is an ordered list of positions, each holding two distinctions; the next generation has one position
more. A rule is a set of knots on relative distinctions, applied at every position i of the new generation:
  flat - the two distinctions of old positions i-1, i, i+1 and of new positions i-1, i (10 relative distinctions, 120 possible knots);
  hop  - old position i, old position floor(i/2) (a far position: halving reaches non-neighbouring parts), new positions i-1, i (8, 56 knots).
A knot whose relative distinctions are missing or coincide at a position is left out there. The first generation has 2 positions; at
depth t the last generation is closed by a knot on every three consecutive distinctions (in order of position, then of its two).
Readings t = 1..40: alive(t), and the first generation's relation (which of the 8 complement classes of its 4 distinctions extend).
Classes as in ROW-NEST-20261112-001: constant, eventually constant, harmony (period 2..10 from depth a <= 20), unexplained.
Weight of a rule with m knots: 2^-(gamma(m + 1) + log2 C(R, m)), R = 120 or 56; every rule with m <= 2 is read, and rules with
m >= 3 are drawn by that weighting.
Run from the repository root:  census.py --all VARIANT WORKER WORKERS  |  census.py --sample VARIANT WORKER N  |  census.py --summary
"""
import glob, hashlib, itertools, json, math, os, random, sys
from collections import Counter
from pysat.solvers import Solver

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("TB_OUT") or os.path.join(HERE, "../../../artifacts/TWO-BIT-ROWS-20261112-001A/TWO-BIT-ROWS-20261112-001A-E001_two_bit_rules")
REL = {"flat": [("o", d, b) for d in (-1, 0, 1) for b in (0, 1)] + [("n", d, b) for d in (-1, 0) for b in (0, 1)],
       "hop": [("o", 0, b) for b in (0, 1)] + [("o", "half", b) for b in (0, 1)] + [("n", d, b) for d in (-1, 0) for b in (0, 1)]}
TRI = {v: list(itertools.combinations(range(len(r)), 3)) for v, r in REL.items()}
K0, TMAX, PMAX, AMAX, MCAP = 2, 40, 10, 20, 30


def gamma_bits(n):
    return 2 * int(math.floor(math.log2(n))) + 1


def weight_bits(variant, m):
    return gamma_bits(m + 1) + math.log2(math.comb(len(TRI[variant]), m))


def build(variant, rule, t):
    gens, nv = [], 0
    for r in range(t + 1):
        gens.append([(nv + 2 * p, nv + 2 * p + 1) for p in range(K0 + r)])
        nv += 2 * (K0 + r)
    knots = set()
    rel = REL[variant]
    for r in range(1, t + 1):
        old, new = gens[r - 1], gens[r]
        for i in range(len(new)):
            for tr in rule:
                vs = []
                for j in tr:
                    side, off, b = rel[j]
                    g = old if side == "o" else new
                    p = i // 2 if off == "half" else i + off
                    vs.append(g[p][b] if 0 <= p < len(g) else None)
                if None not in vs and len(set(vs)) == 3:
                    knots.add(tuple(sorted(vs)))
    last = [v for pl in gens[-1] for v in pl]
    for i in range(len(last) - 2):
        knots.add((last[i], last[i + 1], last[i + 2]))
    return [v for pl in gens[0] for v in pl], sorted(knots)


def read(variant, rule):
    alive, top = [], []
    for t in range(1, TMAX + 1):
        first, knots = build(variant, rule, t)
        with Solver(name="cadical153", bootstrap_with=[c for k in knots for c in ([v + 1 for v in k], [-(v + 1) for v in k])]) as s:
            a = s.solve()
            alive.append(a)
            cls = []
            if a:
                for bits in itertools.product((0, 1), repeat=3):
                    full = (0,) + bits
                    if s.solve(assumptions=[(v + 1) if x else -(v + 1) for v, x in zip(first, full)]):
                        cls.append("".join(map(str, full)))
            top.append("|".join(cls))
    return alive, top


def classify(seq):
    if all(x == seq[0] for x in seq):
        return "constant", 1, 0
    n = len(seq)
    for p in range(1, PMAX + 1):
        for a in range(AMAX):
            if all(seq[t] == seq[t + p] for t in range(a, n - p)):
                return ("eventually constant" if p == 1 else "harmony"), p, a + 1
    return "unexplained", None, None


def record(variant, rule, source):
    alive, top = read(variant, rule)
    return dict(variant=variant, source=source, rule=rule, m=len(rule), bits=round(weight_bits(variant, len(rule)), 4),
                alive=alive, top=top, alive_class=classify(alive), top_class=classify(top))


def run_all(variant, worker, workers):
    os.makedirs(OUT, exist_ok=True)
    f = open(os.path.join(OUT, f"all_{variant}_{worker}.jsonl"), "w")
    idx = -1
    for m in (1, 2):
        for rule in itertools.combinations(TRI[variant], m):
            idx += 1
            if idx % workers == worker:
                f.write(json.dumps(record(variant, list(rule), "all")) + "\n")
    f.close()


def run_sample(variant, worker, n):
    os.makedirs(OUT, exist_ok=True)
    rng = random.Random(int(hashlib.sha256(f"TB:{variant}:{worker}".encode()).hexdigest()[:16], 16))
    f = open(os.path.join(OUT, f"sample_{variant}_{worker}.jsonl"), "w")
    got = 0
    while got < n:
        z = 0                                        # m + 1 by Elias gamma (fair coins), m >= 3 kept
        while rng.random() < 0.5:
            z += 1
        m1 = 1
        for _ in range(z):
            m1 = 2 * m1 + (rng.random() < 0.5)
        m = m1 - 1
        if m < 3 or m > MCAP:
            continue
        rule = rng.sample(TRI[variant], m)
        f.write(json.dumps(record(variant, rule, "sample")) + "\n")
        f.flush()
        got += 1
    f.close()


def summarize():
    rows = [json.loads(x) for n in sorted(glob.glob(os.path.join(OUT, "*.jsonl"))) for x in open(n)]
    S = {}
    for v in ("flat", "hop"):
        R = [r for r in rows if r["variant"] == v]
        A = [r for r in R if r["source"] == "all"]
        Sm = [r for r in R if r["source"] == "sample"]
        d = dict(read_all=len(A), sampled=len(Sm))
        for key in ("alive_class", "top_class"):
            d[key + "_all"] = dict(Counter(r[key][0] for r in A))
            d[key + "_sample"] = dict(Counter(r[key][0] for r in Sm))
        hit = lambda r: "harmony" in (r["alive_class"][0], r["top_class"][0])
        cnt = lambda r: "unexplained" in (r["alive_class"][0], r["top_class"][0])
        d["fewest_knots_harmony"] = min([r["m"] for r in R if hit(r)], default=None)
        d["fewest_knots_unexplained"] = min([r["m"] for r in R if cnt(r)], default=None)
        # weight shares: m <= 2 exactly; m >= 3 from the sample, scaled by the code's mass on m >= 3 (within MCAP)
        mass = {m: 2 ** -gamma_bits(m + 1) for m in range(0, MCAP + 1)}
        tot = sum(mass.values())
        share = 0.0
        for m in (1, 2):
            Am = [r for r in A if r["m"] == m]
            if Am:
                share += mass[m] / tot * sum(hit(r) for r in Am) / len(Am)
        if Sm:
            share += sum(mass[m] for m in range(3, MCAP + 1)) / tot * sum(hit(r) for r in Sm) / len(Sm)
        d["harmony_weight_share"] = round(share, 5)
        d["harmony_periods"] = dict(Counter(r[k][1] for r in R for k in ("alive_class", "top_class") if r[k][0] == "harmony"))
        d["unexplained_rules"] = [r["rule"] for r in R if cnt(r)][:5]
        d["smallest_harmonies"] = [dict(rule=r["rule"], alive=r["alive_class"], top=r["top_class"]) for r in sorted([r for r in R if hit(r)], key=lambda r: r["m"])[:5]]
        d["last_change_top"] = dict(Counter(max([t for t in range(1, len(r["top"])) if r["top"][t] != r["top"][t - 1]] + [0]) for r in R).most_common(8))
        d["dead40_share_sample"] = round(sum(not r["alive"][-1] for r in Sm) / len(Sm), 4) if Sm else None
        S[v] = d
    return S


if __name__ == "__main__":
    if sys.argv[1] == "--all":
        run_all(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif sys.argv[1] == "--sample":
        run_sample(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif sys.argv[1] == "--summary":
        S = summarize()
        json.dump(S, open(os.path.join(OUT, "summary.json"), "w"), indent=1)
        print(json.dumps(S, indent=1))
