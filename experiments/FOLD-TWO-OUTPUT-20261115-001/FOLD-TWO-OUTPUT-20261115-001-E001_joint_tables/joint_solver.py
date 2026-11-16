"""Synthesize a jointly sufficient, minimum-width local interface from two tables.

Each group's eight local assignments induce pairs of residual truth tables.
Equal codewords must have equal pairs. This condition is checked before
building the two Boolean quotients. The physical builder uses one shared
NAND/semantic cache for both consumers, with its visible wires reset at the
chosen cut. Program size is heuristic; interface width is exact.
"""

from collections import Counter
from itertools import combinations, permutations
from math import comb
from time import perf_counter, process_time_ns
from typing import NamedTuple


SOURCE_DEPENDENCIES = ()
PINS = (170, 204, 240)
OPS = ("AND", "OR", "XOR")
DEFAULT_ENTRY = {
    "truth": 106,
    "expr": ("XOR", ("input", 0), ("AND", ("input", 1), ("input", 2))),
    "dag": {"gates": ((1, 2), (5, 5), (0, 6), (0, 7), (6, 7), (8, 9)), "output": 10},
}
COUNTERS = (
    "tasks", "input_rows_received", "eligible_group_count", "groups_requested", "group_trials",
    "group_failures", "group_bound_rejections", "group_incumbents", "group_cache_hits",
    "group_layout_builds", "group_layout_hits", "group_axis_masks", "support_bit_tests",
    "joint_tables_joined", "residual_joint_rows", "residual_packed_shifts", "residual_packed_masks",
    "residual_row_equivalents", "residual_pairs_unpacked",
    "joint_class_lookups", "fold_group_witnesses", "fold_group_hypotheses", "fold_group_rejections",
    "fold_residual_comparisons", "fold_group_hits", "fold_no_witness_matching_entry",
    "code_candidates", "code_rejections", "code_cache_hits", "individual_partition_lookups",
    "direct_projection_codes", "general_code_searches", "cheap_split_code_trials",
    "quotient_projection_tests", "quotient_code_blocks", "residual_compactions",
    "residual_compaction_hits", "compaction_packed_steps", "semantic_recipe_requests",
    "semantic_recipe_hits", "semantic_recipe_builds", "synthesis_axis_tests", "synthesis_pair_tests",
    "synthesis_pair_rejections", "synthesis_packed_cofactors", "synthesis_shannon_nodes",
    "synthesis_pair_contractions", "synthesis_leaf_factor_nodes", "NAND_requests",
    "NAND_structural_hits", "NAND_semantic_hits", "NAND_gates_appended", "packed_NAND_evaluations",
    "named_fold_applications", "flat_fold_applications", "fold_encoder_wires", "physical_cut_resets",
    "physical_constructor_requests", "physical_constructor_hits", "physical_reachable_gates",
    "physical_pruned_gates", "physical_output_comparisons", "physical_output_bits_checked",
    "entry_validation_rows", "entry_physical_validation_NANDs", "entry_permutations",
    "entry_recipes_validated", "semantic_axis_mask_builds", "sparse_compaction_mask_builds",
)


def _binary(op, a, b):
    if op == "AND":
        return a & b
    if op == "OR":
        return a | b
    return a ^ b


def _tree(node):
    if not isinstance(node, (tuple, list)) or not node:
        raise ValueError("invalid template AST")
    if node[0] == "input" and len(node) == 2 and type(node[1]) is int and 0 <= node[1] < 3:
        return ("input", node[1])
    if node[0] in OPS and len(node) == 3:
        return (node[0], _tree(node[1]), _tree(node[2]))
    raise ValueError("template AST requires binary AND, OR or XOR and three local pins")


def _tree_value(node, args, apply):
    if node[0] == "input":
        return args[node[1]]
    return apply(node[0], _tree_value(node[1], args, apply), _tree_value(node[2], args, apply))


