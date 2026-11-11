#!/usr/bin/env python3
"""Independent finite oracle; imports neither learner nor producer.

Whole six-bit states and their one-flip components are enumerated directly.
Upper relations glue pairs of whole source states, rather than invoking the
consumer's table-composition operation. The only external mathematical checker
is the canonical knotlab CLI. This program writes no files.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import os
from pathlib import Path
import re
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CONTRACT = HERE / "contract.json"
DEFAULT_RESULT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "result.json"
NAMES = "abcxyz"
WORDS6 = tuple(itertools.product((0, 1), repeat=6))
TRIPLES = tuple(itertools.combinations(range(6), 3))
KEYS = tuple("".join(NAMES[i] for i in t) for t in TRIPLES)
ORIGINAL = ((0, 1, 2), (0, 4, 5), (3, 1, 5), (3, 4, 2))
EQUIVALENT = ((3, 4, 5), (3, 1, 2), (0, 4, 2), (0, 1, 5))
REMOVED = dict(zip(("abc", "ayz", "xbz", "xyc"), ORIGINAL))
PERMUTATION = (4, 2, 0, 5, 3, 1)
NEGATED = {1, 4}
PANELS = ("original", "equivalent", "remove_abc", "remove_ayz", "remove_xbz",
          "remove_xyc", "free", "disconnected", "recoded")


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def text(word):
    return "".join(map(str, word))


def mask(rows, arity):
    rows = set(rows)
    return "".join("1" if w in rows else "0"
                   for w in itertools.product((0, 1), repeat=arity))


def decode(word):
    original = [None] * 6
    for i, j in enumerate(PERMUTATION):
        original[j] = word[i] ^ (i in NEGATED)
    return tuple(original)


def legal(panel, word):
    if panel == "free":
        return True
    if panel == "disconnected":
        return word[0] == word[1]
    if panel == "recoded":
        word = decode(word)
    rules = EQUIVALENT if panel == "equivalent" else ORIGINAL
    if panel.startswith("remove_"):
        rules = tuple(t for t in rules if t != REMOVED[panel[7:]])
    return all(len({word[i] for i in t}) == 2 for t in rules)


def components(words):
    remaining, answer = set(words), []
    while remaining:
        seed = min(remaining)
        found, pending = {seed}, [seed]
        while pending:
            current = pending.pop()
            for i in range(6):
                neighbor = current[:i] + (1 - current[i],) + current[i + 1:]
                if neighbor in remaining and neighbor not in found:
                    found.add(neighbor)
                    pending.append(neighbor)
        remaining.difference_update(found)
        answer.append(frozenset(found))
    return answer


def projection(words, indices):
    return {tuple(w[i] for i in indices) for w in words}


def glued(words, indices, *, split=False, admit=None):
    """Use whole words in each copy, including source witnesses.

    Admitting a first-copy port tuple adds all whole words with that tuple;
    no producer or learned table is used to derive an intervention oracle.
    """
    first = set(words)
    if admit is not None:
        first.update(w for w in WORDS6 if tuple(w[i] for i in indices) == admit)
    a, b, c = indices
    return {(left[a], left[b], right[b], right[c])
            for left in first for right in words
            if split or left[c] == right[a]}


def expected_reading(words):
    lower = {key: mask(projection(words, t), 3) for key, t in zip(KEYS, TRIPLES)}
    upper = {key: mask(glued(words, t), 4) for key, t in zip(KEYS, TRIPLES)}
    xyz = (3, 4, 5)
    interventions = {
        "erased": "1" * 16,
        "split_hidden": mask(glued(words, xyz, split=True), 4),
        "admit_000_in_first": mask(glued(words, xyz, admit=(0, 0, 0)), 4),
        "admit_111_in_first": mask(glued(words, xyz, admit=(1, 1, 1)), 4),
    }
    return {"lower": lower, "upper": upper, "interventions_xyz": interventions}


def compare_reading(actual, expected, label):
    for section in ("lower", "upper", "interventions_xyz"):
        require(isinstance(actual.get(section), dict), f"{label}: missing {section}")
        require(set(actual[section]) == set(expected[section]), f"{label}: {section} keys")
        for key, wanted in expected[section].items():
            require(actual[section][key] == wanted,
                    f"{label}: {section}.{key}: {actual[section][key]} != {wanted}")


def reporter_analysis(words):
    """Classify functions of physical xyz; coordinate copies are not new bits."""
    result = {}
    inputs = (3, 4, 5)
    for index, name in enumerate(NAMES):
        fibers = {}
        for w in words:
            fibers.setdefault(tuple(w[i] for i in inputs), set()).add(w[index])
        if any(len(v) != 1 for v in fibers.values()):
            result[name] = "not_determined"
            continue
        values = {k: next(iter(v)) for k, v in fibers.items()}
        if len(set(values.values())) == 1:
            result[name] = "constant"
        elif any(all(v == (k[j] ^ sign) for k, v in values.items())
                 for j in range(3) for sign in (0, 1)):
            result[name] = "input_or_negated_input"
        else:
            result[name] = "new_nonconstant_function"
    return result


def independent_knot(bits):
    arity = (len(bits)).bit_length() - 1
    rows = [w for w, allowed in zip(itertools.product((0, 1), repeat=arity), bits)
            if allowed == "1"]
    k2 = all(len({w[:i] + w[i + 1:] for w in rows}) == 2 ** (arity - 1)
             for i in range(arity))
    return {"binding": len(rows) < 2 ** arity,
            "loss_on_erasure": k2, "coexistence": bool(rows),
            "is_knot": bool(rows) and len(rows) < 2 ** arity and k2}


def run_knotlab(cnf, names, witnesses=()):
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(ROOT / "tools")
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    command = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", cnf,
               "--loops", *names[:-1], "--contact", names[-1], "--json"]
    if witnesses:
        command.extend(("--witnesses", *witnesses))
    completed = subprocess.run(command, cwd=ROOT, env=environment,
                               text=True, capture_output=True, check=True, timeout=20)
    return json.loads(completed.stdout)


def canonical_mask_check(bits):
    names = "p q r s".split() if len(bits) == 16 else "x y z".split()
    clauses = [" ".join(("~" if value else "") + name
                        for name, value in zip(names, word))
               for word, allowed in zip(itertools.product((0, 1), repeat=len(names)), bits)
               if allowed == "0"]
    clauses.extend(f"{name} ~{name}" for name in names)
    report = run_knotlab("; ".join(clauses), names)
    wanted_rows = {text(w) for w, bit in
                   zip(itertools.product((0, 1), repeat=len(names)), bits) if bit == "1"}
    require(set(report["allowed"]) == wanted_rows, "knotlab changed the supplied relation")
    expected = independent_knot(bits)
    for key, value in expected.items():
        require(report[key] == value, f"knotlab K1-K3 mismatch for {bits}, {key}")
    return expected


def canonical_full_source_check(expected_upper):
    clauses, witnesses = [], ["h"]
    for tag, ports in (("L", ("p", "q", "h")), ("R", ("h", "r", "s"))):
        names = tuple(f"{name}{tag}" for name in "abc") + ports
        witnesses.extend(names[:3])
        for triple in ORIGINAL:
            clause = [names[i] for i in triple]
            clauses.extend((" ".join(clause), " ".join("~" + n for n in clause)))
    report = run_knotlab("; ".join(clauses), ("p", "q", "r", "s"), witnesses)
    actual = mask((tuple(map(int, w)) for w in report["allowed"]), 4)
    require(actual == expected_upper, "full original-source CLI projection differs")
    require(report["is_knot"], "full original-source CLI is not a knot")
    return {key: report[key] for key in independent_knot(expected_upper)}


def check(result, result_path):
    require(result.get("contract_sha256") == hashlib.sha256(CONTRACT.read_bytes()).hexdigest(),
            "result does not bind the current frozen contract")
    require(set(result["panels"]) == set(PANELS), "missing or extra panels")
    summary, maps, measured, total_runs = {}, {}, set(), 0
    for name in PANELS:
        panel = result["panels"][name]
        whole = frozenset(w for w in WORDS6 if legal(name, w))
        groups = components(whole)
        group_of = {w: group for group in groups for w in group}
        expected = {group: expected_reading(group) for group in groups}
        full_lower = expected_reading(whole)["lower"]
        runs = {run["start"]: run for run in panel["runs"]}
        require(len(runs) == len(panel["runs"]), f"{name}: duplicate starts")
        require(set(runs) == {text(w) for w in whole}, f"{name}: not every legal start")
        used, mismatches, covers = set(), set(), 0
        for start, run in runs.items():
            require(re.fullmatch(r"[01]{6}", start) is not None, f"{name}: invalid start")
            group = group_of[tuple(map(int, start))]
            require(run["reached"] == len(group), f"{name}/{start}: reached count")
            key = run["readings"]
            require(key in panel["readings"], f"{name}/{start}: absent reading")
            compare_reading(panel["readings"][key], expected[group], f"{name}/{start}")
            require(re.fullmatch(r"[0-9a-f]{64}", run["trace_sha256"]) is not None,
                    f"{name}/{start}: malformed trace digest")
            used.add(key)
            covers += group == whole
            mismatches.update(k for k in KEYS if expected[group]["lower"][k] != full_lower[k])
        require(used == set(panel["readings"]), f"{name}: unreferenced readings")
        measured.update(bits for reading in panel["readings"].values()
                        for bits in reading["upper"].values())
        measured.update(reading["lower"]["xyz"] for reading in panel["readings"].values())
        measured.update(bits for reading in panel["readings"].values()
                        for bits in reading["interventions_xyz"].values())
        summary[name] = {
            "legal_states": len(whole), "component_sizes": sorted(map(len, groups)),
            "runs": len(runs), "starts_covering_whole_base": covers,
            "component_whole_different_triples": sorted(mismatches),
            "restricted_triples_per_component": sorted(
                sum(bits != "1" * 8 for bits in reading["lower"].values())
                for reading in expected.values()),
            "xyz_upper_sizes": sorted({r["upper"]["xyz"].count("1")
                                       for r in expected.values()}),
            "physical_bits_given_xyz": reporter_analysis(whole),
            "component_physical_bits_given_xyz": [reporter_analysis(g) for g in groups],
        }
        maps[name] = runs
        total_runs += len(runs)

    require(maps["original"].keys() == maps["equivalent"].keys(), "matched start mismatch")
    for start, run in maps["original"].items():
        other = maps["equivalent"][start]
        require(run["trace_sha256"] == other["trace_sha256"],
                f"equivalent/{start}: observable trace changed")
        first = result["panels"]["original"]["readings"][run["readings"]]
        second = result["panels"]["equivalent"]["readings"][other["readings"]]
        require(first == second, f"equivalent/{start}: learned behavior changed")

    trajectory = result["first_trajectory"]
    seen, last_trial = set(), -1
    for entry in trajectory:
        word = tuple(map(int, entry["state"]))
        require(legal("original", word) and word not in seen, "invalid discovery snapshot")
        seen.add(word)
        require(entry["trial"] > last_trial, "discovery trial order")
        last_trial = entry["trial"]
        wanted = [sum(1 << int(text(row), 2) for row in projection(seen, t)) for t in TRIPLES]
        require(entry["learned_assignments_per_triple"] == wanted,
                "trajectory memory contains unseen or missing assignments")
    require(seen == {w for w in WORDS6 if legal("original", w)}, "first trajectory incomplete")

    original_words = frozenset(w for w in WORDS6 if legal("original", w))
    original_reading = expected_reading(original_words)
    recoded_words = frozenset(w for w in WORDS6 if legal("recoded", w))
    transported_xyz = {tuple(decode(w)[i] for i in (3, 4, 5)) for w in recoded_words}
    require(mask(transported_xyz, 3) == original_reading["lower"]["xyz"],
            "recoded source loses the transported original xyz relation")
    canonical = {bits: canonical_mask_check(bits) for bits in sorted(measured)}
    full_query = canonical_full_source_check(original_reading["upper"]["xyz"])

    # Meaningful wrong mathematical outputs must reject, without touching files.
    mutations = []
    sample = next(iter(result["panels"]["original"]["readings"].values()))
    for section, key, replacement in (("lower", "xyz", "1" * 8),
                                      ("upper", "xyz", "1" * 16),
                                      ("interventions_xyz", "split_hidden",
                                       original_reading["upper"]["xyz"])):
        wrong = copy.deepcopy(sample)
        wrong[section][key] = replacement
        try:
            compare_reading(wrong, original_reading, "intentional wrong-content control")
        except AssertionError:
            mutations.append(f"{section}.{key}")
        else:
            raise AssertionError("wrong-content control was accepted")
    return {
        "status": "PASS", "independence": "separate same-task whole-state implementation",
        "result_sha256": hashlib.sha256(result_path.read_bytes()).hexdigest(),
        "runs_checked": total_runs, "triple_readings_per_run": 20,
        "matched_original_equivalent_traces": len(maps["original"]),
        "discovery_memory_snapshots_checked": len(trajectory),
        "transported_original_xyz_in_recoded": mask(transported_xyz, 3),
        "original_xyz_lower": original_reading["lower"]["xyz"],
        "original_xyz_upper": original_reading["upper"]["xyz"],
        "original_xyz_interventions": original_reading["interventions_xyz"],
        "canonical_distinct_measured_relations": len(canonical),
        "canonical_full_source_query": full_query,
        "rejected_wrong_content_controls": mutations,
        "panels": summary,
        "limits": ["Trace digests are matched across equivalent presentations, not recomputed from full step traces.",
                   "No producer or learner imports; code privacy and general learnability are not proved.",
                   "Support relations are checked; sampling distributions and witness counts are distinct."],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result", nargs="?", type=Path, default=DEFAULT_RESULT)
    args = parser.parse_args()
    try:
        report = check(json.loads(args.result.read_text()), args.result)
    except (AssertionError, KeyError, TypeError, ValueError, OSError,
            subprocess.SubprocessError) as error:
        print(json.dumps({"status": "FAIL", "error": str(error)}, sort_keys=True))
        raise SystemExit(1)
    print(json.dumps(report, indent=2, sort_keys=True))
