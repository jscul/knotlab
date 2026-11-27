"""Project each ordinary stage onto a chosen chain and check all its single-law deletions."""

import argparse
from collections import Counter, defaultdict
from functools import cache, reduce
import gzip
from itertools import combinations, product
import json
from operator import and_
from pathlib import Path
import resource
from time import perf_counter


HERE = Path(__file__).resolve().parent
CHAIN_LAWS = tuple((i, i + 1, i + 2) for i in range(0, 16, 2))
CARRIERS = ((3, 4, 5), (11, 12, 13), (0, 1, 10), (6, 15, 16), (7, 8, 9), (2, 14))
LOWER = ((0, 2, 4), (0, 3, 5), (1, 2, 5), (1, 3, 4))
NAMES = ("A0", "A1", "B0", "B1", "C0", "C1")
ROLES = "ABC"


def conjunction(tables, full):
    return reduce(and_, tables, full)


def words(table, groups):
    return [key for key, values in groups.items() if table & values]


def six_carrier_bonds(six_words):
    """All 20 disjoint-carrier triples. Each true bond must have three free pairs."""
    found = []
    for tr in combinations(range(6), 3):
        fixes = defaultdict(list)
        for w in six_words:
            fixes[tuple(w[i] for i in tr)].append(w)
        if len(fixes) == 8 or any(len({(v[i], v[j]) for v in fixes}) != 4 for i,j in combinations(range(3), 2)):
            continue
        determined = []
        for i, pair in enumerate(ROLES):
            for kind, value in (("both", all), ("either", any)):
                if all(len({value(bit == "1" for bit in w[2*i:2*i+2]) for w in group}) == 1 for group in fixes.values()):
                    determined.append([pair, kind])
        found.append({"triple": tr, "determines": determined})
    return found


class ChainTables:
    def __init__(self):
        # Keep both complementary assignments. Bit s represents the raw
        # chain word whose value on distinction i is bit i of s.
        self.full = (1 << (1 << 17)) - 1
        self.columns = []
        self.zero = []
        for i in range(17):
            width = 1 << i
            zeros = self.full // ((1 << width) + 1)
            self.zero.append(zeros)
            self.columns.append(self.full ^ zeros)
        self.laws = [self.full ^ self.agree(law) for law in CHAIN_LAWS]
        self.bare = conjunction(self.laws, self.full)
        self.dropped = [conjunction(self.laws[:i] + self.laws[i + 1:], self.full) for i in range(8)]
        self.readings = [self.agree(c) for c in CARRIERS]
        self.raw_knot_words = [self.groups([self.columns[i] for i in law]) for law in CHAIN_LAWS]
        self.lower_words = [self.groups([self.readings[i] for i in tr]) for tr in LOWER]
        self.six_words = self.groups(self.readings)
        self.upper_functions = [
            [self.readings[2*i] & self.readings[2*i+1] if i == both
             else self.readings[2*i] | self.readings[2*i+1] for i in range(3)]
            for both in range(3)
        ]
        self.upper_words = [self.groups(fs) for fs in self.upper_functions]

    def agree(self, indices):
        return (conjunction((self.columns[i] for i in indices), self.full) |
                conjunction((self.zero[i] for i in indices), self.full))

    def groups(self, functions):
        return {"".join(map(str, bit_word)): conjunction(
            (f if v else self.full ^ f for f, v in zip(functions, bit_word, strict=True)), self.full)
                for bit_word in product((0, 1), repeat=len(functions))}

    @cache
    def extra_law(self, signed):
        fixed = [self.columns[abs(i)-1] if i > 0 else self.zero[abs(i)-1] for i in signed]
        banned = (conjunction(fixed, self.full) |
                  conjunction((self.full ^ f for f in fixed), self.full))
        return self.full ^ banned

    def flip(self, table, i):
        return ((table & self.zero[i]) << (1 << i)) | ((table & self.columns[i]) >> (1 << i))

    @cache
    def results(self, signature):
        outside = conjunction((self.extra_law(s) for s in signature), self.full)
        allowed = self.bare & outside
        missing = [[w for w, t in group.items() if w != "111" and not allowed & t]
                   for group in self.lower_words]
        assert all(not allowed & group["111"] for group in self.lower_words)
        upper = [words(allowed, group) for group in self.upper_words]
        missing_after_drop = [
            [ROLES[role] for role in range(3) if not remaining & outside & self.upper_words[role]["111"]]
            for remaining in self.dropped]
        # An allowed one-bit flip at an internal shared distinction changes
        # this agreement while preserving every outside knot simultaneously.
        # No such distinction occurs outside the chain.
        flip_nonlocal = []
        for carrier, agreement in zip(CARRIERS, self.readings, strict=True):
            candidates = [i for i in carrier if i % 2 == 0 and 0 < i < 16]
            certified = [i for i in candidates if allowed & agreement & self.flip(allowed & ~agreement, i)]
            flip_nonlocal.append(certified)
        determined_in_chain = [
            (j, i) for j, agreement in enumerate(self.readings) for i, group in enumerate(self.raw_knot_words)
            if all(not (allowed & g & agreement and allowed & g & ~agreement) for g in group.values())]
        upper_local = [
            (role, i, lower_index) for role, fs in enumerate(self.upper_functions)
            for i, f in enumerate(fs) for lower_index, group in enumerate(self.lower_words)
            if all(not (allowed & g & f and allowed & g & ~f) for g in group.values())]
        six_words = words(allowed, self.six_words)
        bonds = six_carrier_bonds(six_words)
        return {
            "projected_chain_assignments": allowed.bit_count(),
            "extra_missing_lower_words": missing,
            "upper_words": upper,
            "roles_still_missing_111_after_deleting_chain_law": missing_after_drop,
            "internal_flip_witnesses_against_all_outside_knots": flip_nonlocal,
            "lower_agreement_read_at_a_chain_knot": determined_in_chain,
            "upper_reading_read_at_a_defining_lower_bond": upper_local,
            "six_word_count": len(six_words), "bonds_on_the_six": bonds,
            "roles_determined_somewhere_on_the_six": [
                both for both in ROLES if any(
                    any((b == both) == (kind == "both") for b, kind in bond["determines"]) for bond in bonds)],
        }


