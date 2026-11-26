"""Inspect actual inputs to the fresh-count laws on matched starting states."""
import argparse
from collections import Counter
import gzip
import json
from pathlib import Path
import random
import sys

STUDY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STUDY))
import hold


def keyset(name):
    with gzip.open(STUDY / (name + "_runs.jsonl.gz"), "rt") as stream:
        return {(r["A"], r["B"]) for r in map(json.loads, stream) if "law" in r}


def verify_frame():
    roster = hold.receivers.register()
    draw = random.Random(20261126).sample(roster, 100)
    extra = {"n3:g7:122@0", "n4:g15:2123@0"}
    base = {name for name, _, _ in draw}
    wanted = {(a, b) for a in base | extra for b in hold.receivers.SENDERS}
    census = keyset("hold")
    assert census == wanted
    previous = STUDY.parent / "LINKED-UNDER-CAP-20261126-001" / "linked_runs.jsonl.gz"
    far = set()
    with gzip.open(previous, "rt") as stream:
        for r in map(json.loads, stream):
            if r.get("law") == "CAP-3" and r["A"] == "tri:122@0" and r["linked"][15] is True:
                far.add(r["B"])
    linked = keyset("linked")
    assert linked == {("tri:122@0", b) for b in far}
    hold.bench.STARS["tri:122@0"], hold.bench.SITE["tri:122@0"] = hold.second.tri(1), 0
    return sorted(census) + sorted(linked), sorted(extra - base)


def audit(pairs):
    tally, example = Counter(), {}
    law = hold.eng.Law("ORD", "CANCEL-WAIT", None, "nae")
    forms = [hold.Hold(name) for name in ["INHERIT", "NET-OWING"]]
    differences = 0
    for a, b in pairs:
        stars, role = hold.bench.build(a, b, 3, join="meeting")
        state = hold.eng.from_stars(stars)
        record = hold.eng.play_round(state, law, hold.eng.Guard(4))
        differs = False
        for birth in record["births"]:
            kind, p, d = (birth[key] for key in ("kind", "p", "D"))
            # Algebraic definitions from the note, including the common floor.
            floor = max(3 - p, 1)
            inherit = max(floor, min(p, d))
            net = max(floor, d - p + 1)
            assert [inherit, net] == [f.fresh(kind, p, d, birth["o"]) for f in forms]
            assert birth["f"] == max(floor, d)
            item = (kind, p, d, inherit, net)
            tally[item] += 1
            differs |= inherit != net
            example.setdefault(item, dict(receiver=a, sender=b, birth=birth["id"], parents=birth["parents"]))
        differences += differs
    return dict(pairs=len(pairs), pairs_with_distinct_counts_in_first_round=differences,
                births=[dict(kind=k[0], p=k[1], D=k[2], inherit=k[3], net=k[4], count=n, example=example[k])
                        for k, n in sorted(tally.items())])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", type=int)
    args = parser.parse_args()
    pairs, extra = verify_frame()
    result = audit(pairs[:args.prefix])
    result["added_to_seeded_receivers"] = extra
    print(json.dumps(result, indent=2))
