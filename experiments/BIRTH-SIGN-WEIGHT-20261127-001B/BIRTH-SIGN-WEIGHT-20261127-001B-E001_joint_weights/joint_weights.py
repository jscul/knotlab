"""Exact finite checks for the two stopping rounds and the three-child founder."""

import argparse
import json
import os
import resource
import subprocess
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations, permutations, product
from pathlib import Path
from time import perf_counter


ROOT = Path(__file__).resolve().parents[3]
PRIOR = ROOT / "research/FACTOR-WEIGHTS-20261126-001"
sys.path.insert(0, str(PRIOR))
import countings


def bits(word):
    return "".join(map(str, word))


def strings(table):
    return [[str(weight) for weight in row] for row in table]


def determinant(table):
    return table[0][0] * table[1][1] - table[0][1] * table[1][0]


def grow(start, rounds):
    stages = [start]
    rosters = []
    for _ in range(rounds):
        stage, status, births = countings.forbid.grown(stages[-1], "nae", "ordinary")
        assert status == "funded"
        stages.append(stage)
        rosters.append(births)
    return stages, rosters


def words(clauses):
    names = sorted({d for clause in clauses for d in clause})
    assert names == list(range(len(names)))
    return set(countings.allowed_words(clauses, names, "nae"))


def two_stops(full):
    record = json.loads((PRIOR / "referee-R1/part_a_full.json").read_text())
    case = next(c for c in record["rows"]["nae / ordinary"]["control failures"] if c["census index"] == 23)
    start = countings.forbid.supports_of(countings.forbid.census()[23])
    assert [list(c) for c in start] == case["start rules"]
    stages, rosters = grow(start, 2)
    births = [[[list(b["inputs"]), list(b["fresh"])] for b in roster] for roster in rosters]
    assert births == case["births"]
    old = (1, 0, 1, 0, 0, 0, 0)
    assert old in words(start)
    first = sorted(w for w in words(stages[1]) if w[:7] == old)
    finished = words(stages[2])
    counts = Counter(w[:10] for w in finished if w[:7] == old)
    stopped = [Fraction(1, len(first))] * len(first)
    continued = [Fraction(counts[w], counts.total()) for w in first]
    result = {
        "source": "FACTOR-WEIGHTS referee R1, NAE / ordinary, census 23",
        "old_state": bits(old), "start_rules": start, "births_by_round": births,
        "first_fresh_states": [bits(w[7:]) for w in first],
        "numbers_of_later_completions": [counts[w] for w in first],
        "at_first_stop": list(map(str, stopped)),
        "at_second_stop_then_forget": list(map(str, continued)),
        "total_variation": str(sum(abs(x-y) for x, y in zip(stopped, continued)) / 2),
    }
    assert continued == [Fraction(1, 2), Fraction(1, 4), Fraction(1, 4)]
    if full:
        D, weights = countings.weightings(stages, rosters, "nae")
        archived = case["first table"]
        fixed = {int(d): v for d, v in archived["other values"].items()}
        a, b = archived["pair"]
        assert not any(a in r and b in r for r in stages[-1])
        tables = {}
        for name, measure in weights.items():
            table = [[Fraction() for _ in range(2)] for _ in range(2)]
            for w, mass in measure.items():
                if all(w[D.index(d)] == v for d, v in fixed.items()):
                    table[w[D.index(a)]][w[D.index(b)]] += mass
            tables[name] = {"mass": strings(table), "determinant": str(determinant(table))}
        assert tables["one stage"]["determinant"] == "1/1620"
        assert tables["start"]["determinant"] == tables["finish"]["determinant"] == "0"
        result.update({"archived_readers": [a, b], "archived_fixed_others": fixed,
                       "tables_before_common_start_weight": tables, "old_state_count": len(words(start))})
    return result


def orbit_kernel(old, *, fix_old_names=False):
    """Actual fresh assignments; all old-value-preserving sibling permutations and fresh-pair swaps."""
    group = [p for p in permutations(range(3)) if tuple(old[i] for i in p) == old]
    if fix_old_names:
        group = [(0, 1, 2)]
    choices = [[p for p in product((0, 1), repeat=2) if len(set((bit,) + p)) > 1] for bit in old]
    classes = defaultdict(list)
    for word in product(*choices):
        # Sorting each fresh pair quotients its transposition. The remaining permutations act on siblings.
        unordered = tuple(tuple(sorted(pair)) for pair in word)
        key = min(tuple(unordered[i] for i in perm) for perm in group)
        classes[key].append(word)
    dist = {w: Fraction(1, len(classes) * len(members)) for members in classes.values() for w in members}
    assert sum(dist.values()) == 1
    return dist, sorted(len(members) for members in classes.values())


