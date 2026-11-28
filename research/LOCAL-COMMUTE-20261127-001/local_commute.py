"""local_commute.py: commutation fixed at birth (LOCAL-COMMUTE-20261127-001; README.md, frozen predictions G, P1-P5).

Each distinction carries a binary observable; a choice says which pairs fail to commute. A pair is decided at the end of
the round in which the later of its two distinctions is born and is never revised. The birth rule may make a pair fail
to commute only if no knot ever holds both and one of the two is already held twice when the pair is decided; so pairs
born in the same round and both loose at birth always commute. A knot's check is the product of its distinctions'
observables; a structure keeps a state when every two checks commute: for each pair of knots, the number of failing
pairs (a in one, b in the other) is even. The closing sign of a closed pattern is the parity of failing pairs whose two
occurrences interleave when the knots are listed in index order (each knot's distinctions sorted).

    local_commute.py [--rounds R] [--cap K] [--limit N] [--sample-runs M]
Writes results.jsonl (one row per census start), summary.json and gates.json next to this file.
"""
import argparse
import itertools
import json
import random
import resource
import sys
import time
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "research" / "FORBID-EDITS-20261126-001"))
import forbid  # the archived ordinary engine (forbid.grown wraps rival_growth.grow)

CENSUS = ROOT / "artifacts/FOUR-READINGS-20261120-001A/FOUR-READINGS-20261120-001A-E001_signed_rules/census.json"
RING3 = ((0, 1, 2), (1, 3, 4), (3, 0, 5))


# ---------------------------------------------------------------- GF(2) linear algebra on integer bit masks

def reduce_rows(rows):
    """Echelon basis {leading bit: row} of the span of rows."""
    piv = {}
    for r in rows:
        while r:
            h = r.bit_length() - 1
            if h in piv:
                r ^= piv[h]
            else:
                piv[h] = r
                break
    return piv


def in_span(piv, v):
    while v:
        h = v.bit_length() - 1
        if h not in piv:
            return False
        v ^= piv[h]
    return True


def solve(rows, rhs, nvars, rng):
    """A uniformly random solution x (bit mask over nvars) of rows[i].x = rhs[i], or None if there is none."""
    aug = [(r, b) for r, b in zip(rows, rhs)]
    piv = {}
    for r, b in aug:
        while r:
            h = r.bit_length() - 1
            if h in piv:
                pr, pb = piv[h]
                r ^= pr
                b ^= pb
            else:
                piv[h] = (r, b)
                break
        else:
            if b:
                return None
    free = [v for v in range(nvars) if v not in piv]
    x = 0
    for v in free:
        if rng.random() < 0.5:
            x |= 1 << v
    for h in sorted(piv):                      # ascending leading bit: lower bits already fixed
        r, b = piv[h]
        rest = r & ~(1 << h)
        val = b ^ (bin(rest & x).count("1") & 1)
        if val:
            x |= 1 << h
    return x


# ---------------------------------------------------------------- growth and bookkeeping

def grow(start, rounds, cap):
    stages = [tuple(tuple(k) for k in start)]
    births = []
    end = None
    for _ in range(rounds):
        new, status, bs = forbid.grown(stages[-1], "parity", "ordinary")
        if status != "funded":
            end = "closed" if status == "closed" else "stalled"
            break
        stages.append(tuple(tuple(k) for k in new))
        births.append(bs)
        if len(stages[-1]) > cap:
            end = "cut"
            break
    if end is None:
        _, status, _ = forbid.grown(stages[-1], "parity", "ordinary")
        end = "growing" if status == "funded" else ("closed" if status == "closed" else "stalled")
    return stages, births, end


