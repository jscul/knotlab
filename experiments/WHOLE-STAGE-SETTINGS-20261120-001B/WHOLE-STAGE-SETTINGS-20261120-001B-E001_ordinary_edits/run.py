"""Compute the frozen one-round funding and closing trials with all outcomes retained."""

from collections import Counter, defaultdict
from fractions import Fraction
import gzip
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, product
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DESIGN = ROOT / "research/WHOLE-STAGE-SETTINGS-20261120-001/preregistration.md"
PRECEDENT = ROOT / ("experiments/ENTANGLEMENT-READ-20261120-001B/"
                    "ENTANGLEMENT-READ-20261120-001B-E001_separated_readings")
FORBIDDING = ROOT / ("experiments/FORBIDDING-JOIN-20261120-001B/"
                    "FORBIDDING-JOIN-20261120-001B-E001_free_readings")
COMPACT = ROOT / ("experiments/ORDINARY-DYNAMICS-20261120-001A/"
                  "ORDINARY-DYNAMICS-20261120-001A-E001_ordinary/end_operator.py")
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name
sys.path.extend((str(PRECEDENT), str(FORBIDDING)))

from counts import StageCounts  # noqa: E402
from edits import (Preparation, built_cases, from_meetings, holders, private_marks, proposal_receipt,  # noqa: E402
                   responses, separations)
from exact_counts import NotAllEqualSupport  # noqa: E402
from minimum import closing_lower_bound, smallest_funding  # noqa: E402
from records import fraction, local_record, local_shape, record_tv, weighted_old_support  # noqa: E402


def load(path, name):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


source = load(PRECEDENT / "run.py", "previous_sources")
compact = load(COMPACT, "independent_compact_update")
SETTINGS = tuple(product((0, 1), repeat=2))
LAWS = ("parity", "nae")


def growth(preparation, settings, law, swap=None):
    edited = preparation.edited(settings, swap)
    final, receipt = proposal_receipt(edited, law, max(preparation.optional) + 1, source.canonical, compact)
    return edited, final, receipt


def trace_naming(preparation, edited, final, receipt, law):
    private = sorted({d for row in private_marks(edited).values() for d in row} | set(preparation.optional))
    renaming = dict(zip(private, reversed(private), strict=True))
    translate = lambda d: renaming.get(d, d)
    transported = tuple(tuple(map(translate, row)) for row in edited)
    outcome, trace = proposal_receipt(transported, law, max(preparation.optional) + 1, source.canonical, compact)
    assert trace["status"] == receipt["status"] and trace["closes"] == receipt["closes"]
    assert tuple(tuple(map(translate, row)) for row in final) == outcome
    return {"transported_private_names": renaming, "status": trace["status"], "physical_supports_transport": True}


def measure(preparation, settings, law, base_counter, *, full):
    edited, final, receipt = growth(preparation, settings, law)
    outcome = responses(preparation, edited, final, receipt)
    separation = separations(preparation, edited, receipt)
    assert not separation["common_proposed_child"]
    row = {"settings": settings, "edited_supports": edited, "final_supports": final,
           "receipt": receipt, "separation": separation, "bits": outcome,
           "trial_counts": point_mass(outcome, 1)}
    if not full:
        row["structural_records"] = [local_shape(preparation, edited, receipt, side, settings[side])[0] for side in (0, 1)]
        return row

    _, swapped, swapped_receipt = growth(preparation, settings, law, swap=0)
    assert (receipt["status"], receipt["closes"]) == (swapped_receipt["status"], swapped_receipt["closes"])
    assert outcome == responses(preparation, edited, swapped, swapped_receipt)
    row["name_transport"] = trace_naming(preparation, edited, final, receipt, law)
    row["single_holder_port_swap"] = {"holder": preparation.readers[0], "births": swapped_receipt["births"],
                                      "binary_outcomes_preserved": True}
    edited_counter = StageCounts(law, edited, edited)
    counter = StageCounts(law, edited, final)
    assert counter.retained() == edited_counter.total() > 0
    input_gate = edited_counter.certify()
    assert all(cell["eligible"] for cell in input_gate)
    final_gate = counter.certify()
    for support, certificate in zip(final, final_gate, strict=True):
        assert certificate["full_law"] and certificate["k1"] and certificate["k2"] and certificate["k3"]
        if not certificate["eligible"]:
            assert law == "parity" and len(support) == 2 and receipt["closes"]
    row["edited_support_certificate"] = input_gate
    row["final_support_certificate"] = final_gate
    row["state_weightings"] = weighted_old_support(preparation, edited, final, law, counter)
    row["state_weightings"]["prepared_old_total"] = base_counter.total()
    for weighting in ("prepared_old", "uniform_edited", "uniform_final"):
        denominator = row["state_weightings"][weighting + "_total"]
        row["state_weightings"][weighting + "_joint_counts"] = point_mass(outcome, denominator)
    row["local_records"] = [local_record(preparation, edited, receipt, settings, side, law, base_counter, counter)
                            for side in (0, 1)]
    return row