def same_class(pair):
    return 0 if pair[0] == pair[1] else 1  # 0 = equal fresh values, 1 = mixed


def table_for(dist, readers, read=same_class):
    left, right = readers
    table = [[Fraction() for _ in range(2)] for _ in range(2)]
    for word, weight in dist.items():
        table[read(word[left])][read(word[right])] += weight
    return table


def matched_table(table):
    rows = list(map(sum, table))
    cols = list(map(sum, zip(*table)))
    return [[r * c for c in cols] for r in rows]


def primary_founder():
    stages, rosters = grow(((0, 1, 2),), 1)
    births = sorted(rosters[0], key=lambda b: b["inputs"])
    assert [(b["inputs"], b["fresh"]) for b in births] == [((0,), (3, 4)), ((1,), (5, 6)), ((2,), (7, 8))]
    old = (0, 0, 1)
    dist, sizes = orbit_kernel(old)
    table = table_for(dist, (0, 1))
    assert determinant(table) == Fraction(1, 12)
    assert table_for(orbit_kernel(old, fix_old_names=True)[0], (0, 1)) == matched_table(table)
    return {
        "founder_state": bits(old), "grown_rules": stages[-1],
        "current_classes": len(sizes), "class_sizes": sizes, "positive_fresh_words": len(dist),
        "classes_equal_mixed_table": strings(table), "determinant": str(determinant(table)),
        "same_marginals_independent": strings(matched_table(table)),
        "fixing_each_old_identity": strings(table_for(orbit_kernel(old, fix_old_names=True)[0], (0, 1))),
    }


def full_founder():
    old_states = sorted(words(((0, 1, 2),)))
    pooled = Counter()
    rows = []
    for old in old_states:
        dist, sizes = orbit_kernel(old)
        peers = next((i, j) for i, j in combinations(range(3), 2) if old[i] == old[j])
        assert determinant(table_for(dist, peers)) == Fraction(1, 12)
        # All founder permutations and complementary old/fresh values carry the labelled measure.
        for p in permutations(range(3)):
            other, _ = orbit_kernel(tuple(old[i] for i in p))
            assert all(other[tuple(w[i] for i in p)] == mass for w, mass in dist.items())
        inverted, _ = orbit_kernel(tuple(1 - b for b in old))
        assert all(inverted[tuple(tuple(1 - b for b in pair) for pair in w)] == mass for w, mass in dist.items())
        for w, mass in dist.items():
            pooled[w] += mass / len(old_states)
        rows.append({"old": bits(old), "same_input_children": peers, "class_sizes": sizes,
                     "table": strings(table_for(dist, peers))})

    old = (0, 0, 1)
    dist, _ = orbit_kernel(old)
    left_right = Counter()
    third = Counter()
    for w, mass in dist.items():
        left_right[w[:2]] += mass
        third[w[2]] += mass
    assert all(left_right[w[:2]] * third[w[2]] == mass for w, mass in dist.items())
    fine_words = sorted({a for a, b in left_right})
    fine = [[left_right[a, b] for b in fine_words] for a in fine_words]
    assert fine == [[Fraction(4 if a == b == (1, 1) else 1, 12) for b in fine_words] for a in fine_words]
    named = {w: Fraction(1, len(dist)) for w in dist}
    # Reinforce the class, then split fresh mixed representatives uniformly for each child independently.
    alpha = (1, 2)
    urn = [[Fraction(a, sum(alpha)) * Fraction(b + (i == j), sum(alpha) + 1)
            for j, b in enumerate(alpha)] for i, a in enumerate(alpha)]
    names_per_class = Counter(map(same_class, fine_words))
    urn_full = [[urn[same_class(a)][same_class(b)] / (names_per_class[same_class(a)] * names_per_class[same_class(b)])
                 for b in fine_words] for a in fine_words]
    assert all(sum(row) == Fraction(1, 3) for row in urn_full)
    assert all(sum(col) == Fraction(1, 3) for col in zip(*urn_full))
    pooled_table = table_for(pooled, (0, 1))
    return {
        "all_six_founder_states": rows, "fine_pair_names": list(map(bits, fine_words)),
        "fine_pair_table": strings(fine), "third_child_is_independent_given_001": True,
        "single_fresh_bit_per_child": strings(table_for(dist, (0, 1), lambda pair: pair[0])),
        "single_bit_determinant": str(determinant(table_for(dist, (0, 1), lambda pair: pair[0]))),
        "all_founder_words_uniform_fixed_pair": strings(pooled_table),
        "pooled_determinant": str(determinant(pooled_table)),
        "uniform_named_completions_class_table": strings(table_for(named, (0, 1))),
        "urn_class_counts": alpha, "urn_class_table": strings(urn), "urn_determinant": str(determinant(urn)),
        "urn_fine_table_preserves_named_marginals": strings(urn_full),
        "positive_weights_given_001": {" ".join(map(bits, w)): str(p) for w, p in sorted(dist.items())},
    }


