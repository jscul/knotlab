"""Test (a): extension by enumeration.  Every round t to t+1 of every R history of tests (c), (d) and (e) whose stage t
has at most 22 distinctions (the stored prefixes, artifacts/.../prefixes/), under the history's law: every allowed word
of stage t is enumerated and, for each birth of round t+1, every assignment of its fresh distinctions; a word extends when
every birth has one satisfying its law (words.Stage.extends).  Cross-check: where stage t+1 has at most 24 distinctions,
all its assignments are enumerated and the allowed words, forgotten onto stage t, are compared with stage t's.  The
enumerated choices of test (c) are checked inside test_c_enum.py; their counts are added here.

Run from the repo root:  timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file> [--part c|d|e|enum]
"""
import argparse
import glob
import json
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rlaw  # noqa: E402
import words  # noqa: E402

PROJECTION_LIMIT = 24


def check_prefix(pre, c, failures):
    stars = [tuple(s) for s in pre["stars"]]
    n_at = pre["n_at"]
    law = pre["law"]
    c["histories"] += 1
    for t in range(len(n_at) - 1):
        old = stars[:n_at[t]]
        old_names = {d for s in old for d in s}
        assert len(old_names) <= 22
        new = stars[n_at[t]:n_at[t + 1]]
        births = [(tuple(d for d in s if d in old_names), sum(1 for d in s if d not in old_names)) for s in new]
        stage = words.Stage(old, law)
        bad_words, bad_births = stage.extends(births)
        c["rounds"] += 1
        c["births"] += len(births)
        c["births_with_shared"] += pre["paid_births"][t]
        c["zero_fresh_births"] += sum(1 for _, f in births if f == 0)
        c["words_checked"] += stage.n_ok
        c["words_failing"] += bad_words
        c["births_failing"] += bad_births
        if stage.n_ok == 0:
            c["stages_with_no_word"] += 1
        if bad_words:
            failures.append({k: pre.get(k) for k in ("test", "arm", "draw", "conv", "law", "name", "settings", "which")}
                            | {"t": t + 1, "failing_words": bad_words})
        names_next = old_names | {d for s in new for d in s}
        if len(names_next) <= PROJECTION_LIMIT:
            n_old, n_new, reached, equal = words.projection_check(old, new, law)
            c["projection_checks"] += 1
            c["projection_equal"] += equal
            assert n_old == stage.n_ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", default="all", choices=("all", "c", "d", "e", "enum"))
    args = ap.parse_args()
    t0 = time.time()
    res = {}
    pdir = rlaw.OUT / "prefixes"
    for part in ("c", "d", "e"):
        if args.part not in ("all", part):
            continue
        c, c_ord, failures = Counter(), Counter(), []
        for f in sorted(glob.glob(str(pdir / f"{part}*.jsonl.gz"))):
            for pre in rlaw.load(f):
                check_prefix(pre, c_ord if pre.get("rule") == "ordinary" else c, failures)
        res[part] = {"counts": dict(c), "failures": failures}
        if c_ord:
            res[part]["ordinary_rows_counts"] = dict(c_ord)
    if args.part in ("all", "enum"):
        c = Counter()
        files = sorted(glob.glob(str(rlaw.OUT / "enum" / "a_enum_*.json")))
        for f in files:
            c.update(json.loads(Path(f).read_text()))
        res["enum"] = {"counts": dict(c), "files": len(files)}
    res["seconds"] = round(time.time() - t0, 1)
    (rlaw.OUT / f"a_{args.part}.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res)[:3000])


if __name__ == "__main__":
    main()
