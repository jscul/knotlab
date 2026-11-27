"""Search all lower bonds that contain the two carriers of an upper pair."""

import argparse
import gzip
import json
import random
import resource
import time
from collections import Counter
from itertools import combinations
from math import comb
from pathlib import Path

import numpy as np
from pysat.solvers import Solver


ROOT = Path(__file__).resolve().parent
SAMPLE_SIZE = 512
SAMPLE_PER_WORD = 64
WORDS = tuple((word >> 2, (word >> 1) & 1, word & 1) for word in range(8))
BARE_PAIRS = (
    ((3, 4, 5), (11, 12, 13)),
    ((0, 1, 10), (6, 15, 16)),
    ((7, 8, 9), (2, 14)),
)


def read_rows(path):
    with gzip.open(path, "rt") as source:
        yield from map(json.loads, source)


def named_pairs(supports, chain):
    laws = [set(supports[index]) for index in chain]
    if len(laws) != 8 or any(len(law) != 3 for law in laws):
        raise ValueError(f"Expected eight three-place laws, got {chain}")
    shared = []
    for i, law in enumerate(laws[:-1]):
        overlap = law & laws[i + 1]
        if len(overlap) != 1:
            raise ValueError(f"Consecutive laws must share one distinction: {chain}")
        shared.append(overlap.pop())
    order = sorted(laws[0] - {shared[0]}) + [shared[0]]
    for i in range(1, 7):
        order.extend(sorted(laws[i] - {shared[i - 1], shared[i]}))
        order.append(shared[i])
    order.extend(sorted(laws[-1] - {shared[-1]}))
    if len(order) != 17 or len(set(order)) != 17:
        raise ValueError(f"The chain does not have the bare order: {chain}")
    return tuple(
        tuple(tuple(sorted(order[i] for i in carrier)) for carrier in pair)
        for pair in BARE_PAIRS
    )


def source_clauses(supports, offset=0):
    for law in supports:
        yield [offset + member + 1 for member in law]
        yield [-(offset + member + 1) for member in law]


def add_agreement(solver, carrier, output, offset=0):
    members = [offset + member + 1 for member in carrier]
    for member in members[1:]:
        solver.add_clause([-output, -members[0], member])
        solver.add_clause([-output, members[0], -member])
    solver.add_clause([output, *members])
    solver.add_clause([output, *(-member for member in members)])


def allowed_samples(supports, size, first_model, seed):
    """Represent each raw distinction across all sample states as a bit set."""
    full = (1 << SAMPLE_SIZE) - 1
    rng = random.Random(seed)
    columns = [full if bit > 0 else 0 for bit in first_model[:size]]
    holders = [[] for _ in range(size)]
    for law in supports:
        for member in law:
            holders[member].append(tuple(other for other in law if other != member))
    order = list(range(size))
    for _ in range(5):
        rng.shuffle(order)
        for member in order:
            forced_one = 0
            forced_zero = 0
            for others in holders[member]:
                seen_one = 0
                seen_zero = 0
                for other in others:
                    seen_one |= columns[other]
                    seen_zero |= full ^ columns[other]
                forced_one |= full ^ seen_one
                forced_zero |= full ^ seen_zero
            columns[member] = (rng.getrandbits(SAMPLE_SIZE) | forced_one) & ~forced_zero
    for law in supports:
        ones = zeros = full
        for member in law:
            ones &= columns[member]
            zeros &= full ^ columns[member]
        if ones or zeros:
            raise ValueError("Sample contains a disallowed raw state")
    return columns


