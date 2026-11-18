"""Read the frozen run and score predictions Q1-Q8 of research/MEET-ORDERS-20261118-001/preregistration.md.

  ../../../.venv/bin/python -B merge.py <runner output dir>
writes artifacts/MEET-ORDERS-20261118-001B/MEET-ORDERS-20261118-001B-E001_census/results.json
"""
import itertools
import json
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "scripts"))
import melib as M
from longrun import load_results

CAT = {n: len(M.bracketings(0, n - 1)) for n in range(4, 12)}


def dual_tree(knots):
    """The knots' pair-sharing tree, unrooted, as a canonical string (centre-rooted canonical form of a tree)."""
    import networkx as nx
    H = nx.Graph()
    H.add_nodes_from(range(len(knots)))
    for i, j in itertools.combinations(range(len(knots)), 2):
        if len(set(knots[i]) & set(knots[j])) == 2:
            H.add_edge(i, j)

    def enc(v, par):
        return "(" + "".join(sorted(enc(w, v) for w in H[v] if w != par)) + ")"
    return min(enc(c, None) for c in nx.center(H))


def main(out_dir):
    recs = load_results(out_dir)
    res = {k: v for k, v in recs.items()}
    bad_status = sorted(k for k, v in res.items() if v.get("status") != "ok")
    R = {k: v["result"] for k, v in res.items() if v.get("status") == "ok"}
    out = {"cases": len(res), "not_ok": bad_status, "predictions": {}}

    # Q1: Lemma B and Theorem 1 on every presentation with n0 = 4..11.
    per_n = defaultdict(lambda: {"bracketings": 0, "ok": 0, "match": 0})
    for k, r in R.items():
        if k.startswith("M1|"):
            for b in r["bracketings"]:
                d = per_n[r["n0"]]
                d["bracketings"] += 1
                d["ok"] += b["ok"]
                d["match"] += b["match"]
    q1 = all(per_n[n]["bracketings"] == CAT[n] == per_n[n]["ok"] == per_n[n]["match"] for n in range(4, 12))
    out["predictions"]["Q1"] = {"held": q1, "per_n0": dict(per_n)}

    # Q5: fewest-knot presentations are exactly the bracketings, n0 = 5..9.
    p5 = {r["n0"]: r for k, r in R.items() if k.startswith("P5|")}
    out["predictions"]["Q5"] = {"held": all(p5.get(n, {}).get("equal_to_bracketings") for n in range(5, 10)), "per_n0": p5}

    # Census: group by bare bracketing.
    cen = defaultdict(list)
    for k, r in R.items():
        if k.startswith("C|"):
            cen[r["n0"]].append(r)

    def dist_at(r, d):
        L = r["levels"][d]
        return json.dumps([L["two"], L["lam"]], sort_keys=True)

    blind = {}
    complete = {}
    sens = {}
    for n0, rows in sorted(cen.items()):
        depth = rows[0]["depth"]
        for d in range(2, depth + 1):
            g = defaultdict(set)
            for r in rows:
                g[r["nesting"]].add(dist_at(r, d))
            vals = defaultdict(set)
            for r in rows:
                vals[dist_at(r, d)].add(r["nesting"])
            blind[f"{n0}@+{d}"] = {"bare_bracketings": len(g), "with_more_than_one_distribution": sum(len(v) > 1 for v in g.values())}
            complete[f"{n0}@+{d}"] = {"distributions": len(vals), "shared_by_several_bare": sum(len(v) > 1 for v in vals.values())}
            ds = [dist_at(r, d) for r in rows]
            ties = [(a["ordered"], b["ordered"]) for a, b in itertools.combinations(rows, 2) if dist_at(a, d) == dist_at(b, d)]
            sens[f"{n0}@+{d}"] = {"presentations_up_to_mirror": len(rows), "distinct": len(set(ds)), "tied_pairs": len(ties),
                                  "tied_examples": ties[:10]}
    out["census"] = {"blind": blind, "complete": complete, "sensitive": sens}
    out["predictions"]["Q2"] = {"held": all(blind[f"{n}@+3"]["with_more_than_one_distribution"] == 0 for n in (7, 8, 9))}
    out["predictions"]["Q3"] = {"held": all(complete[f"{n}@+3"]["shared_by_several_bare"] == 0 for n in (7, 8, 9))}
    out["predictions"]["Q4"] = {"held": all(sens[f"{n}@+4"]["tied_pairs"] == 0 for n in (7, 8)),
                                "n0 = 9 (reported, no prediction)": sens.get("9@+4")}

    # Q6: the chain is the unique presentation with the least two-order chance after the second new distinction, n0 = 5..13.
    q6 = {}
    for n0 in range(5, 14):
        vals = [(M.formula(T), M.nesting(T, 0, n0 - 1)) for T in M.bracketings(0, n0 - 1)]
        low = min(v for v, _ in vals)
        argmin = {s for v, s in vals if v == low}
        chain = M.nesting([(0, i, i + 1) for i in range(1, n0 - 1)], 0, n0 - 1)
        q6[n0] = {"min": str(low), "argmin_bare": sorted(argmin), "chain_unique": argmin == {chain},
                  "distinct_values": len({v for v, _ in vals}), "bare_bracketings": len({s for _, s in vals})}
    out["predictions"]["Q6"] = {"held": all(v["chain_unique"] for v in q6.values()), "per_n0": q6}

    # Q7 and Q8 from the labelled runs.
    xs = [r for k, r in R.items() if k.startswith("X|")]
    q7 = all(L["criterion_disagree"] == 0 for r in xs for L in r["levels"])
    out["predictions"]["Q7"] = {"held": q7, "bases_checked": sum(L["criterion_agree"] for r in xs for L in r["levels"])}
    q8 = {}
    for n0 in sorted({r["n0"] for r in xs}):
        g = defaultdict(set)
        for r in xs:
            if r["n0"] == n0:
                sig = json.dumps([[L["labelled"], L["mass"]] for L in r["levels"]], sort_keys=True)
                g[dual_tree(r["knots"])].add(sig)
        sigs = [s for v in g.values() for s in v]
        q8[n0] = {"trees": len(g), "trees_with_more_than_one_signature": sum(len(v) > 1 for v in g.values()),
                  "signatures_shared_by_several_trees": len(sigs) - len(set(sigs))}
    out["predictions"]["Q8"] = {"held": all(q8[n]["trees_with_more_than_one_signature"] == 0 and
                                            q8[n]["signatures_shared_by_several_trees"] == 0 for n in (6, 7)),
                                "per_n0": q8}

    # Read-outs (no prediction): the five-starts and the six-starts.
    reads = {}
    for r in cen.get(5, []) + cen.get(6, []):
        reads[r["ordered"]] = {"nesting": r["nesting"], "two": [L["two"] for L in r["levels"]],
                               "lam": [L["lam"] for L in r["levels"]]}
    out["read_outs"] = reads
    out["census_rows"] = {n0: [{"ordered": r["ordered"], "nesting": r["nesting"], "levels": r["levels"]} for r in rows]
                          for n0, rows in sorted(cen.items())}
    out["labelled_rows"] = [{"n0": r["n0"], "ordered": r["ordered"], "tree": dual_tree(r["knots"]), "levels": r["levels"]} for r in xs]
    dest = ROOT / "artifacts/MEET-ORDERS-20261118-001B/MEET-ORDERS-20261118-001B-E001_census"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "results.json").write_text(json.dumps(out, indent=1, sort_keys=True))
    print(json.dumps({k: v["held"] for k, v in out["predictions"].items()}, indent=1))
    print("not ok:", bad_status)


if __name__ == "__main__":
    main(sys.argv[1])
