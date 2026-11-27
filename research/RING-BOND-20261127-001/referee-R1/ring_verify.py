"""Recount the ring, check its reading clauses, and compare with the record."""

import argparse
import ast
from collections import Counter, defaultdict
from contextlib import redirect_stdout
from dataclasses import asdict
import io
from itertools import combinations, product
import json
from pathlib import Path
import re
import sys
import time

import numpy as np
from pysat.solvers import Solver

from ring_recount import (
    ROOT, SOURCE, STUDY, Stage, WORDS, WORD_NAMES, candidates_by_holders,
    connected, rings_with_births, scan,
)


def read_json(path):
    return json.loads(path.read_text())


def nae_clauses(rows):
    return [tuple(sign * x for x in row) for row in rows for sign in (1, -1)]


def reading_clauses(var, carrier, name):
    xs = tuple(var[x] for x in carrier)
    one_way = [(name,) + xs, (name,) + tuple(-x for x in xs)]
    other_way = [(-name, sign * xs[0], -sign * x)
                 for x in xs[1:] for sign in (1, -1)]
    return one_way + other_way


def normalize_image(carriers, missing):
    order = sorted(range(len(carriers)), key=lambda i: carriers[i])
    return tuple(carriers[i] for i in order), tuple(
        sorted("".join(word[i] for i in order) for word in missing)
    )


def collapse(supports, carriers, missing):
    """Signed identification of agrees and disagreeing pairs, then solve.

    A disagreeing carrier with at least three distinctions adds a law.
    Complementing a negative representative complements that one literal.
    """
    observed = []
    for word, name in zip(WORDS, WORD_NAMES, strict=True):
        var = {x: x + 1 for knot in supports for x in knot}
        extra = []
        for carrier, agrees in zip(carriers, word, strict=True):
            first, *rest = carrier
            if agrees:
                for x in rest:
                    var[x] = var[first]
            elif len(rest) == 1:
                var[rest[0]] = -var[first]
            else:
                extra.append(carrier)
        clauses = nae_clauses(tuple(tuple(var[x] for x in row) for row in supports + tuple(extra)))
        with Solver(bootstrap_with=clauses) as solver:
            if not solver.solve():
                observed.append(name)
    return tuple(observed) == missing


class DefinedReadings:
    def __init__(self, supports):
        self.supports = supports
        names = sorted(set().union(*map(set, supports)))
        self.var = {x: i + 1 for i, x in enumerate(names)}
        self.clauses = nae_clauses(tuple(tuple(self.var[x] for x in row) for row in supports))
        self.results = {}

    def with_readings(self, carriers):
        names = tuple(range(len(self.var) + 1, len(self.var) + len(carriers) + 1))
        clauses = self.clauses.copy()
        for carrier, name in zip(carriers, names, strict=True):
            clauses.extend(reading_clauses(self.var, carrier, name))
        return Solver(bootstrap_with=clauses), names

    def missing(self, carriers):
        solver, names = self.with_readings(carriers)
        with solver:
            return tuple(text for word, text in zip(WORDS, WORD_NAMES, strict=True)
                         if not solver.solve(assumptions=[r if b else -r
                                                       for r, b in zip(names, word, strict=True)]))

    def unread(self, carrier):
        if carrier in self.results:
            return self.results[carrier]
        solver, (name,) = self.with_readings((carrier,))
        with solver:
            for support in self.supports:
                # Both the law and the reading are unchanged by a total flip.
                patterns = product((0, 1), repeat=len(support) - 1)
                for tail in patterns:
                    if not any(tail):
                        continue
                    assumptions = [self.var[x] if b else -self.var[x]
                                   for x, b in zip(support, (0,) + tail, strict=True)]
                    if solver.solve(assumptions=assumptions + [name]) and solver.solve(
                        assumptions=assumptions + [-name]
                    ):
                        break
                else:
                    self.results[carrier] = False
                    return False
        self.results[carrier] = True
        return True


def strict_carrier(supports, carriers):
    return all(len(set(knot).intersection(carrier)) <= 1
               for knot in supports for carrier in carriers)


def json_counter(values):
    return dict(Counter(map(str, values)))


