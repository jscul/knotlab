"""Rebuild a seeded sample from the archived parity census at 0e332122a3.

The round follows PARTS-MEET-AGAIN definitions §2 and WHAT-A-BIRTH-CARRIES
definitions_b §§1–2. The shared engine supplies only the roster, including
part order and its guard. The census atlas supplies the numbered meetings in
each start. Growth, parity implication, eligibility, and the birth reading
are implemented here. See SHORT-AGAIN/ring_line.py for the recorded edit and
its reading of the receiver's own births.
"""

import argparse
from collections import Counter, deque
from dataclasses import dataclass, field
from functools import cache
from hashlib import sha256
from pathlib import Path
import gzip
import json
import random
import re
import resource
import sys
from time import perf_counter

from networkx import graph_atlas


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARCHIVE = HERE.parent / "parity_runs.jsonl.gz"
KERNEL = (ROOT / "experiments" / "WHAT-A-BIRTH-CARRIES-20261125-001B"
          / "WHAT-A-BIRTH-CARRIES-20261125-001B-E001_link_through_a_made_knot" / "eng.py")
ARCHIVE_SHA = "d9cfdc69be256779bb9c74795c0afb24fd3f8e20f1433c99ae53b58fa18d9ea9"
KERNEL_SHA = "09017631d84ea56182230be5a4345ae8fbfcc504ae244ad4b34d74c282803a40"
SEED = 20261126
ROUNDS, EDIT_AFTER, KNOT_BOUND, GUARD_MULT = 12, 3, 1500, 4
MEMORY_LIMIT = 3 * 1024**3
RECEIVER, FAR, OTHER = 1, 2, 4
NAMED_STARTS = {
    "ring": tuple(((u - 1) % 5, u, *range(5 + 3*u, 8 + 3*u)) for u in range(5)),
    "copier": ((0, 1, 2), (0, 3, 4)),
    "source": ((0, 1, 2, 9, 10, 11), (0, 1, 3), (4, 5, 12, 13, 14),
               (6, 7, 15, 16, 17), (2, 3, 4, 6, 18, 19, 20), (7, 8, 21, 22), (5, 8, 23, 24)),
}


@cache
def pattern(label):
    if label in NAMED_STARTS:
        return NAMED_STARTS[label], 0
    size, atlas_index, loose, site = re.fullmatch(r"(?:n(\d+):)?g(\d+):(\d+)@(\d+)", label).groups()
    numbered = graph_atlas(int(atlas_index))
    n = numbered.number_of_nodes()
    assert len(loose) == n and (size is None or int(size) == n) and 0 <= int(site) < n
    places = [[] for _ in range(n)]
    meetings = sorted(tuple(sorted(pair)) for pair in numbered.edges)
    for d, (a, b) in enumerate(meetings):
        places[a].append(d)
        places[b].append(d)
    next_distinction = len(meetings)
    for u, count in enumerate(map(int, loose)):
        places[u].extend(range(next_distinction, next_distinction + count))
        next_distinction += count
    return tuple(map(tuple, places)), int(site)


def parity_row(distinctions):
    return sum(1 << d for d in distinctions)


def remainder(row, basis):
    while row:
        pivot = row.bit_length() - 1
        if pivot not in basis:
            break
        row ^= basis[pivot]
    return row


def insert(row, basis):
    residual = remainder(row, basis)
    if residual:
        basis[residual.bit_length() - 1] = residual


def actual_basis(places):
    basis = {}
    for held in places:
        insert(parity_row(held), basis)
    return basis


@dataclass
class State:
    places: list[tuple]
    holders: list[list]
    roles: list[int]
    parents: list[tuple]
    names: list[int]
    basis: dict[int, int]

    def copy(self):
        return State(self.places.copy(), [held.copy() for held in self.holders],
                     self.roles.copy(), self.parents.copy(), self.names.copy(), self.basis.copy())

    def loose(self):
        # No distinction is barred at these starts or by this addition.
        return {u: free for u, held in enumerate(self.places)
                if (free := sorted(d for d in held if len(self.holders[d]) == 1))}


