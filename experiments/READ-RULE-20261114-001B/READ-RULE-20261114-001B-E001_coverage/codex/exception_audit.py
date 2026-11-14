"""Independent pair-projection audit of the nine reported Q1 counterexamples.

The selected Q states and residue groupings are read from the READ producer,
not independently reconstructed.  Their state identities are checked against
the original CARRY records.  Exact projections reuse CARRY project_state;
candidate enumeration and pair/exception tests below import no READ coverage
predicate.  This bounded audit does not search the full census for omissions.
"""
from __future__ import annotations

from itertools import permutations
import hashlib
import json
import os
from pathlib import Path
import resource
import sys
import time

sys.dont_write_bytecode = True
for _name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_name] = "1"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CARRY = ROOT / "experiments/CARRY-BOUND-20261114-001A/CARRY-BOUND-20261114-001A-E001_window/codex"
if str(CARRY) not in sys.path:
    sys.path.insert(0, str(CARRY))
import inputs
import window

SUMMARY = HERE / "summary.json"
INDEX = HERE / "source_index.json"
RUN_RESULTS = HERE / "census_run/results.jsonl"
OUTPUT = HERE / "exception_audit.json"


def independent_candidates(flat):
    candidates = set()
    for callee, args in flat["calls"]:
        if callee != "K" or len(args) != 3 or len(set(args)) != 3:
            continue
        for k, x, z in permutations(args):
            if 0 <= k < 3 and x >= 3:
                candidates.add((k, x, z))
    return candidates


def independent_pairs(projection, p, x, z):
    """Explicit ordered bit pairs, independently of the producer's encoding."""
    positions = {label: j for j, label in enumerate(projection["labels"])}
    rows = projection["allowed"]
    if not rows:
        raise ValueError("empty projection is not a live exception witness")

    def pair(left, right):
        return {(int(bool(row & (1 << positions[left]))),
                 int(bool(row & (1 << positions[right])))) for row in rows}

    px, zp, zx = pair(p, x), pair(z, p), pair(z, x)
    equal = {(0, 0), (1, 1)}
    opposite = {(0, 1), (1, 0)}
    full = equal | opposite
    if px not in (equal, opposite, full):
        raise ValueError("p,x projection violates the live complement-closed pair alternatives")
    if any({(1 - a, 1 - b) for a, b in values} != values for values in (px, zp, zx)):
        raise ValueError("pair projection is not complement closed")
    code = "free" if px == full else "equal" if px == equal else "opposite"
    zp_opposite, zx_opposite = zp == opposite, zx == opposite
    exception = px == full and (zp_opposite or zx_opposite)
    return dict(px=sorted(px), zp=sorted(zp), zx=sorted(zx), px_code=code,
                zp_opposite=zp_opposite, zx_opposite=zx_opposite, exception=exception)


def audit_family(selection, produced, original, source_location):
    key = selection["key"]
    prep = inputs.load_paths().Preparation(json.loads(key))
    flat = prep.flat(prep.S)
    expected = independent_candidates(flat)
    candidates = [tuple(c) for c in produced["candidates"]]
    if len(candidates) != len(set(candidates)) or set(candidates) != expected:
        raise ValueError("producer candidate roster differs from independent syntax enumeration")
    if not produced["in_scope"] or not prep.alive:
        raise ValueError("selected family is not both recorded in scope and living")
    if not produced["R"]["window_complete"] or not original["window"]["complete"]:
        raise ValueError("selected exception witness has an incomplete source window")
    original_states = {(int(row["J"], 16), tuple(row["partition"]))
                       for row in original["window"]["state_bonds"]}
    states = {row["id"]: row for row in produced["R"]["state_ties"]}
    if len(states) != len(produced["R"]["state_ties"]):
        raise ValueError("duplicate producer state ID")
    residues = {row["residue"]: row for row in produced["R"]["residues"]}
    body = window.body_allowed(prep, prep.S)
    projections, checks, selected_residues = {}, [], []
    for residue_id in selection["residues"]:
        residue = residues[residue_id]
        if residue["exception_only"] is not True:
            raise ValueError("summary selected a residue without definite exception-only status")
        if len(set(residue["state_ids"])) != len(residue["state_ids"]):
            raise ValueError("duplicate state ID within selected residue")
        checked = 0
        for state_id in residue["state_ids"]:
            state_row = states[state_id]
            q = int(state_row["J"], 16), tuple(state_row["partition"])
            if q not in original_states:
                raise ValueError("producer Q state not present in original CARRY state roster")
            eligible = {j for j, (k, _, _) in enumerate(candidates)
                        if 0 <= q[1][prep.k + k] < prep.k}
            entries = {entry[0]: entry for entry in state_row["ties"]}
            if len(entries) != len(state_row["ties"]) or set(entries) != eligible:
                raise ValueError("recorded tie entries omit or add an independently eligible candidate")
            if not eligible:
                continue
            if state_id not in projections:
                projections[state_id] = window.project_state(prep, q, body)
            projection = projections[state_id]
            for candidate_id in sorted(eligible):
                k, x_local, z_local = candidates[candidate_id]
                aliases = projection["end_aliases"]
                p, x, z = aliases[k], aliases[x_local], aliases[z_local]
                if p != q[1][prep.k + k] or p not in projection["root_labels"]:
                    raise ValueError("candidate p is not the carried root identity")
                if x_local < 3 or x not in projection["own_labels"] or x == p:
                    raise ValueError("candidate x is not a distinct own distinction")
                pairs = independent_pairs(projection, p, x, z)
                expected_entry = [candidate_id, p, pairs["px_code"],
                                  int(pairs["zp_opposite"]), int(pairs["zx_opposite"]),
                                  int(pairs["exception"])]
                agrees = entries[candidate_id] == expected_entry
                checks.append(dict(residue=residue_id, state_id=state_id,
                                   candidate=candidate_id, local=[k, x_local, z_local],
                                   aliases=[p, x, z], projected_rows=len(projection["allowed"]),
                                   producer_entry=entries[candidate_id],
                                   producer_agrees=agrees, **pairs))
                checked += 1
        if checked == 0:
            raise ValueError("selected residue has no eligible carried reading")
        selected_residues.append(dict(residue=residue_id,
                                     recorded_Q_residues=residue["Q_residues"],
                                     recorded_states=len(residue["state_ids"]),
                                     carried_candidate_checks=checked))
    passed = bool(checks) and all(c["exception"] and c["producer_agrees"] for c in checks)
    return dict(key=key, passed=passed, source_location=source_location,
                candidate_roster_independently_complete=True, candidates=len(candidates),
                projected_states=len(projections), checked_readings=len(checks),
                surviving_readings=sum(not c["exception"] for c in checks),
                producer_disagreements=sum(not c["producer_agrees"] for c in checks),
                residues=selected_residues, checks=checks)


