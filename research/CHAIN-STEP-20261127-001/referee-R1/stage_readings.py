"""Independently project each checked chain's readings on the whole stage."""

import argparse
from collections import Counter, defaultdict
from contextlib import contextmanager
from functools import cache
import gzip
from itertools import combinations, product
import json
from pathlib import Path
import resource
from time import perf_counter

from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
BARE_CHAIN = tuple((2 * i, 2 * i + 1, 2 * i + 2) for i in range(8))
# The declared pattern, in the fixed A0, A1, B0, B1, C0, C1 order.
BARE_CARRIERS = ((3, 4, 5), (11, 12, 13), (0, 1, 10), (6, 15, 16), (7, 8, 9), (2, 14))
DEFINING = ((0, 2, 4), (0, 3, 5), (1, 2, 5), (1, 3, 4))
TRIPLES = tuple(combinations(range(6), 3))
PAIRS = ((0, 1), (2, 3), (4, 5))
LOWER_NAMES = ("A0", "A1", "B0", "B1", "C0", "C1")
UPPER_NAMES = tuple((f"{name} both", f"{name} either") for name in "ABC")
EXPECTED_UPPER = set(product((0, 1), repeat=3)) - {(1, 1, 1)}
ALL_LAW_INDICES = tuple(range(8))
DIRECT_CONTROLS = {(87, 2, 1), (2030, 3, 0), (5260, 2, 0)}


@cache
def bit_words(size):
    return tuple(product((0, 1), repeat=size))


def render(word):
    return "".join(map(str, word))


def rendered(words):
    return sorted(map(render, words))


def subword(word, indices):
    return tuple(word[i] for i in indices)


def projection(words, indices):
    return {subword(word, indices) for word in words}


def pairs_free(words):
    return all(len(projection(words, pair)) == 4 for pair in combinations(range(3), 2))


def pair_values(word):
    return tuple((word[a] & word[b], word[a] | word[b]) for a, b in PAIRS)


def upper_images(words):
    values = {pair_values(word) for word in words}
    return [{tuple(v[pair][pair != both] for pair in range(3)) for v in values} for both in range(3)]


def mixed_fixes(words, lower):
    groups = defaultdict(set)
    for word in words:
        groups[subword(word, lower)].add(pair_values(word))
    return [
        [sum(len({value[pair][kind] for value in values}) == 2 for values in groups.values()) for kind in range(2)]
        for pair in range(3)
    ]


def mapped_carriers(supports, chain):
    if len(chain) != 8 or len(set(chain)) != 8:
        raise ValueError(f"Expected eight distinct laws, got {chain}")
    chain_supports = tuple(set(supports[j]) for j in chain)
    if any(len(support) != 3 for support in chain_supports):
        raise ValueError(f"Expected eight three-place laws, got {chain_supports}")
    mapping = {}
    for i, j in combinations(range(8), 2):
        shared = chain_supports[i] & chain_supports[j]
        if len(shared) != int(j == i + 1):
            raise ValueError(f"Wrong number of shared distinctions between chain positions {i} and {j}")
        if shared:
            mapping[2 * j] = shared.pop()
    for i, support in enumerate(chain_supports):
        own = sorted(support.difference(mapping.values()))
        private_slots = [slot for slot in BARE_CHAIN[i] if slot not in mapping]
        # Exchanging the two endpoint distinctions changes no agreement reading.
        mapping.update(zip(private_slots, own, strict=True))
    if len(set(mapping.values())) != 17:
        raise ValueError("Cannot identify the chain's 17 distinctions")
    return tuple(tuple(sorted(mapping[i] for i in carrier)) for carrier in BARE_CARRIERS)


def signed(variables, word):
    return [variable if bit else -variable for variable, bit in zip(variables, word, strict=True)]


