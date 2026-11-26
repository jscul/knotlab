"""Replay the frozen parity census and held-out sample from their declared inputs."""

import argparse
from collections import Counter, defaultdict
from gzip import open as gzip_open
import hashlib
from itertools import combinations, permutations, product
import json
from pathlib import Path
from random import Random
import resource
import time

from frozen_recount_core import (
    BinarySpan, all_words, class_readers, components, grow, mask, meeting_sets,
    motion, names_of, owners_of, perpendicular, projected_equality,
)


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
RESEARCH = STUDY.parent
SOURCE_ROSTER = RESEARCH / "FORBID-EDITS-20261126-001" / "starts.json"
PREDECESSOR = RESEARCH / "TWO-CLASS-SIGN-20261126-001" / "census_canonical.jsonl.gz"
HELDOUT_SEED = 20261206


def census_starts():
    return [
        (n, tuple(map(tuple, meetings)), tuple(loose))
        for n, meetings, loose in json.loads(SOURCE_ROSTER.read_text())
    ]


def input_rows(start):
    n, meetings, loose = start
    rows = [[] for _ in range(n)]
    name = 0
    for first, second, count in meetings:
        for _ in range(count):
            rows[first].append(name)
            rows[second].append(name)
            name += 1
    for row, count in zip(rows, loose, strict=True):
        row.extend(range(name, name + count))
        name += count
    return tuple(map(tuple, rows))


def connected(n, meetings):
    neighbors = [set() for _ in range(n)]
    for first, second, _ in meetings:
        neighbors[first].add(second)
        neighbors[second].add(first)
    return len(components(neighbors)) == 1


def sampled_starts(n, count, seed):
    """Apply the declared conditional weighting with independent code."""
    rng = Random(seed)
    pairs = list(combinations(range(n), 2))
    accepted = []
    while len(accepted) < count:
        present = [(a, b) for a, b in pairs if rng.random() < 1 / 3]
        meetings = tuple((a, b, 1 + rng.randrange(2)) for a, b in present)
        loose = tuple(rng.randrange(3) for _ in range(n))
        if sum(multiplicity for _, _, multiplicity in meetings) + sum(loose) > 18:
            continue
        places = list(loose)
        for first, second, multiplicity in meetings:
            places[first] += multiplicity
            places[second] += multiplicity
        if min(places) >= 3 and connected(n, meetings):
            accepted.append((n, meetings, loose))
    return accepted


def roster_of_size(n):
    """Generate meeting-pattern orbits first, then loose-count orbits within each."""
    pairs = tuple(combinations(range(n), 2))
    number_of = {pair: i for i, pair in enumerate(pairs)}
    renamings = []
    for order in permutations(range(n)):
        indices = tuple(number_of[tuple(sorted((order[a], order[b])))] for a, b in pairs)
        renamings.append((order, indices))

    seen = set()
    roster = set()
    for counts in product(range(3), repeat=len(pairs)):
        total = sum(counts)
        if counts in seen or total < n - 1 or total > 12:
            continue
        meetings = tuple((*pair, count) for pair, count in zip(pairs, counts, strict=True) if count)
        if not connected(n, meetings):
            continue
        orbit = [(tuple(counts[i] for i in indices), order) for order, indices in renamings]
        seen.update(word for word, _ in orbit)
        doubled_pairs = {
            word: tuple((*pair, count) for pair, count in zip(pairs, word, strict=True) if count)
            for word, _ in orbit
        }
        canonical = min(doubled_pairs, key=doubled_pairs.get)
        canonical_orders = [order for word, order in orbit if word == canonical]
        shared = [0] * n
        for first, second, multiplicity in meetings:
            shared[first] += multiplicity
            shared[second] += multiplicity
        lower = [max(0, 3 - count) for count in shared]
        for loose in product(*(range(bound, 3) for bound in lower)):
            if total + sum(loose) <= 12:
                least = min(tuple(loose[knot] for knot in order) for order in canonical_orders)
                roster.add((n, doubled_pairs[canonical], least))
    return roster


