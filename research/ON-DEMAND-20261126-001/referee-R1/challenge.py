"""Recheck induced first-round shortages on connected, finite physical starts.

The start is supplied as actual distinctions and their holders. Ordinary rounds
are computed by enumerating complete subsets, allocating each parent's loose
distinctions, and attaching the births to the resulting holdings. The other
referee implementation, growth.py, runs independently on restricted rosters.
"""

import argparse
import io
import json
import resource
import sys
import time
from collections import Counter, defaultdict
from contextlib import redirect_stdout
from functools import lru_cache
from itertools import combinations, permutations, product
from pathlib import Path

from pysat.solvers import Solver

from growth import Roster, grow


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))
from knotlab.cli import main as knotlab


def make_start(before, after, surplus):
    # H and J are spent. X's own live neighbours are V,A,B,C.
    names = list("RVABCXHJ")
    loose = dict(zip(names, (2, 4, 2 + surplus, 2 + surplus, 2 + surplus, 1, 0, 0)))
    pairs = ["XV", "XA", "XB", "XC", "AB", "CJ", "XJ", "RH", "VH", "HJ"]
    shared = [tuple(pair) for pair in pairs]

    def extend(first, count, prefix):
        last = first
        for i in range(1, count + 1):
            new = f"{prefix}{i}"
            holder = f"{prefix}{i}h"
            names.extend((new, holder))
            loose[new], loose[holder] = 2, 0
            shared.extend(((last, holder), (new, holder), ("H", holder)))
            last = new
        return last

    reader = extend("R", before, "U")
    if after:
        # X now owes one further pair.
        loose["X"] += 1
        extend("X", after, "Y")
    holdings = [[] for _ in names]
    for number, (a, b) in enumerate(shared, 1):
        holdings[names.index(a)].append(number)
        holdings[names.index(b)].append(number)
    next_number = len(shared) + 1
    for k, name in enumerate(names):
        holdings[k].extend(range(next_number, next_number + loose[name]))
        next_number += loose[name]
    assert all(len(star) >= 3 for star in holdings)
    return names, tuple(tuple(star) for star in holdings), names.index(reader)


def owners(holdings):
    out = defaultdict(set)
    for i, star in enumerate(holdings):
        assert len(star) == len(set(star))
        for d in star:
            out[d].add(i)
    assert all(1 <= len(pair) <= 2 for pair in out.values())
    return out


def physical_neighbours(holdings):
    meetings = [set() for _ in holdings]
    for owner_set in owners(holdings).values():
        if len(owner_set) == 2:
            a, b = owner_set
            meetings[a].add(b)
            meetings[b].add(a)
    return meetings


def steps(neighbours, reader):
    distances = {}
    layer = {reader}
    depth = 0
    while layer:
        distances.update((k, depth) for k in layer)
        layer = set().union(*(neighbours[k] for k in layer)) - distances.keys()
        depth += 1
    return distances


def groups(members, meetings):
    # Visit every complete subset in increasing order. Keep the largest that
    # lack a common holder, then visit the uncovered candidate pairs.
    blocks = [members & neighbours for neighbours in meetings]
    pairs = {pair for block in blocks for pair in combinations(sorted(block), 2)}
    neighbours = {v: set() for v in members}
    for a, b in pairs:
        neighbours[a].add(b)
        neighbours[b].add(a)
    unheld = set()

    def extend(part, choices):
        for i, v in enumerate(choices):
            grown = part | {v}
            if len(grown) >= 3 and all(not grown <= block for block in blocks):
                unheld.add(frozenset(grown))
            extend(grown, [w for w in choices[i + 1:] if w in neighbours[v]])

    extend(set(), sorted(members))
    maximal = [g for g in unheld if all(not g < other for other in unheld)]
    for g in maximal:
        pairs.difference_update(combinations(sorted(g), 2))
    return sorted([tuple(sorted(g)) for g in maximal] + list(pairs))


