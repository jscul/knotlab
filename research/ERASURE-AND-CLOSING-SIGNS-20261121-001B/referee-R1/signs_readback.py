"""Read saved sign certificates, apply them to physical words, replay cancellations."""

import argparse
from collections import Counter, deque
import gzip
from itertools import combinations
import json
from pathlib import Path
import resource
import time


HERE = Path(__file__).resolve().parent
TICKET = HERE.parent.name
ARCHIVE = HERE.parents[2] / "artifacts" / TICKET / (TICKET + "-E001_closures")


def load(path):
    with (gzip.open(path, "rt") if path.suffix == ".gz" else path.open()) as file:
        return json.load(file)


def physical_basis(rows, width):
    reduced = rows.copy()
    pivots = {}
    for col in range(width):
        idx = len(pivots)
        found = next((i for i in range(idx, len(rows)) if reduced[i] & 1 << col), None)
        if found is not None:
            reduced[idx], reduced[found] = reduced[found], reduced[idx]
            for i in range(len(rows)):
                if i != idx and reduced[i] & 1 << col:
                    reduced[i] ^= reduced[idx]
            pivots[col] = idx
    result = [0]
    for j in range(width):
        if j not in pivots:
            word = 1 << j
            for col, row in pivots.items():
                if reduced[row] & 1 << j:
                    word |= 1 << col
            result.append(word)
    return result


def apply_word(factors, word, translations, signs):
    parity = 0
    for e in reversed(factors):
        parity ^= ((word ^ signs) >> e) & 1
        word ^= translations[e]
    return parity, word


def check_on_carrier(rows, holders, terminal, certificate, counts):
    names = certificate["physical_name_order"]
    translations = certificate["shift_masks"]
    signs = certificate["sign_mask"]
    local = [[names.index(e) for e in rows[v]] for v in holders]
    masks = [sum(1 << e for e in row) for row in local]
    points = physical_basis(masks, len(names))
    assert len(points) == 1 + len(names) - len(holders) + 1
    for w in points:
        assert all((row & w).bit_count() % 2 == 0 for row in masks)
        for e in range(len(names)):
            assert apply_word([e, e], w, translations, signs) == (0, w)
            new = w ^ translations[e]
            assert all((row & new).bit_count() % 2 == 0 for row in masks)
            counts["named_involution_word_actions"] += 1
        for holder, row in zip(holders, local, strict=True):
            for a, b in combinations(row, 2):
                assert apply_word([a, b], w, translations, signs) == apply_word([b, a], w, translations, signs)
                counts["named_commutation_word_actions"] += 1
            assert apply_word(row, w, translations, signs) == (int(holder == terminal), w)
            counts["named_product_word_actions"] += 1
    counts["zero_and_basis_words"] += len(points)


def replay_negative(rows, holders, terminal, trace, counts):
    physical = {int(i): deque(word) for i, word in trace["physical_cyclic_words"].items()}
    assert set(physical) == set(holders)
    for i, word in physical.items():
        assert sorted(word) == sorted(rows[i])
    root = trace["root"]
    merged = physical.pop(root)
    odd = int(root == terminal)
    for holder, name, rotate_left, rotate_right in trace["joins"]:
        other = physical.pop(holder)
        merged.rotate(-rotate_left)
        other.rotate(-rotate_right)
        assert merged.pop() == name and other.popleft() == name
        merged.extend(other)
        odd ^= holder == terminal
        counts["local_product_joins"] += 1
    for rotate, name in trace["remaining_cancellations"]:
        merged.rotate(-rotate)
        assert merged.popleft() == name and merged.popleft() == name
        counts["remaining_adjacent_cancellations"] += 1
    assert not physical and not merged and odd == trace["sign_bit"] == 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    started = time.perf_counter()
    resource.setrlimit(resource.RLIMIT_AS, (1_750_000 * 1024, resource.getrlimit(resource.RLIMIT_AS)[1]))
    data = load(HERE / "signs_archive_cases.json.gz")
    index = {(d["panel"], d["draw"]): d for d in data}
    forward = load(HERE / "signs_forward_cases.json.gz")
    assert all(index[(d["panel"], d["draw"])] == d for d in forward)
    named_draws = {(d["panel"], d["draw"]): d for d in load(ARCHIVE / "panels_histories.json.gz")}
    structures = load(HERE / "signs_structure.json")["samples"]
    counts = Counter()
    for s in structures[:args.limit]:
        key = s["panel"], s["draw"]
        age, terminal = s["age"], s["odd_holder"]
        physical = named_draws[key]["laws"]["parity"]["cuts"][age - 1]["after_rows"]
        computed = index[key]["laws"]["parity"][age - 1]["closures"]
        closure = next(c for c in computed if c["terminal_holder"] == terminal)
        reading = closure["signed_permutation"]
        holders = closure["holder_ids"]
        assert (reading is None) == (s["certificate"] == "planar_rotation")
        if reading is None:
            replay_negative(physical, holders, terminal, s["literal_reduction"], counts)
            counts["arbitrary_operator_refusals"] += 1
        else:
            check_on_carrier(physical, holders, terminal, reading, counts)
            counts["positive_operator_products"] += 1
            if key == ("S", 2):
                altered = dict(reading, sign_mask=reading["sign_mask"] ^ 1)
                try:
                    check_on_carrier(physical, holders, terminal, altered, Counter())
                except AssertionError:
                    counts["corrupted_physical_sign_rejected"] += 1
                else:
                    raise AssertionError("altered named operator passed")
    elapsed = time.perf_counter() - started
    result = {
        "sample_limit": args.limit, "certificates": counts,
        "full_matching_draw_records_on_separate_forward_input": len(forward),
        "elapsed_seconds": round(elapsed, 5),
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
