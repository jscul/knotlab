#!/usr/bin/env python3
"""Independent exact referee recomputation; does not import census.py.

Interface: finite Boolean NAE gadgets and generation laws in preregistration;
outputs: exact local projections and alive(t) for the tested finite depths.
Budget per invocation: 570 CPU seconds, 580 wall seconds, 7 GiB address space.
No infinite-depth, unrestricted-minimality, or novelty conclusion is computed.
Only this script's sibling growth_mutations.json is written.
"""
import argparse
from collections import Counter
import hashlib
from itertools import combinations, product
import json
import os
from pathlib import Path
import resource
import signal
import sys
import time

sys.dont_write_bytecode = True
resource.setrlimit(resource.RLIMIT_AS, (7 * 1024**3, 7 * 1024**3))
resource.setrlimit(resource.RLIMIT_CPU, (570, 570))
signal.alarm(580)

ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / "artifacts/CHEAP-COUNT-20261112-001A/CHEAP-COUNT-20261112-001A-E001_cheapest_counter"
OUT = Path(__file__).with_suffix(".json")
STATES4 = tuple(product((0, 1), repeat=4))
EVEN = frozenset(x for x in STATES4 if sum(x) % 2 == 0)
RULES = ("rule 60", "rule 90", "rule 150", "rule 102", "hop")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(result):
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


def projection(triples, variables=7):
    """Literal enumeration of all Boolean assignments, grouping first four."""
    counts = Counter()
    for values in product((0, 1), repeat=variables):
        if all(len({values[v] for v in triple}) == 2 for triple in triples):
            counts[values[:4]] += 1
    return frozenset(counts), {"".join(map(str, x)): counts[x] for x in STATES4}


def state_mask(relation):
    return sum(1 << i for i, state in enumerate(STATES4) if state in relation)


