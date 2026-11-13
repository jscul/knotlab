"""Exact finite profiles for bounded knot-bonds on a fixed recursive branch.

No corpus census is run.  Every reported answer follows completed profile
saturation and an exact repeated target-profile vector, never a depth cutoff.
Use --fixture NAME --k K for an individual control, or run all controls.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations, permutations, product
import hashlib
import json
from pathlib import Path
import os
import subprocess
import sys
import time

from pysat.solvers import Solver

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


class ResourceLimit(RuntimeError):
    pass


@dataclass(frozen=True)
class Definition:
    ports: int
    own: int
    knots: tuple
    calls: tuple
    first: int | None = 0


def powerset(items):
    return [tuple(s) for size in range(len(items) + 1) for s in combinations(items, size)]


def is_bond(states, size):
    """K1--K3, with the glossary's >=3 distinctions, not two-variable ties."""
    if size < 3 or not states or len(states) == 1 << size:
        return False
    return all(len({s[:j] + s[j + 1:] for s in states}) == 1 << (size - 1)
               for j in range(size))


class Profiles:
    def __init__(self, definitions, budget, max_profiles=100000, max_states=10000):
        assert budget >= 0
        self.definitions = tuple(definitions)
        self.budget = budget
        # At least one selected variable is a top port.  The remaining
        # observations, including target label zero, need at most k-1 labels.
        self.labels = tuple(range(max(budget - 1, 0)))
        self.subsets = powerset(self.labels)
        self.target_subsets = [j for j in self.subsets if 0 in j]
        self.max_profiles = max_profiles
        self.max_states = max_states
        for d in self.definitions:
            assert d.ports >= 1 and d.own >= 0
            for knot in d.knots:
                assert len(knot) == len(set(knot)) == 3
                assert all(0 <= x < d.ports + d.own for x in knot)
            for callee, actual in d.calls:
                assert len(actual) == self.definitions[callee].ports
                assert all(0 <= x < d.ports + d.own for x in actual)
            assert d.first is None or 0 <= d.first < len(d.calls)
        self.greatest, self.greatest_rounds = self.unmarked()
        self.unrestricted, self.closure_rounds = self.saturate()

    @lru_cache(maxsize=300000)
    def compose(self, typ, labels, owned, child_labels, child_relations):
        d = self.definitions[typ]
        owner = dict(owned)
        remaining = tuple(j for j in labels if j not in owner)
        coordinates = {j: d.ports + d.own + n for n, j in enumerate(remaining)}
        coordinates.update(owner)
        relation = 0
        for assignment in range(1 << (d.ports + d.own + len(remaining))):
            if any(len({(assignment >> j) & 1 for j in knot}) == 1 for knot in d.knots):
                continue
            valid = True
            for (callee, actual), selected, child in zip(d.calls, child_labels, child_relations):
                args = tuple(actual) + tuple(coordinates[j] for j in selected)
                state = sum(((assignment >> source) & 1) << target
                            for target, source in enumerate(args))
                if not (child >> state) & 1:
                    valid = False
                    break
            if valid:
                args = tuple(range(d.ports)) + tuple(coordinates[j] for j in labels)
                state = sum(((assignment >> source) & 1) << target
                            for target, source in enumerate(args))
                relation |= 1 << state
        return relation

    def plans(self, typ, labels, mode):
        """Fresh own allocations and a disjoint partition among child copies."""
        d = self.definitions[typ]
        for owned_labels in powerset(labels):
            if len(owned_labels) > d.own:
                continue
            if mode == "local-target" and 0 not in owned_labels:
                continue
            if mode == "child-target" and 0 in owned_labels:
                continue
            rest = tuple(j for j in labels if j not in owned_labels)
            if rest and not d.calls:
                continue
            for destinations in product(range(len(d.calls)), repeat=len(rest)):
                child_labels = tuple(tuple(j for j, dest in zip(rest, destinations) if dest == n)
                                     for n in range(len(d.calls)))
                if mode == "child-target" and (d.first is None or 0 not in child_labels[d.first]):
                    continue
                for actual in permutations(range(d.ports, d.ports + d.own), len(owned_labels)):
                    yield tuple(zip(owned_labels, actual)), child_labels

    def unmarked(self):
        state = tuple((1 << (1 << d.ports)) - 1 for d in self.definitions)
        rounds = 0
        while True:
            nxt = tuple(self.compose(i, (), (), tuple(() for _ in d.calls),
                                     tuple(state[callee] for callee, _ in d.calls))
                        for i, d in enumerate(self.definitions))
            rounds += 1
            assert all(new & ~old == 0 for old, new in zip(state, nxt))
            if nxt == state:
                return state, rounds
            state = nxt

    def guard(self, state):
        count = sum(len(relations) for relations in state.values())
        if count > self.max_profiles:
            raise ResourceLimit(f"{count} profiles exceed the explicit cap {self.max_profiles}; no decision reported")

    def saturate(self):
        state = {(i, labels): ({self.greatest[i]} if not labels else set())
                 for i in range(len(self.definitions)) for labels in self.subsets}
        rounds = 0
        while True:
            nxt = {key: set(value) for key, value in state.items()}
            for i, d in enumerate(self.definitions):
                for labels in self.subsets:
                    for owned, child_labels in self.plans(i, labels, "ordinary"):
                        sources = [state[callee, selected]
                                   for (callee, _), selected in zip(d.calls, child_labels)]
                        for child in product(*sources):
                            nxt[i, labels].add(self.compose(i, labels, owned, child_labels, child))
            self.guard(nxt)
            rounds += 1
            if nxt == state:
                return state, rounds
            state = nxt

    def target(self, previous=None):
        state = {(i, labels): set() for i in range(len(self.definitions))
                 for labels in self.target_subsets}
        mode = "local-target" if previous is None else "child-target"
        for i, d in enumerate(self.definitions):
            if previous is not None and d.first is None:
                continue
            for labels in self.target_subsets:
                for owned, child_labels in self.plans(i, labels, mode):
                    sources = []
                    for n, ((callee, _), selected) in enumerate(zip(d.calls, child_labels)):
                        bank = previous if previous is not None and n == d.first else self.unrestricted
                        sources.append(bank[callee, selected])
                    for child in product(*sources):
                        state[i, labels].add(self.compose(i, labels, owned, child_labels, child))
        self.guard(state)
        return state

    def accepted(self, state, root=0, aliases=None):
        d = self.definitions[root]
        aliases = tuple(range(d.ports)) if aliases is None else tuple(aliases)
        assert len(aliases) == d.ports
        representatives = tuple(next(j for j, value in enumerate(aliases) if value == identity)
                                for identity in dict.fromkeys(aliases))
        for labels in self.target_subsets:
            for top in powerset(representatives):
                if not top or not 3 <= len(labels) + len(top) <= self.budget:
                    continue
                support = top + tuple(d.ports + j for j in range(len(labels)))
                for relation in state[root, labels]:
                    allowed = set()
                    for s in range(1 << (d.ports + len(labels))):
                        if not (relation >> s) & 1:
                            continue
                        if any(aliases[a] == aliases[b] and ((s >> a) & 1) != ((s >> b) & 1)
                               for a in range(d.ports) for b in range(a)):
                            continue
                        allowed.add(tuple((s >> j) & 1 for j in support))
                    if is_bond(allowed, len(support)):
                        return True
        return False

    @staticmethod
    def key(state):
        return tuple((key, tuple(sorted(value))) for key, value in sorted(state.items()))

    def depths(self, root=0, aliases=None):
        current, seen, answers, profile_counts = self.target(), {}, [], []
        while self.key(current) not in seen:
            if len(seen) >= self.max_states:
                raise ResourceLimit(f"{len(seen)} target states reached the explicit cap {self.max_states}; no decision reported")
            seen[self.key(current)] = len(answers)
            answers.append(self.accepted(current, root, aliases))
            profile_counts.append(sum(map(len, current.values())))
            current = self.target(current)
        preperiod = seen[self.key(current)]
        positive_answers = answers if preperiod == 0 else answers[1:]
        return dict(preperiod=preperiod, period=len(answers) - preperiod,
                    answers=answers, target_profile_counts=profile_counts,
                    every_depth=all(answers), any_depth=any(answers),
                    every_positive_depth=all(positive_answers),
                    any_positive_depth=any(positive_answers))


