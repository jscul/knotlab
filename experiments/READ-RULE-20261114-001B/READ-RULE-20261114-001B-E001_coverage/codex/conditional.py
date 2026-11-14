"""READ-RULE task 3: exact conditional rectangularity through length eight.

The state is (Boolean product, identity carry map), never the product alone.
All I/O, population selection, weights, and CARRY verdicts belong to the caller.
This module writes no files and does not run a census when imported.
"""
from __future__ import annotations

from functools import lru_cache
import importlib.util
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CARRY = ROOT / "experiments/CARRY-BOUND-20261114-001A/CARRY-BOUND-20261114-001A-E001_window/codex"
NO_START = -1
MAX_R = 8
MAX_STORED_PRODUCTS = 250_000
MAX_LEVELS = 100_000


@lru_cache(maxsize=1)
def _relations():
    """Use the authorized CARRY input loader, not a second relation producer."""
    name = "read_rule_conditional_carry_inputs"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, CARRY / "inputs.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name].load_relations()


def carry_map(arguments):
    """End position j holds start position result[j], or no start identity.

    Repeated arguments are retained: (0, 0, -1) carries one start position
    to two end positions. Equality forced by a relation is never identity.
    """
    arguments = tuple(arguments)
    if len(arguments) != 3 or any(type(a) is not int or a < 0 for a in arguments):
        raise ValueError("a SELF call must have three nonnegative integer arguments")
    return tuple(a if a < 3 else NO_START for a in arguments)


def compose_carry(left, right):
    """Identity transport for left then right, in the relation product order."""
    return tuple(left[a] if a != NO_START else NO_START for a in right)


def carry_record(carried):
    return dict(end_to_start=list(carried),
                start_to_end=[[j for j, a in enumerate(carried) if a == i]
                              for i in range(3)])


@lru_cache(maxsize=64)
def slice_masks(carried):
    """All assignments of distinct carried start positions, equal at the end.

    Fixed positions remain in the 8-by-8 table. This only inserts zero rows
    and columns, so the authorized rectangular() tests the same product
    relation as deleting those fixed positions would. Empty slices count as
    rectangular, exactly as in the authorized rectangular().
    """
    sources = tuple(sorted(set(carried) - {NO_START}))
    masks = []
    for values in range(1 << len(sources)):
        assignment = tuple((source, (values >> j) & 1)
                           for j, source in enumerate(sources))
        fixed = dict(assignment)
        left_states = [a for a in range(8)
                       if all(((a >> source) & 1) == value
                              for source, value in assignment)]
        right_states = [b for b in range(8)
                        if all(source == NO_START or ((b >> j) & 1) == fixed[source]
                               for j, source in enumerate(carried))]
        mask = sum(1 << (8 * a + b) for a in left_states for b in right_states)
        masks.append((assignment, mask))
    return tuple(masks)


def check_product(relation, carried, checkpoint=lambda: None):
    """Test every carried-value assignment; retain the first failed slice."""
    rectangular = _relations().rectangular
    failures = 0
    empty = 0
    first_failure = None
    masks = slice_masks(carried)
    for assignment, mask in masks:
        sliced = relation & mask
        empty += sliced == 0
        if not rectangular(sliced):
            failures += 1
            if first_failure is None:
                first_failure = dict(assignment=[list(pair) for pair in assignment],
                                     slice=f"0x{sliced:016x}")
        checkpoint()
    return dict(conditionally_rectangular=failures == 0,
                slice_tests=len(masks), nonrectangular_slices=failures,
                empty_slices=empty, first_failure=first_failure)