class Structure:
    """Birth rounds of knots and distinctions, holders, and the pairs each space allows."""

    def __init__(self, stages, births):
        self.stages, self.births = stages, births
        self.knots = [tuple(sorted(k)) for k in stages[-1]]
        self.T = len(stages) - 1
        self.kround = []
        for t, st in enumerate(stages):
            self.kround += [t] * (len(st) - len(self.kround))
        self.D = 1 + max(d for k in self.knots for d in k)
        start_h = {}
        for k in stages[0]:
            for d in k:
                start_h[d] = start_h.get(d, 0) + 1
        self.start_shared = {d for d, c in start_h.items() if c == 2}
        self.dround = {d: 0 for d in start_h}
        for t, bs in enumerate(births, start=1):
            for b in bs:
                for d in b["fresh"]:
                    self.dround[d] = t
        self.holders = {d: [u for u, k in enumerate(self.knots) if d in k] for d in range(self.D)}
        assert all(1 <= len(h) <= 2 for h in self.holders.values()), "each distinction held once or twice"
        self.unheld = [(a, b) for a, b in itertools.combinations(range(self.D), 2)
                       if not set(self.holders[a]) & set(self.holders[b])]
        self.local = [p for p in self.unheld if self.decidable(*p)]

    def held_twice_by(self, d, t):
        """number of holders of d at the end of round t"""
        return sum(1 for k in self.stages[t] if d in k)

    def decidable(self, a, b):
        ra, rb = self.dround[a], self.dround[b]
        if ra == rb:
            if ra > 0:
                return False                    # both fresh in the same round: loose at birth
            return a in self.start_shared or b in self.start_shared
        early, t = (a, rb) if ra < rb else (b, ra)
        assert self.held_twice_by(early, t) == 2, "the earlier distinction is held twice when the pair is decided"
        return True

    def rows(self, pairs, upto=None):
        """one row per pair of knots present by round `upto` (all if None): failing pairs between them must be even"""
        index = {p: i for i, p in enumerate(pairs)}
        present = [u for u in range(len(self.knots)) if upto is None or self.kround[u] <= upto]
        rows = {}
        for (a, b), i in index.items():
            for u in self.holders[a]:
                for v in self.holders[b]:
                    if u == v or (upto is not None and (self.kround[u] > upto or self.kround[v] > upto)):
                        continue
                    key = (min(u, v), max(u, v))
                    rows[key] = rows.get(key, 0) ^ (1 << i)
        return rows, present

    def cost(self, pairs):
        word = [d for k in self.knots for d in k]
        pos = {}
        for t, d in enumerate(word):
            pos.setdefault(d, []).append(t)
        c = 0
        for i, (a, b) in enumerate(pairs):
            if len(pos.get(a, [])) == 2 and len(pos.get(b, [])) == 2:
                x, y = pos[a]
                z, w = pos[b]
                if x < z < y < w or z < x < w < y:
                    c |= 1 << i
        return c

    def cost_in_order(self, gamma_pairs, order):
        word = [d for u in order for d in self.knots[u]]
        pos = {}
        for t, d in enumerate(word):
            pos.setdefault(d, []).append(t)
        s = 0
        for a, b in gamma_pairs:
            x, y = pos[a]
            z, w = pos[b]
            s ^= int(x < z < y < w or z < x < w < y)
        return s


def odd_attainable(st, pairs, with_dim=False):
    rows, _ = st.rows(pairs)
    piv = reduce_rows(list(rows.values()))
    odd = not in_span(piv, st.cost(pairs))
    return (odd, len(pairs) - len(piv)) if with_dim else odd


def three_parents_in_one_block(stages, births):
    """the reviewer's lemma's hypothesis: three of the closing knot's parents in one block before the closing round"""
    before = stages[-2]
    parents = set(births[-1][0]["parents"])
    if len(parents) < 3:
        return False
    G = nx.Graph()
    G.add_nodes_from(range(len(before)))
    D = 1 + max(d for k in before for d in k)
    for d in range(D):
        h = [u for u, k in enumerate(before) if d in k]
        if len(h) == 2:
            G.add_edge(*h)
    return any(len(parents & set(b)) >= 3 for b in nx.biconnected_components(G))


def outerplanar(knots):
    G = nx.Graph()
    G.add_nodes_from(range(len(knots)))
    D = 1 + max(d for k in knots for d in k)
    for d in range(D):
        h = [u for u, k in enumerate(knots) if d in k]
        if len(h) == 2:
            G.add_edge(*h)
    A = G.copy()
    A.add_edges_from(("apex", u) for u in range(len(knots)))
    return nx.check_planarity(A)[0]


def natural_rule(st):
    """Gamma_R: every locally decidable pair fails to commute. First round where two checks fail to commute, and the
    closing sign if the state is kept (closed patterns only)."""
    rows, _ = st.rows(st.local)
    full = (1 << len(st.local)) - 1
    first = None
    for (u, v), r in rows.items():
        if bin(r & full).count("1") % 2:
            t = max(st.kround[u], st.kround[v])
            first = t if first is None else min(first, t)
    return first


