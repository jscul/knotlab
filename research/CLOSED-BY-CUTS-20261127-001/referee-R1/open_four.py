"""Trace the four-clause reading through the cut laws, including births that actually lose a place."""

import argparse
from collections import Counter, defaultdict
from contextlib import redirect_stdout
from io import StringIO
from itertools import permutations, product
import json
from pathlib import Path
from resource import RUSAGE_SELF, getrusage
import sys
from time import perf_counter

from growth_replay import LAWS, advance, census_starts, loose, ordinary_advance, stages

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from knotlab.cli import main as knot_check


PRIOR = ROOT / "research/UPPER-GROWN-20261127-001/referee-R1/upper_sample.json"
CLAUSES = ((0, 2, 4), (0, 3, 5), (1, 2, 5), (1, 3, 4))
CHAIN = (8, 5, 2, 0, 4, 7, 6, 9)


def indexed_columns(names):
    numeric = sorted(names)
    count = len(numeric)
    if count > 25:
        raise ValueError("Raw state table capped at 25 distinctions")
    states = 1 << count
    bits = {}
    for i, name in enumerate(numeric):
        if i < 3:
            material = bytes([(170, 204, 240)[i]]) * (states // 8)
        else:
            size = 1 << (i - 3)
            material = (bytes(size) + b"\xff" * size) * (1 << (count - i - 1))
        bits[name] = int.from_bytes(material, "little")
    return (1 << states) - 1, bits


def agreement(members, columns, all_states):
    ones = zeros = all_states
    for name in members:
        ones &= columns[name]
        zeros &= ~columns[name]
    return zeros | ones


def cells(allowed, readings):
    parts = [allowed]
    for reading in readings:
        parts = [h for part in parts for h in (part & ~reading, part & reading)]
    return parts


def image(allowed, readings):
    return {f"{i:0{len(readings)}b}": part.bit_count()
            for i, part in enumerate(cells(allowed, readings)) if part}


def mixed(parts, reading):
    return sum(bool(part & reading) and bool(part & ~reading) for part in parts)


def upper_readings(readings):
    a, aa, b, bb, c, cc = readings
    return a & aa, b | bb, c | cc


def upper_word_counts(stage, carriers):
    names = set().union(*map(set, stage), *map(set, carriers))
    full, cols = indexed_columns(names)
    allowed = full
    for knot in stage:
        allowed &= ~agreement(knot, cols, full)
    readings = [agreement(group, cols, full) for group in carriers]
    return image(allowed, upper_readings(readings))


def direct(stage, carriers):
    names = sorted(set().union(*map(set, stage), *map(set, carriers)))
    full, cols = indexed_columns(names)
    laws = [full ^ agreement(k, cols, full) for k in stage]
    reads = [agreement(c, cols, full) for c in carriers]
    upper = upper_readings(reads)
    assert all(len(c) in {2, 3} for c in carriers)
    assert len(set().union(*map(set, carriers))) == sum(map(len, carriers))
    allowed = full
    for law in laws:
        allowed &= law
    uppers = image(allowed, upper)
    seven = {f"{v:03b}" for v in range(7)}
    if set(uppers) != seven:
        return None
    lowers, upper_mixed = [], []
    for clause in CLAUSES:
        triple = [reads[j] for j in clause]
        counts = image(allowed, triple)
        if set(counts) != seven:
            return None
        lowers.append(counts)
        upper_mixed.append([mixed(cells(allowed, triple), u) for u in upper])
    raw_mixed = [[mixed(cells(allowed, (cols[x] for x in knot)), r) for r in reads] for knot in stage]
    if not all(all(row) for row in (*raw_mixed, *upper_mixed)):
        return None
    flips = []
    for carrier, reading in zip(carriers, reads):
        row = []
        for name in carrier:
            shift = 1 << names.index(name)
            row.append((allowed & ~cols[name] & (allowed >> shift)
                        & (reading ^ (reading >> shift))).bit_count())
        flips.append(row)
    if not all(all(row) for row in flips):
        return None
    forbidden = upper[0] & upper[1] & upper[2]
    restored = []
    for i in range(len(laws)):
        value = forbidden
        for j, law in enumerate(laws):
            if i != j:
                value &= law
        restored.append(value.bit_count())
    return {
        "enumerated_distinction_ids": names,
        "source_states": allowed.bit_count(),
        "raw_assignments": 1 << len(names),
        "carriers": carriers,
        "lower_indices": CLAUSES,
        "all_lower_images": lowers,
        "upper": uppers,
        "six_reading_words": image(allowed, reads),
        "source_fixings_mixed_for_each_lower_reading": raw_mixed,
        "lower_clause_fixings_mixed_for_each_upper_reading": upper_mixed,
        "allowed_single_member_flips": flips,
        "upper_111_restored_by_omitting_each_source_law": restored,
    }


def fixed_controls():
    rows = list(product((0, 1), repeat=6))
    results = {}
    for omitted in (None, 0, 1, 2, 3):
        allowed = [w for w in rows if all(
            omitted == i or not all(w[j] for j in clause) for i, clause in enumerate(CLAUSES))]
        upper = Counter("".join(map(str, upper_readings(w))) for w in allowed)
        assert (len(upper), upper.get("111", 0)) == ((7, 0) if omitted is None else (8, 1))
        results[str(omitted)] = {"lower_words": len(allowed), "upper": dict(sorted(upper.items()))}
    capture = StringIO()
    with redirect_stdout(capture):
        code = knot_check(["check", "--cnf", "~A ~B ~C", "--loops", "A", "B", "--contact", "C", "--json"])
    check = json.loads(capture.getvalue())
    assert not code and check["is_knot"]
    return {"four_clause_conjunction_omission": results, "canonical_check_for_the_seven_projected_words": check}


def lineage(start, law, stop):
    step = start
    events = []
    for t in range(1, stop + 1):
        ordinary = ordinary_advance(step)
        growth = advance(step, law)
        assert ordinary.status == growth.status == "funded"
        events.append({
            "round": t,
            "births": [{"knot": b.knot, "parents": b.parents, "inputs": b.inputs, "demand": b.demand,
                        "ordinary_fresh_on_this_parent_stage": o.fresh, "rival_fresh": b.fresh}
                       for b, o in zip(growth.births, ordinary.births, strict=True)]
        })
        step = growth.supports
    return step, events


def addresses(ordered_laws):
    by_distinction = defaultdict(list)
    for pos, law in enumerate(ordered_laws):
        for d in law:
            by_distinction[d].append(pos)
    groups = defaultdict(list)
    for d, places in by_distinction.items():
        groups[tuple(places)].append(d)
    return {k: sorted(v) for k, v in groups.items()}


def paths(stage, required):
    knots = {i: frozenset(k) for i, k in enumerate(stage) if len(k) == 3}
    neighbors = {i: set() for i in knots}
    for i, s in knots.items():
        for j, t in knots.items():
            if j < i and len(s & t) == 1:
                neighbors[i].add(j)
                neighbors[j].add(i)

    def extend(path, used, occupied):
        if len(path) == 8:
            if required & used:
                yield path
            return
        for nxt in sorted(neighbors[path[-1]] - used):
            if len(occupied & knots[nxt]) == 1:
                yield from extend((*path, nxt), used | {nxt}, occupied | knots[nxt])

    for i in knots:
        yield from extend((i,), {i}, knots[i])


def transports(template, carriers, stage, chain):
    actual = addresses([stage[j] for j in chain])
    assert set(actual) == set(template)
    choices = []
    for address, names in template.items():
        assert len(actual[address]) == len(names)
        choices.append([dict(zip(names, p)) for p in permutations(actual[address])])
    for maps in product(*choices):
        mapping = {old: new for local in maps for old, new in local.items()}
        yield tuple(tuple(sorted(mapping[x] for x in group)) for group in carriers)


def metadata(index, law, start, r, stage, carriers, details):
    traced, log = lineage(start, law, r)
    assert traced == stage
    return {"entry": index, "law": law, "round": r, "start": start, "stage": stage,
            "loose": loose(stage), "ordinary_comparison_is_on_the_same_parent_stage": True,
            "birth_history": log, "readout": details}


def shared_sample(law, data):
    index = data["census_rank"]
    start = census_starts()[index]
    carriers = tuple(tuple(k) for k, sign in data["witness"]["raw_agreements_and_selected_value"] if sign == 1)
    stage = dict(stages(start, law, through=2))[2]
    assert list(map(list, stage)) == data["witness"]["source"]
    result = direct(stage, carriers)
    assert result and result["upper_111_restored_by_omitting_each_source_law"] == \
           data["witness"]["restored_upper_111_by_dropped_law"]
    assert loose(stage) and all(result["upper_111_restored_by_omitting_each_source_law"][len(start):])
    out = metadata(index, law, start, 2, stage, carriers, result)
    eight = tuple(stage[j] for j in CHAIN)
    eight_result = direct(eight, carriers)
    assert eight_result and all(eight_result["upper_111_restored_by_omitting_each_source_law"])
    out["sufficient_eight_laws_in_order"] = CHAIN
    out["restricted_to_eight_laws"] = eight_result
    return out


def changed_stages(law, source_limit, cap, different_rivals):
    for i, start in enumerate(census_starts()[:source_limit]):
        stage = start
        for r in range(1, 7):
            result = advance(stage, law)
            if result.status != "funded":
                break
            old, stage = stage, result.supports
            n = len(set().union(*map(set, stage)))
            if n > cap:
                break
            if n < 17 or not loose(stage):
                continue
            ordinary = ordinary_advance(old)
            alt_law = LAWS[1 - LAWS.index(law)]
            cmp = advance(old, alt_law) if different_rivals else ordinary
            cut = {b.knot for b, other in zip(result.births, cmp.births, strict=True)
                   if len(b.fresh) < len(other.fresh)}
            if cut:
                yield (n, len(stage), i, r), start, old, stage, cut


def find_changed(law, data, source_limit, cap, candidate_limit, different_rivals):
    witness = data["witness"]
    template = addresses([witness["source"][j] for j in CHAIN])
    carriers = [k for k, sign in witness["raw_agreements_and_selected_value"] if sign == 1]
    info = Counter()
    actual = sorted(changed_stages(law, source_limit, cap, different_rivals))
    info["stages_in_shortened_birth_roster"] = len(actual)
    for (n, k, i, r), start, old, stage, cut in actual[:candidate_limit]:
        info["roster_stages_visited"] += 1
        for chain in paths(stage, cut):
            info["mapped_eight_knot_rows"] += 1
            for mapped in transports(template, carriers, stage, chain):
                info["mapped_carrier_choices"] += 1
                detail = direct(stage, mapped)
                if not detail:
                    continue
                drops = detail["upper_111_restored_by_omitting_each_source_law"]
                decisive = sorted(j for j in cut if drops[j])
                if not decisive:
                    continue
                row = metadata(i, law, start, r, stage, mapped, detail)
                row.update(eight_source_laws_in_order=chain, decisively_shortened_latest_births=decisive)
                original = ordinary_advance(old).supports
                rival = advance(old, LAWS[1 - LAWS.index(law)]).supports
                row["ordinary_on_same_parent_upper"] = upper_word_counts(original, mapped)
                row["other_cut_on_same_parent_upper"] = upper_word_counts(rival, mapped)
                assert row["ordinary_on_same_parent_upper"]["111"]
                return dict(info), row
    return dict(info), None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", choices=("transfer", "changed", "different"), required=True)
    parser.add_argument("--law", choices=LAWS, action="append")
    parser.add_argument("--start-limit", type=int, default=7075)
    parser.add_argument("--candidate-limit", type=int, default=10000)
    parser.add_argument("--distinction-cap", type=int, default=22)
    parser.add_argument("--output", required=True, type=Path)
    opts = parser.parse_args()
    then = perf_counter()
    prior = json.loads(PRIOR.read_text())[0]
    audit = {"source_of_carriers": str(PRIOR.relative_to(ROOT)), "task": opts.task, "controls": fixed_controls(),
             "frozen_source_roster_limit": opts.start_limit, "search_distinction_cap": opts.distinction_cap,
             "search_stage_limit_per_law": opts.candidate_limit, "results": {}}
    for law in opts.law or LAWS:
        if opts.task == "transfer":
            item = {"witness": shared_sample(law, prior)}
        else:
            stats, result = find_changed(law, prior, opts.start_limit, opts.distinction_cap, opts.candidate_limit,
                                         opts.task == "different")
            item = {"counts": stats, "witness": result}
        audit["results"][law] = item
    audit["seconds"] = round(perf_counter() - then, 5)
    audit["peak_KiB"] = getrusage(RUSAGE_SELF).ru_maxrss
    opts.output.write_text(json.dumps(audit, indent=2) + "\n")
    for law, item in audit["results"].items():
        w = item["witness"]
        print(law, (w["entry"], w["round"]) if w else None, item.get("counts", {}))
    print("seconds", audit["seconds"], "peak_KiB", audit["peak_KiB"])


if __name__ == "__main__":
    main()
