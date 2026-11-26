"""Check frozen start identities, independent growth, and pins across the recorded cuts."""

import argparse
import hashlib
import json
import sys
from collections import Counter
from functools import reduce
from itertools import islice
from operator import xor
from pathlib import Path
from random import Random

from growth import ARMS, RESEARCH, census, components, heldout, joined, meetings, ring, round_detail


HERE = Path(__file__).resolve().parent


def parity_row(distinctions):
    return sum(1 << d for d in distinctions)


def reduce_row(word, basis):
    while word:
        pivot = word.bit_length() - 1
        if pivot not in basis:
            break
        word ^= basis[pivot]
    return word


def parity_basis(stage):
    basis = {}
    for row in stage:
        rest = reduce_row(parity_row(row), basis)
        if rest:
            basis[rest.bit_length() - 1] = rest
    return basis


def parity_states(stage):
    domain = parity_row(set().union(*stage))
    rows = [parity_row(row) for row in stage]
    states = [0]
    word = domain
    while word:
        if all((word & row).bit_count() % 2 == 0 for row in rows):
            states.append(word)
        word = (word - 1) & domain
    return states


def archive_check(cohort, path, pilot):
    lines = path.read_text().splitlines()
    if not pilot:
        assert len(cohort) == len(lines)
    archives = (json.loads(line) for line in lines)
    checked = Counter()
    for (name, stage), entry in zip(cohort.items(), islice(archives, len(cohort)), strict=True):
        neighbours, loose = meetings(stage)
        all_in_one = len(next(components(neighbours))) == len(stage)
        shared_counts = [len(row) - len(open_stock) for row, open_stock in zip(stage, loose, strict=True)]
        is_ring = all_in_one and len(stage) >= 3 and all(n == 2 for n in shared_counts) and all(
            len(adjacent) == 2 for adjacent in neighbours
        )
        assert name == entry["start"]
        assert len(stage) == entry["knots"] and all_in_one
        assert [len(open_stock) for open_stock in loose] == entry["loose"]
        assert max(shared_counts) == entry["most shared distinctions at a knot"]
        assert is_ring == entry["one ring"]
        _, status, _ = round_detail(stage)
        for field in ("pinned exchange", "free exchange"):
            expected = f"does not grow ({status})"
            assert (entry[field] == expected) if status != "funded" else not entry[field].startswith("does not grow")
        checked[status] += 1
    return dict(sorted(checked.items()))


def nae_implication(solver, support):
    # The complement symmetry makes one of the two constant words sufficient.
    return not solver.solve(assumptions=[-d - 1 for d in sorted(support)])


def nae_clauses(stage):
    for row in stage:
        yield [d + 1 for d in sorted(row)]
        yield [-d - 1 for d in sorted(row)]


def witness(name, start, stage, births, **details):
    return {"start": name, "start supports": [sorted(row) for row in start],
            "grown supports": [sorted(row) for row in stage],
            "births": [{"parents": b.parents, "inputs": sorted(b.taken), "demand": b.demand,
                        "implied": b.implied, "ordinary fresh count": b.ordinary_fresh,
                        "fresh": sorted(b.fresh)} for b in births], **details}


def projected_states(states, distinctions):
    return sorted({"".join(str((word >> d) & 1) for d in distinctions) for word in states})