def fixtures():
    return {
        "persistent": (Definition(3, 1, ((0, 2, 3),), ((0, (0, 1, 3)),)),),
        "forgetting": (Definition(3, 2, ((4, 0, 2),), ((0, (2, 0, 3)),)),),
        "alias": (Definition(3, 1, ((0, 2, 3),), ((0, (0, 0, 3)),)),),
        "empty": (Definition(3, 2, tuple(combinations(range(5), 3)), ((0, (0, 1, 3)),)),),
        "finite_branch": (Definition(3, 2, ((0, 3, 4),), (), None),),
        "no_own_at_root": (Definition(3, 0, (), ((1, (0, 1, 2)),)),
                           Definition(3, 1, ((0, 2, 3),), ((1, (0, 1, 3)),))),
        "side": (Definition(3, 1, (), ((0, (1, 2, 3)), (1, (0, 3, 1)))),
                 Definition(3, 1, ((0, 1, 3),), (), None)),
        "branching_depth": (Definition(3, 2, ((4, 0, 2),),
                                       ((0, (2, 0, 3)), (0, (3, 2, 0)), (0, (4, 3, 1)))),),
        # A finite two-type grammar, explicitly outside the one-definition
        # corpus. Both types have nontrivial local NAE relations.
        "period_two": (Definition(3, 2, ((0, 1, 2), (0, 3, 4)), ((1, (0, 1, 2)),)),
                       Definition(3, 3, ((0, 1, 2), (3, 4, 5)), ((0, (0, 1, 2)),))),
    }