def joined_start(receiver, far):
    places, holders, roles = [], [], []

    def knot(role):
        u = len(places)
        places.append([])
        roles.append(role)
        return u

    def distinction(*owners):
        d = len(holders)
        for u in owners:
            places[u].append(d)
        holders.append(list(owners))

    def put(label, role):
        held, site = pattern(label)
        owners = [[] for _ in range(1 + max(d for local in held for d in local))]
        base = len(places)
        for local in held:
            u = knot(role)
            for d in local:
                owners[d].append(u)
        for hs in owners:
            distinction(*hs)
        return base + site

    a = put(receiver, RECEIVER)
    b = None if far == "stub" else put(far, FAR)
    for step in range(3):
        if step < 2:
            neighbor = knot(OTHER)
        elif b is None:
            neighbor = knot(FAR)
        else:
            neighbor = b
        spent = knot(OTHER)
        distinction(a, spent)
        distinction(neighbor, spent)
        distinction(neighbor, spent)
        distinction(a)
        distinction(neighbor)
        a = neighbor
    places = list(map(tuple, places))
    return State(places, holders, roles, [()] * len(places), list(range(len(places))), actual_basis(places))


def takes_for(state, roster, take, choice):
    if take == "J-EACH-PART":
        sources = {}
        for u in roster.members:
            part = roster.part_of[u]
            for d in state.places[u]:
                if len(state.holders[d]) > 1 and sources.setdefault(d, part) != part:
                    sources[d] = -1
        by_name = sorted(sources)

        @cache
        def outside(part):
            return tuple(d for d in by_name if sources[d] != part)

        return lambda ps: outside(roster.part_of[ps[0]]) if len(ps) == 1 else ()

    @cache
    def meets(u):
        return {v for d in state.places[u] for v in state.holders[d] if v != u}

    @cache
    def choose(ps):
        if take is None:
            return ()
        if take in ("MET", "MET-SOLE"):
            suppliers = set.intersection(*(meets(u) for u in ps)).difference(ps)
        elif len(ps) > 1:
            return ()
        elif take == "STEPS1-SOLE":
            suppliers = state.parents[ps[0]]
        elif take == "STEPS2-SOLE":
            suppliers = {v for u in state.parents[ps[0]] for v in state.parents[u]}
        else:
            raise ValueError(take)
        excluded = {d for u in ps for d in state.places[u]}
        candidates = {d for u in suppliers for d in state.places[u]
                      if len(state.holders[d]) > 1 and d not in excluded}
        if take == "MET" and candidates:
            return (min(candidates) if choice == "OLDEST" else max(candidates),)
        return tuple(candidates) if len(candidates) == 1 else ()

    return choose


@dataclass
class Round:
    own: tuple
    implied: frozenset
    implied_owed: int
    made_short: int


