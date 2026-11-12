#!/usr/bin/env python3
"""Stress test one size past (after the run, not frozen): H1 and H2 at spans 11 and 12 under not-all-equal, with the frozen
harm_lib. Each span is split by its first knot kind across workers."""
import json
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import harm_lib as H  # noqa: E402


def job(arg):
    W, first = arg
    out = Counter()
    per = Counter()
    for S in H.patterns(W):
        if S[0] != first:
            continue
        c, cycles = H.classify(W, S, "NAE")
        out["patterns"] += 1
        if c != "harmony":
            continue
        out["harmonies"] += 1
        g = H.offset_gcd(S)
        for w in cycles:
            per[len(w)] += 1
            out["states"] += 1
            out["odd period"] += len(w) % 2
            if not H.antiperiodic(w):
                out["not antiperiodic"] += 1
                out["not antiperiodic, connected"] += g == 1
    return W, dict(out), dict(per)


def main():
    t = time.time()
    jobs = [(W, k) for W in (11, 12) for k in H.kinds_of_span(W)]
    res = {}
    with Pool(16) as pool:
        for W, out, per in pool.imap_unordered(job, jobs):
            r = res.setdefault(W, {"tally": Counter(), "periods": Counter()})
            r["tally"].update(out)
            r["periods"].update(per)
    final = {str(W): {"tally": dict(r["tally"]), "periods": dict(sorted(r["periods"].items()))} for W, r in sorted(res.items())}
    final["H1 holds one size past"] = all(final[str(W)]["tally"].get("odd period", 0) == 0 for W in (11, 12))
    final["H2 holds one size past"] = all(final[str(W)]["tally"].get("not antiperiodic, connected", 0) == 0 for W in (11, 12))
    final["seconds"] = round(time.time() - t, 1)
    print(json.dumps(final, indent=1))
    (HERE / "result_stress.json").write_text(json.dumps(final, indent=1) + "\n")


if __name__ == "__main__":
    main()
