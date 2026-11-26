"""Replay the far-dependent birth in one archived seven-knot addressed edit."""
import argparse
import gzip
import json
from itertools import product
from pathlib import Path
from time import perf_counter
from growth import grow


def replay(pilot):
    path = Path(__file__).resolve().parents[1]/"xrun_E2_1000.jsonl.gz"
    readers = [[3,6],[2,0]]
    with gzip.open(path,"rt") as lines:
        row = next(r for r in map(json.loads,lines) if
                   (r["start"],r["readers"],r["law"],r["arm"]) == (1007,readers,"nae","ordinary"))
    assert row["splits"] and not row["S"]["record unchanged"]
    ones = {1,3,8,17}
    for setting in [(0,0),(1,0)][:1 if pilot else 2]:
        base = row["supports"]
        ed = [v.copy() for v in base]
        new = max(max(v) for v in base)+1
        for i,s in enumerate(setting):
            ed[readers[i][s]].append(new+i)
        assert all(0 < len(ones.intersection(r)) < len(r) for r in base + ed)
        status,births = grow(ed, "nae", "ordinary")
        assert status == "funded"
        assert all(sum(bool(set(b["parents"]) & set(rd)) for rd in readers) == 1 for b in births)
        bob = next(b for b in births if b["parents"] == (2,5))
        inp = [int(d in ones) for d in bob["inputs"]]
        completions = [v for v in product(range(2),repeat=bob["f"]) if len(set(inp+list(v))) == 2]
        print(setting, bob["inputs"], tuple(inp), "allowed triples", len(completions),
              "000 allowed", (0,0,0) in completions)
    print("archive",row["retained of old"], row["U"]["scores"],row["S"]["scores"])


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--pilot",action="store_true")
    start = perf_counter()
    replay(p.parse_args().pilot)
    print("seconds",round(perf_counter()-start,3))