def step(engine, old, names, take, choice, guard):
    loose = old.loose()
    members = [(u, len(ds), 0) for u, ds in loose.items()]
    roster = engine.build_roster(old, members, "roster", guard, parts=(take == "J-EACH-PART"))
    owed = Counter(u for group in roster.groups for u in group)
    short = {u for u, held in loose.items() if owed[u] > len(held)}
    made_short = sum(bool(old.parents[u]) for u in short)
    births = [group for group in roster.groups if short.isdisjoint(group)]
    guard("births", len(births), "joins")
    allocated = Counter(u for group in births for u in group)
    for u, held in loose.items():
        if u not in short:
            births.extend([(u,)] * (len(held) - allocated[u]))
    guard("births", len(births), "births")

    spend = {u: iter(ds) for u, ds in loose.items()}
    take_from = takes_for(old, roster, take, choice)
    new = old.copy()
    base = len(old.places)
    input_rows = []
    for u, ps in enumerate(births, base):
        inputs = tuple(next(spend[p]) for p in ps) + take_from(ps)
        input_rows.append(parity_row(inputs))
        new.places.append(inputs)
        for d in inputs:
            new.holders[d].append(u)

    demand = Counter()
    if births:
        demand_members = [m for m in members if m[0] in short]
        demand_members.extend((u, 1, 0) for u in range(base, base + len(births)))
        future = engine.build_roster(new, demand_members, "demand", guard)
        demand = Counter(u for group in future.groups for u in group)
    implied = [remainder(row, old.basis) == 0 for row in input_rows]
    fresh = [0 if flag else max(demand[u], 3 - len(new.places[u]), 1)
             for u, flag in enumerate(implied, base)]
    guard("distinctions", len(new.holders) + sum(fresh), "fresh")

    occurrence = Counter()
    own = []
    implied_names = set()
    implied_owed = 0
    for u, (ps, row, flag, count) in enumerate(zip(births, input_rows, implied, fresh), base):
        birth = (len(ps) == 1, tuple(sorted(old.names[p] for p in ps)))
        description = (*birth, occurrence[birth])
        occurrence[birth] += 1
        name = names.setdefault(description, len(names) + names.first_birth)
        role = 0
        for p in ps:
            role |= old.roles[p]
        new.roles.append(role)
        new.names.append(name)
        new.parents.append(ps)
        if count:
            d = len(new.holders)
            new.places[u] += tuple(range(d, d + count))
            new.holders.extend([u] for _ in range(count))
            row |= ((1 << count) - 1) << d
        insert(row, new.basis)
        if role == RECEIVER:
            own.append((name, count, len(new.places[u])))
        if flag:
            implied_names.add(name)
            implied_owed += demand[u] > 0
    return new, Round(tuple(sorted(own)), frozenset(implied_names), implied_owed, made_short)


class BirthNames(dict):
    def __init__(self, first_birth):
        super().__init__()
        self.first_birth = first_birth


def affiliation(state):
    """Join live members by a common met knot or a shared distinction."""
    active = dict.fromkeys(state.loose())
    for u in active:
        active[u] = u

    def root(u):
        while active[u] != u:
            active[u] = active[active[u]]
            u = active[u]
        return u

    met_by, held_by = {}, {}
    for u in active:
        for d in state.places[u]:
            active[root(held_by.setdefault(d, u))] = root(u)
            for v in state.holders[d]:
                if v != u:
                    active[root(met_by.setdefault(v, u))] = root(u)
    near = {root(u) for u in active if state.roles[u] == RECEIVER}
    far = {u: root(u) in near for u in active if state.roles[u] == FAR}
    return any(far.values()) if near and far else None, far


def targets(state):
    _, far = affiliation(state)
    sharings = {u: 0 for u, role in enumerate(state.roles) if role == RECEIVER}
    pending = deque(sharings)
    visited_distinctions = set()
    while pending:
        u = pending.popleft()
        for d in state.places[u]:
            if d in visited_distinctions:
                continue
            visited_distinctions.add(d)
            for v in state.holders[d]:
                if v not in sharings:
                    sharings[v] = sharings[u] + 1
                    pending.append(v)
    for linked, bound in ((True, 5), (False, 2)):
        eligible = [u for u, status in far.items() if status == linked]
        order = sorted(eligible, key=lambda u: (sharings.get(u, float("inf")), u))
        for u in order[:bound]:
            yield u, {"linked": linked, "sharings": sharings.get(u)}


@dataclass
class Growth:
    rounds: list[Round] = field(default_factory=list)
    linked: list = field(default_factory=list)
    edit_state: State | None = None
    ended: str = "rounds"
    guard: dict | None = None
    knots: int = 0

    def endpoint(self):
        return {"rounds": len(self.rounds), "ended": self.ended, "knots": self.knots, "guard": self.guard}


