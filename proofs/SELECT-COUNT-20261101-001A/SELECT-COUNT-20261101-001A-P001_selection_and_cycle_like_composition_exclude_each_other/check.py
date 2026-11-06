#!/usr/bin/env python3
"""Checks for SELECT-COUNT-20261101-001A: selection and cycle-like composition exclude each other.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (networkx)."""
import hashlib
import itertools
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/FOUR-PREFER-20261101-001A/FOUR-PREFER-20261101-001A-P001_every_four_place_knot"))
import prefer_lib as PL  # noqa: E402

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
status = {p: json.loads((ROOT / p).read_text()).get("status") for p in manifest["parent_bindings"] if p.endswith(".json")}
check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
      {"mismatched": bad, "statuses": status})


# ------------------------------------------------------------------------------------------------ relations, knots, closure
def cube(k):
    return tuple(itertools.product((0, 1), repeat=k))


def is_knot(R, k):
    """K1-K3 on k places: non-empty, constrained, every (k-1)-place projection full"""
    if not R or len(R) == 2 ** k:
        return False
    return all(len({s[:j] + s[j + 1:] for s in R}) == 2 ** (k - 1) for j in range(k))


def closed_under(R, op):
    return all(tuple(op(*col) for col in zip(*t)) in R for t in itertools.product(R, repeat=3))


def minority(a, b, c):
    return a ^ b ^ c


def majority(a, b, c):
    return (a & b) | (a & c) | (b & c)


def affine(R):
    return closed_under(R, minority)


def bijunctive(R):
    return closed_under(R, majority)


def complement_closed(R):
    return all(tuple(1 - x for x in s) in R for s in R)


def forcing(R, k):
    """(place, value) pairs where that value allows every state"""
    return [(j, v) for j in range(k) for v in (0, 1) if all(s in R for s in cube(k) if s[j] == v)]


def identify(R, i, j, opposite=False):
    """the three-place relation R with places i and j identified (place j dropped); with opposite=True, place j reads the
    identified variable with the opposite sign (a signed incidence)"""
    return frozenset(s[:j] + s[j + 1:] for s in R if (s[i] != s[j]) == opposite)


def forcing_knot(R):
    """a knot with a forcing place obtained from R: R itself, or R with two places identified (same sign first, then opposite)"""
    f = forcing(R, 4)
    if f:
        return {"construction": "the relation itself", "knot": R, "places": 4, "forcing": f[0], "signs needed": False}
    for opposite in (False, True):
        for i, j in itertools.combinations(range(4), 2):
            K = identify(R, i, j, opposite)
            if is_knot(K, 3) and forcing(K, 3):
                how = "places %d and %d identified%s" % (i, j, " with opposite signs" if opposite else "")
                return {"construction": how, "knot": K, "places": 3, "forcing": forcing(K, 3)[0], "signs needed": opposite}
    return None


def hub_check(K, k, place):
    """two copies of the knot K sharing only `place`: are both copies circuits of the system, and is their union minus the shared
    place unconstrained (circuit elimination fails)?  Brute force over the 2k - 1 variables; ranges are all full here."""
    n = 2 * k - 1
    other = [j for j in range(k) if j != place]
    v1 = list(range(k))                                    # copy 1 uses variables 0..k-1
    v2 = [None] * k                                        # copy 2 shares variable `place`, fresh variables otherwise
    v2[place] = place
    fresh = iter(range(k, n))
    for j in other:
        v2[j] = next(fresh)
    S = [t for t in cube(n) if tuple(t[x] for x in v1) in K and tuple(t[x] for x in v2) in K]

    def constrained(Y):
        return len({tuple(t[y] for y in Y) for t in S}) < 2 ** len(Y)

    ranges_full = all(not constrained([x]) for x in range(n))
    circuits = all(constrained(C) and all(not constrained([y for y in C if y != d]) for d in C) for C in (v1, v2))
    union_minus = sorted((set(v1) | set(v2)) - {place})
    return {"ranges full": ranges_full, "both copies are circuits": circuits,
            "union minus the shared place unconstrained (hub)": not constrained(union_minus)}


CL = PL.classes()
WEAK = range(13, 18)

# ------------------------------------------------------------------------------------------------ 1. the weak classes
info1, ok1 = {}, True
for c in WEAK:
    canon, members = CL[c]
    excluded = sorted("".join(map(str, s)) for s in cube(4) if s not in canon)
    props = {"relations": len(members), "states": len(canon), "excluded states (canonical)": excluded,
             "affine (members)": sum(affine(R) for R in members), "bijunctive (members)": sum(bijunctive(R) for R in members),
             "complement-closed (members)": sum(complement_closed(R) for R in members),
             "knots (members)": sum(is_knot(R, 4) for R in members)}
    ok1 &= props["affine (members)"] == props["bijunctive (members)"] == props["complement-closed (members)"] == 0
    ok1 &= props["knots (members)"] == len(members)
    info1["class %d" % c] = props
fp_d = json.loads((ROOT / "proofs/FOUR-PREFER-20261101-001D/FOUR-PREFER-20261101-001D-P001_mutual_selection_at_four_places/result.json")
                  .read_text())
d1 = next(v for k, v in fp_d["checks"].items() if k.startswith("1 "))["info"]
open_classes = sorted(int(k.split()[1]) for k, v in d1.items() if isinstance(v, dict) and v.get("mutually selecting") == "open")
check("1 the five weak four-place classes (13-17) are the classes FOUR-PREFER D leaves open; all 288 of their relations are knots, and "
      "none is affine, bijunctive or complement-closed", ok1 and open_classes == list(WEAK),
      {"classes left open by FOUR-PREFER D": open_classes, **info1})

