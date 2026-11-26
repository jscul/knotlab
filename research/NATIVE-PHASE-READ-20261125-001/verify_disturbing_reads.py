"""Sensitivity to ordinary reads that write, repeatability, and a copied preparation."""

from collections import Counter
from itertools import combinations, permutations, product

from pysat.solvers import Solver


WORDS = tuple(w for w in range(8) if w.bit_count() % 2 == 0)
INDICES = range(len(WORDS))
READERS = range(3)
SETTINGS = (0, 1)
ORDERS = tuple(permutations(READERS))


def bit(word, i):
    return (word >> (2 - i)) & 1


def transition(i, setting, start, end):
    return 1 + ((i * 2 + setting) * 4 + start) * 4 + end


def incompatible_report(i, setting, word_index, answer):
    """Clause literals excluding this report. None means the report cannot occur."""
    if setting == 0:
        return [] if bit(WORDS[word_index], i) == answer else None
    variable = 97 + 4 * i + word_index
    return [-variable if answer else variable]


def clauses(starts, repeat, repeat_starts=INDICES, interposed=False):
    formula = set()

    def add(literals):
        unique = set(literals)
        if all(-literal not in unique for literal in unique):
            formula.add(tuple(sorted(unique)))

    for i, setting, w in product(READERS, SETTINGS, INDICES):
        possible = [transition(i, setting, w, t) for t in INDICES]
        add(possible)
        for first, other in combinations(possible, 2):
            add([-first, -other])
        if repeat and w in repeat_starts:
            for t, answer in product(INDICES, SETTINGS):
                before = incompatible_report(i, setting, w, answer)
                after = incompatible_report(i, setting, t, 1 - answer)
                if before is not None and after is not None:
                    add([-transition(i, setting, w, t)] + before + after)

    if interposed:
        for i, j in permutations(READERS, 2):
            for s, other_s, w, t, v in product(SETTINGS, SETTINGS, starts, INDICES, INDICES):
                for answer in SETTINGS:
                    before = incompatible_report(i, s, w, answer)
                    after = incompatible_report(i, s, v, 1 - answer)
                    if before is not None and after is not None:
                        add([-transition(i, s, w, t), -transition(j, other_s, t, v)] + before + after)

    for setting, order in product(WORDS, ORDERS):
        i, j, k = order
        settings = [bit(setting, reader) for reader in order]
        wrong = [out for out in product(SETTINGS, repeat=3) if sum(out) % 2 != bool(setting)]
        for w, t, v in product(starts, INDICES, INDICES):
            edges = [-transition(i, settings[0], w, t), -transition(j, settings[1], t, v)]
            for out in wrong:
                reports = [incompatible_report(party, s, state, ans)
                           for party, s, state, ans in zip(order, settings, (w, t, v), out)]
                if all(report is not None for report in reports):
                    add(edges + [literal for report in reports for literal in report])
    return sorted(formula)


def solve(formula, solver_name):
    with Solver(name=solver_name, bootstrap_with=formula) as solver:
        return set(solver.get_model()) if solver.solve() else None


def instrument_from_model(model):
    rules = {}
    for i, setting, w in product(READERS, SETTINGS, INDICES):
        image, = [t for t in INDICES if transition(i, setting, w, t) in model]
        answer = bit(WORDS[w], i) if setting == 0 else int(97 + 4 * i + w in model)
        rules[i, setting, WORDS[w]] = (answer, WORDS[image])
    return rules


def translation_read(i, setting, w, seed):
    """One independent shared sign, fixed for the trial. All writes preserve parity."""
    if setting == 0:
        return bit(w, i), w ^ (0b110, 0b101, 0b011)[i]
    answers = (1, 1 ^ bit(w, 2), bit(w, 1))
    return answers[i] ^ seed, w ^ (0b000, 0b011, 0b101)[i]


def with_copied_preparation(rules):
    def read(i, setting, w, seed):
        initial, r = seed
        answer, t = rules[i, setting, w ^ initial]
        return answer ^ bit(initial, i) ^ (r if setting else 0), t ^ initial
    return read


def complete_tables(read, starts_and_seeds):
    matched = Counter()
    for order, setting in product(ORDERS, range(8)):
        counts = Counter()
        for w, seed in starts_and_seeds:
            outcome = 0
            for i in order:
                answer, w = read(i, bit(setting, i), w, seed)
                assert w in WORDS
                outcome |= answer << (2 - i)
            counts[outcome] += 1
        promised = setting in WORDS
        target_parity = int(setting != 0)
        correct = True
        for outcome in range(8):
            if promised and outcome.bit_count() % 2 != target_parity:
                assert counts[outcome] == 0
            elif counts[outcome] * (4 if promised else 8) != len(starts_and_seeds):
                correct = False
        matched[promised] += correct
    return matched


