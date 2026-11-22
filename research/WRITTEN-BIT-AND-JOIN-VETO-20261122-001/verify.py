"""Independent construction and whole-presentation knot checks for the recorded veto.

Run with .venv/bin/python -B. The proposer below uses only parent co-occurrence
in these three cohorts. The separately bound replay uses the project planners.
"""
import argparse
import json
import os
import subprocess
import sys
from collections import Counter
from functools import lru_cache
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path

from pysat.solvers import Minisat22


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARMS = {"signal": (1, 0, 1), "diverted": (0, 1, 1), "quiet": (0, 0, 0)}
KNOT_CHECKS = {}
PROJECTIONS = Counter()


def words(width):
    return product((0, 1), repeat=width)


def lawful(row, law):
    return sum(row) % 2 == 0 if law == "parity" else min(row) != max(row)


@lru_cache(None)
def local_cnf(width, law):
    return tuple(tuple(-(i + 1) if bit else i + 1 for i, bit in enumerate(row))
                 for row in words(width) if not lawful(row, law))


@lru_cache(None)
def check_board(stars, law):
    """Project each complete static presentation; minimum fills do not restrict K1–K3."""
    clauses = [[(row[abs(x) - 1] + 1) * (1 if x > 0 else -1) for x in clause]
               for row in stars for clause in local_cnf(len(row), law)]
    with Minisat22(bootstrap_with=clauses) as solver:
        for row in stars:
            for values in words(len(row)):
                assumptions = [(bit + 1) * (1 if v else -1) for bit, v in zip(row, values)]
                assert solver.solve(assumptions=assumptions) == lawful(values, law)
            PROJECTIONS[law] += 1
            key = f"{law}-{len(row)}"
            if key not in KNOT_CHECKS:
                names = [f"x{i}" for i in range(1, len(row) + 1)]
                cnf = ";".join(" ".join(("~" if v < 0 else "") + names[abs(v) - 1]
                                       for v in clause) for clause in local_cnf(len(row), law))
                args = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", cnf,
                        "--loops", *names[:-1], "--contact", names[-1], "--json"]
                env = dict(os.environ, PYTHONPATH=str(ROOT / "tools"))
                report = json.loads(subprocess.check_output(args, env=env, cwd=ROOT))
                assert report["is_knot"] and report["invisible_in_parts"]
                KNOT_CHECKS[key] = list(report["allowed"])
    return True


def candidate_groups(blocks):
    """Positive-age siblings meet through their actual parent. The founder is alone."""
    live = sorted({v for block in blocks for v in block})
    pairs = {pair for block in blocks for pair in combinations(sorted(block), 2)}
    larger = [set(row) for n in range(3, len(live) + 1) for row in combinations(live, n)
              if all(p in pairs for p in combinations(row, 2))
              and not any(set(row) <= block for block in blocks)]
    maximal = [s for s in larger if not any(s < other for other in larger)]
    groups = [tuple(sorted(s)) for s in maximal]
    groups.extend(p for p in pairs if not any(set(p) <= s for s in maximal))
    return sorted(groups)


def blocks_of(parents, offset):
    members = {}
    for i, row in enumerate(parents, offset):
        for v in row:
            members.setdefault(v, set()).add(i)
    return list(members.values())


def local_extensions(paid, old_reference, old_actual, count, law, transport):
    actual = tuple(old_actual[i] for i in paid)
    ref = tuple(old_reference[i] for i in paid)
    reference_words = [w for w in words(count) if lawful(ref + w, law)]
    if law == "parity":
        chosen = (0,) * count
        assert chosen in reference_words
    elif transport == "opposite" and len(set(ref)) == 1:
        chosen = (1 - ref[0],) * count
        assert chosen in reference_words
    else:
        chosen = min(reference_words)
    possible = [w for w in words(count) if lawful(actual + w, law)]
    costs = [sum(x != y for x, y in zip(w, chosen)) for w in possible]
    return chosen, tuple(w for w, cost in zip(possible, costs) if cost == min(costs))


def roster(stars, blocks, ref, actual, law, guarded):
    candidates = candidate_groups(blocks)
    hot = {v for v, row in enumerate(stars) if any(ref[d] != actual[d] for d in row)}
    kept = [g for g in candidates if not guarded or not hot.intersection(g)]
    counts = Counter(d for row in stars for d in row)
    loose = {v: [d for d in row if counts[d] == 1] for v, row in enumerate(stars)}
    used = Counter(v for g in kept for v in g)
    assert all(n <= len(loose[v]) for v, n in used.items())
    parents = kept + [(v,) for v, bank in loose.items() for _ in range(len(bank) - used[v])]
    implied = law == "parity" and len(parents) == 1
    next_blocks = blocks_of(parents, len(stars))
    demand = Counter(v for g in candidate_groups(next_blocks) for v in g)
    names = iter(range(len(ref), len(ref) + 1000))
    available = {v: iter(ds) for v, ds in loose.items()}
    fresh, paid = [], []
    for i, family in enumerate(parents, len(stars)):
        paid.append(tuple(next(available[v]) for v in family))
        count = 0 if implied else max(demand[i], 1, 3 - len(family))
        fresh.append(tuple(next(names) for _ in range(count)))
    extended = stars + tuple(p + f for p, f in zip(paid, fresh))
    check_board(extended, law)
    return candidates, parents, paid, fresh, extended, next_blocks