def renaming_key(start):
    """Canonical key for size-matched overlap checks using refined knot colors."""
    n, meetings, loose = start
    mutual = [dict() for _ in loose]
    for a, b, count in meetings:
        mutual[a][b] = mutual[b][a] = count

    colors = list(loose)
    while True:
        signatures = [
            (colors[i], tuple(sorted((count, colors[j]) for j, count in mutual[i].items())))
            for i in range(n)
        ]
        code = {signature: i for i, signature in enumerate(sorted(set(signatures)))}
        refined = [code[key] for key in signatures]
        if refined == colors:
            break
        colors = refined
    groups = defaultdict(list)
    for knot, color in enumerate(colors):
        groups[color].append(knot)

    def key(group_orders):
        order = [knot for group in group_orders for knot in group]
        return (
            tuple(loose[knot] for knot in order),
            tuple(mutual[a].get(b, 0) for a, b in combinations(order, 2)),
        )

    return n, min(key(groups) for groups in product(*(permutations(groups[c]) for c in sorted(groups))))


def shared_by_piece(rows):
    owners = owners_of(rows)
    meets = meeting_sets(len(rows), owners)
    pieces = components(meets)
    shared = [{name for name, holders in owners.items() if len(holders) == 2 and holders[0] in piece}
              for piece in pieces]
    triple = any(meets[a] & meets[b] for a, neighbors in enumerate(meets) for b in neighbors)
    return pieces, [mask(part) for part in shared if part], triple


def check_literal(result):
    """Count parity changes by assignments, then minimize literally through each distinction."""
    checks = tuple(map(mask, result.rows))
    names = result.names
    allowed = all_words(result.allowed)
    literal_assignments = len(names) <= 12
    if literal_assignments:
        literal = {word for word in all_words(1 << name for name in names)
                   if not any((word & row).bit_count() & 1 for row in checks)}
        assert literal == allowed
    shortest = {}
    for word in allowed - {0}:
        assert not any((word & row).bit_count() & 1 for row in checks)
        weight = word.bit_count()
        for name in names_of(word):
            minimum, moves = shortest.get(name, (len(names) + 1, set()))
            if weight < minimum:
                shortest[name] = (weight, {word})
            elif weight == minimum:
                moves.add(word)
    assert set(result.moves) == {word for _, moves in shortest.values() for word in moves}
    assert result.ties == sum(len(moves) for _, moves in shortest.values())
    return {
        "allowed changes": len(allowed), "distinct shortest moves": len(result.moves),
        "through-distinction shortest moves with ties": result.ties,
        "all assignments inspected": literal_assignments,
    }


def reader_summary(result, readings):
    return {
        "classes": result.classes,
        "allowed rank": len(result.allowed),
        "move rank": len(result.move_basis),
        "shortest moves": len(result.moves),
        "through-distinction shortest moves with ties": result.ties,
        "listed supports passing K1–K3": [i for i, passes in enumerate(readings["k1_k3"]) if passes],
        "listed supports": len(result.rows),
        "read rank per listed support": [len(reader) for reader in readings["readers"]],
        "readings": {
            key: {name: value for name, value in readings[key].items() if not name.endswith("_values")}
            for key in ("listed", "knots")
        },
    }


def parities(result, readings):
    expressions = parity_expressions(readings["label_basis"])
    reader_expressions = [parity_expressions(basis) for basis in readings["readers"]]
    output = []
    for value, representative in sorted(expressions.items()):
        if value:
            readers = [[i, list(names_of(representatives[value]))]
                       for i, representatives in enumerate(reader_expressions) if value in representatives]
            assert result.is_label(representative)
            output.append({
                "parity of distinctions": list(names_of(representative)),
                "readable at listed supports": readers,
            })
    return output


def parity_expressions(basis):
    expressions = {0: 0}
    for value, representative in basis.items():
        expressions.update({word ^ value: parity ^ representative for word, parity in expressions.items()})
    return expressions


