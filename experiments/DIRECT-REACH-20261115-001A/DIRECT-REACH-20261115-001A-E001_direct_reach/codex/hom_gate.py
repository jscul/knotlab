"""Independent, deterministic controls for finite address-map checking.

The reference implementation below uses ordinary Python bit tuples.  It does
not call the producer's word action, pattern builder, candidate builder, or
map builder.  The gate writes no files and starts no subprocesses.
"""

from itertools import product
import random

import homomorphisms


SEED = 2026111503
RANDOM_DESCRIPTION_COUNT = 20


def _reference_words(s):
    result = [()]
    for length in (1, 2):
        result.extend(product(range(s), repeat=length))
    return result


def _state_bits(key, state, bits):
    """Read input bits left to right, choosing the section by input bit."""
    _s, swaps, zero, one, _placements = key
    output = []
    for bit in bits:
        output.append(bit ^ swaps[state])
        state = (zero if bit == 0 else one)[state]
    return tuple(output)


def _word_bits(key, word, bits):
    result = bits
    for position in range(len(word) - 1, -1, -1):
        result = _state_bits(key, word[position], result)
    return result


def _vertex(bits):
    """Heap numbering computed by one child step per bit."""
    vertex = 0
    for bit in bits:
        vertex = 2 * vertex + 1 + bit
    return vertex


def _bits(vertex):
    return tuple(int(bit) for bit in bin(vertex + 1)[3:])


def _reference_pattern(key, depth):
    words = _reference_words(key[0])
    placements = {tuple(sorted(row)) for row in key[4]}
    terms = {term for row in placements for term in row}
    knots = set()
    for n in range(depth + 1):
        for bits in product((0, 1), repeat=n):
            images = {}
            for term in terms:
                word_number, slot = divmod(term, 3)
                if slot != 0 and n == depth:
                    continue
                image = _word_bits(key, words[word_number], bits)
                if slot != 0:
                    image += (slot - 1,)
                images[term] = _vertex(image)
            for row in placements:
                if all(term in images for term in row):
                    image = tuple(sorted(images[term] for term in row))
                    if len(set(image)) == 3:
                        knots.add(image)
    return knots


def _reference_candidates(s):
    return [(family, c, word)
            for family in ("prefix", "suffix")
            for c in (0, 1) for word in _reference_words(s)]


def _reference_table(key, descriptor, source_depth):
    family, c, word = descriptor
    result = []
    for vertex in range((1 << (source_depth + 1)) - 1):
        image = _word_bits(key, word, _bits(vertex))
        if family == "prefix":
            image = (c,) + image
        else:
            image += (c,)
        result.append(_vertex(image))
    return result


def _descriptor(record):
    return record["family"], record["c"], tuple(record["word"])


def _reference_verdict(source, target, table, target_vertex_count):
    for row in sorted(source):
        image = tuple(sorted(table[v] for v in row))
        if (len(set(image)) != 3 or any(v < 0 or v >= target_vertex_count for v in image)
                or image not in target):
            return False
    return True


def _random_descriptions():
    rng = random.Random(SEED)
    result = []
    for case_index in range(RANDOM_DESCRIPTION_COUNT):
        s = 1 + case_index % 3
        swaps = tuple(rng.randrange(2) for _ in range(s))
        zero = tuple(rng.randrange(s) for _ in range(s))
        one = tuple(rng.randrange(s) for _ in range(s))
        # Every case has a nonempty pattern.  One quarter retain only this
        # placement; the others add independently sampled addressed triples.
        placements = {(0, 1, 2)}
        term_count = 3 * (1 + s + s * s)
        for _ in range(case_index % 4):
            placements.add(tuple(sorted(rng.sample(range(term_count), 3))))
        result.append((s, swaps, zero, one, tuple(sorted(placements))))
    return result


def _control_cases():
    positive = homomorphisms.check_map([(0, 1, 2)], [(1, 3, 5)], [1, 3, 5], 7)
    missing = homomorphisms.check_map([(0, 1, 2)], [(1, 3, 5)], [1, 3, 4], 7)
    collapsed = homomorphisms.check_map([(0, 1, 2)], [(1, 3, 5)], [1, 1, 5], 7)
    outside = homomorphisms.check_map([(0, 1, 2)], [(1, 3, 5)], [1, 3, 7], 7)
    assert positive["accepted"] is True
    assert missing["accepted"] is False
    assert missing["witness"]["reason"] == "image_not_stored_knot"
    assert collapsed["accepted"] is False
    assert collapsed["witness"]["reason"] == "fewer_than_three_distinct_images"
    assert outside["accepted"] is False
    assert outside["witness"]["reason"] == "image_outside_target"

    identity = (1, (0,), (0,), (0,), ((0, 1, 2),))
    prefix = {"family": "prefix", "c": 1, "word": []}
    suffix = {"family": "suffix", "c": 1, "word": []}
    assert homomorphisms.map_vertices(identity, prefix, [0, 4]) == [2, 12]
    assert homomorphisms.map_vertices(identity, suffix, [0, 4]) == [2, 10]
    tree = homomorphisms.evaluate(identity, 2, 3)
    assert tree["accepted_count"] == 6
    assert tree["rejected_count"] == 6
    assert all(record["family"] == "prefix" for record in tree["accepted_maps"])
    assert all(record["family"] == "suffix" for record in tree["rejected_maps"])

    # State 0 swaps the first bit.  State 1 swaps the second bit only
    # after input 0.  On 00, products (0,1) -> 11 and (1,0) -> 10.
    noncommuting = (3, (1, 0, 0), (2, 0, 2), (2, 2, 2), ((0, 1, 2),))
    for word, expected in (((0, 1), 10), ((1, 0), 9)):
        spec = {"family": "prefix", "c": 0, "word": list(word)}
        assert homomorphisms.map_vertices(noncommuting, spec, [3]) == [expected]
        assert _reference_table(noncommuting, _descriptor(spec), 2)[3] == expected
    return {"explicit_positive": positive,
            "handmade_non_homomorphism": missing,
            "collapsed_image": collapsed,
            "outside_target": outside,
            "msb_prefix_suffix": True,
            "right_to_left_noncommuting_words": True,
            "tree_only": {"accepted_count": tree["accepted_count"],
                          "rejected_count": tree["rejected_count"]}}