class Stage:
    """One incremental SAT relation with independently removable source laws."""

    def __init__(self, solver, supports):
        names = sorted({name for support in supports for name in support})
        self.number = {name: i for i, name in enumerate(names, 1)}
        self.solver = solver
        self.top = len(names)
        self.laws = []
        self.supports = tuple(tuple(self.number[name] for name in support) for support in supports)
        self.agreements = {}
        for support in self.supports:
            switch = self.fresh()
            for value in (1, -1):
                self.solver.add_clause([-switch, *(value * variable for variable in support)])
            self.laws.append(switch)

    def fresh(self):
        self.top += 1
        return self.top

    def define(self, inputs, predicate):
        output = self.fresh()
        for word in bit_words(len(inputs)):
            opposite = [-literal for literal in signed(inputs, word)]
            self.solver.add_clause(opposite + [output if predicate(word) else -output])
        return output

    def agreement(self, carrier):
        if carrier not in self.agreements:
            ids = tuple(self.number[name] for name in carrier)
            self.agreements[carrier] = self.define(ids, lambda word: len(set(word)) == 1)
        return self.agreements[carrier]

    def upper_111(self, readings):
        readings_by_pair = tuple(
            (self.define((readings[a], readings[b]), all), self.define((readings[a], readings[b]), any))
            for a, b in PAIRS
        )
        return tuple(
            self.define(tuple(readings_by_pair[pair][pair != both] for pair in range(3)), all)
            for both in range(3)
        )

    def solve(self, literals, *, kept_laws=None, omit=()):
        if kept_laws is None:
            assumptions = [law for index, law in enumerate(self.laws) if index not in omit]
        else:
            assumptions = [self.laws[index] for index in kept_laws]
        return self.solver.solve(assumptions=assumptions + list(literals))

    def observed(self, readings):
        words = {}
        for word in bit_words(len(readings)):
            if self.solve(signed(readings, word)):
                words[word] = {
                    literal for literal in self.solver.get_model() if 0 < literal <= len(self.number)
                }
        return words

    def read_at_any_knot(self, readings, observed):
        """Test whether a source law's raw values determine a reading everywhere."""
        determined = []
        needing_queries = 0
        query_count = 0
        for knot, support in enumerate(self.supports):
            fixes_by_word = {}
            for word, state in observed.items():
                flip = support[0] in state
                fixes_by_word[word] = tuple(int((variable in state) != flip) for variable in support)
            for pos, reading in enumerate(readings):
                zeros = {fix for word, fix in fixes_by_word.items() if not word[pos]}
                ones = {fix for word, fix in fixes_by_word.items() if word[pos]}
                if zeros & ones:
                    continue
                if not zeros or not ones:
                    determined.append([knot, LOWER_NAMES[pos]])
                    continue
                needing_queries += 1
                # Both stage and agreement are invariant under global complement.
                # Try occupied fixes first, then every remaining nonconstant fix
                # with the first raw distinction set to zero.
                known_fixes = sorted(zeros | ones)
                other_fixes = [(0, *suffix) for suffix in bit_words(len(support) - 1) if any(suffix)]
                for fix in known_fixes + [f for f in other_fixes if f not in zeros and f not in ones]:
                    literals = signed(support, fix)
                    if fix not in zeros:
                        query_count += 1
                        if not self.solve(literals + [-reading]):
                            continue
                    if fix not in ones:
                        query_count += 1
                        if not self.solve(literals + [reading]):
                            continue
                    break
                else:
                    determined.append([knot, LOWER_NAMES[pos]])
        return {
            "comparisons": len(self.supports) * len(readings),
            "comparisons_needing_additional_solver_queries": needing_queries,
            "additional_solver_queries": query_count,
            "determining_knot_and_reading": determined,
        }

    def minimal_exclusion(self, literals, *, omit=()):
        if self.solve(literals, omit=omit):
            raise ValueError("Expected an excluded word")
        core = set(self.solver.get_core())
        kept = [index for index, law in enumerate(self.laws) if law in core]
        for index in kept.copy():
            proposal = [law for law in kept if law != index]
            if not self.solve(literals, kept_laws=proposal):
                kept = proposal
        assert not self.solve(literals, kept_laws=kept)
        return kept


@contextmanager
def stage_solver(supports):
    with Solver(name="maplechrono") as solver:
        yield Stage(solver, supports)


def locality_of_triple(words, triple):
    lower = projection(words, triple)
    return {
        "readings": [LOWER_NAMES[i] for i in triple],
        "missing_words": rendered(set(bit_words(3)) - lower),
        "pairs_free": pairs_free(lower),
        "is_bond": 0 < len(lower) < 8 and pairs_free(lower),
        "mixed_fixes_by_upper_pair_and_function": mixed_fixes(words, triple),
    }


def determines_an_upper(locality):
    return any(count == 0 for by_pair in locality["mixed_fixes_by_upper_pair_and_function"] for count in by_pair)


