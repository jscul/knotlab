#!/usr/bin/env python3
"""Referee PARITY-SURVIVE-R1, the fixing split on the sampled survivors (result_scale.jsonl), from every base count: each survivor is
read at each of its n translates along the first copy shift, from count 0 (the same as reading it from every base count), with
PARITY-MIX-R1's tiers (ref_parity_enum.analyse_light: L = parity's linear algebra, B2 = parity with the harmony's states, BN = the
stitches alone, the whole) and its arc consistency on classes over every count-0 class tuple (ref_gac.py, no cap).

    python3 -B ref_survive_tiers.py      (writes result_survive_tiers.json)"""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research" / "PARITY-MIX-20261112-001" / "referee-R1"))
import ref_parity as RP  # noqa: E402
import ref_parity_enum as E  # noqa: E402
import ref_gac as G  # noqa: E402
import ref_survive as SV  # noqa: E402


def main():
    hs = {i: h for i, name, h in SV.eight()}
    tot = Counter()
    for line in (HERE / "result_scale.jsonl").read_text().splitlines():
        res = json.loads(line)
        n = res["n"]
        st = RP.setup(hs[res["i"]])
        func = RP.census(st)["functional slots"]
        rels = G.class_relations(st)
        C = len(st["reps"])
        for x in res["rows"]:
            if not x["state"] or not (0 < x["k"] < n * n):
                continue
            tot["survivors"] += 1
            for dr in range(n):
                K = frozenset(((c // n + dr) % n) * n + c % n for c in x["cells"])
                row = E.analyse_light(st, n, K, func)
                T = row["fixed"] - row["flip-frozen"]
                f = row["fixed but unreached"]
                src = Counter(row.get("sources", []))
                tot["pairs fixed, not flip-frozen"] += T
                tot["L"] += (T - f) + src["B1 parity algebra"]
                tot["P not L"] += src["B2 parity and states"]
                tot["stitches"] += src["BN stitches alone"] + src["only the whole"]
                if f:
                    frozen, fixed = E.fixing_light(st, n, E.light_variant(st, n, K, "whole"))
                    reach = RP.propagation(n, n, K, func)
                    fbu = [r for r in range(n - 1) if fixed[r] and not frozen[r] and not reach[r]]
                    tuples, capped = G.count0_tuples(st, n, K)
                    tot["count-0 enumeration capped"] += capped
                    reached = [all(z) for z in zip(*(G.gac(n, K, rels, C, t) for t in tuples))]
                    tot["beyond GAC"] += sum(1 for r in fbu if not reached[r])
    T = tot["pairs fixed, not flip-frozen"]
    out = dict(tot)
    out["shares"] = {k: round(tot[k] / T, 3) for k in ("L", "P not L", "stitches", "beyond GAC")} if T else None
    (HERE / "result_survive_tiers.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
