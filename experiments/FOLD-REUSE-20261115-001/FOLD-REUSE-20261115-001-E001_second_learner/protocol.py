"""Verifier and a learner that uses the order of returned counterexamples."""

from time import perf_counter_ns


class RuleChecker:
    """Give the learner only a first counterexample, or success after every row."""

    def __init__(self, n, target_truth, expand, fold_dag):
        self.n = n
        self._truth = target_truth
        self._expand = expand
        self._fold_dag = fold_dag
        self.attempts = []

    def examples(self, indices):
        return [(x, (self._truth >> x) & 1) for x in indices]

    def __call__(self, expr):
        start = perf_counter_ns()
        machine = self._expand(expr, self._fold_dag, self.n)
        gates = machine["gates"]
        output = machine["output"]
        total = 1 << self.n
        visited = 0
        counterexample = None
        for x in range(total - 1, -1, -1):
            registers = [(x >> j) & 1 for j in range(self.n)] + [0, 1]
            for left, right in gates:
                registers.append(1 ^ (registers[left] & registers[right]))
            wanted = (self._truth >> x) & 1
            visited += 1
            if registers[output] != wanted:
                counterexample = (x, wanted)
                break
        self.attempts.append({
            "expr": expr, "physical_gates": len(gates), "rows": visited,
            "nand_evaluations": visited * len(gates), "counterexample": counterexample,
            "wall_ns": perf_counter_ns() - start,
        })
        return counterexample


def sample_key(labels):
    return sum((int(bit) & 1) << i for i, bit in enumerate(labels))


def build_median_index(catalog, rows):
    """Compile the shared, public row positions before any task labels arrive."""
    candidates = catalog["candidates"]
    ranked = sorted(range(len(candidates)), key=lambda i: candidates[i]["truth"])
    groups = {}
    for i in ranked:
        truth = candidates[i]["truth"]
        key = sample_key((truth >> x) & 1 for x in rows)
        values, indices = groups.setdefault(key, ([], []))
        values.append(truth)
        indices.append(i)
    return {"groups": groups, "rows": tuple(rows), "indexed_functions": len(candidates)}


def lower_bound(values, lo, hi, key):
    comparisons = 0
    while lo < hi:
        comparisons += 1
        mid = (lo + hi) // 2
        if values[mid] < key:
            lo = mid + 1
        else:
            hi = mid
    return lo, comparisons


def fit_median(catalog, index, examples, check):
    # The search uses only public candidate truths, the supplied labels,
    # and the known order in which the checker reports its first mismatch.
    if tuple(x for x, _ in examples) != index["rows"]:
        raise ValueError("Examples differ from the public input positions")
    key = sample_key(label for _, label in examples)
    values, indices = index["groups"][key]
    lo, hi = 0, len(values)
    proposals = []
    evidence = []
    comparisons = 0
    while lo < hi:
        before = hi - lo
        middle = (lo + hi - 1) // 2
        i = indices[middle]
        candidate = catalog["candidates"][i]
        attempt = {"candidate_index": i, "expr": candidate["expr"], "origin": candidate["origin"],
                   "macro_uses": candidate["macro_uses"], "expanded_NANDs": candidate["expanded_NANDs"],
                   "consistent_before": before}
        proposals.append(attempt)
        correction = check(candidate["expr"])
        if correction is None:
            return {"status": "exact", "initial_proposal": dict(proposals[0]),
                    "final_expr": candidate["expr"], "proposals": proposals, "added_evidence": evidence,
                    "hypotheses_inspected": len(proposals), "order_comparisons": comparisons,
                    "checker_calls": len(proposals), "checker_failures": len(evidence),
                    "final_macro_uses": candidate["macro_uses"], "final_expanded_NANDs": candidate["expanded_NANDs"]}
        x, label = correction
        if ((candidate["truth"] >> x) & 1) == label:
            raise ValueError("Counterexample agrees with proposed program")
        # All bits above x agree with the proposal because they were checked first.
        prefix = ((values[middle] >> (x + 1)) << (x + 1)) | (label << x)
        new_lo, used = lower_bound(values, lo, hi, prefix)
        new_hi, more = lower_bound(values, new_lo, hi, prefix + (1 << x))
        comparisons += used + more
        if not 0 < new_hi - new_lo < before:
            raise ValueError("Counterexample did not narrow the hypothesis set")
        evidence.append({"round": len(proposals), "candidate_index": i, "x": x, "label": label})
        lo, hi = new_lo, new_hi
    raise ValueError("No consistent rule in the admitted class")