def chain_names(supports, chain):
    members = [set(supports[k]) for k in chain]
    shared = [next(iter(a & b)) for a, b in zip(members, members[1:])]
    loose = [sorted(row - set(shared)) for row in members]
    labels = list(loose[0])
    for i in range(1, 8):
        labels += [shared[i-1], *loose[i]]
    assert len(set(labels)) == len(labels) == 17
    return labels


def off_chain(supports, chain, labels):
    """Exact extension conditions on the chain. Positive/negative i+1 denote opposite signs."""
    inside = {x: i for i, x in enumerate(labels)}
    outside = set(range(len(supports))) - set(chain)
    holders = defaultdict(list)
    for knot in outside:
        for d in supports[knot]:
            holders[d].append(knot)
    adjacent = defaultdict(list)
    free = set()
    for d, using in holders.items():
        if len(using) == 2:
            assert d not in inside
            a, b = using
            adjacent[a].append(b)
            adjacent[b].append(a)
        elif len(using) == 1 and d not in inside:
            free.update(using)
        else:
            assert len(using) == 1
    constraints = []
    while outside:
        root = min(outside)
        parts = {root: 1}
        todo = [root]
        while todo:
            here = todo.pop()
            for there in adjacent[here]:
                if there not in parts:
                    parts[there] = -parts[here]
                    todo.append(there)
        outside.difference_update(parts)
        meetings = sum(len(adjacent[k]) for k in parts) // 2
        if meetings != len(parts) - 1 or not free.isdisjoint(parts):
            continue
        signed = sorted((sign * (1 + inside[d]) for k, sign in parts.items() for d in supports[k] if d in inside),
                        key=abs)
        assert len(signed) >= len(parts) + 2
        if signed[0] < 0:
            signed = [-x for x in signed]
        constraints.append((tuple(signed), tuple(sorted(parts))))
    return sorted(constraints)


