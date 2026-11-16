"""Independent joint-response minimum-width primitive NAND comparator.

Only two complete packed truth columns enter solve. Every triple of variables
essential to EACH output (the support intersection) is scanned. Its eight assignments are grouped by BOTH
response columns over every outside assignment. Width is ceil(log2 K), and
ties are deterministic (width,K,triple). This establishes minimum width,
not a minimum-NAND encoder: classes get first-occurrence codes.

Summary bits are synthesized on the three raw grouped inputs. Both residual
functions are synthesized jointly with the ordered physical input domain
(outside raw inputs,summary wires) and a care mask for reachable codes. A
memoized Shannon compiler has constant/projection/complement and easy
AND/OR/XOR branch shortcuts. NAND gates are globally interned and shared.
No named component, supplied group, target generator or predecessor import.

Warm instances retain only public layouts, response columns, semantic
compilation and primitive gates. Returns prune/remap that gate pool to the
current outputs AND summaries. The opt-in dag-first route builds unrestricted
outputs first and finds a complete singleton/pair cut among existing local
wires at any minimum-width triple, else pays for cut-first fallback.
Caches and NAND interning include physical
wire domains. In particular there is no cross-boundary NOT(NOT x)->raw-x
alias simplification. Pure gate interning preserves the summary cut.

Circuit: n raw inputs0..n-1, constants0/1 at n/n+1, NAND gate j at n+2+j.
summary_wires appears both at result top level and in the circuit. A summary
can alias a raw grouped input when the chosen bit is a projection. Such a
wire is still one explicitly counted boundary bit. No redundant all-row
output checker runs inside solve; the caller supplies the common checker.
"""

from __future__ import annotations

from itertools import combinations
import time


SOURCE_DEPENDENCIES = ()
COUNTERS = (
    "solve_calls", "support_variable_tests", "support_packed_ops",
    "axis_masks_built", "triple_layouts_built", "layout_mask_terms",
    "triple_trials", "response_requests", "response_cache_hits",
    "response_columns_extracted", "response_packed_shifts", "response_packed_masks",
    "joint_response_keys", "joint_response_classes", "class_code_bit_tests",
    "residual_truth_bit_reads", "residual_blocks_built", "care_codes",
    "compile_requests", "compile_cache_hits", "compile_states_built",
    "constant_shortcuts", "literal_tests", "literal_shortcuts", "input_patterns_built",
    "shannon_splits", "care_merges", "xor_shortcuts", "and_shortcuts", "or_shortcuts",
    "mux_nodes", "nand_requests", "nand_constant_shortcuts", "nand_cache_hits",
    "nand_gates_created", "export_wire_visits", "export_gates_copied",
    "dependency_masks_built", "unrestricted_attempts", "unrestricted_gate_walks",
    "frontier_group_trials", "frontier_wire_visits", "frontier_acceptances",
    "dag_first_fallbacks", "cut_candidate_wires", "dominator_passes",
    "dominator_gate_visits", "first_cut_taps_considered", "unrestricted_gates_created",
    "unrestricted_compile_states", "fallback_gates_created", "fallback_compile_states",
)


def _integer(x, name):
    if type(x) is not int:
        raise ValueError(f"{name} must be an integer")
    return x


def _embeddings(positions):
    result = (0,)
    for j in positions:
        result += tuple(value | (1 << j) for value in result)
    return result


