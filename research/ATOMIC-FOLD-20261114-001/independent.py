"""Independent finite checks for ATOMIC-FOLD-20261114-001.

Only the six raw membership bits and the declared downstream queries define
the oracle.  This module imports neither a producer nor a learned policy.
Programs have exactly three ordinary Boolean gates, followed by one or two
output taps.  Decoder data are literal (code, query) lookup entries; the
decoder is never passed a world, a scratch register, or a program.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from fractions import Fraction
from itertools import combinations, product
import json


ALL_WORLDS = tuple(range(64))
EVEN_WORLDS = tuple(world for world in ALL_WORLDS if world.bit_count() % 2 == 0)
ODD_WORLDS = tuple(world for world in ALL_WORLDS if world.bit_count() % 2 == 1)
INPUT_NAMES = ("A0", "A1", "B0", "B1", "C0", "C1")
# Pair indices identify A, B, C; masks 1, 2, 3 select h=0, h=1, either.
CONTEXTS = {
    0: {"pair": (1, 2), "kind": "selective", "queries": (1, 2, 3)},
    1: {"pair": (0, 1), "kind": "broad", "queries": (3,)},
    2: {"pair": (0, 2), "kind": "selective", "queries": (1, 2, 3)},
    3: {"pair": (1, 2), "kind": "broad", "queries": (3,)},
    4: {"pair": (0, 1), "kind": "selective", "queries": (1, 2, 3)},
    5: {"pair": (0, 2), "kind": "broad", "queries": (3,)},
}

Gate = tuple[str, int, int]
Code = tuple[int, ...]
Decoder = dict[tuple[Code, int], int]


def _context(context: int | str) -> int:
    if isinstance(context, str) and len(context) == 2 and context[0] == "c":
        context = int(context[1])
    if type(context) is not int or context not in CONTEXTS:
        raise ValueError("context must be 0..5 or c0..c5")
    return context


def _world(world: int) -> int:
    if type(world) is not int or not 0 <= world < 64:
        raise ValueError("world must be a six-bit integer")
    return world


def raw_bits(world: int) -> tuple[int, ...]:
    return tuple((_world(world) >> index) & 1 for index in range(6))


def oracle(world: int, context: int | str, mask: int) -> int:
    """Enumerate the two h values against the original individual rules."""
    world = _world(world)
    context = _context(context)
    if type(mask) is not int or mask not in CONTEXTS[context]["queries"]:
        raise ValueError("query is not offered in this context")
    left, right = CONTEXTS[context]["pair"]
    for h in (0, 1):
        if mask & (1 << h):
            left_allows = (world >> (2 * left + h)) & 1
            right_allows = (world >> (2 * right + h)) & 1
            if left_allows and right_allows:
                return 1
    return 0


def truth_rows(context: int | str) -> list[dict]:
    """All raw worlds, split membership, and complete offered answer vectors."""
    context = _context(context)
    return [
        {
            "world": world,
            "bits": raw_bits(world),
            "split": "train" if world in EVEN_WORLDS else "heldout",
            "answers": tuple(oracle(world, context, mask) for mask in CONTEXTS[context]["queries"]),
        }
        for world in ALL_WORLDS
    ]


def validate_program(gates: Sequence[Sequence], taps: Sequence[int]) -> tuple[tuple[Gate, ...], Code]:
    if len(gates) != 3:
        raise ValueError("a program must contain exactly three gates")
    normalized = []
    for gate_index, gate in enumerate(gates):
        if len(gate) != 3:
            raise ValueError("a gate is (operation, left register, right register)")
        operation, left, right = gate
        if operation not in ("AND", "OR", "XOR", "NAND"):
            raise ValueError("unknown Boolean operation")
        if any(type(index) is not int or not 0 <= index < 6 + gate_index for index in (left, right)):
            raise ValueError("a gate may read only an input or an earlier gate")
        normalized.append((operation, left, right))
    if len(taps) not in (1, 2) or any(type(index) is not int or not 0 <= index < 9 for index in taps):
        raise ValueError("select one or two valid output registers")
    return tuple(normalized), tuple(taps)


def _execute(world: int, gates: tuple[Gate, ...], taps: Code) -> Code:
    registers = list(raw_bits(world))
    for operation, left, right in gates:
        a, b = registers[left], registers[right]
        if operation == "AND":
            value = a & b
        elif operation == "OR":
            value = a | b
        elif operation == "XOR":
            value = a ^ b
        else:
            value = 1 - (a & b)
        registers.append(value)
    return tuple(registers[index] for index in taps)


def execute(world: int, gates: Sequence[Sequence], taps: Sequence[int]) -> Code:
    gates, taps = validate_program(gates, taps)
    return _execute(_world(world), gates, taps)


def live_gates(gates: Sequence[Sequence], taps: Sequence[int]) -> tuple[int, ...]:
    gates, taps = validate_program(gates, taps)
    needed = list(taps)
    live = set()
    while needed:
        register = needed.pop()
        if register >= 6 and register - 6 not in live:
            gate_index = register - 6
            live.add(gate_index)
            needed.extend(gates[gate_index][1:])
    return tuple(sorted(live))


def _fit_codes(context: int, codes: Mapping[int, Code], worlds: Iterable[int]) -> Decoder:
    counts = defaultdict(lambda: [0, 0])
    for world in worlds:
        world = _world(world)
        for mask in CONTEXTS[context]["queries"]:
            counts[(codes[world], mask)][oracle(world, context, mask)] += 1
    return {key: int(labels[1] > labels[0]) for key, labels in counts.items()}


def fit_decoder(context: int | str, gates: Sequence[Sequence], taps: Sequence[int],
                worlds: Iterable[int] = EVEN_WORLDS) -> Decoder:
    """Conditional majority on training labels, with zero for ties."""
    context = _context(context)
    gates, taps = validate_program(gates, taps)
    codes = {world: _execute(world, gates, taps) for world in ALL_WORLDS}
    return _fit_codes(context, codes, worlds)


def validate_decoder(context: int | str, width: int, decoder: Mapping) -> Decoder:
    """Accept literal lookup data only, keeping source state out of decoding."""
    context = _context(context)
    if not isinstance(decoder, Mapping):
        raise ValueError("decoder must be literal lookup data")
    result = {}
    for key, label in decoder.items():
        if not isinstance(key, tuple) or len(key) != 2:
            raise ValueError("decoder key must be (code tuple, query mask)")
        code, mask = key
        if (not isinstance(code, tuple) or len(code) != width
                or any(type(bit) is not int or bit not in (0, 1) for bit in code)
                or type(mask) is not int or mask not in CONTEXTS[context]["queries"]
                or type(label) is not int or label not in (0, 1)):
            raise ValueError("decoder contains an invalid code, query, or label")
        result[key] = label
    return result


def decode(code: Code, mask: int, decoder: Mapping) -> int:
    """An absent cell, like a tied training cell, answers zero."""
    return decoder.get((code, mask), 0)


def _score(context: int, codes: Mapping[int, Code], decoder: Mapping,
           worlds: Iterable[int]) -> dict:
    worlds = tuple(worlds)
    correct = total = 0
    first_failure = None
    for world in worlds:
        for mask in CONTEXTS[context]["queries"]:
            expected = oracle(world, context, mask)
            actual = decode(codes[world], mask, decoder)
            correct += actual == expected
            total += 1
            if actual != expected and first_failure is None:
                first_failure = {"world": world, "mask": mask, "code": codes[world],
                                 "expected": expected, "actual": actual}
    return {"correct": correct, "total": total, "accuracy": correct / total,
            "exact": correct == total, "first_failure": first_failure}


def assess(context: int | str, gates: Sequence[Sequence], taps: Sequence[int],
           decoder: Mapping | None = None, *, include_rows: bool = False) -> dict:
    """Fit on even worlds unless a frozen literal decoder is supplied."""
    context = _context(context)
    gates, taps = validate_program(gates, taps)
    codes = {world: _execute(world, gates, taps) for world in ALL_WORLDS}
    if decoder is None:
        decoder = _fit_codes(context, codes, EVEN_WORLDS)
    decoder = validate_decoder(context, len(taps), decoder)
    result = {"context": context, "width": len(taps), "live_gates": live_gates(gates, taps),
              "train": _score(context, codes, decoder, EVEN_WORLDS),
              "heldout": _score(context, codes, decoder, ODD_WORLDS),
              "all": _score(context, codes, decoder, ALL_WORLDS)}
    if include_rows:
        result["rows"] = [
            {**row, "code": codes[row["world"]],
             "decoded": tuple(decode(codes[row["world"]], mask, decoder)
                              for mask in CONTEXTS[context]["queries"])}
            for row in truth_rows(context)
        ]
    return result


def quotient(context: int | str, gates: Sequence[Sequence], taps: Sequence[int]) -> dict:
    """Coarsest answer equivalence, code collisions, and excess distinctions."""
    context = _context(context)
    gates, taps = validate_program(gates, taps)
    truth_groups, code_groups = defaultdict(list), defaultdict(list)
    truth = {}
    for world in ALL_WORLDS:
        truth[world] = tuple(oracle(world, context, mask) for mask in CONTEXTS[context]["queries"])
        truth_groups[truth[world]].append(world)
        code_groups[_execute(world, gates, taps)].append(world)
    collisions = []
    for code, worlds in sorted(code_groups.items()):
        left = worlds[0]
        right = next((world for world in worlds if truth[world] != truth[left]), None)
        if right is not None:
            position = next(i for i, labels in enumerate(zip(truth[left], truth[right])) if labels[0] != labels[1])
            collisions.append({"code": code, "worlds": (left, right),
                               "mask": CONTEXTS[context]["queries"][position],
                               "answers": (truth[left][position], truth[right][position])})
    excess = []
    for answers, worlds in sorted(truth_groups.items()):
        codes = sorted({_execute(world, gates, taps) for world in worlds})
        if len(codes) > 1:
            excess.append({"answers": answers, "codes": codes, "worlds": worlds})
    return {"coarsest_class_count": len(truth_groups), "code_class_count": len(code_groups),
            "coarsest_classes": [{"answers": key, "worlds": value} for key, value in sorted(truth_groups.items())],
            "code_classes": [{"code": key, "worlds": value} for key, value in sorted(code_groups.items())],
            "collisions": collisions, "excess": excess,
            "exact_sufficient": not collisions,
            "coarsest_exact": not collisions and not excess}


def interventions(context: int | str, gates: Sequence[Sequence], taps: Sequence[int],
                  decoder: Mapping | None = None) -> dict:
    """Flip each raw input separately while holding the other five fixed."""
    context = _context(context)
    gates, taps = validate_program(gates, taps)
    codes = {world: _execute(world, gates, taps) for world in ALL_WORLDS}
    decoder = validate_decoder(context, len(taps),
                               _fit_codes(context, codes, EVEN_WORLDS) if decoder is None else decoder)
    rows = []
    for index, name in enumerate(INPUT_NAMES):
        code_changes = answer_changes = truth_changes = 0
        first = None
        for world in ALL_WORLDS:
            if (world >> index) & 1:
                continue
            other = world ^ (1 << index)
            code_changed = codes[world] != codes[other]
            answer_changed = any(decode(codes[world], mask, decoder) != decode(codes[other], mask, decoder)
                                 for mask in CONTEXTS[context]["queries"])
            truth_changed = any(oracle(world, context, mask) != oracle(other, context, mask)
                                for mask in CONTEXTS[context]["queries"])
            code_changes += code_changed
            answer_changes += answer_changed
            truth_changes += truth_changed
            if (code_changed or answer_changed) and first is None:
                first = (world, other)
        rows.append({"input": name, "pairs": 32, "code_changes": code_changes,
                     "answer_changes": answer_changes, "truth_changes": truth_changes,
                     "first_changed_pair": first})
    return {"rows": rows,
            "code_support": [row["input"] for row in rows if row["code_changes"]],
            "answer_support": [row["input"] for row in rows if row["answer_changes"]],
            "truth_support": [row["input"] for row in rows if row["truth_changes"]]}


def unrestricted_code_bound(contexts: Iterable[int | str], width: int = 1,
                            *, query: int | None = None) -> dict:
    """Exact capacity bound allowing *every* encoder on the 64 worlds.

    Fix decoder answer vectors first.  Every world may independently choose
    whichever code has the highest weighted correctness.  Thus the search
    includes encoders depending on all six bits and splitting identical
    answer classes.  Such splitting cannot beat the best code for that world.
    Enumerating all subsets of decoder vectors is therefore exact.  This is
    a bound for unrestricted encoders, not synthesis in the three-gate grammar.

    Without a fixed query, each context has equal weight and each of its
    offered queries has equal conditional weight.  A fixed query retains only
    contexts offering that query and weights those contexts equally.
    """
    contexts = tuple(_context(context) for context in contexts)
    if not contexts or len(set(contexts)) != len(contexts):
        raise ValueError("supply a nonempty set of distinct contexts")
    if type(width) is not int or not 0 <= width <= 3:
        raise ValueError("bound supports zero through three code bits")
    if query is not None:
        if type(query) is not int or query not in (1, 2, 3):
            raise ValueError("query must be 1, 2, or 3")
        contexts = tuple(context for context in contexts if query in CONTEXTS[context]["queries"])
        if not contexts:
            raise ValueError("none of these contexts offers the query")
    masks = tuple(sorted({query} if query is not None else
                         {mask for context in contexts for mask in CONTEXTS[context]["queries"]}))
    positions = {mask: index for index, mask in enumerate(masks)}
    weighted = []
    for context in contexts:
        offered = (query,) if query is not None else CONTEXTS[context]["queries"]
        weight = 1 if query is not None else 3 // len(offered)
        weighted.extend((context, mask, weight) for mask in offered)
    vectors = tuple(range(1 << len(masks)))
    utilities = [
        [sum(weight for context, mask, weight in weighted
             if ((vector >> positions[mask]) & 1) == oracle(world, context, mask))
         for vector in vectors]
        for world in ALL_WORLDS
    ]
    best = -1
    best_vectors = ()
    for count in range(1, min(1 << width, len(vectors)) + 1):
        for selected in combinations(vectors, count):
            score = sum(max(utility[vector] for vector in selected) for utility in utilities)
            if score > best:
                best, best_vectors = score, selected
    total = len(ALL_WORLDS) * sum(weight for _, _, weight in weighted)
    fraction = Fraction(best, total)
    return {"contexts": contexts, "width": width, "query": query, "masks": masks,
            "correct": best, "total": total, "accuracy": float(fraction),
            "fraction": (fraction.numerator, fraction.denominator),
            "decoder_vectors": [tuple((vector >> index) & 1 for index in range(len(masks)))
                                for vector in best_vectors],
            "scope": "all deterministic encoders on all 64 worlds; common decoder across listed contexts"}


def one_bit_bound(context: int | str) -> dict:
    return unrestricted_code_bound((_context(context),), 1)


def fixed_pair_control(context: int | str, pair: tuple[int, int] = (0, 1),
                       *, raw: bool = False) -> dict:
    """Optimal full-world decoder of a fixed pair's column, or its raw bits.

    ``raw=True`` grants all four raw bits of that pair, a generous information
    control.  Otherwise the two emitted bits are its branch intersections.
    Full-world decoder fitting makes this an analytic upper control, not a
    trained or held-out comparison.
    """
    context = _context(context)
    if len(pair) != 2 or len(set(pair)) != 2 or any(type(item) is not int or item not in (0, 1, 2) for item in pair):
        raise ValueError("pair must contain two distinct rule indices")
    codes = {}
    for world in ALL_WORLDS:
        if raw:
            code = tuple((world >> (2 * rule + h)) & 1 for rule in pair for h in (0, 1))
        else:
            code = tuple(((world >> (2 * pair[0] + h)) & 1) & ((world >> (2 * pair[1] + h)) & 1)
                         for h in (0, 1))
        codes[world] = code
    decoder = _fit_codes(context, codes, ALL_WORLDS)
    return {"context": context, "fixed_pair": pair, "raw_pair_bits": raw,
            **_score(context, codes, decoder, ALL_WORLDS)}


def cue_free_bound(width: int = 2, *, query: int | None = None) -> dict:
    return unrestricted_code_bound(CONTEXTS, width, query=query)


def assess_cue_free(gates: Sequence[Sequence], taps: Sequence[int],
                    decoder: Mapping | None = None) -> dict:
    """One context-free program and one common code/query decoder.

    Conditional labels are weighted so every context contributes equally,
    including contexts offering different numbers of delayed queries.
    """
    gates, taps = validate_program(gates, taps)
    codes = {world: _execute(world, gates, taps) for world in ALL_WORLDS}
    if decoder is None:
        counts = defaultdict(lambda: [0, 0])
        for context, specification in CONTEXTS.items():
            weight = 3 // len(specification["queries"])
            for world in EVEN_WORLDS:
                for mask in specification["queries"]:
                    counts[(codes[world], mask)][oracle(world, context, mask)] += weight
        decoder = {key: int(labels[1] > labels[0]) for key, labels in counts.items()}
    # A selective context admits the complete common mask interface.
    decoder = validate_decoder(0, len(taps), decoder)
    per_context = {context: assess(context, gates, taps,
                                  {key: label for key, label in decoder.items()
                                   if key[1] in CONTEXTS[context]["queries"]})
                   for context in CONTEXTS}
    return {"per_context": per_context,
            **{split: {"accuracy": sum(row[split]["accuracy"] for row in per_context.values()) / 6,
                       "exact": all(row[split]["exact"] for row in per_context.values())}
               for split in ("train", "heldout", "all")}}


def cue_free_witness() -> dict:
    """Same source and delayed query, incompatible answers without context."""
    world = 60  # A=00, B=11, C=11.
    return {"world": world, "bits": raw_bits(world), "mask": 3,
            "contexts": (1, 3), "answers": (oracle(world, 1, 3), oracle(world, 3, 3))}


def composition_check(context: int | str, gates: Sequence[Sequence], taps: Sequence[int],
                      decoder: Mapping | None = None) -> dict:
    """Externally join decoded branch answers with every pair of new rules.

    New rules range independently over all four subsets of h.  The expected
    answer is re-derived from the original raw rules by enumerating h.  This
    is a finite reuse test; the arrangement is external and no policy is run.
    """
    context = _context(context)
    if CONTEXTS[context]["kind"] != "selective":
        raise ValueError("composition requires both offered membership queries")
    gates, taps = validate_program(gates, taps)
    codes = {world: _execute(world, gates, taps) for world in ALL_WORLDS}
    decoder = validate_decoder(context, len(taps),
                               _fit_codes(context, codes, EVEN_WORLDS) if decoder is None else decoder)
    left, right = CONTEXTS[context]["pair"]
    failures = total = 0
    first_failure = None
    for world in ALL_WORLDS:
        branches = tuple(decode(codes[world], 1 << h, decoder) for h in (0, 1))
        for new_left, new_right, mask in product(range(4), range(4), (1, 2, 3)):
            actual = int(any(branches[h] and (new_left & (1 << h)) and (new_right & (1 << h))
                             and (mask & (1 << h)) for h in (0, 1)))
            expected = int(any(((world >> (2 * left + h)) & 1)
                               and ((world >> (2 * right + h)) & 1)
                               and (new_left & (1 << h)) and (new_right & (1 << h))
                               and (mask & (1 << h)) for h in (0, 1)))
            total += 1
            if actual != expected:
                failures += 1
                if first_failure is None:
                    first_failure = {"world": world, "new_rules": (new_left, new_right),
                                     "mask": mask, "expected": expected, "actual": actual}
    irrelevant = next(rule for rule in range(3) if rule not in (left, right))
    code_changes = answer_changes = composed_changes = 0
    for world in ALL_WORLDS:
        for disturbance in (1, 2, 3):
            other = world ^ (disturbance << (2 * irrelevant))
            code_changes += codes[world] != codes[other]
            answer_changes += any(decode(codes[world], mask, decoder) != decode(codes[other], mask, decoder)
                                  for mask in (1, 2, 3))
            assert all(oracle(world, context, mask) == oracle(other, context, mask) for mask in (1, 2, 3))
            before = tuple(decode(codes[world], 1 << h, decoder) for h in (0, 1))
            after = tuple(decode(codes[other], 1 << h, decoder) for h in (0, 1))
            for new_left, new_right, mask in product(range(4), range(4), (1, 2, 3)):
                def composed(branches):
                    return any(branches[h] and (new_left & (1 << h)) and (new_right & (1 << h))
                               and (mask & (1 << h)) for h in (0, 1))
                composed_changes += composed(before) != composed(after)
    return {"cases": total, "failures": failures, "exact": failures == 0,
            "first_failure": first_failure, "new_rule_count": 2,
            "disturbance_cases": 192, "irrelevant_rule": irrelevant,
            "disturbance_code_changes": code_changes,
            "disturbance_answer_changes": answer_changes,
            "disturbance_composed_cases": 9216,
            "disturbance_composed_answer_changes": composed_changes}


def hand_program(context: int | str, width: int | None = None) -> tuple[tuple[Gate, ...], Code]:
    """An explicitly supplied attainable reference, never a learned program."""
    context = _context(context)
    left, right = CONTEXTS[context]["pair"]
    gates = (("AND", 2 * left, 2 * right), ("AND", 2 * left + 1, 2 * right + 1), ("OR", 6, 7))
    if width is None:
        width = 2 if CONTEXTS[context]["kind"] == "selective" else 1
    if width not in (1, 2):
        raise ValueError("reference width must be one or two")
    return gates, (8,) if width == 1 else (6, 7)


def self_check() -> dict:
    """Small positive, negative, split, isolation, and analytic controls."""
    assert len(EVEN_WORLDS) == len(ODD_WORLDS) == 32
    assert set(EVEN_WORLDS).isdisjoint(ODD_WORLDS)
    generic = (("XOR", 0, 1), ("NAND", 2, 3), ("AND", 6, 7))
    for world in ALL_WORLDS:
        a0, a1, b0, b1, _, _ = raw_bits(world)
        assert execute(world, generic, (8,)) == ((a0 ^ a1) & (1 - (b0 & b1)),)
    assert live_gates(generic, (0,)) == ()
    summaries = []
    for context in CONTEXTS:
        pair = CONTEXTS[context]["pair"]
        for worlds in (EVEN_WORLDS, ODD_WORLDS):
            assert len({tuple((world >> (2 * rule + h)) & 1 for rule in pair for h in (0, 1))
                        for world in worlds}) == 16
        gates, taps = hand_program(context)
        assessment = assess(context, gates, taps)
        assert assessment["train"]["exact"] and assessment["heldout"]["exact"]
        bad_decoder = fit_decoder(context, gates, taps)
        key = next(iter(bad_decoder))
        bad_decoder[key] ^= 1
        assert not assess(context, gates, taps, bad_decoder)["all"]["exact"]
        q = quotient(context, gates, taps)
        assert q["coarsest_class_count"] == (4 if CONTEXTS[context]["kind"] == "selective" else 2)
        assert q["coarsest_exact"]
        changed = (("OR", gates[0][1], gates[0][2]), *gates[1:])
        assert not assess(context, changed, taps)["all"]["exact"]
        assert fixed_pair_control(context, pair)["exact"]
        wrong_pair = next(candidate for candidate in combinations(range(3), 2) if candidate != pair)
        assert not fixed_pair_control(context, wrong_pair)["exact"]
        bound = one_bit_bound(context)
        assert bound["fraction"] == ((7, 8) if CONTEXTS[context]["kind"] == "selective" else (1, 1))
        support = interventions(context, gates, taps)
        expected_support = [INPUT_NAMES[index] for index in range(6) if index // 2 in pair]
        assert support["code_support"] == support["answer_support"] == expected_support
        if CONTEXTS[context]["kind"] == "selective":
            composed = composition_check(context, gates, taps)
            assert composed["exact"] and composed["disturbance_code_changes"] == composed["disturbance_answer_changes"] == 0
            assert composed["disturbance_composed_answer_changes"] == 0
            one_gates, one_taps = hand_program(context, 1)
            assert assess(context, one_gates, one_taps)["all"]["accuracy"] == 7 / 8
            assert quotient(context, one_gates, one_taps)["collisions"]
            assert not composition_check(context, one_gates, one_taps)["exact"]
        else:
            extra_gates, extra_taps = hand_program(context, 2)
            assert assess(context, extra_gates, extra_taps)["all"]["exact"]
            assert quotient(context, extra_gates, extra_taps)["excess"]
        summaries.append({"context": context, "hand_exact": True,
                          "corrupt_rejected": True, "one_bit_fraction": bound["fraction"]})
    witness = cue_free_witness()
    assert witness["answers"] == (0, 1)
    # An absent lookup cell is zero; no world or register argument is accepted.
    assert decode((1,), 3, {}) == 0
    try:
        validate_decoder(1, 1, {(60, (1,), 3): 1})
    except ValueError:
        pass
    else:
        raise AssertionError("decoder accepted a world-bearing key")
    for gates, taps in [((("AND", 0, 6), ("OR", 0, 1), ("XOR", 0, 1)), (8,)),
                         ((("BAD", 0, 1), ("OR", 0, 1), ("XOR", 0, 1)), (8,))]:
        try:
            validate_program(gates, taps)
        except ValueError:
            pass
        else:
            raise AssertionError("malformed gate was accepted")
    hidden = {str(mask): cue_free_bound(1, query=mask) for mask in (1, 2, 3)}
    assert all(result["accuracy"] < 1 for result in hidden.values())
    gates, taps = hand_program(0)
    assert not assess_cue_free(gates, taps)["all"]["exact"]
    return {"pass": True, "worlds": 64, "split_sizes": (32, 32), "contexts": summaries,
            "cue_free_witness": witness, "cue_free_single_query_bounds": hidden,
            "cue_free_one_bit": cue_free_bound(1), "cue_free_two_bits": cue_free_bound(2)}


if __name__ == "__main__":
    print(json.dumps(self_check(), indent=2))