def projection_with_controls(old, normal):
    keep = mask(old.names)
    records = {}
    for arm in ("one_fewer", "arity_floor"):
        cut = grow(old.rows, arm=arm)
        assert cut.status == "funded"
        assert [birth.inputs for birth in cut.births] == [birth.inputs for birth in normal.births]
        names = sorted(owners_of(cut.stage))
        permitted = perpendicular(map(mask, cut.stage), names)
        projected = BinarySpan(word & keep for word in permitted)
        removed = len(old.allowed) - len(projected)
        records[arm] = {"removed rank": removed}
        if removed:
            witness = next(word for word in old.allowed if word not in projected)
            records[arm]["old allowed change without completion"] = list(names_of(witness))
            records[arm]["zero-fresh births"] = [birth.inputs for birth in cut.births if not birth.fresh]
    return records


def renamed(rows, rng):
    names = sorted(owners_of(rows))
    labels = [5 + 2 * i for i in range(len(names))]
    rng.shuffle(labels)
    renaming = dict(zip(names, labels, strict=True))
    out = [tuple(renaming[d] for d in reversed(row)) for row in rows]
    rng.shuffle(out)
    return tuple(out)


def goal_results(stage, reads):
    fields = ("local_rank", "quotient_rank", "unreadable_rank", "locally_readable_count", "unreadable_count")
    return stage.classes, *(tuple(reads[scope][field] for field in fields) for scope in ("listed", "knots"))


def rows_from(path, opener=open):
    with opener(path, "rt") as records:
        return [json.loads(line) for line in records]


def score_from(computed, name):
    if not computed["grows"]:
        return f"{name} / does not grow: {computed['end']}"
    if computed["in the conditions"]:
        label = "holds" if passes_p1(computed) else "breaks"
        return f"{name} / P1: in the conditions / {label}"
    causes = []
    if computed["an old knot keeps a loose distinction"]:
        causes.append("an old knot keeps a loose distinction")
    if computed["three knots pairwise share"]:
        causes.append("three knots pairwise share")
    outside = " / ".join(causes)
    return f"{name} / P2: outside the conditions ({outside}) / {computed['classes']} classes"


def passes_p1(row):
    return row["classes"] == row["predicted classes"] and row["each piece parity a label"]


