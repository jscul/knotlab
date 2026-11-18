"""Shared-runner wrapper for run.py's census part (the frozen census code, unchanged): one case per population."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def cases():
    yield "cheap", {"pop": "cheap", "nmax": 12}
    yield "one-split", {"pop": "one-split", "nmax": 8}


def run(case_id, payload):
    import time
    import census as G
    t0 = time.time()
    canon, levels = G.reachable(payload["pop"], payload["nmax"])
    out = {}
    for n, cl in levels.items():
        out[str(n)] = G.determination(canon, cl, n)
        out[str(n)]["seconds"] = round(time.time() - t0, 1)
    return out