def bond_fields(bonds, supports, born):
    readings = Counter(reading for bond in bonds for reading in bond.readings)
    every = [bond for bond in bonds if len(bond.essential) == len(supports)]
    return {
        "bonds": len(bonds),
        "newest birth essential": sum(any(i >= born for i in bond.essential)
                                      for bond in bonds) if born else None,
        "every law essential": len(every),
        "every-law shapes and missing": json_counter(
            "".join(str(len(r.carrier)) for r in bond.readings) + " missing " + ",".join(bond.missing)
            for bond in every),
        "missing counts": json_counter(len(bond.missing) for bond in bonds),
        "readings in two or more bonds": sum(n >= 2 for n in readings.values()),
    }


def bond_extras(bonds, stage):
    supports = stage.supports
    exact_holder_supports = {}
    shortenable = {}
    counts = Counter({"strictly separated": 0, "carriers outside essential laws": 0,
                      "disconnected essential laws": 0, "no essential law": 0,
                      "with a redundant carrier place on the stage": 0})
    for bond in bonds:
        carriers = tuple(r.carrier for r in bond.readings)
        if strict_carrier(supports, carriers):
            counts["strictly separated"] += 1
        if bond.essential not in exact_holder_supports:
            exact_holder_supports[bond.essential] = set().union(*(supports[i] for i in bond.essential))
        if any(not exact_holder_supports[bond.essential].issuperset(x) for x in carriers):
            counts["carriers outside essential laws"] += 1
        if not connected(bond.essential, supports):
            counts["disconnected essential laws"] += 1
        if not bond.essential:
            counts["no essential law"] += 1
        for reading in bond.readings:
            if reading not in shortenable:
                shortenable[reading] = stage.redundant_places(reading)
        if any(shortenable[reading] for reading in bond.readings):
            counts["with a redundant carrier place on the stage"] += 1
    return dict(counts)


def lost_record(prior, stage):
    return [{"carriers": [reading.carrier for reading in bond.readings],
             "previous missing": bond.missing,
             "current missing": stage.missing(bond.readings),
             "read at": {",".join(map(str, r.carrier)): at
                         for r in bond.readings if (at := stage.determined_at(r))}}
            for bond in prior]


def full_report(stages, max_round, *, pilot=False):
    raw = read_json(STUDY / "out" / "ring.json")["full"]
    full, lost, previous = [], {}, {}
    previous_stage = None
    rounds = [max_round] if pilot else range(max_round + 1)
    for t in rounds:
        start = time.perf_counter()
        stage = Stage(stages[t])
        bonds, scan_counts = scan(stage, include_readable=True, prefix=24 if pilot else None)
        field = {"round": t, "knots": len(stage.supports), "distinctions": len(stage.names)}
        field.update(bond_fields(bonds, stage.supports, len(stages[t - 1]) if t else 0))
        current = {bond.carrier_image()[0]: bond for bond in bonds}
        assert len(current) == len(bonds)
        if t and not pilot:
            kept = {k for k, v in previous.items()
                    if k in current and current[k].carrier_image()[1] == v.carrier_image()[1]}
            field["bonds of the round before kept"] = len(kept)
            field["bonds of the round before"] = len(previous)
            old_projection = np.unique(stage.allowed_values & previous_stage.mask(previous_stage.names))
            assert np.array_equal(old_projection, previous_stage.allowed_values)
            lost[t] = lost_record([v for k, v in previous.items() if k not in kept], stage)
        if t == 1:
            field["birth essential in every bond"] = all(3 in bond.essential for bond in bonds)
        if not pilot:
            assert field == {k: v for k, v in raw[t].items() if k != "seconds"}, field
        field["allowed states"] = 2 * len(stage.allowed_values)
        field.update(scan_counts)
        field.update(bond_extras(bonds, stage))
        field["seconds"] = round(time.perf_counter() - start, 4)
        field["previous full-state projection retained"] = t > 0 and not pilot
        full.append(field)
        print(json.dumps(field), file=sys.stderr, flush=True)
        previous, previous_stage = current, stage
    if max_round == 4 and not pilot:
        post = (STUDY / "post" / "p44_and_lost.txt").read_text()
        recorded = {normalize_image(tuple(tuple(c) for c, _ in ast.literal_eval(carriers)),
                                    tuple(ast.literal_eval(missing)))
                    for carriers, missing in re.findall(r"^   (\[\[.*?\]\]) (\['[01]+'\]) ", post, re.M)}
        witnessed = {normalize_image(tuple(row["carriers"]), row["previous missing"]) for row in lost[4]}
        assert len(witnessed) == 14 and witnessed == recorded
        assert all(row["previous missing"] == row["current missing"]
                   and row["read at"] == {"9,11": (7,)} for row in lost[4])
    return {"full": full, "lost": lost, "pilot first readings": 24 if pilot else None}