def direct_enumeration(supports, carriers):
    """Project all raw assignments of a small stage with at most one law broken."""
    names = sorted({d for law in supports for d in law})
    bits = {d: 1 << i for i, d in enumerate(names)}
    law_masks = [sum(bits[d] for d in law) for law in supports]
    carrier_masks = [sum(bits[d] for d in carrier) for carrier in carriers]
    words = set()
    deleted = [set() for _ in supports]
    allowed_states = 0
    for state in range(1 << len(names)):
        failed = None
        for i, mask in enumerate(law_masks):
            if state & mask in (0, mask):
                if failed is not None:
                    break
                failed = i
        else:
            word = tuple(int(state & mask in (0, mask)) for mask in carrier_masks)
            if failed is not None:
                deleted[failed].add(word)
            else:
                words.add(word)
                allowed_states += 1
    return words, deleted, allowed_states


def abstract_controls():
    bare, bare_deletions, allowed_states = direct_enumeration(BARE_CHAIN, BARE_CARRIERS)
    assert mapped_carriers(BARE_CHAIN, ALL_LAW_INDICES) == BARE_CARRIERS
    with stage_solver(BARE_CHAIN) as stage:
        vars_ = tuple(stage.agreement(carrier) for carrier in BARE_CARRIERS)
        observed = stage.observed(vars_)
        assert set(observed) == bare
        embedded = stage.upper_111(vars_)
        for i, alternatives in enumerate(bare_deletions):
            exists_111 = [(1, 1, 1) in image for image in upper_images(bare | alternatives)]
            assert exists_111 == [stage.solve([predicate], omit=(i,)) for predicate in embedded] == [True] * 3
        assert all(stage.solve([predicate], omit=ALL_LAW_INDICES) for predicate in embedded)
        # An open agreement on two members of a law is determined at that law.
        direct_reading = stage.agreement((0, 1))
        direct_words = stage.observed((direct_reading,))
        assert len(direct_words) == 2
        assert [0, "A0"] in stage.read_at_any_knot((direct_reading,), direct_words)["determining_knot_and_reading"]
    named = [locality_of_triple(bare, triple) for triple in DEFINING]
    assert all(r["missing_words"] == ["111"] and not determines_an_upper(r) for r in named)
    assert upper_images(bare) == [EXPECTED_UPPER] * 3
    clause_image = {word for word in bit_words(6) if all(subword(word, triple) != (1, 1, 1) for triple in DEFINING)}
    assert bare <= clause_image and upper_images(clause_image) == [EXPECTED_UPPER] * 3
    deletions = []
    for triple in DEFINING:
        surviving = [other for other in DEFINING if other != triple]
        words = {word for word in bit_words(6) if all(subword(word, other) != (1, 1, 1) for other in surviving)}
        assert all((1, 1, 1) in image for image in upper_images(words))
        deletions.append(rendered(words - clause_image))
    # Plant a bond containing both arguments of the first upper pair.
    planted = {word for word in bit_words(6) if word[:3] != (1, 1, 1)}
    planted_bond = locality_of_triple(planted, (0, 1, 2))
    assert planted_bond["is_bond"] and planted_bond["mixed_fixes_by_upper_pair_and_function"][0] == [0, 0]
    return bare, {
        "bare_chain": {
            "source_supports": BARE_CHAIN,
            "carriers": BARE_CARRIERS,
            "allowed_source_states": allowed_states,
            "lower_joint_words": rendered(bare),
            "defining_lower_triples": named,
            "upper_images": [rendered(image) for image in upper_images(bare)],
            "all_eight_single_deletions_restore_all_three_upper_111": True,
            "whole_chain_deletion_restores_all_three_upper_111": True,
        },
        "four_defining_lower_clauses_in_isolation": {
            "lower_joint_words": rendered(clause_image),
            "upper_images": [rendered(image) for image in upper_images(clause_image)],
            "new_lower_words_after_each_clause_deletion": deletions,
        },
        "open_lower_reading_determined_at_containing_knot": True,
        "planted_lower_bond_determines_two_upper_functions": planted_bond,
    }


