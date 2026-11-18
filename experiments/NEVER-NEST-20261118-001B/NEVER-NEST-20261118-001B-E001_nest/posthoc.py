"""NEVER-NEST-20261118-001B-E001: post hoc readings (labelled as such in the decision note), recomputed from the frozen traces.

1. NN and NN2: whether every lengthening after the first full grid comes at a full grid; lengthenings that come early (holes);
   runs without a full grid; the fills that keep two orders on offer right after each lengthening; the odd-set sizes of NN's fills.
2. CC after one fill of a line: a full grid exactly when no split crosses nothing after the first fill (N6), and the number of
   splits crossing nothing never falls.
Writes posthoc.json next to results.json."""
import gzip
import json
import os
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "artifacts", "NEVER-NEST-20261118-001B", "NEVER-NEST-20261118-001B-E001_nest")


def main():
    res = json.load(gzip.open(os.path.join(OUT, "results.json.gz"), "rt"))   # run.py --merge's results.json, compressed
    out = {"lengthening": {}, "cc_fill": {}}
    for rule in ("NN", "NN2"):
        agg = defaultdict(Counter)
        for r in res["R1"]["results"]:
            if r["rule"] != rule:
                continue
            tr = [x for x in r["trace"] if "stopped" not in x]
            c = agg[r["n0"]]
            c["runs"] += 1
            for a, b in zip(tr, tr[1:]):
                if a["kind"] == "sub" and "zero_two" in b:
                    c["on_offer_after_sub_" + str(min(b["zero_two"], 2))] += 1
            for x in tr:
                if "odd" in x:
                    c["odd_size_" + str(len(x["odd"]))] += 1
            ff = next((i for i, x in enumerate(tr) if x.get("full_grid")), None)
            if ff is None:
                c["no_full_grid"] += 1
                continue
            after = [(a, b) for a, b in zip(tr[ff:], tr[ff + 1:]) if b["kind"] != "fill"]
            early = sum(1 for a, b in after if not a["full_grid"])
            c["lengthenings_after_first_full"] += len(after)
            c["early_lengthenings"] += early
            c["runs_every_lengthening_at_full"] += early == 0
            c["lengthenings_before_first_full"] += sum(1 for b in tr[1:ff + 1] if b["kind"] != "fill")
        out["lengthening"][rule] = {str(k): dict(v) for k, v in sorted(agg.items())}
    for r in res["R2"]["results"]:
        if r["rule"] != "CC" or not r["start"].startswith("fill"):
            continue
        tr = r["trace"]
        c = out["cc_fill"].setdefault(r["start"], Counter())
        key = ("no split apart at the start" if tr[0]["isolated"] == 0 else "a split apart at the start") + \
              (", full grid" if any(x.get("full_grid") for x in tr[1:]) else ", no full grid")
        c[key] += 1
        c["splits apart ever fewer"] += any(x["isolated"] < tr[0]["isolated"] for x in tr[1:])
    out["cc_fill"] = {k: dict(v) for k, v in out["cc_fill"].items()}
    json.dump(out, open(os.path.join(OUT, "posthoc.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