def grow(engine, state, names, take, choice, prefix=None):
    result = Growth() if prefix is None else Growth(rounds=prefix.rounds[:EDIT_AFTER])
    guard = engine.Guard(GUARD_MULT)
    while len(result.rounds) < ROUNDS:
        try:
            state, observation = step(engine, state, names, take, choice, guard)
        except engine.GuardStop as error:
            result.ended = "guard"
            result.guard = {"round": len(result.rounds) + 1, "count": error.what,
                            "value": error.value, "step": error.where}
            break
        result.rounds.append(observation)
        if prefix is None:
            result.linked.append(affiliation(state)[0])
            if len(result.rounds) == EDIT_AFTER:
                result.edit_state = state
        if len(state.places) > KNOT_BOUND:
            result.ended = "knots"
            break
    result.knots = len(state.places)
    return result


def edited_states(baseline, u):
    recorded = baseline.copy()
    d = len(recorded.holders)
    recorded.places[u] += (d,)
    recorded.holders.append([u])
    corrected = recorded.copy()
    corrected.basis = actual_basis(corrected.places)
    old_row, new_row = map(parity_row, (baseline.places[u], recorded.places[u]))
    witness = {
        "old loose distinction": baseline.loose()[u][0],
        "added distinction": d,
        "old row distinctions": baseline.places[u],
        "old row in recorded span": remainder(old_row, recorded.basis) == 0,
        "old row in actual span": remainder(old_row, corrected.basis) == 0,
        "edited row in recorded span": remainder(new_row, recorded.basis) == 0,
        "edited row in actual span": remainder(new_row, corrected.basis) == 0,
    }
    assert [v for k, v in witness.items() if k.endswith("span")] == [True, False, False, True]
    return recorded, corrected, witness


def comparison(a, b):
    common = min(len(a.rounds), len(b.rounds))
    own = []
    implied = []
    for r, (left, right) in enumerate(zip(a.rounds, b.rounds), 1):
        if left.own != right.own:
            own.append(r)
        if left.implied != right.implied:
            implied.append([r, len(left.implied - right.implied), len(right.implied - left.implied)])
    return {"common rounds": common, "own birth difference rounds": own,
            "implied births differing by identity": implied}