# ------------------------------------------------------------------------------------------------ 2. forcing-place knots and hubs
info2, ok2 = {}, True
for c in WEAK:
    canon, members = CL[c]
    tally = {}
    for R in members:
        fk = forcing_knot(R)
        if fk is None:
            ok2 = False
            tally["no forcing knot"] = tally.get("no forcing knot", 0) + 1
            continue
        h = hub_check(fk["knot"], fk["places"], fk["forcing"][0])
        ok2 &= all(h.values())
        key = fk["construction"] if fk["places"] == 4 else ("two places identified with opposite signs" if fk["signs needed"]
                                                             else "two places identified")
        tally[key] = tally.get(key, 0) + 1
    fk = forcing_knot(canon)
    example = {"construction": fk["construction"], "places": fk["places"], "forcing (place, value)": fk["forcing"],
               "knot states": sorted("".join(map(str, s)) for s in fk["knot"]),
               "excluded": sorted("".join(map(str, s)) for s in cube(fk["places"]) if s not in fk["knot"]),
               "hub": hub_check(fk["knot"], fk["places"], fk["forcing"][0])}
    info2["class %d" % c] = {"members by construction": tally, "canonical example": example}
check("2 every relation of the five weak classes yields a knot with a forcing place (13, 16, 17 directly; 14 and 15 by identifying two "
      "places, giving three-place clauses, with opposite signs for 6 relations of class 15), and two copies sharing that place form a "
      "hub: both are circuits and their union minus the shared place is unconstrained, so circuit elimination fails", ok2, info2)

# ------------------------------------------------------------------------------------------------ 3. the general theorem's lemmas
census = {}
ok3 = True
for k in (3, 4):
    H = cube(k)
    n_knots = n_bij_knots = n_aff_knots = 0
    aff_knots_parity = True
    for m in range(1, 1 << len(H)):
        R = frozenset(s for i, s in enumerate(H) if m >> i & 1)
        if not is_knot(R, k):
            continue
        n_knots += 1
        n_bij_knots += bijunctive(R)
        if affine(R):
            n_aff_knots += 1
            aff_knots_parity &= len({sum(s) % 2 for s in R}) == 1 and len(R) == 2 ** (k - 1)
    census["%d places" % k] = {"knots": n_knots, "bijunctive knots": n_bij_knots, "affine knots": n_aff_knots,
                               "affine knots are the two parity cosets": aff_knots_parity}
    ok3 &= n_bij_knots == 0 and n_aff_knots == 2 and aff_knots_parity and n_knots == {3: 34, 4: 742}[k]
check("3 lemmas of the general statement, exhaustively at three and four places: no bijunctive relation is a knot (a bijunctive "
      "relation is determined by its two-place projections, which a knot leaves full), and the affine knots are exactly the two "
      "parity cosets, whose solution counts are 2^(n-r) or 0", ok3, census)

# ------------------------------------------------------------------------------------------------ 4. the three-place table
three = {}
ok4 = True
knots3 = [frozenset(s for i, s in enumerate(cube(3)) if m >> i & 1) for m in range(1, 256)]
knots3 = [R for R in knots3 if is_knot(R, 3)]
selecting = {"not-all-equal"}
for R in knots3:
    name = {4: "parity", 5: "Fibonacci (no-lone)", 7: "clause"}.get(len(R)) or ("not-all-equal" if complement_closed(R) else "x or (y != z)")
    row = three.setdefault(name, {"relations": 0, "affine": 0, "bijunctive": 0, "with a forcing place": 0})
    row["relations"] += 1
    row["affine"] += affine(R)
    row["bijunctive"] += bijunctive(R)
    row["with a forcing place"] += bool(forcing(R, 3))
ok4 &= len(knots3) == 34 and {n: r["relations"] for n, r in three.items()} == {"parity": 2, "Fibonacci (no-lone)": 8, "not-all-equal": 4,
                                                                    "x or (y != z)": 12, "clause": 8}
ok4 &= three["parity"]["affine"] == 2 and sum(r["affine"] for r in three.values()) == 2
ok4 &= sum(r["bijunctive"] for r in three.values()) == 0
check("4 at three places: of the 34 knots only parity is affine (composes its knots like cycles, by Theorem 2) and none is bijunctive; "
      "the knot (not-all-equal), the only law with mutual selection (PINNING C), is not affine; so at three places the selecting law "
      "and the composing law are different", ok4, {"34 knots": three, "mutual selection (PINNING C)": sorted(selecting)})

# ------------------------------------------------------------------------------------------------ 5. control: parity composes
par4 = CL[0][0]
par3 = frozenset(s for s in cube(3) if sum(s) % 2 == 0)
ctrl = {"four-place parity has no forcing place": not forcing(par4, 4),
        "identifying two places of four-place parity gives a two-place relation, not a knot":
            all(not is_knot(identify(par4, i, j), 3) for i, j in itertools.combinations(range(4), 2)),
        "two parity knots sharing a place: union minus it is constrained (elimination holds)":
            not hub_check(par3, 3, 0)["union minus the shared place unconstrained (hub)"],
        "the hub test fires on the clause x or y or z (forcing place)":
            all(hub_check(frozenset(s for s in cube(3) if any(s)), 3, 0).values())}
check("5 control: parity, the composing law, has no forcing place and its knots satisfy circuit elimination, while the test does find "
      "the three-place clause's hub", all(ctrl.values()), ctrl)

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
