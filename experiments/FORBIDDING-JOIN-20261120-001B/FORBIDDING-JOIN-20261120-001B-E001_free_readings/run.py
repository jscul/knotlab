"""Exact free-setting readings before and after the frozen fresh-count cutoffs."""

import argparse
from dataclasses import dataclass
import gzip
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DESIGN = ROOT / "research/FORBIDDING-JOIN-20261120-001/preregistration.md"
PREV_FAMILY = ("ENTANGLEMENT-READ-20261120-001B/"
               "ENTANGLEMENT-READ-20261120-001B-E001_separated_readings")
PREV = ROOT / "experiments" / PREV_FAMILY
PREV_DATA = ROOT / "artifacts" / PREV_FAMILY / "exact_readings.json.gz"
RELAY = ROOT / "research/ENTANGLEMENT-READ-20261120-001/embodied_control.json"
ORDINARY = ROOT / "experiments/ORDINARY-DYNAMICS-20261120-001A/ORDINARY-DYNAMICS-20261120-001A-E001_ordinary"
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name
sys.path.insert(0, str(PREV))

from counts import StageCounts, names  # noqa: E402
from exact_counts import boolean_words  # noqa: E402
from readings import (BANDS, ORIGINS, CONTEXTS, choose_placements, context_counts, context_scores,  # noqa: E402
                      pair_counts, shortest_steps, step_neighborhoods)
from rival_growth import ARMS, grow  # noqa: E402
from summarize_rivals import summarize  # noqa: E402


def load_module(path, name):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


precedent = load_module(PREV / "run.py", "entanglement_predecessor")
rulers = load_module(ORDINARY / "rulers.py", "ordinary_closure_source")
ENGINE = precedent.canonical
PROTOCOLS = (("external_pairs", 2), ("six_marks", 3))


@dataclass(frozen=True)
class Source:
    name: str
    group: str
    supports: tuple
    provenance: dict
    horizon: int
    fixed: dict


def all_sources():
    for old in precedent.sources(False):
        fixed = {width: old.fixed_marks(width) for _, width in PROTOCOLS}
        yield Source(old.name, old.group, old.supports, old.provenance, 1, fixed)
    relay = json.loads(RELAY.read_text())
    yield Source("two_relays", "targeted_relay", tuple(tuple(sorted(row)) for row in relay["start_supports"]),
                 {"method": "prior ten-knot control", "names": relay["names"]}, 1,
                 {2: (0, 1, (1, 2), (5, 6)), 3: (0, 1, (1, 2, 0), (5, 6, 4))})
    for extra in (False, True):
        supports, roles = rulers.source(None, extra)
        yield Source("closure_spare" if extra else "closure_bare", "targeted_closure", supports,
                     {"method": "prior four-knot closure comparison", "roles": roles, "spare": extra}, 2, {})


def source_record(source):
    return {"name": source.name, "group": source.group, "provenance": source.provenance,
            "initial_supports": source.supports, "horizon": source.horizon, "laws": {}}


def eligible_fixed(stage, certificates, fixed):
    alice, bob, left, right = fixed
    if not certificates[alice]["eligible"] or not certificates[bob]["eligible"]:
        return None, "reader_support_lost_full_law"
    if not set(left) <= set(stage[alice]) or not set(right) <= set(stage[bob]):
        return None, "absent_marks"
    steps = shortest_steps(left, right, step_neighborhoods(stage)[0])
    if steps is not None and steps < 2:
        return None, "cross_steps_below_two"
    band = "no_chain" if steps is None else "2" if steps == 2 else "finite_3_or_more"
    return (band, {"supports": [alice, bob], "alice": left, "bob": right, "cross_steps": steps}), None


