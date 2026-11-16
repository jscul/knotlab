#!/usr/bin/env python3
"""Independent raw paired-response certificate audit (no producer imports)."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from functools import lru_cache
import gzip
import hashlib
import importlib.util
from itertools import combinations
import json
from math import comb
from pathlib import Path
from statistics import median


ROOT = Path(__file__).resolve().parents[2]
TICKET = "PAIR-PROOF-20261115-001"
DEFAULT = ROOT / "artifacts" / TICKET / (TICKET + "-E001_shared_witnesses")
OLD = ROOT / "artifacts/PARENT-FOLD-20261115-001/PARENT-FOLD-20261115-001-E001_consumer_edits/explicit-piece"
PARENT_AUDIT = ROOT / "research/PARENT-FOLD-20261115-001/audit.py"
PARENT_AUDIT_SHA256 = "4ca6901f79b85cb5dd1f8ebdb9a2d5a5b99416377f32aa7a4de52d8efd3dc90a"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def load(path):
    return json.loads(Path(path).read_bytes())


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@lru_cache(None)
def parent_oracle():
    require(digest(PARENT_AUDIT) == PARENT_AUDIT_SHA256, "terminal independent parent oracle changed")
    spec = importlib.util.spec_from_file_location("pair_proof_independent_parent_audit", PARENT_AUDIT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require(condition, message):
    if not condition:
        raise ValueError(message)


def response(truths, raw):
    require(len(truths) == 2, "exactly two output tables required")
    return ((int(truths[0]) >> raw) & 1) | (((int(truths[1]) >> raw) & 1) << 1)


def essential_inputs(n, truth):
    return tuple(i for i in range(n) if any(
        ((truth >> x) ^ (truth >> (x ^ (1 << i)))) & 1
        for x in range(1 << n) if not (x >> i) & 1))


def eligible_triples(n, truths):
    common = set(essential_inputs(n, truths[0])) & set(essential_inputs(n, truths[1]))
    return tuple(combinations(sorted(common), 3))


def face_rows(n, axes, outside):
    axes = tuple(axes)
    require(len(axes) == 2 and len(set(axes)) == 2 and all(0 <= i < n for i in axes),
            "two distinct in-range axes required")
    mask = sum(1 << i for i in axes)
    require(0 <= outside < 1 << n and outside & mask == 0, "outside has active face axes")
    return tuple(outside | ((corner & 1) << axes[0]) |
                 (((corner >> 1) & 1) << axes[1]) for corner in range(4))


def certificate(n, truths, rows, triple=None, claimed=None):
    """Check three literal original-input rows, never a supplied signature table."""
    rows = tuple(rows)
    require(len(rows) == len(set(rows)) == 3 and all(0 <= x < 1 << n for x in rows),
            "certificate needs three distinct in-range rows")
    values = tuple(response(truths, x) for x in rows)
    require(len(set(values)) == 3, "three distinct paired output responses required")
    if claimed is not None:
        require(tuple(claimed) == values, "stale or corrupted response values")
    varying = (rows[0] ^ rows[1]) | (rows[0] ^ rows[2])
    require(varying.bit_count() == 2, "not a two-axis certificate")
    if triple is not None:
        triple = tuple(triple)
        require(len(triple) == len(set(triple)) == 3, "triple shape")
        require(all(0 <= i < n for i in triple), "triple axis range")
        require(varying & ~sum(1 << i for i in triple) == 0,
                "certificate rows disagree outside claimed triple")
    covered = tuple(t for t in eligible_triples(n, truths)
                    if varying & ~sum(1 << i for i in t) == 0)
    return dict(rows=rows, responses=values, varying_axes=tuple(
        i for i in range(n) if varying >> i & 1), covered_triples=covered)


def classify_transition(n, before, after, axes, outside, original_rows):
    """Separate unchanged values, same three corners, and same four-corner face."""
    old = certificate(n, before, original_rows)
    four = face_rows(n, axes, outside)
    require(set(original_rows) <= set(four), "original proof not on stated face")
    new_values = tuple(response(after, x) for x in original_rows)
    alternatives = [rows for rows in combinations(four, 3)
                    if len({response(after, x) for x in rows}) == 3]
    return dict(original_values_unchanged=old["responses"] == new_values,
                unchanged_response_rows=sum(a == b for a, b in zip(old["responses"], new_values)),
                same_three_distinct=len(set(new_values)) == 3,
                same_four_has_certificate=bool(alternatives),
                selected_after_rows=alternatives[0] if alternatives else None)


def enumerate_faces(n, truths):
    """Literal scalar queries on every two-axis face, sorted independently."""
    result = {}
    for a, b in combinations(range(n), 2):
        observations = []
        for base in range(1 << n):
            if base & ((1 << a) | (1 << b)):
                continue
            values = tuple(response(truths, row) for row in face_rows(n, (a, b), base))
            masks = [sum(1 << c for c in corners) for corners in combinations(range(4), 3)
                     if len({values[c] for c in corners}) == 3]
            if masks:
                observations.append((base, tuple(masks)))
        if observations:
            result[a, b] = observations
    return result


def groups_covered(triples, pairs):
    return {k for k, group in enumerate(triples) if any(set(pair) <= set(group) for pair in pairs)}


def check_request(n, truths, request):
    require(isinstance(request, (list, tuple)) and len(request) in (3, 4) and
            all(type(v) is int for v in request), "request shape")
    a, b, base = request[:3]
    require(a < b, "request axes are not increasing")
    four = face_rows(n, (a, b), base)
    mask = request[3] if len(request) == 4 else 15
    require(mask in (7, 11, 13, 14, 15), "three or four selected corners required")
    selected = tuple(row for c, row in enumerate(four) if mask >> c & 1)
    values = tuple(response(truths, row) for row in selected)
    return selected, values, len(set(values)) >= 3


def coverage_audit(directory, cases, evidence):
    archived = load(directory / "coverage.json")
    totals = {kind: Counter() for kind in ("surviving", "broken")}
    retention = {kind: Counter() for kind in ("surviving", "broken")}
    tasks = {}
    for case in cases:
        pid = case["id"]
        m = len(case["frontier"])
        triples = tuple(combinations(range(m), 3))
        before = evidence[pid]["snapshots"][None]["targets"]
        original = enumerate_faces(m, before)
        expected_original = []
        for (a, b), options in original.items():
            base, masks = options[0]
            mask = masks[0]
            expected_original.append(dict(test=[a, b, base], corners=[c for c in range(4) if mask >> c & 1]))
        require(archived["original_witnesses"][pid] == expected_original, "original first-witness order")
        for edit in case["edits"]:
            eid = edit["id"]
            current = evidence[pid]["snapshots"][eid]["targets"]
            record = archived["tasks"][pid][eid]
            eligible = eligible_triples(m, current)
            require(eligible == triples and record["eligible"] == list(range(len(triples))), "eligible triple universe")
            fresh = enumerate_faces(m, current)
            by_pair = {tuple(row["test"][:2]): row for row in record["available"]}
            require(set(by_pair) == set(fresh), "available witness pairs")
            for pair, options in fresh.items():
                row = by_pair[pair]
                require(row["test"] == [*pair, options[0][0]], "first fresh outside setting")
                require(row["bases"] == [x[0] for x in options] and row["corner_masks"] == [list(x[1]) for x in options],
                        "complete fresh face/corner enumeration")
                require(row["witness_count"] == len(options), "witness setting count")
                require(row["covers"] == sorted(groups_covered(triples, [pair])), "pair triple coverage")
            coverable = groups_covered(triples, fresh)
            require(record["coverable"] == sorted(coverable), "fresh union coverage")
            missing = set(combinations(range(m), 2)) - set(fresh)
            require(record["unusable_pairs"] == [list(p) for p in sorted(missing)], "unusable pairs")
            same_three, same_four, unchanged = set(), set(), set()
            for pair, options in original.items():
                base, masks = options[0]
                four = face_rows(m, pair, base)
                rows = tuple(row for c, row in enumerate(four) if masks[0] >> c & 1)
                change = classify_transition(m, before, current, pair, base, rows)
                if change["same_three_distinct"]:
                    same_three.add(pair)
                if change["same_four_has_certificate"]:
                    same_four.add(pair)
                if change["original_values_unchanged"]:
                    unchanged.add(pair)
                retention[record["kind"]].update(original_pairs=1,
                    original_values_unchanged=int(change["original_values_unchanged"]),
                    unchanged_response_rows=change["unchanged_response_rows"],
                    same_three_distinct=int(change["same_three_distinct"]),
                    same_four_has_certificate=int(change["same_four_has_certificate"]))
            for name, pairs in (("same_three", same_three), ("any_three_of_four", same_four)):
                saved = record["original_rechecked"][name]
                require(saved["pairs"] == [list(p) for p in sorted(pairs)] and
                        saved["covered"] == sorted(groups_covered(triples, pairs)), "historical witness retention " + name)
            ranks = dict(evidence[pid]["snapshots"][eid]["facts"]["ranks"])
            for k in coverable:
                require(ranks[triples[k]] >= 3, "witness rejects a genuine one-bit cut")
            uncovered = [dict(index=k, triple=list(group), exact_classes=ranks[group])
                         for k, group in enumerate(triples) if k not in coverable]
            require(record["uncovered"] == uncovered, "uncovered exact fallback cases")
            forced = len(triples) - len(coverable)
            require(forced in (0, 1), "panel outside elementary full-cover bound")
            max_untested = m*m//4 if not forced else 3+(m-3)+(m-3)**2//4
            lower = comb(m, 2) - max_untested
            require(record["min_full"] == record["independent_full_lower_bound"] == lower,
                    "independent full-cover bound")
            for k, frontier in enumerate(record["frontier"]):
                pairs = []
                require(frontier["k"] == k and len(frontier["tests"]) == k, "frontier request count")
                for request in frontier["tests"]:
                    _, _, valid = check_request(m, current, request)
                    require(valid, "frontier certificate invalid on current raw-derived target")
                    pairs.append(tuple(request[:2]))
                require(len(set(pairs)) == k and frontier["covered"] == len(groups_covered(triples, pairs)),
                        "frontier coverage attainment")
            require(record["frontier"][-1]["covered"] == len(coverable) and len(record["frontier"])-1 == lower,
                    "full-cover endpoint")
            totals[record["kind"]].update(edits=1, eligible=len(triples), fresh=len(coverable),
                same_three=len(groups_covered(triples, same_three)),
                any_three_of_four=len(groups_covered(triples, same_four)), minimum_full_tests=lower)
            tasks[pid, eid] = dict(n=m, targets=current, triples=triples, fresh=fresh, covered=coverable,
                                  record=record, original=original, unchanged_pairs=unchanged)
    require({k: dict(v) for k, v in totals.items()} == archived["totals"], "coverage totals")
    return tasks, dict(coverage_sha256=digest(directory / "coverage.json"), totals={k:dict(v) for k,v in totals.items()},
                      retention={k:dict(v) for k,v in retention.items()}, full_cover_minima_independently_proved=True,
                      intermediate_frontier_attainments_checked=True,
                      intermediate_frontier_optimality="pending independent integer optimization")


def proof_receipt(case, snapshot, answer):
    """Recompute current proof values from original raw inputs, with fresh per-return cache."""
    n, m = case["n"], len(case["frontier"])
    proofs = answer.get("pair_proofs", ())
    if not isinstance(proofs, (tuple, list)):
        return dict(pair_proof_schema_failures=1), set(), set()
    counts = Counter(pair_proofs_supplied=len(proofs))
    pairs, seen, cache = set(), set(), {}
    targets = tuple(snapshot["raw"][w] for w in case["outputs"])
    # Find an actual raw assignment for each complete stage assignment.
    original_raw = parent_oracle().raw_words(case)
    mapping, _ = parent_oracle().frontier_domain(case, original_raw)
    witnesses = {}
    for raw, stage in enumerate(mapping):
        witnesses.setdefault(stage, raw)
    for request in proofs:
        try:
            rows, _, valid = check_request(m, snapshot["targets"], request)
        except (ValueError, TypeError):
            counts["pair_proof_schema_failures"] += 1
            continue
        key = (*request[:3], request[3] if len(request) == 4 else 15)
        if key in seen:
            counts["pair_proof_duplicate_certificates"] += 1
            continue
        seen.add(key)
        counts["pair_proof_unique_certificates_checked"] += 1
        values = []
        for stage in rows:
            counts["pair_proof_row_requests"] += 1
            if stage in cache:
                counts["pair_proof_row_cache_hits"] += 1
            else:
                cache[stage] = response(targets, witnesses[stage])
                require(cache[stage] == response(snapshot["targets"], stage), "raw/stage proof response mismatch")
                counts["pair_proof_raw_rows_read"] += 1
                counts["pair_proof_output_bits_read"] += 2
            values.append(cache[stage])
        require(valid == (len(set(values)) >= 3), "raw backing changes proof validity")
        counts["pair_proof_certificate_row_requests"] += len(rows)
        counts["pair_proof_successes" if valid else "pair_proof_current_data_failures"] += 1
        if valid:
            pairs.add(tuple(request[:2]))
    triples = eligible_triples(m, snapshot["targets"])
    covered = {triples[k] for k in groups_covered(triples, pairs)}
    chosen = tuple(sorted(answer["triple"]))
    require(chosen not in covered if answer["width"] == 1 else True,
            "certificate excludes a verified one-bit winner")
    counts["pair_proof_certified_axis_pairs"] = len(pairs)
    counts["pair_proof_distinct_rows"] = len(cache)
    return dict(counts), covered, set(cache)


def checker_counts(case, evidence, eid, answer, check, exact, raw_values, proof_counts, covered):
    """Validate semantic counters without using producing verification code."""
    p = parent_oracle()
    n, m, prefix = case["n"], len(case["frontier"]), case["upstream_count"]
    gates = len(answer["circuit"]["gates"])
    omitted = len(covered - {tuple(sorted(answer["triple"]))}) if answer["width"] == 2 else 0
    alternatives = exact["alternatives_checked"]
    expected = dict(exact=True, width=exact["width"], classes=exact["classes"],
        minimum_universe="jointly-essential stage-frontier triples", structural_locality=True,
        raw_assignments=1<<n, stage_assignments=1<<m, raw_outputs=2,
        raw_gates_returned=len(answer["physical"]["gates"]), stage_gates_returned=gates,
        active_stage_gates=exact["active_gates"], shared_stage_gates=exact["shared_gates"],
        shared_summary_wires=exact["shared_summary_wires"], raw_return_replay="history",
        source_sha256=hashlib.sha256(canonical(case)).hexdigest(),
        verification_calls=1, physical_prefix_gates_compared=prefix,
        physical_stage_gates_linked=gates, returned_stage_NAND_evaluations=gates,
        returned_stage_output_bits_compared=2<<m,
        global_minimum_alternative_groups_checked=alternatives-omitted,
        raw_return_prefix_NANDs_reused=prefix, raw_return_output_bits_compared=2<<n,
        stage_support_axis_tests=2*m, stage_class_calls=1+alternatives-omitted,
        original_verification_cache_hits=0)
    cone = evidence["snapshots"][eid]["cone_stage"]
    for tag in ("raw_source", "source_stage"):
        expected.update({tag+"_gates_examined":cone["examined"], tag+"_NAND_evaluations":cone["recomputed"],
            tag+("_unchanged_NANDs_reused" if tag=="raw_source" else "_NANDs_reused"):cone["reused"],
            tag+"_changed_values":cone["changed"], tag+"_recomputed_unchanged_values":cone["recomputed_unchanged"]})
    expected.update(raw_source_prefix_NANDs_reused=prefix,
        raw_source_NAND_row_equivalents=cone["recomputed"]*(1<<n),
        raw_stage_projection_tests=2<<m, raw_stage_output_bits_covered=2<<n)
    ids = p._source_fingerprints(case)
    history = {key:evidence["before_raw"][wire] for wire,key in enumerate(ids) if wire>=n+2}
    actual_ids = p.oracle().circuit_shape(answer["physical"],n)[3]
    historical_hits, new = 0, set()
    for wire in range(n+2+prefix,len(actual_ids)):
        key = actual_ids[wire]
        if key in history:
            require(raw_values[wire] == history[key], "stale original-expression value")
            historical_hits += 1
        else:
            new.add(key)
    expected.update(raw_return_history_expression_lookups=gates,
        raw_return_new_expression_identities=len(new), raw_return_history_expression_hits=historical_hits,
        raw_return_history_expression_misses=gates-historical_hits,
        raw_return_NANDs_reused=prefix+historical_hits, raw_return_NAND_evaluations=gates-historical_hits,
        raw_return_NAND_row_equivalents=(gates-historical_hits)*(1<<n))
    for key,value in expected.items():
        require(check.get(key,0) == value, "checker count/assertion "+key)
    if "pair_no_proof_fast_path" in check:
        expected_proofs = proof_counts if answer["width"]==2 else {
            "pair_proofs_supplied":len(answer.get("pair_proofs",())),
            "pair_proof_certified_axis_pairs":0, "pair_proof_distinct_rows":0}
        for key,value in expected_proofs.items():
            require(check.get(key,0) == value, "proof count "+key)
        require(check.get("alternative_exact_checks_avoided",0) == omitted, "certificate avoided checks exclude winner")
        require(check.get("alternative_exact_checks_actual",0) == alternatives-omitted, "exact fallback count")
        require(check.get("chosen_group_exact_checks",0) == 1, "winner is checked exactly")
        require(check.get("alternative_groups_considered",0) == alternatives, "all alternatives discharged")
        require(check.get("global_minimum_alternative_groups_certified",0) == alternatives,
                "global certificate obligations")
        if "minimum_phase_cpu_ns" in check:
            require(check["verification_remainder_cpu_ns"] == check["verification_cpu_ns"]-check["minimum_phase_cpu_ns"],
                    "optimistic floor subtraction")
            require(check.get("optimistic_no_minimum_is_certified") is False, "free omitted verification called certified")
    return omitted


def original_acquisition(case, original, row, required):
    if not required:
        require(row["acquisition"]=={} and row["original_check"]=={},"unrequested old discovery")
        return
    m=len(case["frontier"]);npairs=comb(m,2);nproofs=len(original)
    observed=set();selected=set()
    for pair, options in original.items():
        base,masks=options[0];rows=face_rows(m,pair,base)
        observed.update(rows)
        selected.update(r for c,r in enumerate(rows) if masks[0]>>c&1)
    expected=dict(old_acquisition_pairs=npairs,packed_contexts_built=1,packed_table_vectors_read=2,
        packed_zero_masks_built=m,packed_pair_queries=npairs,packed_outside_settings=npairs*(1<<(m-2)),
        packed_corner_equivalents=npairs*(1<<m),packed_pair_hits=nproofs,packed_pair_misses=npairs-nproofs,
        face_tests=nproofs,face_successes=nproofs,face_failures=0,query_row_requests=4*nproofs,
        query_unique_rows=len(observed),query_output_bit_reads=2*len(observed),
        query_reused_rows=4*nproofs-len(observed),old_acquisition_hits=nproofs,
        old_acquisition_misses=npairs-nproofs,old_acquisition_saved_proofs=nproofs,old_acquisition_face_entries=npairs)
    for key,value in expected.items():
        require(row["acquisition"].get(key,0)==value,"old discovery counter "+key)
    checked=dict(history_verification_calls=1,pair_proofs_supplied=nproofs,
        pair_proof_unique_certificates_checked=nproofs,pair_proof_successes=nproofs,
        pair_proof_row_requests=3*nproofs,pair_proof_certificate_row_requests=3*nproofs,
        pair_proof_raw_rows_read=len(selected),pair_proof_output_bits_read=2*len(selected),
        pair_proof_row_cache_hits=3*nproofs-len(selected),pair_proof_current_data_failures=0,
        pair_proof_schema_failures=0,pair_proof_certified_axis_pairs=nproofs,
        pair_proof_distinct_rows=len(selected),global_minimum_queries=0,
        exact_history=True,history_scope="this parent original output pair",
        source_sha256=hashlib.sha256(canonical(case)).hexdigest())
    for key,value in checked.items():
        require(row["original_check"].get(key,0)==value,"paid original proof checking "+key)
    require(row["acquisition"]["acquisition_cpu_ns"]<=row["phases"]["acquire"] and
            row["original_check"]["history_verification_cpu_ns"]<=row["phases"]["original_proof_verify"],
            "old discovery/validation clock")


def integer_frontier(m, missing, expected):
    """Independent edge/covered-triple binary optimization, not graph-orbit enumeration."""
    import numpy as np
    from scipy.optimize import Bounds, LinearConstraint, milp
    pairs = [p for p in combinations(range(m), 2) if p not in missing]
    triples = list(combinations(range(m), 3))
    size = len(pairs) + len(triples)
    a = np.zeros((len(triples)+1, size))
    a[0,:len(pairs)] = 1
    for j, group in enumerate(triples):
        a[j+1,len(pairs)+j] = 1
        for k, pair in enumerate(pairs):
            if set(pair) <= set(group):
                a[j+1,k] = -1
    objective = np.array([0.]*len(pairs)+[-1.]*len(triples))
    results = []
    for k, value in enumerate(expected):
        # Endpoints have elementary independently checked proofs. A simple
        # union bound suffices for small budgets when attained exactly.
        upper = min(len(triples), k*(m-2))
        if k in (0,len(expected)-1) or value == upper:
            results.append(dict(k=k,covered=value,proof="elementary endpoint/union bound"))
            continue
        lower = np.array([float(k)]+[-np.inf]*len(triples))
        bound = np.array([float(k)]+[0.]*len(triples))
        solved = milp(objective, integrality=np.ones(size), bounds=Bounds(0,1),
                      constraints=LinearConstraint(a,lower,bound),
                      options={"mip_rel_gap":0,"node_limit":100000})
        if solved.status != 0:
            results.append(dict(k=k,covered=value,proof="not independently optimized",solver_status=int(solved.status)))
            continue
        got = round(-float(solved.fun))
        require(abs(float(solved.fun)+got)<1e-5 and got == value,"frontier integer optimum mismatch")
        selected = [p for j,p in enumerate(pairs) if solved.x[j]>.5]
        require(len(selected)==k and len(groups_covered(triples,selected))==got,"integer optimum witness")
        results.append(dict(k=k,covered=got,proof="independent binary MILP optimum"))
    return results


def check_bindings(directory):
    design = load(directory/"design.json")
    require(set(design.get("arms",{})),"missing bound strategies")
    for category in ("sources","data"):
        for name, expected in design[category].items():
            require(digest(ROOT/name)==expected,"changed bound "+category+": "+name)
    return design


def timing_report(directory, design, rows_by_case):
    samples, counts, first, per_edit = defaultdict(dict), defaultdict(Counter), {}, []
    stream_hashes = {}
    for key, (envelope, rows) in rows_by_case.items():
        panel,arm,block = (envelope[k] for k in ("panel","arm","block"))
        fields = Counter(total=envelope["cpu_ns"],startup=envelope["startup_ns"],wall=envelope["wall_ns"])
        for row in rows:
            for name,value in row["phases"].items():
                fields[name] += value
            for query in row["edits"]:
                for name,value in query["phases"].items():
                    fields["edits."+name] += value
                fields["edit_cpu"] += query["cpu_ns"]
                per_edit.append(dict(panel=panel,block=block,parent=row["id"],edit=query["id"],arm=arm,cpu_ns=query["cpu_ns"]))
        samples[panel,arm][block]=dict(fields)
        stream_hashes[envelope["file"]]=envelope["sha256"]
        if (panel,arm) not in first or block < first[panel,arm]:
            first[panel,arm]=block
    report={}
    for panel in sorted({p for p,_ in samples}):
        methods = {}
        for p,arm in samples:
            if p!=panel:
                continue
            data=samples[p,arm]; blocks=sorted(data)
            first_block=8 if directory.name=="timing-selection" else 0
            require(blocks==list(range(first_block,first_block+8)),"paired eight-block matrix")
            keys=set().union(*(v.keys() for v in data.values()))
            methods[arm]=dict(blocks=blocks,totals_ns=[data[b]["total"] for b in blocks],
                             median_ms={k:median(data[b].get(k,0) for b in blocks)/1e6 for k in keys})
        require(set(methods)==set(design["arms"]),"strategy matrix incomplete")
        deterministic=[a for a in methods if "advice" not in design["arms"][a]]
        best=min(deterministic,key=lambda a:methods[a]["median_ms"]["total"])
        advice=[a for a in methods if a not in deterministic]
        for arm, data in methods.items():
            delta=[(samples[panel,best][b]["total"]-samples[panel,arm][b]["total"])/1e6 for b in data["blocks"]]
            data.update(paired_wins=sum(v>0 for v in delta),paired_savings_ms=delta,
                        median_paired_saving_ms=median(delta),
                        whole_median_saving_ms=methods[best]["median_ms"]["total"]-data["median_ms"]["total"])
        report[panel]=dict(arms=methods,fastest_deterministic=best,
            fastest_advice=min(advice,key=lambda a:methods[a]["median_ms"]["total"]) if advice else None,
            signal_arms=[a for a in advice if methods[a]["paired_wins"]>=7 and methods[a]["median_paired_saving_ms"]>0])
    timing=directory/"timing.json"
    if timing.is_file():
        supplied=load(timing)
        require(supplied["failures"]==[],"assessor failures")
        for panel,part in report.items():
            got=supplied["panels"][panel]
            require(got["fastest_deterministic"]==part["fastest_deterministic"] and
                    got["fastest_advice"]==part["fastest_advice"],"benchmark selection")
            for arm,data in part["arms"].items():
                for key in ("blocks","totals_ns","paired_wins","paired_savings_ms","median_paired_saving_ms","whole_median_saving_ms"):
                    require(got["arms"][arm][key]==data[key],"timing arithmetic "+key)
                for phase,value in data["median_ms"].items():
                    require(got["arms"][arm]["median_ms"][phase]==value,"timing median "+phase)
    if (directory/"edit-times.json").is_file():
        require(load(directory/"edit-times.json")==per_edit,"per-edit timing ledger")
    return report,stream_hashes


@lru_cache(None)
def public_evidence():
    p=parent_oracle()
    cases=load(OLD/"public.json");grades=load(OLD/"grades.json");hints=load(OLD/"hints.json")
    require(len(cases)==36 and len({c["id"] for c in cases})==36,"saved parent panel size")
    evidence={c["id"]:p.inspect_parent(c,grades[c["id"]],hints[c["id"]]) for c in cases}
    return cases,grades,hints,evidence


@lru_cache(None)
def checked_coverage():
    cases,_,_,evidence=public_evidence()
    return coverage_audit(DEFAULT,cases,evidence)


_PHYSICAL_CACHE={}
_PROOF_CACHE={}
_CHECKER_CACHE={}


def audit_all(directory, milp_check=False):
    require(directory.resolve() in (DEFAULT.resolve(),(DEFAULT/"timing-selection").resolve()),"unexpected study directory")
    p=parent_oracle()
    audit_cpu=p.pin_away_from_timing()
    design=check_bindings(directory)
    first_block=8 if directory.name=="timing-selection" else 0
    cases,grades,hints,evidence=public_evidence()
    task_info,coverage=checked_coverage()
    if milp_check:
        patterns={}
        for info in task_info.values():
            record=info["record"];m=info["n"]
            # The declared forced shapes are disjoint complete components,
            # so degree/component signatures are a complete isomorphism key.
            missing={tuple(x) for x in record["unusable_pairs"]}
            adjacency={i:set() for i in range(m)}
            for a,b in missing:
                adjacency[a].add(b);adjacency[b].add(a)
            unseen=set(range(m));components=[]
            while unseen:
                todo=[min(unseen)];component=set()
                while todo:
                    v=todo.pop()
                    if v in component:continue
                    component.add(v);todo.extend(adjacency[v]-component)
                unseen-=component
                require(all(adjacency[v]==component-{v} for v in component),"forced graph outside clique-component symmetry")
                components.append(len(component))
            shape=tuple(sorted(components))
            key=(m,shape)
            expected=[x["covered"] for x in record["frontier"]]
            if key not in patterns:
                patterns[key]=integer_frontier(m,missing,expected)
            else:
                require([x["covered"] for x in patterns[key]]==expected,"isomorphic frontier disagrees")
        coverage["independent_frontier_optimization"]={str(k):v for k,v in patterns.items()}
        coverage["intermediate_frontier_optimality"]=all(all(x["proof"]!="not independently optimized" for x in v) for v in patterns.values())
    rows_by_case={}
    actual_cases={c["id"]:c for c in cases}
    physical_cache=_PHYSICAL_CACHE;proof_cache=_PROOF_CACHE;checker_cache=_CHECKER_CACHE
    counters=Counter();work_totals=defaultdict(Counter);query_answers={}
    manifest=directory/"results.jsonl"
    envelopes=[json.loads(line) for line in manifest.read_bytes().splitlines()]
    for outer in envelopes:
        require(outer["status"]=="ok" and outer["case"] not in rows_by_case,"failed/duplicate measured stream")
        envelope=outer["result"]
        panel,block,arm=(envelope[k] for k in ("panel","block","arm"))
        require(panel in ("broken","mixed") and arm in design["arms"] and block in range(first_block,first_block+8),"stream identity")
        path=directory/envelope["file"]
        require(digest(path)==envelope["sha256"],"changed measured trace")
        with gzip.open(path,"rt") as handle:
            rows=[json.loads(line) for line in handle]
        require(len(rows)==envelope["parents"]==36 and envelope["failures"]==0,"parent receipt completeness")
        require([r["id"] for r in rows]==[c["id"] for c in (cases if block%2==0 else cases[::-1])],"parent order")
        expected_queries={(c["id"],e["id"]) for c in cases for e in c["edits"]
                          if panel=="mixed" or grades[c["id"]]["edits"][e["id"]]["kind"]=="broken"}
        observed=set()
        for row in rows:
            pid=row["id"];case=actual_cases[pid];ev=evidence[pid]
            require(row["failure"] is None,"parent failure")
            require(all(type(v)is int and v>=0 for v in row["phases"].values()),"parent phase clock")
            require(sum(row["phases"].values())+sum(q["cpu_ns"] for q in row["edits"])<=row["cpu_ns"],"parent clock containment")
            one_task=next(info for (task_pid,_),info in task_info.items() if task_pid==pid)
            original_acquisition(case,one_task["original"],row,design["arms"][arm].get("history",False))
            for q in row["edits"]:
                eid=q["id"];snapshot=ev["snapshots"][eid]
                require((pid,eid) not in observed and (pid,eid) in expected_queries,"duplicate/unexpected edit")
                observed.add((pid,eid));require(q["failure"] is None and q["answer"],"edited return failure")
                require(sum(q["phases"].values())<=q["cpu_ns"] and all(type(v)is int and v>=0 for v in q["phases"].values()),"query clock containment")
                answer=q["answer"];p.check_lift(case,answer)
                key=(pid,eid,canonical({k:v for k,v in answer.items() if k!="pair_proofs"}))
                if key not in physical_cache:
                    info,_=p.oracle().verify_result(len(case["frontier"]),snapshot["targets"],answer)
                    raw=p.physical_words(answer["physical"])
                    require(tuple(raw[w] for w in answer["physical"]["outputs"])==tuple(snapshot["raw"][w] for w in case["outputs"]),"actual raw physical outputs")
                    physical_cache[key]=(info,raw)
                    counters["executed_unique_stage_programs"]+=1
                    counters["executed_stage_rows"]+=1<<len(case["frontier"])
                    counters["executed_raw_rows"]+=1<<case["n"]
                exact,raw=physical_cache[key]
                proof_key=(pid,eid,canonical(answer.get("pair_proofs",())))
                if proof_key not in proof_cache:
                    proof_cache[proof_key]=proof_receipt(case,snapshot,answer)
                proof_counts,covered,_=proof_cache[proof_key]
                ledger_key=(key,proof_key,arm)
                if ledger_key not in checker_cache:
                    omitted=checker_counts(case,ev,eid,answer,q["check"],exact,raw,proof_counts,covered)
                    stable={k:v for k,v in q["check"].items()
                            if not k.endswith("_ns") and "layout" not in k and "geometry" not in k}
                    checker_cache[ledger_key]=(omitted,stable)
                else:
                    omitted,stable=checker_cache[ledger_key]
                    require({k:v for k,v in q["check"].items() if not k.endswith("_ns") and "layout" not in k and "geometry" not in k}==stable,
                            "repeated semantic checker counter changed")
                require(q["check"]["verification_cpu_ns"]<=q["phases"]["verify"],"paid checker clock")
                work=q["work"]
                require(work.get("proofs_returned",0)==len(answer.get("pair_proofs",())),"returned proof count")
                require(work.get("face_tests",0)==work.get("face_successes",0)+work.get("face_failures",0),"successful and failed face accounting")
                require(work.get("query_row_requests",0)==work.get("query_unique_rows",0)+work.get("query_reused_rows",0),"solver row sharing accounting")
                require(work.get("query_output_bit_reads",0)==2*work.get("query_unique_rows",0),"solver queried output bits")
                if design["arms"][arm]["mode"] not in ("ordinary","compact"):
                    require(work.get("proof_avoided_exact_groups",0)==omitted,"solver certified alternatives exclude winner")
                    require(work.get("compact_exact_alternatives",0)==exact["alternatives_checked"]-omitted,"solver exact fallback count")
                    require(work.get("proofs_discovered",0)==work.get("face_successes",0),"successful discovery count")
                    require(work.get("proofs_discovered",0)-work.get("proofs_returned",0)==work.get("proofs_unused_or_discarded",0),"unused successful proof accounting")
                require(q.get("bytes",len(canonical(answer)))==len(canonical(answer)),"physical return byte count")
                counters["verified_edited_returns"]+=1
                counters["covered_raw_assignments"]+=1<<case["n"]
                counters["covered_raw_output_bits"]+=2<<case["n"]
                if block==first_block:
                    kind=grades[pid]["edits"][eid]["kind"]
                    work_totals[panel,arm,kind].update({k:v for k,v in q["work"].items() if type(v)is int})
                    work_totals[panel,arm,kind+".checker"].update({k:v for k,v in q["check"].items() if type(v)is int})
                    query_answers[panel,arm,pid,eid]=hashlib.sha256(canonical(answer)).hexdigest()
        require(observed==expected_queries and len(observed)==envelope["edits"],"complete edit stream")
        require(envelope["startup_ns"]+sum(r["cpu_ns"] for r in rows)<=envelope["cpu_ns"],"whole process CPU containment")
        rows_by_case[outer["case"]]=(envelope,rows)
    require(len(rows_by_case)==2*8*len(design["arms"]),"complete paid matrix")
    timing,streams=timing_report(directory,design,rows_by_case)
    return dict(schema_version=1,ticket=TICKET,verdict="PASS",auditor_sha256=digest(Path(__file__)),
        terminal_parent_auditor_sha256=PARENT_AUDIT_SHA256,audit_cpu=audit_cpu,
        design_sha256=digest(directory/"design.json"),manifest_sha256=digest(manifest),streams=streams,
        self_test=self_test(),coverage=coverage,physical_and_receipts=dict(counters),timing=timing,
        first_block_counts={str(k):dict(v) for k,v in work_totals.items()},
        independence="No producer or checker imports; literal face queries, actual raw/stage NAND outputs, exact residual minimum and physical cut replay use a pinned terminal independent oracle.",
        factoring="Only byte-identical programs/proofs bound to identical current raw targets reuse an earlier independent execution.",
        nonclaims=["Saved 36-parent diagnostic panel, not fresh held evidence for a fitted policy.",
                   "An ideal cover optimizes pair count/coverage, not end-to-end CPU.",
                   "Minimum universe is jointly-essential stage-frontier triples.",
                   "Removing all measured minimum-check CPU is an uncertified optimistic cost floor.",
                   "Original values unchanged, same three corners distinct, and same four-corner setting reusable are separate quantities."])


def audit_timing_selection(primary, secondary):
    directory=DEFAULT/"timing-selection"
    initial_design=load(DEFAULT/"design.json")
    extra_design=load(directory/"design.json")
    plans=load(DEFAULT/"plans.json");extra_plans=load(directory/"plans.json")
    rows=load(DEFAULT/"edit-times.json")
    choices={};choice_histogram=defaultdict(Counter)
    allowed=[a for a,s in initial_design["arms"].items() if "advice" in s and not s.get("history")]
    _,grades,_,_=public_evidence()
    for panel in ("mixed","broken"):
        times=defaultdict(dict)
        for row in rows:
            if row["panel"]==panel and row["arm"] in allowed:
                times[row["parent"],row["edit"]].setdefault(row["arm"],{})[row["block"]]=row["cpu_ns"]
        for (pid,eid),methods in times.items():
            require(set(methods)==set(allowed),"timing selector menu completeness")
            require(all(sorted(v)==list(range(8)) for v in methods.values()),"timing selector calibration blocks")
            delta={a:median(methods[a][b]-methods["ideal-skip"][b] for b in range(8)) for a in allowed}
            chosen=min(allowed,key=lambda a:(delta[a],a!="ideal-skip",allowed.index(a)))
            choices.setdefault(pid,{})[eid]=chosen
    require(load(directory/"choices.json")==choices,"all eight calibration timing choice")
    for pid,edits in choices.items():
        for eid,arm in edits.items():
            menu=initial_design["arms"][arm]["advice"]
            require(extra_plans["routed"][pid][eid]==plans[menu][pid][eid],"materialized timing choice changed requests")
            choice_histogram[grades[pid]["edits"][eid]["kind"]][arm]+=1
    for arm,spec in extra_design["arms"].items():
        if arm!="ideal-routed":
            require(spec==initial_design["arms"][arm],"existing replay strategy changed")
    decisions={}
    for panel,part in secondary["timing"].items():
        best=part["fastest_deterministic"];route=part["arms"]["ideal-routed"]
        signal=(route["paired_wins"]>=7 and route["median_paired_saving_ms"]>0 and route["whole_median_saving_ms"]>0)
        decisions[panel]=dict(benchmark=best,route=route,registered_replay_signal=signal)
    result_file=DEFAULT/"result.json"
    if result_file.is_file():
        official=load(result_file)
        require(not official["failures"],"final assessment failures")
        for panel,part in decisions.items():
            saved=official["panels"][panel]
            require(saved["repeat_best_deployable"]==part["benchmark"],"final replay benchmark")
            saved=saved["repeat_contrasts"]["ideal-routed"]
            route=part["route"]
            require(saved["wins"]==route["paired_wins"] and saved["blocks"]==8 and
                    saved["paired_ms"]==route["paired_savings_ms"] and
                    saved["median_paired_ms"]==route["median_paired_saving_ms"],"final replay contrast")
            require(abs(saved["candidate_median_ms"]-route["median_ms"]["total"])<1e-10 and
                    abs(saved["control_median_ms"]-part["route"]["median_ms"]["total"]-saved["median_gap_ms"])<1e-10,
                    "final replay medians")
        require(official["train_gate"]==decisions["broken"]["registered_replay_signal"],
                "training decision requires actual registered replay signal")
    return dict(choices_sha256=digest(directory/"choices.json"),choice_histogram={k:dict(v) for k,v in choice_histogram.items()},
        calibrating_blocks=list(range(8)),new_process_replay=True,decisions=decisions,
        boundary="Per-edit identity/timing advice on the same saved circuits is nondeployable. No evidence of a fitted feature policy or generalization.",
        pooled_12_of_16="Post-initial sensitivity; not used as the independent primary trigger.")


def self_test():
    def tables(values):
        return tuple(sum(((v >> b) & 1) << x for x, v in enumerate(values)) for b in (0, 1))
    before = tables([0, 1, 2, 3])
    after = tables([0, 0, 2, 1])
    change = classify_transition(2, before, after, (0, 1), 0, (0, 1, 2))
    require(not change["same_three_distinct"] and change["same_four_has_certificate"],
            "same-corners and same-face distinction lost")
    permuted = tables([1, 2, 0, 3])
    permutation = classify_transition(2, before, permuted, (0, 1), 0, (0, 1, 2))
    require(not permutation["original_values_unchanged"] and permutation["same_three_distinct"],
            "literal response equality confused with certificate validity")
    n = 5
    h = lambda x: ((x >> 0) ^ (x >> 1) ^ (x >> 2)) & 1
    one_bit = tuple(sum((h(x) ^ ((x >> (3 + b)) & 1)) << x for x in range(1 << n)) for b in (0, 1))
    require(eligible_triples(n, one_bit) == ((0, 1, 2),), "common support negative fixture")
    for axes in combinations((0, 1, 2), 2):
        mask = sum(1 << i for i in axes)
        for outside in range(1 << n):
            if outside & mask:
                continue
            require(len({response(one_bit, x) for x in face_rows(n, axes, outside)}) <= 2,
                    "sound witness rejects a real one-bit cut")
    wrong = False
    try:
        certificate(3, tables([0, 1, 2, 3] * 2), (0, 1, 2), (0, 2, 2))
    except ValueError:
        wrong = True
    require(wrong, "malformed triple admitted")
    stale = False
    try:
        certificate(2, after, (0, 2, 3), claimed=(0, 1, 2))
    except ValueError:
        stale = True
    require(stale, "stale responses admitted")
    return dict(same_four_not_same_three=True, same_three_not_same_values=True,
                one_bit_negative_not_rejected=True, malformed_and_stale_rejected=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--artifacts",type=Path,default=DEFAULT)
    parser.add_argument("--coverage-only",action="store_true")
    parser.add_argument("--milp",action="store_true")
    parser.add_argument("--include-selection",action="store_true")
    parser.add_argument("--output",type=Path)
    args = parser.parse_args()
    if args.self_test:
        report=self_test()
    elif args.coverage_only:
        p=parent_oracle();p.pin_away_from_timing();check_bindings(args.artifacts)
        cases=load(OLD/"public.json");grades=load(OLD/"grades.json");hints=load(OLD/"hints.json")
        evidence={c["id"]:p.inspect_parent(c,grades[c["id"]],hints[c["id"]]) for c in cases}
        _,report=coverage_audit(args.artifacts,cases,evidence)
    else:
        report=audit_all(args.artifacts,args.milp)
        if args.include_selection:
            secondary=audit_all(DEFAULT/"timing-selection")
            report["timing_selection"]=secondary
            report["timing_selection_audit"]=audit_timing_selection(report,secondary)
    if args.output:
        require(args.output.resolve()==DEFAULT/"audit.json","write outside assigned receipt")
        args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    summary=report if args.self_test or args.coverage_only else {
        "verdict":report["verdict"],"replay":report["physical_and_receipts"],
        "panels":{k:{"fastest_deterministic":v["fastest_deterministic"],
                      "fastest_advice":v["fastest_advice"],"signal_arms":v["signal_arms"]} for k,v in report["timing"].items()}}
    if args.include_selection and not args.self_test and not args.coverage_only:
        summary["timing_selection"]={p:dict(benchmark=d["benchmark"],registered_signal=d["registered_replay_signal"],
            wins=d["route"]["paired_wins"],median_paired_saving_ms=d["route"]["median_paired_saving_ms"],
            whole_median_saving_ms=d["route"]["whole_median_saving_ms"]) for p,d in report["timing_selection_audit"]["decisions"].items()}
    print(json.dumps(summary,indent=2,sort_keys=True))
