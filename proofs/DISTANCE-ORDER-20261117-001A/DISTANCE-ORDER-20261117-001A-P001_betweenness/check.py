#!/usr/bin/env python3
"""Exhaustive checks of the statements of DISTANCE-ORDER-20261117-001A-P001 (not a proof).

S1, S2: every set of joint states of three and of four distinctions, every ordered triple.
S3(b), S3(c): every nonempty not-all-equal relation on three to six distinctions; the decoder of the
  proof rebuilds each relation from its disagreement table alone (n >= 4); the n = 3 collision.
S3(a): every relation defined by ties and opposite-pair knots on four and five distinctions: the
  table with N determines it, and the decoder rebuilds it.
S4: three-place parity on four distinctions; four-place parity on five (inside the complement-closed class).
S5: additivity along 0..3 iff every state is a threshold, on every set of states of four distinctions;
  the threshold line gives 2|i - j| for n = 3..10.
S6: on every set of states of four distinctions and every not-all-equal relation to six, every chain of
  the base-point order of m distinctions allows at most 2m patterns on them.
S7: random not-all-equal patterns with no cycle of knots (up to 14 distinctions, 300 patterns), and the
  chain of knots sharing one distinction: rate (1 - (-1/3)^s) / 2 for distinctions s steps apart.

    python3 -B check.py          check
    python3 -B check.py --write  check and write result.json
"""

import itertools
import json
import random
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent


def table(n, sts):
    return {(u, v): sum(((s >> u) ^ (s >> v)) & 1 for s in sts) for u, v in itertools.combinations(range(n), 2)}


def dd(t, u, v):
    return 0 if u == v else t[(min(u, v), max(u, v))]


def ok_state(s, constraints):
    return all(tuple((s >> u) & 1 for u in c) not in ex for c, ex in constraints)


def closure(n, masks):
    full = (1 << (1 << n)) - 1
    seen, frontier = {full}, [full]
    while frontier:
        nxt = []
        for r in frontier:
            for m in masks:
                q = r & m
                if q and q not in seen:
                    seen.add(q)
                    nxt.append(q)
        frontier = nxt
    return seen


def mask(n, c, ex):
    return sum(1 << s for s in range(1 << n) if tuple((s >> u) & 1 for u in c) not in ex)


def states_of(n, r):
    return [s for s in range(1 << n) if r >> s & 1]


NAE = {(0, 0, 0), (1, 1, 1)}
PAIRS3 = [{(0, 0, 0), (1, 1, 1)}, {(0, 0, 1), (1, 1, 0)}, {(0, 1, 0), (1, 0, 1)}, {(1, 0, 0), (0, 1, 1)}]


def check_s1_s2(n):
    bad = 0
    for r in range(1, 1 << (1 << n)):
        sts = states_of(n, r)
        N = len(sts)
        t = table(n, sts)
        for a, b, c in itertools.permutations(range(n), 3):
            between = dd(t, a, b) == dd(t, a, c) + dd(t, c, b)
            none = not any(((s >> a) & 1) == ((s >> b) & 1) != ((s >> c) & 1) for s in sts)
            if between != none:
                bad += 1
            tot = dd(t, a, b) + dd(t, b, c) + dd(t, a, c)
            nae = all(len({(s >> a) & 1, (s >> b) & 1, (s >> c) & 1}) == 2 for s in sts)
            if tot > 2 * N or (tot == 2 * N) != nae:
                bad += 1
    return bad


def decode_nae(n, t):
    """The proof's decoder: N and the knots from the table alone (n >= 4)."""
    if all(x == 1 << (n - 1) for x in t.values()):
        return (1 << (1 << n)) - 1
    sums = {c: dd(t, c[0], c[1]) + dd(t, c[1], c[2]) + dd(t, c[0], c[2]) for c in itertools.combinations(range(n), 3)}
    M = max(sums.values())
    knots = [c for c, x in sums.items() if x == M]
    return sum(1 << s for s in range(1 << n) if ok_state(s, [(c, NAE) for c in knots]))


