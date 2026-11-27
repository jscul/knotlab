"""Reconstruct marked parity families and test the proposed completions.

For a parity change, the selected distinctions occur an even number of times
at each holder. A change consisting of two loose distinctions therefore
recognizes one holder. For two different live holders, an allowed change of
four with just the specified two loose distinctions has two shared
distinctions left. Those must give the two holder steps through a common
third holder, and conversely any such pair of steps gives an allowed change.
Taking the resulting classes gives the start families on the marked names.

For any two specified loose names, a shortest allowed change with precisely
those loose names costs their holders' least number of steps plus two. The
shared distinctions of any such change join its two odd holders by a route,
and a shortest route realizes the bound. When there is no route there is no
such change. Minimizing over one name in each family recovers every direct
holder-step threshold, including thresholds at which no new families join.
Flipping exactly two family parities permits even numbers of other loose
distinctions. It is a different minimum. None of this reconstruction assumes
a particular number of rows, a minimum row size or global connectedness.

Adding one outside holder for the loose set makes each distinction appear
twice, so every row follows from the remaining rows. The outside row can be
empty. A row dependency in the original presentation must give the same
coefficient to two holders of a shared distinction, and must give zero to
any holder with a loose distinction. Thus the number of rows is their rank
plus the number of connected components without a loose distinction. Across
several open components the projection onto the loose distinctions has one
even-parity requirement per component. For one connected start it has just
one, witnessed by joining pairs of its loose distinctions along holder steps.

When every distinction has two holders, the literature's cycle matroid is
what the labelled parity states determine. The usual twists-only statement
assumes two-connectivity. At separating holders the general theorem also
allows splitting and rejoining, independently of any isolated bookkeeping
holder (Courcelle, The Monadic Second-Order Logic of Graphs XVI, §2.4).
"""

import argparse
from collections import Counter, defaultdict, deque
from contextlib import redirect_stdout
from functools import reduce
from io import StringIO
from itertools import combinations, islice
import json
from operator import and_, or_
from pathlib import Path
import resource
import sys
from time import perf_counter


OUTPUT = Path(__file__).with_suffix(".json")


def mask(*names):
    return sum(1 << name for name in set(names))


def bits(value):
    return tuple(i for i in range(value.bit_length()) if value & (1 << i))


def named(row, labels):
    return [labels[i] for i in bits(row)]


def size(rows):
    return reduce(or_, rows, 0).bit_length()


def allowed(rows, law, width):
    if law == "parity":
        return [s for s in range(1 << width) if all((s & r).bit_count() % 2 == 0 for r in rows)]
    if law == "not-all-equal":
        return [s for s in range(1 << width) if all((s & r) not in (0, r) for r in rows)]
    raise ValueError(law)


def profile(rows, width):
    return [sum(bool(r & (1 << j)) for r in rows) for j in range(width)]


def loose(rows, width):
    holders = profile(rows, width)
    assert all(c in (1, 2) for c in holders)
    return mask(*(i for i, count in enumerate(holders) if count == 1))


def is_minimal_projection(states, row):
    present = {s & row for s in states}
    arity = row.bit_count()
    return bool(present) and len(present) < 1 << arity and all(
        len({s & ~(1 << i) for s in present}) == 1 << (arity - 1) for i in bits(row)
    )


def components(items, meets):
    unseen = set(items)
    groups = []
    while unseen:
        group = {unseen.pop()}
        todo = list(group)
        while todo:
            at = todo.pop()
            visit = {b for b in unseen if meets(at, b)}
            unseen -= visit
            group.update(visit)
            todo.extend(visit)
        groups.append(sorted(group))
    return sorted(groups)


def partition_masks(groups):
    return sorted(reduce(or_, group, 0) for group in groups)


def structural(rows, width):
    marks = loose(rows, width)
    near = [{j for j, r in enumerate(rows) if i != j and rows[i] & r} for i in range(len(rows))]
    live = [i for i, r in enumerate(rows) if marks & r]
    families = components(live, lambda a, b: bool(near[a] & near[b]))
    groups = [reduce(or_, (rows[i] & marks for i in fam), 0) for fam in families]
    distances = {}
    for i, fam in enumerate(families):
        dist = {k: 0 for k in fam}
        queue = deque(fam)
        while queue:
            at = queue.popleft()
            for other in near[at] - dist.keys():
                dist[other] = dist[at] + 1
                queue.append(other)
        for j in range(i):
            key = tuple(sorted((groups[i], groups[j])))
            distances[key] = min((dist[k] for k in families[j] if k in dist), default=None)
    return {
        "components": len(components(range(len(rows)), lambda a, b: b in near[a])),
        "holders": sorted(rows[i] & marks for i in live),
        "candidates": sorted(tuple(sorted((rows[i] & marks, rows[j] & marks)))
                             for i, j in combinations(live, 2) if near[i] & near[j]),
        "families": sorted(groups),
        "distances": distances,
    }