def point_mass(bits, denominator):
    return [denominator if [a, b] == list(bits) else 0 for a, b in SETTINGS]


def table(rows, *, records):
    effects = [(-1) ** sum(row["bits"]) for row in rows]
    signs = [word for word in product((-1, 1), repeat=4) if word.count(-1) % 2]
    scores = [sum(e * s for e, s in zip(effects, sign, strict=True)) for sign in signs]
    index = (((0, 1), (2, 3)), ((0, 2), (1, 3)))
    tv_bits = [[int(rows[i]["bits"][side] != rows[j]["bits"][side]) for i, j in pairs]
               for side, pairs in enumerate(index)]
    if records:
        tv_full = {weighting: [[fraction(record_tv(rows[i]["local_records"][side], rows[j]["local_records"][side], weighting))
                                for i, j in pairs] for side, pairs in enumerate(index)]
                   for weighting in ("carried_old_state_full", "uniform_final_after_only")}
    else:
        tv_full = {"structure_only": [[int(rows[i]["structural_records"][side] != rows[j]["structural_records"][side])
                                       for i, j in pairs] for side, pairs in enumerate(index)]}
    own_setting_dep = [any(rows[i]["bits"][side] != rows[j]["bits"][side] for i, j in index[1 - side]) for side in (0, 1)]
    return {"contexts": rows, "correlations": effects, "signed_s": sum(effects[:3]) - effects[3],
            "sign_scores": [{"signs": sign, "score": score} for sign, score in zip(signs, scores, strict=True)],
            "maximum": max(scores), "selected_bit_far_setting_tv": tv_bits, "accessible_record_far_setting_tv": tv_full,
            "own_setting_changes_bit": own_setting_dep,
            "both_settings_change_both_bits": all(own_setting_dep) and all(any(result) for result in tv_bits)}


def verify_design(preparation, rows):
    comparison_groups = rows[0]["receipt"]["groups"]
    if preparation.mechanism == "S":
        assert all(row["receipt"]["groups"] == comparison_groups for row in rows)
        return
    group, = comparison_groups
    assert preparation.readers[0] in group and preparation.readers[1] not in group
    for row in rows:
        birth, = [entry for entry in row["receipt"]["births"] if entry["parents"] == group]
        assert birth["old_inputs"] == rows[0]["receipt"]["births"][0]["old_inputs"]
        if row["settings"][1]:
            assert row["separation"]["witnessed_steps"] is None


def built_results():
    for prep in built_cases():
        data = {"name": prep.name, "mechanism": prep.mechanism, "base": prep.base,
                "readers": prep.readers, "marks": prep.marks, "optional": prep.optional, "law_tables": {}}
        for law in LAWS:
            base = StageCounts(law, prep.base, prep.base)
            rows = [measure(prep, setting, law, base, full=True) for setting in SETTINGS]
            verify_design(prep, rows)
            data["law_tables"][law] = table(rows, records=True)
        yield data
        print(f"{prep.name} measured", flush=True)


