"""Independent re-count of the contest trees and re-check of the leaves with the archived implementation.

For every start and shortfall the contested births are enumerated again with the archived `facts`/`pool`/`apply` (the
engine is not used for proposals or fresh counts), the distinct leaves and their numbers of choice sequences are compared
with `grow.py`, and for every leaf (or a seeded sample when there are more than 200) the births to the end of the fair
continuation are replayed through `apply`, the loose counts of every knot are compared, and every loss certificate is
re-read from the archived holdings. Firing completions are replayed through `apply` as well.

    timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file> [start ...]
"""
from collections import Counter
import json
import random
import sys
import time

import engine
import lib

ART = lib.ARTIFACTS


def recorded_key(cur, ns):
    owners = {}
    for k, s in enumerate(cur):
        for d in s:
            owners.setdefault(d, []).append(k)
    out = []
    for c in range(ns, len(cur)):
        ps = tuple(sorted({h for d in cur[c] for h in owners[d] if h < c}))
        out.append(("b", ps, len(cur[c]) - len(ps)))
    return tuple(sorted(out, key=repr))


def recorded_tree(stars, donor, policy, law):
    raw = lib.recorded()
    ns = len(stars)
    layer = {recorded_key(stars, ns): (tuple(stars), 1)}
    leaves = {}
    applies = 0
    while layer:
        nxt = {}
        for key, (cur, ways) in layer.items():
            _, loose, children, anc, byp, multi, unary = raw.facts(cur, ns)
            props = [g for g in multi if donor in g]
            if len(props) <= len(loose.get(donor, ())):
                leaves[key] = (cur, ways)
                continue
            for g in props:
                new, row = raw.apply(cur, ns, g, law)
                applies += 1
                k2 = recorded_key(new, ns)
                if k2 in nxt:
                    nxt[k2] = (nxt[k2][0], nxt[k2][1] + ways)
                else:
                    nxt[k2] = (new, ways)
        layer = nxt
    return leaves, applies


def replay_births(stars, births, law, policy):
    raw = lib.recorded()
    ns = len(stars)
    cur = tuple(stars)
    for parents, child, fresh in births:
        _, loose, children, anc, byp, multi, unary = raw.facts(cur, ns)
        assert tuple(parents) in raw.pool(multi, unary, policy), ("not enabled", parents)
        cur, row = raw.apply(cur, ns, tuple(parents), law)
        assert len(row["fresh"]) == fresh and len(cur) - 1 == child
    return cur


def holdings(cur, ns):
    raw = lib.recorded()
    _, loose, children, anc, byp, multi, unary = raw.facts(cur, ns)
    return loose, byp


def check_leaf(joint, leaf, policy, law, rng):
    out, fair_written = lib.classify_leaf(leaf, policy)
    fair = leaf.copy()
    lib.fair_complete_donor(fair, policy)
    ns = len(joint.stars)
    cur = replay_births(joint.stars, fair.P.log, law, policy)
    loose, byp = holdings(cur, ns)
    assert [len(loose.get(k, ())) for k in range(len(cur))] == fair.P.loose, "loose counts differ"
    checked = Counter()
    for i, row in enumerate(out):
        src = joint.srcs[i]
        for age, e in row.items():
            if e["status"] == "lost":
                c = fair.lost(i, age)
                k = c["parent_knot"]
                assert not loose.get(k), "certificate parent still holds loose distinctions"
                if None not in c["role_parents_present"]:
                    assert tuple(sorted(c["role_parents_present"])) not in byp, "required birth exists"
                checked["lost certificates re-read"] += 1
            elif e["status"] == "made" and e.get("how") == "firing completion found":
                base = len(joint.stars) + len(leaf.P.log)
                extra = [(tuple(kk), base + n, f) for n, (r, kk, f) in enumerate(e["completion_births"])]
                cur2 = replay_births(joint.stars, list(leaf.P.log) + extra, law, policy)
                loose2, byp2 = holdings(cur2, ns)
                t = leaf.copy()
                for r, kk, f in e["completion_births"]:
                    t.spend(tuple(kk), f)
                tick_parents = src.roles[src.ticks[age]][0]
                key = tuple(sorted(t.real[i][p] for p in tick_parents))
                assert key in byp2, "tick birth missing in archived holdings"
                checked["firing completions replayed"] += 1
    return checked


def main(names):
    from addendum import SPECS
    S = lib.ring_sources()
    report = {"starts": {}}
    rng = random.Random(lib.SEED)
    for name, label, xk, yk, needs_repair in SPECS:
        if names and name not in names:
            continue
        repair = {}
        if needs_repair:
            unf = lib.merge(name, S[xk], S[yk], 0)
            _, _, _, sc = engine.ordinary_layer(engine.Pres.from_stars(unf.stars))
            repair = {int(k): int(n) for k, n in sc}
        report["starts"][name] = {}
        for s in (0, 1):
            for law in lib.LAWS:
                for policy in lib.POLICIES:
                    if law == "nae" and policy == "joins_first":
                        continue
                    t0 = time.time()
                    j = lib.merge(f"{name}-s{s}", S[xk], S[yk], s, repair)
                    mine, nodes = lib.contest_leaves(j, policy)
                    mine_keys = {k: w for k, (_, w, _) in mine.items()}
                    theirs, applies = recorded_tree(j.stars, j.donor, policy, law)
                    theirs_keys = {k: w for k, (_, w) in theirs.items()}
                    assert mine_keys == theirs_keys, f"{name} s{s} {law} {policy}: contest trees differ"
                    keys = sorted(mine, key=repr)
                    sample = keys if len(keys) <= 200 else rng.sample(keys, 200)
                    tally = Counter()
                    for k in sample:
                        tally += check_leaf(j, mine[k][0], policy, law, rng)
                    report["starts"][name][f"s{s} {law} {policy}"] = {
                        "choice_sequences": sum(mine_keys.values()), "distinct_leaves": len(mine_keys),
                        "archived_applies": applies, "trees_identical": True, "leaves_checked": len(sample),
                        "checks": dict(tally), "seconds": round(time.time() - t0, 1)}
                    print(name, s, law, policy, report["starts"][name][f"s{s} {law} {policy}"], flush=True)
    out = ART / ("verify_" + "_".join(sorted(names)) + ".json" if names else "verify.json")
    out.write_text(json.dumps(report, indent=1, sort_keys=True) + "\n")


if __name__ == "__main__":
    main(set(sys.argv[1:]))