def marked_reader(states, marks):
    """Read from changes and the marked loose set without receiving a presentation."""
    state_set = set(states)
    groups = components((1 << i for i in bits(marks)), lambda a, b: (a | b) in state_set)
    holders = partition_masks(groups)
    owner = {1 << i: h for h in holders for i in bits(h)}
    candidates = set()
    best = {}
    for state in states:
        pair = state & marks
        if pair.bit_count() != 2:
            continue
        a, b = (owner[1 << j] for j in bits(pair))
        if a == b:
            continue
        key = tuple(sorted((a, b)))
        length = state.bit_count() - 2
        best[key] = min(best.get(key, length), length)
        if length == 2:
            candidates.add(key)
    families = partition_masks(components(holders, lambda a, b: tuple(sorted((a, b))) in candidates))
    distances = {}
    for a, b in combinations(families, 2):
        reachable = (cost for (u, v), cost in best.items() if (u & a and v & b) or (u & b and v & a))
        distances[a, b] = min(reachable, default=None)
    return {"holders": holders, "candidates": sorted(candidates), "families": families, "distances": distances}


def check_marked(rows, states):
    actual = structural(rows, size(rows))
    read = marked_reader(states, loose(rows, size(rows)))
    assert read == {key: actual[key] for key in read}
    return actual


def canonical_projection(rows, support, law):
    """Cross-check the actual full system with the other place names hidden."""
    from knotlab.cli import main as check

    clauses = []
    for row in rows:
        names = bits(row)
        for word in range(1 << len(names)):
            fails = word.bit_count() % 2 if law == "parity" else word in (0, (1 << len(names))-1)
            if fails:
                clauses.append(" ".join(("~" if word & (1 << j) else "") + f"x{i}"
                                        for j, i in enumerate(names)))
    selected = [f"x{i}" for i in bits(support)]
    hidden = [f"x{i}" for i in range(size(rows)) if not (1 << i) & support]
    with redirect_stdout(StringIO()) as stream:
        status = check(["check", "--cnf", "; ".join(clauses), "--loops", *selected[:-1],
                        "--contact", selected[-1], "--witnesses", *hidden, "--json"])
    assert status == 0
    report = json.loads(stream.getvalue())
    return report["is_knot"], len(report["allowed"])


