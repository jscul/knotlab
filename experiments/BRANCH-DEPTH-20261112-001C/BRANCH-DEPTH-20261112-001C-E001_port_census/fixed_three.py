"""Decide the exact depth set at budget three for the remaining 75 records."""
from argparse import ArgumentParser
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
import gzip
import json
import sys

from census import OUT, ROOT, SOURCE

SOLVER = ROOT / "proofs/BRANCH-DEPTH-20261112-001D/BRANCH-DEPTH-20261112-001D-P001_fixed_budget"
sys.path.insert(0, str(SOLVER))
from check import Profiles, decide_dlang  # noqa: E402


def run_case(item):
    filename,line,definitions = item
    result = decide_dlang(definitions,budget=3,max_profiles=100000,usual_limit=True)
    # Cached method keys retain solver instances; keep the serial and
    # multiprocess replays bounded by each individual case.
    Profiles.compose.cache_clear()
    orbit = result["orbit"]
    answers = orbit["answers"]
    repeating = answers[orbit["preperiod"]:]
    if all(repeating):
        outcome = "all_positive" if all(answers[1:]) else "eventually_all"
    elif any(repeating):
        outcome = "some_periodic"
    else:
        outcome = "eventually_absent"
    return dict(file=filename,line=line,classification=outcome,
                profiles=result["unrestricted_profiles"],orbit=orbit)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    endpoint_data=json.loads((OUT/"endpoint_tables.json").read_text())
    residual={(r["file"],r["line"]) for r in endpoint_data["rows"]
              if r["classification"] != "every_positive_depth"}
    inputs=[]
    for filename in sorted({f for f,_ in residual}):
        for line,raw in enumerate(gzip.open(SOURCE/filename,"rt"),1):
            if (filename,line) in residual:
                inputs.append((filename,line,json.loads(raw)["defs"]))
    assert len(inputs)==len(residual)
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        results=list(pool.map(run_case,inputs,chunksize=1))
    totals=dict(Counter(r["classification"] for r in results))
    (OUT/"fixed_three.json").write_text(json.dumps(dict(totals=totals,rows=results),
                                                   separators=(",",":"))+"\n")
    print(json.dumps(totals,indent=2))


if __name__ == "__main__":
    main()