def check_s3_nae():
    out = {}
    for n in range(3, 7):
        rels = closure(n, [mask(n, c, NAE) for c in itertools.combinations(range(n), 3)])
        tabs = {}
        wrong = 0
        for r in rels:
            t = table(n, states_of(n, r))
            tabs.setdefault(tuple(sorted(t.items())), []).append(r)
            if n >= 4 and decode_nae(n, t) != r:
                wrong += 1
        out[n] = {"relations": len(rels), "tables": len(tabs), "decoder_wrong": wrong if n >= 4 else None}
    return out


def decode_signed(n, t, N):
    cons = []
    for u, v in itertools.combinations(range(n), 2):
        if dd(t, u, v) == 0:
            cons.append(((u, v), {(0, 1), (1, 0)}))
        if dd(t, u, v) == N:
            cons.append(((u, v), {(0, 0), (1, 1)}))
    for a, b, c in itertools.combinations(range(n), 3):
        if dd(t, a, b) + dd(t, b, c) + dd(t, a, c) == 2 * N:
            cons.append(((a, b, c), PAIRS3[0]))
        if dd(t, a, b) == dd(t, a, c) + dd(t, c, b):
            cons.append(((a, b, c), PAIRS3[1]))
        if dd(t, a, c) == dd(t, a, b) + dd(t, b, c):
            cons.append(((a, b, c), PAIRS3[2]))
        if dd(t, b, c) == dd(t, b, a) + dd(t, a, c):
            cons.append(((a, b, c), PAIRS3[3]))
    return sum(1 << s for s in range(1 << n) if ok_state(s, cons))


def check_s3_signed():
    out = {}
    for n in (4, 5):
        masks = [mask(n, p, ex) for p in itertools.combinations(range(n), 2) for ex in ({(0, 1), (1, 0)}, {(0, 0), (1, 1)})]
        masks += [mask(n, c, ex) for c in itertools.combinations(range(n), 3) for ex in PAIRS3]
        rels = closure(n, masks)
        keys, wrong = set(), 0
        for r in rels:
            sts = states_of(n, r)
            t = table(n, sts)
            keys.add((len(sts), tuple(sorted(t.items()))))
            if decode_signed(n, t, len(sts)) != r:
                wrong += 1
        out[n] = {"relations": len(rels), "tables_with_N": len(keys), "decoder_wrong": wrong}
    return out


def check_s4():
    def par(n, c):
        return [s for s in range(1 << n) if sum((s >> u) & 1 for u in c) % 2 == 0]
    a, b = par(4, (0, 1, 2)), par(4, (0, 1, 3))
    c, d = par(5, (0, 1, 2, 3)), par(5, (0, 1, 2, 4))
    comp = lambda n, sts: all(((1 << n) - 1) ^ s in sts for s in sts)
    return {"three_place": len(a) == len(b) == 8 and table(4, a) == table(4, b) and set(a) != set(b)
            and set(table(4, a).values()) == {4},
            "four_place": len(c) == len(d) == 16 and table(5, c) == table(5, d) and set(c) != set(d)
            and set(table(5, c).values()) == {8} and comp(5, c) and comp(5, d)}


def check_s5():
    bad = 0
    for r in range(1, 1 << 16):
        sts = states_of(4, r)
        t = table(4, sts)
        additive = all(dd(t, i, k) == dd(t, i, j) + dd(t, j, k) for i, j, k in itertools.combinations(range(4), 3))
        mono = all(not (((s >> i) & 1) == ((s >> k) & 1) != ((s >> j) & 1))
                   for s in sts for i, j, k in itertools.combinations(range(4), 3))
        if additive != mono:
            bad += 1
    lines = True
    for n in range(3, 11):
        sts = [s for s in range(1 << n) if all(not (((s >> i) & 1) == ((s >> k) & 1) != ((s >> j) & 1))
                                               for i, j, k in itertools.combinations(range(n), 3))]
        t = table(n, sts)
        lines &= len(sts) == 2 * n and all(x == 2 * (v - u) for (u, v), x in t.items())
    return {"bad_sets_n4": bad, "lines_2_abs": lines}


