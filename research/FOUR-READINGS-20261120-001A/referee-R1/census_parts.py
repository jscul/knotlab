"""Independent finite counts for the signed parity review. Run from the repository root."""
import argparse
from collections import Counter, defaultdict
from contextlib import redirect_stdout
from hashlib import sha256
from io import StringIO
from itertools import combinations, permutations
import json
from pathlib import Path
import resource
import sys
from time import perf_counter

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parent.parent
DATA = next((ROOT / "artifacts" / STUDY.name).glob("*_signed_rules"))


def load(name):
    return json.loads((DATA / name).read_text())


def provenance():
    receipt = load("receipt.json")
    contract = next((ROOT / "experiments" / STUDY.name).glob("*_signed_rules/contract.json"))
    inputs = [(DATA / name, digest) for name, digest in receipt["output_sha256"].items()]
    inputs.extend([(STUDY / "preregistration.md", receipt["design_sha256"]),
                   (contract, receipt["contract_sha256"]),
                   (STUDY / "supplemental_stress_freeze.md",
                    load("supplemental_stress.json")["supplemental_freeze_sha256"])])
    for path, digest in inputs:
        assert sha256(path.read_bytes()).hexdigest() == digest, path
    return len(inputs)


def pattern_counts(n, rows):
    """Expand every supplied representative, then count qualified subsets independently."""
    pairs = list(combinations(range(n), 2))
    pair_bits = {pair: 1 << i for i, pair in enumerate(pairs)}
    all_bits = (1 << len(pairs)) - 1
    incident = [sum(bit for pair, bit in pair_bits.items() if h in pair) for h in range(n)]
    direct = Counter()
    for sharing in range(all_bits + 1):
        if all((sharing & s).bit_count() >= 3 for s in incident):
            # Two components of minimum degree three need at least eight holders.
            direct[sharing.bit_count()] += 1
    expected = {int(k): v for k, v in load("labelled_denominators.json")[str(n)].items()}
    assert direct == expected

    renamed_bits = [[pair_bits[tuple(sorted((p[a], p[b])))] for a, b in pairs]
                    for p in permutations(range(n))]
    represented = set()
    count_by_size = Counter()
    yes = 0
    for row in rows:
        pattern = {tuple(meeting) for meeting in row["sharing"]}
        assert len(pattern) == len(row["sharing"]) == row["m"]
        assert pattern <= set(pairs)
        assert all(sum(h in meeting for meeting in pattern) >= 3 for h in range(n))
        # Naming the missing meetings costs less on these almost-full patterns.
        missing = [i for i, pair in enumerate(pairs) if pair not in pattern]
        orbit = {all_bits ^ sum(p[i] for i in missing) for p in renamed_bits}
        assert len(orbit) == row["labelled"] and represented.isdisjoint(orbit)
        represented.update(orbit)
        count_by_size[len(pattern)] += len(orbit)
        if row["operator"]:
            yes += len(orbit)
    assert count_by_size == direct
    return {"types": len(rows), "labelled": direct.total(), "operator_labelled": yes}


def connected(group, sharing):
    seen = {min(group)}
    while True:
        more = {u for x, y in sharing for u, v in [(x, y), (y, x)]
                if v in seen and u in group}
        if more <= seen:
            return seen == group
        seen |= more


def group_reading(n, sharing):
    # Contract adjacent groups recursively. An unused holder can be absorbed
    # into a neighbouring group until all holders belong to a group.
    def visit(groups):
        key = tuple(sorted(groups))
        if key in visited:
            return False
        visited.add(key)
        meets = {(a, b) for a, b in combinations(range(len(groups)), 2)
                 if any((x in groups[a] and y in groups[b]) or
                        (y in groups[a] and x in groups[b]) for x, y in sharing)}
        if len(groups) == 5:
            return len(meets) == 10
        if len(groups) == 6:
            for side in combinations(range(6), 3):
                if sum((a in side) != (b in side) for a, b in meets) == 9:
                    return True
        return any(visit([v for i, v in enumerate(groups) if i not in (a, b)]
                         + [tuple(sorted(groups[a] + groups[b]))]) for a, b in meets)

    visited = set()
    return n >= 5 and visit([(i,) for i in range(n)])