def placement_roster(source, stage, certificates, previous, width):
    fixed = source.fixed.get(width)
    if source.name == "two_relays":
        choice, failure = eligible_fixed(stage, certificates, fixed)
        roster = {"candidate_count": 1, "excluded": {failure: 1} if failure else {}, "slots": []}
        for band in BANDS:
            for origin in ORIGINS:
                eligible = choice is not None and band == choice[0] and origin == "old_only"
                roster["slots"].append({"band": band, "origin": origin, "eligible": int(eligible),
                                        "placement": choice[1] if eligible else None})
        return roster
    if fixed is not None:
        assert eligible_fixed(stage, certificates, fixed)[0] is not None
    return choose_placements(stage, certificates, max(names(previous)) + 1, width, fixed)


def score_external(mass, width):
    words = [tuple(map(int, word)) for word in boolean_words(2 * width)]
    pairs = pair_counts(words, mass, width)
    cells = [context_counts(pairs, *context) for context in CONTEXTS]
    for cell in cells:
        cell["mass"] = [1, 4]
        cell["all_marks_tv_from_common"] = [0, 1]
        cell["joint_pairs_tv_from_common"] = [0, 1]
    record = context_scores(cells)
    zeros = [[[0, 1]] * 2] * 2
    assert record["pair_marginal_remote_tv"] == zeros
    for protocol in ("I", "II"):
        info = record[protocol]
        n, d = info["maximum"]
        assert n <= 2 * d and info["outcome_marginal_remote_tv"] == zeros
    return record


def measure_slot(slot, counter, previous_count, width):
    placement = slot["placement"]
    marks = placement["alice"] + placement["bob"]
    uniform = counter.histogram(marks, "U")[0]
    lifted, divisor = counter.histogram(marks, "L")
    retained = counter.retained()
    assert sum(uniform) == counter.total() and sum(lifted) == retained * divisor
    assert [amount > 0 for amount in uniform] == [amount > 0 for amount in lifted]
    half = len(uniform) // 2
    tilted = uniform[:half] + [2 * value for value in uniform[half:]]
    weights = {"U": weight_table(uniform, 1, width), "T": weight_table(tilted, 1, width)}
    if retained == previous_count:
        weights["L"] = weight_table(lifted, divisor, width)
    else:
        weights["L"] = {"undefined": "positive_mass_old_states_have_no_extension"}
        weights["L_survival"] = weight_table(lifted, divisor, width)
    assert all(all(count > 0 for count in pair) for pair in weights["U"]["readings"]["contexts"][0]["pair_marginals"])
    return {"mark_order": marks, "weightings": weights}


def weight_table(masses, unit, width):
    return {"counts": masses, "total": sum(masses), "integer_units_per_unscaled_mass": unit,
            "readings": score_external(masses, width)}


def prepare_stage(source, law, age, stage, previous, previous_count, start_count):
    counter = StageCounts(law, previous, stage)
    retained = counter.retained()
    initial_retained = counter.initial_survivors(names(source.supports)) if age == 2 else retained
    total = counter.total()
    certificates = counter.certify()
    assert len(certificates) == len(stage) and 0 <= retained <= previous_count
    assert bool(retained) == bool(total)
    assert 0 <= initial_retained <= start_count
    result = {"age": age, "status": "reached" if total else "empty", "supports": stage,
              "distinct_names": names(stage), "complete_states": total, "support_certificates": certificates,
              "every_displayed_support_lawful": all(row["eligible"] for row in certificates),
              "literal_L": "defined" if retained == previous_count else "undefined",
              "L_reference_age": max(age - 1, 0), "previous_stage_states": previous_count,
              "surviving_previous_states": retained, "lost_previous_states": previous_count - retained,
              "initial_states": start_count, "surviving_initial_states": initial_retained}
    if total:
        for family, width in PROTOCOLS:
            roster = placement_roster(source, stage, certificates, previous, width)
            result[family] = roster
            for slot in roster["slots"]:
                if slot["placement"] is not None:
                    slot["result"] = measure_slot(slot, counter, previous_count, width)
    return result