def explore(law, transport, guard, arm, archived_rows):
    starts = (0, 0, 0) if law == "parity" else (1, 1, 0)
    actual = tuple(a ^ b for a, b in zip(starts, ARMS[arm]))
    assert lawful(actual, law) and lawful(starts, law)
    stars = ((0, 1, 2),)
    check_board(stars, law)
    records, predecision, target_use = Counter(), Counter(), Counter()
    final_counts = Counter()
    example = {}
    signatures = Counter()

    def visit(stars, blocks, ref, actual, depth, writer=None, bank=(), target=()):
        assert all(lawful(tuple(w[i] for i in s), law) for w in (ref, actual) for s in stars)
        groups, parents, paid, fresh, full_stars, next_blocks = roster(stars, blocks, ref, actual, law, guard)
        if depth == 1:
            writer = len(stars) + paid.index((0,))
            bank = fresh[writer - len(stars)]
            assert len(bank) == 2
        elif depth == 2:
            target = tuple(len(stars) + i for i, (f, p) in enumerate(zip(parents, paid))
                           if f == (writer,) and len(p) == 1 and p[0] in bank)
        extensions = [local_extensions(p, ref, actual, len(f), law, transport) for p, f in zip(paid, fresh)]
        new_ref = ref + sum((r for r, _ in extensions), ())
        if depth == 3:
            present = len(target) == 2 and target in groups
            outcome = "absent" if not present else "join" if target in parents else "veto"
            deviations = ()
            if present:
                inputs = tuple(d for v in target for d in stars[v])
                assert not set(inputs) & {0, 1, 2} and len(set(inputs)) == len(inputs)
                deviations = tuple(d for d in inputs if actual[d] != ref[d])
                inherited = [d for d in deviations if d in bank]
                companions = [d for d in deviations if d not in bank]
                predecision[f"{len(inherited)} carried, {len(companions)} companions"] += 1
                selected = [p for p in parents if set(p) & set(target)]
                target_use[(outcome, len(selected), len(parents))] += 1
                assert sum(len(set(p) & set(target)) for p in selected) == 4
                # The ordinary step on this very preguard presentation.
                if guard:
                    alt = roster(stars, blocks, ref, actual, law, False)
                    assert target in alt[1]
                example.setdefault(outcome, dict(target=target, writer_bank=bank, holdings=[stars[v] for v in target],
                    reference=[ref[d] for d in inputs], actual=[actual[d] for d in inputs], paid_at_decision=paid,
                    final_parents=parents))
            records[outcome] += 1
            multiplicity = 1
            for _, candidates in extensions:
                multiplicity *= len(candidates)
            # New banks are disjoint and can be combined independently on this complete roster.
            final_counts[outcome] += multiplicity
            signatures[(ref, actual, tuple(sorted(parents)), tuple(sorted(deviations)), multiplicity)] += 1
            return
        for branch in product(*(opts for _, opts in extensions)):
            visit(full_stars, next_blocks, new_ref, actual + sum(branch, ()), depth + 1, writer, bank, target)

    visit(stars, [{0}], starts, actual, 1)
    observed = Counter()
    for row in archived_rows["preguard_histories"]:
        deciding = row["deciding_cut"]
        key = (tuple(map(int, row["reference_through_second_cut"])),
               tuple(map(int, row["actual_through_second_cut"])),
               tuple(sorted(tuple(s) for s in deciding["parent_roster"])),
               tuple(row["target"]["all_differences"]), deciding["number_of_final_fills"])
        observed[key] += 1
    assert signatures == observed, (law, transport, guard, arm)
    assert sum(final_counts.values()) == archived_rows["terminal_history_count"]
    return dict(predecision=dict(records), terminal=dict(final_counts), guard_deviations=dict(predecision),
                actual_births={str(key): value for key, value in sorted(target_use.items())}, example=example)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path, help="write the verification receipt")
    args = parser.parse_args()
    replay_path, = (ROOT / "artifacts" / (HERE.name + "A")).glob("*/results.json")
    replay = json.loads(replay_path.read_text())["study"]
    result = {}
    for law, transport, setting in (("parity", "zero", "parity_zero"), ("nae", "lex", "nae_lexicographic"),
                                   ("nae", "opposite", "nae_opposite_on_homogeneous_reference")):
        for rule, table in (("veto", "feedback"), ("ordinary", "ordinary_continuous_from_same_founder")):
            for arm, stored in (("signal", "signal"), ("diverted", "diversion"), ("quiet", "quiet")):
                result[f"{law}-{transport}-{rule}-{arm}"] = explore(
                    law, transport, rule == "veto", arm, replay[setting][table][stored])
    receipt = {"controls": result, "complete_star_projections": dict(PROJECTIONS),
               "canonical_projected_knot_relations": KNOT_CHECKS, "distinct_static_boards": check_board.cache_info().currsize,
               "all_preguard_words_rosters_deviations_and_final_factors_match": True,
               "compared_replay_sha256": sha256(replay_path.read_bytes()).hexdigest()}
    encoded = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.write:
        args.write.write_text(encoded)
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()

