"""Supplement to GROW-COUNT-20261111-001A-E001, after the run (not the frozen test). The frozen census.py left the world's distinction
count raised after a rejected move with a new distinction, so later proposals could pick an isolated "phantom" distinction as an
existing one (in effect a new one), and its surface and Euler readings counted phantoms. This reruns the registered design with that
fixed (World.remove restores the count), evaluates P5 in code, and reads surfaces on the distinctions in knots.
Writes supplement.json and supplement_log.txt beside this file."""
import json, os, sys
from collections import Counter
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "experiments", "GROW-COUNT-20261111-001A", "GROW-COUNT-20261111-001A-E001_count_from_growth"))
import census as c

_remove = c.World.remove
def remove(self, t):
    _remove(self, t)
    used = {v for k in self.knots for v in k}
    self.V = max(used) + 1
c.World.remove = remove

def used_reading(r):
    T = [tuple(t) for t in r["T"]]
    used = sorted({v for t in T for v in t})
    idx = {v: i for i, v in enumerate(used)}
    T2 = [tuple(sorted(idx[v] for v in t)) for t in T]
    return len(used), c.ka.is_surface(len(used), T2), c.ka.euler(len(used), T2), r["V"] - len(used)

if __name__ == "__main__":
    jobs = [(r, b, s, law) for r in c.RULES for b in c.CLOSE_BIAS for s in c.SEEDS for law in c.LAWS_RUN]
    with Pool(c.WORKERS) as pool:
        runs = pool.map(c.grow, jobs, chunksize=1)
    out = {}
    for rule in c.RULES:
        for law in c.LAWS_RUN:
            rs = [r for r in runs if r["rule"] == rule and r["law"] == law]
            deg, cok, cno = Counter(), Counter(), Counter()
            surf = []
            for r in rs:
                deg.update({int(k): v for k, v in r["closed degrees"].items()})
                cok.update({int(k): v for k, v in r["closings accepted by degree"].items()})
                cno.update({int(k): v for k, v in r["closings rejected by degree"].items()})
                n, is_s, chi, phantom = used_reading(r)
                if is_s:
                    surf.append((n, chi))
            out[f"{rule} {law}"] = {"runs": len(rs), "stalled": sum(r["stalled"] for r in rs),
                "runs with pairs in three or more knots": sum(1 for r in rs if any(int(k) >= 3 for k in r["pairs by count"])),
                "runs with pinched links": sum(1 for r in rs if r["pinched links"]),
                "closed degrees": dict(sorted(deg.items())), "closings accepted by degree": dict(sorted(cok.items())),
                "closings rejected by degree": dict(sorted(cno.items())),
                "runs with degree 6 at 90% or more": sum(1 for r in rs if r["closed degrees"] and r["closed degrees"].get(6, 0) >= 0.9 * sum(r["closed degrees"].values())),
                "closed surfaces (distinctions, chi)": sorted(surf), "phantoms left": sum(used_reading(r)[3] for r in rs)}
    s = out
    s["P1"] = s["free NAE"]["runs with pairs in three or more knots"] == s["free NAE"]["runs"]
    s["P2"] = s["open NAE"]["runs with pinched links"] > 0
    s["P3"] = len(s["disc NAE"]["closed degrees"]) >= 3 and s["disc NAE"]["runs with degree 6 at 90% or more"] == 0
    s["P4"] = not any(chi == 0 for n, chi in s["disc NAE"]["closed surfaces (distinctions, chi)"])
    s["P5"] = s["disc NAE"]["closings accepted by degree"].get(3, 0) == 0
    print(json.dumps(s, indent=1))
    json.dump({"summary": s, "runs": runs}, open(os.path.join(HERE, "supplement.json"), "w"), default=str)