def physical_growth(initial, region, reader, rounds, law):
    holdings = list(initial)
    next_number = max(d for star in holdings for d in star) + 1
    members = set(region)
    signals = {k: ("start", 0, 0, len(holdings[k])) for k in members}
    descendants = {reader}
    all_views = []
    traces = []
    end = "rounds"
    for _ in range(rounds):
        degree = owners(holdings)
        meetings = physical_neighbours(holdings)
        joined = groups(members, meetings)
        demand = Counter(k for group in joined for k in group)
        available = {k: sorted(d for d in holdings[k] if len(degree[d]) == 1) for k in members}
        short = {k: [demand[k], len(available[k])] for k in members if demand[k] > len(available[k])}
        row = {"groups": joined, "owing": dict(sorted(demand.items())), "short": short}
        traces.append(row)
        if short:
            end = "stall"
            break
        parents = joined + [(k,) for k in sorted(members) for _ in range(len(available[k]) - demand[k])]
        born = {}
        for group in parents:
            new = len(holdings)
            holdings.append(tuple(available[k].pop() for k in group))
            born[new] = group
        assert all(not ds for ds in available.values())
        proposed = groups(set(born), physical_neighbours(holdings))
        next_demand = Counter(k for group in proposed for k in group)
        closing = law == "parity" and len(born) == 1
        plain, with_parents = Counter(), Counter()
        new_descendants = set()
        for new, group in born.items():
            p = len(group)
            fresh = 0 if closing else max(1, 3 - p, next_demand[new])
            holdings[new] += tuple(range(next_number, next_number + fresh))
            next_number += fresh
            description = ("offshoot" if p == 1 else "join", p, fresh, p + fresh)
            signals[new] = description
            if any(k in descendants for k in group):
                new_descendants.add(new)
                plain[description] += 1
                with_parents[(description, tuple(sorted(signals[p] for p in group)))] += 1
        all_views.append((plain, with_parents))
        row["births"] = len(born)
        descendants, members = new_descendants, set(born)
        if closing:
            end = "closed"
            break
    all_views.extend((Counter(), Counter()) for _ in range(rounds - len(all_views)))
    return end, tuple(all_views), traces, holdings


def permitted(bits, law):
    if law == "nae":
        return len(set(bits)) == 2
    return sum(bits) % 2 == 0


def blocked_clause(star, bits):
    return [-v if bit else v for v, bit in zip(star, bits)]


@lru_cache(maxsize=None)
def canonical_projection(arity, denied):
    labels = [f"d{i}" for i in range(arity)]
    cnf = "; ".join(" ".join(("~" if bit else "") + label for bit, label in zip(row, labels))
                    for row in denied)
    args = ["check", "--cnf", cnf, "--loops", *labels[:-1], "--contact", labels[-1], "--json"]
    result = io.StringIO()
    with redirect_stdout(result):
        assert knotlab(args) == 0
    return json.loads(result.getvalue())


def projections(holdings, law):
    # Pin every local pattern against the whole conjunction before giving the
    # actual projected relation, represented by all its forbidden rows, to the
    # canonical command. Only identical projected relations share a check.
    clauses = [blocked_clause(star, bits) for star in holdings
               for bits in product((0, 1), repeat=len(star)) if not permitted(bits, law)]
    results = []
    with Solver(bootstrap_with=clauses) as solver:
        for star in holdings:
            denied = []
            for bits in product((0, 1), repeat=len(star)):
                assumptions = [v if bit else -v for v, bit in zip(star, bits)]
                allowed = solver.solve(assumptions=assumptions)
                assert allowed == permitted(bits, law)
                if not allowed:
                    denied.append(bits)
            verdict = canonical_projection(len(star), tuple(denied))
            assert verdict["is_knot"]
            results.append({"places": len(star), "allowed states": len(verdict["allowed"]),
                            "K1": verdict["binding"], "K2": verdict["loss_on_erasure"],
                            "K3": verdict["coexistence"]})
    return results


def serial_views(views):
    return [[[[key, count] for key, count in sorted(counter.items())] for counter in readings]
            for readings in views]