def random_local_rule(st, rng):
    """Decide round by round: at each round a uniformly random solution of that round's constraints given the earlier
    rounds' choices. Returns ('dead end', round) or ('kept', gamma as a set of failing pairs)."""
    decided = {}
    def round_of(p):
        return max(st.dround[p[0]], st.dround[p[1]])
    for t in range(st.T + 1):
        new = [p for p in st.local if round_of(p) == t]
        idx = {p: i for i, p in enumerate(new)}
        cons = {}
        rhs = {}
        for p in st.local:
            if round_of(p) > t:
                continue
            a, b = p
            for u in st.holders[a]:
                for v in st.holders[b]:
                    if u == v or st.kround[u] > t or st.kround[v] > t or max(st.kround[u], st.kround[v]) != t:
                        continue
                    key = (min(u, v), max(u, v))
                    if p in idx:
                        cons[key] = cons.get(key, 0) ^ (1 << idx[p])
                    else:
                        rhs[key] = rhs.get(key, 0) ^ decided[p]
                        cons.setdefault(key, 0)
        keys = sorted(set(cons) | set(rhs))
        x = solve([cons.get(k, 0) for k in keys], [rhs.get(k, 0) for k in keys], len(new), rng)
        if x is None:
            return ("dead end", t)
        for p, i in idx.items():
            decided[p] = (x >> i) & 1
    return ("kept", {p for p, v in decided.items() if v})


# ---------------------------------------------------------------- one start

def study(start_index, supports, rounds, cap, sample_runs, rng):
    stages, births, end = grow(supports, rounds, cap)
    row = {"start": start_index, "end": end, "rounds": len(stages) - 1, "knots": len(stages[-1])}
    if end == "cut":
        row["note"] = "cut above the knot cap: not run"
        return row
    st = Structure(stages, births)
    # A1: no knot holds a locally decidable (hence possibly failing) pair
    row["A1 no knot holds a decidable pair"] = all(not set(st.holders[a]) & set(st.holders[b]) for a, b in st.local)
    row["funded rounds"] = len(births)
    row["natural rule: first round without a state"] = natural_rule(st)
    if end == "closed" and not births:
        row["closed at round 0"] = True
    elif end == "closed":
        last = births[-1]
        row["closing round"] = len(births)
        row["A3 one implied birth closes the whole"] = (len(last) == 1 and last[0]["f"] == 0
                                                        and bool(last[0]["old_inputs_already_imply_law"])
                                                        and all(len(h) == 2 for h in st.holders.values()))
        row["outerplanar"] = outerplanar(st.knots)
        row["unheld pairs"] = len(st.unheld)
        row["locally decidable pairs"] = len(st.local)
        row["whole choices attain odd"], row["whole choices: free directions"] = odd_attainable(st, st.unheld, True)
        row["birth choices attain odd"], row["birth choices: free directions"] = odd_attainable(st, st.local, True)
        row["three parents in one block"] = three_parents_in_one_block(stages, births)
        if len(births) == 1:
            row["A5 round-1 closure: birth equals whole"] = len(st.local) == len(st.unheld)
        nr = row["natural rule: first round without a state"]
        if nr is None:
            row["natural rule closing sign"] = "odd" if bin(st.cost(st.local)).count("1") % 2 else "even"
    if sample_runs:
        runs = []
        for _ in range(sample_runs):
            verdict, val = random_local_rule(st, rng)
            if verdict == "dead end":
                runs.append(["dead end", val])
            elif end == "closed" and births:
                runs.append(["kept", "odd" if st.cost_in_order(sorted(val), range(len(st.knots))) else "even"])
            else:
                runs.append(["kept", None])
        row["random local rule runs"] = runs
    return row


# ---------------------------------------------------------------- gates