def slots(rule, i, old, new, ref):
    def at(j):
        return old[j] if 0 <= j < len(old) else ref
    if rule == "rule 60":
        return (new, at(i - 1), at(i), ref)
    if rule == "rule 90":
        return (new, at(i - 1), at(i + 1), ref)
    if rule == "rule 150":
        return (new, at(i - 1), at(i), at(i + 1))
    if rule == "rule 102":
        return (new, at(i), at(i + 1), ref)
    if rule == "hop":
        return (new, at(i // 2), at(i), ref)
    raise ValueError(rule)


def seq_string(sequence):
    return "".join("1" if b else "0" for b in sequence)


def closure(row):
    return all(len(set(row[i:i + 3])) == 2 for i in range(len(row) - 2))


def finite_class(sequence):
    """Same finite-prefix decision rule; labels are NOT asymptotic results."""
    if len(set(sequence)) == 1:
        return "constant"
    for period in range(1, 17):
        for start in range(32):
            if all(sequence[i] == sequence[i + period]
                   for i in range(start, len(sequence) - period)):
                return "eventually constant" if period == 1 else f"period {period}"
    return "unexplained"


def linear_growth(rule, depth, odd=False):
    """GF(2) forms in 3 initial bits + R + an affine constant bit."""
    old = [1, 2, 4]
    ref, constant = 8, 16
    records = []
    for t in range(1, depth + 1):
        row = []
        for i in range(len(old) + 1):
            operands = slots(rule, i, old, 0, ref)[1:]
            form = constant if odd else 0
            for value in operands:
                form ^= value
            row.append(form)
        witnesses = []
        for seed in range(16):
            assignment = seed | constant
            values = [(form & assignment).bit_count() % 2 for form in row]
            if closure(values):
                witnesses.append({"seed": seed, "last": "".join(map(str, values))})
        records.append({"depth": t, "alive": bool(witnesses),
                        "seed_count": len(witnesses), "witness": witnesses[:1],
                        "forms": row})
        old = row
    return records


def projected_gadget_growth(rule, relation, depth):
    """Witness projection composed with disjoint fresh variables per position.

    A repeated source is given a distinct named copy, tied by the strict NAE
    equality gadget checked below. Thus each local state is tested in the
    full four-variable projection, including states with equal slot values.
    """
    records = [{"depth": t, "seeds": []} for t in range(1, depth + 1)]
    for seed in product((0, 1), repeat=4):
        old, ref = list(seed[:3]), seed[3]
        for t in range(1, depth + 1):
            row = []
            for i in range(len(old) + 1):
                allowed = [new for new in (0, 1)
                           if slots(rule, i, old, new, ref) in relation]
                assert len(allowed) == 1, (rule, t, i, allowed)
                row.append(allowed[0])
            if closure(row):
                records[t - 1]["seeds"].append("".join(map(str, seed)))
            old = row
    return [{"depth": x["depth"], "alive": bool(x["seeds"]),
             "seed_count": len(x["seeds"])} for x in records]


class NAEBuilder:
    def __init__(self):
        self.variables = 0
        self.triples = []

    def new(self):
        self.variables += 1
        return self.variables

    def nae(self, a, b, c):
        assert len({a, b, c}) == 3
        self.triples.append((a, b, c))

    def unequal(self, a, b):
        auxiliaries = [self.new() for _ in range(3)]
        for fresh in auxiliaries:
            self.nae(a, b, fresh)
        self.nae(*auxiliaries)

    def equal(self, a, b):
        middle = self.new()
        self.unequal(a, middle)
        self.unequal(middle, b)

    def clauses(self):
        return [clause for triple in self.triples
                for clause in (list(triple), [-v for v in triple])]


def check_copy_primitives():
    checks = {}
    for name in ("unequal", "equal"):
        b = NAEBuilder()
        left, right = b.new(), b.new()
        getattr(b, name)(left, right)
        counts = Counter()
        for values in product((0, 1), repeat=b.variables):
            if all(len({values[v - 1] for v in tri}) == 2 for tri in b.triples):
                counts[values[:2]] += 1
        expected = {(0, 1), (1, 0)} if name == "unequal" else {(0, 0), (1, 1)}
        assert set(counts) == expected
        checks[name] = {"named_projection": [list(p) for p in sorted(counts)],
                        "witness_counts": {str(k): v for k, v in counts.items()},
                        "variables": b.variables, "strict_NAE_triples": len(b.triples)}
    return checks


def strict_gadget_cnf(rule, depth, gadget):
    b = NAEBuilder()
    ref = b.new()
    old = [b.new() for _ in range(3)]
    collisions = 0
    for t in range(1, depth + 1):
        row = [b.new() for _ in range(len(old) + 1)]
        for i, new in enumerate(row):
            named = list(slots(rule, i, old, new, ref))
            seen = set()
            for j, value in enumerate(named):
                if value in seen:
                    copy = b.new()
                    b.equal(value, copy)
                    named[j] = copy
                    collisions += 1
                seen.add(value)
            helpers = [b.new() for _ in range(3)]
            local = named + helpers
            for triple in gadget:
                b.nae(*(local[v] for v in triple))
        old = row
    for i in range(len(old) - 2):
        b.nae(*old[i:i + 3])
    return b.clauses(), {"variables": b.variables, "strict_NAE_triples": len(b.triples),
                         "slot_collision_copies": collisions}


def relation_growth_cnf(rule, relation, depth):
    """Independent general finite-relation encoding with duplicate-literal cleanup."""
    ref = 1
    next_id = 2
    old = list(range(next_id, next_id + 3))
    next_id += 3
    clauses = []
    rows = []
    for t in range(1, depth + 1):
        row = list(range(next_id, next_id + len(old) + 1))
        next_id += len(row)
        for i, new in enumerate(row):
            ids = slots(rule, i, old, new, ref)
            for state in STATES4:
                if state in relation:
                    continue
                clause = {(-v if bit else v) for v, bit in zip(ids, state)}
                if any(-literal in clause for literal in clause):
                    continue
                clauses.append(sorted(clause))
        rows.append(row)
        old = row
    return clauses, rows, next_id


def small_sat_controls(gadget, direct, depth=8):
    from pysat.solvers import Solver
    results = []
    for rule in ("rule 60", "hop"):
        for t in range(1, depth + 1):
            cnf, size = strict_gadget_cnf(rule, t, gadget)
            with Solver(name="cadical153", bootstrap_with=cnf) as solver:
                sat = solver.solve()
            assert sat == direct[rule][t - 1]["alive"]
            results.append({"rule": rule, "depth": t, "alive": sat, **size})
    # Direct parity CNF, a separate exact encoding, including dead controls.
    for rule in RULES:
        for t in range(1, depth + 1):
            clauses, rows, _ = relation_growth_cnf(rule, EVEN, t)
            for i in range(len(rows[-1]) - 2):
                tri = rows[-1][i:i + 3]
                clauses += [tri, [-v for v in tri]]
            with Solver(name="cadical153", bootstrap_with=clauses) as solver:
                sat = solver.solve()
            assert sat == direct[rule][t - 1]["alive"]
    return results


def mutate(gadget):
    original = set(gadget)
    candidates = tuple(k for k in combinations(range(7), 3) if not set(k) <= set(range(4)))
    rows, relations = [], {}
    for deleted in range(len(gadget)):
        for replacement in (None,) + tuple(k for k in candidates if k not in original):
            changed = gadget[:deleted] + gadget[deleted + 1:]
            if replacement is not None:
                changed = changed + [replacement]
            relation, witness_counts = projection(changed)
            mask = state_mask(relation)
            relations[mask] = relation
            rows.append({"kind": "delete" if replacement is None else "replace",
                         "j": deleted, "k": replacement,
                         "rel_size": len(relation), "relation_mask": mask,
                         "same_parity": relation == EVEN,
                         "allowed_states": ["".join(map(str, x)) for x in sorted(relation)],
                         "named_witness_counts": witness_counts})
    return rows, relations


def exact_relation_growth(relation, depth):
    """Incremental SAT, adding only the current prefix before each query.

    Previous terminal conditions have independent activation variables and
    may be false. R=0 loses no solution because NAE projections and terminal
    NAE are complement invariant; this invariance is asserted independently.
    """
    from pysat.solvers import Solver
    assert all(tuple(1 - bit for bit in state) in relation for state in relation)
    ref, next_id = 1, 5
    old = [2, 3, 4]
    records = []
    started = time.perf_counter()
    with Solver(name="cadical153", bootstrap_with=[[-ref]]) as solver:
        for t in range(1, depth + 1):
            row = list(range(next_id, next_id + len(old) + 1))
            next_id += len(row)
            for i, new in enumerate(row):
                ids = slots("rule 60", i, old, new, ref)
                for state in STATES4:
                    if state in relation:
                        continue
                    literals = {(-v if bit else v) for v, bit in zip(ids, state)}
                    if not any(-literal in literals for literal in literals):
                        solver.add_clause(sorted(literals))
            active = next_id
            next_id += 1
            for i in range(len(row) - 2):
                triple = row[i:i + 3]
                solver.add_clause([-active] + triple)
                solver.add_clause([-active] + [-v for v in triple])
            before = time.perf_counter()
            alive = solver.solve(assumptions=[active])
            record = {"depth": t, "alive": alive, "solve_seconds": time.perf_counter() - before}
            if alive:
                positive = {v for v in solver.get_model() if v > 0}
                record["initial_seed_R0"] = [int(v in positive) for v in (2, 3, 4)]
                record["last"] = "".join(str(int(v in positive)) for v in row)
                assert closure([int(v in positive) for v in row])
            records.append(record)
            old = row
        stats = solver.accum_stats()
    return records, {"elapsed_seconds": time.perf_counter() - started, "SAT_stats": stats}


def word_growth(rule, depth):
    """Exact packed-word recurrence, independent of GF(2) coefficient forms.

    R=0 is sufficient by complement symmetry. Low bits are the initial three
    positions. Missing positions are zero. The observed word has t+3 bits.
    """
    words = list(range(8))
    sequence, seeds = [], []
    for t in range(1, depth + 1):
        if rule == "rule 60":
            words = [word ^ (word << 1) for word in words]
        elif rule == "rule 90":
            words = [(word << 1) ^ (word >> 1) for word in words]
        elif rule == "rule 150":
            words = [word ^ (word << 1) ^ (word >> 1) for word in words]
        elif rule == "rule 102":
            words = [word ^ (word >> 1) for word in words]
        else:
            raise ValueError(rule)
        valid_triple_starts = (1 << (t + 1)) - 1
        accepted = []
        for initial, word in enumerate(words):
            zeros, ones = ~word, word
            bad0 = zeros & (zeros >> 1) & (zeros >> 2) & valid_triple_starts
            bad1 = ones & (ones >> 1) & (ones >> 2) & valid_triple_starts
            if not (bad0 or bad1):
                accepted.append(initial)
        sequence.append(bool(accepted))
        seeds.append(accepted)
    return sequence, seeds


def exhaustive_two_depth_control(relation):
    """Enumerate complete tiny row assignments, without SAT or CNF."""
    verdicts = []
    for target in (1, 2):
        allowed = False
        for initial in product((0, 1), repeat=3):
            frontier = [initial]
            for t in range(1, target + 1):
                next_frontier = []
                for old in frontier:
                    for row in product((0, 1), repeat=len(old) + 1):
                        if all(slots("rule 60", i, old, row[i], 0) in relation for i in range(len(row))):
                            next_frontier.append(row)
                frontier = next_frontier
            if any(closure(row) for row in frontier):
                allowed = True
                break
        verdicts.append(allowed)
    return verdicts


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--phase", choices=("projections", "parity", "mutants", "algebra"), required=True)
    p.add_argument("--depth", type=int, default=64)
    args = p.parse_args()
    start = time.perf_counter()
    result = json.loads(OUT.read_text()) if OUT.exists() else {}
    s1 = json.loads((DATA / "s1.json").read_text())
    gadget = [tuple(x) for x in s1["table"]["3"]["gadget"]]
    inputs = [DATA / "s1.json", DATA / "s2.json", DATA / "summary.json"] + sorted(DATA.glob("s3_*.jsonl"))
    inputs += [ROOT / "research/CHEAP-COUNT-20261112-001" / name
               for name in ("preregistration.md", "cheap_count.md")]
    result["provenance"] = {
        "scope_kind": "epic", "scope_id": "CHEAP-COUNT-20261112-001",
        "independent_code": "No import or call of census.py; independently implemented Boolean enumeration, GF(2), and SAT CNF.",
        "input_sha256": {str(x.relative_to(ROOT)): digest(x) for x in inputs},
        "python": sys.executable, "thread_id": os.environ.get("CODEX_THREAD_ID"),
        "script_sha256": digest(Path(__file__)),
        "limits": {"cpu_seconds": 570, "wall_alarm_seconds": 580, "address_space_bytes": 7 * 1024**3},
    }
    if args.phase == "projections":
        relation, counts = projection(gadget)
        assert relation == EVEN
        mutations, relations = mutate(gadget)
        original = [json.loads(line) for path in sorted(DATA.glob("s3_*.jsonl"))
                    for line in path.read_text().splitlines() if line]
        index = {(x["kind"], x["j"], tuple(x["k"]) if x["k"] else None): x for x in original}
        discrepancies = []
        for row in mutations:
            key = row["kind"], row["j"], row["k"]
            prior = index.get(key)
            if prior is None or prior["rel_size"] != row["rel_size"] or (prior["cls"] == "same parity") != row["same_parity"]:
                discrepancies.append({"key": key, "original": prior, "recomputed": row})
        result["projection_checks"] = {
            "first_f3_gadget": gadget, "even_parity_exact": True,
            "odd_states_have_no_extension": True, "named_witness_counts": counts,
            "copy_primitives": check_copy_primitives(),
            "mutation_count": len(mutations), "same_parity_count": sum(x["same_parity"] for x in mutations),
            "unique_projected_relations": len(relations),
            "relation_multiplicities": dict(Counter(x["relation_mask"] for x in mutations)),
            "original_rows": len(original), "original_unique_keys": len(index),
            "original_projection_discrepancies": discrepancies,
        }
        result["mutations"] = mutations
        print(json.dumps(result["projection_checks"], indent=2))
    elif args.phase == "parity":
        s2 = json.loads((DATA / "s2.json").read_text())
        relation, counts = projection(gadget)
        assert relation == EVEN
        direct = {rule: linear_growth(rule, args.depth) for rule in RULES}
        parity_result = {}
        for rule in RULES:
            sequence = [r["alive"] for r in direct[rule]]
            computed = seq_string(sequence)
            via = projected_gadget_growth(rule, relation, args.depth) if rule in ("rule 60", "hop") else None
            if via is not None:
                assert [(r["alive"], r["seed_count"]) for r in via] == [(r["alive"], r["seed_count"]) for r in direct[rule]]
            parity_result[rule] = {
                "sequence": computed, "alive_depths": [i + 1 for i, a in enumerate(sequence) if a],
                "original_equal": computed == s2[rule]["direct"][:args.depth],
                "finite_prefix_class": finite_class(sequence), "raw_GF2": direct[rule],
                "gadget_by_exact_disjoint_projection_equal": True if via is not None else None,
                "gadget_raw": via,
            }
        expected = set(range(1, 7)) | set(range(11, 15)) | set(range(27, 31)) | set(range(59, 63))
        assert set(parity_result["rule 60"]["alive_depths"]) == {x for x in expected if x <= args.depth}
        result["parity_growth"] = parity_result
        result["parity_controls"] = {
            "strict_NAE_full_system_SAT": small_sat_controls(gadget, direct, min(args.depth, 8)),
            "odd_parity_rule60": {
                "sequence": seq_string(r["alive"] for r in linear_growth("rule 60", args.depth, odd=True)),
                "projection_disjoint_from_even": not any(x in relation for x in STATES4 if sum(x) % 2),
            },
            "collision_justification": "Each collided slot gets a fresh distinct copy; equality is two strict-NAE inequalities. Full primitive truth tables verified. Every gadget uses disjoint helpers. Hence local existential elimination commutes with conjunction for all tested depths.",
            "verification_boundary": "Depths 1..64: exact full-system quantified elimination from independently exhausted local gadget/copy relations plus exhaustive 16-seed propagation. Depths 1..8: additional whole-system SAT for direct clauses and strict NAE gadgets. At depth64 the whole strict NAE formula is rebuilt and checked for distinct variables in every triple; it is not submitted to whole-system SAT.",
            "source_lifetime": "All initial variables and R are existential open choices; no executor supplies values.",
            "strict_NAE_depth64_structure": {rule: strict_gadget_cnf(rule, args.depth, gadget)[1]
                                              for rule in ("rule 60", "hop")},
        }
        print(json.dumps({rule: {k: v for k, v in x.items() if k not in ("raw_GF2", "gadget_raw")} for rule, x in parity_result.items()}, indent=2))
    elif args.phase == "mutants":
        mutations, relations = mutate(gadget)
        original = [json.loads(line) for path in sorted(DATA.glob("s3_*.jsonl"))
                    for line in path.read_text().splitlines() if line]
        original_index = {(x["kind"], x["j"], tuple(x["k"]) if x["k"] else None): x for x in original}
        growth = {}
        for index, (mask, relation) in enumerate(sorted(relations.items())):
            if relation == EVEN:
                raw = linear_growth("rule 60", args.depth)
                stats = {"method": "exact GF(2) seed enumeration"}
            else:
                raw, stats = exact_relation_growth(relation, args.depth)
                stats["method"] = "incremental exact relation SAT with R=0 by complement symmetry"
            sequence = [x["alive"] for x in raw]
            tiny_control = exhaustive_two_depth_control(relation)
            assert sequence[:2] == tiny_control[:args.depth]
            growth[mask] = {"sequence": seq_string(sequence),
                            "finite_prefix_class": "same parity" if relation == EVEN else finite_class(sequence),
                            "raw": raw, "exhaustive_depth1_and2": tiny_control, **stats}
            print(f"relation {index + 1}/{len(relations)} mask={mask} class={growth[mask]['finite_prefix_class']} seq={growth[mask]['sequence']}", flush=True)
            # Keep bounded completed evidence if a later relation hits the ceiling.
            result["mutant_relation_growth"] = growth
            save(result)
        discrepancies = []
        for row in mutations:
            computed = growth[row["relation_mask"]]
            row["sequence"] = computed["sequence"]
            row["finite_prefix_class"] = computed["finite_prefix_class"]
            prior = original_index[(row["kind"], row["j"], row["k"])]
            if (prior["alive"] is not None and prior["alive"][:args.depth] != row["sequence"]) or prior["cls"] != row["finite_prefix_class"]:
                discrepancies.append({"key": (row["kind"], row["j"], row["k"]),
                                      "original": prior, "recomputed": row})
        result["mutations"] = mutations
        result["mutant_summary"] = {
            "depth": args.depth, "count": len(mutations), "unique_relations": len(growth),
            "finite_prefix_classes": dict(Counter(x["finite_prefix_class"] for x in mutations)),
            "same_parity_mutations": [{k: v for k, v in x.items() if k in ("kind", "j", "k")} for x in mutations if x["same_parity"]],
            "original_discrepancies": discrepancies,
            "counting_fraction_under_preregistered_finite_rule": sum(x["same_parity"] or x["finite_prefix_class"] == "unexplained" for x in mutations) / len(mutations),
            "all_deletions_alive_through_horizon": all(set(x["sequence"]) == {"1"} for x in mutations if x["kind"] == "delete"),
            "constant_prefix_breakdown": dict(Counter(x["sequence"][0] for x in mutations if x["finite_prefix_class"] == "constant")),
            "settling_prefix_last_alive_depths": dict(Counter(max(i + 1 for i, value in enumerate(x["sequence"]) if value == "1")
                                                               for x in mutations if x["finite_prefix_class"] == "eventually constant")),
            "enumeration_arithmetic": "C(7,3)-C(4,3)=31 admissible triples;12 deletions+12*(31-12) replacements=240.",
            "minimality_implications": [
                "For a proven minimum f3 gadget with 12 constraints, deleting one cannot preserve the exact parity; otherwise a smaller gadget would exist.",
                "A parity-preserving replacement has 12 constraints and is therefore another minimum f3 gadget.",
                "Minimality alone does not determine which replacements preserve parity, or whether other projected relations have nonperiodic alive sequences.",
            ],
            "scope": "The 169 constant and 68 eventually constant labels describe the tested 1..64 prefix under the registered classifier. They are not all-depth theorems; nor is unexplained proof of counting.",
        }
        print(json.dumps(result["mutant_summary"], indent=2))
    elif args.phase == "algebra":
        algebra = {}
        for rule in ("rule 60", "rule 90", "rule 150", "rule 102"):
            sequence, seeds = word_growth(rule, args.depth)
            control = linear_growth(rule, min(64, args.depth))
            assert sequence[:len(control)] == [x["alive"] for x in control]
            assert [2 * len(x) for x in seeds[:len(control)]] == [x["seed_count"] for x in control]
            alive = [i + 1 for i, value in enumerate(sequence) if value]
            algebra[rule] = {
                "depth": args.depth, "alive_depths": alive,
                "sequence": seq_string(sequence),
                "seed_words_at_alive_depths": {i + 1: x for i, x in enumerate(seeds) if x},
                "matches_independent_GF2_forms_through64": True,
            }
        result["algebra_extension"] = algebra
        result["claim_scope_notes"] = {
            "P3": "The report explicitly marks P3 failed and reproduces hop alive 1..7,9,11, then dead 12..64, so the registered finite prediction failure is honestly disclosed. An all-depth no-counting/death claim is not established by this finite prefix.",
            "rules90_150": "Exact finite sequences match, and the packed-word recurrences supply an exact uniform depth predicate for this one-sided boundary and terminal closure. Dependence on binary depth in additive automata alone is not a proof that this closure's satisfiability sequence is nonperiodic. The registered observation is unexplained within 64 (no period<=16 with onset<=32). A theorem for that exact predicate or a directly applicable cited theorem is needed for the stronger phrase count too.",
            "additive_algebra": "After x_i := main_i XOR R, all four additive rules have zero exterior and three free initial bits. Rule60 is W XOR (W<<1); rule90 is (W<<1) XOR (W>>1); rule150 adds W; rule102 is W XOR (W>>1). The length is t+3, and terminal NAE forbids000 and111 among all consecutive triples. The formulas, not a generic CA picture, specify the exact tested depth predicate.",
            "extension_evidence_class": "Finite exact computation beyond the preregistered horizon, clearly separated; not a proof of all-depth behavior or a new registered result.",
            "rule102": "The zero-exterior recurrence gives one more zero at the right on each update, so at t>=3 the last three relative bits are all zero and terminal NAE fails. This elementary induction extends its observed death beyond64; no analogous proof is supplied here for hop.",
        }
        print(json.dumps({rule: {k: v for k, v in x.items() if k not in ("sequence", "seed_words_at_alive_depths")} for rule, x in algebra.items()}, indent=2))
    result.setdefault("invocations", []).append({"phase": args.phase, "depth": args.depth,
                                                "script_sha256": digest(Path(__file__)),
                                                "elapsed_seconds": time.perf_counter() - start,
                                                "peak_rss_KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
    save(result)


if __name__ == "__main__":
    main()