def counted(results):
    lower = not any(results["extra_missing_lower_words"])
    upper = all(ws == ["000","001","010","011","100","101","110"] for ws in results["upper_words"])
    lower_nonlocal = (all(results["internal_flip_witnesses_against_all_outside_knots"])
                      and not results["lower_agreement_read_at_a_chain_knot"])
    upper_nonlocal = not results["upper_reading_read_at_a_defining_lower_bond"]
    essential = not any(results["roles_still_missing_111_after_deleting_chain_law"])
    passing_six = [role for role in ROLES if role not in results["roles_determined_somewhere_on_the_six"]]
    passing_six_and_needed = [role for role in passing_six if all(
        role not in failed for failed in results["roles_still_missing_111_after_deleting_chain_law"])]
    original = lower and upper and lower_nonlocal
    return {
        "chains": True, "exact_bare_chain_projection": results["projected_chain_assignments"] == 2 * 3**8,
        "exact_bare_six_reading_image": results["six_word_count"] == 39,
        "four_exact_lower_clauses": lower, "three_seven_word_upper_images": upper,
        "lower_readings_nonlocal_to_every_raw_knot_certified": lower_nonlocal,
        "upper_nonlocal_to_each_defining_lower_bond": upper_nonlocal,
        "all_eight_laws_needed_for_all_three_roles": essential,
        "original_step": original,
        "step_with_defining_bond_check": lower and upper and lower_nonlocal and upper_nonlocal,
        "step_with_defining_bond_check_and_all_eight_needed":
            lower and upper and lower_nonlocal and upper_nonlocal and essential,
        "some_qualifying_role_with_all_bonds_on_the_six": original and bool(passing_six),
        "all_three_qualifying_roles_with_all_bonds_on_the_six": original and len(passing_six) == 3,
        "some_qualifying_role_with_all_bonds_on_the_six_and_all_eight_needed": original and bool(passing_six_and_needed),
        "all_three_qualifying_roles_with_all_bonds_on_the_six_and_all_eight_needed":
            original and len(passing_six_and_needed) == 3,
    }


def minimal_extras(tables, signature):
    """Inclusion-minimal subsets of outside tree conditions producing each exception."""
    minima = defaultdict(list)
    for n in range(len(signature) + 1):
        for indices in combinations(range(len(signature)), n):
            result = tables.results(tuple(signature[i] for i in indices))
            events = []
            for i, missing in enumerate(result["extra_missing_lower_words"]):
                events.extend("missing " + word + " on " + ",".join(NAMES[j] for j in LOWER[i]) for word in missing)
            for i, roles in enumerate(result["roles_still_missing_111_after_deleting_chain_law"]):
                events.extend(f"upper 111 still missing with {role} both after deleting chain law {i+1}" for role in roles)
            for event in events:
                if not any(set(prior).issubset(indices) for prior in minima[event]):
                    minima[event].append(indices)
    return dict(minima)


def direct_projection(tables, supports, chain, labels, constraints):
    """Query every chain assignment satisfying at least seven chain laws, modulo global complementation."""
    from pysat.solvers import Solver
    selectable = max(d for law in supports for d in law) + 2
    cnf = []
    ids = {k: i for i, k in enumerate(chain)}
    for k, law in enumerate(supports):
        values = [d + 1 for d in law]
        selector = [selectable + ids[k]] if k in ids else []
        cnf.extend([selector + values, selector + [-x for x in values]])
    rejected = Counter()
    queries = 0
    with Solver(bootstrap_with=cnf) as solver:
        outside = conjunction((tables.extra_law(s) for s, _ in constraints), tables.full)
        # The bare assignments have a complete eight-law witness. For each
        # omitted law only the assignments violating that law are additional.
        for i, mask in enumerate([tables.bare] + [m & ~tables.bare for m in tables.dropped]):
            candidates = mask & tables.zero[0]
            # Converting to bytes avoids a long reallocated integer per
            # word. All eight selectors are fixed on every query.
            entries = candidates.to_bytes(16384, "little")
            expected = (outside & tables.zero[0]).to_bytes(16384, "little")
            selectors = [(1 if i == j+1 else -1)*(selectable+j) for j in range(8)]
            for offset, val in enumerate(entries):
                while val:
                    least = val & -val
                    bit_index = 8*offset + least.bit_length()-1
                    assumptions = [d+1 if bit_index & (1 << j) else -(d+1) for j, d in enumerate(labels)]
                    actual = solver.solve(assumptions=selectors + assumptions)
                    if actual != bool(expected[offset] & least):
                        raise ValueError(("projection mismatch", chain, i, bit_index))
                    rejected[str(i)] += not actual
                    queries += 1
                    val ^= least
    return {"queries": queries, "rejected_with_no_deletion_then_laws_1_through_8": dict(rejected)}