def at(orbit, n):
    if n < len(orbit["answers"]):
        return orbit["answers"][n]
    return orbit["answers"][orbit["preperiod"] + (n - orbit["preperiod"]) % orbit["period"]]


def from_dlang(definitions, usual_limit=True):
    """Translate the admitted language; the branch repeats its first SELF call.

    Earlier-definition calls are complete side subpatterns.  The designated
    first-child convention is explicit; no call order is guessed from a set.
    """
    translated = []
    for i, (ports, own, body) in enumerate(definitions):
        knots, calls, first = set(), [], None
        for callee, actual in body:
            actual = tuple(actual)
            if callee == "K":
                knots.add(tuple(sorted(actual)))
            else:
                if callee == "SELF":
                    if first is None:
                        first = len(calls)
                    if usual_limit and set(actual) == set(range(ports)) and len(actual) == ports == 3:
                        knots.add((0, 1, 2))
                    callee = i
                calls.append((int(callee), actual))
        translated.append(Definition(ports, own, tuple(sorted(knots)), tuple(calls), first))
    return tuple(translated)


def decide_dlang(definitions, budget=3, max_profiles=100000, usual_limit=True, max_states=10000):
    """Public batch entry point. An unfinished resource-limited run is no verdict."""
    started = time.monotonic()
    translated = from_dlang(definitions, usual_limit)
    engine = Profiles(translated, budget, max_profiles, max_states)
    root = len(translated) - 1
    return dict(status="decided", budget=budget, branch="repeated first SELF call",
                usual_limit_preprocessing=usual_limit,
                greatest_port_relations=list(engine.greatest),
                closure_rounds=engine.closure_rounds,
                unrestricted_profiles=sum(map(len, engine.unrestricted.values())),
                orbit=engine.depths(root=root), seconds=time.monotonic() - started)


def run_fixture(name, definitions, budget, cap, max_states=10000):
    started = time.monotonic()
    engine = Profiles(definitions, budget, cap, max_states)
    orbit = engine.depths()
    report = dict(name=name, budget=budget, greatest_port_relations=list(engine.greatest),
                  unmarked_rounds=engine.greatest_rounds, closure_rounds=engine.closure_rounds,
                  unrestricted_profiles=sum(map(len, engine.unrestricted.values())),
                  orbit=orbit, seconds=time.monotonic() - started)
    if budget == 3:
        expected = {"persistent": lambda n: True,
                    "forgetting": lambda n: n <= 1,
                    "side": lambda n: n <= 2,
                    "alias": lambda n: True,
                    "empty": lambda n: False,
                    "finite_branch": lambda n: n == 0,
                    "no_own_at_root": lambda n: n >= 1,
                    "period_two": lambda n: n % 2 == 0}.get(name)
        if expected is not None:
            assert all(at(orbit, n) == expected(n) for n in range(30)), report
        if name == "branching_depth":
            assert all(at(orbit, n) for n in range(3))
            assert all(not at(orbit, n) for n in range(7, 30))
    if name == "period_two":
        # Alias positions represent the same distinction; the repeated-port
        # root is empty when every formal port is the same variable.
        assert not engine.depths(aliases=(0, 0, 0))["any_depth"]
        report["all_root_ports_aliased"] = engine.depths(aliases=(0, 0, 0))
    return report