def nine_facts(partial=False):
    labels = ["p1", "q1", "p2", "q2", "p3", "q3", "R1", "R2", "R3"]
    width = len(labels)
    ring_names = mask(6, 7, 8)
    triples = [mask(2*i, 2*i + 1, 6+i) for i in range(3)]
    target = allowed(triples + [ring_names], "parity", width)
    equations = [s for s in range(1, 1 << width) if all((v & s).bit_count() % 2 == 0 for v in target)]
    tables = {r: mask(*allowed([r], "parity", width)) for r in equations}
    target_table = mask(*target)
    minimal = {r for r in equations if is_minimal_projection(target, r)}
    choices = combinations(equations, 4)
    if partial:
        choices = islice(choices, 64)
    total = basis = minimal_basis = checked = 0
    loose_choices = defaultdict(list)
    completed = defaultdict(list)
    meeting_degrees = Counter()
    for rows in choices:
        total += 1
        if reduce(and_, (tables[r] for r in rows)) != target_table:
            continue
        basis += 1
        minimal_basis += all(r in minimal for r in rows)
        if max(profile(rows, width)) > 2:
            continue
        cap = loose(rows, width)
        full = tuple(sorted((*rows, cap)))
        assert len(set(full)) == 5 and all(c == 2 for c in profile(full, width))
        assert all(r in minimal for r in full)
        for omit in range(5):
            assert reduce(and_, (tables[r] for j, r in enumerate(full) if omit != j)) == target_table
        completed[full].append(cap)
        loose_choices[cap].append(rows)
        degrees = tuple(sorted(sum(bool(r & s) for s in rows if r != s) for r in rows))
        meeting_degrees[degrees] += 1
        check_marked(rows, target)
        checked += 1
    if partial:
        return {"four-law choices": total, "bases": basis, "two-holder bases checked": checked}

    # The earlier named alternative uses the root and one four-place law per ring.
    old_loop = [ring_names] + [ring_names ^ r for r in triples]
    assert reduce(and_, (tables[r] for r in old_loop)) == target_table
    assert all(r in minimal for r in old_loop) and max(profile(old_loop, width)) == 3
    degree_counts = {(2, 2, 2, 2): 12, (1, 1, 1, 3): 8}
    assert len(completed) == 4 and checked == 20 and meeting_degrees == degree_counts
    assert set(loose_choices) == minimal and all(len(cs) == 5 for cs in completed.values())
    assert all(set(triples) <= set(full) for full in completed)
    tested = {r: canonical_projection(triples + [ring_names], r, "parity") for r in equations}
    assert {r for r, (passes, _) in tested.items() if passes} == minimal
    assert all(count == len({state & r for state in target}) for r, (_, count) in tested.items())
    return {
        "nine places in order": labels, "joint states": len(target),
        "nonzero equations": len(equations), "inclusion-minimal relations": len(minimal),
        "nonminimal equations": [named(r, labels) for r in equations if r not in minimal],
        "four-law choices tested": total, "independent bases": basis, "bases all of whose relations are minimal": minimal_basis,
        "bases with at most two holders": checked, "of them four relations meeting in a ring": meeting_degrees[2, 2, 2, 2],
        "of them three relations meeting a fourth": meeting_degrees[1, 1, 1, 3],
        "canonical tests on all fifteen projected supports": {
            ",".join(named(r, labels)): {"passes": verdict, "joint values": count}
            for r, (verdict, count) in tested.items()},
        "distinct labelled completions": len(completed),
        "omissions with the same 32 states": sum(len(c) for c in completed.values()),
        "distinct loose sets": len(loose_choices),
        "basis counts per loose set": {",".join(named(r, labels)): len(v) for r, v in sorted(loose_choices.items())},
        "four distinct bases with loose p1,q1,R1": [
            [named(r, labels) for r in p] for p in loose_choices[triples[0]]],
        "distinct arity lists with loose p1,q1,R1": sorted({
            tuple(sorted(r.bit_count() for r in p)) for p in loose_choices[triples[0]]}),
        "completed systems as five equations": [[named(r, labels) for r in full] for full in sorted(completed)],
        "earlier four-place presentation": {"laws": [named(r, labels) for r in old_loop],
                                            "holders per place": profile(old_loop, width),
                                            "joint states": len(allowed(old_loop, "parity", width))},
    }


def pair_costs():
    # Seven consecutive holders, each end and each odd-numbered holder live.
    rows = [0] * 7
    labels = []
    for i, count in enumerate([2, 2, 1, 1, 2, 2]):
        for j in range(count):
            bit = 1 << len(labels)
            labels.append(f"shared-{i}-{i+1}-{j+1}")
            rows[i] |= bit
            rows[i+1] |= bit
    for i, label in zip((0, 1, 3, 5, 6), "acdeb"):
        rows[i] |= 1 << len(labels)
        labels.append(label)
    width = len(labels)
    target = allowed(rows, "parity", width)
    actual = check_marked(rows, target)
    marks = loose(rows, width)
    assert all(is_minimal_projection(target, r) for r in rows)
    pairs = []
    for (a, b), distance in sorted(actual["distances"].items()):
        best_direct = min((z for z in target if (z & marks).bit_count() == 2 and z & a and z & b),
                          key=lambda z: (z.bit_count(), z))
        best_pair = min((z for z in target if all((z & f).bit_count() % 2 == int(f in (a, b))
                                                  for f in actual["families"])),
                        key=lambda z: (z.bit_count(), z))
        assert best_direct.bit_count() == distance + 2
        pairs.append({"first": named(a, labels), "second": named(b, labels), "holder steps": distance,
                      "least change with exactly two loose distinctions": named(best_direct, labels),
                      "least change flipping the two family facts": named(best_pair, labels)})
    direct = sorted({r["holder steps"] for r in pairs})
    indirect = sorted({len(r["least change flipping the two family facts"])-2 for r in pairs})
    assert direct == [1, 6] and indirect == [1, 4]
    partitions = {}
    for threshold in range(max(direct + indirect)+1):
        links = {}
        for r in pairs:
            k = tuple(sorted((mask(*(labels.index(x) for x in r["first"])),
                              mask(*(labels.index(x) for x in r["second"])))))
            links[k] = (r["holder steps"], len(r["least change flipping the two family facts"])-2)
        levels = [partition_masks(components(actual["families"], lambda a, b: links[tuple(sorted((a, b)))][j] <= threshold))
                  for j in (0, 1)]
        assert levels[0] == levels[1]
        partitions[threshold] = [named(group, labels) for group in levels[0]]
    return {"holder rows": [named(r, labels) for r in rows], "states": len(target),
            "start families": [named(f, labels) for f in actual["families"]], "pairs": pairs,
            "recorded holder-step thresholds": direct, "thresholds from unrestricted pair cost minus two": indirect,
            "common partitions at each threshold": partitions}


