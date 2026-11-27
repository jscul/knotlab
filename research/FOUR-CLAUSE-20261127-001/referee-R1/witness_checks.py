"""Replay the two reported four-clause witnesses by exact state enumeration."""

import argparse
from dataclasses import asdict
from itertools import combinations, product
import json
import os
from pathlib import Path
from subprocess import check_output
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RESEARCH = ROOT / "research"
CENSUS = RESEARCH / "FORBID-EDITS-20261126-001/starts.json"
CONTROL = RESEARCH / "UPPER-GROWN-20261127-001/referee-R1/upper_sample.json"
SAMPLE = HERE.parent / "out/four_6.jsonl"
GROWTH = RESEARCH / "NAE-LAYER-20261127-001/referee-R1"
sys.path.insert(0, str(GROWTH))
from growth_rule import advance, supports_of


FOUR = ((0, 2, 4), (0, 3, 5), (1, 2, 5), (1, 3, 4))
CARRIERS_5260 = ((2, 8, 10), (7, 13), (0, 1, 5), (9, 12, 14), (3, 4, 11), (6, 15, 16))
ALL_TRIPLES = tuple(combinations(range(6), 3))
FULL_TRIPLE = tuple(f"{word:03b}" for word in range(8))
KNOT_WORDS = FULL_TRIPLE[:-1]


