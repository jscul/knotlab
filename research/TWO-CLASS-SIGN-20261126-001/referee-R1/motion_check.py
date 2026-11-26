#!/usr/bin/env python3
"""Rebuild the tied shortest changes and parity classes of two bare rings."""

import argparse
from collections import Counter, defaultdict, deque
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import resource
from time import perf_counter


ROOT = Path(__file__).resolve().parents[3]
MOTION_ID = "MOTION-AT-EDDY-20261119-001"
MOTION_RUN = f"{MOTION_ID}-E001_motion"
FROZEN_INPUTS = Path("experiments") / MOTION_ID / MOTION_RUN / "inputs.json"
PATTERNS = Path("artifacts") / MOTION_ID / MOTION_RUN / "patterns.json"
READS_ID = "READS-HOLDERS-SOURCES-20261120-001A"
MOTION = Path("artifacts") / READS_ID / f"{READS_ID}-E001_reads_changes/motion.json"
RING_CASE = {5: "R0", 31: "R31"}
MEMORY_CAP = 2_000_000_000
PREPARATIONS = [(size, age, pinned) for size in RING_CASE for age in (0, 1) for pinned in (False, True)]
PILOT = [(5, 0, False), (31, 1, False)]


def require_equal(actual, expected, label):
    if actual != expected:
        raise AssertionError(f"{label}\nrebuilt {actual!r}\nrecorded {expected!r}")


def read_json(path):
    return json.loads((ROOT / path).read_text())


def mark_ids(value):
    while value:
        bit = value & -value
        yield bit.bit_length() - 1
        value ^= bit


def mask(marks):
    return sum(1 << mark for mark in marks)


def incidence(holdings):
    owners = defaultdict(list)
    for holder, marks in enumerate(holdings):
        require_equal(len(set(marks)), len(marks), "distinct marks at one holder")
        for mark in marks:
            owners[mark].append(holder)
    require_equal(sorted(owners), list(range(len(owners))), "consecutive mark names")
    if any(len(holders) not in (1, 2) for holders in owners.values()):
        raise AssertionError("the ring replay requires one or two holders per mark")
    return [tuple(owners[mark]) for mark in range(len(owners))]


def stages(spec):
    """Use source meeting order, then number children by their parent pairs."""
    size = len(spec["sizes"])
    source = [[] for _ in range(size)]
    neighbours = [set() for _ in source]
    meetings = spec["meetings"]
    for mark, (first, second) in enumerate(meetings):
        source[first].append(mark)
        source[second].append(mark)
        neighbours[first].add(second)
        neighbours[second].add(first)
    require_equal([len(row) for row in neighbours], [2] * size, "source neighbours")
    fresh = len(meetings)
    available = []
    for wanted, held in zip(spec["sizes"], source):
        supply = list(range(fresh, fresh + wanted - len(held)))
        require_equal(len(supply), 2, "source loose distinctions per knot")
        fresh += len(supply)
        held.extend(supply)
        available.append(deque(supply))

    parent_pairs = sorted(tuple(sorted(row)) for row in neighbours)
    require_equal(len(set(parent_pairs)), size, "distinct pairs of parents")
    partners = [set() for _ in source]
    for first, second in parent_pairs:
        partners[first].add(second)
        partners[second].add(first)
    for a, b in parent_pairs:
        if b in neighbours[a] or partners[a] & partners[b]:
            raise AssertionError("the declared bare-ring construction requires only two-parent births")

    children = []
    for first, second in parent_pairs:
        children.append([available[first].popleft(), available[second].popleft(), fresh, fresh + 1])
        fresh += 2
    require_equal(sum(map(len, available)), 0, "all source loose distinctions spent")
    return source, source + children


def binary_basis(vectors):
    pivots = {}
    for value in vectors:
        while value:
            pivot = value.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = value
                break
            value ^= pivots[pivot]
    return pivots


