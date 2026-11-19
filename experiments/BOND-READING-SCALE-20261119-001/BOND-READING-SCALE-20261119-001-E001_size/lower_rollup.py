"""Summarize completed lower shards and attach literal minimum witnesses."""

import argparse
from collections import Counter, defaultdict
import gzip
import json
from pathlib import Path
import sys

from lower import EXTEND_ROUND, ROOT, Arrangement, bond_readings, classify, indices, next_stage


def read_shards(path):
    if path.is_dir():
        raw = [json.loads(line) for line in (path / "results.jsonl").read_text().splitlines()]
        final = {row["case"]: row for row in raw}
        for row in final.values():
            if row["status"] == "ok":
                yield row["result"]
        return
    if path.suffix == ".gz":
        with gzip.open(path, "rt") as file:
            yield from json.load(file)["rows"]
    else:
        yield from json.loads(path.read_text())["rows"]


def later_marks(record):
    stage = Arrangement.parse(record["current"])
    successor = next_stage(stage)
    _, bonds, _ = bond_readings(successor)
    mark = record["any_arity"]["bond"]
    image = record["any_arity"]["image_outside_the_old_span"]

    def minimum(xs):
        selected = sum(successor.label_bits[x] for x in xs)
        return min((b.bit_count() for b in bonds if b & selected == selected), default=None)

    assert minimum(mark) == len(mark) and (minimum(image) is None or minimum(image) > len(image))
    return record | {"literal_next": [sorted(s) for s in successor.stars],
                     "later_arbitrary_mark_K": [minimum(mark), minimum(image)],
                     "later_image_bond": next(([successor.labels[i] for i in indices(word)] for word in bonds
                                               if word.bit_count() == minimum(image) and
                                               set(image) <= {successor.labels[i] for i in indices(word)}), None)}


def summarize(shards, recheck):
    dimensions = defaultdict(Counter)
    groups = defaultdict(Counter)
    outcomes = defaultdict(dict)
    rechecked = 0
    material = []
    for shard in shards:
        mode, order, ordinary = shard["mode"], shard["order"], shard["ordinary_junctions"]
        for w, stats in shard["widths"].items():
            dimensions[order, mode, ordinary, int(w)].update(stats)
        residual = []
        for rec in shard["residual"]:
            if recheck and mode == "native" and rec["maps_by_outcome"].get("next_pair_extends_lifetime_open"):
                rec = classify(rec["witness"]["rooted_allocation"], order, mode)
                rechecked += 1
            width, multiplicity = rec["current_width"], rec["max_ordinary_meeting_multiplicity"]
            key = (order, mode, width, ordinary, multiplicity)
            groups[key].update(rec["maps_by_outcome"])
            if "witness" in rec:
                for outcome, count in rec["maps_by_outcome"].items():
                    if count and outcome not in ("maps", "equations"):
                        outcomes[outcome].setdefault(key, rec["witness"])
            residual.append(rec)
        material.append(shard | {"residual": residual})

    least = {}
    for outcome, records in outcomes.items():
        least[outcome] = {}
        for regime, cap in [("meet_once", 1), ("meet_twice_allowed", 2), ("unrestricted", float("inf"))]:
            native = [key for key in records if key[:2] == (2, "native") and key[-1] <= cap]
            if not native:
                continue
            low_width = min(native, key=lambda key: key[2:])
            low_junctions = min(native, key=lambda key: (key[3], key[2], key[4]))
            proof = records[low_width]
            if outcome == "changes_equations":
                proof = later_marks(proof)
            least[outcome][regime] = {"min_width_key": low_width, "min_junctions_key": low_junctions,
                                      "witness_at_min_width": proof}
    digest = {"population_columns": ["order", "mode", "ordinary_junctions", "width"],
              "residual_columns": ["order", "mode", "width", "ordinary_junctions", "max_ordinary_multiplicity"],
              "population": [[key, data] for key, data in sorted(dimensions.items())],
              "maps": [[key, data] for key, data in sorted(groups.items())],
              "least_observed": least, "literal_rows_rechecked_for_lifetime": rechecked,
              "completed_shards": [[s["mode"], s["order"], s["ordinary_junctions"], *s["partition"],
                                    sorted(map(int, s["widths"]))] for s in material]}
    return digest, material


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("sources", nargs="+", type=Path)
    p.add_argument("--recheck-lifetime", action="store_true")
    p.add_argument("--raw-output", type=Path)
    args = p.parse_args()
    sys.path.insert(0, str(ROOT / "experiments" / EXTEND_ROUND))
    result, rows = summarize((r for p in args.sources for r in read_shards(p)), args.recheck_lifetime)
    if args.raw_output:
        with gzip.open(args.raw_output, "wt") as handle:
            json.dump({"rows": rows}, handle, separators=(",", ":"))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
