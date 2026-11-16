"""Independent finite joint-cut and physical NAND replay.

This module imports no producer, checker, fixture builder, or assessor.  Its
truth convention is bit x for raw input x; raw input j is bit j of x.  The
cofactor certificate enumerates literal assignments rather than reproducing
the producer's packed sparse-column implementation.  Timing is read from
sealed receipts, never remeasured here.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from functools import lru_cache
import gzip
import hashlib
from itertools import combinations
import json
from math import comb
from pathlib import Path
from statistics import median


ROOT = Path(__file__).resolve().parents[2]
TICKET = "FOLD-TWO-OUTPUT-20261115-001"
FAMILY = TICKET + "-E001_joint_tables"
DEFAULT = ROOT / "artifacts" / TICKET / FAMILY
METHODS = ("reference", "dag-first", "primitive", "named", "flat")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_bytes())


def integer(value, name, lower=0, upper=None):
    require(type(value) is int and value >= lower and (upper is None or value <= upper),
            "invalid integer " + name)
    return value


def scatter(value, positions):
    return sum(((value >> k) & 1) << j for k, j in enumerate(positions))


def source_value(expr, raw):
    """The grading-only source language; never a solver input."""
    if type(expr) is int:
        return (raw >> expr) & 1
    require(isinstance(expr, (list, tuple)) and expr, "malformed source expression")
    op = expr[0]
    if op == "NOT":
        require(len(expr) == 2, "NOT arity")
        return 1 ^ source_value(expr[1], raw)
    require(len(expr) == 3 and op in ("AND", "OR", "XOR"), "source grammar")
    a, b = source_value(expr[1], raw), source_value(expr[2], raw)
    return a & b if op == "AND" else a | b if op == "OR" else a ^ b


@lru_cache(maxsize=None)
def support(n, truth):
    return tuple(j for j in range(n)
                 if any(((truth >> x) ^ (truth >> (x ^ (1 << j)))) & 1
                        for x in range(1 << n)))


@lru_cache(maxsize=None)
def partition(n, targets, group):
    """Joint response classes, first-occurrence labels, and individual labels."""
    outside = tuple(j for j in range(n) if j not in group)
    signatures = []
    for local in range(8):
        base = scatter(local, group)
        responses = []
        for truth in targets:
            responses.append(tuple((truth >> (base | scatter(v, outside))) & 1
                                   for v in range(1 << len(outside))))
        signatures.append(tuple(responses))
    lookup, labels = {}, []
    for signature in signatures:
        if signature not in lookup:
            lookup[signature] = len(lookup)
        labels.append(lookup[signature])
    individual = []
    for port in range(2):
        seen = {}
        individual.append(tuple(seen.setdefault(sig[port], len(seen)) for sig in signatures))
    return len(lookup), tuple(labels), tuple(individual)


@lru_cache(maxsize=None)
def characterize(n, targets):
    integer(n, "n", 3)
    require(len(targets) == 2, "two output tables required")
    for truth in targets:
        integer(truth, "truth", 0, (1 << (1 << n)) - 1)
    supports = tuple(support(n, t) for t in targets)
    common = tuple(sorted(set(supports[0]) & set(supports[1])))
    ranks = tuple((g, partition(n, targets, g)[0]) for g in combinations(common, 3))
    require(ranks, "no eligible triple")
    least = min(count for _, count in ranks)
    width = (least - 1).bit_length()
    return dict(supports=supports, common_essential=common, eligible_count=len(ranks),
                minimum_classes=least, minimum_bits=width,
                minimizers=tuple(g for g, k in ranks if k == least),
                minimum_width_triples=tuple(g for g, k in ranks if (k - 1).bit_length() == width),
                class_count_histogram=dict(Counter(k for _, k in ranks)), ranks=ranks)


def circuit_shape(circuit, n):
    require(isinstance(circuit, dict), "circuit missing")
    if "n" in circuit:
        require(type(circuit["n"]) is int and circuit["n"] == n, "circuit arity changed")
    gates = circuit.get("gates")
    require(isinstance(gates, list), "gate array required")
    first = n + 2
    deps = [*(1 << j for j in range(n)), 0, 0]
    identities = [hashlib.sha256(canonical(["raw", j])).hexdigest() for j in range(n)]
    identities += [hashlib.sha256(canonical(["const", b])).hexdigest() for b in (0, 1)]
    for k, gate in enumerate(gates):
        require(isinstance(gate, (list, tuple)) and len(gate) == 2, "NAND arity")
        a, b = gate
        integer(a, "NAND lhs", 0, first + k - 1)
        integer(b, "NAND rhs", 0, first + k - 1)
        deps.append(deps[a] | deps[b])
        identities.append(hashlib.sha256(canonical(["NAND", *sorted((identities[a], identities[b]))])).hexdigest())
    ends = circuit.get("outputs")
    require(isinstance(ends, (list, tuple)) and len(ends) == 2, "two physical outputs required")
    for wire in ends:
        integer(wire, "physical output", 0, len(deps) - 1)
    return gates, tuple(ends), deps, identities


def execute(circuit, n, raw):
    """Fresh scalar physical execution; the caller validates shape once."""
    values = [*((raw >> j) & 1 for j in range(n)), 0, 1]
    for a, b in circuit["gates"]:
        values.append(1 ^ (values[a] & values[b]))
    return values


def verify_result(n, targets, result):
    require(isinstance(result, dict) and result.get("status") == "exact", "non-exact return")
    require(result.get("n") == n, "returned arity")
    group = result.get("triple")
    require(isinstance(group, (list, tuple)) and len(group) == 3, "triple required")
    require(all(type(j) is int for j in group), "triple indices must be integers")
    group = tuple(sorted(group))
    require(len(set(group)) == 3, "repeated group input")
    facts = characterize(n, tuple(targets))
    require(set(group) <= set(facts["common_essential"]), "group not essential to both outputs")
    count, classes, _ = partition(n, tuple(targets), group)
    width = (count - 1).bit_length()
    require(width == facts["minimum_bits"], "nonminimal summary width")
    require(result.get("class_count") == count and result.get("width") == width, "reported class/width")
    taps = result.get("summary_wires")
    require(isinstance(taps, (list, tuple)) and len(taps) == width and len(set(taps)) == width,
            "physical summary tuple length")
    circuit = result.get("circuit")
    gates, ends, dependencies, identities = circuit_shape(circuit, n)
    for tap in taps:
        integer(tap, "summary tap", 0, len(dependencies) - 1)
    mask = sum(1 << j for j in group)
    require(all(not (dependencies[t] & ~mask) for t in taps), "encoder reads outside raw group")
    first, tapset = n + 2, set(taps)

    def reach(end, stop):
        pending, seen = [end], set()
        while pending:
            wire = pending.pop()
            if wire in seen:
                continue
            seen.add(wire)
            if stop and wire in tapset:
                continue
            if wire >= first:
                pending.extend(gates[wire - first])
            elif stop and wire < n:
                require(wire not in group, "raw group bypasses physical taps")
        return seen

    cut_reach = [reach(w, True) for w in ends]
    used = [r & tapset for r in cut_reach]
    require(used[0] | used[1] == tapset, "unused summary tap")
    full_reach = [reach(w, False) for w in ends]
    truth, codes = [0, 0], [None] * 8
    code_truths = [0] * width
    for raw in range(1 << n):
        values = execute(circuit, n, raw)
        for port, end in enumerate(ends):
            require(values[end] == ((targets[port] >> raw) & 1), "wrong physical output")
            truth[port] |= values[end] << raw
        local = sum(((raw >> j) & 1) << k for k, j in enumerate(group))
        code = sum(values[t] << k for k, t in enumerate(taps))
        require(codes[local] in (None, code), "encoder depends on outside inputs")
        codes[local] = code
    for row, code in enumerate(codes):
        for bit in range(width):
            code_truths[bit] |= ((code >> bit) & 1) << row
    by_code = {}
    for local, code in enumerate(codes):
        require(by_code.setdefault(code, classes[local]) == classes[local], "code collision between residual classes")
    for name in ("assignment_classes", "class_codes"):
        if result.get(name) is not None:
            # class_codes in the independent producer means class labels, not physical codewords.
            require(tuple(result[name]) == classes, "reported " + name)
    if "assignment_codes" in result:
        require(list(result["assignment_codes"]) == codes, "reported physical codewords")
    if result.get("summary_truths") is not None:
        require(list(result["summary_truths"]) == code_truths, "reported encoder truth")
    if "truth" in result:
        require(list(result["truth"]) == list(targets), "reported output truth")
    if "expanded_NANDs" in result:
        require(result["expanded_NANDs"] == len(gates), "expanded NAND count")
    if "summary_wires" in circuit:
        require(list(circuit["summary_wires"]) == list(taps), "inner/outer tap disagreement")
    if "summary_wires_by_output" in result:
        require([set(v) for v in result["summary_wires_by_output"]] == used, "tap consumer report")
    reach0, reach1 = full_reach
    cert = dict(exact=True, width=width, classes=count, common=len(facts["common_essential"]),
                verified_assignments=1 << n, verified_output_bits=2 << n,
                alternatives_checked=0 if width == 1 else facts["eligible_count"] - 1,
                gates=len(gates), shared_gates=sum(w >= first for w in reach0 & reach1),
                active_gates=sum(w >= first for w in reach0 | reach1),
                shared_summary_wires=len(used[0] & used[1]), structural_locality=True)
    return cert, dict(group=group, code_words=codes, code_truths=code_truths,
                      represented_words=len(by_code), individual_taps=[len(u) for u in used],
                      physical_identity=[identities[w] for w in (*ends, *taps)],
                      scalar_NAND_evaluations=(1 << n) * len(gates))


def verify_work(n, targets, result):
    """Accounting identities only; no claim to replay elapsed time or all search."""
    work = result.get("work", {})
    require(all(type(v) in (int, float) and v >= 0 for v in work.values()), "negative/non-numeric search work")
    if "group_trials" in work:
        require(work["tasks"] == 1 and work["input_rows_received"] == 2 << n, "task/input work")
        require(work["group_trials"] == work["groups_requested"] ==
                work["group_failures"] + work["group_incumbents"], "failed group trials unaccounted")
        require(work["group_trials"] <= characterize(n, tuple(targets))["eligible_count"], "too many distinct group trials")
        bound, trials, failures, incumbents = 8, 0, 0, 0
        for _, count in characterize(n, tuple(targets))["ranks"]:
            trials += 1
            if count > bound:
                failures += 1
                continue
            incumbents += 1
            width = (count - 1).bit_length()
            if width == 1:
                break
            bound = 1 << (width - 1)
        require((work["group_trials"], work["group_failures"], work["group_incumbents"]) ==
                (trials, failures, incumbents), "literal replay of failed group-search schedule")
        require(work["eligible_group_count"] == characterize(n, tuple(targets))["eligible_count"]
                and work["support_bit_tests"] == 2 * n and work["group_cache_hits"] == 0,
                "support/search eligibility accounting")
        require(work["group_layout_builds"] + work["group_layout_hits"] == trials + 1,
                "layout requests including selected-code construction")
        # The sealed implementation packs both outputs into disjoint blocks
        # before extracting one joint response in a single shift/mask.
        require(work["joint_tables_joined"] == 1 and
                work["residual_packed_shifts"] == work["residual_packed_masks"] ==
                work["residual_joint_rows"], "response operation accounting")
        require(work["residual_row_equivalents"] == (1 << (n - 2)) * work["residual_joint_rows"],
                "response row equivalent accounting")
        require(work["residual_joint_rows"] <= 8 * work["group_trials"], "response rows per group")
        require(work["physical_output_comparisons"] == 2 and work["physical_output_bits_checked"] == 2 << n,
                "both output checks charged")
        require(work["physical_cut_resets"] == 1, "physical interface reset")
        require(work["physical_reachable_gates"] == len(result["circuit"]["gates"]), "reachable gate accounting")
        require(work["NAND_gates_appended"] == work["physical_reachable_gates"] + work["physical_pruned_gates"],
                "failed/dead physical gate accounting")
    elif "triple_trials" in work:
        ranks = characterize(n, tuple(targets))["ranks"]
        require(work["solve_calls"] == 1 and work["support_variable_tests"] == n,
                "reference task/support accounting")
        require(work["triple_trials"] == len(ranks) and work["response_requests"] == 2 * len(ranks),
                "reference scans all eligible triples")
        require(work["joint_response_keys"] == 8 * len(ranks) and
                work["joint_response_classes"] == sum(k for _, k in ranks), "reference full class accounting")
        uncached = work["response_requests"] - work["response_cache_hits"]
        require(work["response_columns_extracted"] == work["response_packed_shifts"] ==
                work["response_packed_masks"] == 8 * uncached, "reference memoized response accounting")
        require(work["export_gates_copied"] == len(result["circuit"]["gates"]), "reference export accounting")
        accepted = result.get("unrestricted_met_contract") is True
        require(work["class_code_bit_tests"] == (0 if accepted else 8 * result["width"]),
                "reference encoder construction accounting")
        require(work["residual_blocks_built"] == (0 if accepted else 2 * result["class_count"]) and
                work["residual_truth_bit_reads"] == (0 if accepted else 2 * result["class_count"] * (1 << (n - 3))),
                "reference both residuals constructed/charged")
        require(work["unrestricted_attempts"] == int(result.get("strategy") == "dag-first"), "unrestricted attempt accounting")
        require(work["frontier_acceptances"] == int(accepted) and
                work["dag_first_fallbacks"] == int(result.get("dag_first_fallback", False)), "circuit-first attempt/fallback accounting")
    return dict(work)


def fixture_audit(panels, grades):
    counts = Counter()
    groups = defaultdict(Counter)
    class_histograms = defaultdict(Counter)
    tie_histograms = defaultdict(Counter)
    same_hist, support_first, ties, wide_decoys = Counter(), Counter(), Counter(), Counter()
    seen_ids, seen_tables = set(), set()
    for panel, tasks in panels.items():
        index = {t["id"]: t for t in tasks}
        require(len(index) == len(tasks), "duplicate public task id")
        require(set(grades[panel]) == set(index), "grading/public identity mismatch")
        for task in tasks:
            require(set(task) == {"id", "n", "outputs"}, "provenance in public solver input")
            n, targets, name = task["n"], tuple(task["outputs"]), task["id"]
            require(name not in seen_ids and (n, tuple(sorted(targets))) not in seen_tables, "repeated public identity/table pair")
            seen_ids.add(name)
            seen_tables.add((n, tuple(sorted(targets))))
            grade = grades[panel][name]
            facts = characterize(n, targets)
            for field in ("supports", "common_essential", "eligible_count", "minimum_classes", "minimum_bits",
                          "minimizers", "minimum_width_triples", "class_count_histogram"):
                expected, actual = grade[field], facts[field]
                if field == "class_count_histogram":
                    expected = {int(k): v for k, v in expected.items()}
                require(canonical(expected) == canonical(actual), "fixture grading " + field)
            require(len(set().union(*facts["supports"])) == n, "inactive public input")
            require(grade["width"] == facts["minimum_bits"] and grade["min_classes"] == facts["minimum_classes"],
                    "legacy grade width")
            require(grade["n"] == n, "grade arity")
            for port, expr in enumerate(grade["source"]):
                literal = sum(source_value(expr, raw) << raw for raw in range(1 << n))
                require(literal == targets[port], "grading source disagrees with public table")
            planted = tuple(sorted(grade["planted_triple"]))
            k, labels, individual = partition(n, targets, planted)
            require(list(labels) == grade["planted_joint_partition"] and
                    [list(x) for x in individual] == grade["planted_single_partitions"], "planted partition")
            require(k == (2 if grade["kind"] == "shared" else 4), "matched planted class condition")
            require(facts["minimum_classes"] == k, "better unplanted cut")
            require(all(max(x) == 1 for x in individual), "single output is not individually one-bit")
            peer, peer_grade = index[grade["partner"]], grades[panel][grade["partner"]]
            changed = grade["changed_output"]
            require(peer_grade["partner"] == name and peer_grade["pair"] == grade["pair"], "unpaired fixture")
            require(targets[1 - changed] == peer["outputs"][1 - changed] and targets[changed] != peer["outputs"][changed],
                    "unmatched output change")
            require(facts["supports"] == characterize(n, tuple(peer["outputs"]))["supports"], "support mismatch across pair")
            key = (panel, str(n), grade["kind"])
            counts[panel] += 1
            groups[key].update(tasks=1, eligible_triples=facts["eligible_count"], minimum_classes=k,
                               minimum_bits=facts["minimum_bits"], minimum_width_ties=len(facts["minimum_width_triples"]))
            class_histograms[key].update(facts["class_count_histogram"])
            tie_histograms[key][len(facts["minimum_width_triples"])] += 1
            support_first[key] += ((facts["ranks"][0][1] - 1).bit_length() == facts["minimum_bits"])
            ties[key] += len(facts["minimum_width_triples"]) > 1
            wide_decoys[key] += any(v > 4 for _, v in facts["ranks"])
            if grade["kind"] == "shared":
                def hist(pair):
                    return tuple(sum((((pair[0] >> x) & 1) + 2 * ((pair[1] >> x) & 1)) == j
                                     for x in range(1 << n)) for j in range(4))
                same_hist[(panel, str(n))] += hist(targets) == hist(peer["outputs"])
    return dict(task_counts=dict(counts), groups={"/".join(k): dict(v) for k, v in groups.items()},
                histogram_matched_pairs={"/".join(k): v for k, v in same_hist.items()},
                support_first_minimum={"/".join(k): v for k, v in support_first.items()},
                cases_with_minimum_width_ties={"/".join(k): v for k, v in ties.items()},
                all_cut_class_count_histograms={"/".join(k): dict(v) for k, v in class_histograms.items()},
                minimum_width_tie_histograms={"/".join(k): dict(v) for k, v in tie_histograms.items()},
                cases_with_three_bit_decoy_cuts={"/".join(k): v for k, v in wide_decoys.items()})


def median_fields(rows):
    keys = set().union(*(r.keys() for r in rows))
    return {key: median(r.get(key, 0) for r in rows) for key in keys}


def measure(task, raw, cert):
    result = raw.get("result") or {}
    exact = raw.get("failure") is None and cert is not None
    out = Counter(tasks=1, exact=int(exact), correct_width=int(exact),
                  width1=int(exact and cert["width"] == 1), width2=int(exact and cert["width"] == 2),
                  classes2=int(exact and cert["classes"] == 2), classes4=int(exact and cert["classes"] == 4),
                  table_rows=cert["verified_assignments"] if exact else 0,
                  output_bits=cert["verified_output_bits"] if exact else 0,
                  physical_gates=cert["gates"] if exact else 0,
                  shared_gates=cert["shared_gates"] if exact else 0,
                  active_gates=cert["active_gates"] if exact else 0,
                  shared_taps=cert["shared_summary_wires"] if exact else 0,
                  shared_intermediate_returns=int(exact and cert["shared_summary_wires"] > 0),
                  any_shared_gate_returns=int(exact and cert["shared_gates"] > 0),
                  fold_uses=result.get("fold_uses", 0), returns_using_fold=int(result.get("fold_uses", 0) > 0))
    for field in ("cpu_ns", "wall_ns", "init_cpu_ns", "synth_cpu_ns", "verify_cpu_ns", "verify_wall_ns", "return_bytes"):
        out[field] = integer(raw[field], field)
    require(out["cpu_ns"] >= out["init_cpu_ns"] + out["synth_cpu_ns"] + out["verify_cpu_ns"],
            "component CPU exceeds paid row CPU")
    if exact:
        facts = characterize(task["n"], tuple(task["outputs"]))
        out["uses_planted_group"] = int(tuple(sorted(result["triple"])) == facts["minimizers"][0])
    else:
        out["uses_planted_group"] = 0
    return out


def self_test():
    """Hand fixtures, including an exact two-bit control retaining shared work."""
    n = 5
    targets = [0, 0]
    broken = [0, 0]
    for x in range(32):
        a, b, c, d, e = [(x >> j) & 1 for j in range(5)]
        q = (a & b) ^ c ^ d
        targets[0] |= q << x
        targets[1] |= (q ^ e) << x
        broken[0] |= q << x
        broken[1] |= (q ^ a ^ e) << x
    good = characterize(n, tuple(targets))
    bad = characterize(n, tuple(broken))
    require(good["minimum_classes"] == 2 and good["minimizers"] == ((0, 1, 2), (0, 1, 3)), "hand positive ties")
    require(dict(bad["class_count_histogram"]) == {4: 4}, "hand broken all-cut bound")
    gates = []
    def nand(a, b):
        gates.append([a, b])
        return n + 1 + len(gates)
    def xor(a, b):
        h = nand(a, b)
        return nand(nand(a, h), nand(b, h))
    t = nand(0, 1)
    t = nand(t, t)
    h = xor(t, 2)
    q = xor(h, 3)
    r = xor(q, 4)
    fixture = dict(status="exact", n=n, triple=[0, 1, 2], class_count=2, width=1,
                   summary_wires=[h], circuit=dict(n=n, gates=deepcopy(gates), outputs=[q, r]))
    positive_cert, _ = verify_result(n, targets, fixture)
    require(positive_cert["shared_gates"] > 0, "no actual shared computation")
    r_bad = xor(xor(q, 0), 4)
    broken_fixture = dict(status="exact", n=n, triple=[0, 1, 2], class_count=4, width=2,
                          summary_wires=[h, 0], circuit=dict(n=n, gates=deepcopy(gates), outputs=[q, r_bad]))
    broken_cert, _ = verify_result(n, broken, broken_fixture)
    require(broken_cert["shared_gates"] > 0, "broken cut loses all shared computation")
    mutations = []
    mutant = deepcopy(fixture)
    mutant["circuit"]["gates"][0] = [0, 0]
    mutations.append(("wrong NAND", mutant))
    mutant = deepcopy(fixture)
    mutant["circuit"]["outputs"][1] = q
    mutations.append(("only second output corrupted", mutant))
    mutant = deepcopy(fixture)
    mutant["summary_wires"] = [0]
    mutations.append(("raw bypass of claimed summary", mutant))
    mutant = deepcopy(fixture)
    mutant["summary_wires"] = [3]
    mutations.append(("outside-reading encoder", mutant))
    mutant = deepcopy(fixture)
    mutant["class_count"], mutant["width"] = 4, 2
    mutant["triple"], mutant["summary_wires"] = [0, 2, 3], [0, 2]
    mutations.append(("suboptimal cut", mutant))
    mutant = deepcopy(fixture)
    mutant["circuit"]["gates"][0] = [n + 2, 1]
    mutations.append(("forward reference", mutant))
    rejected = []
    for name, mutant in mutations:
        try:
            verify_result(n, targets, mutant)
        except ValueError:
            rejected.append(name)
        else:
            raise AssertionError("mutation accepted: " + name)
    # Outside selectors can distinguish all eight local assignments: no two-bit cap.
    query = sum(((x >> (0 if ((x >> 3) & 3) == 0 else 1 if ((x >> 3) & 3) == 1 else 2)) & 1) << x
                for x in range(32))
    require(partition(n, (query, query ^ ((1 << 32) - 1)), (0, 1, 2))[0] == 8, "three-bit cofactor fixture")
    return dict(positive_classes=good["minimum_classes"], positive_ties=len(good["minimizers"]),
                broken_classes=bad["minimum_classes"], broken_retains_shared_gates=broken_cert["shared_gates"],
                three_bit_cut_classes=8, rejected_mutations=rejected)


def audit(out):
    design = load(out / "design.json")
    for name, wanted in design["sources"].items():
        require(digest(ROOT / name) == wanted, "bound source changed: " + name)
    for name, wanted in design["data"].items():
        require(digest(out / name) == wanted, "bound data changed: " + name)
    panels = {p: load(out / (p + ".json")) for p in ("primary", "sensitivity")}
    grades = load(out / "grades.json")
    fixtures = fixture_audit(panels, grades)
    self_checks = self_test()
    streams, work_runs, group_runs = defaultdict(dict), defaultdict(list), defaultdict(list)
    prefixes = defaultdict(dict)
    identities, choices, physical = {}, {}, {}
    failures, raw_digests = [], {}
    totals = Counter()
    for line in (out / "results.jsonl").read_text().splitlines():
        event = json.loads(line)
        require(event["status"] == "ok", "unresolved worker failure: " + event["case"])
        saved = event["result"]
        key = saved["panel"], saved["cache"], saved["arm"]
        rep = saved["repeat"]
        require(key[2] in METHODS and rep not in streams[key], "unknown/duplicate stream")
        require(saved["cpu"] == design["cpu"], "CPU affinity changed")
        path = out / saved["file"]
        require(digest(path) == saved["sha256"], "stream digest changed")
        raw_digests[path.name] = saved["sha256"]
        with gzip.open(path, "rt") as handle:
            rows = [json.loads(row) for row in handle]
        tasks = panels[key[0]]
        require(saved["tasks"] == len(rows) == len(tasks), "incomplete stream")
        counts, work, cells = Counter(), Counter(), defaultdict(Counter)
        prefix = [saved["startup_cpu_ns"]]
        identity, selected, signature = [], [], []
        for task, raw in zip(tasks, rows, strict=True):
            require(task["id"] == raw["id"], "public task order changed")
            result = raw.get("result")
            cert = None
            if raw.get("failure") is None:
                cert, info = verify_result(task["n"], tuple(task["outputs"]), result)
                require(raw["certificate"] == cert, "producer certificate disagrees with scalar audit")
                work.update(verify_work(task["n"], tuple(task["outputs"]), result))
                totals.update(physical_programs=1, scalar_rows=1 << task["n"],
                              scalar_output_bits=2 << task["n"], scalar_NAND_evaluations=info["scalar_NAND_evaluations"])
                signature.append(info["physical_identity"])
                public_return = dict(n=result["n"], triple=result["triple"], width=result["width"],
                                     class_count=result["class_count"], summary_wires=result["summary_wires"],
                                     circuit=dict(gates=result["circuit"]["gates"], outputs=result["circuit"]["outputs"]))
                require(len(canonical(public_return)) == raw["return_bytes"], "public return byte accounting")
            else:
                failures.append(dict(panel=key[0], cache=key[1], arm=key[2], repeat=rep,
                                     id=task["id"], failure=raw["failure"]))
                signature.append(None)
            metric = measure(task, raw, cert)
            if cert is not None:
                metric["uses_planted_group"] = int(tuple(sorted(result["triple"])) == tuple(sorted(grades[key[0]][task["id"]]["triple"])))
            counts.update(metric)
            grade = grades[key[0]][task["id"]]
            for label in (str(task["n"]), grade["kind"], f"{task['n']}-{grade['kind']}"):
                cells[label].update(metric)
            prefix.append(prefix[-1] + metric["cpu_ns"])
            choice = [result.get(k) for k in ("triple", "width", "class_count")] if result else [None] * 3
            selected.append(choice)
            identity.append([choice, result.get("circuit"), result.get("summary_wires"), metric["fold_uses"]] if result else None)
        encoded_identity = canonical(identity)
        if key in identities:
            require(identities[key] == encoded_identity, "physical programs changed across repeats")
        identities[key], choices[key], physical[key] = encoded_identity, selected, signature
        counts.update(startup_cpu_ns=saved["startup_cpu_ns"], startup_wall_ns=saved["startup_wall_ns"],
                      paid_cpu_ns=counts["cpu_ns"] + saved["startup_cpu_ns"],
                      paid_wall_ns=counts["wall_ns"] + saved["startup_wall_ns"])
        streams[key][rep], prefixes[key][rep] = dict(counts), prefix
        work_runs[key].append(work)
        for label, cell in cells.items():
            group_runs[key + (label,)].append(cell)
    methods = {}
    for panel, cache, repeat_count in (("primary", "warm", 10), ("primary", "cold", 5), ("sensitivity", "warm", 2)):
        category = panel + "-" + cache
        methods[category] = {}
        for arm in METHODS:
            key = panel, cache, arm
            require(set(streams[key]) == set(range(repeat_count)), "missing run matrix " + str(key))
            stats = median_fields(list(streams[key].values()))
            stats["cpu_repeats_ns"] = [streams[key][i]["paid_cpu_ns"] for i in range(repeat_count)]
            stats["wall_repeats_ns"] = [streams[key][i]["paid_wall_ns"] for i in range(repeat_count)]
            stats["work"] = median_fields(work_runs[key])
            stats["groups"] = {k[-1]: median_fields(v) for k, v in group_runs.items() if k[:3] == key}
            methods[category][arm] = stats
        require(choices[panel, cache, "named"] == choices[panel, cache, "flat"], "named/flat chosen interfaces differ")
    warm = methods["primary-warm"]
    baseline = min(("reference", "dag-first", "primitive"), key=lambda arm: warm[arm]["paid_cpu_ns"])
    comparisons = {}
    for arm, row in warm.items():
        base = warm[baseline]
        comparisons[arm] = dict(cpu_saved_pct=100 * (1 - row["paid_cpu_ns"] / base["paid_cpu_ns"]),
                                wall_saved_pct=100 * (1 - row["paid_wall_ns"] / base["paid_wall_ns"]),
                                paired_cpu_wins=sum(x < y for x, y in zip(row["cpu_repeats_ns"], base["cpu_repeats_ns"], strict=True)),
                                paired_wall_wins=sum(x < y for x, y in zip(row["wall_repeats_ns"], base["wall_repeats_ns"], strict=True)),
                                lower_steady_cpu=row["cpu_ns"] < base["cpu_ns"])
    guide = comparisons["named"]
    qualifies = (not any(f["panel"] == "primary" for f in failures)
                 and warm["named"]["fold_uses"] > 0
                 and 10 * warm["named"]["paid_cpu_ns"] <= 9 * warm[baseline]["paid_cpu_ns"]
                 and guide["paired_cpu_wins"] >= 8 and guide["wall_saved_pct"] > 0
                 and guide["lower_steady_cpu"] and comparisons["flat"]["lower_steady_cpu"])
    historical_path = ROOT / "artifacts/FOLD-DISCOVERY-20261115-001/FOLD-DISCOVERY-20261115-001-E001_learned_library/gate-freeze.json"
    previous = load(historical_path)
    median_paths = {arm: [median(values) for values in zip(*prefixes["primary", "warm", arm].values(), strict=True)]
                    for arm in (baseline, "named")}
    gaps = [x + previous["cpu_ns"] - y for x, y in zip(median_paths["named"], median_paths[baseline], strict=True)]
    history = dict(pool_cpu_ns=previous["cpu_ns"], pool_wall_ns=previous["wall_ns"], historical_winner_was_supplied=False,
                   cpu_if_charged_ns=warm["named"]["paid_cpu_ns"] + previous["cpu_ns"],
                   wall_if_charged_ns=warm["named"]["paid_wall_ns"] + previous["wall_ns"],
                   first_cpu_break_even_with_pool=next((i for i in range(1, len(gaps)) if gaps[i] <= 0), None),
                   last_cpu_gap_with_pool_ns=gaps[-1])
    official = load(out / "result.json")
    independently_computed = dict(methods=methods, benchmark=baseline, comparisons=comparisons,
                                  qualifies_for_paid_learning=qualifies, pool_sensitivity=history)
    for key, wanted in independently_computed.items():
        require(canonical(official[key]) == canonical(wanted), "assessor aggregation discrepancy: " + key)
    require(official["measured_returns"] == totals["physical_programs"] + len(failures), "return count summary")
    require(official["total_assignments"] == totals["scalar_rows"] and official["total_verified_bits"] == totals["scalar_output_bits"],
            "physical replay denominator")
    matched = {}
    matched_primitive = {}
    for panel, cache in (("primary", "warm"), ("primary", "cold"), ("sensitivity", "warm")):
        a, b = physical[panel, cache, "named"], physical[panel, cache, "flat"]
        matched[panel + "-" + cache] = dict(tasks=len(a), same_physical_dependencies=sum(x == y for x, y in zip(a, b, strict=True)))
        p = physical[panel, cache, "primitive"]
        matched_primitive[panel + "-" + cache] = dict(
            tasks=len(a), same_physical_dependencies=sum(x == y for x, y in zip(a, p, strict=True)),
            same_interfaces=sum(x == y for x, y in zip(choices[panel, cache, "named"], choices[panel, cache, "primitive"], strict=True)))
    return dict(schema_version=1, ticket=TICKET, verdict="PASS", independence="Separate literal cofactor and scalar NAND implementation; no producer imports or timed reruns.",
                auditor_sha256=digest(__file__), design_sha256=digest(out / "design.json"),
                result_sha256=digest(out / "result.json"), stream_sha256=raw_digests,
                self_test=self_checks, fixtures=fixtures, replay=dict(totals), failures=failures,
                benchmark=baseline, comparisons=comparisons, qualifies_for_paid_learning=qualifies,
                methods=methods, pool_sensitivity=history, named_inline_control=matched,
                matched_primitive_control=matched_primitive,
                nonclaims=["A width minimum is not a NAND minimum or a lower bound on search CPU.",
                           "A two-bit broken cut can still share substantial output computation.",
                           "Recorded logical counters and CPU durations are not interchangeable units.",
                           "The historical pool ledger grants selecting the supplied fold for free; that learner selected a different entry.",
                           "This audit replays physical programs and accounting identities, not original wall-clock execution."])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--fixtures", action="store_true", help="Audit saved public tables/grading only; no solver or outcome access")
    parser.add_argument("--artifacts", type=Path, default=DEFAULT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.self_test:
        report = self_test()
    elif args.fixtures:
        report = fixture_audit({p: load(args.artifacts / (p + ".json")) for p in ("primary", "sensitivity")},
                               load(args.artifacts / "grades.json"))
    else:
        report = audit(args.artifacts.resolve())
    if args.output:
        require(args.output.resolve() == DEFAULT / "audit.json", "output outside owned audit artifact")
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report if args.self_test or args.fixtures else
                     {k: report[k] for k in ("verdict", "replay", "benchmark", "comparisons", "qualifies_for_paid_learning")},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