class PrimitiveReference:
    """Construct one instance per cold task or reuse one for a warm stream."""

    def __init__(self, n, strategy="cut-first"):
        started = time.perf_counter()
        self.n = _integer(n, "n")
        if n < 3:
            raise ValueError("the triple-summary domain needs at least three inputs")
        if strategy not in ("cut-first", "dag-first"):
            raise ValueError("unknown primitive reference strategy")
        self.strategy = strategy
        self.rows = 1 << n
        self.full = (1 << self.rows) - 1
        self.zero, self.one = n, n + 1
        self._work = dict.fromkeys(COUNTERS, 0)
        self._axes, self._layouts, self._responses, self._patterns = {}, {}, {}, {}
        self._functions, self._gate_ids, self._gates, self._gate_supports = {}, {}, [], []
        self.setup_seconds = time.perf_counter() - started

    def work_counters(self):
        return dict(self._work)

    def ledger(self):
        return {"n": self.n, "strategy": self.strategy, "work": self.work_counters(), "setup_seconds": self.setup_seconds,
                "cache": {"axis_masks": len(self._axes), "triple_layouts": len(self._layouts),
                          "response_columns": len(self._responses), "input_patterns": len(self._patterns),
                          "semantic_functions": len(self._functions), "interned_NANDs": len(self._gates)}}

    def _axis_low(self, j):
        if j not in self._axes:
            width = 1 << j
            self._axes[j] = self.full // ((1 << (2 * width)) - 1) * ((1 << width) - 1)
            self._work["axis_masks_built"] += 1
        return self._axes[j]

    def _support(self, outputs):
        support = []
        for j in range(self.n):
            low = self._axis_low(j)
            changes = [((truth ^ (truth >> (1 << j))) & low) for truth in outputs]
            self._work["support_variable_tests"] += 1
            self._work["support_packed_ops"] += 6
            if all(changes):
                support.append(j)
        return tuple(support)

    def _layout(self, triple):
        if triple not in self._layouts:
            outside = tuple(j for j in range(self.n) if j not in triple)
            inside_rows, outside_rows = _embeddings(triple), _embeddings(outside)
            mask = 0
            for row in outside_rows:
                mask |= 1 << row
            self._layouts[triple] = (inside_rows, outside_rows, mask, outside)
            self._work["triple_layouts_built"] += 1
            self._work["layout_mask_terms"] += len(outside_rows)
        return self._layouts[triple]

    def _response(self, truth, triple, inside, mask):
        self._work["response_requests"] += 1
        key = (truth, triple)
        if key in self._responses:
            self._work["response_cache_hits"] += 1
            return self._responses[key]
        response = tuple((truth >> offset) & mask for offset in inside)
        self._work["response_columns_extracted"] += 8
        self._work["response_packed_shifts"] += 8
        self._work["response_packed_masks"] += 8
        self._responses[key] = response
        return response

    def _choose(self, outputs, support):
        chosen, chosen_key, minimum_width, eligible = None, None, None, []
        for triple in combinations(support, 3):
            self._work["triple_trials"] += 1
            inside, outside, mask, positions = self._layout(triple)
            first = self._response(outputs[0], triple, inside, mask)
            second = self._response(outputs[1], triple, inside, mask)
            classes, codes, representatives = {}, [], []
            for assignment, response in enumerate(zip(first, second)):
                self._work["joint_response_keys"] += 1
                if response not in classes:
                    classes[response] = len(classes)
                    representatives.append(assignment)
                codes.append(classes[response])
            count = len(classes)
            self._work["joint_response_classes"] += count
            width = (count - 1).bit_length()
            key = (width, count, triple)
            candidate = (triple, width, count, tuple(codes), tuple(representatives),
                         first, second, outside, positions)
            if minimum_width is None or width < minimum_width:
                minimum_width, eligible = width, [candidate]
            elif width == minimum_width:
                eligible.append(candidate)
            if chosen_key is None or key < chosen_key:
                chosen_key = key
                chosen = candidate
        return chosen, sorted(eligible, key=lambda row: (row[2], row[0]))

    def _dependencies(self, wire):
        if wire < self.n:
            return 1 << wire
        if wire < self.n + 2:
            return 0
        return self._gate_supports[wire - self.n - 2]

    def _nand(self, a, b):
        self._work["nand_requests"] += 1
        if a == self.zero or b == self.zero:
            self._work["nand_constant_shortcuts"] += 1
            return self.one
        if a == self.one and b == self.one:
            self._work["nand_constant_shortcuts"] += 1
            return self.zero
        # These identities preserve dependence on the admitted input wire;
        # no inverse-node alias can expose a grouped raw input through a cut.
        if a == self.one:
            a = b
        elif b == self.one:
            b = a
        pair = tuple(sorted((a, b)))
        if pair in self._gate_ids:
            self._work["nand_cache_hits"] += 1
            return self._gate_ids[pair]
        wire = self.n + 2 + len(self._gates)
        self._gates.append(pair)
        self._gate_supports.append(self._dependencies(a) | self._dependencies(b))
        self._gate_ids[pair] = wire
        self._work["nand_gates_created"] += 1
        self._work["dependency_masks_built"] += 1
        return wire

    def _not(self, wire):
        return self._nand(wire, wire)

    def _and(self, a, b):
        t = self._nand(a, b)
        return self._nand(t, t)

    def _or(self, a, b):
        return self._nand(self._not(a), self._not(b))

    def _xor(self, a, b):
        t = self._nand(a, b)
        return self._nand(self._nand(a, t), self._nand(b, t))

    def _input_pattern(self, k, j):
        key = (k, j)
        if key not in self._patterns:
            full = (1 << (1 << k)) - 1
            width = 1 << j
            low = full // ((1 << (2 * width)) - 1) * ((1 << width) - 1)
            self._patterns[key] = full ^ low
            self._work["input_patterns_built"] += 1
        return self._patterns[key]

    def _compile(self, truth, care, variables):
        self._work["compile_requests"] += 1
        truth &= care
        key = (truth, care, variables)
        if key in self._functions:
            self._work["compile_cache_hits"] += 1
            return self._functions[key]
        self._work["compile_states_built"] += 1
        if not truth:
            self._work["constant_shortcuts"] += 1
            result = self.zero
        elif truth == care:
            self._work["constant_shortcuts"] += 1
            result = self.one
        else:
            result = None
            full = (1 << (1 << len(variables))) - 1
            for j, wire in enumerate(variables):
                pattern = self._input_pattern(len(variables), j)
                self._work["literal_tests"] += 1
                if ((truth ^ pattern) & care) == 0:
                    result = wire
                elif ((truth ^ (full ^ pattern)) & care) == 0:
                    result = self._not(wire)
                if result is not None:
                    self._work["literal_shortcuts"] += 1
                    break
            if result is None:
                if not variables:
                    raise AssertionError("nonconstant zero-input function")
                self._work["shannon_splits"] += 1
                half_rows = 1 << (len(variables) - 1)
                low_mask = (1 << half_rows) - 1
                lo, hi = truth & low_mask, truth >> half_rows
                lc, hc = care & low_mask, care >> half_rows
                child_variables, select = variables[:-1], variables[-1]
                # Same constraints on the intersection allow a common
                # don't-care completion, so this selector can be removed.
                if not ((lo ^ hi) & lc & hc):
                    self._work["care_merges"] += 1
                    result = self._compile((lo & lc) | (hi & hc), lc | hc, child_variables)
                elif lc == hc and ((lo ^ hi) & lc) == lc:
                    self._work["xor_shortcuts"] += 1
                    result = self._xor(select, self._compile(lo, lc, child_variables))
                else:
                    left = self._compile(lo, lc, child_variables)
                    right = self._compile(hi, hc, child_variables)
                    if left == right:
                        result = left
                    elif left == self.zero:
                        self._work["and_shortcuts"] += 1
                        result = self._and(select, right)
                    elif right == self.zero:
                        self._work["and_shortcuts"] += 1
                        result = self._and(self._not(select), left)
                    elif left == self.one:
                        self._work["or_shortcuts"] += 1
                        result = self._nand(select, self._not(right))
                    elif right == self.one:
                        self._work["or_shortcuts"] += 1
                        result = self._or(select, left)
                    else:
                        self._work["mux_nodes"] += 1
                        result = self._nand(self._nand(self._not(select), left), self._nand(select, right))
        self._functions[key] = result
        return result

    def _reachable(self, wires, counter):
        required = set()
        todo = list(wires)
        while todo:
            wire = todo.pop()
            self._work[counter] += 1
            if wire < self.n + 2 or wire in required:
                continue
            required.add(wire)
            todo.extend(self._gates[wire - self.n - 2])
        return required

    def _frontier(self, outputs, triple, width, reachable):
        """Complete singleton/pair node cut, not a greedy maximal frontier.

        A bit in D(v) denotes a group-only candidate wire that blocks EVERY
        grouped-source path to v. Outside/constant vertices have no such
        paths, hence all bits. A NAND intersects both fanin masks and may add
        its own bit. For pairs, remove each first tap and recompute D; any
        remaining bit supplies a sound second tap. This covers every pair.
        Three raw grouped inputs are a complete three-bit cut if required.
        """
        self._work["frontier_group_trials"] += 1
        group = sum(1 << j for j in triple)
        if width == 3:
            return list(triple)
        candidates = list(triple)
        for wire in reachable:
            dependency = self._dependencies(wire)
            if dependency and not dependency & ~group:
                candidates.append(wire)
        candidates = sorted(set(candidates))
        self._work["cut_candidate_wires"] += len(candidates)
        bits = {wire: 1 << j for j, wire in enumerate(candidates)}
        full = (1 << len(candidates)) - 1

        def mandatory(removed=None):
            self._work["dominator_passes"] += 1
            dom = {wire: (bits.get(wire, 0) if wire in triple else full)
                   for wire in range(self.n)}
            dom[self.zero] = dom[self.one] = full
            if removed is not None and removed < self.n:
                dom[removed] = full
            for wire in reachable:
                self._work["dominator_gate_visits"] += 1
                self._work["frontier_wire_visits"] += 1
                if wire == removed:
                    dom[wire] = full
                else:
                    a, b = self._gates[wire - self.n - 2]
                    dom[wire] = (dom[a] & dom[b]) | bits.get(wire, 0)
            return dom[outputs[0]] & dom[outputs[1]]

        if width == 1:
            mask = mandatory()
            return [] if not mask else [candidates[(mask & -mask).bit_length() - 1]]
        if width == 0:
            return []
        for index, first in enumerate(candidates):
            self._work["first_cut_taps_considered"] += 1
            mask = mandatory(first) & (full ^ ((1 << (index + 1)) - 1))
            if mask:
                return [first, candidates[(mask & -mask).bit_length() - 1]]
        return []

    def _export(self, outputs, summaries):
        required = self._reachable(list(outputs) + list(summaries), "export_wire_visits")
        ordered = sorted(required)
        mapping = {wire: wire for wire in range(self.n + 2)}
        gates = []
        for old in ordered:
            a, b = self._gates[old - self.n - 2]
            mapping[old] = self.n + 2 + len(gates)
            gates.append([mapping[a], mapping[b]])
        self._work["export_gates_copied"] += len(gates)
        summary_wires = [mapping[s] for s in summaries]
        circuit = {"n": self.n, "gates": gates, "outputs": [mapping[o] for o in outputs],
                   "summary_wires": summary_wires}
        return circuit, summary_wires

    def solve(self, outputs):
        start, cpu = time.perf_counter(), time.process_time_ns()
        before = self.work_counters()
        self._work["solve_calls"] += 1
        if not isinstance(outputs, (list, tuple)) or len(outputs) != 2:
            raise ValueError("outputs must be two packed truth integers")
        outputs = tuple(_integer(t, "truth") for t in outputs)
        if any(t < 0 or t > self.full for t in outputs):
            raise ValueError("packed truth outside the input register")
        unrestricted_start, unrestricted_cpu = time.perf_counter(), time.process_time_ns()
        unrestricted, unrestricted_gate_count, unrestricted_reachable = None, None, ()
        if self.strategy == "dag-first":
            self._work["unrestricted_attempts"] += 1
            old_gates, old_states = self._work["nand_gates_created"], self._work["compile_states_built"]
            unrestricted = [self._compile(truth, self.full, tuple(range(self.n))) for truth in outputs]
            self._work["unrestricted_gates_created"] += self._work["nand_gates_created"] - old_gates
            self._work["unrestricted_compile_states"] += self._work["compile_states_built"] - old_states
            unrestricted_reachable = tuple(sorted(self._reachable(unrestricted, "unrestricted_gate_walks")))
            unrestricted_gate_count = len(unrestricted_reachable)
        unrestricted_seconds = time.perf_counter() - unrestricted_start
        unrestricted_cpu_ns = time.process_time_ns() - unrestricted_cpu
        index_start, index_cpu_start = time.perf_counter(), time.process_time_ns()
        support = self._support(outputs)
        chosen, eligible = self._choose(outputs, support)
        index_seconds = time.perf_counter() - index_start
        index_cpu = time.process_time_ns() - index_cpu_start
        if chosen is None:
            return {"status": "unsupported", "n": self.n, "width": None, "class_count": None,
                    "triple": None, "summary_wires": [], "circuit": None,
                    "reason": "fewer than three inputs essential to each output", "joint_support": list(support),
                    "strategy": self.strategy, "unrestricted_met_contract": False,
                    "unrestricted_gate_count": unrestricted_gate_count,
                    "work": {k: self._work[k] - before[k] for k in COUNTERS},
                    "timing": {"index_seconds": index_seconds, "index_cpu_ns": index_cpu,
                               "unrestricted_seconds": unrestricted_seconds, "unrestricted_cpu_ns": unrestricted_cpu_ns,
                               "elapsed_seconds": time.perf_counter() - start,
                               "cpu_ns": time.process_time_ns() - cpu}}
        compile_start, compile_cpu = time.perf_counter(), time.process_time_ns()
        accepted = False
        if unrestricted is not None:
            for candidate in eligible:
                taps = self._frontier(unrestricted, candidate[0], candidate[1], unrestricted_reachable)
                if len(taps) == candidate[1]:
                    chosen, summaries, physical_outputs = candidate, taps, unrestricted
                    accepted = True
                    self._work["frontier_acceptances"] += 1
                    break
        triple, width, count, codes, representatives, first, second, outside_rows, outside = chosen
        summary_truths = None
        if not accepted:
            old_gates, old_states = self._work["nand_gates_created"], self._work["compile_states_built"]
            if unrestricted is not None:
                self._work["dag_first_fallbacks"] += 1
            summary_truths = []
            for j in range(width):
                summary_truths.append(sum(((code >> j) & 1) << assignment for assignment, code in enumerate(codes)))
                self._work["class_code_bit_tests"] += 8
            summaries = [self._compile(truth, 255, triple) for truth in summary_truths]
            residuals = [0, 0]
            block_rows = len(outside_rows)
            for code, assignment in enumerate(representatives):
                for answer, columns in enumerate((first, second)):
                    column = columns[assignment]
                    block = 0
                    for j, raw in enumerate(outside_rows):
                        block |= ((column >> raw) & 1) << j
                    residuals[answer] |= block << (code * block_rows)
                    self._work["residual_truth_bit_reads"] += block_rows
                    self._work["residual_blocks_built"] += 1
            care = (1 << (count * block_rows)) - 1
            self._work["care_codes"] += count
            variables = tuple(outside) + tuple(summaries)
            physical_outputs = [self._compile(truth, care, variables) for truth in residuals]
            if unrestricted is not None:
                self._work["fallback_gates_created"] += self._work["nand_gates_created"] - old_gates
                self._work["fallback_compile_states"] += self._work["compile_states_built"] - old_states
        compile_seconds = time.perf_counter() - compile_start
        compile_cpu_ns = time.process_time_ns() - compile_cpu
        export_start = time.perf_counter()
        circuit, summary_wires = self._export(physical_outputs, summaries)
        return {
            "status": "exact", "n": self.n, "width": width, "class_count": count,
            "triple": list(triple), "summary_wires": summary_wires, "circuit": circuit,
            "strategy": self.strategy, "unrestricted_met_contract": accepted if unrestricted is not None else None,
            "unrestricted_gate_count": unrestricted_gate_count,
            "dag_first_fallback": unrestricted is not None and not accepted,
            "summary_truths": summary_truths, "class_codes": None if accepted else list(codes), "joint_support": list(support),
            "encoding": ("existing unrestricted NAND frontier; no recoding" if accepted else
                         "first-occurrence response classes; unused codes are don't-cares"),
            "selection": ("minimum width, first valid existing cut in (class_count,triple) order" if accepted else
                          "minimum(width,class_count,triple); no NAND-optimality claim"),
            "cut_search": "complete singleton/pair dominator masks; raw-input triple for width3",
            "work": {k: self._work[k] - before[k] for k in COUNTERS},
            "timing": {"index_seconds": index_seconds, "index_cpu_ns": index_cpu,
                       "unrestricted_seconds": unrestricted_seconds, "unrestricted_cpu_ns": unrestricted_cpu_ns,
                       "compile_seconds": compile_seconds, "compile_cpu_ns": compile_cpu_ns,
                       "return_seconds": time.perf_counter() - export_start,
                       "elapsed_seconds": time.perf_counter() - start,
                       "cpu_ns": time.process_time_ns() - cpu},
        }