def conditional_from_calls(calls, checkpoint=lambda: None, *, max_r=MAX_R,
                           max_stored_products=MAX_STORED_PRODUCTS,
                           max_levels=MAX_LEVELS):
    """Complete product/carry length sets, using the semigroup's numeric caps.

    ``calls`` contains {relation: int, arguments: [int, int, int]}. The caller
    may use CARRY's frozen R_i plus SyntaxPreparation, avoiding allowed-state
    recomputation. Products use the authorized compose() and rectangular().

    The 250,000 operational storage bound counts relation/carry pairs. The
    cumulative count of distinct Boolean products per stored length is also
    returned. A cap gives no verdict, even when an earlier accepted length
    occurs in the retained partial trace, matching semigroup's cap behavior.
    Conditional success is never assumed to persist at later lengths.
    """
    if type(max_r) is not int or not 1 <= max_r <= MAX_R:
        raise ValueError("the preregistered horizon must be in 1..8")
    if type(max_stored_products) is not int or max_stored_products < 1:
        raise ValueError("max_stored_products must be a positive integer")
    if type(max_levels) is not int or max_levels < 1:
        raise ValueError("max_levels must be a positive integer")
    relations = _relations()
    calls = tuple(calls)
    generators = {}
    source_calls = []
    for letter, call in enumerate(calls):
        relation = call["relation"]
        if type(relation) is not int or not 0 <= relation < (1 << 64):
            raise ValueError("a SELF relation must be an unsigned 64-bit integer")
        carried = carry_map(call["arguments"])
        pair = relation, carried
        generators.setdefault(pair, letter)
        source_calls.append(dict(letter=letter, relation=f"0x{relation:016x}",
                                 arguments=list(call["arguments"]),
                                 **carry_record(carried)))
    if not calls:
        raise ValueError("no SELF generators")

    current = {pair: (letter,) for pair, letter in generators.items()}
    seen = {}
    trace = []
    checks = {}
    stored = 0
    stored_boolean = 0
    actual_slice_tests = 0
    composition_attempts = 0
    least_r = None
    repeat_start = None
    period = None
    constructing = None
    partial_level = None

    def finish(cap=None, cap_reason=None):
        complete = cap is None and len(trace) == max_r
        decided_r = least_r if complete else None
        verdict = ("capped" if not complete else "conditionally_rectangular"
                   if decided_r is not None else f"none_through_{max_r}")
        return dict(complete=complete, certified=complete and decided_r is not None,
                    verdict=verdict, r=decided_r, least_r=decided_r,
                    least_r_in_partial_trace=least_r if not complete else None,
                    max_r=max_r, cap=cap, cap_reason=cap_reason,
                    cap_basis="relation_carry_pairs", generators=source_calls,
                    distinct_generators=len(generators),
                    length_set_sizes=[row["products"] for row in trace],
                    boolean_length_set_sizes=[row["boolean_products"] for row in trace],
                    all_conditionally_rectangular_by_length=[
                        row["all_conditionally_rectangular"] for row in trace],
                    trace=trace, repeat_start=repeat_start, period=period,
                    stored_products=stored, stored_boolean_products=stored_boolean,
                    unique_pairs_checked=len(checks), actual_slice_tests=actual_slice_tests,
                    composition_attempts=composition_attempts,
                    partial_level=partial_level, partial_construction=constructing,
                    limits=dict(max_stored_products=max_stored_products,
                                max_levels=max_levels, max_r=max_r))

    try:
        while len(trace) < max_r:
            r = len(trace) + 1
            level = frozenset(current)
            if level in seen:
                repeat_start = seen[level]
                period = r - repeat_start
                # Exact recurrence of the complete pair sets determines every
                # remaining length. No persistence-of-success claim is used.
                for repeated_r in range(r, max_r + 1):
                    source_r = repeat_start + (repeated_r - repeat_start) % period
                    source = trace[source_r - 1]
                    row = dict(source, r=repeated_r, words=len(calls) ** repeated_r,
                               derived_from_r=source_r)
                    if source["first_failure"] is not None:
                        row["first_failure"] = dict(source["first_failure"],
                                                    representative_word_at_r=source_r)
                    trace.append(row)
                    if row["all_conditionally_rectangular"] and least_r is None:
                        least_r = repeated_r
                break
            if r > max_levels:
                return finish(f"P_n length-set cap {max_levels}", "cap")
            if stored + len(current) > max_stored_products:
                partial_level = dict(r=r, products=len(current), tested=0,
                                     boolean_products=len({pair[0] for pair in current}))
                return finish(f"stored P_n product/carry cap {max_stored_products}", "cap")
            stored += len(current)
            boolean_products = len({pair[0] for pair in current})
            stored_boolean += boolean_products
            seen[level] = r
            good = failures = slices = empty = 0
            first_failure = None
            partial_level = dict(r=r, products=len(current), tested=0,
                                 boolean_products=boolean_products)
            for pair in sorted(current):
                relation, carried = pair
                if pair not in checks:
                    item = check_product(relation, carried, checkpoint)
                    actual_slice_tests += item["slice_tests"]
                    checks[pair] = item
                item = checks[pair]
                good += item["conditionally_rectangular"]
                failures += item["nonrectangular_slices"]
                slices += item["slice_tests"]
                empty += item["empty_slices"]
                partial_level["tested"] += 1
                if first_failure is None and not item["conditionally_rectangular"]:
                    first_failure = dict(relation=f"0x{relation:016x}",
                                         word=list(current[pair]),
                                         **carry_record(carried), **item["first_failure"])
                checkpoint()
            row = dict(r=r, products=len(current), boolean_products=boolean_products,
                       carry_maps=len({pair[1] for pair in current}), words=len(calls) ** r,
                       conditionally_rectangular_products=good,
                       non_conditionally_rectangular_products=len(current) - good,
                       all_conditionally_rectangular=good == len(current),
                       slice_tests=slices, nonrectangular_slices=failures,
                       empty_slices=empty, first_failure=first_failure,
                       derived_from_r=None)
            trace.append(row)
            partial_level = None
            if row["all_conditionally_rectangular"] and least_r is None:
                least_r = r
            if r == max_r:
                break
            nxt = {}
            next_boolean = set()
            constructing = dict(r=r + 1, products=0, boolean_products=0)
            for (relation, carried), word in sorted(current.items()):
                for (generator, generator_carry), letter in sorted(generators.items()):
                    pair = (relations.compose(relation, generator),
                            compose_carry(carried, generator_carry))
                    composition_attempts += 1
                    extended_word = word + (letter,)
                    if pair not in nxt or extended_word < nxt[pair]:
                        nxt[pair] = extended_word
                    next_boolean.add(pair[0])
                    constructing.update(products=len(nxt), boolean_products=len(next_boolean))
                    if stored + len(nxt) > max_stored_products:
                        return finish(f"P_n construction product/carry cap {max_stored_products}",
                                      "cap")
                    checkpoint()
            current = nxt
            constructing = None
    except relations.LimitReached as exc:
        return finish(str(exc), exc.reason)
    except MemoryError:
        return finish("Python MemoryError", "memory")
    return finish()