def run_history(source, law, arm):
    old = source.supports
    initial_count = StageCounts(law, old, old).total()
    stages = [prepare_stage(source, law, 0, old, old, initial_count, initial_count)]
    assert stages[0]["every_displayed_support_lawful"]
    stages[0]["stage_persists"] = True
    old_count = initial_count
    for age in range(1, source.horizon + 1):
        stage, receipt = grow(old, law, arm, ENGINE)
        if stage is None:
            stages.append({"age": age, "status": receipt["status"], "transition": receipt,
                           "persistent_states": old_count, "stage_persists": bool(old_count)})
            break
        record = prepare_stage(source, law, age, stage, old, old_count, initial_count)
        record["transition"] = receipt
        record["stage_persists"] = bool(record["complete_states"])
        stages.append(record)
        if record["status"] == "empty":
            break
        old, old_count = stage, record["complete_states"]
    return stages


def validate_baseline(record, archived):
    comparisons = 0
    for law in ("parity", "nae"):
        for stage, previous in zip(record["laws"][law]["ordinary"], archived["laws"][law], strict=True):
            assert stage["status"] == "reached" and stage["complete_states"] == previous["complete_assignments"]
            assert stage["supports"] == tuple(map(tuple, previous["supports"]))
            if stage["age"]:
                for planned, old in zip(stage["transition"]["births"], previous["growth"]["births"], strict=True):
                    assert planned["parents"] == tuple(old["parents"]) and planned["inputs"] == tuple(old["consumed"])
                    assert planned["fresh"] == tuple(old["fresh"]) and planned["D"] == old["lookahead_demand"]
                assert not stage["lost_previous_states"]
            for family, _ in PROTOCOLS:
                assert stage[family]["candidate_count"] == previous[family]["candidate_count"]
                assert stage[family]["excluded"] == previous[family]["excluded"]
                for measured, saved in zip(stage[family]["slots"], previous[family]["slots"], strict=True):
                    assert measured["eligible"] == saved["eligible"]
                    if not measured["eligible"]:
                        continue
                    comparisons += 1
                    assert measured["result"]["mark_order"] == tuple(saved["result"]["mark_order"])
                    for name, new_weight in measured["result"]["weightings"].items():
                        old_weight = saved["result"]["weightings"][name]
                        assert new_weight["counts"] == old_weight["counts"]
                        assert new_weight["integer_units_per_unscaled_mass"] == old_weight["integer_units_per_unscaled_mass"]
                        assert json.loads(json.dumps(new_weight["readings"])) == old_weight["arms"]["external"]
    return comparisons


def matched_archived_readings(stage, old, law, archive_stage):
    """Carry every frozen grown mark whose distinctions and reader law survive the cutoff."""
    out = {}
    counter = StageCounts(law, old, stage["supports"]) if stage["status"] == "reached" else None
    for family, width in PROTOCOLS:
        rows = []
        for slot in archive_stage[family]["slots"]:
            original = slot["placement"]
            if original is None:
                continue
            prior = {"band": slot["band"], "origin": slot["origin"], "placement": original}
            if counter is None:
                rows.append({"prior": prior, "undefined": stage["status"]})
                continue
            alice, bob = original["supports"]
            left, right = tuple(original["alice"]), tuple(original["bob"])
            if not set(left) <= set(stage["supports"][alice]) or not set(right) <= set(stage["supports"][bob]):
                rows.append({"prior": prior, "undefined": "absent_marks"})
                continue
            fixed = alice, bob, left, right
            choice, failure = eligible_fixed(stage["supports"], stage["support_certificates"], fixed)
            if failure:
                rows.append({"prior": prior, "undefined": failure})
                continue
            band, placement = choice
            assert band == slot["band"] and placement["cross_steps"] == original["cross_steps"]
            fresh = measure_slot({"placement": placement}, counter, stage["previous_stage_states"], width)
            rows.append({"prior": prior, "result": fresh})
        out[family] = rows
    return out