def scenario(before, after, surplus, rounds, law, pilot):
    names, holdings, reader = make_start(before, after, surplus)
    meetings = physical_neighbours(holdings)
    assert len(steps(meetings, reader)) == len(holdings)
    roster = Roster.from_holdings(holdings)
    live = set(roster.loose)
    near = {k: set().union(*(meetings[h] & live for h in meetings[k])) - {k} for k in live}
    distances = steps(near, reader)
    assert distances == roster.steps_from(reader)
    ball = frozenset(k for k, d in distances.items() if d <= rounds + 1)
    assert ball == roster.within(reader, rounds + 1)
    extra = sorted(live - ball)
    checks = [frozenset(take) for length in range(len(extra) + 1) for take in combinations(extra, length)]
    full = physical_growth(holdings, live, reader, rounds, law)
    full_roster = grow(roster, rounds, law=law)
    assert full[0] == full_roster.end == "rounds"
    assert full[1] == full_roster.views(reader, rounds)
    first = {k: v for k, v in full[2][0].items() if k != "short"}
    first["groups"] = [[names[k] for k in g] for g in first["groups"]]
    first["owing"] = {names[k]: v for k, v in first["owing"].items()}
    all_holders = set().union(*(meetings[k] for k in ball))
    result = {"left links added": before, "right links added": after, "extra loose at each of A,B,C": surplus,
              "law": law, "rounds": rounds, "reader": names[reader], "knot order": names,
              "start holdings": holdings, "loose": {names[k]: n for k, n in roster.loose.items()},
              "start projections": projections(holdings, law),
              "full first round": first, "full births per round": [row["births"] for row in full[2]],
              "full reader views": serial_views(full[1]), "ball": sorted(names[k] for k in ball),
              "holder steps": {names[k]: n for k, n in sorted(distances.items())},
              "holders met by the ball": sorted(names[k] for k in all_holders),
              "holders displaying at least two ball members": {
                  names[h]: sorted(names[k] for k in meetings[h] & ball)
                  for h in sorted(all_holders) if len(meetings[h] & ball) >= 2}}
    if before == after == surplus == 0:
        result["projections on the whole structure after round one"] = projections(full[3], law)
    bad = set()
    covered = Counter()
    for additions in checks[:1] if pilot else checks:
        region = ball | additions
        got = physical_growth(holdings, region, reader, rounds, law)
        reduced = grow(roster.restrict(region), rounds, law=law)
        assert got[0] == reduced.end and got[1] == reduced.views(reader, rounds)
        assert {k: tuple(v) for k, v in got[2][0]["short"].items()} == reduced.shortages
        differences = [i + 1 for i, (v1, v2) in enumerate(zip(got[1], full[1])) if v1 != v2]
        covered[(got[0], bool(differences))] += 1
        if differences:
            bad.add(additions)
        if not additions:
            row = got[2][0]
            result["ball first round"] = {"groups": [[names[k] for k in g] for g in row["groups"]],
                                          "owing": {names[k]: v for k, v in row["owing"].items()},
                                          "short, owing and loose": {names[k]: v for k, v in row["short"].items()}}
            result["ball reader views"] = serial_views(got[1])
            result["rounds where the ball differs"] = differences
    result["regions by end and comparison"] = {
        f"{end}, {'different' if differs else 'same'}": count for (end, differs), count in sorted(covered.items())}
    result["additions giving a different view"] = sorted(sorted(names[k] for k in s) for s in bad)
    if not pilot:
        orders = list(permutations(extra))
        mid = len(extra) // 2
        mids = list(combinations(extra, mid))
        result["admissions"] = {"all distinct half-steps": len(mids),
                                "differing half-steps": sum(frozenset(m) in bad for m in mids),
                                "all orders": len(orders),
                                "orders with a differing prefix, including the ball": sum(
                                    any(frozenset(order[:i]) in bad for i in range(len(order) + 1))
                                    for order in orders)}
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", action="store_true", help="compare one region at each exact configuration")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (3 << 30, 3 << 30))
    started = time.monotonic()
    rows = []
    # Three requested horizons with the same omitted knot. In the last case
    # the ball is funded, and its six optional members have 20 half-steps.
    for before, after, rounds in [(0, 0, 1), (1, 0, 2), (2, 0, 3), (1, 2, 1)]:
        for surplus in (0, 1):
            for law in ("nae", "parity"):
                mark = time.monotonic()
                row = scenario(before, after, surplus, rounds, law, args.pilot)
                if args.pilot:
                    row = {key: row[key] for key in (
                        "left links added", "right links added", "extra loose at each of A,B,C",
                        "rounds", "law", "full births per round", "regions by end and comparison")}
                row["seconds"] = round(time.monotonic() - mark, 6)
                rows.append(row)
    report = {"weighting": "Each listed hand-built input once per law and stated surplus.",
              "pilot": args.pilot, "memory limit bytes": 3 << 30, "cases": rows,
              "seconds": round(time.monotonic() - started, 6),
              "peak resident KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(f"{len(rows)} start-law cases in {report['seconds']} seconds")


if __name__ == "__main__":
    main()