def _validate_gate_dag(dag, truth, work):
    wires = [*PINS, 0, 255]
    gates = []
    for pair in dag["gates"]:
        if len(pair) != 2 or any(type(w) is not int or not 0 <= w < len(wires) for w in pair):
            raise ValueError("invalid physical entry gate")
        a, b = pair
        gates.append((a, b))
        wires.append(255 ^ (wires[a] & wires[b]))
    out = dag["output"]
    if type(out) is not int or not 0 <= out < len(wires) or wires[out] != truth:
        raise ValueError("entry gate program disagrees with the public byte")
    work["entry_physical_validation_NANDs"] += len(gates)
    return tuple(gates), out


class _Recipe(NamedTuple):
    cost: int
    op: str
    args: tuple


class _Physical:
    """Only wires obtainable through the cut participate in consumer semantic CSE."""

    def __init__(self, solver):
        self.solver = solver
        self.n, self.full, self.work = solver.n, solver.full, solver._work
        self.values = [*solver.columns, 0, self.full]
        self.gates = []
        self.structural = {}
        self.semantic = {value: wire for wire, value in enumerate(self.values)}
        self.instances = {}

    def nand(self, a, b):
        self.work["NAND_requests"] += 1
        key = (a, b) if a <= b else (b, a)
        wire = self.structural.get(key)
        if wire is None:
            value = self.full ^ (self.values[a] & self.values[b])
            self.work["packed_NAND_evaluations"] += 1
            wire = self.semantic.get(value)
            if wire is None:
                wire = len(self.values)
                self.values.append(value)
                self.gates.append(key)
                self.work["NAND_gates_appended"] += 1
            else:
                self.work["NAND_semantic_hits"] += 1
            self.structural[key] = wire
        else:
            self.work["NAND_structural_hits"] += 1
        self.semantic[self.values[wire]] = wire
        return wire

    def binary(self, op, a, b):
        if op == "AND":
            h = self.nand(a, b)
            return self.nand(h, h)
        if op == "OR":
            return self.nand(self.nand(a, a), self.nand(b, b))
        h = self.nand(a, b)
        return self.nand(self.nand(a, h), self.nand(b, h))

    def enter_cut(self, outside, taps):
        # A previously equivalent internal wire may read the hidden group.
        # Even structural entries may point to a semantic alias. Start fresh
        # with the precise allowed sources, then share freely across outputs.
        self.structural = {}
        self.instances = {}
        self.semantic = {self.values[w]: w for w in (*outside, *taps, self.n, self.n + 1)}
        self.work["physical_cut_resets"] += 1

    def template(self, order, group):
        args = tuple(group[i] for i in order)
        if self.solver.arm == "flat":
            self.work["flat_fold_applications"] += 1
            result = _tree_value(self.solver.entry_expr, args, self.binary)
        else:
            self.work["named_fold_applications"] += 1
            gates, out = self.solver.entry_dag
            local = [*args, self.n, self.n + 1]
            for a, b in gates:
                local.append(self.nand(local[a], local[b]))
            result = local[out]
        self.work["fold_encoder_wires"] += 1
        return result

    def build(self, plan, wires):
        key = (plan, wires)
        self.work["physical_constructor_requests"] += 1
        existing = self.instances.get(key)
        if existing is not None:
            self.work["physical_constructor_hits"] += 1
            return existing
        op, args = plan.op, plan.args
        if op == "literal":
            axis, inverse = args
            w = wires[axis]
            result = self.nand(w, w) if inverse else w
        elif op == "const":
            result = self.n + args[0]
        elif op == "pair":
            i, j, primitive, child = args
            v = self.binary(primitive, wires[i], wires[j])
            quotient = tuple(v if p == i else x for p, x in enumerate(wires) if p != j)
            result = self.build(child, quotient)
        else:
            axis, *tail = args
            rest = wires[:axis] + wires[axis + 1:]
            if op == "drop":
                result = self.build(tail[0], rest)
            elif op == "mux":
                x = wires[axis]
                low, high = (self.build(child, rest) for child in tail)
                low_branch = self.nand(self.nand(x, x), low)
                result = self.nand(low_branch, self.nand(x, high))
            else:
                inverted, child = tail
                x = wires[axis]
                if inverted:
                    x = self.nand(x, x)
                result = self.binary(op, x, self.build(child, rest))
        self.instances[key] = result
        return result

    def finish(self, ends, taps):
        start = self.n + 2

        def reach(wire, stop):
            pending, seen = [wire], set()
            while pending:
                wire = pending.pop()
                if wire not in seen:
                    seen.add(wire)
                    if wire >= start and wire not in stop:
                        pending.extend(self.gates[wire - start])
            return seen

        tapset = set(taps)
        cut = [reach(w, tapset) for w in ends]
        reaches = [reach(w, ()) for w in ends]
        active = sorted(w for w in reaches[0] | reaches[1] if w >= start)
        remap = {w: w for w in range(start)}
        gates = []
        for w in active:
            a, b = self.gates[w - start]
            remap[w] = start + len(gates)
            gates.append([remap[a], remap[b]])
        if any(w not in remap for w in taps):
            raise AssertionError("unused minimal interface bit")
        self.work["physical_reachable_gates"] += len(gates)
        self.work["physical_pruned_gates"] += len(self.gates) - len(gates)
        cuts = [[remap[w] for w in taps if w in seen] for seen in cut]
        fanouts = [sum(int(w == a) + int(w == b) for a, b in gates) +
                   sum(w == remap[end] for end in ends) for w in (remap[t] for t in taps)]
        return ({"n": self.n, "gates": gates, "outputs": [remap[w] for w in ends]},
                [remap[w] for w in taps], cuts, fanouts,
                sum(w >= start for w in reaches[0] & reaches[1]))