def direct_control(row, supports):
    words, deleted, allowed_states = direct_enumeration(supports, row["carriers"])
    assert rendered(words) == row["lower_joint_words"]
    for law, solver_verdicts in zip(
        row["chain_law_indices"], row["by_single_chain_law_deletion_upper_111_restored"], strict=True
    ):
        assert [(1, 1, 1) in image for image in upper_images(words | deleted[law])] == solver_verdicts
    return {
        "start": row["start"], "round": row["round"], "chain_number": row["chain_number"],
        "allowed_source_states_before_any_deletion": allowed_states,
        "full_six_reading_image_and_all_eight_single_deletions_match": True,
    }


def agreement_quotient(supports, carriers, triple, word, laws):
    """Identify the raw distinctions in each of the lower agreements fixed true."""
    names = {}
    for index, bit in zip(triple, word, strict=True):
        if bit == "1":
            carrier = carriers[index]
            names.update(dict.fromkeys(carrier, carrier[0]))
    return [sorted({names.get(d, d) for d in supports[i]}) for i in laws]


def three_pairwise_inequalities(quotient):
    distinctions = sorted({d for support in quotient for d in support})
    if len(quotient) != 3 or len(distinctions) != 3:
        return False
    return set(map(tuple, quotient)) == set(combinations(distinctions, 2))


def replay(stage, source, chain, position, bare):
    carriers = mapped_carriers(source["supports"], chain)
    readings = tuple(stage.agreement(carrier) for carrier in carriers)
    observed = stage.observed(readings)
    words = set(observed)
    if not words <= bare:
        raise ValueError("Whole-stage words exceed the bare-chain image")
    lower_local = stage.read_at_any_knot(readings, observed)
    named = [locality_of_triple(words, triple) for triple in DEFINING]
    other_bonds = []
    chain_set = set(chain)
    for triple in TRIPLES:
        if triple in DEFINING:
            continue
        entry = locality_of_triple(words, triple)
        if not entry["is_bond"]:
            continue
        exclusions = []
        for absent in entry["missing_words"]:
            literals = signed(subword(readings, triple), tuple(map(int, absent)))
            assert stage.solve(literals, kept_laws=chain)
            core = stage.minimal_exclusion(literals)
            exclusions.append({
                "word": absent,
                "inclusion_minimal_stage_law_exclusion": core,
                "out_of_chain_laws_in_exclusion": sorted(set(core) - chain_set),
                "single_stage_law_deletions_that_restore_word": [
                    i for i in core if stage.solve(literals, omit=(i,))
                ],
            })
        entry["exclusions"] = exclusions
        other_bonds.append(entry)
    images = upper_images(words)
    upper = [{"words": rendered(image), "pairs_free": pairs_free(image)} for image in images]
    relations_hold = images == [EXPECTED_UPPER] * 3
    predicates = stage.upper_111(readings)
    # This compares the solver's upper encoding against the six-reading projections.
    assert [stage.solve([p]) for p in predicates] == [(1, 1, 1) in image for image in images]
    single = [[stage.solve([p], omit=(i,)) for p in predicates] for i in chain]
    all_deleted = [stage.solve([p], omit=chain) for p in predicates]
    lower_single = all(entry["missing_words"] == ["111"] for entry in named)
    lower_unread = not lower_local["determining_knot_and_reading"]
    upper_unread = not any(determines_an_upper(entry) for entry in named)
    other_determining = [entry for entry in other_bonds if determines_an_upper(entry)]
    single_essential = all(map(all, single))
    frozen_step = lower_single and lower_unread and all(len(r["words"]) == 7 and r["pairs_free"] for r in upper)
    archived_fields = {
        "lower triples miss exactly their triple": lower_single,
        "upper": [{"upper words": len(r["words"]), "pairs free": r["pairs_free"]} for r in upper],
        "every chain law needed": single_essential,
        "no lower reading read at a knot": lower_unread,
        "a step": frozen_step,
    }
    recorded = source.get("recorded", {}).get("mapped", ()) if source.get("recorded") else ()
    mismatches = {}
    if recorded:
        archived = recorded[position]
        mismatches = {field: [archived.get(field), value] for field, value in archived_fields.items() if archived.get(field) != value}
    anomalous_absences = []
    for triple, record in zip(DEFINING, named, strict=True):
        for absent in record["missing_words"]:
            if absent == "111":
                continue
            literals = signed(subword(readings, triple), tuple(map(int, absent)))
            assert stage.solve(literals, kept_laws=chain)
            restores = [i for i in range(len(stage.laws)) if stage.solve(literals, omit=(i,))]
            core = stage.minimal_exclusion(literals)
            quotient = agreement_quotient(source["supports"], carriers, triple, absent, core)
            anomalous_absences.append({
                "lower_readings": record["readings"],
                "extra_missing_word": absent,
                "single_stage_law_deletions_that_restore_word": restores,
                "inclusion_minimal_stage_law_exclusion": core,
                "individual_law_supports": {i: source["supports"][i] for i in set(restores) | set(core)},
                "out_of_chain_laws_in_exclusion": sorted(set(core) - chain_set),
                "source_law_supports_after_identifying_the_true_agreements": quotient,
                "three_pairwise_inequalities_on_three_bits": three_pairwise_inequalities(quotient),
            })
    redundant_uses = []
    for law, results in zip(chain, single, strict=True):
        for both, restored in enumerate(results):
            if not restored:
                core = stage.minimal_exclusion([predicates[both]], omit=(law,))
                assert set(core) - chain_set
                redundant_uses.append({
                    "omitted_law": law, "both_pair": "ABC"[both],
                    "inclusion_minimal_stage_law_exclusion": core,
                    "out_of_chain_laws_in_exclusion": sorted(set(core) - chain_set),
                })
    strict = frozen_step and upper_unread and relations_hold and single_essential
    return {
        "start": source["start"],
        "round": source["round"],
        "chain_number": position + 1,
        "chain_law_indices": chain,
        "knots": len(stage.supports),
        "distinctions": len(stage.number),
        "carriers": carriers,
        "lower_joint_words": rendered(words),
        "bare_lower_joint_words_lost_on_stage": rendered(bare - words),
        "lower_locality": lower_local,
        "defining_lower_triples": named,
        "other_bonds_on_the_six_named_readings": other_bonds,
        "upper_function_determined_at_other_bond_on_the_six": bool(other_determining),
        "upper_images": upper,
        "all_three_expected_upper_images": relations_hold,
        "all_upper_readings_unread_at_every_defining_lower_triple": upper_unread,
        "by_single_chain_law_deletion_upper_111_restored": single,
        "whole_chain_deletion_upper_111_restored": all_deleted,
        "frozen_fields": archived_fields,
        "strict_step_on_defining_bonds": strict,
        "strict_step_with_all_bonds_on_the_six_checked": strict and not other_determining,
        "counterexamples_to_frozen_form": anomalous_absences,
        "failed_single_deletion_checks": redundant_uses,
        "archived_fields_compared": len(archived_fields) if recorded else 0,
        "archive_mismatches": mismatches,
    }