def local_report(stages, max_round, *, pilot=False):
    raw = {row["round"]: row for row in read_json(STUDY / "out" / "ring.json")["local"]}
    summaries = []
    for t in [max_round] if pilot else range(1, max_round + 1):
        start = time.perf_counter()
        supports = stages[t]
        born = len(stages[t - 1])
        candidate, alternatives = candidates_by_holders(supports, per_size=3 if pilot else None)
        stage = DefinedReadings(supports)
        images = {k: stage.missing(k) for k in candidate}
        equal = {k: (image, holders) for k, (image, holders) in candidate.items()
                 if images[k] == image}
        good = {k: (image, holders) for k, (image, holders) in equal.items()
                if all(stage.unread(x) for x in k)}
        matching = {k: [h for image, h in choices if image == images[k]]
                    for k, choices in alternatives.items()
                    if k in good or (k not in equal and all(stage.unread(c) for c in k))}
        matching = {k: sets for k, sets in matching.items() if sets}
        old_distinctions = set().union(*map(set, stages[t - 1]))
        joins = {i for i in range(born, len(supports))
                 if len(old_distinctions.intersection(supports[i])) >= 2}
        join_only = {k: h for k, sets in matching.items() for h in sets
                     if (latest := set(i for i in h if i >= born)) and latest <= joins}
        field = {
            "round": t, "holders cap": 4,
            "bonds": len(good),
            "with a newest birth among the holders": sum(any(i >= born for i in h) for _, h in good.values()),
            "holder sizes": json_counter(len(holders) for _, holders in good.values()),
            "missing counts": json_counter(len(image) for image, _ in good.values()),
        }
        if t in raw and not pilot:
            assert field == {k: v for k, v in raw[t].items() if k != "seconds"}, field
        if t <= 3 and not pilot:
            bonds, _ = scan(Stage(supports))
            qualified, whole = {}, {}
            for bond in bonds:
                key, missing = bond.carrier_image()
                h = bond.essential
                whole[key] = (missing, h)
                has_carriers = set().union(*(supports[i] for i in h)).issuperset(set().union(*key))
                if h and len(h) <= 4 and connected(h, supports) and has_carriers:
                    if DefinedReadings(tuple(supports[i] for i in h)).missing(key) == missing:
                        qualified[key] = missing
            assert qualified.items() <= {key: value[0] for key, value in good.items()}.items()
            assert all(whole[key][0] == v[0] for key, v in good.items())
            field["full search with stated local qualifications"] = len(qualified)
            extra = sorted(good.keys() - qualified.keys())
            field["local bonds without the stated full-search qualifications"] = len(extra)
            if extra:
                key = extra[0]
                field["example of a local bond without the full-search qualifications"] = {
                    "carriers": key, "missing": good[key][0], "local holders": good[key][1],
                    "whole-stage essential laws": whole[key][1],
                }
        field.update({
            "candidate readership triples": len(candidate),
            "with more than one qualifying holder set before stage checks": sum(
                len(sets) > 1 for sets in alternatives.values()),
            "same image as whole stage": len(equal),
            "strictly separated among final bonds": sum(strict_carrier(supports, key) for key in good),
            "valid for at least one holder set after stage checks": len(matching),
            "with some valid holder set using a newest birth": sum(
                any(any(i >= born for i in h) for h in sets) for sets in matching.values()),
            "with every valid holder set using a newest birth": sum(
                all(any(i >= born for i in h) for h in sets) for sets in matching.values()),
            "with some valid holder set whose newest births are joins only": len(join_only),
            "seconds": round(time.perf_counter() - start, 4),
        })
        if join_only:
            key = min(join_only)
            field["example of a holder set whose newest births are joins only"] = {
                "carriers": key, "missing": images[key], "holders": join_only[key],
            }
        summaries.append(field)
        print(json.dumps(field), file=sys.stderr, flush=True)
    return {"local": summaries, "pilot connected holder sets per size": 3 if pilot else None}