def canonical_scope(clauses, old, scope):
    """Give knotlab the full actual source and quantify away every omitted distinction."""
    clauses_text = []
    for row in clauses:
        clauses_text += [" ".join(f"v{d}" for d in row), " ".join(f"~v{d}" for d in row)]
    if old is not None:
        clauses_text.extend(("" if bit else "~") + f"v{i}" for i, bit in enumerate(old))
    others = [d for d in range(9) if d not in scope]
    command = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", ";".join(clauses_text),
               "--loops", *(f"v{d}" for d in scope[:-1]), "--contact", f"v{scope[-1]}",
               "--witnesses", *(f"v{d}" for d in others), "--json"]
    check = subprocess.run(command, cwd=ROOT, env={**os.environ, "PYTHONPATH": str(ROOT / "tools")},
                           capture_output=True, text=True, check=True)
    report = json.loads(check.stdout)
    return {"scope": scope, "command_args": command[2:], "allowed_patterns": len(report["allowed"]),
            "K1": report["binding"], "K2": report["loss_on_erasure"], "K3": report["coexistence"],
            "is_knot": report["is_knot"]}


def support_checks(full):
    stages, _ = grow(((0, 1, 2),), 1)
    clauses = stages[-1]
    all_states = words(clauses)
    scope = (2, 3, 4, 5, 6)
    if not full:
        return {"canonical_five_place_control": canonical_scope(clauses, None, scope)}
    outputs = {}
    for label, old in [("full", None), ("founder_fixed", (0, 0, 1))]:
        actual = {w for w in all_states if old is None or w[:3] == old}
        weighted = set()
        for start in {w[:3] for w in actual}:
            dist, _ = orbit_kernel(start)
            weighted.update(start + sum(fresh, ()) for fresh, weight in dist.items() if weight > 0)
        assert actual == weighted
        masks = {sum(1 << i for i, bit in enumerate(w) if bit) for w in actual}
        counts = {s: len({w & s for w in masks}) for s in range(512)}
        knots = []
        for s in range(512):
            k = s.bit_count()
            if k < 3 or counts[s] == 1 << k:
                continue
            members = tuple(i for i in range(9) if s & (1 << i))
            if all(counts[s ^ (1 << i)] == 1 << (k - 1) for i in members):
                knots.append(members)
        crossing = [k for k in knots if {3, 4}.intersection(k) and {5, 6}.intersection(k)]
        checks = [canonical_scope(clauses, old, k) for k in sorted({(0, 1, 2), scope, (3, 4, 5, 6, 7, 8)} | set(crossing))]
        assert all(row["is_knot"] == (row["scope"] in knots) for row in checks)
        outputs[label] = {"positive_states": len(actual), "scopes_of_arity_at_least_three": 466,
                          "all_knots": knots, "knots_meeting_both_fresh_pairs": crossing,
                          "canonical_checks": checks}
    assert not outputs["founder_fixed"]["all_knots"]
    assert len(outputs["full"]["knots_meeting_both_fresh_pairs"]) == 2
    return outputs


def max_value_chsh(table):
    """All binary deterministic readings, with constants and repeated settings allowed."""
    n = len(table)
    funcs = list(product((-1, 1), repeat=n))
    e = [[sum(a[i] * b[j] * table[i][j] for i in range(n) for j in range(n)) for b in funcs] for a in funcs]
    return max(max(abs(x + y) for x, y in zip(row0, row1)) + max(abs(x - y) for x, y in zip(row0, row1))
               for row0 in e for row1 in e)