def conditional(prep, calls=None, checkpoint=lambda: None, **limits):
    """Preparation-based convenience API; cached calls avoid recomputation."""
    if calls is None:
        calls = _relations().per_call(prep, checkpoint)
    return conditional_from_calls(calls, checkpoint, **limits)


def controls():
    """Cheap hand-specified controls, executed only when explicitly called."""
    full = (1 << 64) - 1
    identity = sum(1 << (8 * a + a) for a in range(8))
    call = lambda relation, arguments: dict(relation=relation, arguments=arguments)
    answers = {}
    answers["free_no_carry"] = conditional_from_calls([call(full, [3, 4, 5])])
    assert answers["free_no_carry"]["r"] == 1
    answers["identity_all_carried"] = conditional_from_calls([call(identity, [0, 1, 2])])
    assert answers["identity_all_carried"]["r"] == 1
    answers["identity_no_carry"] = conditional_from_calls([call(identity, [3, 4, 5])])
    assert answers["identity_no_carry"]["verdict"] == "none_through_8"
    answers["same_relation_different_carries"] = conditional_from_calls(
        [call(identity, [0, 1, 2]), call(identity, [3, 4, 5])])
    first = answers["same_relation_different_carries"]["trace"][0]
    assert first["products"] == 2 and first["boolean_products"] == 1
    assert first["conditionally_rectangular_products"] == 1
    assert answers["same_relation_different_carries"]["r"] is None
    doubled = sum(1 << (8 * a + b) for a in range(8) for b in range(8)
                  if (b & 1) == (a & 1) and ((b >> 1) & 1) == (a & 1))
    answers["one_start_two_ends"] = conditional_from_calls([call(doubled, [0, 0, 3])])
    assert answers["one_start_two_ends"]["r"] == 1
    assert answers["one_start_two_ends"]["trace"][0]["slice_tests"] == 2
    assert compose_carry((1, -1, -1), (-1, 0, -1)) == (-1, 1, -1)
    # One relation with two unequal nonzero rows; its square is one allowed
    # pair, and its cube is empty. Thus the first successful length is two.
    chain = (1 << 1) | (1 << 10)
    answers["first_success_at_two"] = conditional_from_calls([call(chain, [3, 4, 5])])
    assert answers["first_success_at_two"]["r"] == 2
    answers["storage_cap_is_undecided"] = conditional_from_calls(
        [call(full, [3, 4, 5])], max_stored_products=1)
    assert answers["storage_cap_is_undecided"]["verdict"] == "capped"
    assert answers["storage_cap_is_undecided"]["r"] is None
    assert answers["storage_cap_is_undecided"]["least_r_in_partial_trace"] == 1
    return dict(passed=True, controls=answers)


if __name__ == "__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--controls", action="store_true", required=True)
    parser.parse_args()
    print(json.dumps(controls(), sort_keys=True, allow_nan=False))
