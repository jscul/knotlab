"""Read-out of runs/referee-selfpairs (job_selfpairs.py) into referee_selfpairs.json, with the study's selfpairs.json read as data
for the comparison of totals.

  .venv/bin/python -B research/HUNT-SHORTEN-20261119-001/referee-R1/selfpairs_readout.py
"""
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
STUDY = ROOT / "artifacts/HUNT-SHORTEN-20261119-001A/HUNT-SHORTEN-20261119-001A-E001_attach/selfpairs.json"


def main():
    tot = Counter()
    fails, stages = [], []
    for line in open(ROOT / "runs/referee-selfpairs/results.jsonl"):
        r = json.loads(line)
        assert r["status"] == "ok", (r["case"], r["error"])
        for k, v in r["result"]["counts"].items():
            tot[k] += v
        fails += r["result"]["failures"]
        stages += r["result"]["stages with R-keeping isometries"]
    per = Counter()
    for key, rnd, nj, keep, ok, hb, capped in stages:
        per["stages"] += 1
        per["stages with more than 20 R-keeping isometries"] += keep > 20
        per["R-keeping isometries beyond the first 20 of each stage"] += max(0, keep - 20)
        per["stages capped"] += capped
    # the one stage capped at 200,000 representatives, finished without a cap by job_onestage.py (runs/referee-onestage2)
    one = json.loads(open(ROOT / "runs/referee-onestage2/results.jsonl").readline())["result"]
    capped = [s for s in stages if s[6]]
    assert len(capped) == 1
    k, rnd, nj, keep, ok, hb, _ = capped[0]
    done = dict(tot)
    done["rounds 1-7: coset representatives"] += one["coset representatives"] - 200000
    done["rounds 1-7: carry the equations"] += one["carry the equations"] - (200000 - keep)
    done["rounds 1-7: do not carry the equations"] += one["keep R, not the equations"] - keep
    done["rounds 1-7: keep R, not the equations"] += one["keep R, not the equations"] - keep
    done["rounds 1-7: keep R, not the equations, holder-breaking"] += one["keep R, not the equations, holder-breaking"] - hb
    done["rounds 1-7: extensions that are isometries"] += one["extensions that are isometries"] - ok
    done["rounds 1-7: capped"] -= 1
    out = {"totals": dict(sorted(tot.items())), "totals with the capped stage finished": dict(sorted(done.items())),
           "the capped stage, finished": {"start": k, "round": rnd, "junctions": nj, **one},
           "per stage": dict(per), "failures": fails,
           "study (selfpairs.json, read as data)": json.loads(STUDY.read_text())["counts"]}
    (HERE / "referee_selfpairs.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items()}, indent=1)[:5000])


if __name__ == "__main__":
    main()