def sample_agreements(carriers, columns):
    """Record, for each sample state, which of the carriers agree."""
    packed = np.frombuffer(
        b"".join(word.to_bytes(SAMPLE_SIZE // 8, "little") for word in columns),
        dtype=np.uint8,
    ).reshape(len(columns), -1)
    indexes = np.array([(first, second, rest[0] if rest else first)
                        for first, second, *rest in carriers])
    first, second, third = indexes.T
    agreement = ~((packed[first] ^ packed[second]) | (packed[first] ^ packed[third]))
    rows = np.packbits(np.unpackbits(agreement, axis=1, bitorder="little").T,
                       axis=1, bitorder="little")
    return [int.from_bytes(row.tobytes(), "little") for row in rows]


def set_bits(mask):
    while mask:
        bit = mask & -mask
        yield bit, bit.bit_length() - 1
        mask ^= bit


def is_bond_relation(mask):
    if mask in (0, 255):
        return False
    # The two words with a fixed pair differ only in the forgotten place.
    for offset in (1, 2, 4):
        for word in range(8):
            if word & offset == 0 and mask & ((1 << word) | (1 << (word + offset))) == 0:
                return False
    return True


class StageSearch:
    def __init__(self, supports, seed):
        self.supports = supports
        self.size = len(set().union(*map(set, supports)))
        self.carriers = tuple(combinations(range(self.size), 2)) + tuple(
            combinations(range(self.size), 3)
        )
        self.carrier_index = {carrier: i for i, carrier in enumerate(self.carriers)}
        self.all_carriers = (1 << len(self.carriers)) - 1
        membership = [bytearray((len(self.carriers) + 7) // 8) for _ in range(self.size)]
        for index, carrier in enumerate(self.carriers):
            for member in carrier:
                membership[member][index // 8] |= 1 << (index % 8)
        self.holding = [int.from_bytes(mask, "little") for mask in membership]
        self.visibly_readable = 0
        for law in supports:
            for size in (2, 3):
                for carrier in combinations(sorted(law), size):
                    self.visibly_readable |= 1 << self.carrier_index[carrier]

        self.solver = Solver(bootstrap_with=source_clauses(supports))
        if not self.solver.solve():
            raise ValueError("Source stage has no allowed state")
        self.columns = allowed_samples(supports, self.size, self.solver.get_model(), seed)
        self.sample_rows = sample_agreements(self.carriers, self.columns)
        self.sample_mask = (1 << SAMPLE_SIZE) - 1
        self.agreement_literals = {}
        self.locality_solver = None
        self.locality_literals = {}
        self.variation = {}
        self.counts = Counter()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.solver.delete()
        if self.locality_solver is not None:
            self.locality_solver.delete()

    def literal(self, carrier):
        if carrier not in self.agreement_literals:
            variable = self.size + 1 + len(self.agreement_literals)
            add_agreement(self.solver, carrier, variable)
            self.agreement_literals[carrier] = variable
        return self.agreement_literals[carrier]

    def variation_solver(self):
        if self.locality_solver is not None:
            return self.locality_solver
        n = self.size
        solver = Solver(bootstrap_with=source_clauses(self.supports))
        solver.append_formula(source_clauses(self.supports, n))
        for law_index, law in enumerate(self.supports):
            flag = 2 * n + 1 + law_index
            for member in law:
                variable = member + 1
                solver.add_clause([-flag, -variable, n + variable])
                solver.add_clause([-flag, variable, -(n + variable)])
        self.locality_solver = solver
        return solver

    def varies_at_every_law(self, carrier, witnesses=None):
        if witnesses is None and carrier in self.variation:
            return self.variation[carrier]
        if self.visibly_readable & (1 << self.carrier_index[carrier]):
            self.variation[carrier] = False
            return False
        solver = self.variation_solver()
        n = self.size
        if carrier not in self.locality_literals:
            output = 2 * n + len(self.supports) + 1 + 2 * len(self.locality_literals)
            add_agreement(solver, carrier, output)
            add_agreement(solver, carrier, output + 1, n)
            self.locality_literals[carrier] = output
        output = self.locality_literals[carrier]
        for i, law in enumerate(self.supports):
            self.counts["variation_sat_calls"] += 1
            if not solver.solve(assumptions=[output, -(output + 1), 2 * n + 1 + i]):
                self.variation[carrier] = False
                return False
            if witnesses is not None:
                selected = solver.get_model()
                agree = [int(bit > 0) for bit in selected[:n]]
                disagree = [int(bit > 0) for bit in selected[n:2 * n]]
                assert all(agree[member] == disagree[member] for member in law)
                assert len({agree[member] for member in carrier}) == 1
                assert len({disagree[member] for member in carrier}) == 2
                assert all(len({state[member] for member in raw_law}) == 2
                           for state in (agree, disagree) for raw_law in self.supports)
                witnesses.append([agree, disagree])
        self.variation[carrier] = True
        return True

    def sampled_word(self, carrier):
        first, second, *rest = carrier
        differences = self.columns[first] ^ self.columns[second]
        if rest:
            differences |= self.columns[first] ^ self.columns[rest[0]]
        return differences ^ self.sample_mask

    def unresolved_words(self, x, y, candidates):
        x_truth = self.sampled_word(x)
        y_truth = self.sampled_word(y)
        unresolved = []
        for x_value, y_value, _ in WORDS[::2]:
            sampled = (x_truth if x_value else x_truth ^ self.sample_mask) & (
                y_truth if y_value else y_truth ^ self.sample_mask
            )
            assumptions = [self.literal(x) if x_value else -self.literal(x),
                           self.literal(y) if y_value else -self.literal(y)]
            if not sampled:
                self.counts["projection_sat_calls"] += 1
                if not self.solver.solve(assumptions=assumptions):
                    return None
            some_agree = 0
            all_agree = candidates
            for sample_index, (_, index) in enumerate(set_bits(sampled)):
                if sample_index == SAMPLE_PER_WORD:
                    break
                agreements = self.sample_rows[index]
                some_agree |= agreements
                all_agree &= agreements
                if not all_agree and not (candidates & ~some_agree):
                    break
            unresolved.append((assumptions, all_agree, candidates & ~some_agree))
        return unresolved

    def word_exists(self, assumptions, carrier, agrees):
        # Complementing the whole source preserves every agreement. Fix one raw
        # distinction to 0, then test the two possible kinds of third reading.
        raw_variables = [member + 1 for member in carrier]
        if agrees:
            self.counts["projection_sat_calls"] += 1
            return self.solver.solve(assumptions=assumptions + [-v for v in raw_variables])
        for variable in raw_variables[1:]:
            self.counts["projection_sat_calls"] += 1
            if self.solver.solve(assumptions=assumptions + [-raw_variables[0], variable]):
                return True
        return False

    def search(self, x, y):
        if set(x) & set(y):
            raise ValueError(f"Fixed carriers overlap: {x} and {y}")
        disjoint = self.all_carriers
        for member in (*x, *y):
            disjoint &= ~self.holding[member]
        choices = disjoint.bit_count()
        raw_remaining = self.size - len(x) - len(y)
        assert choices == comb(raw_remaining, 2) + comb(raw_remaining, 3)
        candidates = disjoint & ~self.visibly_readable
        if self.visibly_readable & ((1 << self.carrier_index[x]) | (1 << self.carrier_index[y])):
            return choices, candidates.bit_count(), {}
        unresolved = self.unresolved_words(x, y, candidates)
        if unresolved is None:
            return choices, candidates.bit_count(), {}
        investigate = 0
        for _, missing_zero, missing_one in unresolved:
            investigate |= missing_zero | missing_one
        self.counts["thirds_needing_sat"] += investigate.bit_count()
        result = {}
        for candidate_bit, index in set_bits(investigate):
            carrier = self.carriers[index]
            mask = 255
            for prefix, (assumptions, missing_zero, missing_one) in enumerate(unresolved):
                if missing_zero & candidate_bit and not self.word_exists(assumptions, carrier, False):
                    mask ^= 1 << (2 * prefix)
                if missing_one & candidate_bit and not self.word_exists(assumptions, carrier, True):
                    mask ^= 1 << (2 * prefix + 1)
            if is_bond_relation(mask) and all(map(self.varies_at_every_law, (x, y, carrier))):
                result[carrier] = mask
        return choices, candidates.bit_count(), result


def direct_models(supports, size):
    masks = [sum(1 << member for member in law) for law in supports]
    return [state for state in range(1 << size)
            if all(0 < state & mask < mask for mask in masks)]


def direct_agreement(state, carrier_mask):
    return (state & carrier_mask) in (0, carrier_mask)


def direct_bonds(models, supports, pair, size):
    to_mask = lambda members: sum(1 << member for member in members)
    leftovers = sorted(set(range(size)).difference(*pair))
    result = {}
    pairs = [(direct_agreement(state, to_mask(pair[0])),
              direct_agreement(state, to_mask(pair[1])), state) for state in models]
    for third_size in (2, 3):
        for third in combinations(leftovers, third_size):
            third_mask = to_mask(third)
            words = set()
            for x, y, state in pairs:
                words.add((x, y, direct_agreement(state, third_mask)))
                if len(words) == 8:
                    break
            if len(words) in (0, 8) or any(len({(word[i], word[j]) for word in words}) != 4
                                          for i, j in combinations(range(3), 2)):
                continue
            if all(direct_variation(models, to_mask(carrier), to_mask(law))
                   for carrier in (*pair, third) for law in supports):
                result[third] = sum(1 << (4 * x + 2 * y + z) for x, y, z in words)
    return result


def direct_variation(models, carrier_mask, law_mask):
    readings = [set(), set()]
    for state in models:
        word = state & law_mask
        agrees = direct_agreement(state, carrier_mask)
        if word in readings[not agrees]:
            return True
        readings[agrees].add(word)
    return False


def run_controls(witness_stage=None):
    cases = []
    bare = [tuple(range(2 * i, 2 * i + 3)) for i in range(8)]
    with StageSearch(bare, 823) as search:
        models = direct_models(bare, search.size)
        for pair in named_pairs(bare, range(8)):
            direct = direct_bonds(models, bare, pair, search.size)
            assert not direct and search.search(*pair)[2] == direct
        cases.append({"case": "bare eight-law chain", "allowed_states": len(models),
                      "upper_pairs": 3, "determining_bonds": [0, 0, 0]})

    if witness_stage is None:
        return cases

    supports = witness_stage["supports"]
    pairs = named_pairs(supports, witness_stage["chains"][2])
    pair = ((3, 4, 8), (11, 13, 15))
    third = (0, 9, 12)
    assert pair in pairs or pair[::-1] in pairs
    with StageSearch(supports, 824) as search:
        models = direct_models(supports, search.size)
        direct = direct_bonds(models, supports, pair, search.size)
        _, _, actual = search.search(*pair)
        assert direct == actual and direct[third] == 127
        masks = [sum(1 << member for member in carrier) for carrier in (*pair, third)]
        counts = [0] * 8
        for state in models:
            x, y, z = [direct_agreement(state, mask) for mask in masks]
            counts[4 * x + 2 * y + z] += 1
        assert counts == [8586, 1968, 942, 186, 1206, 90, 132, 0]

        law_masks = [sum(1 << member for member in law) for law in supports]
        violations = Counter(
            sum(1 << index for index, law_mask in enumerate(law_masks)
                if direct_agreement(state, law_mask))
            for state in range(1 << search.size)
            if all(direct_agreement(state, mask) for mask in masks)
        )
        assert violations[0] == 0
        deletion_counts = [violations[1 << index] for index in range(len(supports))]
        essential = [index for index, restored in enumerate(deletion_counts) if restored]
        assert essential == [1, 6, 7, 9]
        essential_mask = sum(1 << index for index in essential)
        assert all(rejected & essential_mask for rejected in violations)
        cases.append({"case": "rival-law stage 0, chain index 2", "allowed_states": len(models),
                      "stage": witness_stage["id"], "chain_index": 2,
                      "pair": pair, "determining_bonds": len(actual), "third": third,
                      "word_state_counts": counts,
                      "states_restoring_111_at_each_single_deletion": deletion_counts,
                      "unique_minimal_source_laws": [supports[index] for index in essential]})
    return cases


def witness(search, stage, index, pair_index, x, y, third, relation, raw_labels):
    assignments = []
    for carrier in (x, y, third):
        by_law = []
        assert search.varies_at_every_law(carrier, witnesses=by_law)
        assignments.append(by_law)
    return {
        "stage": stage["id"], "chain_index": index, "chain": stage["chains"][index],
        "pair_index": pair_index, "supports": stage["supports"], "raw_order": raw_labels,
        "carriers": [[raw_labels[i] for i in carrier] for carrier in (x, y, third)],
        "allowed_words": [WORDS[i] for i in range(8) if relation & (1 << i)],
        "agree_and_disagree_witnesses_by_carrier_and_law": assignments,
    }


def run_census(stages, output):
    counts = Counter()
    total_by_pair = [Counter() for _ in BARE_PAIRS]
    relations = Counter()
    first_witness = None
    for stage in stages:
        raw_labels = sorted(set().union(*map(set, stage["supports"])))
        raw_index = {member: index for index, member in enumerate(raw_labels)}
        supports = [tuple(raw_index[member] for member in law) for law in stage["supports"]]
        counts["stages"] += 1
        counts["chains"] += len(stage["chains"])
        counts["max_distinctions"] = max(counts["max_distinctions"], len(raw_labels))
        stage_has_bond = False
        with StageSearch(supports, seed=42401 + stage["id"]) as search:
            cache = {}
            for index, chain in enumerate(stage["chains"]):
                pairs = named_pairs(supports, chain)
                all_named = set().union(*map(set, pairs))
                bond_counts = []
                named_bond_counts = []
                choices_per_pair = []
                for pair_index, (x, y) in enumerate(pairs):
                    pair = tuple(sorted((x, y)))
                    if pair not in cache:
                        cache[pair] = search.search(*pair)
                    choices, nonvisible, thirds = cache[pair]
                    bond_counts.append(len(thirds))
                    named_bond_counts.append(sum(third in all_named for third in thirds))
                    choices_per_pair.append(choices)
                    pair_counts = total_by_pair[pair_index]
                    pair_counts["third_carrier_choices"] += choices
                    pair_counts["thirds_contained_in_a_law"] += choices - nonvisible
                    pair_counts["determining_bonds"] += len(thirds)
                    pair_counts["named_third_bonds"] += named_bond_counts[-1]
                    pair_counts["pairs_with_a_bond"] += bool(thirds)
                    for relation in thirds.values():
                        relations[relation] += 1
                    if thirds and first_witness is None:
                        third = next(iter(thirds))
                        first_witness = witness(search, stage, index, pair_index, *pair, third,
                                                thirds[third], raw_labels)
                stage_has_bond |= any(bond_counts)
                counts["chains_with_a_bond"] += any(bond_counts)
                output.write(json.dumps({"stage": stage["id"], "chain_index": index,
                                         "determining_bonds": bond_counts,
                                         "third_carrier_choices": choices_per_pair,
                                         "named_third_bonds": named_bond_counts},
                                        separators=(",", ":")) + "\n")
            counts["stages_with_a_bond"] += stage_has_bond
            counts["distinct_stage_pairs"] += len(cache)
            counts["distinct_stage_pairs_with_a_bond"] += sum(bool(result[2]) for result in cache.values())
            counts["distinct_stage_pair_determining_bonds"] += sum(len(result[2]) for result in cache.values())
            counts.update(search.counts)
    return {"coverage": counts, "totals_by_pair": total_by_pair,
            "totals": sum(total_by_pair, Counter()), "relations": relations,
            "first_witness": first_witness}


def main():
    options = argparse.ArgumentParser(description=__doc__)
    options.add_argument("--pilot", action="store_true",
                         help="Use the pilot stages or run only the bare-chain control")
    options.add_argument("--widest", type=int, default=0,
                         help="Time only this many of the widest full-census stages")
    options.add_argument("--controls", action="store_true", help="Run direct raw truth-table controls")
    args = options.parse_args()
    if args.pilot and args.widest:
        options.error("Choose either --pilot or --widest")
    start = time.monotonic()
    if args.controls:
        witness_stage = None if args.pilot else next(read_rows(ROOT / "step_stages.jsonl.gz"))
        summary = {"direct_controls": run_controls(witness_stage)}
        suffix = "_controls_pilot" if args.pilot else "_controls"
    else:
        input_suffix = "_pilot" if args.pilot else ""
        suffix = "_widest" if args.widest else input_suffix
        stages = read_rows(ROOT / f"step_stages{input_suffix}.jsonl.gz")
        if args.widest:
            stages = sorted(stages, key=lambda row: (
                len(set().union(*map(set, row["supports"]))), len(row["chains"])
            ), reverse=True)[:args.widest]
        with gzip.open(ROOT / f"step_paired_rows{suffix}.jsonl.gz", "wt") as output:
            summary = run_census(stages, output)
        summary["sample_states_per_stage"] = SAMPLE_SIZE
        summary["sample_states_per_pair_word_limit"] = SAMPLE_PER_WORD
    summary["wall_seconds"] = time.monotonic() - start
    summary["peak_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    with (ROOT / f"step_paired{suffix}.json").open("w") as output:
        json.dump(summary, output, indent=2)
        output.write("\n")
    print(json.dumps({key: value for key, value in summary.items() if key != "first_witness"}))


if __name__ == "__main__":
    main()
