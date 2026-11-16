"""Independent TRIPLE-ORDER oracle, transcript and physical replay.

The terminal two-output audit supplies the independent literal oracle and
scalar NAND interpreter.  No producer, feature extractor, trainer, checker,
fixture generator, or assessor is imported.  Scientific replay is performed
only after a frozen checkpoint and complete receipts are authorized.
"""

from __future__ import annotations

from functools import lru_cache
from fractions import Fraction
from collections import Counter, defaultdict
from datetime import datetime
import gzip
import importlib.util
from itertools import combinations
import json
from math import gcd
from pathlib import Path
from statistics import median


ROOT = Path(__file__).resolve().parents[2]
TICKET = "TRIPLE-ORDER-20261115-001"
DEFAULT = ROOT / "artifacts" / TICKET / (TICKET + "-E001_rank_triples")
ORACLE_PATH = ROOT / "research/FOLD-TWO-OUTPUT-20261115-001/audit.py"
ORACLE_SHA256 = "adbe5f223102b41091ee0a13367288a1e13929fbed6d8a05564bec25c568db1d"


@lru_cache(maxsize=1)
def oracle():
    import hashlib
    if hashlib.sha256(ORACLE_PATH.read_bytes()).hexdigest() != ORACLE_SHA256:
        raise ValueError("terminal independent oracle changed")
    spec = importlib.util.spec_from_file_location("triple_order_terminal_independent", ORACLE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@lru_cache(maxsize=None)
def dense_responses(n, targets, group):
    """Literal compact response columns; producer uses sparse packed columns."""
    outside = tuple(j for j in range(n) if j not in group)
    result = []
    for local in range(8):
        base = oracle().scatter(local, group)
        columns = []
        for table in targets:
            columns.append(sum(((table >> (base | oracle().scatter(v, outside))) & 1) << v
                               for v in range(1 << len(outside))))
        result.append(tuple(columns))
    return tuple(result)


def width_targets(n, targets):
    """All admissible minimizing labels, including ties unrelated to ancestry."""
    facts = oracle().characterize(n, tuple(targets))
    return dict(minimum_width=facts["minimum_bits"], minimum_classes=facts["minimum_classes"],
                eligible_triples=[g for g, _ in facts["ranks"]],
                minimizing_triples=facts["minimum_width_triples"],
                classes_by_triple=dict(facts["ranks"]))


def table_summary(n, table):
    count = table.bit_count()
    coordinates = []
    for j in range(n):
        low = [x for x in range(1 << n) if not x & (1 << j)]
        low_ones = sum((table >> x) & 1 for x in low)
        high_ones = sum((table >> (x | (1 << j))) & 1 for x in low)
        changes = sum(((table >> x) ^ (table >> (x | (1 << j)))) & 1 for x in low)
        coordinates.append((low_ones, high_ones, changes))
    return count, tuple(sorted(coordinates))


def fingerprint(value):
    import hashlib
    return hashlib.sha256(oracle().canonical(value)).hexdigest()


def raw_family(n, targets):
    return fingerprint(("raw pair domain v1", n, sorted(table_summary(n, t) for t in targets)))


def consumer_family(n, consumers):
    """Independent scalar reconstruction of the declared split invariant."""
    def value(expr, raw):
        if expr == "inner":
            return raw & 1
        if type(expr) is int:
            oracle().require(expr >= 3, "raw inner pin inside downstream-only expression")
            return (raw >> (expr - 2)) & 1
        op = expr[0]
        a, b = value(expr[1], raw), value(expr[2], raw)
        oracle().require(op in ("AND", "OR", "XOR"), "downstream source operation")
        return a & b if op == "AND" else a | b if op == "OR" else a ^ b
    k = n - 3
    descriptors = []
    for expr in consumers:
        low = sum(value(expr, raw << 1) << raw for raw in range(1 << k))
        high = sum(value(expr, (raw << 1) | 1) << raw for raw in range(1 << k))
        descriptors.append((table_summary(k, low), table_summary(k, high), (low ^ high).bit_count()))
    ordinary = tuple(sorted(descriptors))
    reversed_inner = tuple(sorted((b, a, d) for a, b, d in descriptors))
    return fingerprint(("downstream domain v1", n, min(ordinary, reversed_inner)))


def check_panel(split, public, grades):
    """Grade public tables and split keys without generating any task."""
    require = oracle().require
    expected = 48 if split == "train" else 192
    require(len(public) == len(grades) == expected and {r["id"] for r in public} == set(grades), "panel size/IDs")
    index = {r["id"]: r for r in public}
    seen, families, structures = set(), set(), set()
    from collections import Counter
    counts, ties, decoys = Counter(), Counter(), Counter()
    for row in public:
        n, outputs = row["n"], tuple(row["outputs"])
        grade = grades[row["id"]]
        require(set(row) == {"id", "n", "outputs"} and n in (7, 8, 9), "public input leak/arity")
        require((n, tuple(sorted(outputs))) not in seen, "duplicate table pair")
        seen.add((n, tuple(sorted(outputs))))
        facts = width_targets(n, outputs)
        candidates = tuple(combinations(range(n), 3))
        require(facts["eligible_triples"] == list(candidates), "input not essential to both outputs")
        classes = [facts["classes_by_triple"][t] for t in candidates]
        widths = [(k - 1).bit_length() for k in classes]
        require(classes == grade["candidate_classes"] and widths == grade["candidate_widths"], "candidate supervision classes")
        require(facts["minimum_width"] == grade["width"] and facts["minimum_classes"] == grade["min_classes"], "minimum supervision width")
        require(oracle().canonical(facts["minimizing_triples"]) == oracle().canonical(grade["minimizers"]), "missing valid tied supervision")
        require([list(t) for t, k in zip(candidates, classes) if k == min(classes)] == grade["class_minimizers"], "class minimizers")
        require(facts["minimum_classes"] == (2 if grade["kind"] == "shared" else 4), "matched class condition")
        require(tuple(grade["triple"]) in facts["minimizing_triples"], "planted group not width-minimal")
        for port, expr in enumerate(grade["source"]):
            require(sum(oracle().source_value(expr, raw) << raw for raw in range(1 << n)) == outputs[port], "source truth")
        raw_key = raw_family(n, outputs)
        structure = consumer_family(n, grade["logical_consumers"])
        require(raw_key == grade["truth_family"] and structure == grade["structure"], "split fingerprints")
        should = "test" if int(raw_key[:2], 16) & 1 else "train"
        should2 = "test" if int(structure[:2], 16) & 1 else "train"
        require(should == should2 == split, "split-domain violation")
        families.add(raw_key)
        structures.add(structure)
        peer = index[grade["partner"]]
        peer_grade = grades[grade["partner"]]
        changed = grade["changed_output"]
        require(peer_grade["partner"] == row["id"] and peer_grade["pair"] == grade["pair"], "pair identity")
        require(peer["outputs"][1 - changed] == outputs[1 - changed] and peer["outputs"][changed] != outputs[changed], "matched output change")
        require(peer_grade["structure"] == structure and peer_grade["truth_family"] == raw_key, "pair split apart")
        simple = []
        for group, width in zip(candidates, widths):
            individual = oracle().partition(n, outputs, group)[2]
            if min(len(set(p)) for p in individual) == 2 and width > facts["minimum_width"]:
                simple.append(list(group))
        require(simple and simple == grade["single_output_decoys"], "single-output false candidate grading")
        label = f"{n}/{grade['operation']}/{grade['kind']}"
        counts[label] += 1
        ties[label] += len(facts["minimizing_triples"])
        decoys[label] += len(simple)
    require(len(families) == len(structures) == expected // 2, "repeated consumer/raw family")
    return dict(rows=expected, matched_pairs=expected // 2, counts=dict(counts),
                total_valid_labels=dict(ties), single_output_decoys=dict(decoys),
                raw_families=sorted(families), consumer_families=sorted(structures))


@lru_cache(maxsize=None)
def scalar_axis_profiles(n, targets):
    """Count six unordered transitions of the TWO-bit visible answer."""
    transitions = []
    edge_order = ((0, 1), (2, 3), (0, 2), (1, 3), (0, 3), (1, 2))
    for axis in range(n):
        edges = dict.fromkeys(edge_order, 0)
        for raw in range(1 << n):
            if raw & (1 << axis):
                continue
            flipped = raw | (1 << axis)
            before = ((targets[0] >> raw) & 1) + 2 * ((targets[1] >> raw) & 1)
            after = ((targets[0] >> flipped) & 1) + 2 * ((targets[1] >> flipped) & 1)
            if before != after:
                edges[tuple(sorted((before, after)))] += 1
        transitions.append(tuple(edges[e] for e in edge_order))
    return tuple(transitions)


@lru_cache(maxsize=None)
def features(n, targets, channel, axes=None):
    axes = tuple(range(n)) if axes is None else tuple(axes)
    buckets = {}
    for axis in axes:
        profile6 = scalar_axis_profiles(n, tuple(targets))[axis]
        x0, x1, y0, y1, same, opposite = profile6
        ca, cb, both = x0 + x1 + same + opposite, y0 + y1 + same + opposite, same + opposite
        if channel == "marginals":
            profile, mass = (ca, cb), max(ca, cb)
        elif channel == "joint":
            profile, mass = (ca, cb, both), ca + cb - both
        else:
            oracle().require(channel == "transitions", "unknown feature channel")
            profile, mass = profile6, sum(profile6)
        scale = gcd(*profile)
        signature = tuple(v // scale for v in profile) if scale else profile
        buckets.setdefault(signature, []).append((axis, mass))
    count = len(axes)
    units = (2 * count + ((4 * count + 1) if channel == "transitions" else 2 * count)
             + {"marginals": 4, "joint": 6, "transitions": 12}[channel] * count + 2 * count)
    return tuple(tuple(b) for b in buckets.values() if len(b) >= 3), units


def influence_shape(values):
    ordered = tuple(sorted(values))
    common = gcd(*ordered)
    return tuple(v // common for v in ordered) if common and ordered[-1] <= 4 * common else None


@lru_cache(maxsize=None)
def choose_candidate(n, targets, channel, shapes, eligible=None, details=False):
    """Exhaustive semantic choice plus independent public bookkeeping replay."""
    eligible = tuple(combinations(range(n), 3)) if eligible is None else tuple(eligible)
    axes = tuple(sorted(set().union(*eligible)))
    oracle().require(len(eligible) == len(tuple(combinations(axes, 3))), "audit expects complete eligible domain")
    buckets, base_units = features(n, tuple(targets), channel, axes)
    shapes = tuple(tuple(s) for s in shapes)
    index = {axis: (i, mass) for i, bucket in enumerate(buckets) for axis, mass in bucket}
    candidates = []
    for group in eligible:
        data = [index.get(axis) for axis in group]
        if any(v is None for v in data) or len({v[0] for v in data}) != 1:
            continue
        category = influence_shape([v[1] for v in data]) if shapes else None
        priority = shapes.index(category) if category in shapes else len(shapes)
        candidates.append((priority, len(buckets[data[0][0]]), group))
    best = min(candidates, default=None)
    # The producer uses mass bins to avoid enumerating all triples. Reconstruct
    # the work charged by that fixed procedure, then compare its result with
    # the exhaustive choice above. The scalar feature counts are independent.
    state = None
    visits = probes = tuples = 0
    for bucket in buckets:
        visits += 1
        group = tuple(axis for axis, _ in bucket[:3])
        key = (len(shapes), len(bucket), group)
        state = key if state is None else min(state, key)
        if not shapes:
            continue
        if len(bucket) == 3:
            tuples += 1
            category = influence_shape([mass for _, mass in bucket])
            if category in shapes:
                state = min(state, (shapes.index(category), 3, group))
            continue
        bins = {}
        for axis, mass in bucket:
            bins.setdefault(mass, []).append(axis)
        for priority, shape in enumerate(shapes):
            if priority > state[0]:
                break
            a, b, c = shape
            for mass, low_axes in bins.items():
                probes += 1
                scale, remainder = divmod(mass, a)
                if remainder or not scale:
                    continue
                middle, high = bins.get(b * scale), bins.get(c * scale)
                if middle is None or high is None:
                    continue
                middle_index = int(a == b)
                high_index = int(a == c) + int(b == c)
                if len(middle) <= middle_index or len(high) <= high_index:
                    continue
                group = tuple(sorted((low_axes[0], middle[middle_index], high[high_index])))
                tuples += 1
                state = min(state, (priority, len(bucket), group))
    oracle().require(state == best, "optimized shape lookup differs from exhaustive triple priority")
    answer = (None if best is None else best[2]), base_units + visits + probes + tuples
    return (*answer, dict(bucket_visits=visits, shape_scale_probes=probes, candidate_tuple_visits=tuples)) if details else answer


def replay_fit(public, grades):
    """Reproduce all finite supervised choices, using no producer fitter."""
    from collections import Counter
    gates = (4, 10, 20, 35, 56, 84)
    channels = ("marginals", "joint", "transitions")
    rows = []
    for task in public:
        n, outputs = task["n"], tuple(task["outputs"])
        truth = width_targets(n, outputs)
        eligible = tuple(truth["eligible_triples"])
        good = frozenset(truth["minimizing_triples"])
        positions = {g: i for i, g in enumerate(eligible)}
        rows.append((n, outputs, eligible, positions, good, min(positions[g] for g in good), truth["minimum_width"] == 1))
        oracle().require(list(grades[task["id"]]["minimizers"]) == [list(g) for g in truth["minimizing_triples"]], "fit target labels")
    def model(channel, gate, shapes=()):
        return dict(version="axis-transitions-v1", channel=channel, min_eligible=gate, shape_priority=[list(s) for s in shapes])
    empty = dict(objective_units=0, early_group_attempts_saved=0, first_minimizer_positions_saved_all=0,
                 feature_units=0, tasks_scored=0, training_promotions=0)
    winner, winner_score, winner_key = model("lexical", 0), empty, (0, 0, 0, 0, 0)
    models = [dict(model=winner, **empty)]
    shape_reports = {}
    for channel_index, channel in enumerate(channels, 1):
        positive, exposure, cases = Counter(), Counter(), Counter()
        for n, outputs, eligible, _, good, *_ in rows:
            buckets, _ = features(n, outputs, channel)
            index = {axis: (i, mass) for i, bucket in enumerate(buckets) for axis, mass in bucket}
            per_positive, per_all = Counter(), Counter()
            for group in eligible:
                data = [index.get(a) for a in group]
                if any(v is None for v in data) or len({v[0] for v in data}) != 1:
                    continue
                shape = influence_shape([v[1] for v in data])
                if shape is not None:
                    per_all[shape] += 1
                    per_positive[shape] += int(group in good)
            for shape, count in per_all.items():
                exposure[shape] += Fraction(count, len(eligible))
            for shape, count in per_positive.items():
                if count:
                    positive[shape] += Fraction(count, len(good))
                    cases[shape] += 1
        smooth = Fraction(1, 4)
        priority = [s for s in positive if cases[s] >= 2 and positive[s] > exposure[s]]
        priority.sort(key=lambda s: (-(positive[s] + smooth) / (exposure[s] + smooth), -positive[s], s))
        priority = tuple(priority[:2])
        shape_reports[channel] = [dict(shape=list(s), positive_task_mass=float(positive[s]),
                                       candidate_task_mass=float(exposure[s]), supporting_tasks=cases[s])
                                  for s in sorted(exposure)]
        for length in range(len(priority) + 1):
            shapes = priority[:length]
            proposals = [choose_candidate(n, outputs, channel, shapes, eligible) for n, outputs, eligible, *_ in rows]
            for gate in gates:
                units = saved = all_saved = paid = promoted = 0
                for row, (candidate, cost) in zip(rows, proposals, strict=True):
                    _, _, eligible, positions, good, original, early = row
                    if len(eligible) < gate:
                        continue
                    paid += 1
                    units += cost
                    if candidate is None:
                        continue
                    position = positions[candidate]
                    promoted += int(position != 0)
                    gain = original if candidate in good else -int(position > original)
                    all_saved += gain
                    saved += gain if early else 0
                score = dict(objective_units=24 * saved - units, early_group_attempts_saved=saved,
                             first_minimizer_positions_saved_all=all_saved, feature_units=units,
                             tasks_scored=paid, training_promotions=promoted)
                candidate_model = model(channel, gate, shapes)
                models.append(dict(model=candidate_model, **score))
                key = (score["objective_units"], -score["feature_units"], -length, -channel_index, gate)
                if key > winner_key:
                    winner, winner_score, winner_key = candidate_model, score, key
    fixed = model("joint", 4)
    fixed_score = next(m for m in models if m["model"] == fixed)
    return dict(model=winner, fit_score=winner_score, candidates=models, shape_fit=shape_reports,
                fixed_score={k: v for k, v in fixed_score.items() if k != "model"},
                model_body_sha256=fingerprint(winner), training_tasks=len(rows), early_stop_tasks=sum(row[-1] for row in rows),
                minimum_triple_labels=sum(len(row[4]) for row in rows), candidate_count=len(models))


RANK_FIELDS = ("orders", "lexical_returns", "feature_calls", "axis_profiles", "axis_masks_built",
               "layouts_built", "layout_cache_hits", "packed_shifts", "packed_xors", "packed_ands",
               "packed_popcounts", "axis_normalizations", "bucket_visits", "shape_scale_probes",
               "candidate_tuple_visits", "promotions", "estimated_feature_units")
COFACTOR_FIELDS = ("fixed_order_calls", "fixed_candidates", "fixed_feature_hits", "fixed_layout_builds",
                   "fixed_packed_shifts", "fixed_packed_masks", "fixed_response_keys")
METHODS = ("lex", "fixed", "reference", "learned", "cofactor", "prior-generic", "transitions")


class TraceReplay:
    """Private public-output memory and ranking geometry, reset each deployment."""

    def __init__(self, n, arm, model):
        self.n, self.arm, self.model = n, arm, model
        self.memory = {}
        self.layout_seen = False

    def check(self, targets, result):
        require = oracle().require
        n, targets = self.n, tuple(targets)
        eligible = tuple(width_targets(n, targets)["eligible_triples"])
        audit = result["search_audit"]
        require(not audit["interface_cache_hit"], "duplicate whole-table cache unexpectedly available")
        attempts, remembered, delivered = [], [], set()
        extra = Counter()
        bound, best, first_rank = 8, None, None
        rank_work = {} if self.arm == "lex" else dict.fromkeys(COFACTOR_FIELDS if self.arm == "cofactor" else RANK_FIELDS, 0)

        def trial(group, source):
            nonlocal bound, best, first_rank
            seen, columns = set(), 0
            for response in dense_responses(n, targets, group):
                seen.add(response)
                columns += 1
                if len(seen) > bound:
                    break
            exact = len(seen) if len(seen) <= bound else 0
            attempts.append([*group, bound, exact, columns, source])
            if source == 0:
                extra["order_remembered_trials"] += 1
            if not exact:
                return False
            best = dict(triple=group, classes=exact, width=(exact - 1).bit_length())
            first_rank = len(attempts)
            if source == 0:
                extra["order_remembered_incumbents"] += 1
            if best["width"] == 1:
                if source == 0:
                    extra["order_remembered_minimum_hits"] += 1
                return True
            bound = 1 << (best["width"] - 1)
            return False

        stopped = False
        for truth in targets:
            group = self.memory.get(truth)
            if group is None:
                continue
            extra["order_remembered_outputs_seen"] += 1
            if group in delivered or group not in eligible:
                continue
            extra["order_remembered_eligible"] += 1
            remembered.append(list(group))
            delivered.add(group)
            if trial(group, 0):
                stopped = True
                break
        called = not stopped and self.arm != "lex"
        if not stopped:
            if self.arm == "cofactor":
                priorities = sorted((len({dense_responses(n, targets, g)[i] for i in (0, 1, 2, 4)}), g) for g in eligible)
                order = [g for _, g in priorities]
                rank_work.update(fixed_order_calls=1, fixed_candidates=len(eligible),
                                 fixed_layout_builds=0 if self.layout_seen else len(eligible),
                                 fixed_packed_shifts=4 * len(eligible), fixed_packed_masks=4 * len(eligible),
                                 fixed_response_keys=4 * len(eligible))
                self.layout_seen = True
            elif self.arm == "lex":
                order = eligible
            else:
                channel, gate = self.model["channel"], self.model["min_eligible"]
                rank_work["orders"] = 1
                if channel == "lexical" or len(eligible) < max(2, gate):
                    order = eligible
                    rank_work["lexical_returns"] = 1
                else:
                    proposed, units, detail = choose_candidate(n, targets, channel,
                                                               tuple(tuple(s) for s in self.model["shape_priority"]), eligible, True)
                    order = eligible if proposed is None else (proposed, *(g for g in eligible if g != proposed))
                    rank_work.update(detail)
                    rank_work.update(feature_calls=1, axis_profiles=n, axis_normalizations=n,
                                     axis_masks_built=0 if self.layout_seen else n,
                                     layouts_built=int(not self.layout_seen), layout_cache_hits=int(self.layout_seen),
                                     packed_shifts=2 * n, packed_xors=4 * n + 1 if channel == "transitions" else 2 * n,
                                     packed_ands={"marginals": 2, "joint": 3, "transitions": 6}[channel] * n,
                                     packed_popcounts={"marginals": 2, "joint": 3, "transitions": 6}[channel] * n,
                                     estimated_feature_units=units,
                                     promotions=int(proposed is not None and proposed != eligible[0]),
                                     lexical_returns=int(proposed is None or proposed == eligible[0]))
                    self.layout_seen = True
            for group in order:
                extra["order_received_proposals"] += 1
                if group in delivered:
                    extra["order_memory_duplicates_skipped"] += 1
                    continue
                delivered.add(group)
                if trial(group, 1):
                    stopped = True
                    break
        require(audit["attempts"] == attempts, "rank/cache/failed-bound trace differs from independent replay")
        require(best is not None and tuple(result["triple"]) == best["triple"] and
                result["class_count"] == best["classes"] and result["width"] == best["width"], "selected ranked cut")
        require(audit["ranking_called"] == called and audit["first_minimum_rank"] == first_rank,
                "ranking call/rank metadata")
        require(audit["remembered_candidates"] == remembered and audit["memory_enabled"], "public cache proposals")
        require(audit["eligible_count"] == len(eligible) and audit["candidates_considered"] == len(attempts), "eligible/attempt denominator")
        require(audit["stopped_at_minimum_one"] == (best["width"] == 1) and
                audit["full_eligible_covered"] == (len(attempts) == len(eligible)), "proof/first-hit boundary")
        require(best["width"] == 1 or len(attempts) == len(eligible), "premature two-bit success")
        require(result["ranking_work"] == rank_work, "rank feature/cache/work ledger")
        for truth in targets:
            self.memory[truth] = best["triple"]
        require(audit["remembered_output_columns"] == len(self.memory), "public cache size/update")
        w = result["work"]
        exact = sum(a[4] > 0 for a in attempts)
        columns = sum(a[5] for a in attempts)
        expected = dict(tasks=1, input_rows_received=2 << n, eligible_group_count=len(eligible), support_bit_tests=2 * n,
                        group_trials=len(attempts), groups_requested=len(attempts), group_failures=len(attempts)-exact,
                        group_incumbents=exact, group_bound_rejections=len(attempts)-exact,
                        residual_joint_rows=columns, residual_packed_shifts=columns-len(attempts),
                        residual_packed_masks=columns, residual_row_equivalents=columns*(1 << (n-2)),
                        joint_class_lookups=columns, residual_pairs_unpacked=sum(a[4] for a in attempts),
                        order_attempts=len(attempts), order_exact_group_counts=exact,
                        order_truncated_group_checks=len(attempts)-exact, order_memory_updates=2,
                        order_ranker_calls=int(called), order_ranker_candidates_supplied=len(eligible)*int(called),
                        order_interface_hits=0, order_duplicate_proposals=0, order_lex_completion_proposals=0)
        expected.update({k:extra.get(k,0) for k in ("order_received_proposals", "order_memory_duplicates_skipped",
                         "order_remembered_outputs_seen", "order_remembered_eligible", "order_remembered_trials",
                         "order_remembered_incumbents", "order_remembered_minimum_hits")})
        for key, value in expected.items():
            require(w[key] == value, "search counter " + key)
        require(w["group_layout_builds"] + w["group_layout_hits"] == len(attempts) + 1, "layout work")
        require(w["physical_output_comparisons"] == 2 and w["physical_output_bits_checked"] == 2 << n and
                w["physical_cut_resets"] == 1, "two-output physical verification/reset")
        require(w["NAND_gates_appended"] == w["physical_reachable_gates"] + w["physical_pruned_gates"] and
                w["physical_reachable_gates"] == len(result["circuit"]["gates"]), "physical gate/pruning ledger")
        require(result["fold_uses"] == 0, "primitive builder unexpectedly uses supplied fold")
        require(audit["ranking_cpu_ns"] == (audit["ordering_prepare_cpu_ns"] if called else 0), "ranking timing scope")
        return dict(attempts=len(attempts), columns=columns, first_rank=first_rank, memory_trials=sum(a[-1]==0 for a in attempts))


def read(path):
    return json.loads(Path(path).read_bytes())


def check_bindings(out):
    require, digest = oracle().require, oracle().digest
    design, train, held = (read(out/name) for name in ("design.json", "train-receipt.json", "held-bound.json"))
    for name, value in design["sources"].items():
        require(digest(ROOT/name) == value, "changed source " + name)
    for name, value in train["files"].items():
        require(digest(out/name) == value, "changed training file " + name)
    for name in ("held.json", "held-grades.json", "model.json", "design.json", "train-receipt.json"):
        require(digest(out/name) == held[name], "changed released file " + name)
    require(datetime.fromisoformat(design["frozen_utc"]) < datetime.fromisoformat(train["started"]) <
            datetime.fromisoformat(train["frozen_utc"]) < datetime.fromisoformat(held["test_opened_utc"]) <=
            datetime.fromisoformat(held["sealed_utc"]), "freeze/exposure chronology")
    attempts = [json.loads(l) for l in (out/"fit-attempts.jsonl").read_text().splitlines()]
    require(len(attempts) == train["attempts"] and attempts[-1]["status"] == "ok" and
            all(a["status"] == "failed" for a in attempts[:-1]), "fit attempts")
    require(sum(a["cpu_ns"] for a in attempts) == train["cpu_ns"] and
            sum(a["wall_ns"] for a in attempts) == train["wall_ns"], "failed fit costs omitted")
    require(attempts[-1]["phases"] == train["phases"] and
            sum(p["cpu_ns"] for p in train["phases"].values()) <= attempts[-1]["cpu_ns"], "training phase charges")
    require(train["model_sha256"] == digest(out/"model.json"), "model file digest")
    return design, train, held


PHYSICAL_FIELDS = ("status", "n", "triple", "class_count", "width", "summary_wires", "circuit", "assignment_classes",
                   "assignment_codes", "class_codes", "summary_truths", "truth", "expanded_NANDs", "summary_wires_by_output")


def metric(task, raw, cert, grade):
    result = raw["result"] or {}
    trace, work = result.get("search_audit", {}), result.get("work", {})
    attempts = trace.get("attempts", [])
    rank = trace.get("first_minimum_rank")
    exact = raw["failure"] is None and cert is not None
    c = Counter(tasks=1, exact=int(exact), width1=int(cert is not None and cert["width"]==1),
                width2=int(cert is not None and cert["width"]==2),
                table_rows=cert["verified_assignments"] if exact else 0,
                output_bits=cert["verified_output_bits"] if exact else 0,
                gates=cert["gates"] if exact else 0, shared_gates=cert["shared_gates"] if exact else 0,
                trials=len(attempts) if trace else work.get("triple_trials",work.get("group_trials",0)),
                best_possible_trials=1 if grade["width"]==1 else len(width_targets(task["n"],tuple(task["outputs"]))["eligible_triples"]),
                first_rank_sum=rank or 0, rank_observed=int(rank is not None), first_is_best=int(rank==1),
                ordering_prepare_cpu_ns=trace.get("ordering_prepare_cpu_ns",0), ranking_cpu_ns=trace.get("ranking_cpu_ns",0),
                policy_called=int(bool(trace.get("ranking_called"))), cached_proposals=sum(a[-1]==0 for a in attempts),
                exact_columns_read=sum(a[5] for a in attempts), failed_bound_checks=sum(a[4]==0 for a in attempts),
                chosen_planted=int(exact and sorted(result["triple"])==sorted(grade["triple"])))
    for key in ("cpu_ns","wall_ns","init_cpu_ns","synth_cpu_ns","verify_cpu_ns","verify_wall_ns","return_bytes"):
        c[key] = oracle().integer(raw[key], key)
    oracle().require(c["cpu_ns"] >= c["init_cpu_ns"]+c["synth_cpu_ns"]+c["verify_cpu_ns"], "component CPU exceeds charged row")
    oracle().require(c["ranking_cpu_ns"] <= c["synth_cpu_ns"], "ranking timer exceeds paid synthesis")
    return c


def payment(curve, reference, fee, completed_pairs):
    gaps = [a+fee-b for a,b in zip(curve,reference,strict=True)]
    hits = [i for i in range(1,len(gaps)) if gaps[i]<=0]
    positive = [i for i in range(1,len(gaps)) if gaps[i]>0]
    first = hits[0] if hits else None
    durable = max(positive, default=0)+1
    return dict(gap_ns=gaps[-1],first_break_even=first,
                first_break_even_completed_pairs=completed_pairs[first] if first else None,
                sustained_break_even=durable if durable<len(gaps) else None,cumulative_gap_ns=gaps)


def audit(out):
    require, digest, canonical = oracle().require, oracle().digest, oracle().canonical
    design, train, held_seal = check_bindings(out)
    training, training_grades, held, grades = (read(out/name) for name in
        ("train.json","train-grades.json","held.json","held-grades.json"))
    fit = replay_fit(training,training_grades)
    diagnostics, model = read(out/"fit-diagnostics.json"), read(out/"model.json")
    require(fit["model"]==model and fit["model_body_sha256"]==diagnostics["model_sha256"], "fitted checkpoint")
    for key in ("fit_score","fixed_score","candidates","shape_fit","training_tasks","early_stop_tasks","minimum_triple_labels","candidate_count"):
        require(fit[key]==diagnostics[key], "fit replay " + key)
    train_panel=check_panel("train",training,training_grades)
    held_panel=check_panel("test",held,grades)
    require(not set(train_panel["raw_families"])&set(held_panel["raw_families"]) and
            not set(train_panel["consumer_families"])&set(held_panel["consumer_families"]), "cross-split family leakage")
    previous=ROOT/"artifacts/FOLD-TWO-OUTPUT-20261115-001/FOLD-TWO-OUTPUT-20261115-001-E001_joint_tables"
    archive_keys, archive_structures=set(),set()
    previous_grades=read(previous/"grades.json")
    for panel in ("primary","sensitivity"):
        for row in read(previous/(panel+".json")):
            if row["n"] in (7,8,9):
                archive_keys.add(raw_family(row["n"],tuple(row["outputs"])))
                g=previous_grades[panel][row["id"]]
                if g["kind"]=="shared": archive_structures.add(consumer_family(row["n"],g["logical_consumers"]))
    require(not (set(train_panel["raw_families"]+held_panel["raw_families"])&archive_keys) and
            not (set(train_panel["consumer_families"]+held_panel["consumer_families"])&archive_structures), "predecessor example leakage")
    models={"learned":model,"fixed":dict(version="axis-transitions-v1",channel="joint",min_eligible=4,shape_priority=[]),
            "transitions":dict(version="axis-transitions-v1",channel="transitions",min_eligible=4,shape_priority=[])}
    counts=defaultdict(dict);cells=defaultdict(list);work_runs=defaultdict(list);curves=defaultdict(list);ranks=defaultdict(list)
    identities={}; failures=[]; physical_cache={}; totals=Counter(); stream_digests={}
    pair_counts=[0]; seen_pairs=set()
    for task in held:
        pair=grades[task["id"]]["pair"]
        pair_counts.append(pair_counts[-1]+int(pair in seen_pairs));seen_pairs.add(pair)
    events=[json.loads(l) for l in (out/"results.jsonl").read_text().splitlines()]
    for event in events:
        require(event["status"]=="ok", "unresolved deployed worker failure")
        saved=event["result"];arm,rep=saved["arm"],saved["repeat"]
        require(arm in METHODS and 0<=rep<10 and rep not in counts[arm], "unknown/duplicate stream")
        require(saved["cpu"]==design["cpu"] and saved["sha256"]==digest(out/saved["file"]), "worker CPU/hash")
        stream_digests[saved["file"]]=saved["sha256"]
        with gzip.open(out/saved["file"],"rt") as f: rows=[json.loads(l) for l in f]
        require(len(rows)==len(held)==saved["tasks"], "incomplete deployment")
        total,operations=Counter(),Counter();by=defaultdict(Counter);rank_values=defaultdict(list)
        seen_outputs=set();states={};fingerprint_rows=[];curve=[saved["startup_cpu_ns"]]
        for task,raw in zip(held,rows,strict=True):
            require(task["id"]==raw["id"], "held task ordering")
            n,targets=task["n"],tuple(task["outputs"]);result=raw["result"]
            cert=None
            if raw["failure"] is None:
                key=canonical([n,targets,{k:result[k] for k in PHYSICAL_FIELDS if k in result}])
                if key not in physical_cache:
                    physical_cache[key]=oracle().verify_result(n,targets,result)
                    totals.update(unique_physical_programs=1,executed_scalar_rows=1<<n,
                                  executed_scalar_output_bits=2<<n,
                                  executed_scalar_NANDs=physical_cache[key][1]["scalar_NAND_evaluations"])
                cert,info=physical_cache[key]
                require(raw["certificate"]==cert, "paid checker differs from scalar physical/cut audit")
                if arm in ("reference","prior-generic"):
                    oracle().verify_work(n,targets,result)
                else:
                    if n not in states: states[n]=TraceReplay(n,arm,models.get(arm))
                    states[n].check(targets,result)
                public_return={**{k:result[k] for k in ("n","triple","class_count","width","summary_wires")},
                               "circuit":{k:result["circuit"][k] for k in ("gates","outputs")}}
                require(len(canonical(public_return))==raw["return_bytes"], "returned physical-byte count")
                totals.update(covered_program_returns=1,covered_return_assignments=1<<n,covered_output_bits=2<<n)
            else:
                failures.append([event["case"],task["id"],raw["failure"]])
            grade=grades[task["id"]]
            m=metric(task,raw,cert,grade);total.update(m)
            seen_output=any((n,t) in seen_outputs for t in targets)
            seen_outputs.update((n,t) for t in targets)
            for label in (grade["kind"],str(n),grade["operation"],"seen_output" if seen_output else "new_outputs",
                          grade["kind"]+("-seen" if seen_output else "-new")):
                by[label].update(m)
            if m["rank_observed"]:rank_values[grade["kind"]].append(m["first_rank_sum"])
            operations.update({k:v for k,v in result.get("work",{}).items() if type(v)is int})
            operations.update({"rank_"+k:v for k,v in (result.get("ranking_work") or {}).items() if type(v)is int})
            curve.append(curve[-1]+m["cpu_ns"])
            fingerprint_rows.append([result.get(k) for k in ("triple","summary_wires","circuit","width")])
        ident=canonical(fingerprint_rows)
        require(arm not in identities or identities[arm]==ident, "deterministic programs changed across repeats")
        identities[arm]=ident
        total.update(startup_cpu_ns=saved["startup_cpu_ns"],startup_wall_ns=saved["startup_wall_ns"],
                     deployment_cpu_ns=curve[-1],deployment_wall_ns=saved["startup_wall_ns"]+total["wall_ns"])
        counts[arm][rep]=total;cells[arm].append(by);work_runs[arm].append(operations);curves[arm].append(curve);ranks[arm].append(rank_values)
    methods,prefix={},{}
    for arm in METHODS:
        require(set(counts[arm])==set(range(10)), "missing scheduled stream " + arm)
        ordered=[counts[arm][i] for i in range(10)]
        m=methods[arm]=oracle().median_fields(ordered)
        m["groups"]={k:oracle().median_fields([r[k] for r in cells[arm]]) for k in cells[arm][0]}
        m["rank_median"]={k:median(v) for k,v in ranks[arm][0].items() if v}
        m["work"]=oracle().median_fields(work_runs[arm])
        m["cpu_repeats_ns"]=[r["deployment_cpu_ns"] for r in ordered]
        m["wall_repeats_ns"]=[r["deployment_wall_ns"] for r in ordered]
        m["paid_cpu_ns"]=m["deployment_cpu_ns"]+(train["cpu_ns"] if arm=="learned" else 0)
        m["paid_wall_ns"]=m["deployment_wall_ns"]+(train["wall_ns"] if arm=="learned" else 0)
        prefix[arm]=[median(v) for v in zip(*curves[arm],strict=True)]
    benchmark=min((a for a in METHODS if a!="learned"),key=lambda a:methods[a]["paid_cpu_ns"])
    learner=methods["learned"];comparisons={}
    for arm,m in methods.items():
        if arm=="learned":continue
        comparisons[arm]=dict(paid_cpu_gap_ns=learner["paid_cpu_ns"]-m["paid_cpu_ns"],
                              paid_wall_gap_ns=learner["paid_wall_ns"]-m["paid_wall_ns"],paid_cpu_ratio=learner["paid_cpu_ns"]/m["paid_cpu_ns"],
                              paid_wins=sum(x+train["cpu_ns"]<y for x,y in zip(learner["cpu_repeats_ns"],m["cpu_repeats_ns"],strict=True)),
                              deployment_wins=sum(x<y for x,y in zip(learner["cpu_repeats_ns"],m["cpu_repeats_ns"],strict=True)),
                              deployment_cpu_gap_ns=learner["deployment_cpu_ns"]-m["deployment_cpu_ns"],fewer_exact_trials=m["trials"]-learner["trials"])
    label_cost=read(out/"label-cost.json")
    require(label_cost["exact"] and label_cost["train_sha256"]==digest(out/"train.json") and label_cost["labels"]==
            sum(len(width_targets(t["n"],tuple(t["outputs"]))["eligible_triples"]) for t in training), "label sensitivity binding/count")
    checker_path="experiments/FOLD-TWO-OUTPUT-20261115-001/FOLD-TWO-OUTPUT-20261115-001-E001_joint_tables/checker.py"
    require(label_cost["source_sha256"]==design["sources"][checker_path]==digest(ROOT/checker_path), "timed label checker source")
    fees=dict(fully_paid=train["cpu_ns"],frozen_policy_available=0,
              labelled_training_available=train["cpu_ns"]-train["phases"]["training_tasks_and_labels"]["cpu_ns"])
    fees["raw_training_tables_available"]=fees["labelled_training_available"]+label_cost["cpu_ns"]
    trajectories={name:payment(prefix["learned"],prefix[benchmark],fee,pair_counts) for name,fee in fees.items()}
    gate=not failures and comparisons[benchmark]["paid_cpu_gap_ns"]<0 and comparisons[benchmark]["paid_wins"]>=8
    official=read(out/"result.json")
    for key,value in dict(methods=methods,benchmark=benchmark,comparisons=comparisons,sensitivity_fees=fees,
                          trajectories=trajectories,meets_paid_criterion=gate,failures=failures).items():
        require(canonical(official[key])==canonical(value), "assessor arithmetic " + key)
    require(official["observed_programs"]==totals["covered_program_returns"]+len(failures) and
            official["checked_assignments"]==totals["covered_return_assignments"] and
            official["checked_output_bits"]==totals["covered_output_bits"], "physical coverage summary")
    return dict(schema_version=1,ticket=TICKET,verdict="PASS",auditor_sha256=digest(__file__),
                terminal_oracle_sha256=ORACLE_SHA256,design_sha256=digest(out/"design.json"),model_sha256=digest(out/"model.json"),
                result_sha256=digest(out/"result.json"),streams=stream_digests,
                independence="Literal scalar supervision/features and NAND replay; exhaustive triple-priority verification; no producer imports or timed solver reruns.",
                fit={k:v for k,v in fit.items() if k not in ("candidates","shape_fit")},
                split={"train":train_panel,"held":held_panel,"disjoint_from_each_other_and_predecessor":True},
                replay=dict(totals),physical_factoring="Every physical assertion field and target table must match byte-for-byte before a prior scalar execution is reused; every receipt and trace is still checked.",
                benchmark=benchmark,meets_paid_criterion=gate,comparisons=comparisons,methods=methods,
                sensitivity_fees=fees,trajectories=trajectories,failures=failures,
                nonclaims=["Full Boolean truth tables and triple size are supplied; this is bounded ranking and synthesis.",
                           "The min_eligible gate35 is observationally identical to gates4/10/20 on the declared n7-9 population.",
                           "Width two still requires exclusion of every eligible width-one cut.",
                           "Timing repeats reuse the same96 matched held pairs, not new scientific tasks.",
                           "Estimated fitting units are a selection proxy; reported process CPU includes all host overhead."])


def scan_trace(n, targets, supplied_order):
    """Independent first-hit/minimum-width schedule for the sharing backend.

    This intentionally distinguishes a priority from its necessary proof.
    A first width-two witness does not permit stopping.  After any incumbent
    only strictly narrower alternatives can improve the objective.
    """
    require = oracle().require
    truth = tuple(targets)
    facts = width_targets(n, truth)
    order = tuple(tuple(sorted(g)) for g in supplied_order)
    require(len(order) == len(set(order)) and set(order) == set(facts["eligible_triples"]),
            "ranking omits/repeats an eligible triple")
    bound, incumbent = 8, None
    attempts = []
    for group in order:
        seen, probes, accepted = set(), 0, True
        for response in dense_responses(n, truth, group):
            seen.add(response)
            probes += 1
            if len(seen) > bound:
                accepted = False
                break
        attempts.append(dict(triple=group, bound=bound, response_probes=probes,
                             observed_classes=len(seen), accepted=accepted))
        if not accepted:
            continue
        width = (len(seen) - 1).bit_length()
        incumbent = dict(triple=group, width=width, classes=len(seen))
        if width == 1:
            break
        bound = 1 << (width - 1)
    require(incumbent is not None and incumbent["width"] == facts["minimum_width"],
            "scan failed to establish global minimum")
    require(incumbent["width"] == 1 or len(attempts) == len(order),
            "two-bit answer without complete exclusion of one-bit cuts")
    return dict(selected=incumbent, attempts=attempts,
                group_trials=len(attempts), failed_trials=sum(not a["accepted"] for a in attempts),
                residual_probes=sum(a["response_probes"] for a in attempts))


def self_test():
    base = oracle().self_test()
    positive, negative = [0, 0], [0, 0]
    for raw in range(32):
        a, b, c, d, e = [(raw >> j) & 1 for j in range(5)]
        q = (a & b) ^ c ^ d
        positive[0] |= q << raw
        positive[1] |= (q ^ e) << raw
        negative[0] |= q << raw
        negative[1] |= (q ^ a ^ e) << raw
    pos = width_targets(5, tuple(positive))
    require = oracle().require
    require(len(pos["minimizing_triples"]) == 2, "lost tied supervision labels")
    fast = scan_trace(5, positive, pos["eligible_triples"])
    slow = scan_trace(5, positive, list(reversed(pos["eligible_triples"])))
    require(fast["group_trials"] < slow["group_trials"], "ordering positive control")
    neg = width_targets(5, tuple(negative))
    for order in (neg["eligible_triples"], list(reversed(neg["eligible_triples"]))):
        result = scan_trace(5, negative, order)
        require(result["group_trials"] == len(order) and result["selected"]["width"] == 2,
                "rewired premature stop")
    malformed = pos["eligible_triples"][:-1]
    try:
        scan_trace(5, positive, malformed)
    except ValueError:
        pass
    else:
        raise AssertionError("incomplete ranking accepted")
    local = sum(((((raw & 1) & ((raw >> 1) & 1)) ^ ((raw >> 2) & 1))) << raw for raw in range(8))
    buckets, _ = features(3, (local, local), "transitions")
    require(buckets == (((0, 2), (1, 2), (2, 4)),) and influence_shape((2, 2, 4)) == (1, 1, 2),
            "scalar transition profiles and empirical influence shape")
    chosen, _ = choose_candidate(3, (local, local), "transitions", ((1, 1, 2),))
    require(chosen == (0, 1, 2), "shape proposal")
    return dict(terminal_physical_fixtures=base, tied_supervision_targets=2,
                positive_fast_trials=fast["group_trials"], positive_slow_trials=slow["group_trials"],
                negative_requires_every_eligible_triple=len(neg["eligible_triples"]),
                scalar_transition_shape=[1, 1, 2],
                malformed_order_rejected=True)


if __name__ == "__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--artifacts", type=Path, default=DEFAULT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report=self_test() if args.self_test else audit(args.artifacts.resolve())
    if args.output:
        oracle().require(args.output.resolve()==DEFAULT/"audit.json", "output outside owned receipt")
        args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report if args.self_test else {k:report[k] for k in
                     ("verdict","replay","benchmark","meets_paid_criterion","comparisons","sensitivity_fees")}, indent=2, sort_keys=True))