def replay(engine, case):
    start = perf_counter()
    receiver, far = case["A"], case["B"]
    ration, take, choice = case["law"]
    assert ration == "ORD" and case["knot law"] == "parity"
    initial = joined_start(receiver, far)
    names = BirthNames(len(initial.places))
    baseline = grow(engine, initial, names, take, choice)
    observed = dict(A=receiver, B=far, law=case["law"], rounds=len(baseline.rounds),
                    ended=baseline.ended, linked=baseline.linked, changes=[],
                    **{"made short": [r.made_short for r in baseline.rounds], "knot law": "parity"})
    edits = []
    if len(baseline.rounds) > EDIT_AFTER and baseline.linked[EDIT_AFTER - 1] is not None:
        for u, description in targets(baseline.edit_state):
            as_recorded, with_actual_basis, witness = edited_states(baseline.edit_state, u)
            recorded = grow(engine, as_recorded, names, take, choice, baseline)
            corrected = grow(engine, with_actual_basis, names, take, choice, baseline)
            recorded_comparison = comparison(baseline, recorded)
            difference_rounds = recorded_comparison["own birth difference rounds"]
            observed["changes"].append(dict(**description, heard=next(iter(difference_rounds), None),
                                            rounds=recorded_comparison["common rounds"]))
            edits.append({
                **description, "knot": u, "basis witness": witness,
                "comparison round for setting + sharings + 1": (
                    EDIT_AFTER + description["sharings"] + 1 if description["sharings"] is not None else None),
                "recorded edit endpoint": recorded.endpoint(), "actual basis endpoint": corrected.endpoint(),
                "baseline against recorded edit": recorded_comparison,
                "baseline against actual basis edit": comparison(baseline, corrected),
                "recorded edit against actual basis edit": comparison(recorded, corrected),
                "implied by round, recorded edit": [len(r.implied) for r in recorded.rounds],
                "implied by round, actual basis edit": [len(r.implied) for r in corrected.rounds],
            })
    mismatches = {k: {"archived": case[k], "rebuilt": v} for k, v in observed.items() if case[k] != v}
    return {
        "key": [receiver, far, case["law"]], "archive mismatches": mismatches,
        "baseline endpoint": baseline.endpoint(), "link by round": baseline.linked,
        "made short by round": observed["made short"],
        "implied by round": [len(r.implied) for r in baseline.rounds],
        "implied owed by round": [r.implied_owed for r in baseline.rounds],
        "changes": edits, "wall seconds": round(perf_counter() - start, 4),
        "process peak KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }


def verified(path, digest):
    data = path.read_bytes()
    if sha256(data).hexdigest() != digest:
        raise ValueError(f"Input differs from 0e332122a3: {path}")
    return data


def sample():
    rows = [r for line in gzip.decompress(verified(ARCHIVE, ARCHIVE_SHA)).splitlines()
            if "law" in (r := json.loads(line))]
    rows.sort(key=lambda r: (r["A"], r["B"]))
    # One equally weighted row within each stated stratum. The strata are
    # chosen to span the settings and endpoints and include positive controls.
    strata = (
        (None, None, "rounds", 12, "unlinked"),
        ("MET", "OLDEST", "guard", 4, "change"),
        ("MET", "NEWEST", "guard", 4, "change"),
        ("MET-SOLE", None, "knots", 6, "change"),
        ("STEPS1-SOLE", None, "rounds", 12, "linked"),
        ("STEPS2-SOLE", None, "rounds", 12, "unlinked"),
        ("J-EACH-PART", None, "knots", 6, 4),
        ("J-EACH-PART", None, "guard", 5, 5),
        ("J-EACH-PART", None, "rounds", 12, "change"),
    )

    def qualifies(change, read, endpoint):
        if read == "unlinked":
            return not change["linked"]
        if read == "linked":
            return change["linked"]
        if read == "change":
            return change["heard"] is None
        return change["heard"] == read and change["rounds"] == endpoint

    rng = random.Random(SEED)
    for take, choice, stop, endpoint, read in strata:
        pool = [r for r in rows if r["law"] == ["ORD", take, choice] and r["ended"] == stop
                and r["rounds"] == endpoint and any(qualifies(c, read, endpoint) for c in r["changes"])]
        case = rng.choice(pool)
        yield {"stratum": [take, choice, stop, endpoint, read], "eligible archive rows": len(pool)}, case


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("list", "pilot", "sample"))
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY_LIMIT, MEMORY_LIMIT))
    cases = list(sample())
    if args.mode == "pilot":
        cases = [cases[i] for i in (0, 1, 6)]
    elif args.mode == "list":
        print(json.dumps([dict(stratum, key=[case["A"], case["B"], case["law"]],
                               changes=case["changes"]) for stratum, case in cases], indent=2))
        return

    verified(KERNEL, KERNEL_SHA)
    sys.path.insert(0, str(KERNEL.parent))
    import eng

    assert eng.GUARD == {"pairs": 20_000, "groups": 20_000, "births": 20_000, "distinctions": 400_000,
                         "incidences": 2_000_000, "cliques": 200_000}
    started = perf_counter()
    results = []
    for stratum, case in cases:
        result = dict(stratum, **replay(eng, case))
        print(json.dumps({"key": result["key"], "wall seconds": result["wall seconds"],
                          "archive mismatches": list(result["archive mismatches"])}), file=sys.stderr, flush=True)
        results.append(result)
    result = {"mode": args.mode, "commit": "0e332122a3", "seed": SEED, "archive sha256": ARCHIVE_SHA,
              "roster kernel sha256": KERNEL_SHA, "round bound": ROUNDS, "edit after round": EDIT_AFTER,
              "knot bound": KNOT_BOUND, "guard multiplier": GUARD_MULT, "address space bytes": MEMORY_LIMIT,
              "wall seconds": round(perf_counter() - started, 4), "cases": results}
    if args.out:
        with args.out.open("x", encoding="utf-8") as out:
            json.dump(result, out, indent=2)
            out.write("\n")
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