def update_counts(counts, row, seen_starts):
    counts["checked_chains"] += 1
    counts["archived_fields_compared"] += row["archived_fields_compared"]
    counts["archive_field_mismatches"] += len(row["archive_mismatches"])
    counts["six_reading_words_equal_bare_chain"] += not row["bare_lower_joint_words_lost_on_stage"]
    counts[f"six_reading_words_count_{len(row['lower_joint_words'])}"] += 1
    counts["source_six_reading_word_checks"] += len(bit_words(6))
    for key in ("comparisons", "comparisons_needing_additional_solver_queries", "additional_solver_queries"):
        counts[f"lower_reading_vs_source_knot_{key}"] += row["lower_locality"][key]
    counts["lower_reading_vs_source_knot_determinations"] += len(row["lower_locality"]["determining_knot_and_reading"])
    for entry in row["defining_lower_triples"]:
        counts["defining_lower_triples_checked"] += 1
        counts["defining_lower_triples_missing_exactly_111"] += entry["missing_words"] == ["111"]
        counts["defining_lower_triples_that_are_bonds"] += entry["is_bond"]
        counts["defining_lower_triple_vs_distinct_upper_function_comparisons"] += 6
        counts["defining_lower_bond_vs_distinct_upper_function_comparisons"] += 6 * entry["is_bond"]
        counts["defining_lower_triple_vs_distinct_upper_function_determinations"] += sum(
            count == 0 for pair in entry["mixed_fixes_by_upper_pair_and_function"] for count in pair
        )
        counts["defining_lower_triple_and_upper_function_with_some_feasible_fix_leaving_only_one_value"] += sum(
            count < 8 - len(entry["missing_words"]) for pair in entry["mixed_fixes_by_upper_pair_and_function"] for count in pair
        )
    counts["other_triples_of_six_named_readings_checked"] += len(TRIPLES) - len(DEFINING)
    counts["other_triple_of_six_vs_distinct_upper_function_comparisons"] += 6 * (len(TRIPLES) - len(DEFINING))
    other_bonds = row["other_bonds_on_the_six_named_readings"]
    counts["other_bonds_on_six_named_readings"] += len(other_bonds)
    counts["other_bond_of_six_vs_distinct_upper_function_comparisons"] += 6 * len(other_bonds)
    counts["other_bond_of_six_vs_distinct_upper_function_determinations"] += sum(
        count == 0 for entry in other_bonds for pair in entry["mixed_fixes_by_upper_pair_and_function"] for count in pair
    )
    counts["other_bonds_on_six_named_readings_determining_an_upper_function"] += sum(
        determines_an_upper(entry) for entry in other_bonds
    )
    counts["upper_relations_checked"] += len(row["upper_images"])
    counts["upper_relations_missing_exactly_111"] += sum(image["words"] == rendered(EXPECTED_UPPER) for image in row["upper_images"])
    counts["upper_pairs_checked"] += 3 * len(row["upper_images"])
    counts["upper_relations_with_all_three_pairs_free"] += sum(image["pairs_free"] for image in row["upper_images"])
    counts["single_chain_laws_checked"] += len(row["chain_law_indices"])
    for deletion in row["by_single_chain_law_deletion_upper_111_restored"]:
        counts["single_deletion_role_checks"] += len(deletion)
        counts["single_deletion_role_checks_restoring_111"] += sum(deletion)
        counts["single_chain_law_deletions_restoring_111_for_all_three_roles"] += all(deletion)
    counts["whole_chain_deletion_role_checks"] += len(row["whole_chain_deletion_upper_111_restored"])
    counts["whole_chain_deletion_role_checks_restoring_111"] += sum(row["whole_chain_deletion_upper_111_restored"])
    if row["frozen_fields"]["a step"]:
        counts["chains_carrying_frozen_step"] += 1
        seen_starts["frozen_step"].add(row["start"])
    if row["frozen_fields"]["every chain law needed"]:
        counts["chains_with_every_law_needed"] += 1
        seen_starts["all_laws_needed"].add(row["start"])
    if row["strict_step_on_defining_bonds"]:
        counts["chains_passing_all_gates_with_defining_bonds"] += 1
        seen_starts["strict_step"].add(row["start"])
    if row["upper_function_determined_at_other_bond_on_the_six"]:
        counts["chains_with_upper_function_determined_at_other_bond_on_same_six"] += 1
        seen_starts["upper_determined_at_other_bond_on_same_six"].add(row["start"])
        if row["strict_step_on_defining_bonds"]:
            counts["otherwise_strict_chains_with_upper_function_determined_at_other_bond_on_same_six"] += 1
            seen_starts["otherwise_strict_upper_determined_at_other_bond_on_same_six"].add(row["start"])
    if row["strict_step_with_all_bonds_on_the_six_checked"]:
        counts["chains_passing_all_gates_with_all_bonds_on_same_six"] += 1
        seen_starts["strict_step_all_bonds_on_same_six"].add(row["start"])


