"""Shared-runner job for the referee's check of EXTEND-ROUND-20261119-001 (own growth, own full tables, own isometry enumeration,
own reading test and own extension; GROW-SMALL's origin.json and PARENT-RULE-R1's static grouping read as data; no study code
imported or run).

Pairs:
- reached: all 87 of GROW-SMALL (both stages regrown by the referee's FIRST-KNOT-R1 engine with the program's rule), the 23 larger
  ones the study left out included;
- static: the 1,034 pairs of PARENT-RULE-R1's own grouping (runs/referee-parent-groups), rebuilt from the atlas.
For each pair (A -> B):
- every isometry of the full tables (CREATED-PAIR-R1's enumerator: no WL colours, no twin quotient);
- the reading R (Lemma A): the live junctions, their loose counts, the family F of sets of live junctions met by one junction.
  An isometry keeps R when it carries the loose distinctions onto the loose ones and each live junction's distinctions onto a live
  junction's (psi), and psi carries F onto F.  Recorded for F whole and for its maximal members only (what extend.py tests);
- every R-keeping isometry (no cap of 50) is extended through the referee's own round: each new junction of A's next stage is
  matched to B's with psi of its parent set and the same fresh count, its taken distinctions to the counterpart's taken from
  psi of each parent, its fresh ones in order; the extension is checked entry by entry on the next full tables (the referee's shore
  enumeration up to 22 junctions, else GROW-SMALL-R1's flow-bounded bonds with every pair of one block reached);
- whether the next tables are isometric at all, and whether some isometry of them carries old distinctions onto old ones (a
  search with the age in the first colours).

  .venv/bin/python -B scripts/longrun.py launch research/EXTEND-ROUND-20261119-001/referee-R1/job_extend.py \\
      --out runs/referee-extend --unit referee-extend --workers 4 --case-timeout 3600 --case-mem 3G --mem-max 16G
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/CREATED-PAIR-20261119-001/referee-R1", "research/GROW-SMALL-20261119-001/referee-R1",
          "research/VARIABLE-OUTPUT-READER-20261118-001F/referee-R1", "research/FIRST-KNOT-20261118-001/referee-R1",
          "research/CENSUS-READ-20261118-001/referee-R1", "research/GROWN-PAIR-20261119-001/referee-R1",
          "research/MEET-ONCE-20261119-001/referee-R1", "research/PARENT-RULE-20261119-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
ORIGIN = ROOT / "artifacts/GROW-SMALL-20261119-001A/GROW-SMALL-20261119-001A-E001_grow/origin.json"
PARAMS = {}


def setup(params):
    PARAMS.update(params)


def floored(G, info, rng):
    return [i["d"] if i["implied"] else max(i["d"], 3 - i["p"], 1) for i in info]


def grow(stars, rounds):
    """The stage after 'rounds' rounds and one more, both relabelled together (old labels kept), with round tags and parents."""
    import referee_first as RFK
    G = RFK.Start([list(s) for s in stars])
    for _ in range(rounds):
        if G.step(floored, None, None) != "ok":
            return None
    stage = [sorted(b) for b in G.bits]
    nj = len(stage)
    r = G.step(floored, None, None)
    if r != "ok":
        return {"stage": stage, "next": None, "status": r}
    nxt = [sorted(b) for b in G.bits]
    new = [{"j": j, "parents": sorted(G.parents[j]), "fresh": G.fresh[j]} for j in range(nj, len(nxt))]
    return {"stage": stage, "next": nxt, "new": new}


def relabel_pair(stage, nxt):
    labels = sorted({b for s in nxt for b in s})
    idx = {b: i for i, b in enumerate(labels)}
    old = sorted({idx[b] for s in stage for b in s})
    return [sorted(idx[b] for b in s) for s in stage], [sorted(idx[b] for b in s) for s in nxt], set(old)


def owners(S):
    own = defaultdict(list)
    for j, s in enumerate(S):
        for x in s:
            own[x].append(j)
    return own


def reading(S):
    own = owners(S)
    nb = defaultdict(set)
    for js in own.values():
        if len(js) == 2:
            nb[js[0]].add(js[1])
            nb[js[1]].add(js[0])
    live = sorted({js[0] for js in own.values() if len(js) == 1})
    lv = set(live)
    fam = {frozenset(nb[w] & lv) for w in range(len(S)) if len(nb[w] & lv) >= 2}
    fmax = {s for s in fam if not any(s < t for t in fam)}
    loose = {x for x, js in own.items() if len(js) == 1}
    return live, loose, fam, fmax


def keeps(phi, SA, SB, ra, rb):
    live_a, loose_a, fam_a, fmax_a = ra
    live_b, loose_b, fam_b, fmax_b = rb
    if {phi[x] for x in loose_a} != loose_b:
        return None, False, False
    star_b = {frozenset(SB[u]): u for u in live_b}
    psi = {}
    for u in live_a:
        img = frozenset(phi[x] for x in SA[u])
        if img not in star_b:
            return None, False, False
        psi[u] = star_b[img]
    whole = {frozenset(psi[u] for u in s) for s in fam_a} == fam_b
    top = {frozenset(psi[u] for u in s) for s in fmax_a} == fmax_b
    return psi, whole, top


def extend(phi, psi, A, B):
    """phi' on A's next distinctions (relabelled indices), or None when the rounds do not correspond under psi."""
    SA, NA, newA = A["S"], A["N"], A["new"]
    SB, NB, newB = B["S"], B["N"], B["new"]
    oldA, oldB = A["old"], B["old"]
    if len(newA) != len(newB):
        return None
    pool = defaultdict(list)
    for q in newB:
        pool[(frozenset(q["parents"]), q["fresh"])].append(q)
    ownB = owners(SB)
    phi2 = dict(phi)
    for q in newA:
        key = (frozenset(psi.get(u, -1) for u in q["parents"]), q["fresh"])
        if not pool.get(key):
            return None
        r = pool[key].pop()
        taken_a = [x for x in NA[q["j"]] if x in oldA]
        fresh_a = [x for x in NA[q["j"]] if x not in oldA]
        by_parent_b = {ownB[x][0]: x for x in NB[r["j"]] if x in oldB}
        ownA = A["own"]
        for x in taken_a:
            phi2[x] = by_parent_b[psi[ownA[x][0]]]
        for x, y in zip(fresh_a, [x for x in NB[r["j"]] if x not in oldB]):
            phi2[x] = y
    if sorted(phi2.values()) != list(range(len(phi2))) or len(phi2) != len({x for s in NB for x in s}):
        return None
    return phi2


def side(stars, rounds):
    g = grow(stars, rounds)
    if g is None or g["next"] is None:
        return None
    S, N, old = relabel_pair(g["stage"], g["next"])
    # parents are junction indices (unchanged by relabelling)
    own1 = {q["j"]: frozenset(q["parents"]) for q in g["new"]}
    return {"S": S, "N": N, "old": old, "new": g["new"], "own": owners(S), "own1": own1}


def analyse(sa, sb, rounds):
    import job_created as JC
    import job_growsmall as GS
    A, B = side(sa, rounds), side(sb, rounds)
    out = {"both grow a round": A is not None and B is not None}
    if not out["both grow a round"]:
        return out
    out["junctions"] = [len(A["S"]), len(B["S"])]
    out["next junctions"] = [len(A["N"]), len(B["N"])]
    # tables of the stage on the old distinctions (relabelled 0..n-1 in the same order as the next stage's labels)
    KA, _, _, _ = GS.full_table([sorted(s) for s in A["S"]])
    KB, _, _, _ = GS.full_table([sorted(s) for s in B["S"]])
    # GS.full_table relabels to 0..nb-1 in sorted order; the old labels are an initial segment? map explicitly
    la, lb = sorted(A["old"]), sorted(B["old"])
    ra, rb = reading(A["S"]), reading(B["S"])
    KA1, _, _, how_a = GS.full_table(A["N"])
    KB1, _, _, how_b = GS.full_table(B["N"])
    out["next tables by"] = [how_a, how_b]
    n_iso = keep_whole = keep_top = ext_ok = ext_bad = no_corr = 0
    if len(la) == len(lb):
        for phi0 in JC.isometries(KA, KB):
            n_iso += 1
            phi = {la[x]: lb[y] for x, y in enumerate(phi0)}
            psi, whole, top = keeps(phi, A["S"], B["S"], ra, rb)
            keep_whole += whole
            keep_top += top
            if psi is None or not top:
                continue
            phi2 = extend(phi, psi, A, B)
            if phi2 is None:
                no_corr += 1
                continue
            n1 = len(KA1)
            ok = all(KA1[x][y] == KB1[phi2[x]][phi2[y]] for x in range(n1) for y in range(x + 1, n1))
            ext_ok += ok
            ext_bad += not ok
            if "control" not in out:
                # control: swap the images of two fresh distinctions of different new junctions; the check should refuse it
                fr = [(x, q["j"]) for q in A["new"] for x in A["N"][q["j"]] if x not in A["old"]]
                two = next(((x, y) for (x, jx) in fr for (y, jy) in fr if jx != jy and A["own1"][jx] != A["own1"][jy]), None)
                if two:
                    bad = dict(phi2)
                    bad[two[0]], bad[two[1]] = phi2[two[1]], phi2[two[0]]
                    out["control"] = not all(KA1[x][y] == KB1[bad[x]][bad[y]] for x in range(n1) for y in range(x + 1, n1))
    out.update({"isometries": n_iso, "keep R (F whole)": keep_whole, "keep R (maximal members of F)": keep_top,
                "extensions that are isometries of the next tables": ext_ok, "extensions that are not": ext_bad,
                "rounds do not correspond": no_corr})
    if len(KA1) == len(KB1):
        first = next(iter(JC.isometries(KA1, KB1, cap=1)), None)
        out["next tables isometric"] = first is not None
        if first is not None:
            n1 = len(KA1)
            ex = [[int(x in A["old"]) for x in range(n1)], [int(y in B["old"]) for y in range(n1)]]
            out["some next isometry carries old onto old"] = next(iter(JC.isometries(KA1, KB1, extra=ex, cap=1)), None) is not None
    else:
        out["next tables isometric"] = False
    return out


def cases():
    only = set(PARAMS["only"].split(",")) if PARAMS.get("only") else None
    allc = [(f"R-{i:03d}", {"part": "R", "pair": p}) for i, p in enumerate(json.load(open(ORIGIN))["pairs"])]
    st = []
    for line in open(ROOT / "runs/referee-parent-groups/results.jsonl"):
        r = json.loads(line)
        for g in r["result"]["other-states groups"]:
            sg = g["state groups"]
            for x in range(len(sg)):
                for y in range(x + 1, len(sg)):
                    for a in sg[x]:
                        for b in sg[y]:
                            st.append([a, b])
    for a in range(0, len(st), 40):
        allc.append((f"S-{a // 40:03d}", {"part": "S", "pairs": st[a:a + 40]}))
    for cid, p in allc:
        if only is None or cid in only:
            yield cid, p


def run(case_id, p):
    from job_parent_groups import stars_of
    if p["part"] == "S":
        return {"rows": [{"members": [a, b], **analyse(stars_of(a[1], a[2]), stars_of(b[1], b[2]), 0)} for a, b in p["pairs"]]}
    q = p["pair"]
    (_, ga, ea, rnd), (_, gb, eb, _) = q["starts"]
    return {"rows": [{"kind": q["kind"], "starts": q["starts"], **analyse(stars_of(ga, ea), stars_of(gb, eb), rnd)}]}