def gates(rng):
    out = {}
    stages, births, end = grow(RING3, 4, 40)
    st = Structure(stages, births)
    out["ring of three closes in round 1"] = (end == "closed" and len(births) == 1)
    out["ring: birth choices attain odd"] = odd_attainable(st, st.local)
    out["ring: natural rule is the readers' matching"] = sorted(st.local) == [(0, 4), (1, 5), (2, 3)]
    out["ring: natural rule keeps a state"] = natural_rule(st) is None
    out["ring: natural rule closes odd"] = bin(st.cost(st.local)).count("1") % 2 == 1
    # the whole space on the 173 census types and on the record's four outerplanar controls
    census = json.loads(CENSUS.read_text())

    def from_ends(ends):
        n = 1 + max(v for e in ends for v in e)
        return [tuple(i for i, e in enumerate(ends) if u in e) for u in range(n)]

    def whole_odd(knots):
        S = Structure([tuple(knots)], [])
        return odd_attainable(S, S.unheld)

    odd173 = sum(whole_odd(from_ends([tuple(x) for x in t["sharing"]])) for t in census)
    out["whole space odd attainable on the census types (of 173)"] = odd173

    def ring(n, mult):
        knots = [[] for _ in range(n)]
        d = 0
        for u in range(n):
            for _ in range(mult):
                knots[u].append(d)
                knots[(u + 1) % n].append(d)
                d += 1
        return [tuple(k) for k in knots]

    controls = {"ring of three, meetings doubled": ring(3, 2), "ring of four, meetings doubled": ring(4, 2),
                "ring of five, meetings doubled": ring(5, 2), "ring of four, meetings tripled": ring(4, 3)}
    out["outerplanar controls: whole space odd attainable"] = {k: whole_odd(v) for k, v in controls.items()}
    out["outerplanar controls are outerplanar"] = {k: outerplanar(v) for k, v in controls.items()}

    S4 = Structure([tuple(controls["ring of four, meetings doubled"])], [])
    word_order = [0, 2, 1, 3]
    mut = any(S4.cost_in_order([p], word_order) for p in S4.unheld)   # some failing set is odd with no conditions
    out["mutant without conditions, ring of four doubled in order 0,2,1,3: odd"] = mut
    out["ring of four doubled: true answer (whole choices)"] = whole_odd(controls["ring of four, meetings doubled"])
    # the three-label closure: a knot meeting three others once each, each of them with two loose distinctions
    star = ((0, 1, 2), (0, 3, 4), (1, 5, 6), (2, 7, 8))
    stages, births, end = grow(star, 4, 40)
    S8 = Structure(stages, births)
    out["three-label closure: closes at round 2 on 8 knots"] = (end == "closed" and len(births) == 2 and len(S8.knots) == 8)
    out["three-label closure: birth choices attain odd"] = odd_attainable(S8, S8.local)
    out["three-label closure: whole choices attain odd"] = odd_attainable(S8, S8.unheld)
    out["three-label closure: natural rule first round without a state"] = natural_rule(S8)
    return out


