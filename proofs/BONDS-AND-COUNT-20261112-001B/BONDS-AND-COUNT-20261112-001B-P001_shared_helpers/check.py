"""Exact NAE encoding with a borrowed broadcast reference; local obstructions.

Run with the repository .venv Python.  --write-result records the replay.
The positive constructor and its polynomial reference use separate algorithms.
All bounded local obstructions retain directly checked SAT countermodels.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools as it
import json
from pathlib import Path

import numpy as np
from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ENUM = ROOT / "research/CHEAP-COUNT-20261112-001/referee-R1/codex/s1_enumeration.json"
CENSUS = ROOT / "experiments/CHEAP-COUNT-20261112-001A/CHEAP-COUNT-20261112-001A-E001_cheapest_counter/census.py"
Q9 = ((0, 1, 2), (0, 1, 6), (0, 2, 4), (0, 3, 4),
      (0, 3, 5), (0, 5, 6), (2, 3, 6), (2, 4, 6), (3, 4, 5))


def holds(state, triples):
    return all(not (state[a] == state[b] == state[c]) for a, b, c in triples)


def encoded_pair(a, b, ref=0):
    """Three raw distinctions, with helper meanings relative to ref."""
    x, y = a ^ ref, b ^ ref
    return b, ref ^ int(not (x or y)), ref ^ int(not (x and y))


def invariant(p, x, h, k, ref, opposite):
    return [(p, x, h), (p, x, k), (p, h, k),
            (x, h, opposite), (x, k, ref)]


def bulk(b, c, f, g, v, w, h, k, ref, opposite):
    return invariant(v, w, h, k, ref, opposite) + [
        (b, f, w), (c, f, w), (f, w, opposite),
        (g, v, h), (g, k, ref)]


def right_end(b, v, w, h, k, ref, opposite):
    return invariant(v, w, h, k, ref, opposite) + invariant(v, b, h, k, ref, opposite)


def clauses(triples):
    return [clause for triple in sorted(set(map(tuple, triples)))
            for clause in ([x + 1 for x in triple], [-x - 1 for x in triple])]


def build(depth, width=3, close=True):
    assert depth >= 0 and width >= 2
    rows, nv = [], 0
    for generation in range(depth + 1):
        row = [tuple(range(nv + 3 * j, nv + 3 * j + 3))
               for j in range(width + generation)]
        rows.append(row)
        nv += 3 * len(row)
    ref = nv
    nv += 1
    opposite = rows[0][0][2]  # An already charged initial helper, now broadcast.
    triples = set()

    def add(batch):
        for triple in batch:
            assert len(set(triple)) == 3, (depth, width, triple)
            triples.add(tuple(sorted(triple)))

    # a,h0,S,b,h1,k1,R: exact initial relation on the first two positions.
    names = rows[0][0] + rows[0][1] + (ref,)
    add(tuple(names[j] for j in q) for q in Q9)
    for j in range(2, width):
        add(invariant(rows[0][j - 1][0], *rows[0][j], ref, opposite))
    for old, new in zip(rows, rows[1:]):
        for j in range(len(old)):
            b = old[j - 1][0] if j else ref
            c, f, g = old[j]
            v = new[j - 1][0] if j else ref
            add(bulk(b, c, f, g, v, *new[j], ref, opposite))
        add(right_end(old[-1][0], new[-2][0], *new[-1], ref, opposite))
    if close:
        add((rows[-1][j][0], rows[-1][j + 1][0], rows[-1][j + 2][0])
            for j in range(len(rows[-1]) - 2))
    assert {x for t in triples for x in t} == set(range(nv))
    return rows, ref, opposite, sorted(triples), nv


def update(xs, ref=0):
    return [(xs[j - 1] if j else ref) ^ (xs[j] if j < len(xs) else ref) ^ ref
            for j in range(len(xs) + 1)]


def canonical_state(rows, ref_id, seed, ref):
    values = [None] * (ref_id + 1)
    values[ref_id] = ref
    xs = list(seed)
    for row in rows:
        for j, ids in enumerate(row):
            triple = encoded_pair(xs[j - 1] if j else ref, xs[j], ref)
            for var, value in zip(ids, triple):
                values[var] = value
        xs = update(xs, ref)
    assert None not in values
    return values


def local_tables():
    # A separately allocated complementary reference costs S plus 3 witnesses.
    # This optional alternative still has two broadcast references.
    ref_gadget = ((0, 1, 2), (0, 1, 3), (0, 1, 4), (2, 3, 4))
    ref_projection = {s[:2] for s in it.product((0, 1), repeat=5)
                      if holds(s, ref_gadget)}
    assert ref_projection == {(0, 1), (1, 0)}
    seed_allowed = []
    for s in it.product((0, 1), repeat=7):
        a, h0, opposite, b, h1, k1, ref = s
        target = (opposite != ref and (a, h0, opposite) == encoded_pair(ref, a, ref)
                  and (b, h1, k1) == encoded_pair(a, b, ref))
        assert holds(s, Q9) == target, s
        if target:
            seed_allowed.append("".join(map(str, s)))
    assert len(seed_allowed) == 8

    inv_checks = transition_checks = end_checks = 0
    for ref, p, x, h, k in it.product((0, 1), repeat=5):
        s = (p, x, h, k, ref, 1 - ref)
        target = (x, h, k) == encoded_pair(p, x, ref)
        assert holds(s, invariant(0, 1, 2, 3, 4, 5)) == target
        inv_checks += 1
    for ref, b, c, v in it.product((0, 1), repeat=4):
        _, f, g = encoded_pair(b, c, ref)
        for w, h, k in it.product((0, 1), repeat=3):
            s = (b, c, f, g, v, w, h, k, ref, 1 - ref)
            target = w == (b ^ c ^ ref) and (w, h, k) == encoded_pair(v, w, ref)
            assert holds(s, bulk(*range(10))) == target, s
            transition_checks += 1
    for ref, b, v in it.product((0, 1), repeat=3):
        for w, h, k in it.product((0, 1), repeat=3):
            s = (b, v, w, h, k, ref, 1 - ref)
            target = w == b and (w, h, k) == encoded_pair(v, w, ref)
            assert holds(s, right_end(*range(7))) == target, s
            end_checks += 1

    # Wrong reference in one update constraint admits an incorrect 00 -> 1.
    bad_bulk = bulk(*range(10))
    bad_bulk[7] = (2, 5, 8)  # (f,w,R) in place of (f,w,S).
    bad = (0, 0, 1, 1, 0, 1, 0, 1, 0, 1)
    assert holds(bad, bad_bulk) and not holds(bad, bulk(*range(10)))
    # Merely retaining all four NAE triples on the first four seed identities
    # does not force the complementary reference.
    seed_hub = (1, 1, 0, 0)  # a,h0,S,R; here S=R.
    assert holds(seed_hub, it.combinations(range(4), 3))
    return dict(seed_joint_states=128, seed_allowed=seed_allowed,
                separate_reference_gadget_projection=sorted(ref_projection),
                separate_reference_gadget_extra_distinctions=4,
                invariant_checks=inv_checks, bulk_checks=transition_checks,
                right_end_checks=end_checks,
                twisted_reference_wrong_update=list(bad),
                incomplete_seed_reference_control=list(seed_hub))


def private_gadgets():
    source = json.loads(ENUM.read_text())
    gadgets = source["gadgets"]
    assert source["enumeration_complete"] and len(gadgets) == 168
    even = [x for x in it.product((0, 1), repeat=4) if sum(x) % 2 == 0]
    functions = []
    for gadget in gadgets:
        section = {}
        for x in it.product((0, 1), repeat=4):
            ys = [y for y in it.product((0, 1), repeat=3) if holds(x + y, gadget)]
            assert bool(ys) == (x in even)
            if ys:
                assert len(ys) == 1
                section[x] = ys[0]
        for h in range(3):
            fn = {x: section[x][h] for x in even}
            for pair in it.combinations(range(4), 2):
                groups = {}
                for x, value in fn.items():
                    groups.setdefault(tuple(x[j] for j in pair), set()).add(value)
                assert any(len(values) > 1 for values in groups.values())
            functions.append(fn)
    # Two neighbouring private gadgets share R and x1.  Reusing helper 0
    # of gadget 0 rejects at least one correct raw transition.
    g = gadgets[0]
    rejected = []
    for x0, x1, x2 in it.product((0, 1), repeat=3):
        left = (0, x0, x1, x0 ^ x1)
        right = (0, x1, x2, x1 ^ x2)
        a = next(y for y in it.product((0, 1), repeat=3) if holds(left + y, g))
        b = next(y for y in it.product((0, 1), repeat=3) if holds(right + y, g))
        if a[0] != b[0]:
            rejected.append(dict(input=[x0, x1, x2], left_helper=a[0], right_helper=b[0]))
    assert rejected
    return dict(gadgets=168, uniquely_determined_helper_occurrences=504,
                functions_descending_to_a_named_pair=0,
                direct_overlap_rejected_inputs=rejected)


def pair_functions():
    """All 28 normalized functions of either adjacent pair, deduplicated."""
    functions = {}
    for side, table in it.product(("left", "right"), range(16)):
        signature = tuple((table >> (2 * (a if side == "left" else b)
                                     + (b if side == "left" else c))) & 1
                          for a, b, c in it.product((0, 1), repeat=3))
        functions.setdefault(signature, dict(side=side, table=table))
    assert len(functions) == 28
    return functions


def arbitrary_encoding(xs, f, g):
    out = []
    for j, b in enumerate(xs):
        a = xs[j - 1] if j else 0
        c = xs[j + 1] if j + 1 < len(xs) else 0
        key = 4 * a + 2 * b + c
        out.extend((b, f[key], g[key]))
    return out


def maximal_local(width, f, g, span=2):
    """Every true strict triple, even giving endpoints width-specific rules."""
    n = 6 * width + 4
    positions = ([j // 3 for j in range(3 * width)]
                 + [j // 3 for j in range(3 * (width + 1))] + [None])
    candidate = []
    for triple in it.combinations(range(n), 3):
        pos = [positions[j] for j in triple if positions[j] is not None]
        if max(pos) - min(pos) <= span:
            candidate.append(triple)
    raw = list(it.product((0, 1), repeat=width))
    good = [arbitrary_encoding(x, f, g) + arbitrary_encoding(update(x), f, g) + [0]
            for x in raw]
    arr = np.array(good, dtype=np.uint8)
    candidates = np.array(candidate, dtype=np.int32)
    entries = arr[:, candidates]
    valid = np.all((entries[:, :, 0] != entries[:, :, 1])
                   | (entries[:, :, 0] != entries[:, :, 2]), axis=0)
    return [tuple(map(int, q)) for q in candidates[valid]], good, raw


def state_from_model(model, n):
    positive = set(x for x in model if x > 0)
    return [int(j + 1 in positive) for j in range(n)]


def local_obstructions():
    fs = pair_functions()
    witnesses, one, two = [], 0, 0
    width = 5
    for f, g in it.product(fs, repeat=2):
        k1, good, raw = maximal_local(width, f, g)
        witness = None
        with Solver(name="cadical195", bootstrap_with=clauses(k1)) as sat:
            for xs, row in zip(raw, good):
                fix = [j + 1 if value else -j - 1
                       for j, value in enumerate(row[:3 * width])]
                fix.append(-(6 * width + 4))
                for j in range(3 * width, 6 * width + 3, 3):
                    if sat.solve(assumptions=fix + [-j - 1 if row[j] else j + 1]):
                        full = state_from_model(sat.get_model(), 6 * width + 4)
                        assert holds(full, k1)
                        assert full[:3 * width] == row[:3 * width] and full[-1] == 0
                        assert full[j] != row[j]
                        witness = dict(steps=1, input=list(xs), position=(j - 3 * width) // 3,
                                       expected=row[j], full="".join(map(str, full)))
                        break
                if witness:
                    break
        if witness:
            one += 1
        else:
            k2, _, _ = maximal_local(width + 1, f, g)
            nv = 3 * (3 * width + 3) + 1
            ref = nv - 1
            joined = [tuple(ref if j == 6 * width + 3 else j for j in q) for q in k1]
            joined += [tuple(ref if j == 6 * (width + 1) + 3 else j + 3 * width
                             for j in q) for q in k2]
            with Solver(name="cadical195", bootstrap_with=clauses(joined)) as sat:
                for xs, row in zip(raw, good):
                    fix = [j + 1 if value else -j - 1
                           for j, value in enumerate(row[:3 * width])] + [-nv]
                    expected = update(update(xs))
                    for pos, value in enumerate(expected):
                        j = 3 * (2 * width + 1) + 3 * pos
                        if sat.solve(assumptions=fix + [-j - 1 if value else j + 1]):
                            full = state_from_model(sat.get_model(), nv)
                            assert holds(full, joined)
                            assert full[:3 * width] == row[:3 * width] and full[-1] == 0
                            assert full[j] != value
                            witness = dict(steps=2, input=list(xs), position=pos,
                                           expected=value, full="".join(map(str, full)))
                            break
                    if witness:
                        break
            assert witness is not None, (fs[f], fs[g])
            two += 1
        witness.update(helper_1=fs[f], helper_2=fs[g])
        witnesses.append(witness)
    assert (one, two, len(witnesses)) == (724, 60, 784)
    return dict(normalized_functions=28, ordered_encodings=784, span=2,
                initial_width=5, one_step_countermodels=one,
                two_step_countermodels=two, exact_iterable_encodings=0,
                witnesses=witnesses)


def local_constant_reference_obstructions():
    """Even a freely supplied local S channel plus one 3-input helper fails."""
    width = 5
    reference_channel = (1,) * 8
    witnesses = []
    for table in range(256):
        g = tuple((table >> j) & 1 for j in range(8))
        triples, good, raw = maximal_local(width, reference_channel, g)
        witness = None
        with Solver(name="cadical195", bootstrap_with=clauses(triples)) as sat:
            for xs, row in zip(raw, good):
                fix = [j + 1 if value else -j - 1
                       for j, value in enumerate(row[:3 * width])]
                fix += [-(6 * width + 4)]
                # Favour the proposal: both generations' local reference
                # helpers have their correct opposite-to-R values for free.
                fix += [j + 1 for j in range(3 * width + 1, 6 * width + 3, 3)]
                for j in range(3 * width, 6 * width + 3, 3):
                    if sat.solve(assumptions=fix + [-j - 1 if row[j] else j + 1]):
                        full = state_from_model(sat.get_model(), 6 * width + 4)
                        assert holds(full, triples)
                        assert full[:3 * width] == row[:3 * width] and full[-1] == 0
                        assert all(full[p] == 1 for p in range(1, 6 * width + 3, 3))
                        assert full[j] != row[j]
                        witness = dict(table=table, input=list(xs),
                                       position=(j - 3 * width) // 3, expected=row[j],
                                       full="".join(map(str, full)))
                        break
                if witness:
                    break
        assert witness is not None, table
        witnesses.append(witness)
    return dict(three_input_helper_functions=256, span=2, initial_width=5,
                old_and_new_reference_channels_pinned_for_free=True,
                one_step_countermodels=len(witnesses), witnesses=witnesses)


def binomial_mask(t):
    out = 1
    bit = 1
    while bit <= t:
        if bit & t:
            out ^= out << bit
        bit <<= 1
    return out


def polynomial_terminal(t, seed):
    q = binomial_mask(t)
    return (q if seed[0] else 0) ^ (q << 1 if seed[1] else 0) ^ (q << 2 if seed[2] else 0)


def closed_mask(poly, width):
    zero = ((1 << width) - 1) ^ poly
    return not ((poly & (poly >> 1) & (poly >> 2))
                | (zero & (zero >> 1) & (zero >> 2)))


def exact_life(t):
    n = 1 << ((t + 5).bit_length() - 1)
    return n - 5 <= t <= n - 2


def positive_replay():
    # Full projection tests: all raw main inputs at widths 2..7, both R values.
    one_step = 0
    for width in range(2, 8):
        rows, ref, _, triples, nv = build(1, width, close=False)
        cnf = clauses(triples)
        with Solver(name="cadical195", bootstrap_with=cnf) as sat:
            for seed in it.product((0, 1), repeat=width):
                for ref_value in (0, 1):
                    state = canonical_state(rows, ref, seed, ref_value)
                    assert holds(state, triples)
                    fix = [ref + 1 if ref_value else -ref - 1]
                    fix += [ids[0] + 1 if value else -ids[0] - 1
                            for ids, value in zip(rows[0], seed)]
                    assert sat.solve(assumptions=fix)
                    # Any differing output main or helper must be impossible.
                    for ids in rows[1]:
                        for j in ids:
                            assert not sat.solve(assumptions=fix + [-j - 1 if state[j] else j + 1])
                    one_step += 1

    spec = importlib.util.spec_from_file_location("bound_cheap_count_census", CENSUS)
    census = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(census)
    assert census.RULES["rule 60"] == ["n0", "o-1", "o0", "r"]
    seeds = list(it.product((0, 1), repeat=3))
    alive, projections, inventory = [], [], []
    for t in range(1, 65):
        rows, ref, _, triples, nv = build(t)
        expected_variables = 3 * (t + 1) * (t + 6) // 2 + 1
        assert nv == expected_variables
        assert len(triples) == 5 * t * t + 34 * t + 15
        valid = []
        with Solver(name="cadical195", bootstrap_with=clauses(triples)) as sat:
            for seed in seeds:
                expected = closed_mask(polynomial_terminal(t, seed), t + 3)
                fix = [-ref - 1] + [ids[0] + 1 if b else -ids[0] - 1
                                    for ids, b in zip(rows[0], seed)]
                got = sat.solve(assumptions=fix)
                assert got == expected, (t, seed)
                if expected:
                    valid.append("".join(map(str, seed)))
        assert bool(valid) == exact_life(t)
        alive.append(bool(valid))
        projections.append(valid)
        if t <= 8:
            legacy_cnf = census.growth(t, census.RULES["rule 60"])
            legacy_ref = (t + 1) * (t + 6) // 2
            with Solver(name="cadical195", bootstrap_with=legacy_cnf) as sat:
                for seed in seeds:
                    for ref_value in (0, 1):
                        expected = closed_mask(polynomial_terminal(t, tuple(x ^ ref_value for x in seed)), t + 3)
                        fix = [legacy_ref + 1 if ref_value else -legacy_ref - 1]
                        fix += [j + 1 if b else -j - 1 for j, b in enumerate(seed)]
                        assert sat.solve(assumptions=fix) == expected
        if t in (1, 8, 16, 32, 64):
            inventory.append(dict(depth=t, distinctions=nv, nae_triples=len(triples)))
    # Algebraic replay well beyond the registered 64, using integers rather
    # than the rule constructor or a SAT solver.
    for t in range(1, 8193):
        got = any(closed_mask(polynomial_terminal(t, seed), t + 3) for seed in seeds)
        assert got == exact_life(t), t
    for h in range(3, 15):
        n = 1 << h
        for r, seed_mask in enumerate((5, 3, 1, 1)):
            seed = tuple((seed_mask >> j) & 1 for j in range(3))
            assert closed_mask(polynomial_terminal(n - 5 + r, seed), n - 2 + r)
    return dict(all_input_one_step_cases=one_step, widths_checked=list(range(2, 8)),
                exact_closed_projection_depths=64,
                predecessor_raw_projection_depths=8,
                algebraic_band_replay_depth=8192,
                alive_1_to_64="".join("1" if x else "0" for x in alive),
                alive_depths_1_to_64=[j + 1 for j, x in enumerate(alive) if x],
                initial_main_relations=projections, inventory=inventory)


def two_output_private_block():
    """Any strict unsigned NAE definition of two adjacent parities, 4 helpers."""
    length, helpers = 2, 4
    named_count = 2 * length + 2
    candidate = [q for q in it.combinations(range(named_count + helpers), 3)
                 if max(q) >= named_count]
    top = len(candidate)
    cnf = []
    target_names = []
    for raw in it.product((0, 1), repeat=named_count - 1):
        names = (0,) + raw  # R,x0,x1,x2,y0,y1
        valid = all(names[length + 2 + j] == (names[1 + j] ^ names[2 + j])
                    for j in range(length))
        if valid:
            target_names += [names, tuple(1 - x for x in names)]
            variables = list(range(top + 1, top + 1 + helpers))
            top += helpers
            for j, q in enumerate(candidate, 1):
                terms = [(None, names[k]) if k < named_count else (variables[k - named_count], None)
                         for k in q]
                if not any(term == (None, 1) for term in terms):
                    cnf.append([-j] + [term[0] for term in terms if term[0]])
                if not any(term == (None, 0) for term in terms):
                    cnf.append([-j] + [-term[0] for term in terms if term[0]])
        else:
            for helper_values in it.product((0, 1), repeat=helpers):
                full = names + helper_values
                cnf.append([j + 1 for j, q in enumerate(candidate)
                            if not holds(full, [q])])
    for q in it.combinations(range(named_count), 3):
        assert {tuple(s[j] for j in q) for s in target_names} == set(it.product((0, 1), repeat=3))
    digest = hashlib.sha256(json.dumps(cnf, separators=(",", ":")).encode()).hexdigest()
    with Solver(name="cadical195", bootstrap_with=cnf) as sat:
        satisfiable = sat.solve()
    assert not satisfiable
    return dict(outputs=2, raw_named=6, private_helpers=4, satisfiable=False,
                clauses=len(cnf), variables=top, cnf_sha256=digest,
                solver="cadical195", proof_trace_replayed=False,
                scope="Isolated two-output block; no inherited helper channel.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    local = local_tables()
    private = private_gadgets()
    negative = local_obstructions()
    reference_negative = local_constant_reference_obstructions()
    replay = positive_replay()
    block = two_output_private_block()
    dependencies = [CENSUS, ENUM,
                    ROOT / "research/CHEAP-COUNT-20261112-001/referee-R1/report.md",
                    ROOT / "research/ROW-NEST-20261112-001/row_nest.md",
                    ROOT / "research/TWO-BIT-ROWS-20261112-001/two_bit_rows.md"]
    result = dict(
        artifact_id="BONDS-AND-COUNT-20261112-001B-P001",
        status="Partial", primary_epistemic_class="uniform-family-theorem",
        secondary_epistemic_classes=["exact-obstruction-or-countermodel", "finite-instance-classification"],
        source_contribution=0,
        construction_contract="Three distinctions per position, one global R, and broadcast access to an already charged seed helper S.",
        strict_single_broadcast_reference_target_achieved=False,
        arbitrary_width_soundness="argued-in-prose from the checked finite local tables",
        arbitrary_width_completeness="argued-in-prose from the checked finite local tables",
        arbitrary_depth_composability="argued-in-prose by induction on generations",
        non_eventually_periodic_life="argued-in-prose by exact dyadic live/dead bands",
        local_tables=local, private_gadgets=private,
        positive_replay=replay, local_obstructions=negative,
        local_constant_reference_obstructions=reference_negative,
        two_output_private_block=block,
        dependency_bindings={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in dependencies},
        owned_bindings={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in (HERE / "check.py", HERE / "proof.md")},
        validation=dict(level="V1-separate-algorithm-same-task",
                        independence="NAE/SAT construction versus integer polynomial reference; all 784 obstruction witnesses checked directly against complete local relations.",
                        trusted_kernel=False, external_review=False,
                        novelty="candidate-local-delta"),
        blocker_class="substantive-near-miss",
        remaining_obligations=[
            "Obtain the exact rule-60 transition with only the original global R and bounded neighbouring access to helpers, or prove an obstruction beyond the deterministic adjacent-pair encoding class.",
            "Period-dependent, longer-support and nondeterministic helper encodings and inherited-helper overlapping blocks are not excluded."])
    if args.write_result:
        (HERE / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(dict(status="passed", local_tables=local,
                         local_obstructions={k: v for k, v in negative.items() if k != "witnesses"},
                         local_constant_reference_obstructions={k: v for k, v in reference_negative.items() if k != "witnesses"},
                         positive_replay={k: v for k, v in replay.items() if k != "initial_main_relations"},
                         two_output_private_block=block), indent=2))


if __name__ == "__main__":
    main()