def direct_finite_projection(name, definitions, target_depth, omit_side=False):
    """Independent finite SAT expansion, no profile or composition calls.

    The simple fixtures' exact unmarked port relations are known directly:
    TOP, NAE for period_two, or empty. The expansion includes target-depth+1
    own variables, so a required observation can lie beyond the target.
    """
    horizon = target_depth + 1
    nv = definitions[0].ports
    first_own = {}
    triples, contradiction = [], False

    def expand(typ, actual, level, address):
        nonlocal nv, contradiction
        d = definitions[typ]
        own = list(range(nv, nv + d.own))
        nv += d.own
        env = list(actual) + own
        if all(x == 0 for x in address):
            first_own[level] = own
        if not (omit_side and name == "side" and typ == 1):
            triples.extend(tuple(env[j] for j in knot) for knot in d.knots)
        for n, (callee, args) in enumerate(d.calls):
            supplied = tuple(env[j] for j in args)
            if level < horizon:
                expand(callee, supplied, level + 1, address + (n,))
            elif name == "period_two":
                triples.append(supplied)
            elif name == "empty":
                contradiction = True

    expand(0, tuple(range(definitions[0].ports)), 0, ())
    cnf = [clause for triple in triples for clause in
           ([j + 1 for j in triple], [-j - 1 for j in triple])]
    if contradiction:
        cnf += [[1], [-1]]
    tested = 0
    witness = None
    with Solver(name="cadical195", bootstrap_with=cnf) as sat:
        for support in combinations(range(nv), 3):
            if not set(support).intersection(range(definitions[0].ports)):
                continue
            if not set(support).intersection(first_own.get(target_depth, ())):
                continue
            allowed = set()
            for bits in product((0, 1), repeat=3):
                assumptions = [j + 1 if b else -j - 1 for j, b in zip(support, bits)]
                if sat.solve(assumptions=assumptions):
                    allowed.add(bits)
            tested += 1
            # Separate calculation of the proper projections.
            if allowed and len(allowed) != 8 and all(
                    {tuple(s[j] for j in keep) for s in allowed} == set(product((0, 1), repeat=2))
                    for keep in ((0, 1), (0, 2), (1, 2))):
                witness = dict(support=list(support), allowed=sorted(allowed))
                break
    return dict(target_depth=target_depth, horizon=horizon, found=witness is not None,
                supports_tested=tested, witness=witness)


