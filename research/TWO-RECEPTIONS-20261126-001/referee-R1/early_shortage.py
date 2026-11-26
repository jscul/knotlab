"""Rebuild the initial owing of pairs reported to hear under the cross-part take."""
from collections import Counter
import gzip
import json
from pathlib import Path
import resource
import sys
from time import perf_counter

resource.setrlimit(resource.RLIMIT_AS, (512 * 1024**2,) * 2)
from reception_growth import build_pair, eng


def read():
    source = Path(__file__).resolve().parents[1] / "shortage_runs.jsonl.gz"
    out = []
    with gzip.open(source, "rt") as stream:
        for line in stream:
            r = json.loads(line)
            if r.get("law") != ["ORD", "J-EACH-PART", None]:
                continue
            heard = [c["heard"] for c in r["changes"] if c["heard"] is not None]
            if not heard:
                continue
            pair = build_pair(r["A"], r["B"])
            state = eng.from_stars(pair.stars)
            roster = eng.build_roster(state, eng.live_members(state), "start", eng.Guard(4))
            owing = Counter(u for g in roster.groups for u in g)
            short = [u for u in roster.members if owing[u] > len(state.usable(u))]
            out.append({"receiver":r["A"], "sender":r["B"], "start short":short, "recorded hearings":heard})
            if "--pilot" in sys.argv:
                break
    return out


if __name__ == "__main__":
    start = perf_counter()
    rows = read()
    print(json.dumps({"pairs":len(rows), "pairs with a short start":sum(bool(r["start short"]) for r in rows),
                      "hearings with a short start":sum(len(r["recorded hearings"]) for r in rows if r["start short"]),
                      "hearings":sum(len(r["recorded hearings"]) for r in rows),
                      "rows":rows, "seconds":round(perf_counter()-start,4)}, indent=2))