def parity_audit(name, start, status, stage, births, tally, examples):
    old_basis = parity_basis(start)
    new_basis = parity_basis(stage)
    old_loose = set().union(*meetings(start)[1])
    new_neighbours, new_loose = meetings(stage)
    fresh = set().union(*new_loose)
    assert fresh == set().union(*(b.fresh for b in births))
    assert Counter(d for b in births for d in b.taken) == Counter(old_loose)
    pins = {d for d in fresh if reduce_row(1 << d, new_basis) == 0}
    pins_from_counts = set()
    for part in components(new_neighbours):
        stock = set().union(*(new_loose[i] for i in part))
        if len(stock) == 1:
            pins_from_counts.update(stock)
    assert pins == pins_from_counts
    assert all(b.implied == (reduce_row(parity_row(b.taken), old_basis) == 0) for b in births)
    assert all(not b.implied or b.demand == 0 for b in births)
    newly_fixed_spent = {d for d in old_loose if reduce_row(1 << d, old_basis) and reduce_row(1 << d, new_basis) == 0}
    tally["funded rounds without any loose distinction after growth"] += not fresh
    tally["rounds leaving fresh loose distinctions"] += bool(fresh)
    tally["fresh loose distinctions"] += len(fresh)
    tally["rounds fixing a fresh loose distinction"] += bool(pins)
    tally["fixed fresh loose distinctions"] += len(pins)
    tally["rounds newly fixing a consumed loose distinction"] += bool(newly_fixed_spent)
    tally["newly fixed consumed loose distinctions"] += len(newly_fixed_spent)
    if pins:
        examples["fresh pins"].append({"start": name, "distinctions": sorted(pins)})
        if "first fresh pin" not in examples:
            assert len(pins) == 1 and len(fresh) == 1 and status == "funded"
            old_states = parity_states(start)
            grown_states = parity_states(stage)
            ordinary, _, _ = round_detail(start)
            ordinary_states = parity_states(ordinary)
            old_mask = parity_row(set().union(*start))
            spent = next(b for b in births if not b.fresh and not b.implied)
            pinned_birth = next(b for b in births if b.fresh & pins)
            projected_support = sorted(pinned_birth.taken | pinned_birth.fresh)
            old_false = min((word for word in old_states if (word & parity_row(spent.taken)).bit_count() % 2),
                            key=lambda word: (word.bit_count(), word))
            sum_of_rows = reduce(xor, map(parity_row, stage))
            assert sum_of_rows == parity_row(pins)
            examples["first fresh pin"] = witness(
                name, start, stage, births,
                **{"fixed fresh distinction": next(iter(pins)), "fixed value": 0,
                   "sum of grown rows": sorted(pins), "old states": len(old_states),
                   "old states with a cut completion": len({word & old_mask for word in grown_states}),
                   "old states with an ordinary completion": len({word & old_mask for word in ordinary_states}),
                   "old allowed state with no cut completion, distinctions at one": [d for d in sorted(set().union(*start))
                                                                                   if old_false & (1 << d)],
                   "cut states": len(grown_states), "ordinary states": len(ordinary_states),
                   "ordinary loose distinctions": sorted(set().union(*meetings(ordinary)[1])),
                   "birth projection distinction order": projected_support,
                   "cut projection on this birth": projected_states(grown_states, projected_support),
                   "ordinary projection on this birth": projected_states(ordinary_states, projected_support),
                   "ordinary supports": [sorted(row) for row in ordinary]}
            )
    unary_implied = next((b for b in births if b.implied and len(b.taken) == 1), None)
    if unary_implied and "first implied unary birth" not in examples:
        assert not unary_implied.fresh and reduce_row(parity_row(unary_implied.taken), old_basis) == 0
        examples["first implied unary birth"] = witness(name, start, stage, births,
                                                         **{"already fixed input": next(iter(unary_implied.taken))})


def arm_audit(cohort):
    from pysat.solvers import Solver

    totals = {law: {arm: Counter() for arm in ARMS} for law in ("parity", "not-all-equal")}
    examples = {arm: {"fresh pins": []} for arm in ARMS}
    for name, start in cohort.items():
        with Solver(bootstrap_with=nae_clauses(start)) as old_nae:
            assert old_nae.solve()
            for law, tallies in totals.items():
                implied = None if law == "parity" else lambda support: nae_implication(old_nae, support)
                for arm, tally in tallies.items():
                    stage, status, births = round_detail(start, arm, implied)
                    tally[status] += 1
                    if status != "funded":
                        continue
                    tally["births"] += len(births)
                    tally["implied births"] += sum(b.implied for b in births)
                    tally["implied births without fresh distinctions"] += sum(b.implied and not b.fresh for b in births)
                    tally["nonimplied births without fresh distinctions"] += sum(not b.implied and not b.fresh for b in births)
                    for b in births:
                        if len(b.taken | b.fresh) < 3:
                            assert b.implied
                            tally[f"implied births of {len(b.taken | b.fresh)} places"] += 1
                    if law == "parity":
                        parity_audit(name, start, status, stage, births, tally, examples[arm])
                    else:
                        with Solver(bootstrap_with=nae_clauses(stage)) as after:
                            tally["funded rounds with an allowed state"] += after.solve()
    return {"counts": totals, "parity witnesses": examples}


def recode(stage, rng):
    order = rng.sample(range(len(stage)), len(stage))
    names = sorted(set().union(*stage))
    labels = dict(zip(names, rng.sample(range(4 * len(names)), len(names)), strict=True))
    return order, tuple(frozenset(labels[d] for d in stage[i]) for i in order)


def birth_signature(births, parent_names):
    return Counter((tuple(sorted(parent_names[i] for i in b.parents)), b.demand,
                    b.implied, b.ordinary_fresh, len(b.fresh)) for b in births)