def canonical_controls():
    results = {}
    for name, cnf, expected in (("nae", "a b c; ~a ~b ~c", True),
                                ("empty", "a; ~a; b ~b c", False),
                                ("full", "a ~a b; c ~c a", False)):
        command = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", cnf,
                   "--loops", "a", "b", "--contact", "c", "--json"]
        result = json.loads(subprocess.check_output(command, cwd=ROOT, text=True,
                                                   env={**os.environ, "PYTHONPATH": str(ROOT / "tools")}))
        assert result["is_knot"] == expected
        results[name] = result["is_knot"]
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", choices=tuple(fixtures()))
    parser.add_argument("--k", type=int, default=3)
    parser.add_argument("--max-profiles", type=int, default=100000)
    parser.add_argument("--max-states", type=int, default=10000)
    parser.add_argument("--definitions-json", type=Path)
    parser.add_argument("--batch-json", type=Path)
    parser.add_argument("--bottomless", action="store_true",
                        help="Do not add the admitted usual-limit pass-through NAE constraint")
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    if args.definitions_json or args.batch_json:
        assert not args.write_result and not args.fixture
        path = args.definitions_json or args.batch_json
        data = json.loads(path.read_text())
        records = data if args.batch_json else [data]
        output = []
        for n, record in enumerate(records):
            definitions = record["defs"] if isinstance(record, dict) else record
            identifier = record.get("id", n) if isinstance(record, dict) else n
            try:
                answer = decide_dlang(definitions, args.k, args.max_profiles, not args.bottomless, args.max_states)
            except ResourceLimit as error:
                answer = dict(status="resource-limit", reason=str(error))
            output.append(dict(id=identifier, **answer))
        print(json.dumps(output, indent=2))
        return
    selected = fixtures()
    if args.fixture:
        selected = {args.fixture: selected[args.fixture]}
    results = [run_fixture(name, definitions, args.k, args.max_profiles, args.max_states)
               for name, definitions in selected.items()]
    benchmark_four = None
    derived_least = None
    if not args.fixture and args.k == 3:
        benchmark_four = run_fixture("branching_depth", fixtures()["branching_depth"], 4,
                                     args.max_profiles, args.max_states)
        assert all(at(benchmark_four["orbit"], n) == (n <= 4) for n in range(30))
        benchmark_three = next(r for r in results if r["name"] == "branching_depth")
        derived_least = {}
        for depth in range(3, 7):
            assert not at(benchmark_three["orbit"], depth)
            lower = 4 if at(benchmark_four["orbit"], depth) else 5
            # The admitted predecessor's uniform upper construction is
            # argued in the proof; only its arithmetic is checked here.
            upper = min(4, (depth + 1) // 2 + 2) if at(benchmark_four["orbit"], depth) else (depth + 1) // 2 + 2
            assert lower == upper
            derived_least[str(depth)] = lower
    direct = {}
    if args.k == 3:
        for result in results:
            name = result["name"]
            if name == "branching_depth":
                continue  # Its exponential tree is not needed for this small control.
            direct[name] = [direct_finite_projection(name, selected[name], n) for n in range(4)]
            assert all(item["found"] == at(result["orbit"], item["target_depth"])
                       for item in direct[name])
        if "side" in selected:
            missing_side = direct_finite_projection("side", selected["side"], 0, omit_side=True)
            assert not missing_side["found"]
            direct["incorrectly_omit_side_constraints"] = missing_side
    # Matched acceptance controls: empty relation, full relation, and two-bit
    # ties never count as a >=3 knot-bond.
    assert not is_bond(set(), 3)
    assert not is_bond(set(product((0, 1), repeat=3)), 3)
    assert not is_bond({(0, 0), (1, 1)}, 2)
    assert is_bond(set(product((0, 1), repeat=3)) - {(0, 0, 0), (1, 1, 1)}, 3)
    pass_through = [(3, 1, [("SELF", (0, 1, 2))])]
    corrected = decide_dlang(pass_through, budget=3)
    bottomless = decide_dlang(pass_through, budget=3, usual_limit=False)
    assert corrected["greatest_port_relations"] == [126]
    assert bottomless["greatest_port_relations"] == [255]
    try:
        Profiles(fixtures()["branching_depth"], 3, max_profiles=1)
    except ResourceLimit:
        resource_control = "raised-without-verdict"
    else:
        raise AssertionError("The deliberately insufficient profile cap must not report a decision")
    try:
        Profiles(fixtures()["persistent"], 3, max_states=1).depths()
    except ResourceLimit:
        state_resource_control = "raised-without-verdict"
    else:
        raise AssertionError("The deliberately insufficient target-state cap must not report a decision")
    for small_budget in (0, 1, 2):
        assert not Profiles(fixtures()["persistent"], small_budget).depths()["any_depth"]
    tie_engine = Profiles((Definition(3, 1, ((0, 1, 3),), ((0, (0, 1, 3)),)),), 3)
    tie_orbit = tie_engine.depths(aliases=(0, 0, 0))
    assert not tie_orbit["any_depth"]
    coherent_aliased_ports = sum(1 for s in range(8) if (tie_engine.greatest[0] >> s) & 1
                                and len({(s >> j) & 1 for j in range(3)}) == 1)
    assert coherent_aliased_ports == 2
    result = dict(artifact_id="BRANCH-DEPTH-20261112-001D-P001", status="Proved",
                  theorem="Effective ultimate periodicity for fixed support budget, exact profiles and a fixed regular first-child branch.",
                  uniform_proof="argued-in-prose", minimum_support=3,
                  validation="V1-separate-algorithm-same-task", controls=results,
                  benchmark_budget_4=benchmark_four,
                  benchmark_least_bonds_derived=derived_least,
                  direct_finite_projection_controls=direct,
                  canonical_knotlab_controls=canonical_controls(),
                  usual_limit_control=dict(corrected=corrected, bottomless=bottomless),
                  resource_limit_control=resource_control,
                  state_resource_limit_control=state_resource_control,
                  budgets_below_three_rejected=True,
                  coherent_tie_only_alias=dict(port_states=coherent_aliased_ports, orbit=tie_orbit),
                  unknown_budget_decidability_established=False,
                  corpus_664_replayed=False,
                  resource_note="No practical runtime guarantee for all 664 rules follows from finite termination. The explicit cap raises ResourceLimit without returning a verdict.")
    dependencies = [ROOT / "proofs/BONDS-AND-COUNT-20261112-001E/BONDS-AND-COUNT-20261112-001E-P001_branching_depth/proof.md",
                    ROOT / "proofs/NEST-COUNT-20261112-001A/NEST-COUNT-20261112-001A-P001_finite_state/proof.md"]
    result["dependency_bindings"] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                      for p in dependencies}
    if args.write_result:
        assert not args.fixture and args.k == 3
        result["owned_bindings"] = {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                                     for name in ("check.py", "proof.md")}
        (HERE / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