def checker_report(stages, round_one, *, pilot=False):
    sys.path.insert(0, str(ROOT / "tools"))
    from knotlab.cli import main as knotlab

    def render(clauses, names):
        return "; ".join(" ".join(("" if lit > 0 else "~") + names[abs(lit)] for lit in row)
                         for row in clauses)

    def check(cnf, roles, contact, witnesses, missing):
        order = [r for r in roles if r != contact] + [contact]
        with redirect_stdout(io.StringIO()) as capture:
            status = knotlab(["check", "--cnf", cnf, "--loops", *order[:-1], "--contact", contact,
                              "--witnesses", *witnesses, "--json"])
        assert status == 0
        result = json.loads(capture.getvalue())
        actual_order = [roles.index(name) for name in result["variables"]]
        absent = {"".join(word[i] for i in actual_order) for word in missing}
        assert result["is_knot"] and set(result["allowed"]) == set(WORD_NAMES) - absent
        return result["is_knot"]

    result = []
    stage = DefinedReadings(stages[1])
    variables = {i: f"x{x}" for x, i in stage.var.items()}
    for bond in round_one[:1] if pilot else round_one:
        carriers = [r.carrier for r in bond.readings]
        names = ["r" + "_".join(map(str, carrier)) for carrier in carriers]
        readers = tuple(range(len(variables) + 1, len(variables) + 4))
        legend = variables | dict(zip(readers, names, strict=True))
        joint = stage.clauses.copy()
        for carrier, reader in zip(carriers, readers, strict=True):
            joint.extend(reading_clauses(stage.var, carrier, reader))
        projected = [tuple(-r if b == "1" else r for r, b in zip(readers, word, strict=True))
                     for word in bond.missing]
        for contact in names:
            verdict = check(render(projected, legend), names, contact, (), bond.missing)
            underlying = check(render(joint, legend), names, contact, tuple(variables.values()), bond.missing)
            result.append({"readings": [[list(r.carrier), r.label] for r in bond.readings],
                           "clause": render(projected, legend),
                           "contact": contact, "is_knot": verdict,
                           "all laws essential": len(bond.essential) == len(stages[1]),
                           "actual stage and reading definitions pass": underlying})
    if not pilot:
        raw = read_json(STUDY / "out" / "ring.json")["checker"]
        predicted = [{k: v for k, v in row.items()
                      if k not in ("all laws essential", "actual stage and reading definitions pass")}
                     for row in result if row["all laws essential"]]
        assert predicted == raw
    return result


def checks_report(stages, max_round, *, pilot=False):
    raw = read_json(STUDY / "out" / "collapse.json")["ring"]
    collapsed = []
    round_one = None
    for t in range(0, min(max_round, 3) + 1):
        start = time.perf_counter()
        bonds, _ = scan(Stage(stages[t]))
        if t == 1:
            round_one = bonds
        if pilot:
            bonds = bonds[:8]
        agree = sum(collapse(stages[t], tuple(r.carrier for r in bond.readings), bond.missing) for bond in bonds)
        score = {"round": t, "bonds": len(bonds), "collapse agrees": agree}
        if not pilot:
            assert score == raw[t]
        score["seconds including enumeration"] = round(time.perf_counter() - start, 4)
        collapsed.append(score)
        print(json.dumps(score), file=sys.stderr, flush=True)
    chain_rows = []
    for text, expected in read_json(STUDY / "post" / "chain_and_orbits.json")["chains"].items():
        supports = ast.literal_eval(text)
        stage = Stage(supports)
        bonds, _ = scan(stage)
        every = [b for b in bonds if len(b.essential) == len(supports)]
        chain_rows.append({"supports": supports, "bonds": len(bonds), "every law essential": len(every),
                           "strictly separated": sum(strict_carrier(supports, key) for key, _ in
                                                     (b.carrier_image() for b in bonds)),
                           "literal witness": [asdict(every[0])] if every else []})
        assert len(bonds) == expected["bonds"] and len(every) == expected["every law essential"]
        if every:
            old = expected["example"][0]
            assert any(b.carrier_image() == normalize_image(tuple(tuple(c) for c, _ in old["readings"]),
                                                            tuple(old["missing"]))
                       and b.essential == tuple(old["essential"]) for b in every)
    return {"collapse": collapsed, "chains": chain_rows,
            "round 4 projection bound": round_four_projection_bound(stages, pilot=pilot),
            "canonical round 1 contact roles": checker_report(stages, round_one, pilot=pilot)}


