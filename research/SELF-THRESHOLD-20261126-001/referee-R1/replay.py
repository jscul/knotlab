"""Replay named pair records from scratch and inspect allocation choices at individual births."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from time import process_time

from archive import HERE, draws, panel
from growth import Growth, first_hearing
from starts import build_pair


def alternative_counts(birth):
    floor = max(3 - birth.p, 1)
    ordinary = max(floor, birth.D)
    return {
        "HALF": max(floor, min(ordinary, (birth.D + 1) // 2 + 1)),
        "PLACES": max(floor, min(ordinary, birth.p + 1)),
        "CAP-3": max(floor, min(ordinary, 3)),
        "ORD": ordinary,
    }


def describe(birth):
    return [birth.kind, birth.p, birth.D, birth.f]


def trace(rounds, start, comparison):
    """Differences from another prescription on this trajectory, with first-birth evidence."""
    size = 0
    differences = Counter()
    first = None
    digest = sha256()
    for ix in range(start, len(rounds)):
        row = rounds[ix]
        size += len(row.births)
        for b in row.births:
            # Birth and parent IDs identify the full ordered, deterministic construction on a fixed start.
            digest.update(repr((ix + 1, b.knot, b.parents, b.kind, b.p, b.D, b.f)).encode())
            if comparison:
                other = alternative_counts(b)[comparison]
                if other != b.f:
                    typ = (b.kind, b.p, b.D, b.f, other)
                    differences[typ] += 1
                    if first is None:
                        first = {"round": ix + 1, "knot": b.knot, "parents": b.parents, "type": typ}
    return {"births":size, "digest":digest.hexdigest(), "first":first,
            "types":[[*typ, count] for typ, count in sorted(differences.items())]}


def check_pair(panel_name, pair, laws):
    start = process_time()
    a,b = pair
    saved = panel(panel_name)[tuple(pair)]
    edits, rounds, bound = (([3, 5, 8], 24, 6000) if panel_name == "linked"
                            else ([1, 2, 3], 12, 1500))
    result = {}
    for law in laws:
        s = process_time()
        g = Growth(*build_pair(a,b), law=law).run(rounds, bound)
        other = {"HALF":"CAP-3", "PLACES":"CAP-3", "CAP-3":"PLACES"}.get(law)
        row = {"A":a, "B":b, "law":law, "rounds":len(g.rounds), "ended":g.stop,
               "made short":[x.made_short for x in g.rounds],
               "births":[len(x.births) for x in g.rounds],
               "linked":[g.linked(t) for t in range(1, len(g.rounds)+1)], "changes":[]}
        bindings = Counter()
        for turn in g.rounds:
            for birth in turn.births:
                if birth.f < max(3 - birth.p, 1, birth.D):
                    bindings[birth.kind] += 1
        row["binds on the growth with no change"] = dict(bindings) if law in {
            "HALF", "PLACES", "PLACES-JOINS", "PLACES-OFFSHOOTS", "CAP3-JOINS"} else {}
        details = {"baseline":trace(g.rounds, 0, other), "changes":[]}
        for t in edits:
            if len(g.rounds) <= t or row["linked"][t-1] is None:
                continue
            for want, limit in [(True,5), (False,2)]:
                for m in g.mark_candidates(t, want)[:limit]:
                    h = g.fork(t)
                    h.mark(m.knot)
                    h.run(rounds, bound)
                    hit = first_hearing(g,h,t)
                    end = min(len(g.rounds),len(h.rounds))
                    row["changes"].append({"t0":t, "linked":want, "sharings":m.sharings,
                        "heard":hit, "rounds":end, "births with":
                        [len(x.births) for x in h.rounds] if hit is not None else None})
                    info = {"after":t, "knot":m.knot, "linked":want, "sharings":m.sharings,
                            "heard":hit,"end":end,"changed_end":len(h.rounds),
                            "post_mark":trace(h.rounds, t, other)}
                    if hit is not None:
                        info["own_at_hearing"] = [len(v.rounds[hit-1].receiver_signature) for v in (g,h)]
                    details["changes"].append(info)
        expected = saved[law]
        difference = {k:{"rebuilt":row[k],"archive":expected[k]} for k in row if row[k]!=expected[k]}
        assert set(expected)==set(row), (expected.keys(), row.keys())
        details.update({"differences":difference, "seconds":round(process_time()-s,3)})
        result[law] = details
    return {"panel":panel_name, "pair":pair,"laws":result,"cpu_seconds":round(process_time()-start,3)}


def selected(name):
    d = draws(name)
    return list(dict.fromkeys(d["uniform"] + d["targeted"]))


if __name__ == "__main__":
    arg = argparse.ArgumentParser()
    arg.add_argument("name", choices=["linked","census"])
    arg.add_argument("start", type=int)
    arg.add_argument("stop", type=int)
    arg.add_argument("--laws", default="HALF,PLACES,CAP-3")
    opts = arg.parse_args()
    cases = selected(opts.name)
    for pair in cases[opts.start:opts.stop]:
        print(json.dumps(check_pair(opts.name, pair, opts.laws.split(","))), flush=True)