def main():
    started = time.monotonic()
    summary_bytes, index_bytes = SUMMARY.read_bytes(), INDEX.read_bytes()
    summary, index = json.loads(summary_bytes), json.loads(index_bytes)
    selections = summary["Q1"]["exception_only_families"]
    selected = {row["key"]: row for row in selections}
    if len(selected) != 9 or len(selections) != 9:
        raise ValueError("this bounded assignment is frozen to exactly nine selected families")
    indexed = {row["key"]: row for row in index["rows"] if row["key"] in selected}
    if set(indexed) != set(selected):
        raise ValueError("selected family missing from original source offset index")
    source = ROOT / index["source"]
    stat = source.stat()
    if (stat.st_size, stat.st_mtime_ns) != (index["size"], index["mtime_ns"]):
        raise ValueError("original CARRY source changed since offset indexing")
    produced = {}
    with RUN_RESULTS.open() as stream:
        for line in stream:
            record = json.loads(line)
            if record["case"] in selected:
                if record["status"] != "ok":
                    raise ValueError("selected READ producer record is not ok")
                produced[record["case"]] = record["result"]
    if set(produced) != set(selected):
        raise ValueError("selected family missing from READ runner results")
    families = []
    with source.open("rb") as stream:
        for selection in selections:
            location = indexed[selection["key"]]
            stream.seek(location["offset"])
            raw_bytes = stream.read(location["bytes"])
            record = json.loads(raw_bytes)
            if record["case"] != selection["key"] or record["status"] != "ok":
                raise ValueError("original source record identity/status mismatch")
            provenance = dict(source=index["source"], offset=location["offset"],
                              bytes=location["bytes"], line_sha256=hashlib.sha256(raw_bytes).hexdigest())
            try:
                family = audit_family(selection, produced[selection["key"]], record["result"], provenance)
            except (ValueError, KeyError, IndexError, AssertionError) as exc:
                family = dict(key=selection["key"], passed=False,
                              error=f"{type(exc).__name__}: {exc}", source_location=provenance)
            families.append(family)
    stable = hashlib.sha256(SUMMARY.read_bytes()).digest() == hashlib.sha256(summary_bytes).digest()
    answer = dict(passed=stable and all(f["passed"] for f in families),
                  selected_families=len(families), families=families,
                  checked_readings=sum(f.get("checked_readings", 0) for f in families),
                  projected_states=sum(f.get("projected_states", 0) for f in families),
                  scope="Only the nine definite Q1 exception-only witnesses selected in summary.json.",
                  Q_states_independently_reconstructed=False,
                  Q_state_scope="Q states and residue groups are read from the producer; identities are checked against original CARRY records. Candidate enumeration and pair/exception tests are independently recomputed.",
                  source_summary_stable=stable,
                  summary_sha256=hashlib.sha256(summary_bytes).hexdigest(),
                  source_index_sha256=hashlib.sha256(index_bytes).hexdigest(),
                  declared_original_source_sha256=index["sha256"],
                  original_full_source_rehashed=False,
                  implementation_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  seconds=time.monotonic() - started,
                  process_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    OUTPUT.write_text(json.dumps(answer, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({k: answer[k] for k in ("passed", "selected_families", "checked_readings",
                                          "projected_states", "Q_states_independently_reconstructed",
                                          "source_summary_stable", "seconds", "process_peak_rss_kib")},
                     sort_keys=True))
    return 0 if answer["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