def kernel_basis(equations, width):
    pivots = binary_basis(equations)
    ordered = sorted(pivots.items())
    basis = []
    for mark in range(width):
        if mark in pivots:
            continue
        value = 1 << mark
        for pivot, equation in ordered:
            if (value & equation).bit_count() % 2:
                value |= 1 << pivot
        basis.append(value)
    return basis


def span(vectors):
    values = [0]
    for vector in vectors:
        values.extend([state ^ vector for state in values])
    return values


def exhaustive_ties(states, width):
    minima = [set() for _ in range(width)]
    for state in sorted(states, key=int.bit_count):
        for mark in mark_ids(state):
            tied = minima[mark]
            if not tied or state.bit_count() == next(iter(tied)).bit_count():
                tied.add(state)
    return minima


def incidence_ties(owners, pinned):
    """A least even support through a mark consists of it and an alternate shortest path."""
    # Summing the knot equations makes the incidence at the auxiliary holder -1 even.
    active = {
        mark: holders if len(holders) == 2 else (*holders, -1)
        for mark, holders in enumerate(owners)
        if len(holders) == 2 or not pinned
    }
    adjacency = defaultdict(list)
    for mark, (first, second) in active.items():
        adjacency[first].append((second, mark))
        adjacency[second].append((first, mark))

    minima = [set() for _ in owners]
    for mark, (first, second) in active.items():
        queue = deque([first])
        levels = {first: 0}
        paths = {first: {0}}
        while queue:
            holder = queue.popleft()
            if holder == second:
                break
            next_level = levels[holder] + 1
            for peer, step in adjacency[holder]:
                if step == mark:
                    continue
                if peer not in levels:
                    levels[peer] = next_level
                    paths[peer] = set()
                    queue.append(peer)
                if levels[peer] == next_level:
                    paths[peer].update(path | (1 << step) for path in paths[holder])
        minima[mark] = {path | (1 << mark) for path in paths.get(second, ())}
    return minima


def orbits(states, moves):
    pending = set(states)
    sizes = []
    while pending:
        queue = [pending.pop()]
        for state in queue:
            for move in moves:
                after = state ^ move
                if after in pending:
                    pending.remove(after)
                    queue.append(after)
        sizes.append(len(queue))
    return sorted(sizes)


def inclusion_minimal(change, columns):
    # A legal support is minimal exactly when its only nonzero kernel word is itself.
    return len(binary_basis(columns[mark] for mark in mark_ids(change))) == change.bit_count() - 1


def projected_knots(holdings, allowed):
    projections = Counter()
    for marks in holdings:
        projected = [sum(((word >> mark) & 1) << i for i, mark in enumerate(marks))
                     for word in allowed]
        rules = tuple(sorted(span(binary_basis(projected).values())))
        projections[len(marks), rules] += 1

    checks = []
    for (arity, words), count in sorted(projections.items()):
        all_places = (1 << arity) - 1
        binding = len(words) < 1 << arity
        erasure = all(len({word & (all_places ^ (1 << mark)) for word in words}) == 1 << (arity - 1)
                      for mark in range(arity))
        checks.append(dict(arity=arity, words=list(words), occurrences=count, binding=binding,
                           loss_on_erasure=erasure, coexistence=bool(words),
                           is_knot=binding and erasure and bool(words)))
    return checks


def check_source_ties(minima, owners, original, pinned):
    loose_at = defaultdict(list)
    for mark, holders in enumerate(owners):
        if len(holders) == 1:
            loose_at[holders[0]].append(mark)
    for mark, holders in enumerate(owners):
        if pinned:
            expected = {original} if len(holders) == 2 else set()
        elif len(holders) == 1:
            expected = {mask(loose_at[holders[0]])}
        else:
            first, second = holders
            expected = {mask([mark, a, b]) for a in loose_at[first] for b in loose_at[second]}
        require_equal(minima[mark], expected, f"source tie formula at mark {mark}")