def audit(retain, source_triplet, census_by_index, label_rows, counts, literal, renaming):
    name, index, start = source_triplet
    n, meetings, _ = start
    rows = input_rows(start)
    before = motion(rows)
    growth = grow(rows)
    pieces, piece_parities, triple = shared_by_piece(rows)
    counts[("source pieces", len(pieces))] += 1
    counts[("round status", growth.status)] += 1
    computed = {"index": index, "knots": n, "grows": growth.status == "funded"}
    if not computed["grows"]:
        computed["end"] = growth.status

    after = motion(growth.stage) if computed["grows"] else None
    phases = [("start", before)]
    if after is not None:
        phases.append(("after one round", after))
    if name == "census":
        old_status = census_by_index[index]
        if after is None:
            assert old_status["after one round"] == "no round (stall or close)"
            counts[("status agrees with earlier archive", growth.status)] += 1

    for phase, result in phases:
        counts[(phase, "classes", result.classes)] += 1
        if name == "census":
            expected = old_status[phase]["loose free"]
            assert (expected["classes"], expected["dim S"], expected["dim H"], expected["distinctions"]) == (
                result.classes, len(result.allowed), len(result.move_basis), len(result.names))
            counts[(phase, "matches earlier archived count and ranks")] += 1
        reads = class_readers(result) if result.class_bits else None
        if reads:
            for scope in ("listed", "knots"):
                counts[(phase, scope, "quotient rank", reads[scope]["quotient_rank"])] += 1
                counts[(phase, scope, "unreadable rank", reads[scope]["unreadable_rank"])] += 1
                counts[(phase, scope, "classes and unreadable label count", result.classes,
                        reads[scope]["unreadable_count"])] += 1
        if result.classes >= 4:
            record = reader_summary(result, reads)
            record.update({
                "set": name, "index": index, "when": phase, "start": start,
                "round status": growth.status, "parities": parities(result, reads),
            })
            label_rows.append(record)
        # Exercise the literal comparison once per phase and size, and on multi-class stages up to rank 14.
        if len(result.allowed) <= 14 and (result.classes >= 4 or (name, n, phase) not in literal):
            raw = check_literal(result)
            raw.update({"index": index, "start": start})
            literal[(name, n, phase)].append(raw)

    if after is None:
        return computed, None

    owners = owners_of(growth.stage)
    kept_loose = any(len(owners[d]) == 1 for row in rows for d in row)
    supplied = {d for d, holders in owners_of(rows).items() if len(holders) == 1}
    spent = [d for birth in growth.births for d in birth.inputs]
    assert len(spent) == len(set(spent)) and set(spent) == supplied
    counts[("each old loose distinction spent once",)] += 1
    counts[("C2 old knot retains loose distinction", kept_loose)] += 1
    counts[("C3 three mutually meeting knots", triple)] += 1
    counts[("grown pieces", len(components(meeting_sets(len(growth.stage), owners))))] += 1
    counts[("round-one births", len(growth.births))] += 1
    counts[("round-one implied zero-fresh births", sum(b.implied and not b.fresh for b in growth.births))] += 1
    counts[("projection equality", projected_equality(before, after))] += 1
    assert any(all(len(owners[d]) == 2 for d in row) for row in rows)
    counts[("some proper subcollection holds every distinction",)] += 1
    computed.update({
        "classes": after.classes,
        "an old knot keeps a loose distinction": kept_loose,
        "three knots pairwise share": triple,
        "predicted classes": 1 << len(piece_parities),
        "in the conditions": not kept_loose and not triple,
        "each piece parity a label": all(after.is_label(word) for word in piece_parities),
    })
    if after.classes >= 4:
        computed["labels read knot by knot"] = reads["listed"]["quotient_rank"] == 0

    result = {"start": start, "start supports": rows, "after supports": growth.stage}
    for arm, controls in projection_with_controls(before, growth).items():
        ranks = controls["removed rank"]
        counts[("projection control", arm, "old allowed rank removed", ranks)] += 1
        if ranks and (name, arm) not in retain["projection witnesses"]:
            retain["projection witnesses"][(name, arm)] = {"index": index, "start": start, **controls}

    if computed["in the conditions"]:
        double = sum(c == 2 for _, _, c in meetings)
        cycle = len(meetings) > n - len(pieces)
        pass_p1 = passes_p1(computed)
        counts[("P1", "classes", after.classes, "piece parity works", computed["each piece parity a label"])] += 1
        counts[("P1", "double meetings", double, "pass", pass_p1)] += 1
        counts[("P1", "single-meeting cycles", cycle, "pass", pass_p1)] += 1
        counts[("P1", "round-one births", len(growth.births), "pass", pass_p1)] += 1
        counts[("P1", "classes at start", before.classes, "pass", pass_p1)] += 1
        odd_move_lengths = [word.bit_count() for word in after.moves if word.bit_count() & 1]
        odd_allowed = any(word.bit_count() & 1 for word in after.allowed)
        assert len(piece_parities) == 1
        assert all((word & piece_parities[0]).bit_count() % 2 == word.bit_count() % 2 for word in after.allowed)
        assert computed["each piece parity a label"] == (odd_allowed and not odd_move_lengths)
        shortest_odd = min(odd_move_lengths, default=0)
        counts[("P1", "shortest odd-sized selected change", shortest_odd, "odd allowed", odd_allowed)] += 1
        key = (name, bool(double), pass_p1)
        if key not in retain["P1 examples"]:
            witness = min((word for word in after.moves if word.bit_count() & 1), key=int.bit_count, default=0)
            retain["P1 examples"][key] = {
                "index": index, **result, "after classes": after.classes,
                "old shared distinctions": list(names_of(piece_parities[0])),
                "odd allowed change": odd_allowed,
                "shortest odd-sized selected change": list(names_of(witness)),
            }

    if after.classes >= 4:
        changed = grow(renamed(rows, renaming))
        assert changed.status == "funded"
        new = motion(changed.stage)
        assert goal_results(after, reads) == goal_results(new, class_readers(new))
        counts[("four-or-more-class growths replayed after renaming and knot reordering",)] += 1
    return computed, reads


