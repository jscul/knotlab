"""Regrow the live-roster examples and enumerate joint states using bit sets.

The small-stage pass compares every saved exact pair reading on stages of at
most 20 distinctions with a fresh enumeration. The focused cases add the
smallest reversals, a sign exception and a history-weighting exception.
"""

import argparse
import gzip
import itertools
import json
import math
import operator
import resource
import sys
import time
from collections import Counter
from contextlib import redirect_stdout
from fractions import Fraction
from functools import lru_cache, reduce
from io import StringIO
from pathlib import Path

from end_recount import FAMILY, HERE, LAWS, ROOT, TICKET, counts
from regrow_engine import Growth


# Each number is a file index in the catalogue; the output includes the start.
FOCUS = {
    "L0": {157, 480, 1089, 1403},
    "L1": {133, 157, 1409},
    "L6": {157, 480, 865},
    "L7": {157, 480},
}


@lru_cache(maxsize=6)
def columns(n):
    size = max(1, (1 << n) // 8)
    out = []
    for bit in range(n):
        if bit < 3:
            period = bytes([sum(1 << i for i in range(8) if i & (1 << bit))])
        else:
            block = 1 << (bit-3)
            period = bytes(block) + bytes([255]) * block
        out.append(int.from_bytes(period*(size//len(period)), "little"))
    return out


def allowed(places, n):
    col = columns(n)
    universe = (1 << (1 << n))-1
    valid = universe
    for knot in places:
        zeros = universe ^ reduce(operator.or_, (col[i] for i in knot))
        ones = reduce(operator.and_, (col[i] for i in knot))
        valid &= universe ^ (zeros | ones)
    return valid


def local_relation(valid, places, col):
    parts = [valid]
    for d in places:
        parts = [m for p in parts for m in (p & ~col[d], p & col[d])]
    return tuple(i for i, mask in enumerate(parts) if mask)


def verdict(states, arity):
    k1 = len(states) < 2**arity
    k2 = all(len({(s >> (i+1)) << i | (s & ((1 << i)-1)) for s in states})
             == 2**(arity-1) for i in range(arity))
    return k1, k2, bool(states)


@lru_cache(maxsize=None)
def canonical_check(local, arity):
    """Use the canonical check entry point on the exact projected relation."""
    tools_path = str(ROOT / "tools")
    if tools_path not in sys.path:
        sys.path.insert(0, tools_path)
    from knotlab.cli import main
    names = [f"d{i}" for i in range(arity)]
    clauses = []
    for assignment in set(range(2**arity)).difference(local):
        clauses.append(" ".join(("~" if assignment & 1 << (arity-1-i) else "")+v
                                for i,v in enumerate(names)))
    args = ["check", "--cnf", ";".join(clauses), "--loops", *names[:-1],
            "--contact", names[-1], "--json"]
    output = StringIO()
    with redirect_stdout(output):
        code = main(args)
    report = json.loads(output.getvalue())
    assert code == 0 and report["is_knot"] == all(verdict(local, arity))
    return report["is_knot"]


def steps(neighbors, source):
    dist = {source: 0}
    queue = [source]
    for u in queue:
        for v in neighbors[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                queue.append(v)
    return dist


def delays(growth, members, target_pairs, horizon=6):
    ancestry = {u: {u} for u in members}
    found = {}
    for d in range(1, horizon+1):
        start = len(growth.places)
        if not growth.step():
            break
        for child in range(start, len(growth.places)):
            origins = set().union(*(ancestry.get(parent, set()) for parent in growth.parents[child]))
            ancestry[child] = origins
            for p in itertools.combinations(sorted(origins), 2):
                if p in target_pairs:
                    found.setdefault(p, d)
        if len(found) == len(target_pairs):
            break
    return found


def gamma_numer(gu, gv, valid):
    uz, uo = gu
    vz, vo = gv
    return ((valid & uz & vz).bit_count() + (valid & uo & vo).bit_count()
            - (valid & uz & vo).bit_count() - (valid & uo & vz).bit_count())


def uniform_start_extensions(start_stars, valid, n):
    """Array of allowed bit assignments grouped by their start assignment."""
    import numpy as np

    old = max(max(places) for places in start_stars) + 1
    mask = np.unpackbits(np.frombuffer(valid.to_bytes((1 << n)//8, "little"),
                                      dtype=np.uint8), bitorder="little").reshape(-1, 1 << old)
    sizes = mask.sum(axis=0)
    prior = allowed(start_stars, old).bit_count()
    assert (sizes > 0).sum() == prior
    return sizes, prior


def history_rho(diff, valid, n, sizes, prior):
    import numpy as np

    hits = np.unpackbits(np.frombuffer((diff & valid).to_bytes((1 << n)//8, "little"),
                                      dtype=np.uint8), bitorder="little").reshape(-1, len(sizes)).sum(axis=0)
    return sum((Fraction(int(hits[sizes == k].sum()), int(k)) for k in set(sizes) if k),
               Fraction()) / prior


def permuted_s(pairs, parts):
    """Shuffle every member in each part and retain only the decided keys."""
    permuted = {}
    for field in ("kappa","gamma"):
        distribution = Counter()
        for choices in itertools.product(*(itertools.permutations(part) for part in parts)):
            renaming = dict(itertools.chain.from_iterable(
                zip(a,b,strict=True) for a,b in zip(parts,choices,strict=True)))
            pts = []
            for (u,v), row in pairs.items():
                y = pairs[tuple(sorted((renaming[u],renaming[v])))].get("delta")
                if isinstance(y,int):
                    pts.append((abs(row[field]), y))
            c,d,_ = counts(pts)
            distribution[c-d] += 1
        n = sum(distribution.values())
        mean = Fraction(sum(s * ct for s,ct in distribution.items()), n)
        var = sum((s-mean)**2 * ct for s,ct in distribution.items())/n
        permuted[field] = dict(mean=str(mean), variance=str(var), permutations=n,
                               S_distribution=dict(sorted(distribution.items())))
    return permuted


def small_table(g, rec, stat, focus, start_stars):
    n = len(g.holders)
    z_mask = allowed(g.places, n)
    z = z_mask.bit_count()
    cols = columns(n)
    assert z == int(rec["Z"]) and len(g.places) == rec["knots"] and n == rec["distinctions"]
    assert set(g.members) == set(itertools.chain.from_iterable(rec["parts"]))
    stat["stages"] += 1
    stat["assignments_enumerated"] += 2**n
    stat["maximum_distinctions"] = max(stat["maximum_distinctions"], n)
    if rec["round"] != 1 and focus:
        raise ValueError("The focused history calculation uses one complete round")
    relation_rows = []
    for knot, places in enumerate(g.places):
        rel = local_relation(z_mask, places, cols)
        ok = all(verdict(rel,len(places)))
        assert ok == canonical_check(rel,len(places))
        stat["knot_projections"] += 1
        stat["failed_knots"] += not ok
        if focus:
            relation_rows.append(dict(knot=knot, places=places, allowed_states=len(rel), K1_K2_K3=ok))
    stage_roster = g.roster()
    terms = {}
    for u in g.members:
        shared = [d for d in g.places[u] if len(g.holders[d]) > 1]
        terms[u] = (~reduce(operator.or_, (cols[d] for d in shared)),
                    reduce(operator.and_, (cols[d] for d in shared)))
    pairs = {}
    prior = None
    if focus and n <= 20:
        sizes, prior = uniform_start_extensions(start_stars, z_mask, n)
    for row in rec["pairs"]:
        if row["part"] is None:
            continue
        u,v = row["u"], row["v"]
        loose_u = [d for d in g.places[u] if len(g.holders[d]) == 1]
        loose_v = [d for d in g.places[v] if len(g.holders[d]) == 1]
        assert row["lam"] == [len(loose_u),len(loose_v)]
        assert row["sig"] == [len(g.places[u])-len(loose_u),len(g.places[v])-len(loose_v)]
        values = {((cols[a] ^ cols[b]) & z_mask).bit_count() for a,b in itertools.product(loose_u,loose_v)}
        assert values == {int(row["N"])}
        gamma_z = gamma_numer(terms[u],terms[v],z_mask)
        assert gamma_z == int(row["gZ"])
        stat["member_pairs"] += 1
        stat["loose_distinction_pairs"] += len(loose_u)*len(loose_v)
        if focus:
            ws = steps(stage_roster.neighbors,u)[v]
            hs = steps(g.meeting,u)[v]
            assert ws == row["ws"] and hs == row["hs"]
            info = dict(u=u, v=v, loose=row["lam"], shared=row["sig"], N=int(row["N"]),
                        kappa=Fraction(z-2*int(row["N"]),z), gamma=Fraction(gamma_z,z),
                        delta=row["delta"], ws=ws, hs=hs)
            if prior is not None:
                hist = history_rho(cols[loose_u[0]] ^ cols[loose_v[0]],z_mask,n,sizes,prior)
                assert hist == Fraction(rec["small"]["history_rho"][f"{u},{v}"])
                info["history_kappa"] = str(1-2*hist)
            pairs[u,v] = info
    if not focus:
        return None
    places = [list(p) for p in g.places]
    members = list(g.members)
    horizons = delays(g, members, set(pairs))
    for pair, row in pairs.items():
        assert horizons.get(pair) == (row["delta"] if isinstance(row["delta"], int) else None)
    shuffle = permuted_s(pairs,rec["parts"])
    for field, s in shuffle.items():
        archived = rec["shuffle"].get(field)
        if archived:
            assert math.isclose(float(Fraction(s["mean"])), archived["mean"], abs_tol=1e-9)
            assert math.isclose(float(Fraction(s["variance"])), archived["var"], abs_tol=1e-9)
    return dict(start=start_stars, round=rec["round"], places=places, members=members,
                parts=rec["parts"], assignments=2**n, allowed=z, projected_relations=relation_rows,
                pairs=list(pairs.values()), shuffle=shuffle)


def replay(limit, focus_only):
    starts = json.loads((ROOT/"research"/TICKET/"census_starts.json").read_text())
    tally = {}
    focused = {}
    for law in LAWS:
        tally[law] = Counter()
        focused[law] = {}
        with gzip.open(FAMILY/f"run5_{law}.jsonl.gz","rt") as f:
            for raw in itertools.islice(f, limit):
                row = json.loads(raw)
                idx = row["index"]
                chosen = set()
                if not focus_only:
                    chosen.update(s["round"] for s in row["stages"]
                                  if s["status"] == "computed" and s["distinctions"] <= 20)
                if idx in FOCUS.get(law, set()):
                    chosen.add(1)
                if not chosen:
                    continue
                stars = starts[idx]["stars"]
                growth = Growth(stars,law)
                for s in row["stages"]:
                    if s["round"] > max(chosen):
                        break
                    assert growth.step() > 0
                    if s["round"] not in chosen:
                        continue
                    s_focus = s["round"] == 1 and idx in FOCUS.get(law,set())
                    # A focused replay also grows beyond its stage to read arrival.
                    if s_focus:
                        rerun = Growth(stars,law)
                        rerun.step()
                        focused[law][idx] = small_table(rerun,s,tally[law],True,stars)
                    else:
                        small_table(growth,s,tally[law],False,stars)
    # A three-place relation that forces its first distinction fails forgetting.
    malformed = (0,1,2,3)
    assert not canonical_check(malformed,3)
    return dict(checked=tally, focused=focused, control_restricting_one_distinction="rejected",
                canonical_relations_checked=canonical_check.cache_info().currsize)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--limit", type=int, help="prefix of recorded starts per law")
    ap.add_argument("--focus-only", action="store_true")
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(2_300_000_000,2_300_000_000))
    tic = time.monotonic()
    answer = replay(args.limit,args.focus_only)
    answer.update(limit_per_law=args.limit, focus_only=args.focus_only, seconds=time.monotonic()-tic,
                  peak_rss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    args.output.write_text(json.dumps(answer,indent=2,sort_keys=True,default=str)+"\n")