def chains(n, t, o):
    D = lambda u, v: dd(t, u, v)
    others = [x for x in range(n) if x != o and D(o, x) > 0]
    out = []
    def grow(seq):
        ups = [w for w in others if w not in seq and D(o, w) > D(o, seq[-1]) and D(seq[-1], w) > 0
               and D(o, w) == D(o, seq[-1]) + D(seq[-1], w)]
        if not ups:
            out.append(seq)
        for w in ups:
            grow(seq + [w])
    grow([o])
    return out


def check_s6():
    bad = 0
    for r in range(1, 1 << 16):
        sts = states_of(4, r)
        t = table(4, sts)
        for o in range(4):
            for ch in chains(4, t, o):
                if len({tuple((s >> x) & 1 for x in ch) for s in sts}) > 2 * len(ch):
                    bad += 1
    for n in (5, 6):
        for r in closure(n, [mask(n, c, NAE) for c in itertools.combinations(range(n), 3)]):
            sts = states_of(n, r)
            t = table(n, sts)
            for o in range(n):
                for ch in chains(n, t, o):
                    if len({tuple((s >> x) & 1 for x in ch) for s in sts}) > 2 * len(ch):
                        bad += 1
    return bad


def steps_apart(n, knots):
    adj = [set() for _ in range(n)]
    for k in knots:
        for u, v in itertools.combinations(k, 2):
            adj[u].add(v)
            adj[v].add(u)
    dist = {}
    for s in range(n):
        seen = {s: 0}
        front = [s]
        while front:
            nxt = []
            for u in front:
                for w in adj[u]:
                    if w not in seen:
                        seen[w] = seen[u] + 1
                        nxt.append(w)
            front = nxt
        dist[s] = seen
    return dist


def check_s7():
    rng = random.Random(20261117)
    bad, done = 0, 0
    cases = [[(2 * i, 2 * i + 1, 2 * i + 2) for i in range(6)]]
    for _ in range(300):
        n_knots = rng.randint(1, 6)
        knots, n = [(0, 1, 2)], 3
        for _ in range(n_knots - 1):
            at = rng.randrange(n)
            knots.append((at, n, n + 1))
            n += 2
        perm = list(range(n))
        rng.shuffle(perm)
        cases.append([tuple(perm[u] for u in k) for k in knots])
    for knots in cases:
        n = 1 + max(max(k) for k in knots)
        sts = [s for s in range(1 << n) if ok_state(s, [(k, NAE) for k in knots])]
        N = len(sts)
        t = table(n, sts)
        st = steps_apart(n, knots)
        for (u, v), x in t.items():
            if Fraction(x, N) != (1 - Fraction(-1, 3) ** st[u][v]) / 2:
                bad += 1
        done += 1
    return {"patterns": done, "bad_pairs": bad}


def run():
    res = {"S1_S2_bad": {3: check_s1_s2(3), 4: check_s1_s2(4)}, "S3_nae": check_s3_nae(),
           "S3_signed": check_s3_signed(), "S4": check_s4(), "S5": check_s5(), "S6_bad": check_s6(), "S7": check_s7()}
    nae = res["S3_nae"]
    res["passed"] = (all(v == 0 for v in res["S1_S2_bad"].values())
                     and nae[3]["tables"] < nae[3]["relations"]
                     and all(nae[n]["tables"] == nae[n]["relations"] and nae[n]["decoder_wrong"] == 0 for n in (4, 5, 6))
                     and all(v["tables_with_N"] == v["relations"] and v["decoder_wrong"] == 0 for v in res["S3_signed"].values())
                     and all(res["S4"].values()) and res["S5"]["bad_sets_n4"] == 0 and res["S5"]["lines_2_abs"]
                     and res["S6_bad"] == 0 and res["S7"]["bad_pairs"] == 0)
    return res


if __name__ == "__main__":
    out = run()
    print(json.dumps(out, indent=1, default=str))
    if "--write" in sys.argv:
        manifest = json.loads((HERE / "manifest.json").read_text())
        (HERE / "result.json").write_text(json.dumps({
            "schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
            "proof": manifest["proof"], "status": "passed" if out["passed"] else "failed", "checks": out,
            "failures": [] if out["passed"] else ["a statement check failed"]}, indent=1, default=str) + "\n")
    sys.exit(0 if out["passed"] else 1)