def robustness_results():
    for sampled in source.sources(False):
        base = sampled.supports
        loose = private_marks(base)
        group_plan = source.canonical.J.S.from_junctions(base)
        groups = [set(group) for group in group_plan.groups_among(i for i in loose if loose[i])]
        candidates = [pair for pair in combinations((i for i in loose if loose[i]), 2)
                      if not any(set(pair) <= group for group in groups)]
        row = {"name": sampled.name, "group": sampled.group, "provenance": sampled.provenance,
               "base": base, "eligible_pairs": candidates}
        if not candidates:
            row["ineligible"] = "no_pair_of_live_holders_without_common_proposal"
            yield row
            continue
        a, b = candidates[0]
        prep = Preparation(sampled.name, "S", base, (a, b), (loose[a][0], loose[b][0]), sampled.group)
        row["readers"], row["marks"], row["optional"] = prep.readers, prep.marks, prep.optional
        row["connected_readers"] = separations(prep, base, {"groups": groups, "live": [i for i in loose if loose[i]]})["written_holder_steps"] is not None
        row["law_tables"] = {}
        for law in LAWS:
            rows = [measure(prep, setting, law, None, full=False) for setting in SETTINGS]
            verify_design(prep, rows)
            row["law_tables"][law] = table(rows, records=False)
        yield row


def brief(tables):
    return {law: {key: table[key] for key in ("correlations", "signed_s", "maximum", "selected_bit_far_setting_tv",
                                             "accessible_record_far_setting_tv", "both_settings_change_both_bits")}
            for law, table in tables.items()}


def summary(built, sample, minimum):
    grouped = defaultdict(Counter)
    for row in sample:
        group = grouped[row["group"]]
        group["predeclared"] += 1
        if row.get("ineligible"):
            group["ineligible"] += 1
            continue
        for law in LAWS:
            group[f"{law}_eligible"] += 1
            observed = row["law_tables"][law]
            group[f"{law}_any_remote_bit_change"] += int(any(any(side) for side in observed["selected_bit_far_setting_tv"]))
            group[f"{law}_both_bits_depend_on_both_settings"] += int(observed["both_settings_change_both_bits"])
            group[f"{law}_above_two"] += int(observed["maximum"] > 2)
            group[f"{law}_funded_trials"] += sum(item["receipt"]["status"] == "extend" for item in observed["contexts"])
    return {"minimum": minimum, "built": [{"name": row["name"], "tables": brief(row["law_tables"])} for row in built],
            "robustness": [{"group": group, **row} for group, row in grouped.items()], "robustness_denominator": len(sample),
            "robustness_excluded": [row["name"] for row in sample if row.get("ineligible")]}


def main():
    start = time.monotonic()
    frozen = json.loads((HERE / "contract.json").read_text())["design_sha256"]
    assert frozen == sha256(DESIGN.read_bytes()).hexdigest()
    def nae_lawful(meetings, supply):
        supports = from_meetings(meetings, supply)
        with NotAllEqualSupport(supports) as oracle:
            return all(oracle.certificate(support)["eligible"] for support in supports)

    minimum = {"S": smallest_funding(13, False), "S_no_written_meeting": smallest_funding(16, True),
               "S_without_law_filter": smallest_funding(13, False, parity=False),
               "S_no_written_meeting_without_law_filter": smallest_funding(16, True, parity=False),
               "S_nae": smallest_funding(13, False, parity=False, literal_lawful=nae_lawful),
               "S_nae_no_written_meeting": smallest_funding(16, True, parity=False, literal_lawful=nae_lawful),
               "C_binary": closing_lower_bound(2), "C_ternary": closing_lower_bound(3)}
    built = list(built_results())
    sampled = list(robustness_results())
    data = {"metadata": {"design_sha256": frozen, "setting_probability": [1, 4],
                         "accessible_region": "own input support and complete supports and ownership of its directly owned births",
                         "value_source": "uniform allowed preparation, optional zero under parity or fair under NAE, equal growth extensions",
                         "fresh_names": "reserved optional slots and child-local indices in measured records",
                         "cell_order": ["00", "01", "10", "11"]},
            "minimum": minimum, "built": built, "robustness": sampled}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "exact_tables.json.gz").write_bytes(gzip.compress(json.dumps(data, separators=(",", ":")).encode(), mtime=0))
    (OUT / "summary.json").write_text(json.dumps(summary(built, sampled, minimum), indent=2) + "\n")
    print(f"Completed all tables in {time.monotonic() - start:.3f} s", flush=True)


if __name__ == "__main__":
    main()