class JointSolver:
    """A separate arm-local cache for an n-input stream of public table pairs."""

    def __init__(self, n, arm="primitive", entry=None, fold_dag=None):
        wall, cpu = perf_counter(), process_time_ns()
        if type(n) is not int or n < 3:
            raise ValueError("joint triple search requires at least three inputs")
        if arm not in ("primitive", "named", "flat"):
            raise ValueError("unknown joint solver arm")
        if arm == "primitive" and (entry is not None or fold_dag is not None):
            raise ValueError("the primitive comparator takes no supplied entry")
        self.n, self.arm, self.rows = n, arm, 1 << n
        self.full = (1 << self.rows) - 1
        self._work = Counter(dict.fromkeys(COUNTERS, 0))
        self.zero = tuple(self.full // ((1 << (1 << j)) + 1) for j in range(n))
        self.columns = tuple(self.full ^ mask for mask in self.zero)
        self._work["group_axis_masks"] += n
        self._axis = {(n, j): zero for j, zero in enumerate(self.zero)}
        self._layouts, self._interfaces, self._codes, self._recipes = {}, {}, {}, {}
        self._compact_masks = {}
        self.entry_expr = self.entry_dag = None
        self.orientations, self.witness = {}, {}
        if arm != "primitive":
            entry = DEFAULT_ENTRY if entry is None else entry
            truth = entry["truth"]
            self.entry_expr = _tree(entry["expr"])
            if type(truth) is not int or not 0 <= truth < 256 or _tree_value(self.entry_expr, PINS, _binary) != truth:
                raise ValueError("entry AST disagrees with its three-input truth table")
            if any(not ((truth ^ (truth >> (1 << i))) & (255 ^ value)) for i, value in enumerate(PINS)):
                raise ValueError("entry must essentially depend on all three pins")
            self._work["entry_recipes_validated"] += 1
            self._work["entry_validation_rows"] += 8
            if arm == "named":
                self.entry_dag = _validate_gate_dag(fold_dag if fold_dag is not None else entry["dag"],
                                                    truth, self._work)
            for order in permutations(range(3)):
                oriented = _tree_value(self.entry_expr, tuple(PINS[i] for i in order), _binary)
                self.orientations.setdefault(oriented, order)
            for oriented in sorted(self.orientations):
                canonical = oriented ^ (255 if oriented & 1 else 0)
                signature = sum(((canonical >> (1 << i)) & 1) << i for i in range(3))
                pivot = (canonical & -canonical).bit_length() - 1
                # The witness already certifies row zero and every singleton
                # whose residual equaled that of row zero. The pivot supplies
                # the other residual, so only the remaining rows need testing.
                known = {0, pivot, *(1 << i for i in range(3) if not (signature >> i) & 1)}
                checks = tuple((row, (canonical >> row) & 1) for row in range(8) if row not in known)
                self.witness.setdefault(signature, []).append((canonical, oriented, pivot, checks))
            self._work["entry_permutations"] += 6
        self.setup_cpu_ns = process_time_ns() - cpu
        self.setup_seconds = perf_counter() - wall
        self._setup_work = self.work_counters()
        self._setup_record = {"cpu_ns": self.setup_cpu_ns, "seconds": self.setup_seconds,
                              "work": self._setup_work.copy()}
        self._total_cpu_ns = self._total_seconds = 0

    def work_counters(self):
        return dict(self._work)

    def ledger(self):
        return {"counters": self.work_counters(), "setup": self._setup_record,
                "solve_cpu_ns": self._total_cpu_ns, "solve_seconds": self._total_seconds,
                "cache_entries": {"geometry": len(self._layouts), "interfaces": len(self._interfaces),
                                  "codes": len(self._codes), "recipes": len(self._recipes)}}

    def _axis_zero(self, k, j):
        key = (k, j)
        value = self._axis.get(key)
        if value is None:
            value = ((1 << (1 << k)) - 1) // ((1 << (1 << j)) + 1)
            self._axis[key] = value
            self._work["semantic_axis_mask_builds"] += 1
        return value

    def _drop_zero_axis(self, value, k, axis):
        # value has zeros throughout every high block of this axis.
        key = (k, axis)
        steps = self._compact_masks.get(key)
        if steps is None:
            steps = tuple((1 << (p - 1), self._axis_zero(k, p)) for p in range(axis + 1, k))
            self._compact_masks[key] = steps
            self._work["sparse_compaction_mask_builds"] += 1
        for stride, mask in steps:
            value = (value | (value >> stride)) & mask
        self._work["compaction_packed_steps"] += len(steps)
        return value

    def _layout(self, group):
        layout = self._layouts.get(group)
        if layout is None:
            offsets, mask = [0], self.full
            for g in group:
                mask &= self.zero[g]
                offsets += [v + (1 << g) for v in offsets]
            outside = tuple(i for i in range(self.n) if i not in group)
            layout = self._layouts[group] = (mask | (mask << self.rows), offsets, outside)
            self._work["group_layout_builds"] += 1
        else:
            self._work["group_layout_hits"] += 1
        return layout

    def _group(self, joint, group, bound):
        mask, offsets, _ = self._layout(group)
        work = self._work
        columns = [None] * 8

        def column(index):
            value = columns[index]
            if value is None:
                shift = offsets[index]
                # The outputs occupy disjoint blocks of the same packed int.
                # group=000 positions plus any corresponding local offset
                # remain in their own block, including its last outside row.
                value = (joint >> shift) & mask
                columns[index] = value
                work["residual_joint_rows"] += 1
                work["residual_packed_shifts"] += 1
                work["residual_packed_masks"] += 1
                work["residual_row_equivalents"] += self.rows >> 2
            return value

        def unpack(value):
            work["residual_pairs_unpacked"] += 1
            return value & self.full, value >> self.rows

        if self.witness:
            base = column(0)
            signature = sum((column(1 << i) != base) << i for i in range(3))
            work["fold_group_witnesses"] += 1
            work["fold_residual_comparisons"] += 3
            candidates = self.witness.get(signature, ())
            if not candidates:
                work["fold_no_witness_matching_entry"] += 1
            for canonical, oriented, pivot, checks in candidates:
                work["fold_group_hypotheses"] += 1
                one = column(pivot)
                work["fold_residual_comparisons"] += 1
                if one != base:
                    for i, bit in checks:
                        work["fold_residual_comparisons"] += 1
                        if column(i) != (one if bit else base):
                            break
                    else:
                        work["fold_group_hits"] += 1
                        classes = tuple((canonical >> i) & 1 for i in range(8))
                        pair = unpack(base), unpack(one)
                        return (2, classes, tuple(pair[c] for c in classes), oriented)
                work["fold_group_rejections"] += 1
        lookup, classes = {}, []
        for i in range(8):
            pair = column(i)
            work["joint_class_lookups"] += 1
            cl = lookup.setdefault(pair, len(lookup))
            if len(lookup) > bound:
                work["group_bound_rejections"] += 1
                return None
            classes.append(cl)
        residuals = tuple(unpack(v) for v in lookup)
        return (len(lookup), tuple(classes), tuple(residuals[c] for c in classes), None)

    def _interface(self, tables):
        work = self._work
        if tables in self._interfaces:
            work["group_cache_hits"] += 1
            return self._interfaces[tables]
        support = tuple(tuple(i for i, mask in enumerate(self.zero) if (t ^ (t >> (1 << i))) & mask)
                        for t in tables)
        work["support_bit_tests"] += self.n * 2
        shared = tuple(sorted(set(support[0]) & set(support[1])))
        work["eligible_group_count"] += comb(len(shared), 3)
        joint = tables[0] | (tables[1] << self.rows)
        work["joint_tables_joined"] += 1
        best, bound = None, 8
        for group in combinations(shared, 3):
            work["groups_requested"] += 1
            work["group_trials"] += 1
            result = self._group(joint, group, bound)
            if result is None:
                work["group_failures"] += 1
                continue
            count, classes, cols, oriented = result
            width = (count - 1).bit_length()
            best = (group, count, classes, cols, oriented)
            work["group_incumbents"] += 1
            # Every eligible variable is essential to each output: zero bits
            # cannot suffice. A width-w incumbent requires only a search for
            # at most 2**(w-1) joint classes in remaining groups.
            if width == 1:
                break
            bound = 1 << (width - 1)
        self._interfaces[tables] = (shared, best)
        return shared, best

    def _recipe(self, k, truth):
        work = self._work
        work["semantic_recipe_requests"] += 1
        key = (k, truth)
        result = self._recipes.get(key)
        if result is not None:
            work["semantic_recipe_hits"] += 1
            return result
        full = (1 << (1 << k)) - 1
        if truth in (0, full):
            result = _Recipe(0, "const", (int(truth != 0),))
        else:
            result = self._factor(k, truth, full)
        work["semantic_recipe_builds"] += 1
        self._recipes[key] = result
        return result

    def _factor(self, k, t, full):
        """Peel canalyzing/affine leaves, contract primitive pairs, then use Shannon."""
        work = self._work
        candidates, axes = [], []
        mux = None
        for i in range(k):
            mask = self._axis_zero(k, i)
            work["synthesis_axis_tests"] += 1
            if t == full ^ mask:
                return _Recipe(0, "literal", (i, False))
            if t == mask:
                return _Recipe(1, "literal", (i, True))
            stride = 1 << i
            lo, hi = t & mask, (t >> stride) & mask
            work["synthesis_packed_cofactors"] += 2
            if lo == hi:
                child = self._recipe(k - 1, self._drop_zero_axis(lo, k, i))
                return _Recipe(child.cost, "drop", (i, child))
            axes.append((i, mask, lo, hi))
            if lo == 0:
                op, inverted, residual = "AND", False, hi
            elif hi == mask:
                op, inverted, residual = "OR", False, lo
            elif hi == 0:
                op, inverted, residual = "AND", True, lo
            elif lo == mask:
                op, inverted, residual = "OR", True, hi
            elif lo ^ hi == mask:
                op, inverted, residual = "XOR", False, lo
            else:
                # Favor repeated polarities and sparse/dense cofactors on an
                # arbitrary table when no exact factor is available.
                half = 1 << (k - 1)
                a, b = lo.bit_count(), hi.bit_count()
                rank = (min(a, half - a) + min(b, half - b), (lo ^ hi).bit_count(), i)
                if mux is None or rank < mux[0]:
                    mux = (rank, i, lo, hi)
                continue
            child = self._recipe(k - 1, self._drop_zero_axis(residual, k, i))
            area = {"AND": 2, "OR": 3, "XOR": 4}[op] + int(inverted) + child.cost
            candidate = _Recipe(area, op, (i, inverted, child))
            if k > 3:
                work["synthesis_leaf_factor_nodes"] += 1
                return candidate
            candidates.append(candidate)
        if candidates:
            work["synthesis_leaf_factor_nodes"] += 1
            return min(candidates, key=lambda r: r.cost)
        for i, j in combinations(range(k), 2):
            work["synthesis_pair_tests"] += 1
            mask = axes[i][1] & axes[j][1]
            di, dj = 1 << i, 1 << j
            c01, c10 = (t >> di) & mask, (t >> dj) & mask
            work["synthesis_packed_cofactors"] += 2
            if c01 != c10:
                work["synthesis_pair_rejections"] += 1
                continue
            c00, c11 = t & mask, (t >> (di + dj)) & mask
            work["synthesis_packed_cofactors"] += 2
            if c00 == c01 != c11:
                op, one = "AND", c11
            elif c00 != c01 == c11:
                op, one = "OR", c01
            elif c00 == c11 != c01:
                op, one = "XOR", c01
            else:
                work["synthesis_pair_rejections"] += 1
                continue
            qt = self._drop_zero_axis(c00 | (one << di), k, j)
            child = self._recipe(k - 1, qt)
            work["synthesis_pair_contractions"] += 1
            return _Recipe({"AND": 2, "OR": 3, "XOR": 4}[op] + child.cost, "pair", (i, j, op, child))
        _, i, lo, hi = mux
        low = self._recipe(k - 1, self._drop_zero_axis(lo, k, i))
        high = self._recipe(k - 1, self._drop_zero_axis(hi, k, i))
        work["synthesis_shannon_nodes"] += 1
        return _Recipe(4 + low.cost + high.cost, "mux", (i, low, high))

    def _individual_classes(self, cols):
        result = []
        for output in range(2):
            labels = {}
            result.append(tuple(labels.setdefault(pair[output], len(labels)) for pair in cols))
            self._work["individual_partition_lookups"] += len(cols)
        return tuple(result)

    def _projections(self, labels, codes, width):
        """Smallest subset of code bits determining one consumer's residual."""
        for k in range(width + 1):
            for subset in combinations(range(width), k):
                self._work["quotient_projection_tests"] += 1
                by_code = {}
                for row, code in enumerate(codes):
                    shifted = sum(((code >> bit) & 1) << i for i, bit in enumerate(subset))
                    old = by_code.setdefault(shifted, row)
                    if labels[old] != labels[row]:
                        break
                else:
                    return subset, by_code
        raise AssertionError("selected code merges different residual functions")

    def _code(self, classes, columns, count, orientation):
        width = (count - 1).bit_length()
        if width == 1:
            # A jointly essential group must affect each output. With only
            # two joint residuals, each individual output must distinguish
            # those same two, so its quotient uses this single bit.
            h = sum(c << i for i, c in enumerate(classes)) if orientation is None else orientation
            key = (h,)
            result = self._codes.get(key)
            if result is None:
                codes = tuple((h >> row) & 1 for row in range(8))
                projection = ((0,), {0: codes.index(0), 1: codes.index(1)})
                result = self._codes[key] = ((h,), codes, (projection, projection))
                self._work["code_candidates"] += 1
            else:
                self._work["code_cache_hits"] += 1
            return result
        individual = self._individual_classes(columns)
        key = (classes, individual, orientation)
        cached = self._codes.get(key)
        if cached is not None:
            self._work["code_cache_hits"] += 1
            return cached

        def encoding(bits):
            codes = tuple(sum(((byte >> row) & 1) << bit for bit, byte in enumerate(bits))
                          for row in range(8))
            targets = {}
            self._work["code_candidates"] += 1
            for row, code in enumerate(codes):
                if targets.setdefault(code, classes[row]) != classes[row]:
                    self._work["code_rejections"] += 1
                    return None
            projections = tuple(self._projections(labels, codes, len(bits)) for labels in individual)
            return bits, codes, projections

        if width == 3:
            result = encoding(PINS)
        else:
            simple = all(max(labels) <= 1 for labels in individual)
            result = None
            if simple:
                basis = tuple(sum(value << row for row, value in enumerate(labels))
                              for labels in individual)
                result = encoding(basis)
                self._work["direct_projection_codes"] += 1
            if result is None:
                # Four possible words. For three or four joint classes there
                # are exactly 24 injective assignments of classes to words.
                self._work["general_code_searches"] += 1
                best = None
                for assignment in permutations(range(4), count):
                    bits = tuple(sum(((assignment[c] >> j) & 1) << s for s, c in enumerate(classes))
                                 for j in range(2))
                    candidate = encoding(bits)
                    score = self._code_score(candidate)
                    if best is None or score < best:
                        result, best = candidate, score
            if count == 3:
                # A valid four-word code can split one of three joint classes.
                # Consider all pairs of raw or one-primitive wires. This finite
                # shortcut is shared by both arms; size optimality is not claimed.
                best = self._code_score(result)
                if best[0] > 1:
                    cheap = list(PINS)
                    for a, b in combinations(PINS, 2):
                        cheap.extend(_binary(op, a, b) for op in OPS)
                    for pair in combinations(cheap, 2):
                        self._work["cheap_split_code_trials"] += 1
                        if sum(self._recipe(3, p).cost for p in pair) > best[0]:
                            continue
                        candidate = encoding(pair)
                        if candidate is not None:
                            score = self._code_score(candidate)
                            if score < best:
                                result, best = candidate, score
        if result is None:
            raise AssertionError("missing sufficient code")
        self._codes[key] = result
        return result

    def _code_score(self, encoding):
        bits, _, projections = encoding
        inputs = sum(len(subset) for subset, _ in projections)
        # One additional used quotient pin costs one primitive gate or more.
        # This is only a selection score, independent of any supplied fold.
        gate_estimate = sum(self._recipe(3, bit).cost for bit in bits)
        return gate_estimate + 2 * (inputs - 2), inputs, gate_estimate, bits

    def _quotient(self, output, projection, columns, outside, group, dense):
        subset, mapping = projection
        blocks = []
        for c in range(1 << len(subset)):
            # No local assignment has an unused projected codeword. Reuse the
            # nearest represented word, with the smaller word breaking ties.
            used = c if c in mapping else min(mapping, key=lambda v: ((c ^ v).bit_count(), v))
            sparse = columns[mapping[used]][output]
            value = dense.get(sparse)
            if value is None:
                value, k = sparse, self.n
                for axis in reversed(group):
                    value = self._drop_zero_axis(value, k, axis)
                    k -= 1
                dense[sparse] = value
                self._work["residual_compactions"] += 1
            else:
                self._work["residual_compaction_hits"] += 1
            blocks.append(value)
        self._work["quotient_code_blocks"] += len(blocks)
        block_rows = 1 << len(outside)
        return sum(block << (i * block_rows) for i, block in enumerate(blocks))

    def solve(self, supplied, second=None):
        """Accept (packed0, packed1) or two packed integer positional arguments."""
        wall, cpu = perf_counter(), process_time_ns()
        if second is None:
            if not isinstance(supplied, (tuple, list)) or len(supplied) != 2:
                raise ValueError("joint synthesis requires exactly two truth tables")
            tables = tuple(supplied)
        else:
            tables = (supplied, second)
        if any(type(t) is not int or not 0 <= t <= self.full for t in tables):
            raise ValueError("invalid complete public packed truth table")
        before = self.work_counters()
        self._work["tasks"] += 1
        self._work["input_rows_received"] += 2 * self.rows
        shared, interface = self._interface(tables)
        if interface is None:
            result = {"status": "no_eligible_triple", "n": self.n, "arm": self.arm,
                      "shared_support": list(shared), "triple": None, "width": None,
                      "class_count": None, "summary_wires": [], "circuit": None, "fold_uses": 0}
            return self._receipt(result, before, wall, cpu, {})
        group, count, classes, cols, orientation = interface
        width = (count - 1).bit_length()
        bits, codes, projections = self._code(classes, cols, count, orientation)
        outside = self._layout(group)[2]
        dense = {}
        quotients = tuple(self._quotient(o, projections[o], cols, outside, group, dense) for o in range(2))
        after_search_wall, after_search_cpu = perf_counter(), process_time_ns()
        physical = _Physical(self)
        taps, folded = [], []
        for i, byte in enumerate(bits):
            order = self.orientations.get(byte)
            if order is not None:
                taps.append(physical.template(order, group))
                folded.append(i)
            else:
                taps.append(physical.build(self._recipe(3, byte), group))
        physical.enter_cut(outside, taps)
        ends = []
        for quotient, (subset, _) in zip(quotients, projections):
            wires = outside + tuple(taps[j] for j in subset)
            ends.append(physical.build(self._recipe(len(wires), quotient), wires))
        after_build_wall, after_build_cpu = perf_counter(), process_time_ns()
        observed = tuple(physical.values[end] for end in ends)
        self._work["physical_output_comparisons"] += 2
        self._work["physical_output_bits_checked"] += 2 * self.rows
        if observed != tables:
            raise AssertionError("synthesized physical program differs from one or both public tables")
        circuit, final_taps, used, fanout, shared_gates = physical.finish(ends, taps)
        reached = set(used[0]) | set(used[1])
        if set(final_taps) != reached:
            raise AssertionError("declared code has a disconnected tap")
        fold_uses = sum(final_taps[i] in reached for i in folded)
        shared_taps = len(set(used[0]) & set(used[1]))
        result = {
            "status": "exact", "n": self.n, "arm": self.arm, "width": width, "class_count": count,
            "triple": list(group), "shared_support": list(shared), "shared_essential_inputs": len(shared),
            "eligible_groups": comb(len(shared), 3), "summary_truths": list(bits),
            "summary_wires": final_taps, "summary_wires_by_output": used,
            "summary_pin_fanouts": fanout, "shared_summary_wires": shared_taps,
            "shared_gates": shared_gates, "assignment_classes": list(classes),
            "assignment_codes": list(codes), "quotient_summary_bits": [list(p[0]) for p in projections],
            "outside_inputs": list(outside), "fold_uses": fold_uses,
            "named_fold_uses": fold_uses if self.arm == "named" else 0,
            "flat_fold_uses": fold_uses if self.arm == "flat" else 0,
            "expanded_NANDs": len(circuit["gates"]), "truth": list(observed),
            "outputs": circuit["outputs"], "circuit": circuit,
            "verified_assignments": self.rows, "verified_output_bits": 2 * self.rows,
        }
        timings = {"group_and_code_seconds": after_search_wall - wall,
                   "group_and_code_cpu_ns": after_search_cpu - cpu,
                   "build_seconds": after_build_wall - after_search_wall,
                   "build_cpu_ns": after_build_cpu - after_search_cpu,
                   "verification_seconds": perf_counter() - after_build_wall,
                   "verification_cpu_ns": process_time_ns() - after_build_cpu}
        return self._receipt(result, before, wall, cpu, timings)

    def _receipt(self, result, before, wall, cpu, timings):
        work = {k: v - before.get(k, 0) for k, v in self._work.items()}
        elapsed_cpu = process_time_ns() - cpu
        elapsed = perf_counter() - wall
        self._total_cpu_ns += elapsed_cpu
        self._total_seconds += elapsed
        timings.update(search_seconds=elapsed - timings.get("verification_seconds", 0),
                       search_cpu_ns=elapsed_cpu - timings.get("verification_cpu_ns", 0),
                       verify_seconds=timings.get("verification_seconds", 0),
                       verify_cpu_ns=timings.get("verification_cpu_ns", 0),
                       elapsed_seconds=elapsed, cpu_ns=elapsed_cpu)
        result.update(work=work, timing=timings)
        return result
