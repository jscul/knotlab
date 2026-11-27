"""Direct truth tables for the archived examples and the independent catalogue of closed boxes."""
import argparse
from collections import Counter
from functools import lru_cache
from itertools import product
import json
from pathlib import Path
import time

import numpy as np
from archive_check import HERE, PREV, closed_examples


class TruthTable:
    def __init__(self, supports):
        count = max(max(knot) for knot in supports) + 1
        self.states = np.arange(1 << count, dtype=np.uint32)
        self.all = (1 << len(self.states)) - 1
        self.equal = lru_cache(maxsize=None)(self._equal)
        laws = [self.all ^ self.equal(tuple(sorted(knot))) for knot in supports]
        prefix = [self.all]
        for good in laws:
            prefix.append(prefix[-1] & good)
        self.allowed = prefix[-1]
        self.exactly_one = []
        suffix = self.all
        for i in reversed(range(len(laws))):
            self.exactly_one.append(prefix[i] & suffix & ~laws[i])
            suffix &= laws[i]
        self.exactly_one.reverse()

    def _equal(self, places):
        mask = sum(1 << place for place in places)
        values = self.states & mask
        return int.from_bytes(np.packbits((values == 0) | (values == mask), bitorder="little").tobytes(), "little")

    def upper(self, box):
        bits = []
        for (a, va), (b, vb) in box:
            different = self.equal(a) ^ self.equal(b)
            bits.append(different if va == vb else self.all ^ different)
        states = []
        for word in product((0, 1), repeat=3):
            mask = self.all
            for reading, bit in zip(bits, word):
                mask &= reading if bit else ~reading
            states.append(mask)
        missing = [i for i, states_i in enumerate(states) if not self.allowed & states_i]
        lost = 0
        for word in missing:
            lost |= states[word]
        needed = [i for i, extra in enumerate(self.exactly_one) if extra & lost]
        return [format(word, "03b") for word in missing], needed

    def forbidden_states(self, signed):
        cell = self.allowed
        for carrier, sign in signed:
            mask = self.equal(carrier)
            cell &= mask if sign else ~mask
        return cell


def as_box(box):
    return tuple(tuple((tuple(sorted(c)), int(s)) for c, s in pair) for pair in box)


def audit_stage(supports, cut, boxes):
    closed = TruthTable(supports)
    ends = [i for i, knot in enumerate(supports) if cut in knot]
    opened = [knot.copy() for knot in supports]
    opened[ends[1]][opened[ends[1]].index(cut)] = 18
    cut_table = TruthTable(opened)
    lower = {}
    counts = Counter()
    for box in boxes:
        missing, needed = closed.upper(box)
        counts["boxes_checked"] += 1
        counts["closed_upper_misses_only_111"] += int(missing == ["111"])
        counts["all_source_laws_needed"] += int(len(needed) == 12)
        counts["single_source_deletions_restoring_111"] += len(needed) if missing == ["111"] else 0
        counts["all_18_distinctions_read"] += len({d for pair in box for carrier, _ in pair for d in carrier}) == 18
        cut_missing, _ = cut_table.upper(box)
        counts["old_upper_free_after_actual_cut"] += not cut_missing
        for triple in product(*box):
            signed = tuple(sorted(triple))
            if signed not in lower:
                assert not closed.forbidden_states(signed)
                lower[signed] = not cut_table.forbidden_states(signed)
    counts["distinct_lower_clauses_from_closed_boxes"] = len(lower)
    counts["same_lower_clauses_on_seeded_cut"] = sum(lower.values())
    # Break the bound-method cache's reference to its table.
    closed.equal.cache_clear()
    cut_table.equal.cache_clear()
    return counts


def read_post(archive, limit, catalogue):
    examples = {(file, n): row for file, n, row in closed_examples()}
    post = json.loads((PREV / "post/replay_box.json").read_text())
    order = [key for key, r in examples.items() if r["boxes"]]
    assert len(order) == len(post)
    all_results = []
    for r in archive["rows"][:limit]:
        key = r["closed_file"], r["line"]
        raw = examples[key]
        example = raw["example"][0]
        supports = r["closed_supports"]
        table = TruthTable(supports)
        missing, needed = table.upper(as_box(example["box"]))
        expectation = post[order.index(key)]
        ok = (raw["bonds"] == expectation["bonds"] and missing == example["upper missing"] == expectation["reported"]
              and needed == example["laws needed"] and len(needed) == expectation["knots needed"]
              and missing == ["".join(map(str, word)) for word in expectation["missing"]])
        assert ok
        entry = {"source": list(key), "post_matches": ok, "post_missing": missing, "post_needed": needed}
        if catalogue is None:
            entry.update(audit_stage(supports, r["seeded_link"], [as_box(example["box"])]))
        else:
            entry.update(audit_stage(supports, r["seeded_link"], catalogue[key]))
        all_results.append(entry)
    return all_results


def load_catalogue(path):
    archived = json.loads((HERE / "archive_counts.json").read_text())
    # The recount may index distinctions in the sorted list of links. Convert back to the
    # archived distinction identities by matching the pair of knots holding each one.
    by_source = {(a["closed_file"], a["line"]): a for a in archived["rows"]}
    output = {}
    for r in json.loads(path.read_text())["rows"]:
        if r["kind"] != "closed" or not r["boxes"]:
            continue
        key = tuple(r["source"])
        archive = by_source[key]
        def holders(knots):
            return [tuple(i for i, knot in enumerate(knots) if d in knot) for d in range(18)]
        own = holders(r["supports"])
        target = holders(archive["closed_supports"])
        assert set(own) == set(target) and key not in output
        ids = [target.index(ends) for ends in own]
        boxes = [as_box([[[[ids[d] for d in carrier], sign] for carrier, sign in pair] for pair in box])
                 for box in r["boxes"]]
        assert len(boxes) == archive["closed_boxes"]
        output[key] = boxes
    assert len(output) == len(archived["rows"])
    return output


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int, default=49)
    p.add_argument("--catalogue", type=Path)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    start = time.monotonic()
    counts = json.loads((HERE / "archive_counts.json").read_text())
    catalogue = load_catalogue(args.catalogue) if args.catalogue else None
    rows = read_post(counts, args.limit, catalogue)
    totals = Counter()
    for row in rows:
        totals.update({k: v for k, v in row.items() if isinstance(v, int)})
    out = {"scope": "all closed boxes" if catalogue else "first archived box per system",
           "totals": totals, "rows": rows, "elapsed_seconds": round(time.monotonic() - start, 4)}
    if args.output:
        args.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}))
