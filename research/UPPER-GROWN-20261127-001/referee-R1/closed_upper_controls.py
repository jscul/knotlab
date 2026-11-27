"""Check the complete box list by direct assignments, including lower-bond controls."""

import argparse
from collections import Counter, defaultdict
from itertools import product
import json
from pathlib import Path
import resource
import time

import numpy as np

from closed_recount import adjacency, boxes_from_clauses, breadth_first_key, breadth_first_keys


SIX_WORDS = tuple(product((0, 1), repeat=6))
CHOICES = tuple(product((0, 1), (2, 3), (4, 5)))
LOWER_CONJUNCTION = {word for word in SIX_WORDS if any(word[p:p + 2] == (0, 0) for p in (0, 2, 4))}
UPPER = tuple(tuple(word[p] ^ word[p + 1] for p in (0, 2, 4)) for word in SIX_WORDS)
UPPER_CODES = np.array([4 * a + 2 * b + c for a, b, c in UPPER], dtype=np.uint8)


def state_table(raw_distinctions, supports):
    assignments = np.arange(1 << raw_distinctions, dtype=np.uint32)
    distinctions = ((assignments >> np.arange(raw_distinctions, dtype=np.uint32)[:, None]) & 1).astype(np.uint8)
    fails = []
    for a, b, c in supports:
        fails.append((distinctions[a] == distinctions[b]) & (distinctions[b] == distinctions[c]))
    fails = np.array(fails)
    num_fails = fails.sum(axis=0)
    keep = num_fails <= 1
    return distinctions[:, keep], num_fails[keep] == 0, fails[:, keep]


def bit_words(projected):
    codes = np.zeros(projected.shape[1], dtype=np.uint8)
    for row in projected:
        codes = (codes << 1) | row
    return codes


def is_read(column, words):
    return len(np.unique((words << 1) | column)) == len(np.unique(words))


def equality_obstruction(carriers, supports):
    """Determine whether contracting equality makes the binary laws contradictory."""
    rename = {item: carrier[0] for carrier in carriers for item in carrier}
    opposite = defaultdict(set)
    for source in supports:
        reduced = {rename.get(x, x) for x in source}
        if len(reduced) == 1:
            return "constant law"
        if len(reduced) == 2:
            a, b = reduced
            opposite[a].add(b)
            opposite[b].add(a)
    seen = {}
    for root in opposite:
        if root in seen:
            continue
        seen[root] = 0
        queue = [root]
        for a in queue:
            for b in opposite[a]:
                if b not in seen:
                    seen[b] = seen[a] ^ 1
                    queue.append(b)
                if seen[b] == seen[a]:
                    return "odd inequality cycle"
    return "binary laws satisfiable"


def product_controls():
    carriers = [(2 * i, 2 * i + 1) for i in range(6)]
    pairs = ((1, 10), (2, 9), (5, 6))
    corners = [tuple(sorted(corner)) for corner in product(*pairs)]
    assert boxes_from_clauses(carriers, corners) == [pairs]
    overlap = carriers[:]
    overlap[-1] = (0, 11)
    assert not boxes_from_clauses(overlap, corners)
    assert len(LOWER_CONJUNCTION) == 37
    assert {UPPER[SIX_WORDS.index(w)] for w in LOWER_CONJUNCTION} == set(product((0, 1), repeat=3)) - {(1, 1, 1)}
    for i, omitted in enumerate(CHOICES):
        assert not boxes_from_clauses(carriers, corners[:i] + corners[i + 1:])
        admitted = [w for w in SIX_WORDS if all(not all(w[p] for p in c) for c in CHOICES if c != omitted)]
        assert {UPPER[SIX_WORDS.index(w)] for w in admitted} == set(product((0, 1), repeat=3))
    return {"mixed_sign_box": 1, "box_remains_after_lower_clause_deletion": 0,
            "lower_clause_deletions_restoring_upper_111": 8, "box_remains_with_carrier_overlap": 0}


def previous_witness(systems):
    previous = Path(__file__).resolve().parents[2] / "RING-BOND-20261127-001" / "referee-R1" / "layer_witness.json"
    original = json.loads(previous.read_text())
    supports = original["source_knots_not_all_equal"]
    by_distinction = defaultdict(list)
    for i, support in enumerate(supports):
        for place in support:
            by_distinction[place].append(i)
    witness_labels = set(breadth_first_keys(adjacency(len(supports), by_distinction.values())))
    matches = []
    for row in systems:
        if breadth_first_key(adjacency(row["knots"], row["links"])) in witness_labels:
            assert row["allowed_states"] == original["allowed_source_states"]
            matches.append({name: row[name] for name in ("file", "line", "archive_index", "boxes", "allowed_states")})
    assert len(matches) <= 1
    return matches