def round_four_projection_bound(stages, *, pilot=False):
    # A fresh distinction of a newest birth belongs to no other law.
    # Omitting it from the carriers lets that law be satisfied by changing
    # it alone. Thus all six freshest distinctions must be read if all
    # laws are essential. Projection onto a subset can only lose witnesses
    # of essentiality, so it suffices to check all nine-place supersets.
    stage = Stage(stages[4])
    previous = tuple(sorted(set().union(*map(set, stages[3]))))
    fresh = tuple(x for x in stage.names if x not in previous)
    assert len(fresh) == 6 and all(sum(x in knot for knot in stage.supports) == 1 for x in fresh)
    deletion_rows = tuple(stage.values[stage.culprit == i] for i in range(len(stage.supports)))
    subsets = Counter()
    for index, subset in enumerate(combinations(previous, 3)):
        if pilot and index == 8:
            break
        mask = stage.mask(subset + fresh)
        base = set(map(int, np.unique(stage.allowed_values & mask)))
        base |= {bits ^ mask for bits in base}
        # An uncomplemented row suffices to witness increase because the
        # projected base is already closed under complement.
        affected = sum(not base.issuperset(map(int, np.unique(rows & mask))) for rows in deletion_rows)
        subsets[affected] += 1
    if not pilot:
        assert sum(subsets.values()) == 286 and max(subsets) < len(stage.supports)
    return {"required newest distinctions": fresh, "checked nine-place supersets": sum(subsets.values()),
            "subset counts by number of laws whose deletion adds states": dict(subsets)}


def swap_report(stages, *, pilot=False):
    raw = read_json(STUDY / "out" / "ring.json")["swaps"]
    prefix = 24 if pilot else None
    records = {}
    for t in (1, 2):
        bonds, _ = scan(Stage(stages[t]), forms="flip", prefix=prefix)
        key = f"all flip-unchanged readings, round {t}"
        records[key] = {
            "bonds": len(bonds),
            "every law essential": sum(len(bond.essential) == len(stages[t]) for bond in bonds),
            "missing counts": json_counter(len(bond.missing) for bond in bonds),
        }
        if not pilot:
            assert records[key] == raw[key]
    exact_low, _ = scan(Stage(stages[2]), prefix=prefix)
    prior_keys = {bond.carrier_image() for bond in exact_low}
    for mode, key in (("padded", "reported carrier cap-four computation, round 2"),
                      ("agree", "genuine carriers up to four, round 2")):
        stage = Stage(stages[2])
        bonds, _ = scan(stage, sizes=(2, 3, 4), forms=mode, prefix=prefix)
        long_bonds = [b for b in bonds if any(len(r.carrier) == 4 for r in b.readings)]
        record = {
            "bonds": len(bonds), "with a carrier of four": len(long_bonds),
            "missing counts": json_counter(len(bond.missing) for bond in bonds),
        }
        if mode == "padded" and not pilot:
            assert record == raw["carriers up to four, round 2"]
        record["underlying shorter bonds for long claims"] = sum(
            normalize_image(tuple(r.used for r in b.readings), b.missing) in prior_keys for b in long_bonds
        )
        checked = {r: stage.redundant_places(r) for r in set(
            r for b in long_bonds for r in b.readings if len(r.carrier) == 4)}
        record["with every four-place carrier depending on all places on the stage"] = sum(
            all(not checked[r] for r in b.readings if len(r.carrier) == 4) for b in long_bonds
        )
        record["examples by missing count"] = {
            n: next(asdict(b) for b in long_bonds if len(b.missing) == n)
            for n in sorted({len(b.missing) for b in long_bonds})
        }
        records[key] = record
    return records


def direct_groups(meetings):
    """Try all subsets of the small live roster in decreasing size order."""
    accepted = []
    for width in range(len(meetings), 1, -1):
        for group in combinations(sorted(meetings), width):
            witnesses = [meetings[i] for i in group]
            if any(first.isdisjoint(second) for first, second in combinations(witnesses, 2)):
                continue
            if width > 2 and set.intersection(*witnesses):
                continue
            if not any(set(group).issubset(larger) for larger in accepted):
                accepted.append(group)
    return sorted(accepted, key=lambda group: (len(group) == 2, group))


