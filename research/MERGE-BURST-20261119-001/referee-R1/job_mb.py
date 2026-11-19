"""Shared-runner job for the referee's check of MERGE-BURST-20261119-001 (own code: the referee's EXPLOSIVE-R1 grower, the program's
rule with groups as maximal cliques of the candidate graph with no common neighbour; the study's starts read from runs/explosive as
data; no study code run).

For each of EXPLOSIVE's 16 explosive cap7 starts, grown in a child process (5.5 GB, 600 s) round by round, after every round:
- the referee's own blocks N(w) ∩ live for every junction w, the maximal ones (equal blocks once, contained ones dropped), and the
  largest number of live junctions two distinct maximal blocks share (the reduction's "two blocks share two points" when >= 2);
- when the maximal blocks are a single block: its size, and the next round's groups computed by the rule itself on the current
  stage (not by the reduction), without building the round: their number and sizes.

Cases class-NN (the reading-slip check): the same growth, and at every round the referee's own class verdict on the stage's maximal
blocks, in the reduction's order: two maximal blocks sharing two live junctions; else three live junctions pairwise in a common
maximal block with no block holding all three (a cycle of three blocks); else the next round stalls (a live junction in more of
the rule's groups than it has loose distinctions); else fewer than two loose distinctions; else in the class (a readable stage).

  .venv/bin/python -B scripts/longrun.py launch research/MERGE-BURST-20261119-001/referee-R1/job_mb.py \\
      --out runs/referee-mb --unit referee-mb --workers 2 --case-timeout 3600 --case-mem 6G --mem-max 13G
"""
import itertools
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/EXPLOSIVE-20261119-001/referee-R1"))
PARAMS = {}
CHILD_AS = 5_500_000_000
SECONDS = 600
CLASS_J = 1000   # the class cases stop past this many junctions; the follow cases give the later rounds' block overlaps


def setup(params):
    PARAMS.update(params)


def stage_blocks(G):
    live = [j for j in range(len(G.bits)) if any(len(G.owner[b]) == 1 for b in G.bits[j])]
    lv = set(live)
    blocks = set()
    for w in range(len(G.bits)):
        B = frozenset(G.nbr[w] & lv)
        if len(B) >= 2:
            blocks.add(B)
    maximal = [B for B in blocks if not any(B < C for C in blocks)]
    worst = 0
    if len(maximal) <= 3000:
        by = defaultdict(list)
        for i, B in enumerate(maximal):
            for k in B:
                by[k].append(i)
        seen = Counter()
        for k, idxs in by.items():
            for a, b in itertools.combinations(idxs, 2):
                seen[(a, b)] += 1
        worst = max(seen.values(), default=0)
    else:
        worst = -1
    return live, maximal, worst


def verdict(G):
    live, maximal, worst = stage_blocks(G)
    if worst < 0 or worst >= 2:
        return "two blocks share two points" if worst >= 2 else "too many blocks to compare", len(maximal)
    of = defaultdict(set)
    for i, B in enumerate(maximal):
        for k in B:
            of[k].add(i)
    co = defaultdict(set)
    for B in maximal:
        for x in B:
            co[x] |= B - {x}
    for x in co:
        for y, z in itertools.combinations(sorted(co[x]), 2):
            if z in co[y] and not (of[x] & of[y] & of[z]):
                return "cycle of three blocks", len(maximal)
    lo = {j: [b for b in G.bits[j] if len(G.owner[b]) == 1] for j in live}
    use = Counter(j for g in G.groups(live, None) for j in g)
    if any(use[j] > len(lo[j]) for j in live):
        return "stall", len(maximal)
    if sum(len(v) for v in lo.values()) < 2:
        return "one loose distinction or none", len(maximal)
    return "in", len(maximal)


def _child_class(conn, sizes, edges, rounds):
    import resource
    import job_expl as JX
    import job_ring as JR
    resource.setrlimit(resource.RLIMIT_AS, (CHILD_AS, CHILD_AS))
    G = JX.grower(JR.stars_of(len(sizes), edges, list(sizes)))
    for t in range(1, rounds + 1):
        r = G.step(JX.floored, None, None)
        if r != "ok":
            conn.send({"kind": r, "t": t})
            return
        v, m = verdict(G)
        conn.send({"kind": "round", "t": t, "junctions": len(G.bits), "maximal blocks": m, "verdict": v})
        if v == "in":
            conn.send({"kind": "in", "t": t})
            return
        if len(G.bits) > CLASS_J:
            conn.send({"kind": "junction cap"})
            return
    conn.send({"kind": "horizon"})


def _child(conn, sizes, edges, rounds):
    import resource
    import job_expl as JX
    import job_ring as JR
    resource.setrlimit(resource.RLIMIT_AS, (CHILD_AS, CHILD_AS))
    G = JX.grower(JR.stars_of(len(sizes), edges, list(sizes)))
    for t in range(1, rounds + 1):
        r = G.step(JX.floored, None, None)
        if r != "ok":
            conn.send({"kind": r, "t": t})
            return
        born = [j for j in range(len(G.bits)) if G.round[j] == t]
        live, maximal, worst = stage_blocks(G)
        rec = {"kind": "round", "t": t, "count": len(born), "group": max(len(G.parents[j]) for j in born), "live": len(live),
               "maximal blocks": len(maximal), "most live shared by two maximal blocks": worst}
        if len(maximal) == 1:
            rec["single block size"] = len(maximal[0])
            gs = G.groups(live, None)
            rec["next round's groups by the rule (count, sizes)"] = [len(gs), dict(Counter(len(g) for g in gs))]
            conn.send(rec)
            conn.send({"kind": "single block", "t": t})
            return
        conn.send(rec)
    conn.send({"kind": "horizon"})


def follow(sizes, edges, rounds=40, target=None):
    import multiprocessing as mp
    import time
    ctx = mp.get_context("fork")
    a, b = ctx.Pipe(duplex=False)
    pr = ctx.Process(target=target or _child, args=(b, sizes, edges, rounds))
    pr.start()
    b.close()
    out, end = [], "memory"
    t0 = time.time()
    while True:
        if a.poll(1.0):
            try:
                m = a.recv()
            except EOFError:
                break
            if m["kind"] == "round":
                out.append(m)
                continue
            end = m["kind"]
            break
        if not pr.is_alive() and not a.poll(0):
            break
        if time.time() - t0 > SECONDS:
            pr.kill()
            end = "time"
            break
    pr.join(5)
    if pr.is_alive():
        pr.kill()
    return {"rounds": out, "end": end}


def population():
    out = []
    for line in open(ROOT / "runs/explosive/results.jsonl"):
        r = json.loads(line)
        if not r["case"].startswith("cap-7"):
            continue
        for x in r["result"]["starts"]:
            if x["measured"] == "explosive":
                out.append({"sizes": x["sizes"], "edges": [tuple(y) for y in x["edges"]], "n": x["n"]})
    out.sort(key=lambda x: (x["n"], sum(x["sizes"]), x["sizes"], x["edges"]))
    return out


def cases():
    only = set(PARAMS["only"].split(",")) if PARAMS.get("only") else None
    for i, x in enumerate(population()):
        for cid, kind in ((f"start-{i:02d}", "follow"), (f"class-{i:02d}", "class")):
            if (only is None and kind == "follow") or (only is not None and cid in only):
                yield cid, {"i": i, "kind": kind}


def run(case_id, p):
    x = population()[p["i"]]
    if p.get("kind") == "class":
        return {"start": x, "class": follow(x["sizes"], x["edges"], target=_child_class)}
    return {"start": x, "follow": follow(x["sizes"], x["edges"])}
