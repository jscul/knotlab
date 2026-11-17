"""Referee R1 for TWO-ENDS-20261117-001 (own code; the study's composite.py is not imported, its outputs only compared).

  ../../../.venv/bin/python -B referee_two_ends.py > referee_two_ends.json      (from this directory)

1. The two certified bonds of 7 at depth 12 (CARRIER's threshold_deep_8db5da810c00-79_N12_c7.json): each is a bond of P_12 by
   direct SAT (constrained, every subset one smaller free), for -79 and for -73, which is the same pattern.
2. The product test on the census, counted by distinct pattern (identical clause sets at N = 9): composite.json's verdicts against
   forgetting, per description and per distinct pattern, and whether any group of identical patterns has mixed verdicts.
3. The carried mode, by SAT at depth 11 for 8db5da810c00-73: for each orbit O at level 4 and each orbit O' 4 to 7 levels below it
   inside its subtree, whether the joint of O and O' is a product, and, when it is not, which pairs are missing.
"""
import gzip
import itertools
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/CARRIER-20261117-001/referee-R1"))  # noqa
sys.path.insert(0, str(ROOT / "experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex"))
import referee_carrier as C  # noqa: E402  (the referee's own SAT tools, CARRIER-R1)
from pattern import pattern  # noqa: E402


def part1():
    cert = json.load(open(ROOT / "research/CARRIER-20261117-001/threshold_deep_8db5da810c00-79_N12_c7.json"))
    out = []
    for idx in ("8db5da810c00-79", "8db5da810c00-73"):
        P = C.Pattern(idx, 12)
        for cell in cert["cells"]:
            b = cell["bond"]
            levels = [next(n for n in range(13) if (1 << n) - 1 <= v < (1 << (n + 1)) - 1) for v in b]
            out.append({"pattern": idx, "s": cell["s"], "bond": b, "levels": levels, "bond_of_P12": P.is_bond(b)})
    return out


def part2():
    comp = json.load(open(ROOT / "research/TWO-ENDS-20261117-001/composite.json"))
    census = {k[7:]: v for k, v in comp.items() if k.startswith("census:")}
    keys = {}
    for line in gzip.open(ROOT / "artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz", "rt"):
        r = json.loads(line)
        if r["case"][:12] in census:
            keys[r["case"][:12]] = r["key"]
    g = defaultdict(list)
    for k, key in keys.items():
        g[frozenset(tuple(sorted(t)) for t in pattern(key, 9).tolist())].append(k)
    passes = lambda k: census[k]["l0"] is not None
    forget = lambda k: census[k]["r_forget"] is not None
    return {"census_descriptions": len(keys), "distinct_patterns": len(g),
            "product_test_holds": {"descriptions": sum(map(passes, keys)), "distinct": sum(passes(v[0]) for v in g.values())},
            "forgetting": {"descriptions": sum(map(forget, keys)), "distinct": sum(forget(v[0]) for v in g.values())},
            "test_equals_forgetting_on_every_description": all(passes(k) == forget(k) for k in keys),
            "groups_with_mixed_verdicts": sum(len({passes(k) for k in v}) > 1 for v in g.values())}


def part3(idx="8db5da810c00-73", N=11, j=4, distances=(4, 5, 6, 7)):
    """Every orbit O' d levels below an orbit O at level 4, inside its subtree: is the joint a product?  For the non-products, which
    pairs are missing: those with an all-equal end (O or O' all 0 or all 1), and the others, listed by O's and O''s assignment."""
    P = C.Pattern(idx, N)
    out = {"pattern": idx, "N": N, "rows": []}
    eq = lambda x, n: x in (0, (1 << n) - 1)
    for O in P.orb[j]:
        for d in distances:
            lv = j + d
            sub = {(u << d) | t for u in O for t in range(1 << d)}
            prod = 0
            for O2 in P.orb[lv]:
                if not set(O2) <= sub:
                    continue
                vars_ = [C.vid(j, u) for u in O] + [C.vid(lv, v) for v in O2]
                proj = {int(r) for r in P.project(vars_)}
                m, m2 = len(O), len(O2)
                A = sorted({r & ((1 << m) - 1) for r in proj})
                B = sorted({r >> m for r in proj})
                missing = [(a, b) for a in A for b in B if a | (b << m) not in proj]
                if not missing:
                    prod += 1
                    continue
                other = [(a, b) for a, b in missing if not eq(a, m) and not eq(b, m2)]
                out["rows"].append({"O": O, "O2": O2, "distance": d, "missing_pairs": len(missing),
                                    "partners_of_all_equal_O": {format(a, f"0{m}b"): [format(b, f"0{m2}b") for b in B
                                                                                        if a | (b << m) in proj] for a in (0, (1 << m) - 1)},
                                    "missing_without_an_all_equal_end": len(other),
                                    "their_O2_values": sorted({format(b, f"0{m2}b") for _, b in other}),
                                    "their_O_values": sorted({format(a, f"0{m}b") for a, _ in other})})
            out.setdefault("products", {})[f"{O}, d={d}"] = prod
    return out


def main():
    out = {"1_certified_bonds_of_7": part1(), "2_product_test_by_distinct_pattern": part2(), "3_carried_mode": part3()}
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