def coherent(full):
    import sympy as sp

    eye, X = sp.eye(2), sp.Matrix([[0, 1], [1, 0]])
    Y, Z = sp.Matrix([[0, -sp.I], [sp.I, 0]]), sp.diag(1, -1)
    # Columns label E and M; the four rows label fresh states 00, 01, 10, 11.
    V = sp.Matrix([[0, 0], [0, 1 / sp.sqrt(2)], [0, 1 / sp.sqrt(2)], [1, 0]])
    assert V.T * V == eye
    dist, _ = orbit_kernel((0, 0, 1))
    joint = table_for(dist, (0, 1))
    pairs = list(product((0, 1), repeat=2))
    results = {}
    for label, table in [("orbit", joint), ("matched_independent", matched_table(joint))] if full else [("orbit", joint)]:
        amplitudes = sp.Matrix(table).applyfunc(sp.sqrt)
        psi = amplitudes.reshape(4, 1)

        def expectation(state, left, right):
            return sp.simplify((state.H * sp.kronecker_product(left, right) * state)[0])

        corr = sp.Matrix([[expectation(psi, a, b) for b in (X, Y, Z)] for a in (X, Y, Z)])
        spectrum = sorted((corr.T * corr).diagonal(), reverse=True)
        assert corr.is_diagonal()
        upper = 2 * sp.sqrt(sum(spectrum[:2]))
        if label == "orbit":
            bob = [(3 * X + Z) / sp.sqrt(10), (3 * X - Z) / sp.sqrt(10)]
        else:
            bob = [X, X]
        alice = [X, Z]
        for read in alice + bob:
            assert read.H == read and sp.simplify(read * read) == eye
        es = [expectation(psi, a, b) for a in alice for b in bob]
        attained = sp.simplify(sum(es[:3]) - es[3])
        assert attained == upper
        result = {"value_read_max": str(max_value_chsh(table)),
                  "sqrt_amplitudes_determinant": str(amplitudes.det()),
                  "XX_YY_ZZ": list(map(str, corr.diagonal())),
                  "correlations_at_attaining_reads": list(map(str, es)),
                  "arbitrary_local_read_max": str(upper)}
        if full:
            fine = [[Fraction() for _ in pairs] for _ in pairs]
            for w, mass in dist.items():
                fine[pairs.index(w[0])][pairs.index(w[1])] += mass
            if label == "matched_independent":
                fine = matched_table(fine)
            full_amplitudes = sp.Matrix(fine).applyfunc(sp.sqrt)
            assert sp.simplify(full_amplitudes - V * amplitudes * V.T) == sp.zeros(4)
            full_psi = full_amplitudes.reshape(16, 1)
            # Extend each read by +1 on the two-dimensional orthogonal complement.
            def lift(read):
                return V * read * V.T + sp.eye(4) - V * V.T

            lifted = [lift(r) for r in alice + bob]
            assert all(sp.simplify(r * r) == sp.eye(4) for r in lifted)
            full_es = [expectation(full_psi, a, b) for a in lifted[:2] for b in lifted[2:]]
            assert full_es == es
            active = [row[1:] for row in fine[1:]]  # 00 has no weight at old input 0.
            result.update({"fine_value_read_max": str(max_value_chsh(active)),
                           "fine_amplitudes_shape": [4, 4], "fine_isometry": True,
                           "fine_attained": str(sp.simplify(sum(full_es[:3]) - full_es[3]))})
        results[label] = result
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    started = perf_counter()
    out = {"mode": "pilot" if args.pilot else "full", "phases_seconds": {}}

    def run(name, function, *args):
        then = perf_counter()
        out[name] = function(*args)
        out["phases_seconds"][name] = round(perf_counter() - then, 6)

    run("two_stops", two_stops, not args.pilot)
    run("founder", primary_founder)
    if not args.pilot:
        run("all_founders_and_controls", full_founder)
    run("support", support_checks, not args.pilot)
    run("coherent_and_value_reads", coherent, not args.pilot)
    out["elapsed_seconds"] = round(perf_counter() - started, 6)
    out["peak_process_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
