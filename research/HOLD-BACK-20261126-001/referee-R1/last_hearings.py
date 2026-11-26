"""Continue every cap first hearing without a later recorded birth in both runs."""
import argparse
from collections import Counter
import json
from itertools import islice
from pathlib import Path
import sys

from archive import records

STUDY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STUDY))
import hold


def unfinished():
    for row in records(STUDY / "linked_runs.jsonl.gz"):
        for i, change in enumerate(row["changes"]):
            h = change["heard"]
            if h and not (any(row["births"][h:]) and any(change["births with"][h:])):
                yield row, i


def continuation(row, i):
    c = row["changes"][i]
    t, h = c["t0"], c["heard"]
    assert row["law"][0] == "CAP-3" and h == c["rounds"]
    law = hold.eng.Law("CAP-3", "CANCEL-WAIT", None, "nae")
    stars, roles = hold.bench.build(row["A"], row["B"], 3, join="meeting")
    baseline = hold.ring_line.Growth(stars, roles, law)
    baseline.run(t, 6000)
    ranked, distance = hold.linked.far_members(baseline, t, c["linked"])
    rank = sum((e["t0"], e["linked"]) == (t, c["linked"]) for e in row["changes"][:i])
    knot = ranked[rank]
    assert distance[knot] == c["sharings"]

    # Share the catalogue of exact receiver birth identities between the two runs.
    # Each name consists of the kind, the parents' names and its sibling index.
    startnames = {u: u for u, role in enumerate(roles) if role == "A"}
    names = {}
    def run(changed):
        state = hold.eng.from_stars(stars)
        own = startnames.copy()
        own_history, counts, sizes = [], [], []
        guard = hold.eng.Guard(4)
        for rnd in range(1, h + 2):
            if changed and rnd == t + 1:
                new = len(state.holders)
                state.holders.append([knot])
                state.places[knot].append(new)
                state.maker.append(knot)
                state.barred.append(False)
            result = hold.eng.play_round(state, law, guard)
            signatures = []
            sibling = Counter()
            for b in result["births"]:
                if all(p in own for p in b["parents"]):
                    family = b["kind"], tuple(sorted(own[p] for p in b["parents"]))
                    identity = (*family, sibling[family])
                    sibling[family] += 1
                    own[b["id"]] = names.setdefault(identity, len(startnames) + len(names))
                    signatures.append((own[b["id"]], b["f"], len(state.places[b["id"]])))
            own_history.append(sorted(signatures))
            counts.append(len(result["births"]))
            sizes.append(state.n_knots)
        return own_history, counts, sizes
    w, b, n = run(False)
    x, k, m = run(True)
    assert b == row["births"][:h + 1] and k[:h] == c["births with"]
    assert w[:h-1] == x[:h-1] and w[h-1] != x[h-1]
    return dict(receiver=row["A"], sender=row["B"], addition_after=t, member=knot,
                sharings=distance[knot], first_heard=h, old_knot_limit=6000,
                knots_after_hearing=[n[h-1], m[h-1]], next_round=h+1,
                next_round_births=[b[h], k[h]])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip", type=int, default=0)
    parser.add_argument("--limit", type=int, default=3)
    args = parser.parse_args()
    hold.bench.MULT = 4
    hold.receivers.register()
    hold.bench.STARS["tri:122@0"], hold.bench.SITE["tri:122@0"] = hold.second.tri(1), 0
    for row, i in islice(unfinished(), args.skip, args.skip + args.limit):
        print(json.dumps(continuation(row, i)), flush=True)