def markers(rows, full):
    signatures = {}
    for row in rows:
        n = row["n"]
        pairs = {tuple(pair) for pair in row["sharing"]}
        assert connected(set(range(n)), pairs)
        verdict = group_reading(n, pairs)
        assert verdict == row["operator"]
        neighbours = [{b if a == j else a for a, b in pairs if j in (a, b)} for j in range(n)]
        # A two-colouring is a finite certificate of the absence of an odd holder loop.
        two_colours = any(all(((mask >> a) ^ (mask >> b)) & 1 for a, b in pairs)
                          for mask in range(1 << (n - 1)))
        weak = any(all(neighbours[h] == set(four) - {h} for h in four)
                   for four in combinations(range(n), 4))
        arities = tuple(sorted(map(len, neighbours)))
        assert list(arities) == row["arities"]
        assert (weak, not two_colours, False) == (
            row["relaxed_Fano_four_triples"], row["has_odd_holder_loop"], row["literal_Fano_piece"])
        signature = (n, len(pairs), arities, len(pairs) - n + 1, weak)
        signatures[row["atlas"]] = (verdict, signature, not two_colours)
    by_size = {}
    archived = load("additional_controls.json")
    for stronger, name in enumerate(("readings_with_fano_degree_and_loop_count",
                                     "readings_including_odd_length")):
        pairs = {(a, b) for a, b in combinations(sorted(signatures), 2)
                 if signatures[a][0] != signatures[b][0]
                 and signatures[a][1:2 + stronger] == signatures[b][1:2 + stronger]}
        expected = {tuple(v) for v in archived[name] if v[0] in signatures and v[1] in signatures}
        assert pairs == expected
        if pairs:
            first = min(pairs, key=lambda ab: (signatures[ab[0]][1][1], ab))
            by_size[name] = [len(pairs), list(first), signatures[first[0]][1][1]]
    if full:
        by_id = {r["atlas"]: {tuple(p) for p in r["sharing"]} for r in rows}
        assert by_id[188] - by_id[189] == {(0, 1)} and by_id[189] - by_id[188] == {(0, 3)}
    return by_size


def k123(active, states):
    mask = sum(1 << i for i in active)
    words = {w & mask for w in states}
    loss = all(len({w & ~(1 << i) for w in words}) == 1 << (len(active) - 1) for i in active)
    return [len(words) < 1 << len(active), loss, bool(words)]


def binary_rank(rows):
    pivots = {}
    for row in rows:
        while row:
            leading = row.bit_length()
            if leading not in pivots:
                pivots[leading] = row
                break
            row ^= pivots[leading]
    return len(pivots)


def deletion_checks(rows):
    saved = {r["atlas"]: r["one_deletion_witnesses"]
             for r in load("scalar_one_deletion_witnesses.json")}
    exceptions = []
    checked = 0
    for row in rows:
        n, m = row["n"], row["m"]
        forms = [sum(1 << j for j, pair in enumerate(row["sharing"]) if i in pair)
                 for i in range(n)]
        # The higher bit is the odd right-hand sign of the last equation.
        system = forms[:-1] + [forms[-1] | (1 << m)]
        assert binary_rank(system) > binary_rank(forms)
        assert row["classical_states"] == 0
        full_at_every_omission = True
        for i, witness in enumerate(saved[row["atlas"]]):
            remaining = forms[:i] + forms[i+1:]
            rank = binary_rank(remaining)
            assert rank == n - 1 and 1 << (m-rank) == row["states_after_one_rule_deleted"]
            assert witness < 1 << m and all((witness & form).bit_count() % 2 == (j == n-1)
                                           for j, form in enumerate(forms) if i != j)
            units = [1 << j for j in range(m) if (1 << j) & forms[i]]
            projected_rank = binary_rank(remaining + units) - rank
            if projected_rank != len(units) - 1:
                full_at_every_omission = False
                exceptions.append([row["atlas"], i, 1 << projected_rank, 1 << (len(units)-1)])
            checked += 1
        assert len(saved[row["atlas"]]) == n
        assert full_at_every_omission == row["deleted_star_implies_full_opposite_rule_for_every_choice"]
    return {"single_deletions": checked, "omitted_rules_with_extra_restrictions": exceptions}