def overlap(sample, earlier):
    exact = Counter(sample)
    prior_exact = set(earlier)
    same_pattern = [renaming_key(start) for start in sample]
    prior_same_pattern = defaultdict(list)
    for i, start in enumerate(earlier):
        prior_same_pattern[renaming_key(start)].append(i)
    matched = [[i, prior_same_pattern[key]] for i, key in enumerate(same_pattern) if key in prior_same_pattern]
    return {
        "earlier seed sample count": len(earlier),
        "distinct labelled starts in held-out sample": len(exact),
        "distinct held-out starts up to renaming": len(set(same_pattern)),
        "held-out draws repeating an earlier labelled start": sum(count for key, count in exact.items() if key in prior_exact),
        "held-out draws repeating an earlier start up to renaming": len(matched),
        "overlap pairs by draw index": matched,
    }


def recount(limit):
    start_time = time.perf_counter()
    census = census_starts()
    census_size = Counter(start[0] for start in census)
    assert len(census) == len(set(census))
    for n, count in census_size.items():
        regenerated = roster_of_size(n)
        assert len(regenerated) == count and regenerated == {start for start in census if start[0] == n}
    sources = {}
    for i, start in enumerate(census):
        sources.setdefault(("census", start[0]), []).append(("census", i, start))
    samples = {}
    for n in (6, 7, 8):
        sample = sampled_starts(n, limit if limit is not None else 300, HELDOUT_SEED + n)
        samples[n] = sample
        sources[("held out", n)] = [("held out", f"{n}-{i}", start) for i, start in enumerate(sample)]
    orig = {
        name: {row["index"]: row for row in rows_from(STUDY / path)}
        for name, path in (("census", "frozen_census.jsonl"), ("held out", "frozen_heldout.jsonl"))
    }
    assert len(orig["census"]) == len(census) and len(orig["held out"]) == 900
    earlier = {int(row["structure"].split()[-1]): row for row in rows_from(PREDECESSOR, gzip_open)}
    preparation_seconds = time.perf_counter() - start_time

    by_size = {}
    by_set = defaultdict(Counter)
    literal = defaultdict(list)
    renaming = Random(61012001)
    retain = {"P1 examples": {}, "projection witnesses": {}}
    label_rows, comparisons = [], []
    stop_candidates = []
    errors = []
    score = Counter()
    p1_breaks, p3_defeats = [], []
    least_p1_failure = None
    for (name, n), items in sources.items():
        counts = Counter()
        for source in items[:limit]:
            _, index, _ = source
            row, after = audit(retain, source, earlier, label_rows, counts, literal, renaming)
            if row != orig[name][index]:
                errors.append({"set": name, "computed": row, "archive": orig[name][index]})
            else:
                counts[("all fields match the frozen row",)] += 1
            comparisons.append([name, row])
            score[score_from(row, name)] += 1
            if row["grows"] and row["in the conditions"] and not passes_p1(row):
                p1_breaks.append([name, index, row["classes"], row["predicted classes"], row["each piece parity a label"]])
                if least_p1_failure is None:
                    least_p1_failure = {"set": name, "index": index, "start": source[-1], "classes": row["classes"]}
            if row.get("classes", 0) >= 4:
                read_by_knots = row["labels read knot by knot"]
                verdict = "read knot by knot" if read_by_knots else "not read knot by knot"
                score[f"{name} / P3: four or more classes / {verdict}"] += 1
                if not read_by_knots:
                    p3_defeats.append([name, index, row["classes"]])
            if name == "held out" and after and after["listed"]["quotient_rank"]:
                stop_candidates.append([index, source[-1], row["classes"], after["listed"]["quotient_rank"]])
        by_size[f"{name}, {n} knots"] = render_counts(counts)
        by_set[name].update(counts)
    replay_seconds = time.perf_counter() - start_time - preparation_seconds

    projected_score = {"tally": dict(score), "P1 breaks": p1_breaks, "candidate tower steps": p3_defeats}
    published_score = json.loads((STUDY / "score.json").read_text())
    recorded_multiclass = json.loads((STUDY / "multi_class.json").read_text())
    recorded_keys = Counter((r["when"], r["census index"]) for r in recorded_multiclass)
    read_keys = {(r["when"], r["index"]) for r in label_rows if r["set"] == "census"}
    lab_records = {(r["when"], r["index"]): r for r in label_rows if r["set"] == "census"}
    for archived in recorded_multiclass:
        key = archived["when"], archived["census index"]
        if key not in lab_records:
            continue
        now = lab_records[key]
        assert (
            (now["classes"], now["readings"]["listed"]["local_rank"], now["read rank per listed support"])
            == (archived["classes"], archived["labels read knot by knot"],
                [dict(archived["readable in one knot"]).get(i, 0) for i in range(now["listed supports"])])
        )
    overlap_by_size = {
        n: overlap(sample, sampled_starts(n, 1000, 20261126 + n)) for n, sample in samples.items()
    }
    output = {
        "input weighting": (
            "Equal count of census starts up to renaming. Held-out starts are labelled accepted draws with replacement, "
            "using 300 draws per size at seeds 20261206 + n. Overlap compares with the earlier extension weighting at "
            "1000 draws per size at seeds 20261126 + n."
        ),
        "limit per size": limit,
        "independently regenerated census roster counts": dict(census_size),
        "held-out uniqueness and overlap by size": overlap_by_size,
        "set counts": {name: render_counts(counts) for name, counts in by_set.items()},
        "counts by size": by_size,
        "archive comparison": {
            "compared frozen rows": len(comparisons),
            "differing frozen rows": errors,
            "matches archived scoring in full": limit is None and projected_score == published_score,
            "recomputed row digest": hashlib.sha256(json.dumps(comparisons, sort_keys=True).encode()).hexdigest(),
            "pre-freeze multi-class duplicate rows": [
                [phase, index, repetitions] for (phase, index), repetitions in recorded_keys.items() if repetitions > 1
            ],
            "pre-freeze multi-class rows absent but in independent replay": sorted(read_keys - recorded_keys.keys()),
        },
        "score": dict(score),
        "four-or-more-class cases": label_rows,
        "least P1 counterexample in archive order": least_p1_failure,
        "P3 failures in its frozen test": p3_defeats,
        "literal held-out stop counts by class count": dict(Counter(row[2] for row in stop_candidates)),
        "literal held-out stop cases with at least two classes and a nonzero local-span quotient": stop_candidates,
        "P1 witnesses": [{"set": name, "has double meeting": has_double, "passes": passes, **record}
                         for (name, has_double, passes), record in retain["P1 examples"].items()],
        "projection witnesses": [{"set": name, "arm": arm, **record}
                                 for (name, arm), record in retain["projection witnesses"].items()],
        "literal checks": [{"set": name, "knots": n, "when": when, "checks": records}
                           for (name, n, when), records in literal.items()],
        "preparation seconds": round(preparation_seconds, 3),
        "replay seconds": round(replay_seconds, 3),
        "total seconds": round(time.perf_counter() - start_time, 3),
        "maximum resident KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "address space cap bytes": resource.getrlimit(resource.RLIMIT_AS)[0],
    }
    return output


def render_counts(counts):
    return {" / ".join(map(str, key)): value for key, value in sorted(counts.items())}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit-per-size", type=int)
    parser.add_argument("--out", type=Path, required=True)
    arguments = parser.parse_args()
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    memory = min([2_500_000_000] + [bound for bound in (soft, hard) if bound != resource.RLIM_INFINITY])
    resource.setrlimit(resource.RLIMIT_AS, (memory, hard))
    data = recount(arguments.limit_per_size)
    arguments.out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"{data['archive comparison']['compared frozen rows']} rows, {data['total seconds']:.2f} seconds, "
          f"{data['maximum resident KiB']} KiB")