def run_gate():
    """Return JSON-compatible gate evidence; assertion failures fail the gate."""
    controls = _control_cases()
    cases = []
    accepted_total = rejected_total = checked_accepted_knots = 0
    for case_index, key in enumerate(_random_descriptions()):
        result = homomorphisms.evaluate(key, 8, 9)
        source = _reference_pattern(key, 8)
        target = _reference_pattern(key, 9)
        stored_source = {tuple(int(v) for v in row)
                         for row in homomorphisms.pattern.pattern(key, 8)}
        stored_target = {tuple(int(v) for v in row)
                         for row in homomorphisms.pattern.pattern(key, 9)}
        assert source == stored_source
        assert target == stored_target
        assert source, f"random case {case_index} unexpectedly has no source knots"
        assert result["source_knot_count"] == len(source)
        assert result["target_knot_count"] == len(target)
        assert result["accepted_count"] == len(result["accepted_maps"])
        assert result["rejected_count"] == len(result["rejected_maps"])
        records = result["accepted_maps"] + result["rejected_maps"]
        by_descriptor = {_descriptor(record): record for record in records}
        expected_descriptors = _reference_candidates(key[0])
        assert len(records) == len(by_descriptor) == 4 * (1 + key[0] + key[0] ** 2)
        assert set(by_descriptor) == set(expected_descriptors)
        accepted = {_descriptor(record) for record in result["accepted_maps"]}
        reference_accepted = set()
        for descriptor in expected_descriptors:
            table = _reference_table(key, descriptor, 8)
            expected = _reference_verdict(source, target, table, (1 << 10) - 1)
            if expected:
                reference_accepted.add(descriptor)
            record = by_descriptor[descriptor]
            if descriptor in accepted:
                # Explicit knot-by-knot reference check of each accepted map.
                for row in sorted(source):
                    image = tuple(sorted(table[v] for v in row))
                    assert len(set(image)) == 3
                    assert image in target
                    checked_accepted_knots += 1
                assert record["checked_knots"] == len(source)
            else:
                row = tuple(record["source_knot"])
                assert row in source
                original_order = [table[v] for v in row]
                image = tuple(sorted(original_order))
                assert record["image_in_source_order"] == original_order
                assert record["image_knot"] == list(image)
                assert record["distinct_images"] == (len(set(image)) == 3)
                assert image not in target or len(set(image)) != 3
                assert record["reason"] == ("fewer_than_three_distinct_images"
                                            if len(set(image)) != 3
                                            else "image_not_stored_knot")
                assert record["source_knot_index"] == sorted(source).index(row)
                assert record["checked_knots"] == record["source_knot_index"] + 1
        assert accepted == reference_accepted, f"candidate decision mismatch in case {case_index}"
        accepted_total += len(accepted)
        rejected_total += result["rejected_count"]
        cases.append({"case_index": case_index,
                      "key": [key[0], list(key[1]), list(key[2]), list(key[3]),
                              [list(row) for row in key[4]]],
                      "source_knot_count": len(source), "target_knot_count": len(target),
                      "candidate_count": len(expected_descriptors),
                      "accepted_count": len(accepted),
                      "rejected_count": result["rejected_count"]})
    assert len(cases) == RANDOM_DESCRIPTION_COUNT
    assert accepted_total > 0 and rejected_total > 0
    assert checked_accepted_knots > 0
    return {"schema_version": 1, "gate": "G-hom", "passed": True,
            "seed": SEED, "random_description_count": len(cases),
            "source_depth": 8, "target_depth": 9,
            "reference": "independent plain Python bit-tuple state action, pattern, and map",
            "random_generation": "s cycles 1..3; seeded automata; tree placement plus 0..3 random triples",
            "candidate_decisions_compared": accepted_total + rejected_total,
            "accepted_maps_checked": accepted_total,
            "rejected_maps_checked": rejected_total,
            "accepted_knots_checked": checked_accepted_knots,
            "controls": controls, "cases": cases,
            "nonclaims": ["finite stored triples only", "no semantic contact claim"]}