def json_stages(path):
    with gzip.open(path, "rt", encoding="utf-8") as archive:
        for line in archive:
            yield json.loads(line)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="Replay the independent reconstruction's timing slice")
    parser.add_argument("--controls-only", action="store_true")
    parser.add_argument("--stages", type=Path, default=HERE / "stages.jsonl.gz")
    args = parser.parse_args()
    begin = perf_counter()
    bare, controls = abstract_controls()
    controls_seconds = perf_counter() - begin
    if args.controls_only:
        print(json.dumps(controls, indent=2))
        print(f"Controls came to {controls_seconds:.4f} seconds")
        return
    if args.pilot:
        from recount import pilot_stages

        stages = pilot_stages()
    else:
        stages = json_stages(args.stages)
    suffix = "_pilot" if args.pilot else ""
    summary = {}
    counts = defaultdict(Counter)
    checked_starts = defaultdict(set)
    seen_starts = defaultdict(lambda: defaultdict(set))
    strict_first_round = {}
    frozen_first_round = {}
    strict_same_six_first_round = {}
    direct_controls = []
    anomalies = []
    stage_timings = []
    with gzip.open(HERE / f"stage_readings{suffix}.jsonl.gz", "wt", encoding="utf-8") as output:
        for source in stages:
            checked = source["checked_chains"]
            recorded = source.get("recorded") or {}
            if not checked:
                if recorded.get("mapped"):
                    raise ValueError("An archived check has no reconstructed chain")
                continue
            if "mapped" in recorded and len(checked) != len(recorded["mapped"]):
                raise ValueError("Wrong number of reconstructed checked chains")
            tick = perf_counter()
            stage_round = source["round"]
            start = source["start"]
            with stage_solver(source["supports"]) as stage:
                for position, chain in enumerate(checked):
                    row = replay(stage, source, chain, position, bare)
                    output.write(json.dumps(row, separators=(",", ":")) + "\n")
                    for key in ("all", stage_round):
                        update_counts(counts[key], row, seen_starts[key])
                        checked_starts[key].add(start)
                    if row["strict_step_on_defining_bonds"]:
                        strict_first_round[start] = min(strict_first_round.get(start, stage_round), stage_round)
                    if row["strict_step_with_all_bonds_on_the_six_checked"]:
                        strict_same_six_first_round[start] = min(strict_same_six_first_round.get(start, stage_round), stage_round)
                    if row["frozen_fields"]["a step"]:
                        frozen_first_round[start] = min(frozen_first_round.get(start, stage_round), stage_round)
                    if not row["strict_step_on_defining_bonds"] or row["archive_mismatches"]:
                        anomalies.append(row)
                    if (start, stage_round, position) in DIRECT_CONTROLS:
                        direct_controls.append(direct_control(row, source["supports"]))
            stage_timings.append((start, stage_round, len(stage.number), len(checked), round(perf_counter() - tick, 6)))
    for key, counter in counts.items():
        summary[str(key)] = {
            **counter,
            "checked_starts": len(checked_starts[key]),
            "starts_with_frozen_step": len(seen_starts[key]["frozen_step"]),
            "starts_with_all_laws_needed_for_some_checked_chain": len(seen_starts[key]["all_laws_needed"]),
            "starts_with_strict_step_among_checked_chains": len(seen_starts[key]["strict_step"]),
            "starts_with_upper_function_determined_at_other_bond_on_same_six": len(
                seen_starts[key]["upper_determined_at_other_bond_on_same_six"]
            ),
            "starts_with_otherwise_strict_chain_whose_other_bond_on_same_six_determines_an_upper_function": len(
                seen_starts[key]["otherwise_strict_upper_determined_at_other_bond_on_same_six"]
            ),
            "starts_with_strict_step_all_bonds_on_same_six": len(seen_starts[key]["strict_step_all_bonds_on_same_six"]),
        }
    result = {
        "scope": "The reconstructed checked chains, each on its whole stage. Knot and law indices are zero-based. Chain number is one-based.",
        "lower_locality": "Exact variation at a fixed raw word of each source knot, using solver witnesses for feasible stage states.",
        "upper_locality": "Six distinct functions checked against each defining triple and all other triples on the same six named readings. Arbitrary other stage bonds are outside this script.",
        "upper_function_order": UPPER_NAMES,
        "upper_deletion_order": ["A both", "B both", "C both"],
        "controls": controls,
        "direct_enumeration_of_actual_stages": direct_controls,
        "counts": summary,
        "first_frozen_step_by_round_counting_starts": Counter(frozen_first_round.values()),
        "first_strict_step_by_round_counting_starts": Counter(strict_first_round.values()),
        "first_strict_step_all_bonds_on_same_six_by_round_counting_starts": Counter(strict_same_six_first_round.values()),
        "start_first_round_when_frozen_and_strict_differ": {
            start: {"frozen": round_, "strict": strict_first_round.get(start)}
            for start, round_ in frozen_first_round.items() if strict_first_round.get(start) != round_
        },
        "anomalies": anomalies,
        "elapsed_seconds": round(perf_counter() - begin, 6),
        "controls_seconds": round(controls_seconds, 6),
        "peak_resident_KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "stages_timed": len(stage_timings),
        "stage_timings_[start,round,distinctions,chains,seconds]": stage_timings if args.pilot else sorted(
            stage_timings, key=lambda row: -row[-1]
        )[:10],
    }
    destination = HERE / f"stage_readings_summary{suffix}.json"
    destination.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(destination.name, result["elapsed_seconds"], "seconds")
    print(json.dumps(result["counts"].get("all", {}), indent=2))


if __name__ == "__main__":
    main()