def direct_birth_roster(supports):
    holders = defaultdict(list)
    for i, knot in enumerate(supports):
        for x in knot:
            holders[x].append(i)
    assert all(len(owners) <= 2 for owners in holders.values())
    loose = {i: sorted(x for x in knot if len(holders[x]) == 1)
             for i, knot in enumerate(supports)}
    meetings = {i: {other for x in supports[i] for other in holders[x] if other != i}
                for i in loose if loose[i]}
    parents = direct_groups(meetings)
    spending = Counter(i for group in parents for i in group)
    assert all(spent <= len(loose[i]) for i, spent in spending.items())
    inputs = [tuple(sorted(loose[i].pop(0) for i in group)) for group in parents]
    for i, remaining in loose.items():
        for x in remaining:
            parents.append((i,))
            inputs.append((x,))

    upcoming = direct_groups({i: set(group) for i, group in enumerate(parents)})
    demands = Counter(i for group in upcoming for i in group)
    next_distinction = max(holders) + 1
    verified = []
    signed = nae_clauses(tuple(tuple(x + 1 for x in knot) for knot in supports))
    with Solver(bootstrap_with=signed) as old_laws:
        for i, (group, taken) in enumerate(zip(parents, inputs, strict=True)):
            demand = demands[i]
            fresh_count = max(demand, 3 - len(group), 1)
            # When the lookahead permits fewer fresh places, test whether the
            # old laws allow the inputs to be all zero. Complement covers all one.
            if demand < fresh_count and not old_laws.solve(assumptions=[-(x + 1) for x in taken]):
                fresh_count = demand
            fresh = tuple(range(next_distinction, next_distinction + fresh_count))
            verified.append({"knot": len(supports) + i, "parents": group, "inputs": taken,
                             "demand": demand, "fresh": fresh})
            next_distinction += fresh_count
    return verified


def growth_report(stages, births):
    earlier = read_json(STUDY.parent / "NAE-LAYER-20261127-001" / "referee-R1" / "carrier_birth.json")
    original = read_json(STUDY / "out" / "symmetry.json")["rounds"]
    assert tuple(tuple(sorted(r)) for r in earlier["source"]["supports"]) == SOURCE
    results = []
    replayed = SOURCE
    for t, support in enumerate(stages):
        row = {"round": t, "supports": support, "independent growth crosscheck": True}
        if t:
            recorded = [asdict(birth) for birth in births[t - 1]]
            derived = direct_birth_roster(replayed)
            assert derived == recorded
            replayed += tuple(birth["inputs"] + birth["fresh"] for birth in derived)
            if t <= 4:
                assert tuple(tuple(sorted(r)) for r in earlier["with_birth_reading"][t - 1]["supports"]) == support
            row["births"] = recorded
        assert replayed == support and len(support) == original[t]["knots"]
        results.append(row)
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--part", choices=("full", "local", "checks", "swaps", "growth"), required=True)
    parser.add_argument("--max-round", type=int, choices=range(1, 6))
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    started = time.perf_counter()
    max_round = args.max_round or {"full": 4, "local": 5, "checks": 3}.get(args.part, 5)
    if args.part == "full" and max_round > 4:
        parser.error("The full-search replay covers rounds 0 to 4")
    growth_rounds = min(max_round, 2) if args.pilot else max_round
    stages, births = rings_with_births(growth_rounds) if args.part == "growth" else rings_with_births()
    if args.part == "full":
        report = full_report(stages, max_round, pilot=args.pilot)
    elif args.part == "local":
        report = local_report(stages, max_round, pilot=args.pilot)
    elif args.part == "checks":
        report = checks_report(stages, max_round, pilot=args.pilot)
    elif args.part == "swaps":
        report = swap_report(stages, pilot=args.pilot)
    else:
        report = growth_report(stages, births)
    payload = json.dumps({"results": report, "elapsed seconds": round(time.perf_counter() - started, 4)}, indent=2)
    if args.out:
        args.out.write_text(payload + "\n")
    else:
        print(payload)


if __name__ == "__main__":
    main()