def compare(name, stage, tally, rng, shared_round, engine):
    from pysat.solvers import Solver

    order, relabeled = recode(stage, rng)
    for law in ("parity", "nae"):
        for arm in ARMS:
            own_records = []
            for source in (stage, relabeled):
                with Solver(bootstrap_with=nae_clauses(source)) as solver:
                    implied = None if law == "parity" else lambda support: nae_implication(solver, support)
                    ours, status, births = round_detail(source, arm, implied)
                reference, info = shared_round(tuple(tuple(sorted(row)) for row in source), law, arm, engine)
                assert status == info["status"], (name, law, arm)
                if reference is not None:
                    assert ours == tuple(map(frozenset, reference)), (name, law, arm)
                    for b, row in zip(births, info["births"], strict=True):
                        assert (b.parents, b.taken, b.demand, b.implied, b.ordinary_fresh, b.fresh) == (
                            row["parents"], frozenset(row["inputs"]), row["D"], row["old_inputs_already_imply_law"],
                            row["q"], frozenset(row["fresh"]))
                tally[status] += 1
                own_records.append((status, births))
            (status, births), (other_status, other_births) = own_records
            assert status == other_status
            assert birth_signature(births, range(len(stage))) == birth_signature(other_births, order)
            tally["paired relabeling comparisons"] += 1


def shared_comparison(panels, pilot):
    experiment = RESEARCH.parent / "experiments"
    sys.path.insert(0, str(experiment / "NAE-GROWTH-20261119-001B/NAE-GROWTH-20261119-001B-E001_nae"))
    sys.path.insert(0, str(experiment / "FORBIDDING-JOIN-20261120-001B/FORBIDDING-JOIN-20261120-001B-E001_free_readings"))
    import naelib as shared_engine
    from rival_growth import grow as shared_round

    rng = Random(20261210)
    cases = {}
    for panel in panels.values():
        for n in sorted(set(map(len, panel.values()))):
            choices = [name for name, stage in panel.items() if len(stage) == n]
            for name in rng.sample(choices, min(4, len(choices))):
                cases[name] = panel[name]
    if not pilot:
        for i in (165, 1590, 1665, 1689, 1795):
            cases[f"census {i}"] = census()[i]
        cases["held out 7-179"] = heldout()[7, 179]
    for n in range(3, 11):
        cases[f"ring of {n} knots with two loose each"] = ring(n)
    cases["closed four-knot parity start"] = round_detail(ring(3, 1))[0]
    cases["one-loose four-knot start"] = (frozenset({0, 1, 2, 6}), frozenset({0, 3, 4}),
                                         frozenset({1, 3, 5}), frozenset({2, 4, 5}))
    apart = tuple(frozenset(d + 20 for d in row) for row in ring(3, 1))
    cases["one live ring beside a closing ring"] = ring(5) + apart
    for n in (4, 5, 6, 7, 8):
        first, status, _ = round_detail(ring(n))
        if status == "funded":
            cases[f"ring of {n} knots grown for one round"] = first
    tally = Counter()
    for name, stage in cases.items():
        compare(name, stage, tally, rng, shared_round, shared_engine)
    return {"seed": 20261210, "sources": list(cases), "counts": tally}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, help="check this prefix of each frozen cohort for a timed pilot")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    pilot = args.limit is not None
    panels = {"census": {f"census {i}": stage for i, stage in enumerate(census()[:args.limit])},
              "heldout": {f"held out {n}-{i}": stage for (n, i), stage in islice(heldout().items(), args.limit)}}
    result = {
        "growth source": "Independent round reconstruction. Shared growth is used only as a separate comparator.",
        "census source": "Archived FORBID-EDITS-20261126-001/starts.json in its recorded order",
        "census source sha256": hashlib.sha256((RESEARCH / "FORBID-EDITS-20261126-001/starts.json").read_bytes()).hexdigest(),
        "heldout source": "Reconstructed labelled draws with replacement using seed 20261206 plus the knot count",
        "archive check fields": ["start", "knots", "loose", "most shared distinctions at a knot", "one ring", "funding"],
        "archive counts": {name: archive_check(panel, HERE.parent / f"recur_{name}.jsonl", pilot)
                           for name, panel in panels.items()},
        "shared growth comparison": shared_comparison(panels, pilot),
        "arm audit": {name: arm_audit(panel) for name, panel in (panels | {"built controls": joined()}).items()},
    }
    serialized = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(serialized)
    else:
        print(serialized, end="")


if __name__ == "__main__":
    main()