def check_grown_ties(rows, catalogue, pinned):
    policy = "pinned" if pinned else "free"
    archived_supports = catalogue["literal_short_minimum_supports"]
    profiles = catalogue["target_profiles"]
    require_equal(len(rows), len(profiles), "catalogued marks")
    for row, profile in zip(rows, profiles):
        expected = profile[policy]
        require_equal(row["mark"], profile["mark"], "archived mark name")
        require_equal(row["population"], profile["population"], "archived mark population")
        for key in ("size", "ties", "ties_with_current_loose"):
            require_equal(row[key], expected[key], f"mark {row['mark']} {key}")
        require_equal(expected["listed_all_supports"], True, "complete archived ties")
        require_equal(row["supports"], sorted(archived_supports[i] for i in expected["supports"]),
                      f"mark {row['mark']} exact tied supports")


def analyse(holdings, size, age, pinned):
    owners = incidence(holdings)
    width = len(owners)
    loose = mask(mark for mark, held in enumerate(owners) if len(held) == 1)
    original = mask(range(size))
    knot_reads = [mask(marks) for marks in holdings]
    mark_reads = [1 << mark for mark in range(width)]
    reads = mark_reads + knot_reads
    equations = knot_reads + ([1 << mark for mark in mark_ids(loose)] if pinned else [])
    allowed = kernel_basis(equations, width)
    if any((equation & value).bit_count() % 2 for value in allowed for equation in equations):
        raise AssertionError("illegal kernel basis assignment")

    minima = incidence_ties(owners, pinned)
    moves = sorted(set().union(*minima))
    if any((equation & value).bit_count() % 2 for value in [*moves, original] for equation in equations):
        raise AssertionError("an analysed change violates a parity or pinning equation")
    shortest_rank = len(binary_basis(moves))
    allowed_rank = len(allowed)
    class_count = 1 << (allowed_rank - shortest_rank)
    class_size = 1 << shortest_rank
    columns = [mask(holders) for holders in owners]

    # In the larger cases a basis of minimal supports suffices for the span comparison.
    circuit_basis = binary_basis([*moves, original])
    require_equal(len(circuit_basis), allowed_rank, "span of shortest changes and old ring")
    require_equal(all(inclusion_minimal(change, columns) for change in [*moves, original]),
                  True, "inclusion minimality of spanning changes")

    rows = []
    for mark, ties in enumerate(minima):
        population = "original_shared"
        if mark >= size:
            population = "current_loose" if loose & (1 << mark) else "original_loose_consumed"
        rows.append(dict(mark=mark, population=population,
                         size=next(iter(ties)).bit_count() if ties else None,
                         ties=len(ties), ties_with_current_loose=sum(bool(change & loose) for change in ties),
                         supports=sorted(list(mark_ids(change)) for change in ties)))
    if not age:
        check_source_ties(minima, owners, original, pinned)

    pinned_minima = minima if pinned else incidence_ties(owners, True)
    if any(change.bit_count() < 4 for ties in pinned_minima for change in ties):
        raise AssertionError("a shorter pinned change would require a separate four-change count")
    ordinary = sorted(change for change in set().union(*pinned_minima) if change.bit_count() == 4)
    odd_exchange_pairs = 0
    assignment_basis_checks = 0
    for read in reads:
        for change in moves:
            odd = (read & change).bit_count() % 2
            odd_exchange_pairs += odd
            for state in (0, change, original):
                before = (read & state).bit_count() % 2
                after = (read & (state ^ change)).bit_count() % 2
                require_equal(before ^ after, odd, "read and change ordering sign")
                assignment_basis_checks += 1

    ordinary_rank = len(binary_basis(ordinary))
    odd_translation_pairs = sum(any((read & basis_word).bit_count() % 2 for basis_word in allowed)
                                for read in reads) * (1 << max(0, allowed_rank - 1))
    result = dict(knots=len(holdings), distinctions=width, loose=loose.bit_count(), ring=size,
                  age=age, loose_pinned=pinned,
                  marked_minimum_sizes=Counter(str(row["size"]) for row in rows if row["size"] is not None),
                  allowed_change_rank=allowed_rank, allowed_assignments=1 << allowed_rank,
                  shortest_generators=len(moves), shortest_rank=shortest_rank,
                  shortest_counts_by_size=Counter(str(change.bit_count()) for change in moves),
                  shortest_fixed_weighting_dimension=class_count, ordinary_four_count=len(ordinary),
                  ordinary_four_rank=ordinary_rank, ordinary_fixed_weighting_dimension=1 << (allowed_rank - ordinary_rank),
                  all_circuit_rank=len(circuit_basis), all_circuit_fixed_weighting_dimension=1,
                  original_ring_in_shortest_span=len(circuit_basis) == shortest_rank,
                  original_ring=list(mark_ids(original)),
                  odd_original_overlap_in_shortest=sum((move & original).bit_count() % 2 for move in moves),
                  mark_or_knot_read_change_pairs=len(reads) * len(moves), odd_exchange_pairs=odd_exchange_pairs,
                  assignment_basis_checks=assignment_basis_checks, projected_knots=projected_knots(holdings, allowed),
                  all_translation_read_pairs=len(reads) << allowed_rank,
                  odd_pairs_over_all_translations=odd_translation_pairs)

    if size == 5 or allowed_rank == 1:
        states = span(allowed)
        require_equal(exhaustive_ties(states, width), minima, "enumeration and incidence ties")
        require_equal(sorted(change for change in states if change.bit_count() == 4 and not change & loose),
                      ordinary, "exhaustive ordinary four changes")
        sizes = orbits(states, moves)
        require_equal(sizes, [class_size] * class_count, "enumerated versus rank class sizes")
        require_equal(sum((read & state).bit_count() % 2 for read in reads for state in states),
                      odd_translation_pairs, "enumerated versus rank read overlaps")
        minimal = [change for change in states if change and inclusion_minimal(change, columns)]
        require_equal(len(binary_basis(minimal)), allowed_rank, "enumerated inclusion-minimal span")
        result.update(enumerated_allowed_states=len(states), all_circuit_count=len(minimal), orbit_sizes=sizes)

    return result, rows, [list(mark_ids(change)) for change in ordinary]