def test_repeat(read, starts_and_seeds, intervening=False):
    changed = Counter()
    for i, setting in product(READERS, SETTINGS):
        for w, seed in starts_and_seeds:
            first, t = read(i, setting, w, seed)
            if intervening:
                for j, other_setting in product(READERS, SETTINGS):
                    if i != j:
                        _, v = read(j, other_setting, t, seed)
                        again, _ = read(i, setting, v, seed)
                        changed[i, setting, j, other_setting] += again != first
            else:
                again, _ = read(i, setting, t, seed)
                changed[i, setting] += again != first
    return changed


def main():
    full = list(product(WORDS, SETTINGS))
    assert complete_tables(translation_read, full) == {True: 24, False: 24}
    assert complete_tables(translation_read, [(w, 0) for w in WORDS]) == {True: 12, False: 0}
    repeats = test_repeat(translation_read, full)
    assert repeats == {(0, 0): 8, (0, 1): 0, (1, 0): 0, (1, 1): 8, (2, 0): 8, (2, 1): 0}
    print("Ordinary reads may write: 384/384 cells; 3 of the 6 instruments always reverse on repetition.")

    full_constraints = clauses(INDICES, repeat=True)
    assert len(full_constraints) == 2652
    assert solve(full_constraints, "g4") is None and solve(full_constraints, "cadical195") is None
    counts = {}
    for k in (1, 2, 3):
        counts[k] = sum(solve(clauses(subset, repeat=True), "g4") is not None
                        for subset in combinations(INDICES, k))
    assert counts == {1: 4, 2: 6, 3: 0}
    print("All 108-variable constraints checked: 4/4 singleton, 6/6 pair, 0/4 triple and 0/1 full supports admit repeatable parity rules.")

    # A read-only copy of the initial word lets each trial use the same
    # single-start witness. Both its action and its reported sign are relabelled.
    model = solve(clauses((0,), repeat=True), "g4")
    copy_read = with_copied_preparation(instrument_from_model(model))
    calibrated = [(initial, (initial, r)) for initial, r in full]
    assert complete_tables(copy_read, calibrated) == {True: 24, False: 24}
    assert not any(test_repeat(copy_read, calibrated).values())
    changes = test_repeat(copy_read, calibrated, intervening=True)
    print("Copied preparation: 384/384 cells and all immediate repeats agree.")
    # Report the interposed read explicitly; different valid SAT witnesses can
    # choose different failing histories.
    if any(changes.values()):
        (i, s, j, other_s), n = next((key, n) for key, n in changes.items() if n)
        print(f"Intervening read: reader {i} setting {s}, reader {j} setting {other_s}, "
              f"reader {i} setting {s}: {n}/8 repeated answers changed.")
    else:
        print("This witness also passes every tested single interposed read.")

    for w in INDICES:
        singleton = (w,)
        holdout = clauses(singleton, repeat=True, repeat_starts=singleton, interposed=True)
        first = solve(holdout, "g4")
        second = solve(holdout, "cadical195")
        assert first is not None and second is not None
        if w == 0:
            calibrated_read = with_copied_preparation(instrument_from_model(first))
            assert complete_tables(calibrated_read, calibrated) == {True: 24, False: 24}
            assert not any(test_repeat(calibrated_read, calibrated).values())
            assert not any(test_repeat(calibrated_read, calibrated, intervening=True).values())
        print(f"Single start {WORDS[w]:03b}, remote intervening read and immediate repeat: "
              f"SAT ({len(holdout)} clauses)")
    # Fixed witness in the report, independent of which model a solver returns.
    # Each row lists the answers and next words in WORDS order.
    witness = {
        (0, 0): ("0011", (0b011, 0b000, 0b101, 0b110)),
        (0, 1): ("1111", (0b000, 0b011, 0b000, 0b110)),
        (1, 0): ("0101", (0b101, 0b011, 0b000, 0b110)),
        (1, 1): ("1100", (0b011, 0b000, 0b000, 0b110)),
        (2, 0): ("0110", (0b110, 0b011, 0b101, 0b000)),
        (2, 1): ("0000", (0b000, 0b011, 0b101, 0b110)),
    }
    fixed_rules = {(i, setting, w): (int(answers[index]), images[index])
                   for (i, setting), (answers, images) in witness.items()
                   for index, w in enumerate(WORDS)}
    read = with_copied_preparation(fixed_rules)
    assert complete_tables(read, calibrated) == {True: 24, False: 24}
    assert not any(test_repeat(read, calibrated).values())
    assert not any(test_repeat(read, calibrated, intervening=True).values())
    print("Second copied-start rule reproduced 384 cells, all 48 immediate and 192 interposed-read trials.")


if __name__ == "__main__":
    main()
