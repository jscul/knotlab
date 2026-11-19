"""Shared-runner job for the referee's check of BREAK-EDDIES-20261119-001 (own engine; the starts read from the study's
population.json and population_ref.json as data; no study code imported or run).

Each start (sizes and touches, built by the referee's TOUCH-CENSUS-R1 convention) is grown in a child process with its own
address-space limit (CHILD_GB) by the referee's engine (complete rounds, the fewest counts, GF(2) implication; FRESH-COUNT-R1 /
FIRST-KNOT-R1), printing after every round its counts, the largest group (most parents of one new junction) and the live
junctions, to 60 rounds or MAXJ junctions (30,000).  The last line read is kept, so a case stopped by memory or time still reports the
rounds it finished.  Then the stage test: for s = 1, 2, 3 the stage after s rounds is taken as a start (its junction stars, nothing
else) and grown 8 rounds beside the original's continuation (both capped at 20,000 junctions), and the counts compared.

  .venv/bin/python -B scripts/longrun.py launch research/BREAK-EDDIES-20261119-001/referee-R1/job_break.py \\
      --out runs/referee-break-eddies --unit referee-break-eddies --workers 3 --case-timeout 1800 --case-mem 4G --mem-max 16G
"""
import json
import resource
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EXP = ROOT / "experiments/BREAK-EDDIES-20261119-001B/BREAK-EDDIES-20261119-001B-E001_breaks"
CHILD_GB = 3.5
MAXJ = 30000                                           # enough rounds for the recurrences; the study went to 300,000
CHILD = r'''
import json, sys
from pathlib import Path
ROOT = Path(sys.argv[1])
for p in ("research/FIRST-KNOT-20261118-001/referee-R1", "research/TOUCH-CENSUS-20261118-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
import referee_first as RFK
import referee_touch as RT
st = json.loads(sys.argv[2]); MAXJ = int(sys.argv[3]); mode = sys.argv[4]
n = len(st["sizes"])
M = [[0] * n for _ in range(n)]
for a, b in st["edges"]:
    M[a][b] += 1; M[b][a] += 1
S0 = RT.stars(st["sizes"], M)

def largest(G, r):
    return max((len(G.parents[j]) for j in range(len(G.bits)) if G.round[j] == r), default=0)

if mode == "grow":
    G = RFK.Start(S0)
    groups = []
    for _ in range(60):
        r = G.step(RFK.fewest, None, None)
        if r != "ok":
            print(json.dumps({"end": r}), flush=True)
            break
        groups.append(largest(G, G.rounds))
        print(json.dumps({"counts": G.counts(), "group": groups, "live": len(G.live)}), flush=True)
        if len(G.bits) > MAXJ:
            print(json.dumps({"end": "junction cap"}), flush=True)
            break
else:
    out = {}
    for s in (1, 2, 3):
        G = RFK.Start(S0)
        ok = all(G.step(RFK.fewest, None, None) == "ok" for _ in range(s))
        if not ok:
            out[s] = "ended"
            continue
        H = RFK.Start([list(b) for b in G.bits])
        a, b = [], []
        for _ in range(8):
            ra = G.step(RFK.fewest, None, None)
            rb = H.step(RFK.fewest, None, None)
            if ra != rb:
                a.append(ra); b.append(rb)
                break
            if ra != "ok":
                break
            a.append(sum(1 for j in range(len(G.bits)) if G.round[j] == G.rounds))
            b.append(sum(1 for j in range(len(H.bits)) if H.round[j] == H.rounds))
            if len(G.bits) > 20000:
                break
        out[s] = {"continued": a, "as a start": b, "equal": a == b}
    print(json.dumps({"stage": out}), flush=True)
'''


def child(st, mode, timeout):
    lim = int(CHILD_GB * 2 ** 30)
    try:
        p = subprocess.run([sys.executable, "-B", "-c", CHILD, str(ROOT), json.dumps(st), str(MAXJ), mode], capture_output=True,
                           text=True, timeout=timeout, preexec_fn=lambda: resource.setrlimit(resource.RLIMIT_AS, (lim, lim)))
        lines, stop = p.stdout.strip().splitlines(), ("finished" if p.returncode == 0 else f"memory (exit {p.returncode})")
    except subprocess.TimeoutExpired as ex:
        out = ex.stdout.decode() if isinstance(ex.stdout, bytes) else (ex.stdout or "")
        lines, stop = out.strip().splitlines(), "time"
    return [json.loads(x) for x in lines if x.startswith("{")], stop


def cases():
    for i, st in enumerate(json.loads((EXP / "population.json").read_text())):
        yield f"G-{i:03d}", {"start": st}
    for i, st in enumerate(json.loads((EXP / "population_ref.json").read_text())):
        yield f"F-{i:02d}", {"start": st}


def run(case_id, payload):
    st = {"sizes": payload["start"]["sizes"], "edges": payload["start"]["edges"]}
    rows, stop = child(st, "grow", 1200)
    last = next((r for r in reversed(rows) if "counts" in r), {"counts": [len(st["sizes"])], "group": [], "live": None})
    end = next((r["end"] for r in rows if "end" in r), None)
    out = {"start": st, **last, "stop": end or stop}
    srows, sstop = child(st, "stage", 400)
    out["stage"] = srows[-1]["stage"] if srows else sstop
    return out
