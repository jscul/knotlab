"""Score predictions P1-P4 of research/MEET-GROW-20261118-001/preregistration.md from the runner output.

  ../../../.venv/bin/python -B merge.py <runner output dir> [<another runner output dir> ...]
writes artifacts/MEET-GROW-20261118-001B/MEET-GROW-20261118-001B-E001_pairgraph/results.json
"""
import itertools
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from longrun import load_results


def first_uncarried(a, b):
    """The first level at which no automorphism carries a's labelled pair-graph distribution onto b's (None if carried)."""
    best = -1
    for k in range(len(a["levels"][0]["per_alpha"])):
        lv = 0
        for La, Lb in zip(a["levels"], b["levels"]):
            if La["per_alpha"][k] != Lb["per_alpha"][0]:
                break
            lv += 1
        best = max(best, lv)
    return None if best == len(a["levels"]) else a["levels"][best]["n"]


def profile_carried(a, b):
    """Levels (with a profile) at which some automorphism carries a's joint (pair graph, option profile) distribution onto b's,
    one automorphism for all those levels."""
    idx = [i for i, L in enumerate(a["levels"]) if "per_alpha_profile" in L]
    if not idx:
        return True
    K = len(a["levels"][0]["per_alpha"])
    return any(all(a["levels"][i]["per_alpha_profile"][k] == b["levels"][i]["per_alpha_profile"][0] for i in idx)
               for k in range(K))


def main(out_dirs):
    recs = {}
    for d in out_dirs:
        recs.update(load_results(d))
    bad = sorted(k for k, v in recs.items() if v["status"] != "ok")
    rows = [v["result"] for v in recs.values() if v["status"] == "ok"]
    out = {"cases": len(recs), "not_ok": bad, "per_n0": {}}
    p1 = p2 = p3 = p4 = True
    for n0 in sorted({r["n0"] for r in rows}):
        rs = [r for r in rows if r["n0"] == n0]
        g = defaultdict(list)
        for r in rs:
            g[json.dumps(r["pattern"])].append(r)
        within = []
        for H, xs in g.items():
            for a, b in itertools.combinations(xs, 2):
                f = first_uncarried(a, b)
                within.append({"a": a["ordered"], "b": b["ordered"], "first_uncarried_n": f, "profile": profile_carried(a, b)})
        counts_ok = all(len({json.dumps([L["labelled_bases"] for L in x["levels"]]) for x in xs}) == 1 for xs in g.values())
        across = []
        for H1, H2 in itertools.combinations(g, 2):
            x, y = g[H1][0], g[H2][0]
            same = [L1["n"] for L1, L2 in zip(x["levels"], y["levels"])
                    if "renaming_digest" in L1 and L1["renaming_digest"] == L2["renaming_digest"]]
            across.append({"a": x["ordered"], "b": y["ordered"], "levels_with_equal_renaming_digest": same})
        n_unc = sum(w["first_uncarried_n"] is not None for w in within)
        n_same = sum(bool(c["levels_with_equal_renaming_digest"]) for c in across)
        p1 &= n_unc == 0
        p2 &= n_same == 0
        p3 &= counts_ok
        n_prof = sum(not w["profile"] for w in within)
        p4 &= n_prof == 0
        out["per_n0"][n0] = {
            "presentations_up_to_mirror": len(rs), "meeting_patterns": len(g),
            "pattern_sizes": sorted(len(v) for v in g.values()), "pairs_within": len(within),
            "pairs_not_carried": n_unc, "pairs_profile_not_carried": n_prof, "not_carried": [w for w in within if w["first_uncarried_n"] is not None][:20],
            "pattern_pairs_with_equal_renaming_digest": n_same, "labelled_counts_follow_pattern": counts_ok,
            "per_pattern": [{"pattern": json.loads(H), "presentations": len(xs), "bare": sorted({x["bare"] for x in xs}),
                             "labelled_bases": [L["labelled_bases"] for L in xs[0]["levels"]],
                             "pair_graphs": [L["pair_graphs"] for L in xs[0]["levels"]],
                             "two_orders_distinct_by_presentation": [len({x["levels"][i]["two"] for x in xs})
                                                                     for i in range(len(xs[0]["levels"]))]}
                            for H, xs in g.items()]}
    out["predictions"] = {"P1": p1, "P2": p2, "P3": p3, "P4": p4}
    dest = ROOT / "artifacts/MEET-GROW-20261118-001B/MEET-GROW-20261118-001B-E001_pairgraph"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "results.json").write_text(json.dumps(out, indent=1, sort_keys=True))
    print(json.dumps(out["predictions"]), "not ok:", bad)
    for n0, v in out["per_n0"].items():
        print(n0, {k: v[k] for k in ("presentations_up_to_mirror", "meeting_patterns", "pairs_within", "pairs_not_carried",
                                      "pattern_pairs_with_equal_renaming_digest", "labelled_counts_follow_pattern", "pairs_profile_not_carried")})


if __name__ == "__main__":
    main(sys.argv[1:])
