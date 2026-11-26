"""Independently tabulate saved rows, including scores outside the splits flag."""
import argparse
import gzip
import json
from collections import Counter
from fractions import Fraction
from itertools import islice
from pathlib import Path
from time import perf_counter

HERE = Path(__file__).resolve().parent
GROUPS = ("count", "xcount", "tables5", "xrun", "built", "shared")


def read(groups, limit):
    t = perf_counter()
    result = {}
    for group in groups:
        bins = {}
        seen = set()
        for f in sorted(HERE.parent.glob(group + "_*.jsonl.gz")):
            with gzip.open(f, "rt") as lines:
                for line in islice(lines, limit):
                    r = json.loads(line)
                    if group == "shared" and r["kind"] != "shared birth, read":
                        continue
                    k = (r["kind of edit"], r["law"], r["arm"])
                    if k not in bins:
                        bins[k] = (Counter(), {}, {})
                    c, best, witness = bins[k]
                    c[r["kind"]] += 1
                    if r["kind"] not in ("read","shared birth, read"):
                        continue
                    seen.add(r["start"])
                    c["splits"] += r["splits"]
                    c["two-sided same setting"] += r["two-sided forbidding"]
                    c["loss"] += r["forbids somewhere"]
                    dep = r.get("forbidding changes with own setting")
                    if dep is not None:
                        c["changes any"] += any(dep)
                        c["changes all"] += all(dep)
                    for w in ("U","S"):
                        if w not in r:
                            continue
                        lab = "split" if r["splits"] else "other"
                        scores = {a: Fraction(v) for a,v in r[w]["scores"].items()}
                        c[w + " rows"] += 1
                        c[w + " record changed"] += not r[w]["record unchanged"]
                        c[w + " split and record changed"] += r["splits"] and not r[w]["record unchanged"]
                        c[w + " single changed"] += not r[w]["single unchanged"]
                        c[w + " excess"] += max(scores.values()) > (Fraction(3,4) if k[0] == "M1" else 2)
                        for tag,score in scores.items():
                            label = " ".join((w,lab,tag))
                            if score > best.get(label, -1):
                                best[label] = score
                                witness[label] = [r["start"], r["readers"]]
                        for ll in r[w].get("correlations",{}).values():
                            mag = max(abs(Fraction(v)) for v in ll)
                            best[w+" abs correlation"] = max(mag,best.get(w+" abs correlation", 0))
        result[group] = {"starts with read rows":len(seen), "counts":{
            " ".join(k): {"counts":c, "max":{key:str(v) for key,v in best.items()}, "attained":wit}
            for k,(c,best,wit) in sorted(bins.items())}}
    result["seconds"] = round(perf_counter()-t,3)
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("groups", choices=GROUPS, nargs="+")
    p.add_argument("--pilot", type=int, help="prefix of each input file")
    p.add_argument("--save", type=Path)
    args = p.parse_args()
    out = read(args.groups, args.pilot)
    if args.save:
        (HERE/args.save).write_text(json.dumps(out, indent=1)+"\n")
    print("seconds",out["seconds"],"groups",args.groups)