def columns(width):
    """Bit s is set in column i exactly when assignment s gives distinction i value 1."""
    result = []
    for i in range(width):
        if i < 3:
            block = bytes([(0xAA, 0xCC, 0xF0)[i]])
        else:
            span = 1 << (i - 3)
            block = bytes(span) + b"\xff" * span
        result.append(int.from_bytes(block * ((1 << (width - 3)) // len(block)), "little"))
    return tuple(result)


class States:
    def __init__(self, supports):
        self.width = max(max(support) for support in supports) + 1
        self.raw = columns(self.width)
        self.universe = (1 << (1 << self.width)) - 1
        self.law = tuple(self.universe ^ self.agreement(support) for support in supports)
        self.allowed = self.obey(range(len(supports)))
        self.knot_fixes = [self.cells(self.allowed, tuple(self.raw[i] for i in s)) for s in supports]

    def agreement(self, support):
        ones = zeros = self.universe
        for i in support:
            ones &= self.raw[i]
            zeros &= self.universe ^ self.raw[i]
        return ones | zeros

    def obey(self, laws):
        states = self.universe
        for i in laws:
            states &= self.law[i]
        return states

    def cells(self, states, readings):
        cells = {"": states}
        for reading in readings:
            refined = {}
            for word, cell in cells.items():
                for bit, mask in (("0", self.universe ^ reading), ("1", reading)):
                    if matches := cell & mask:
                        refined[word + bit] = matches
            cells = refined
        return cells

    def flip_witness(self, reading, i):
        step = 1 << i
        changing = (reading ^ (reading >> step)) & self.allowed
        changing &= (self.allowed >> step) & (self.universe ^ self.raw[i])
        if changing:
            first = (changing & -changing).bit_length() - 1
            return [first, first + step]
        return None


def mixed(fixes, reading):
    return sum(bool(cell & reading) and (cell & reading) != cell for cell in fixes.values())


def counts(cells):
    return {word: cell.bit_count() for word, cell in sorted(cells.items())}


def choose(readings, positions):
    return tuple(readings[i] for i in positions)


def upper_values(lower, both):
    return tuple((first & second) if i == both else (first | second)
                 for i, (first, second) in enumerate(zip(lower[::2], lower[1::2], strict=True)))


def pair_images(words):
    return {f"{i}{j}": sorted({word[i] + word[j] for word in words})
            for i, j in combinations(range(3), 2)}


def clause_for_missing(names, word):
    return " ".join(f"~{name}" if value == "1" else name
                    for name, value in zip(names, word, strict=True))


def canonical(lower_words, upper_words, both):
    """Independently check K1-K3, forgetting all six readings of the lower layer."""
    C = tuple(f"Q{i}" for i in range(6))
    U = ("A", "B", "C")
    clauses = [clause_for_missing(C, f"{word:06b}") for word in range(64)
               if f"{word:06b}" not in lower_words]
    for i, name in enumerate(U):
        for a, b, value in product((0, 1), repeat=3):
            correct = (a & b) if i == both else (a | b)
            if value != correct:
                clauses.append(clause_for_missing((C[2 * i], C[2 * i + 1], name), f"{a}{b}{value}"))
    checks = []
    for contact in U:
        loops = [name for name in U if name != contact]
        argv = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", "; ".join(clauses),
                "--loops", *loops, "--contact", contact, "--witnesses", *C, "--json"]
        report = json.loads(check_output(argv, env={**os.environ, "PYTHONPATH": str(ROOT / "tools")}, cwd=ROOT))
        ordered = {"".join(word[report["variables"].index(name)] for name in U) for word in report["allowed"]}
        assert ordered == set(upper_words) and report["is_knot"]
        checks.append({key: report[key] for key in ("variables", "allowed", "binding", "loss_on_erasure",
                                                    "coexistence", "is_knot")})
    return checks


def abstract_check(both):
    raw_words = tuple(product((0, 1), repeat=6))
    images = []
    for omit in (None, *range(len(FOUR))):
        retained = [word for word in raw_words if all(i == omit or not all(choose(word, clause))
                                                     for i, clause in enumerate(FOUR))]
        image = sorted({"".join(map(str, upper_values(word, both))) for word in retained})
        restores = ["".join(map(str, word)) for word in retained if all(upper_values(word, both))]
        assert tuple(image) == (KNOT_WORDS if omit is None else FULL_TRIPLE)
        images.append({"omitted_lower_clause_index": omit, "lower_words": len(retained),
                       "upper_words": image, "lower_words_giving_upper_111": restores})
    return images


def perfect_matchings(names):
    if not names:
        yield ()
        return
    first, *tail = names
    for other in tail:
        rest = tuple(value for value in tail if value != other)
        for matching in perfect_matchings(rest):
            yield ((first, other), *matching)


def other_pairings(lower_cells):
    """Check every partition and its two choices of alternating triples on these six carriers."""
    missing = {subset: set(FULL_TRIPLE) - {"".join(choose(word, subset)) for word in lower_cells}
               for subset in ALL_TRIPLES}
    matches = []
    for pairs in perfect_matchings(tuple(range(6))):
        for parity in range(2):
            triples = [tuple(sorted(pairs[i][role] for i, role in enumerate(roles)))
                       for roles in product((0, 1), repeat=3) if sum(roles) % 2 == parity]
            if any(len(missing[triple]) != 1 for triple in triples):
                continue
            signs = dict()
            for triple in triples:
                word = next(iter(missing[triple]))
                for i, sign in zip(triple, word, strict=True):
                    signs.setdefault(i, set()).add(sign)
            if all(len(values) == 1 for values in signs.values()):
                matches.append({"pairs": pairs, "parity": parity, "clauses": triples,
                                "signed_values_in_carrier_order": [next(iter(signs[i])) for i in range(6)]})
    return matches


def prior_rounds(states, supports_by_round, carriers, upper):
    result = []
    for round_number, supports in enumerate(supports_by_round[:-1]):
        width = max(max(s) for s in supports) + 1
        available = [i for i, carrier in enumerate(carriers) if max(carrier) < width]
        actual = States(supports)
        extended = states.obey(range(len(supports)))
        projected = 0
        for extension in range(1 << (states.width - width)):
            projected |= (states.allowed >> (extension << width)) & actual.universe
        assert projected == actual.allowed
        assert extended.bit_count() == actual.allowed.bit_count() << (states.width - width)
        result.append({"round": round_number, "distinctions": width, "knots": len(supports),
                       "allowed_states": actual.allowed.bit_count(), "projection_unchanged": True,
                       "carrier_indices_already_present": available,
                       "fixed_upper_readings_defined_on_actual_round": len(available) == len(carriers),
                       "upper_counts_after_adding_free_later_distinctions": counts(states.cells(extended, upper))})
    return result


def check_role(states, carriers, lower, lower_cells, triples, stages, both):
    upper = upper_values(lower, both)
    upper_cells = states.cells(states.allowed, upper)
    assert tuple(sorted(upper_cells)) == KNOT_WORDS
    pair_words = pair_images(upper_cells)
    assert all(len(image) == 4 for image in pair_words.values())
    local = [[mixed(triples[clause], read) for read in upper] for clause in FOUR]
    assert all(value > 0 for row in local for value in row)

    deletions = []
    for i, support in enumerate(stages[-1]):
        remaining = states.obey(set(range(len(stages[-1]))) - {i})
        cells = states.cells(remaining, upper)
        restored = cells.get("111", 0)
        deletions.append({"law_index": i, "knot": support, "round": sum(i >= len(s) for s in stages[:-1]),
                          "allowed_states_after_deletion": remaining.bit_count(), "states_restoring_111": restored.bit_count(),
                          "first_restored_state": (restored & -restored).bit_length() - 1 if restored else None,
                          "upper_word_counts_after_deletion": counts(cells)})
    essential = [row["law_index"] for row in deletions if row["states_restoring_111"]]
    essential_image = states.cells(states.obey(essential), upper)
    assert tuple(sorted(essential_image)) == KNOT_WORDS
    deterministic = []
    for subset, cells in triples.items():
        reads = [i for i, reading in enumerate(upper) if not mixed(cells, reading)]
        if reads:
            is_bond = 0 < len(cells) < 8 and all(len(s) == 4 for s in pair_images(cells).values())
            deterministic.append({"carrier_indices": subset, "upper_reading_indices": reads,
                                  "this_triple_itself_a_bond": is_bond})
    return {
        "both_pair": "ABC"[both],
        "upper_word_counts": counts(upper_cells),
        "upper_pair_images": pair_words,
        "fixes_leaving_both_values_per_reading_for_each_of_four_lower_bonds": local,
        "fixes_leaving_both_values_per_upper_reading_at_each_knot": [
            [mixed(cell, read) for read in upper] for cell in states.knot_fixes],
        "deterministic_by_any_three_of_six_carrier_readings": deterministic,
        "individual_law_deletions": deletions,
        "unique_minimal_law_indices_for_upper_111_exclusion": essential,
        "upper_word_counts_with_only_essential_laws": counts(essential_image),
        "earlier_rounds": prior_rounds(states, stages, carriers, upper),
        "four_clauses_on_independent_lower_readings": abstract_check(both),
        "canonical_check": canonical(lower_cells, upper_cells, both),
    }


def replay(census, rank, carriers, signs, pilot):
    assert len(carriers) == len(signs) == 6
    assert len(set().union(*map(set, carriers))) == sum(map(len, carriers))
    assert all(len(carrier) in (2, 3) for carrier in carriers)
    assert tuple(signs) == (1,) * 6
    stages = [supports_of(census[rank])]
    births = []
    for _ in range(2):
        grown = advance(stages[-1])
        assert grown.status == "funded"
        stages.append(grown.supports)
        births.append([asdict(birth) for birth in grown.births])

    states = States(stages[-1])
    lower = tuple(states.agreement(carrier) for carrier in carriers)
    lower_cells = states.cells(states.allowed, lower)
    triples = {subset: states.cells(states.allowed, choose(lower, subset)) for subset in ALL_TRIPLES}
    assert all(tuple(sorted(triples[clause])) == KNOT_WORDS for clause in FOUR)
    unread = [[mixed(cell, read) for read in lower] for cell in states.knot_fixes]
    assert all(all(row) for row in unread)
    flips = [{str(i): states.flip_witness(read, i) for i in carrier}
             for read, carrier in zip(lower, carriers, strict=True)]
    assert all(all(row.values()) for row in flips)

    for assignment in range(512):
        expected = [i for i, support in enumerate(stages[-1])
                    if len({(assignment >> place) & 1 for place in support}) == 1]
        measured = [i for i, law in enumerate(states.law) if not ((law >> assignment) & 1)]
        assert measured == expected

    return {"census_entry": rank, "round": 2, "knots_by_round": stages,
            "growth_births_by_round": births, "distinctions": states.width,
            "allowed_states": states.allowed.bit_count(), "carriers_in_A0_A1_B0_B1_C0_C1_order": carriers,
            "forbidden_values_of_six_agreements": signs, "lower_bond_indices": FOUR,
            "six_reading_word_counts": counts(lower_cells),
            "lower_bond_word_counts": [counts(triples[clause]) for clause in FOUR],
            "fixes_leaving_both_values_per_lower_reading_at_each_knot": unread,
            "single_change_witnesses_per_lower_carrier_member": flips,
            "pairings_with_four_consistently_signed_clauses_on_these_six_carriers": other_pairings(lower_cells),
            "upper_roles": [check_role(states, carriers, lower, lower_cells, triples, stages, both)
                            for both in (range(1) if pilot else range(3))]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    census = json.loads(CENSUS.read_text())
    archive_420 = json.loads(CONTROL.read_text())[0]["witness"]
    carriers, signs = zip(*archive_420["raw_agreements_and_selected_value"], strict=True)
    control = replay(census, 420, tuple(map(tuple, carriers)), signs, args.pilot)
    assert tuple(map(tuple, archive_420["source"])) == control["knots_by_round"][-1]
    assert control["allowed_states"] == 17928
    assert [int(word, 2) for word in control["six_reading_word_counts"]] == archive_420["actual_lower_words"]
    assert [row["states_restoring_111"] for row in control["upper_roles"][0]["individual_law_deletions"]] == (
        archive_420["restored_upper_111_by_dropped_law"])
    assert {tuple(sorted(s)) for s in archive_420["lower_clauses"]} == set(FOUR)
    result = {"growth_source": str((GROWTH / "growth_rule.py").relative_to(ROOT)),
              "census_source": str(CENSUS.relative_to(ROOT)),
              "state_encoding": "Distinction i is bit i in the integer assignment labels.",
              "word_encoding": "Displayed words give values in the stated order from left to right.",
              "deletion_semantics": "Keep all distinctions, carriers, and remaining laws of the final round fixed.",
              "census_420": control}
    if not args.pilot:
        archive_5260 = next(row for line in SAMPLE.read_text().splitlines()
                            if (row := json.loads(line))["start"] == "census 5260")
        case = replay(census, 5260, CARRIERS_5260, (1,) * 6, args.pilot)
        assert [(max(max(s) for s in supports) + 1, len(supports)) for supports in case["knots_by_round"]] == [
            (row["distinctions"], row["knots"]) for row in archive_5260["rounds"]]
        result["census_5260"] = case
    if args.out:
        args.out.write_text(json.dumps(result, indent=2) + "\n")
    else:
        print(json.dumps({key: {"allowed_states": row["allowed_states"], "roles": len(row["upper_roles"])}
                          for key, row in result.items() if isinstance(row, dict)}))


if __name__ == "__main__":
    main()
