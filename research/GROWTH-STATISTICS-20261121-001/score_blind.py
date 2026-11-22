"""After release, join the sealed calls to the custodian's crosswalk."""

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path

from blind_reader import read_shape


def score(packet, calls, key):
    roots = [source for details in key.values() for source in details["roots"]]
    for panel, id_field, count in [("main", "main_id", 12), ("shape", "shape_id", 6)]:
        identifiers = [
            [row["id"] for row in packet[panel]],
            [row["id"] for row in calls[panel]],
            [row[id_field] for row in roots if id_field in row],
        ]
        if any(len(ids) != count or len(set(ids)) != count for ids in identifiers):
            raise ValueError(f"{panel} requires {count} uniquely identified rows in each input")
        if any(set(ids) != set(identifiers[0]) for ids in identifiers[1:]):
            raise ValueError(f"{panel} IDs differ between the packet, calls or key")
    main = {row["id"]: row for row in calls["main"]}
    shapes = {row["id"]: row for row in calls["shape"]}
    companion = {}
    for row in packet["shape"]:
        swapped = []
        for r, bond, meeting in row["scales"]:
            swapped.append([r, meeting, bond])
        companion[row["id"]] = read_shape(dict(id=row["id"], scales=swapped))["call"]
    labels = {"round-limit candidate": "pinwheel", "polygonal-limit candidate": "periodic"}
    rows = []
    totals = defaultdict(Counter)
    for family, details in key.items():
        for source in details["roots"]:
            row = main.pop(source["main_id"])
            target = source["target"]
            shape_id = source.get("shape_id")
            shape_call = shapes.pop(shape_id)["call"] if shape_id else None
            guessed = "inconclusive"
            if row["bounded"]:
                guessed = "bounded"
            elif row["cubic_arrangement"]:
                guessed = "cubic"
            elif row["dimension"] == 2 and shape_call in labels:
                guessed = labels[shape_call]
            verdict = "abstained" if guessed == "inconclusive" else ("correct" if guessed == family else "wrong")
            d_verdict = ("abstained" if row["dimension"] is None else
                         "correct" if row["dimension"] == target["meeting_dimension"] else "wrong")
            totals["combined"][verdict] += 1
            totals[family][verdict] += 1
            totals["dimension"][d_verdict] += 1
            if shape_id:
                for name, call in [("bond_shape", shape_call), ("meeting_shape", companion[shape_id])]:
                    result = "abstained" if call not in labels else "correct" if labels[call] == family else "wrong"
                    totals[name][result] += 1
            rows.append(dict(family=family, main_id=row["id"], shape_id=shape_id,
                             dimension=row["dimension"], dimension_key=target["meeting_dimension"],
                             exponent=row["exponent"], local=[row["local_hits"], row["local_total"]],
                             witnesses=row["witnesses"], main_call=row["call"], shape_call=shape_call,
                             meeting_shape=companion.get(shape_id), combined=guessed, verdict=verdict))
    if main or shapes or len(rows) != 12 or len(companion) != 6:
        raise ValueError("Every registered row must be scored exactly once")
    return dict(rows=rows, totals=dict(totals))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("packet", "calls", "key", "lock"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    digest = sha256(args.calls.read_bytes()).hexdigest()
    if args.lock.read_text().split()[0] != digest:
        raise SystemExit("Calls differ from the pre-release lock")
    result = score(*(json.loads(p.read_bytes()) for p in (args.packet, args.calls, args.key)))
    print(json.dumps(result, indent=2, sort_keys=True))