def all_stages(archive):
    with gzip.open(archive, "rt") as source:
        yield from map(json.loads, source)


def one_law_controls(pilot):
    """All single extra laws on the chain's ten attachable distinctions. A fresh distinction makes it free."""
    began = perf_counter()
    tables = ChainTables()
    loose = (0, 1, 3, 5, 7, 9, 11, 13, 15, 16)
    totals = Counter()
    by_arity = defaultdict(Counter)
    lower_exceptions = []
    upper_exceptions = []
    passing_redundancies = []
    for arity in range(3, len(loose) + 1):
        choices = list(combinations(loose, arity))
        for members in (choices[:3] if pilot else choices):
            result = tables.results((tuple(d + 1 for d in members),))
            fields = counted(result)
            for counter in (totals, by_arity[arity]):
                counter["added_laws"] += 1
                for name, value in fields.items():
                    if name != "chains":
                        counter[name] += value
            if not fields["four_exact_lower_clauses"]:
                lower_exceptions.append({"extra_law_on_chain_positions_zero_based": members,
                                         "extra_missing_lower_words": result["extra_missing_lower_words"]})
            elif not fields["all_eight_laws_needed_for_all_three_roles"]:
                passing_redundancies.append({"extra_law_on_chain_positions_zero_based": members,
                                             "roles_still_missing_111_after_deleting_chain_law":
                                                 result["roles_still_missing_111_after_deleting_chain_law"]})
            if not fields["three_seven_word_upper_images"]:
                upper_exceptions.append({"extra_law_on_chain_positions_zero_based": members,
                                         "four_exact_lower_clauses": fields["four_exact_lower_clauses"],
                                         "upper_word_sets_with_A_B_C_both": result["upper_words"]})
    return {
        "scope": "One additional unsigned not-all-equal source law on an unchanged two-holder bare chain of eight. "
                 "All subsets of its ten attachable distinctions having at least three places. A law with a truly "
                 "fresh distinction always extends and agrees with the bare control.",
        "pilot": pilot, "elapsed_seconds": round(perf_counter()-began, 3),
        "peak_resident_KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "totals": totals, "by_arity": by_arity, "lower_failure_extensions": lower_exceptions,
        "upper_failure_extensions": upper_exceptions,
        "lower_passing_extensions_with_redundancy": passing_redundancies,
    }


