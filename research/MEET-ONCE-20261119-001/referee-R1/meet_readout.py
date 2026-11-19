"""Readout of the referee's MEET-ONCE check (job_meetonce.py from GROWN-PAIR-R1 with --param notable=1, job_meet_tables.py,
job_meet_groups.py; runs/referee-meet-once-*).

  ../../../.venv/bin/python -B meet_readout.py > referee_meet.json
"""
import gzip
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ART = ROOT / "artifacts/MEET-ONCE-20261119-001A/MEET-ONCE-20261119-001A-E001_meet"
UT = ROOT / "artifacts/UNIQUE-TABLE-20261119-001A/UNIQUE-TABLE-20261119-001A-E001_unique/verify_rivals.json"


def lines(run):
    return [json.loads(x) for x in open(ROOT / "runs" / run / "results.jsonl")]


def meet_once(stars):
    own = defaultdict(list)
    for j, s in enumerate(stars):
        for b in s:
            own[b].append(j)
    c = Counter(tuple(v) for v in own.values() if len(v) == 2)
    return not c or max(c.values()) < 2


def groups_of(run):
    G = []
    for r in lines(run):
        G += r["result"]["groups"]
    return G


def tally(G):
    T = [t for g in G for t in g["tests"]]
    return {"groups": len(G), "sizes": dict(Counter(g["arrangements"] for g in G)),
            "one state group (same states)": sum(g["state groups"] == 1 for g in G),
            "two or more state groups": sum(g["state groups"] > 1 for g in G), "undecided": sum(g["undecided"] for g in G),
            "tests": len(T), "tests by kind, method, verdict": {" / ".join(map(str, k)): v for k, v in
                                                               Counter((t["kind"], t["how"], t["same states"]) for t in T).items()}}


def main():
    census = {}
    for line in open(ROOT / "runs/census-exact5/results.jsonl"):
        r = json.loads(line)
        if r.get("status") == "ok" and r["case"].startswith("census"):
            for a in r["result"]["arrangements"]:
                census[a["index"]] = a["key"]
    mine = {}
    for r in lines("referee-meet-once-pop"):
        for s in r["result"]["stages"]:
            mine[(s["index"], s["round"])] = s
    theirs, shards = {}, Counter()
    for line in gzip.open(ART / "results_meet-once.jsonl.gz", "rt"):
        r = json.loads(line)
        shards[r["status"]] += 1
        if r["status"] == "ok":
            for s in r["result"]["stages"]:
                theirs[(s["index"], s["round"])] = s
    tabs = [r["result"] for r in lines("referee-meet-once-tables")]
    G = groups_of("referee-meet-once-groups")
    study = json.load(open(ART / "meet_pairs2.json"))
    mine_sets = [frozenset(tuple(p) for cls in g["provenance"] for p in cls) for g in G]
    contained = sum(any(frozenset(tuple(m["prov"][0]) for m in g["members"]) <= s for s in mine_sets) for g in study["groups"])

    def closed(st):
        c = Counter(b for s in st for b in s)
        return all(v == 2 for v in c.values())
    open_groups = sum(sum(not closed(m["stars"]) for m in g["members"]) >= 2 for g in study["groups"])
    P = groups_of("referee-meet-once-past-groups")

    def band(j):
        return "41 to 50" if min(j) >= 41 else ("15 to 40" if min(j) >= 15 and max(j) <= 40 else "straddling 14 and 15")
    past_stages = Counter()
    for r in lines("referee-meet-once-past"):
        for s in r["result"]["stages"]:
            past_stages[len(s["stars"])] += 1
    six = json.load(open(UT))
    print(json.dumps({
        "population": {
            "census starts": len(census), "study shards ok": dict(shards),
            "starts covered by the study's shards (index range)": [min(i for i, _ in theirs), max(i for i, _ in theirs)],
            "meet-once grown stages, 15 to 40 junctions: referee / study": [len(mine), len(theirs)],
            "same (start, round) set": set(mine) == set(theirs),
            "same start key on every stage": all(census[i] == theirs[(i, r)]["key"] for i, r in theirs),
            "same junction count on every stage": all(len(mine[k]["stars"]) == theirs[k]["junctions"] for k in theirs)},
        "tables read to distance 8": {
            "stages": len(tabs), "slowest (s)": max(t["seconds"] for t in tabs),
            "equal to the referee's full shore table at <= 9 (stages of at most 18 junctions)":
                dict(Counter(str(t.get("equals the full shore table at <= 9")) for t in tabs))},
        "non-isomorphic arrangements (singleton buckets + classes in shared buckets)":
            sum(v for v in Counter((t["distinctions"], t["invariant"]) for t in tabs).values() if v == 1)
            + sum(r["result"]["classes"] for r in lines("referee-meet-once-groups")),
        "candidate groups (15 to 40)": tally(G),
        "study's 102 groups each inside a referee group": contained,
        "groups with two or more open arrangements (the note's 'without them')": open_groups,
        "one size past (every meet-once grown stage of 14 to 50 junctions)": {
            "stages by junctions": dict(sorted(past_stages.items())), **tally(P),
            "groups by band": dict(Counter(band(g["junctions"]) for g in P))},
        "UNIQUE-TABLE's six static pairs (junctions, truth meets once, rival meets once)": [
            [r["case"], r["junctions"], meet_once(r["truth"]), meet_once(r["rival"])] for r in six],
        "groups": G}, indent=1))


if __name__ == "__main__":
    main()