def order_check(st, rng, trials):
    """random elements of each space: the closing sign is the same under random orders of the knots"""
    agree = 0
    total = 0
    for pairs in (st.local, st.unheld):
        rows, _ = st.rows(pairs)
        keys = sorted(rows)
        for _ in range(trials):
            x = solve([rows[k] for k in keys], [0] * len(keys), len(pairs), rng)
            gamma = [p for i, p in enumerate(pairs) if (x >> i) & 1]
            signs = set()
            for _ in range(5):
                order = list(range(len(st.knots)))
                rng.shuffle(order)
                signs.add(st.cost_in_order(gamma, order))
            total += 1
            agree += len(signs) == 1
    return agree, total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=4)
    ap.add_argument("--cap", type=int, default=40)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--sample-runs", type=int, default=5)
    ap.add_argument("--sample-size", type=int, default=500)
    ap.add_argument("--past", type=int, default=200)
    ap.add_argument("--out", default=str(HERE))
    args = ap.parse_args()
    out = Path(args.out)
    rng = random.Random(20261127)
    t0 = time.time()
    g = gates(random.Random(20261127))
    starts = forbid.starts()
    idx = list(range(len(starts)))[: args.limit]
    sample = set(random.Random(20261127).sample(idx, min(args.sample_size, len(idx))))
    rows = []
    with (out / "results.jsonl").open("w") as fh:
        for i in idx:
            r = study(i, forbid.supports_of(starts[i]), args.rounds, args.cap,
                      args.sample_runs if i in sample else 0, rng)
            rows.append(r)
            fh.write(json.dumps(r) + "\n")
    # order-independence on 200 random elements of the two spaces (closed patterns, seeded)
    ocheck = [0, 0]
    closed = [r for r in rows if r["end"] == "closed"]
    closed = [r for r in closed if r["rounds"] >= 1]
    picks = random.Random(20261127).sample(closed, min(10, len(closed)))
    for r in picks:
        stages, births, _ = grow(forbid.supports_of(starts[r["start"]]), args.rounds, args.cap)
        a, b = order_check(Structure(stages, births), rng, 5)
        ocheck[0] += a
        ocheck[1] += b
    g["order check: same closing sign under 5 orders (agree, total)"] = ocheck
    # one size past: round rounds+1 on starts still growing at the last round
    growing = [r["start"] for r in rows if r["end"] == "growing"]
    past = random.Random(20261127).sample(growing, min(args.past, len(growing)))
    past_rows = [study(i, forbid.supports_of(starts[i]), args.rounds + 1, args.cap, 0, rng) for i in past]
    with (out / "past.jsonl").open("w") as fh:
        for r in past_rows:
            fh.write(json.dumps(r) + "\n")
    (out / "gates.json").write_text(json.dumps(g, indent=1) + "\n")
    summary = summarise(rows, past_rows)
    summary["seconds"] = round(time.time() - t0, 1)
    summary["peak KiB"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    (out / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps({"gates": g, "summary": summary}, indent=1))


def summarise(rows, past_rows):
    s = {"starts": len(rows)}
    for e in ("closed", "stalled", "growing", "cut"):
        s["end " + e] = sum(r["end"] == e for r in rows)
    funded = [r for r in rows if r.get("funded rounds", 0) >= 1]
    s["starts with a funded round"] = len(funded)
    s["natural rule loses its state (of starts with a funded round)"] = sum(
        r["natural rule: first round without a state"] is not None for r in funded)
    s["A1 holds on every structure"] = all(r.get("A1 no knot holds a decidable pair", True) for r in rows)
    closed = [r for r in rows if r["end"] == "closed"]
    s["closed at round 0 (no closure)"] = sum(1 for r in closed if r.get("closed at round 0"))
    closed = [r for r in closed if not r.get("closed at round 0")]
    s["closures"] = len(closed)
    s["A3 holds at every closure"] = all(r["A3 one implied birth closes the whole"] for r in closed)
    r1 = [r for r in closed if r["closing round"] == 1]
    s["A5 holds at every round-1 closure"] = all(r["A5 round-1 closure: birth equals whole"] for r in r1)
    s["P2 whole odd = not outerplanar at every closure"] = all(
        r["whole choices attain odd"] == (not r["outerplanar"]) for r in closed)
    by_round = {}
    for r in closed:
        k = str(r["closing round"])
        b = by_round.setdefault(k, {"closures": 0, "not outerplanar": 0, "whole odd": 0, "birth odd": 0,
                                    "birth odd among not outerplanar": 0, "natural rule keeps a state": 0,
                                    "natural rule closes odd": 0, "free directions lost (sum)": 0})
        b["closures"] += 1
        b["not outerplanar"] += not r["outerplanar"]
        b["whole odd"] += r["whole choices attain odd"]
        b["birth odd"] += r["birth choices attain odd"]
        b["birth odd among not outerplanar"] += (r["birth choices attain odd"] and not r["outerplanar"])
        b["free directions lost (sum)"] += r["whole choices: free directions"] - r["birth choices: free directions"]
        b["natural rule keeps a state"] += r["natural rule: first round without a state"] is None
        b["natural rule closes odd"] += r.get("natural rule closing sign") == "odd"
    s["closures by round"] = by_round
    later = [r for r in closed if r["closing round"] >= 2 and not r["outerplanar"]]
    covered = [r for r in later if r["three parents in one block"]]
    other = [r for r in later if not r["three parents in one block"]]
    s["P3 later closures with three parents in one block"] = len(covered)
    s["P3 of them, birth choices attain odd"] = sum(r["birth choices attain odd"] for r in covered)
    s["P3' other later closures not outerplanar"] = len(other)
    s["P3' of them, birth choices attain odd"] = sum(r["birth choices attain odd"] for r in other)
    s["P3' starts where birth choices lose the odd close"] = [r["start"] for r in other
                                                              if r["whole choices attain odd"] and not r["birth choices attain odd"]]
    s["later closures that are outerplanar"] = sum(1 for r in closed if r["closing round"] >= 2 and r["outerplanar"])
    runs = [x for r in rows for x in r.get("random local rule runs", [])]
    s["P5 random local rule runs"] = len(runs)
    s["P5 dead ends"] = sum(x[0] == "dead end" for x in runs)
    s["P5 closing signs at closures (odd, even)"] = [sum(x[1] == "odd" for x in runs), sum(x[1] == "even" for x in runs)]
    s["past: starts"] = len(past_rows)
    s["past: natural rule loses its state"] = sum(r.get("natural rule: first round without a state") is not None
                                                 for r in past_rows if r["end"] != "cut")
    pc = [r for r in past_rows if r["end"] == "closed" and not r.get("closed at round 0")]
    s["past: closures"] = len(pc)
    s["past: closures not outerplanar, birth odd"] = [sum(not r["outerplanar"] for r in pc),
                                                      sum(r["birth choices attain odd"] and not r["outerplanar"] for r in pc)]
    s["past: A1, A3, P2 hold"] = (all(r.get("A1 no knot holds a decidable pair", True) for r in past_rows)
                                  and all(r["A3 one implied birth closes the whole"] for r in pc)
                                  and all(r["whole choices attain odd"] == (not r["outerplanar"]) for r in pc))
    return s


if __name__ == "__main__":
    main()