def compare(result, rows, ordinary, archive, catalogue):
    size, age, pinned = (result[key] for key in ("ring", "age", "loose_pinned"))
    require_equal(set(result), set(archive), "motion archive field coverage")
    for key, value in result.items():
        require_equal(value, archive[key], f"{size} knots, growth {age}, pinned {pinned}, {key}")
    if age:
        check_grown_ties(rows, catalogue, pinned)
        require_equal(sorted(ordinary), sorted(catalogue["ordinary_quads"]), "archived ordinary four changes")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="run two preparations without writing output")
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY_CAP, MEMORY_CAP))
    start = perf_counter()
    frozen = read_json(FROZEN_INPUTS)
    catalogue = read_json(PATTERNS)
    former_stage_path = Path(frozen["source_archive"])
    former_stage_bytes = (ROOT / former_stage_path).read_bytes()
    require_equal(sha256(former_stage_bytes).hexdigest(), frozen["archive_sha256"], "source archive digest")
    require_equal(sha256((ROOT / FROZEN_INPUTS).read_bytes()).hexdigest(), catalogue["frozen_inputs_sha256"],
                  "frozen source specification digest")
    former = json.loads(former_stage_bytes)["cases"][RING_CASE[5]]["stages"]
    specs = {spec["id"]: spec for spec in frozen["cases"]}
    rebuilt = {n: stages(specs[case]) for n, case in RING_CASE.items()}
    for age, holdings in enumerate(rebuilt[5]):
        require_equal(holdings, former[str(age)]["stars"], f"archived five-knot holdings at growth {age}")
    for n, case in RING_CASE.items():
        digest = sha256(json.dumps(rebuilt[n][1]).encode()).hexdigest()
        require_equal(digest, catalogue["cases"][case]["stage_support_sha256"], f"first growth holdings for {n} knots")

    motion_rows = read_json(MOTION)["rings"]
    archived = {(row["ring"], row["age"], row["loose_pinned"]): row for row in motion_rows}
    require_equal(len(motion_rows), len(archived), "distinct archived preparations")
    require_equal(set(archived), set(PREPARATIONS), "archived preparation coverage")
    results = []
    for n, age, pinned in PILOT if args.pilot else PREPARATIONS:
        stage_start = perf_counter()
        result, rows, ordinary = analyse(rebuilt[n][age], n, age, pinned)
        archive = archived[n, age, pinned]
        compare(result, rows, ordinary, archive, catalogue["cases"][RING_CASE[n]])
        class_count = result["shortest_fixed_weighting_dimension"]
        result.update(class_count=class_count, class_sizes=[1 << result["shortest_rank"]] * class_count,
                      per_mark=rows, exact_per_mark_comparison="archived literal supports" if age else "bare-ring formula",
                      matched_motion_fields=sorted(archive), wall_seconds=round(perf_counter() - stage_start, 6))
        results.append(result)
        print(f"{n} knots, growth {age}, pinned {pinned}, allowed rank {result['allowed_change_rank']}, "
              f"shortest rank {result['shortest_rank']}, class sizes {result['class_sizes']}, "
              f"{result['wall_seconds']:.6f} s", flush=True)

    wall_seconds = round(perf_counter() - start, 6)
    peak_kib = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print(f"Total {wall_seconds:.6f} s, peak {peak_kib} KiB, one process")
    if args.pilot:
        return
    command = f".venv/bin/python -B {Path(__file__).resolve().relative_to(ROOT)}"
    output = dict(rebuilt=results, total_wall_seconds=wall_seconds, peak_resident_kib=peak_kib,
                  workers=1, memory_cap_bytes=MEMORY_CAP, replay_command=command, pilot_command=f"{command} --pilot",
                  source_specification_read=str(FROZEN_INPUTS),
                  comparison_archives_read={"five_knot_holdings": str(former_stage_path),
                                            "grown_mark_ties_and_holding_digests": str(PATTERNS),
                                            "preparation_summaries": str(MOTION)},
                  total_mark_profiles=sum(len(result["per_mark"]) for result in results),
                  matched_literal_mark_profiles=sum(len(result["per_mark"]) for result in results if result["age"]),
                  total_read_change_pairs=sum(result["mark_or_knot_read_change_pairs"] for result in results),
                  total_odd_read_change_pairs=sum(result["odd_exchange_pairs"] for result in results),
                  controls=["Reconstructed holdings matched the five-knot source and first growth holdings, and the 31-knot first growth digest.",
                            "Every available mark kept every tied shortest support, including the pinned 31-distinction source change.",
                            "Source ties used a bare-ring formula as the second check. The preparation archive gives source size distributions.",
                            "The read and change sign was checked on zero, the change itself and the old ring for each pair.",
                            "On the five-knot preparations and the pinned 31-knot source, complete assignment and class enumeration matched rank calculations.",
                            "The two large 31-knot free preparations and the grown pinned preparation use exact ranks and structural supports."],
                  not_run=["Assignment and inclusion-minimal count enumeration on the 31-knot source with loose values free and the two first-growth preparations.",
                           "The earlier catalogue's physical reach and the motion archive's guarded trajectory, swap, prepared switch and relative-sign probability comparisons."])
    Path(__file__).with_name("motion_results.json").write_text(json.dumps(output, indent=2) + "\n")


if __name__ == "__main__":
    main()