def six_parts(count):
    # The CLI is an extra cross-check of the independent state enumeration.
    sys.path.insert(0, str(ROOT / "tools"))
    from knotlab.cli import main as knot_check

    rules = [list(range(first, first + 3)) for first in (0, 3, 6)]
    rules += [list(range(first, 9, 3)) for first in range(3)]
    masks = [sum(1 << i for i in rule) for rule in rules]
    history = {tuple(r["retained"]): r for r in load("six_parts.json")}
    assert len(history) == 64
    part_sizes = defaultdict(set)
    for subset in range(count):
        required = tuple(i for i in range(6) if (subset >> i) & 1)
        states = [w for w in range(512) if all(
            (w & masks[i]).bit_count() % 2 == (i == 5) for i in required)]
        part_sizes[len(required)].add(len(states))
        active = sorted({i for j in required for i in rules[j]})
        projected = {w & sum(1 << i for i in active) for w in states}
        record = history[required]
        gates = k123(active, states)
        assert (active, len(states), len(projected), gates) == (
            record["active"], record["ambient_models"], record["relation_models"], record["K123"])
        if active:
            clauses = []
            for i in required:
                for word in range(8):
                    if word.bit_count() % 2 != (i == 5):
                        literals = [("~" if (word >> k) & 1 else "") + f"d{d}"
                                    for k, d in enumerate(rules[i])]
                        clauses.append(" ".join(literals))
            names = [f"d{d}" for d in active]
            output = StringIO()
            with redirect_stdout(output):
                status = knot_check(["check", "--cnf", ";".join(clauses), "--loops", *names[:-1],
                                     "--contact", names[-1], "--json"])
            checked = json.loads(output.getvalue())
            assert status == 0 and gates == [checked[k] for k in ("binding", "loss_on_erasure", "coexistence")]
        assert len(record["stars"]) == 6
        for i, r in enumerate(record["stars"]):
            words = sorted({''.join(str((w >> j) & 1) for j in rules[i]) for w in states})
            assert (i, words, i in required, k123(rules[i], states)) == (
                r["holder"], r["allowed"], r["imposed"], r["K123"])
    return {i: sorted(s) for i, s in part_sizes.items()}


def incidence_control():
    # The seven nonzero binary triples have a unique third label a xor b per pair.
    triples = {tuple(sorted((a, b, a ^ b))) for a, b in combinations(range(1, 8), 2)}
    saved = load("marker_controls.json")
    assert triples == {tuple(t) for t in saved["fano"]}
    for j, tri in enumerate(map(tuple, saved["fano"])):
        degrees = sorted(sum(i in t for t in triples - {tri}) for i in range(1, 8))
        assert degrees == saved["Fano_minus_holder_degrees"][str(j)]
    for removed in range(1, 8):
        rest = [set(t) - {removed} for t in triples]
        degrees = sorted(sum(i in t for t in rest) for i in set(range(1, 8)) - {removed})
        assert degrees == saved["Fano_minus_distinction_degrees"][str(removed)]
        kept = [set(t) for t in triples if removed not in t]
        assert len(kept) == 4 and all(len(a & b) == 1 for a, b in combinations(kept, 2))

    def nae_count(rules, names):
        masks = [sum(1 << i for i in t) for t in rules]
        return sum(all(0 < w & m < m for m in masks) for w in range(1 << names))

    six = [range(i, i + 3) for i in [0, 3, 6]] + [range(i, 9, 3) for i in range(3)]
    counts = [nae_count([tuple(i - 1 for i in t) for t in triples], 7), nae_count(six, 9)]
    assert counts == [saved["fano_NAE_states"], saved["six_NAE_states"]]
    return counts


def weighting_control():
    # Knot 0 has even parity, knot 7 has odd parity. Match the first bit.
    legal = [[x for x in range(8) if x.bit_count() % 2 == sign] for sign in (0, 1)]
    left, right = Counter(), Counter()
    weights = Counter()
    for bit in (0, 1):
        answers = [[x for x in words if x & 1 == bit] for words in legal]
        for i, a in enumerate(answers[0]):
            for j, b in enumerate(answers[1]):
                weight = 3 if i == j else 1
                left[a] += weight
                right[b] += weight
                weights[weight] += 1
    assert all(set(v.values()) == {4} and len(v) == 4 for v in (left, right))
    assert weights == {1: 4, 3: 4}
    return {"denominator": 16, "numerator_counts": dict(weights), "marginal_numerator": 4}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="one small instance of each calculation")
    args = parser.parse_args()
    started = perf_counter()
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
    records = load("census.json")
    rows = [r for r in records if r["n"] <= (5 if args.pilot else 7)]
    sizes = sorted({r["n"] for r in rows})
    counts = {n: pattern_counts(n, [r for r in rows if r["n"] == n]) for n in sizes}
    output = {"mode": "pilot" if args.pilot else "full", "input_hashes": provenance(),
              "census": counts, "matched_markers": markers(rows, not args.pilot),
              "scalar_deletions": deletion_checks(rows),
              "six_rule_parts": six_parts(3 if args.pilot else 64), "not_all_equal": incidence_control(),
              "uniform_marginal_control": weighting_control()}
    output.update(seconds=round(perf_counter() - started, 4),
                  peak_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