def _evaluate(circuit, x):
    n = circuit["n"]
    values = [(x >> j) & 1 for j in range(n)] + [0, 1]
    for a, b in circuit["gates"]:
        values.append(1 ^ (values[a] & values[b]))
    return tuple(values[o] for o in circuit["outputs"]), values


def _check_cut(result):
    circuit, group = result["circuit"], set(result["triple"])
    summaries = set(result["summary_wires"])
    n = circuit["n"]
    memo = {}
    def inputs(wire, stop):
        key = (wire, stop)
        if key in memo:
            return memo[key]
        if stop and wire in summaries:
            return set()
        if wire < n:
            return {wire}
        if wire < n + 2:
            return set()
        a, b = circuit["gates"][wire - n - 2]
        result = inputs(a, stop) | inputs(b, stop)
        memo[key] = result
        return result
    assert all(not (inputs(o, True) & group) for o in circuit["outputs"])
    assert all(inputs(s, False) <= group for s in summaries)


def self_test():
    """Unrelated hand/random primitive fixtures only; no study inputs."""
    import json
    import random
    rng = random.Random(14017)
    checked = 0
    accepted = fallback = 0
    for n in (3, 4, 5):
        engines = {strategy: PrimitiveReference(n, strategy) for strategy in ("cut-first", "dag-first")}
        targets = [tuple(rng.getrandbits(1 << n) for _ in range(2)) for _ in range(6)]
        # Shared simple primitive structure supplies a compressible case.
        shared = [0, 0]
        for x in range(1 << n):
            parity = (x & 1) ^ ((x >> 1) & 1) ^ ((x >> 2) & 1)
            shared[0] |= (parity | ((x >> 3) & 1)) << x
            shared[1] |= (parity & ((x >> 4) & 1)) << x
        targets.append(tuple(shared))
        for outputs in targets:
            # Admissibility is the INTERSECTION of semantic supports.
            support = [j for j in range(n) if all(any(
                ((truth >> x) & 1) != ((truth >> (x ^ (1 << j))) & 1)
                for x in range(1 << n)) for truth in outputs)]
            minimum = None
            oracle = {}
            for triple in combinations(support, 3):
                outside = tuple(j for j in range(n) if j not in triple)
                keys = set()
                for inside in range(8):
                    offset = sum(((inside >> j) & 1) << p for j, p in enumerate(triple))
                    key = tuple(tuple((truth >> (offset | raw)) & 1 for raw in _embeddings(outside))
                                for truth in outputs)
                    keys.add(key)
                candidate = ((len(keys) - 1).bit_length(), len(keys), triple)
                oracle[triple] = candidate
                minimum = candidate if minimum is None else min(minimum, candidate)
            for strategy, engine in engines.items():
                result = engine.solve(outputs)
                assert result["joint_support"] == support
                if minimum is None:
                    assert result["status"] == "unsupported"
                    continue
                assert result["status"] == "exact"
                _check_cut(result)
                own = (result["width"], result["class_count"], tuple(result["triple"]))
                assert own == oracle[tuple(result["triple"])] and result["width"] == minimum[0]
                if strategy == "cut-first":
                    assert own == minimum
                else:
                    accepted += int(result["unrestricted_met_contract"])
                    fallback += int(result["dag_first_fallback"])
                for x in range(1 << n):
                    actual, values = _evaluate(result["circuit"], x)
                    assert actual == tuple((truth >> x) & 1 for truth in outputs)
                    if result["summary_truths"] is not None:
                        local = sum(((x >> p) & 1) << j for j, p in enumerate(result["triple"]))
                        assert [values[s] for s in result["summary_wires"]] == [
                            (truth >> local) & 1 for truth in result["summary_truths"]]
                    checked += 1
                # Warm export must not include unrelated old pool gates.
                repeated = engine.solve(outputs)
                assert repeated["work"]["nand_gates_created"] == 0
                assert repeated["circuit"] == result["circuit"]
                assert repeated["work"]["response_columns_extracted"] == 0
                json.dumps(result)
    # Outside variables seen by only one answer are never eligible group pins.
    outside_fixture = [0, 0]
    for x in range(32):
        h = (x & 1) ^ ((x >> 1) & 1) ^ ((x >> 2) & 1)
        outside_fixture[0] |= (h | ((x >> 3) & 1)) << x
        outside_fixture[1] |= (h & ((x >> 4) & 1)) << x
    for strategy in ("cut-first", "dag-first"):
        result = PrimitiveReference(5, strategy).solve(outside_fixture)
        assert result["joint_support"] == [0, 1, 2] and result["triple"] == [0, 1, 2]
        assert result["width"] == 1 and result["class_count"] == 2
        _check_cut(result)
        assert all(_evaluate(result["circuit"], x)[0] == tuple((t >> x) & 1 for t in outside_fixture)
                   for x in range(32))
    # Interleaved outside inputs can prevent the fixed-order unrestricted
    # Shannon DAG from materializing the required local one-bit boundary.
    # The paid fallback must still return a complete contract-compatible DAG.
    interleaved = [0, 0]
    for x in range(32):
        h = ((x >> 1) & 1) ^ ((x >> 3) & 1) ^ ((x >> 4) & 1)
        interleaved[0] |= (h | (x & 1)) << x
        interleaved[1] |= (h & ((x >> 2) & 1)) << x
    result = PrimitiveReference(5, "dag-first").solve(interleaved)
    assert result["joint_support"] == [1, 3, 4] and result["width"] == 1
    assert result["dag_first_fallback"] and result["work"]["dag_first_fallbacks"] == 1
    assert result["work"]["unrestricted_gates_created"] > 0
    assert result["work"]["fallback_compile_states"] > 0
    _check_cut(result)
    assert all(_evaluate(result["circuit"], x)[0] == tuple((t >> x) & 1 for t in interleaved)
               for x in range(32))
    fallback += 1
    # A greedy maximal frontier would return both h and NOT(h). The complete
    # single-wire calculation must instead return the shared ancestor h.
    fixture = PrimitiveReference(5, "dag-first")
    h = fixture._xor(fixture._xor(0, 1), 2)
    u = fixture._not(h)
    outputs = [fixture._nand(h, 3), fixture._nand(u, 4)]
    reachable = tuple(sorted(fixture._reachable(outputs, "unrestricted_gate_walks")))
    assert fixture._frontier(outputs, (0, 1, 2), 1, reachable) == [h]
    # Independent brute enumeration checks singleton/pair completeness on
    # small arbitrary physical DAGs, including constants and aliased inputs.
    cut_cases = 0
    for _ in range(12):
        builder = PrimitiveReference(5)
        wires = list(range(7))
        for _ in range(12):
            wires.append(builder._nand(rng.choice(wires), rng.choice(wires)))
        roots = [wires[-1], wires[-2]]
        reachable = tuple(sorted(builder._reachable(roots, "unrestricted_gate_walks")))
        group_mask = 7
        candidates = list(range(3)) + [wire for wire in reachable
                     if builder._dependencies(wire) and not builder._dependencies(wire) & ~group_mask]
        candidates = sorted(set(candidates))
        def blocks(taps):
            seen, todo = set(), list(roots)
            while todo:
                wire = todo.pop()
                if wire in seen or wire in taps:
                    continue
                seen.add(wire)
                if wire < 3:
                    return False
                if wire >= 7:
                    todo.extend(builder._gates[wire - 7])
            return True
        for width in (1, 2):
            exact = any(blocks(set(taps)) for taps in combinations(candidates, width))
            found = builder._frontier(roots, (0, 1, 2), width, reachable)
            assert (len(found) == width) == exact
            if found:
                assert blocks(set(found))
            cut_cases += 1
    return {"synthetic_only": True, "status": "passed", "scalar_rows_checked": checked,
            "minimum_width_cut_shared_gates_and_warm_caches": "passed",
            "support_intersection_and_outside_fixture": "passed", "complete_cut_cases": cut_cases,
            "dag_first_acceptances": accepted, "dag_first_fallbacks": fallback}


if __name__ == "__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test:
        parser.error("use --self-test; study inputs are provided only by the caller")
    print(json.dumps(self_test(), sort_keys=True))
