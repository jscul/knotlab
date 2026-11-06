#!/usr/bin/env python3
"""Checks for HUB-GLUE-20261102-001C: an opened hub can create emergence that does not compose.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy). About ten minutes."""
import collections
import hashlib
import itertools
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/HUB-GLUE-20261102-001A/HUB-GLUE-20261102-001A-P001_selection_leaves_a_hub_and_pieces_glue"))
import glue_lib as G  # noqa: E402

T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:600], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        print(json.dumps(info, default=str, indent=1))
        sys.exit(1)


# ------------------------------------------------------------------------------------------------ 0. bindings
manifest = json.loads((HERE / "manifest.json").read_text())
bad = {p: d for p, d in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != d}
status = {p: json.loads((ROOT / p).read_text()).get("status") for p in manifest["parent_bindings"]
          if p.endswith(".json") and p.startswith("proofs/")}
check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
      {"mismatched": bad, "statuses": status})

SPACES = G.census_spaces(ROOT)
NAE = {t for t in itertools.product((0, 1), repeat=3) if len(set(t)) > 1}


def two_sum_sets(S, n, P, Q, ports, bound):
    """crossing circuits, and the 2-sums predicted from the circuits through one port on each side"""
    cs = G.circuits(S, n, bound)
    interior = P - ports
    p0 = sorted(ports)[0]
    sideP = [C for C in cs if C <= P and p0 in C and not (C - {p0}) & ports]
    sideQ = {frozenset((C - ports) | {p0}) for C in cs if C <= Q | ports and len(C & ports) == 1 and C & Q}
    predicted = {frozenset((K1 - {p0}) | (K2 - {p0})) for K1 in sideP for K2 in sideQ
                 if K1 - {p0} and K2 - {p0} and (bound is None or len(K1) + len(K2) - 2 <= bound)}
    crossing = {C for C in cs if C & interior and C & Q}
    return cs, crossing, predicted


# ------------------------------------------------------------------------------------------------ 1-3. every splice at every line, every removal on the point side
t1 = collections.Counter()
t2 = collections.Counter()
t3 = collections.defaultdict(collections.Counter)
ok1 = ok2 = ok3 = True
for i1, n1, H1, s1 in SPACES:
    for i2, n2, H2, s2 in SPACES:
        if n1 + n2 - 1 > 13:
            continue
        for li in range(len(H1)):
            ls, ss, n, side, ports = G.splice(H1, s1, n1, li, H2, s2, n2, 0)
            P = {v for v in range(n) if side[v] == 0}
            Q = set(range(n)) - P
            L, Lsig = list(H1[li]), s1[li]
            for M, line in enumerate(ls):
                if not set(line) <= P:
                    continue
                Sm = G.removal(ls, ss, n, M)
                I = {tuple(t[p] ^ Lsig[j] for j, p in enumerate(L)) for t in Sm}
                # the closed point piece is H1 itself (the P points keep their labels); remove M from it and keep L
                idxM = [tuple(l) for l in H1].index(tuple(line))
                SP = G.removal(H1, s1, n1, idxM)
                I2 = {tuple(t[p] ^ Lsig[j] for j, p in enumerate(L)) for t in SP}
                t1["removals on the point side"] += 1
                ok1 &= I == I2
                closed = all(tuple(1 - v for v in x) in I for x in I) and I <= NAE
                ok2 &= closed and len(I) in (2, 4, 6)
                shared = len(set(line) & set(L))
                t2["%d patterns" % len(I)] += 1
                if len(I) == 4:
                    free = [j for j in range(3) if all(len({(x[a], x[b]) for x in I}) == 2
                                                        for a, b in itertools.combinations([q for q in range(3) if q != j], 2))]
                    ok2 &= len(free) == 1
                    t2["4 patterns: the released port lies on the removed line"] += L[free[0]] in line
                    t2["4 patterns: released port off the removed line"] += L[free[0]] not in line
                if shared == 2:
                    t2["removed line holds two ports"] += 1
                    t2["removed line holds two ports: 4 patterns"] += len(I) == 4
                bound = None if n <= 11 else 6
                cs, crossing, predicted = two_sum_sets(Sm, n, P, Q, ports, bound)
                c = t3["%d patterns" % len(I)]
                c["removals"] += 1
                c["crossing knots"] += len(crossing)
                c["outside the 2-sums"] += len(crossing - predicted)
                c["2-sum candidates that are not knots"] += len(predicted - crossing)
                c["crossing knots through a port"] += sum(1 for C in crossing if C & ports)
                if len(I) == 2:
                    ok3 &= crossing == predicted
check("1 at every removal on the point side of every splice of two census knot spaces up to 13 points (every line, one point), the "
      "port patterns that remain are exactly the patterns of the closing line that the closed point piece allows without the removed "
      "line", ok1 and t1["removals on the point side"] > 0, dict(t1))