def compare(left, right, law):
    assert size(left) == size(right)
    width = size(left)
    first = allowed(left, law, width)
    second = allowed(right, law, width)
    assert first == second
    marks = loose(left, width)
    assert marks == loose(right, width)
    details = []
    for rows, states in ((left, first), (right, second)):
        actual = check_marked(rows, states) if law == "parity" else structural(rows, width)
        details.append({"laws": [bits(r) for r in rows], "components": actual["components"],
                        "live holder groups": [bits(h) for h in actual["holders"]],
                        "start families": [bits(f) for f in actual["families"]],
                        "laws that pass the minimal projection test": sum(is_minimal_projection(states, r) for r in rows)})
    return {"law": law, "same labelled allowed states": len(first), "shared loose set": bits(marks),
            "first": details[0], "second": details[1]}


def boundaries():
    # A closed set of four triples. Absorbing one of its equations into an
    # independent open law connects the presentations and changes the row count.
    closed = [mask(3, 4, 5), mask(3, 6, 7), mask(4, 6, 8), mask(5, 7, 8)]
    abc = mask(0, 1, 2)
    disconnected = compare([abc, *closed], [abc | closed[0], *closed[1:]], "parity")
    assert [disconnected[k]["components"] for k in ("first", "second")] == [2, 1]
    # A two-place law is admitted by the relation but excluded by the frozen search.
    b = mask(3, 4, 5)
    ordinary = [mask(0, 1, 3), mask(2, 4, 5), b]
    with_two = [ordinary[0] ^ b, ordinary[1] ^ b, b]
    two = compare(ordinary, with_two, "parity")
    assert min(len(r) for r in two["second"]["laws"]) == 2
    # Complements of the four holder triples are a second NAE presentation
    # of exactly the same closed relation.
    six = [r >> 3 for r in closed]
    empty = loose(six, 6)
    assert empty == 0
    small_caps = []
    for extra in range(3):
        rows = six[:]
        for i in range(extra):
            rows[i] |= 1 << (6+i)
        marked = loose(rows, 6+extra)
        valid = allowed(rows, "parity", 6+extra)
        check_marked(rows, valid)
        small_caps.append({"loose": bits(marked), "states": len(valid),
                           "assignments on the loose set, as positions set to one": [
                               bits(v) for v in sorted({s & marked for s in valid})]})
    disjoint_open = [mask(0, 1, 2), mask(3, 4, 5)]
    both_open = allowed(disjoint_open, "parity", 6)
    assert check_marked(disjoint_open, both_open)["components"] == 2
    assert not is_minimal_projection(both_open, 63)
    closed_nae = compare(six, [63 ^ r for r in six], "not-all-equal")
    return {"different rule counts with a separate closed component": disconnected,
            "a connected presentation acquiring a two-place equation": two,
            "empty loose set": {"original parity states": len(allowed(six, "parity", 6)),
                                "completed bookkeeping equation places": bits(empty),
                                "bookkeeping equation passes minimal projection test": is_minimal_projection([0], empty)},
            "zero, one or two loose distinctions on a connected four-knot start": small_caps,
            "one outside holder on two separate open triples": {
                "projected states on all six loose distinctions": len(both_open),
                "states of even parity on six distinctions": len(allowed([63], "parity", 6))},
            "closed four-triple NAE presentations": closed_nae}


def joined_blocks(pairs):
    # Each group has two holders sharing three names. A single additional
    # shared distinction joins each specified pair of groups.
    rows = [mask(3*i, 3*i+1, 3*i+2) for i in range(4) for _ in range(2)]
    for j, (a, b) in enumerate(pairs, 12):
        rows[2*a] |= 1 << j
        rows[2*b] |= 1 << j
    return [r for i, r in enumerate(rows) if i != 1]