def audit(archive, pilot, direct):
    started = perf_counter()
    tables = ChainTables()
    total = defaultdict(Counter)
    by_round = defaultdict(lambda: defaultdict(Counter))
    bad = []
    bad_identities = defaultdict(set)
    direct_queries = []
    sizes = defaultdict(Counter)
    pass_starts = defaultdict(lambda: defaultdict(set))
    pass_stages = defaultdict(lambda: defaultdict(set))
    maps = defaultdict(Counter)
    group_totals = defaultdict(Counter)
    comparisons = defaultdict(Counter)
    by_role = defaultdict(lambda: defaultdict(Counter))
    start_by_round = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))
    exception_certificates = {}
    rejected_stages = []
    determining_bond_cases = []
    direct_signatures = set()
    for stage in all_stages(archive):
        start, rnd = stage["start"], stage["round"]
        if pilot and start not in (90, 2030, 3609):
            continue
        supports = stage["supports"]
        recorded = stage["recorded"].get("mapped", ())
        one_stage = defaultdict(Counter)
        by_determining_bond = defaultdict(list)
        for index, chain in enumerate(stage["all_chains"]):
            labels = chain_names(supports, chain)
            components = off_chain(supports, chain, labels)
            signature = tuple(s for s, _ in components)
            result = tables.results(signature)
            fields = counted(result)
            if direct:
                # Check every original-step/essentiality exception. Also check
                # one actual stage for every signed list of outside conditions.
                if signature in direct_signatures and fields["step_with_defining_bond_check_and_all_eight_needed"]:
                    continue
                if pilot and len(direct_queries) >= 3:
                    continue
                direct_signatures.add(signature)
                direct_queries.append({
                    "census_entry": start, "round": rnd, "chain_rank": index+1,
                    "original_step_and_all_eight_needed": fields["step_with_defining_bond_check_and_all_eight_needed"],
                    **direct_projection(tables, supports, chain, labels, components),
                })
                continue
            if index < len(recorded):
                rec = recorded[index]
                expected = [rec["lower triples miss exactly their triple"], rec["no lower reading read at a knot"],
                            rec["every chain law needed"], rec["a step"]]
                found = [fields["four_exact_lower_clauses"], fields["lower_readings_nonlocal_to_every_raw_knot_certified"],
                         fields["all_eight_laws_needed_for_all_three_roles"], fields["original_step"]]
                if expected != found:
                    raise ValueError(("raw mismatch", start, rnd, index+1, expected, found))
                for old, upper_words in zip(rec["upper"], result["upper_words"], strict=True):
                    if old["upper words"] != len(upper_words) or old["pairs free"] != all(
                            len({w[a]+w[b] for w in upper_words}) == 4 for a,b in combinations(range(3), 2)):
                        raise ValueError(("upper mismatch", start, rnd, index+1))
            portion = "frozen" if index < len(recorded) else "omitted"
            for bond in result["bonds_on_the_six"]:
                if bond["determines"]:
                    cause = (bond["triple"], tuple(tuple(item) for item in bond["determines"]))
                    by_determining_bond[cause].append(index+1)
            increments = {k: int(v) for k,v in fields.items()}
            for key in ("all", portion):
                total[key].update(increments)
                by_round[key][rnd].update(increments)
                sizes[key][len(components)] += 1
                maps[key][result["projected_chain_assignments"]] += 1
                comparisons[key][f"bare six-word set retained={fields['exact_bare_six_reading_image']}, "
                                 f"all three roles pass all bonds on six={fields['all_three_qualifying_roles_with_all_bonds_on_the_six']}"] += 1
                has_rule = any(s in ((1,2,6), (12,16,17)) for s, _ in components)
                comparisons[key][f"single observed outside law up to reversal={has_rule}, "
                                 f"lower failure={not fields['four_exact_lower_clauses']}"] += 1
                for label, value in fields.items():
                    if value:
                        pass_starts[key][label].add(start)
                        pass_stages[key][label].add((start,rnd))
                        start_by_round[key][rnd][label].add(start)
                one_stage[key].update(increments)
                for bond in result["bonds_on_the_six"]:
                    if bond["triple"] not in LOWER:
                        group_totals[key]["additional_true_lower_bonds"] += 1
                        group_totals[key]["additional_true_lower_bonds_determining_an_upper_function"] += bool(bond["determines"])
                for role in ROLES:
                    blocked = role in result["roles_determined_somewhere_on_the_six"]
                    necessary = all(role not in rs for rs in result["roles_still_missing_111_after_deleting_chain_law"])
                    by_role[key][role]["checked"] += 1
                    by_role[key][role]["has_a_determining_bond_on_the_six"] += blocked
                    by_role[key][role]["qualifies_with_all_bonds_on_the_six"] += fields["original_step"] and not blocked
                    by_role[key][role]["qualifies_with_all_bonds_on_the_six_and_all_eight_needed"] += (
                        fields["original_step"] and not blocked and necessary)
            if fields["step_with_defining_bond_check_and_all_eight_needed"]:
                continue
            name = (start, tuple(chain))
            bad_identities[portion].add(name)
            key = str(signature)
            if key not in exception_certificates:
                exception_certificates[key] = minimal_extras(tables, signature)
            record = {
                "census_entry": start, "round": rnd, "chain_rank": index+1, "portion": portion,
                "chain_knots_zero_based": chain, "chain_distinctions_in_canonical_order": labels,
                "external_conditions": [{"signed_one_based_chain_positions": s, "source_knots_zero_based": ks}
                                        for s, ks in components], **result,
            }
            bad.append(record)
        for key, row in one_stage.items():
            if row["chains"] and row["all_three_qualifying_roles_with_all_bonds_on_the_six"] < row["chains"]:
                rejected_stages.append({"census_entry": start, "round": rnd, "portion": key,
                                        "chains": row["chains"], "original_step": row["original_step"],
                                        "surviving_with_any_role": row["some_qualifying_role_with_all_bonds_on_the_six"],
                                        "surviving_with_all_roles": row["all_three_qualifying_roles_with_all_bonds_on_the_six"],
                                        "surviving_all_roles_and_laws":
                                            row["all_three_qualifying_roles_with_all_bonds_on_the_six_and_all_eight_needed"]})
        if by_determining_bond:
            determining_bond_cases.append({
                "census_entry": start, "round": rnd,
                "bonds": [{"lower_agreements": [NAMES[i] for i in triple], "upper_functions_determined": functions,
                           "chain_ranks_one_based": indices}
                          for (triple, functions), indices in sorted(by_determining_bond.items())]})
    output = {
        "pilot": pilot, "elapsed_seconds": round(perf_counter()-started, 3),
        "peak_resident_KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    if direct:
        return {**output, "distinct_signatures_checked": len(direct_signatures),
                "total_direct_queries": sum(row["queries"] for row in direct_queries),
                "direct_specific_stage_condition_checks": direct_queries}
    return {
        **output,
        "scope": "Ordinary finite stages, fixed bare-chain reading. All chains enumerated before any cap.",
        "upper_locality_scope": "Each of the four defining lower bonds; separately all 20 candidate triples among the six carriers.",
        "totals": total, "by_round": by_round,
        "distinct_starts_with_at_least_one": {k: {x: len(v) for x,v in tbl.items()} for k,tbl in pass_starts.items()},
        "distinct_stages_with_at_least_one": {k: {x: len(v) for x,v in tbl.items()} for k,tbl in pass_stages.items()},
        "tree_conditions_per_chain": sizes, "projected_chain_assignments_histogram": maps,
        "all_six_bond_counts": group_totals, "all_six_bond_counts_by_role": by_role,
        "chains_with_a_determining_bond_among_the_six_carriers": determining_bond_cases,
        "joint_checks": comparisons,
        "distinct_starts_by_round": {k: {rnd: {label: len(ids) for label,ids in tab.items()} for rnd,tab in t.items()}
                                     for k,t in start_by_round.items()},
        "stages_with_some_rejection_on_lower_or_six_bond_gates": rejected_stages,
        "minimal_external_condition_indices_zero_based": exception_certificates,
        "distinct_exception_chains": {k: len(v) for k,v in bad_identities.items()} |
                                     {"all": len(set().union(*bad_identities.values()))},
        "exception_rows": bad,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=HERE / "stages.jsonl.gz")
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--direct", action="store_true")
    parser.add_argument("--one-law", action="store_true")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = one_law_controls(args.pilot) if args.one_law else audit(args.archive, args.pilot, args.direct)
    if args.pilot:
        result.pop("exception_rows", None)
        result.pop("stages_with_some_rejection_on_lower_or_six_bond_gates", None)
        result.pop("chains_with_a_determining_bond_among_the_six_carriers", None)
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k in {"elapsed_seconds", "peak_resident_KiB",
                                                               "totals", "total_direct_queries", "distinct_signatures_checked"}}))


if __name__ == "__main__":
    main()