def controls(row):
    supports = row["supports"]
    distinctions, allowed, break_one = state_table(row["distinctions"], supports)
    assert int(allowed.sum()) == row["allowed_states"]
    read = {}
    laws = [bit_words(distinctions[np.asarray(knot)][:, allowed]) for knot in supports]
    lower_bonds = set()
    upper_images = Counter()
    lower_image_sizes = Counter()
    signs = Counter()
    carrier_sizes = Counter()
    repeated_at_source = Counter()
    restored_counts = Counter()
    disagreements = []
    for entry in row["all_upper"]:
        box = entry["carriers_and_missing_values"]
        places = [x for pair in box for carrier, _ in pair for x in carrier]
        assert len(places) == len(set(places))
        six = np.empty((6, distinctions.shape[1]), dtype=np.uint8)
        readings = [(tuple(carrier), v) for pair in box for carrier, v in pair]
        signs["".join(str(v) for _, v in readings)] += 1
        carrier_sizes["".join(map(str, sorted(len(carrier) for carrier, _ in readings)))] += 1
        group = {x: i for i, (carrier, _) in enumerate(readings) for x in carrier}
        repeats = sum(len({group.get(x, x + 6) for x in law}) < len(law) for law in supports)
        repeated_at_source[repeats] += 1
        for i, (carrier, missing_value) in enumerate(readings):
            if carrier not in read:
                raw = distinctions[np.array(carrier)]
                value = np.all(raw == raw[0], axis=0).astype(np.uint8)
                assert not any(is_read(value[allowed], law) for law in laws)
                for omitted in range(len(carrier)):
                    kept = np.delete(raw[:, allowed], omitted, axis=0)
                    assert not is_read(value[allowed], bit_words(kept))
                read[carrier] = value
            six[i] = read[carrier] == missing_value

        words = bit_words(six)
        upper = UPPER_CODES[words]
        counts = np.bincount(upper[allowed], minlength=8)
        upper_missing = np.flatnonzero(counts == 0)
        restores = (break_one & np.isin(upper, upper_missing)[None, :]).sum(axis=1)
        restored_counts.update(map(int, restores))
        if counts.tolist() != entry["words"] or restores.tolist() != entry["restored_assignments_by_deleted_law"]:
            disagreements.append({"box": box, "projection_or_deletion": True})
        if len(upper_missing) != 1:
            disagreements.append({"box": box, "missing": upper_missing.tolist()})
        else:
            upper_images[f"{upper_missing[0]:03b}"] += 1

        indices = np.unique(words[allowed])
        present = {SIX_WORDS[w] for w in indices}
        assert present <= LOWER_CONJUNCTION
        lower_image_sizes[len(present)] += 1
        present_rows = np.asarray(sorted(present), dtype=np.uint8)
        for corner in CHOICES:
            lower_bonds.add(tuple(sorted(readings[k] for k in corner)))
            projection = bit_words(present_rows[:, corner].T)
            assert set(projection) == set(range(7))
            for up in range(3):
                if is_read(present_rows[:, 2 * up] ^ present_rows[:, 2 * up + 1], projection):
                    disagreements.append({"box": box, "single_lower_bond_reads_upper": [corner, up]})

    obstructions = Counter()
    for triple in lower_bonds:
        if any(value != 1 for _, value in triple):
            obstructions["requires a disagreement"] += 1
            continue
        obstructions[equality_obstruction([c for c, _ in triple], supports)] += 1
    return {"file": row["file"], "line": row["line"], "boxes": row["boxes"], "upper_images": upper_images,
            "sizes_of_actual_six_reading_images": lower_image_sizes, "signs": signs,
            "carrier_sizes": carrier_sizes, "source_laws_repeating_a_carrier": repeated_at_source,
            "restored_assignment_count_histogram": restored_counts,
            "distinct_lower_bonds": len(lower_bonds), "lower_binary_obstructions": obstructions,
            "disagreements": disagreements}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("records", type=Path)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    started = time.perf_counter()
    selected = [row for line in args.records.read_text().splitlines() if (row := json.loads(line))["boxes"]]
    readings = [controls(row) for row in selected[:args.limit]]
    summary = {"systems": len(readings), "boxes": sum(row["boxes"] for row in readings),
               "distinct_lower_bonds": sum(row["distinct_lower_bonds"] for row in readings),
               "disagreements": sum(len(row["disagreements"]) for row in readings)}
    for field in ("upper_images", "sizes_of_actual_six_reading_images", "signs", "carrier_sizes",
                  "source_laws_repeating_a_carrier", "restored_assignment_count_histogram", "lower_binary_obstructions"):
        counts = Counter()
        for row in readings:
            counts.update(row[field])
        summary[field] = dict(sorted(counts.items()))
    payload = {"summary": summary, "systems": readings,
               "product_controls": product_controls(), "previous_witness_class": previous_witness(selected),
               "resources": {"seconds": round(time.perf_counter() - started, 3),
                             "peak_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}}
    print(json.dumps(summary, indent=2))
    if args.output:
        with args.output.open("x") as file:
            json.dump(payload, file, indent=1)
            file.write("\n")


if __name__ == "__main__":
    main()