def naming_check(source, law, arm, stages):
    fixed = {d: d for d in names(source.supports)}
    old = source.supports
    checks = []
    for stage in stages[1:]:
        alternate, receipt = grow(old, law, arm, ENGINE, allocation="last")
        assert receipt["status"] == stage["transition"]["status"]
        if alternate is None:
            break
        assert receipt["following_funding"]["status"] == stage["transition"]["following_funding"]["status"]
        for expected, translated in zip(stage["transition"]["births"], receipt["births"], strict=True):
            assert expected["parents"] == translated["parents"] and expected["D"] == translated["D"]
            assert tuple(fixed[bit] for bit in expected["inputs"]) == translated["inputs"]
            fixed.update(zip(expected["fresh"], translated["fresh"], strict=True))
        assert alternate == tuple(tuple(fixed[bit] for bit in support) for support in stage["supports"])
        assert len(set(fixed.values())) == len(fixed)
        counter = StageCounts(law, old, alternate)
        assert counter.total() == stage["complete_states"] and counter.retained() == stage["surviving_previous_states"]
        checked = 0
        for family, _ in PROTOCOLS:
            for slot in stage.get(family, {}).get("slots", []):
                if slot["placement"] is None:
                    continue
                retained = slot["result"]
                marks = tuple(fixed[bit] for bit in retained["mark_order"])
                actual = counter.histogram(marks, "U")[0]
                assert actual == retained["weightings"]["U"]["counts"]
                checked += 1
        checks.append({"age": stage["age"], "take_first_to_last": sorted(fixed.items()),
                       "transported_uniform_histograms": checked})
        old = alternate
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    frozen = json.loads((HERE / "contract.json").read_text())["design_sha256"]
    assert frozen == sha256(DESIGN.read_bytes()).hexdigest()
    start = time.monotonic()
    archive = {source["name"]: source for source in json.loads(gzip.decompress(PREV_DATA.read_bytes()))["sources"]}
    specs = tuple(all_sources())
    records = [source_record(source) for source in specs]
    compared, naming = 0, 0
    for source, record in zip(specs, records, strict=True):
        for law in ("parity", "nae"):
            record["laws"][law] = {"ordinary": run_history(source, law, "ordinary")}
        if source.name in archive:
            compared += validate_baseline(record, archive[source.name])
    assert len(archive) == 33 and compared == 694
    print(f"Verified {compared} ordinary placements against the predecessor in {time.monotonic() - start:.3f} s", flush=True)
    for source, record in zip(specs, records, strict=True):
        for law in ("parity", "nae"):
            histories = record["laws"][law]
            for arm in ARMS[1:]:
                histories[arm] = run_history(source, law, arm)
                if source.name in archive:
                    stage1 = histories[arm][1]
                    stage1["matched_predecessor_marks"] = matched_archived_readings(
                        stage1, source.supports, law, archive[source.name]["laws"][law][1])
                if source.group in ("controls", "built", "targeted_closure", "targeted_relay"):
                    checks = naming_check(source, law, arm, histories[arm])
                    record.setdefault("naming_checks", {}).setdefault(law, {})[arm] = checks
                    naming += sum(row["transported_uniform_histograms"] for row in checks)
        print(f"{source.name} complete at {time.monotonic() - start:.3f} s", flush=True)

    meta = {"design_sha256": frozen, "ordinary_archive_sha256": sha256(PREV_DATA.read_bytes()).hexdigest(),
            "ordinary_archive_placements_replayed": compared, "private_naming_uniform_histograms": naming,
            "histogram_order": "Alice u,v[,unused], then Bob u,v[,unused]; binary lexicographic order",
            "next_funding": "computed on current written supports with all low-arity rows retained",
            "L_reference": "previous measured stage; age one uses the start, age two uses age one; age zero uses itself",
            "L_survival": "one conditional weighting on all previous assignments admitting a lift; reported only on loss",
            "selection": "predecessor's lexicographic support/mark order and named minimum marks; fixed relay marks",
            "allocation": "keep the first f of ordinary q private names; the alternate keeps the last f"}
    args.output.mkdir(parents=True, exist_ok=True)
    output = json.dumps({"metadata": meta, "sources": records}, separators=(",", ":")).encode()
    (args.output / "exact_readings.json.gz").write_bytes(gzip.compress(output, mtime=0))
    (args.output / "summary.json").write_text(json.dumps(summarize(records, meta), indent=2) + "\n")


if __name__ == "__main__":
    main()