check("2 every such interface is a complement-closed set of not-all-equal patterns of the closing line, of size 2, 4 or 6; at size 4 "
      "exactly one port is released (the other two stay tied), and it never lies on the removed line; when the removed line holds two "
      "ports the interface has size 4", ok2 and t2["4 patterns: the released port lies on the removed line"] == 0 and
      t2["removed line holds two ports"] == t2["removed line holds two ports: 4 patterns"], dict(t2))
check("3 with one pair (size 2) the crossing knots are exactly the 2-sums, as for a held hub; with two or three pairs the 2-sum fails "
      "in every way (circuits on spaces up to 11 points in full, up to 6 elements at 12 and 13)",
      ok3 and t3["4 patterns"]["outside the 2-sums"] > 0 and t3["6 patterns"]["outside the 2-sums"] > 0,
      {k: dict(v) for k, v in t3.items()})

# ------------------------------------------------------------------------------------------------ 4. emergence that no chain of eliminations produces
FANO = next((n, H, s) for idx, n, H, s in SPACES if idx == 21)
ls, ss, n, side, ports = G.splice(FANO[1], FANO[2], 7, 0, FANO[1], FANO[2], 7, 0)
P = {v for v in range(n) if side[v] == 0}
Q = set(range(n)) - P
info4 = collections.Counter()
for M, line in enumerate(ls):
    held = not set(line) <= P
    Sm = G.removal(ls, ss, n, M)
    cs = G.circuits(Sm, n)
    ties = [C for C in cs if len(C) == 2]
    knots = [C for C in cs if len(C) >= 3]
    cls = {v: frozenset([v]) for v in range(n)}
    for t in ties:
        a, b = tuple(t)
        u = cls[a] | cls[b]
        for w in u:
            cls[w] = u
    canon = lambda C: frozenset(cls[v] for v in C)
    allk = {canon(K): K for K in knots}
    gen = {canon(K) for K in knots if K <= P or K <= Q | ports}
    changed = True
    while changed:
        changed = False
        items = [allk[c] for c in gen if c in allk]
        for K1, K2 in itertools.combinations(items, 2):
            for h in K1 & K2:
                c = canon((K1 | K2) - {h})
                if c in allk and c not in gen:
                    gen.add(c)
                    changed = True
    for K in knots:
        if K & (P - ports) and K & Q:
            info4[("hub held" if held else "hub opened", "generated by eliminations" if canon(K) in gen else "not generated")] += 1
info4 = {"%s: %s" % k: v for k, v in info4.items()}
check("4 in the 13-point Fano splice (all circuits): when the hub is held every crossing knot is generated from one-sided knots by "
      "eliminations (up to ties); when it is opened some are not: new emergence at the opened hub",
      info4.get("hub held: not generated", 0) == 0 and info4.get("hub opened: not generated", 0) > 0, info4)

# ------------------------------------------------------------------------------------------------ 5. why two ports on the removed line stay tied
info5 = collections.Counter()
for idx, n, H, s in SPACES:
    for li, L in enumerate(H):
        for mi, M in enumerate(H):
            shared = sorted(set(L) & set(M))
            if mi == li or len(shared) != 2:
                continue
            a, b = shared
            odd = s[li][L.index(a)] ^ s[li][L.index(b)] ^ s[mi][M.index(a)] ^ s[mi][M.index(b)]
            rest_lines = [l for k, l in enumerate(H) if k not in (li, mi)]
            pts = [p for p in range(n) if p not in (a, b)]
            nice = any(all(p in l for p, l in zip(perm, rest_lines)) for perm in itertools.permutations(pts))
            info5["pairs of lines sharing two points"] += 1
            info5["4-cycle nice with an odd sign product"] += bool(nice and odd)
check("5 in every census knot space, every 4-cycle a-M-b-L through two lines sharing two points is nice (the rest has a perfect "
      "matching) and carries an odd number of negative signs, as sign-nonsingularity requires; so when M holds two ports a, b of the "
      "closing line L, their tie from M (equal under M's signs) makes them opposite under L's signs",
      info5["pairs of lines sharing two points"] > 0 and info5["pairs of lines sharing two points"] == info5["4-cycle nice with an odd sign product"],
      dict(info5))

OUT["seconds"] = round(time.time() - T0, 1)
print("ALL OK", OUT["seconds"], "s")
result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"], "proof": manifest["proof"],
          "status": "passed", "claim": manifest["claim"], "checks": {k: v for k, v in OUT.items() if k != "seconds"}}
text = json.dumps(result, indent=1, sort_keys=True, default=str) + "\n"
if "--write" in sys.argv:
    (HERE / "result.json").write_text(text)
elif not (HERE / "result.json").exists() or json.loads((HERE / "result.json").read_text()) != json.loads(text):
    print("result.json does not match a fresh run; rerun with --write after review")
    sys.exit(1)