def whitney_blocks():
    first = joined_blocks(((0, 1), (0, 2), (0, 3)))
    second = joined_blocks(((0, 1), (1, 2), (2, 3)))
    record = compare(first, second, "parity")
    states = allowed(first, "parity", 15)
    varying = reduce(or_, states)
    assert bits(((1 << 15)-1) ^ varying) == (12, 13, 14)
    record["three shared distinctions fixed to zero"] = [12, 13, 14]
    profiles = []
    for cropped in (first, second):
        full = [cropped[0], mask(0, 1, 2), *cropped[1:]]
        profiles.append(sorted(((full[2*i] | full[2*i+1]) >> 12).bit_count() for i in range(4)))
    assert profiles == [[1, 1, 1, 3], [1, 1, 2, 2]]
    record["numbers of these three incident to each block of paired holders"] = profiles
    return record


def nae_controls():
    first = [mask(0, 1, 2), mask(0, 3, 4), mask(1, 5, 6), mask(2, 7, 8)]
    marks = loose(first, 9)
    positive = allowed(first, "not-all-equal", 9)
    assert positive == allowed([*first, marks], "not-all-equal", 9)
    assert len({s & marks for s in positive}) == 62
    assert canonical_projection(first, marks, "not-all-equal") == (True, 62)
    second = [mask(0, 1, 2), mask(0, 3, 4)]
    marks2 = loose(second, 5)
    original = allowed(second, "not-all-equal", 5)
    filtered = allowed([*second, marks2], "not-all-equal", 5)
    mixed_pair = mask(1, 3)
    first_change = next((s, s ^ mixed_pair) for s in original if s ^ mixed_pair in original)
    one_triple = allowed([mask(0, 1, 2)], "not-all-equal", 3)
    same_pair = mask(0, 1)
    not_uniform = next((s, s ^ same_pair) for s in one_triple if s ^ same_pair not in one_triple)
    x = mask(0, 1, 2)
    y = mask(3, 4, 5)
    joined = [x, y, x | mask(6, 7), y | mask(6, 8)]
    regrouped = [x, y, x | mask(6, 7, 8), y | mask(6)]
    changed = compare(joined, regrouped, "not-all-equal")
    assert changed["first"]["start families"] != changed["second"]["start families"]
    return {"implied NAE on all six loose distinctions": {
                "four laws": [bits(r) for r in first], "loose": bits(marks), "states before and after": len(positive),
                "projected values on loose distinctions": len({s & marks for s in positive})},
            "adding NAE on all loose distinctions can change states": {
                "two laws": [bits(r) for r in second], "loose": bits(marks2),
                "states before": len(original), "states after": len(filtered),
                "one removed state as positions set to one": bits(next(s for s in original if s not in filtered))},
            "two-flip test under NAE": {
                "two bits at different holders, flipped between two allowed states": bits(mixed_pair),
                "before and after, positions set to one": [bits(s) for s in first_change],
                "two bits at one holder, no uniform translation symmetry": bits(same_pair),
                "allowed and forbidden triple, positions set to one": [bits(s) for s in not_uniform]},
            "two redundant NAE laws with different marked families": changed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    limit = 2 * 1024 ** 3
    resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
    tick = perf_counter()
    sample = nine_facts(partial=True)
    sample_time = perf_counter() - tick
    print(f"64 of 1365 four-law choices at the one-process configuration: {sample_time:.4f}s; "
          f"linear estimate {sample_time * 1365 / 64:.3f}s. {sample}")
    tick = perf_counter()
    calibration = joined_blocks(((0, 1), (0, 2), (0, 3)))
    # The largest truth table below has 15 names. Check a prefix at this width.
    accepted = sum(all((s & r).bit_count() % 2 == 0 for r in calibration) for s in range(2048))
    sample_time = perf_counter() - tick
    print(f"2048 of 32768 assignments for a 15-name table: {sample_time:.4f}s; "
          f"linear estimate {16 * sample_time:.3f}s per table. {accepted} passed the calibration equations.")
    tick = perf_counter()
    triples = [mask(0, 1, 6), mask(2, 3, 7), mask(4, 5, 8), mask(6, 7, 8)]
    assert canonical_projection(triples, sum(1 << i for i in range(9)), "parity") == (False, 32)
    sample_time = perf_counter()-tick
    print(f"Widest of the 15 projected supports, including checker startup: {sample_time:.3f}s; "
          f"15 times that pilot is {15*sample_time:.2f}s.")
    if args.pilot:
        return
    tick = perf_counter()
    result = {"nine facts": nine_facts(), "direct and parity pair costs": pair_costs(), "scope controls": boundaries(),
              "completed systems with different arrangements of separating distinctions": whitney_blocks(),
              "not-all-equal controls": nae_controls()}
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n")
    print(f"Wrote {OUTPUT.name} in {perf_counter() - tick:.3f}s.")


if __name__ == "__main__":
    main()
