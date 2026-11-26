"""Uniform-within-stratum sample of placements with a birth belonging to multiple readers."""
import argparse
from collections import Counter
from itertools import chain
import json
from pathlib import Path
from random import Random
from time import perf_counter
from literal import archive_rows, check

HERE = Path(__file__).resolve().parent
SEED = 2026112605


def sample():
    rng = Random(SEED)
    chosen, sizes = {}, Counter()
    for f in sorted(HERE.parent.glob("shared_*.jsonl.gz")):
        for ln,r in archive_rows(f):
            if r["kind"] != "shared birth, read":
                continue
            k = (r["kind of edit"],r["law"],r["arm"],r["splits"],r["U"]["record unchanged"],r["on every side"])
            sizes[k] += 1
            if rng.randrange(sizes[k]) == 0:
                chosen[k] = (f.name,ln,r)
    return [(k,sizes[k],*chosen[k]) for k in sorted(chosen)]


def main(pilot,save):
    rows = sample()
    if pilot:
        rows = [next(x for x in rows if x[0][:2] == (edit,law))
                for edit in ("E1","M1") for law in ("nae","parity")]
    out = []
    for k,size,name,line,r in rows:
        z = check(r,shared=True)
        weights = z["checks"]["weightings"]
        assert not z["differences"], (r["start"],z["differences"])
        out.append({"archive":name,"line":line,"start":r["start"],"readers":r["readers"],"stratum":k,
                    "stratum size":size,"scores":{w:r[w]["scores"] for w in weights},
                    "states":{s:[x["retained"],x["kept"],x["grown states"],x["enumeration"]]
                              for s,x in z["settings"].items()},
                    "births":{s:t["records"] for s,t in z["settings"].items()},
                    "reading tables":{w:x["readings"] for w,x in weights.items()},
                    "stored changes":{w:x["stored record changes"] for w,x in weights.items()},
                    "declared changes":{w:x["complete record changes"] for w,x in weights.items()}})
    if save:
        (HERE/save).write_text(json.dumps({"seed":SEED,"rows":out},separators=(",",":"))+"\n")
    print("cases",len(out),"settings",sum(len(r["states"]) for r in out),
          "literal settings",sum(v[-1]=="whole" for r in out for v in r["states"].values()))
    print("newly changed record flags",sum(not any(r["stored changes"][w]) and any(r["declared changes"][w])
                                           for r in out for w in ("S","U")))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--pilot",action="store_true")
    p.add_argument("--save",type=Path)
    args = p.parse_args()
    start = perf_counter()
    main(args.pilot,args.save)
    print("seconds",round(perf_counter()-start,3))
