"""Independent, bounded controls for the TOP-INFO localisation referee.

Standard library only; no study Python is opened or imported.  These tiny
finite checks test the cuts and their failure modes.  The accompanying audit
supplies the uniform argument.  Run with the workspace .venv Python and -B.
"""
from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import math
import random
import resource
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path


ROOT = Path('/home/jscul/p-vs-np-contact-first')
HERE = ROOT / 'research/TOP-INFO-20261114-001/referee-R1/codex'
resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))


def relation_product(left, right):
    answer = []
    for row in left:
        out = 0
        for j in range(len(right)):
            if row & (1 << j):
                out |= right[j]
        answer.append(out)
    return tuple(answer)


@dataclass(frozen=True)
class Generator:
    source: str
    end: str
    relation: tuple[int, ...]
    identity_carried: bool


class System:
    """A tiny typed relation/carry algebra, explicitly closed before use."""

    def __init__(self, kinds, generators, value_count=2):
        self.kinds = tuple(kinds)
        self.generators = tuple(generators)
        self.identity = tuple(1 << j for j in range(value_count))
        seen = {self.initial(k) for k in self.kinds}
        todo = deque(seen)
        while todo:
            state = todo.popleft()
            for label, g in enumerate(self.generators):
                if g.source != state[0]:
                    continue
                nxt = self.step(state, label)
                if nxt not in seen:
                    seen.add(nxt)
                    todo.append(nxt)
        self.states = seen
        self.m = len(seen)
        self.period = math.factorial(self.m)
        self.K = self.m * (self.period + 1)

    def initial(self, kind):
        return kind, self.identity, True

    def step(self, state, label):
        g = self.generators[label]
        assert state[0] == g.source, (state, label, g)
        return (g.end, relation_product(state[1], g.relation),
                state[2] and g.identity_carried)

    def prefixes(self, word, initial=None):
        state = self.initial(self.kinds[0]) if initial is None else initial
        result = [state]
        for label in word:
            state = self.step(state, label)
            result.append(state)
        return result

    def value(self, word, initial=None):
        return self.prefixes(word, initial)[-1]


def repeated_pair(states, modulus=None):
    seen = {}
    for j, state in enumerate(states):
        key = state if modulus is None else (state, j % modulus)
        if key in seen:
            return seen[key], j
        seen[key] = j
    return None


def shorten(system, word, *, initial=None, preserve_residue=True):
    """Delete equal prefix states; with residues retain length modulo m!."""
    old = tuple(word)
    word = old
    bound = system.m * system.period if preserve_residue else system.m
    cuts = []
    while len(word) >= bound:
        pair = repeated_pair(system.prefixes(word, initial),
                             system.period if preserve_residue else None)
        assert pair is not None
        i, j = pair
        before = system.value(word, initial)
        word = word[:i] + word[j:]
        assert system.value(word, initial) == before
        if preserve_residue:
            assert (j - i) % system.period == 0
        cuts.append((i, j))
    assert system.value(word, initial) == system.value(old, initial)
    if preserve_residue:
        assert (len(old) - len(word)) % system.period == 0
    return word, cuts


def short_loop(system, word):
    assert len(word) >= system.m
    pair = repeated_pair(system.prefixes(word[:system.m]))
    assert pair is not None
    i, j = pair
    assert 0 < j - i <= system.m
    assert system.period % (j - i) == 0
    return i, j


def insert_multiple(system, word, amount, loop=None):
    assert amount >= 0 and amount % system.period == 0
    i, j = short_loop(system, word) if loop is None else loop
    y = word[i:j]
    assert system.value(word[:i]) == system.value(word[:j])
    assert amount % len(y) == 0
    answer = word[:j] + y * (amount // len(y)) + word[j:]
    assert len(answer) == len(word) + amount
    assert system.value(answer) == system.value(word)
    return answer


def preserve_loop_and_shorten(system, word):
    """Keep a short pumpable prefix, shorten only what follows it."""
    i, j = short_loop(system, word)
    prefix = word[:j]
    suffix, cuts = shorten(system, word[j:], initial=system.value(prefix))
    answer = prefix + suffix
    assert len(answer) < system.K
    assert (len(word) - len(answer)) % system.period == 0
    assert system.value(answer) == system.value(word)
    assert system.value(answer[:i]) == system.value(answer[:j])
    return answer, (i, j), cuts


def shape_holds(gaps, long_index, wrapper, C, K):
    """Gap source blocks, interspersed occupied source blocks, then target."""
    positions = []
    index = 0
    for j, gap in enumerate(gaps):
        index += len(gap) if not isinstance(gap, int) else gap
        if j + 1 < len(gaps):
            positions.append(index)
            index += 1
    depth = index + wrapper
    B = C * K
    return all(min(i + wrapper, depth - (i + wrapper)) <= B
               for i in positions), depth, positions


def semigroup_controls():
    eq, ne, full = (1, 2), (2, 1), (3, 3)
    system = System(('S',), (
        Generator('S', 'S', eq, True),
        Generator('S', 'S', ne, False),
        Generator('S', 'S', full, False),
    ))
    rng = random.Random(2026111401)
    residue_cases = 0
    restoration_cases = 0
    backward_cases = 0
    example = None
    for C in (2, 3, 4, 6):
        for _ in range(20):
            t = rng.randrange(C - 1)  # main port and target are outside these t.
            words = [tuple(rng.randrange(3) for _ in range(rng.randrange(1, 4) * system.K))
                     for _ in range(t + 1)]
            original_depth = sum(map(len, words)) + t
            longest = max(range(len(words)), key=lambda a: len(words[a]))
            old_states = list(map(system.value, words))
            reduced = list(words)
            removed = 0
            for j in range(len(words)):
                if j == longest:
                    continue
                reduced[j], _ = shorten(system, words[j])
                removed += len(words[j]) - len(reduced[j])
                assert len(reduced[j]) < system.K
                residue_cases += 1
            reduced[longest] = insert_multiple(system, reduced[longest], removed)
            assert sum(map(len, reduced)) + t == original_depth
            assert list(map(system.value, reduced)) == old_states
            for wrapper in (0, 1):
                assert shape_holds(reduced, longest, wrapper, C, system.K)[0]
            restoration_cases += 1

            # Stronger repair: obtain a short base carrying a saved short loop,
            # then pump it to arbitrary later depths of the original residue.
            base = []
            saved = None
            for j, word in enumerate(words):
                if j == longest:
                    new, loop, _ = preserve_loop_and_shorten(system, word)
                    saved = loop
                else:
                    new, _ = shorten(system, word)
                base.append(new)
            assert all(len(word) < system.K for word in base)
            assert list(map(system.value, base)) == old_states
            for wrapper in (0, 1):
                base_depth = sum(map(len, base)) + t + wrapper
                r = (original_depth + wrapper) % system.period
                H = (C + 1) * system.K + C
                desired = H + 1 + ((r - H - 1) % system.period)
                for target in range(desired, desired + 4 * system.period, system.period):
                    amount = target - base_depth
                    assert amount >= 0 and amount % system.period == 0
                    new = list(base)
                    new[longest] = insert_multiple(system, base[longest], amount, saved)
                    shape, depth, _ = shape_holds(new, longest, wrapper, C, system.K)
                    assert shape and depth == target
                    assert list(map(system.value, new)) == old_states
                    backward_cases += 1
                    if example is None:
                        example = dict(C=C, wrapper=wrapper, original_depth=original_depth + wrapper,
                                       base_depth=base_depth, H=H, restored_depth=target,
                                       original_gaps=list(map(len, words)),
                                       base_gaps=list(map(len, base)),
                                       final_gaps=list(map(len, new)), loop=list(saved))

    # A repeated prefix loop need not be an idempotent semigroup element.
    algebra = System(('A',), (
        Generator('A', 'A', (1, 1, 1), False),  # constant 0
        Generator('A', 'A', (1, 4, 2), False),  # fixes 0, swaps 1 and 2
    ), value_count=3)
    prefix, y = (0,), (1,)
    assert algebra.value(prefix + y) == algebra.value(prefix)
    assert algebra.value(y + y) != algebra.value(y)
    for k in range(10):
        assert algebra.value(prefix + y * k) == algebra.value(prefix)

    # Reusing an arbitrary residue-preserving deletion as the insertion loop
    # can fail to add exactly m!, although a short loop always repairs it.
    too_long_loop = (0,) * (2 * system.period)
    assert system.value(too_long_loop) == system.value(())
    unsafe_addition_rejected = system.period % len(too_long_loop) != 0
    assert unsafe_addition_rejected
    fixed = insert_multiple(system, too_long_loop, system.period)
    assert len(fixed) == len(too_long_loop) + system.period

    return dict(m=system.m, period=system.period, K=system.K,
                shortening_cases=residue_cases, exact_restoration_cases=restoration_cases,
                arbitrary_depth_recovery_cases=backward_cases, recovery_example=example,
                stable_prefix_nonidempotent_loop_checked=True,
                arbitrary_long_loop_insertion_rejected=unsafe_addition_rejected,
                short_loop_repair_verified=True)


def typed_controls():
    eq = (1, 2)
    system = System(('A', 'B'), (
        Generator('A', 'B', eq, True),
        Generator('B', 'A', eq, True),
    ))
    word = (0, 1, 0, 1, 0, 1)
    # The same relation/carry state is seen at positions 0 and 1, but their
    # copy types differ.  Deleting that first factor leaves an illegal word.
    q0, q1 = system.prefixes(word)[:2]
    assert q0[1:] == q1[1:] and q0[0] != q1[0]
    wrong_cut_rejected = False
    try:
        system.value(word[1:])
    except AssertionError:
        wrong_cut_rejected = True
    assert wrong_cut_rejected
    reduced, cuts = shorten(system, word, preserve_residue=False)
    assert system.value(reduced) == system.value(word)
    return dict(m=system.m, period=system.period, type_erased_cut_rejected=True,
                old_word=list(word), legal_reduced_word=list(reduced), cuts=cuts,
                endpoint_type_preserved=True)


def relation_on(variables, constraints, support):
    index = {name: j for j, name in enumerate(variables)}
    answer = set()
    for bits in itertools.product((0, 1), repeat=len(variables)):
        if all(len({bits[index[x]] for x in triple}) > 1 for triple in constraints):
            answer.add(tuple(bits[index[x]] for x in support))
    return answer


def subset_projections(relation, width):
    return {positions: {tuple(row[j] for j in positions) for row in relation}
            for k in range(width + 1) for positions in itertools.combinations(range(width), k)}


def is_bond(relation, width):
    projections = subset_projections(relation, width)
    return (len(relation) < 2**width and
            all(len(allowed) == 2**len(positions)
                for positions, allowed in projections.items() if len(positions) < width))


def projection_controls():
    # At an unselected branch copy q is allocated and passed into both arms.
    # a is allocated in a side arm; b,z are allocated in the retained lower
    # block.  The branch copy itself owns no selected member of W.
    support = ('p', 'a', 'b', 'z')
    old = relation_on(('p', 'a', 'q', 'b', 'z'),
                      (('p', 'a', 'q'), ('q', 'b', 'z')), support)
    assert is_bond(old, 4)
    # Cutting only a member-free unary run retains both selected arms and the
    # same non-main identity q at its lower interface.
    correct = relation_on(('p', 'a', 'Q', 'b', 'z'),
                          (('p', 'a', 'Q'), ('Q', 'b', 'z')), support)
    assert old == correct
    old_subsets = subset_projections(old, 4)
    new_subsets = subset_projections(correct, 4)
    assert old_subsets == new_subsets

    # An own-only occupancy rule cuts through the branchpoint, deleting its
    # selected side arm.  Retaining a as a dangling coordinate is unsound.
    erased = relation_on(('p', 'a', 'q', 'b', 'z'), (('q', 'b', 'z'),), support)
    assert len(erased) == 16 and erased != old
    # A mutant that disconnects a non-main interface identity also fails.
    # This control does not assert that its transfer relation stayed equal.
    lost_carry = relation_on(('p', 'a', 'q0', 'q1', 'b', 'z'),
                            (('p', 'a', 'q0'), ('q1', 'b', 'z')), support)
    assert len(lost_carry) == 16 and lost_carry != old

    # A living, one-recursive-type NAE family can have arbitrarily nonlocal
    # *least* bonds: S(p,q,r) owns x and imposes NAE(p,q,x), S(p,q,x),
    # S(p,x,q).  Take x_s down the first call chain, then follow the second
    # call once and the first call i times to z_i.  The displayed constraints
    # below are its exact relevant relation: every omitted subtree extends
    # by choosing its fresh own values opposite p.  q can be opposite p,
    # leaving x_s free.  Thus every {p,x_s,z_i} is a least 3-bond, for every i.
    fan_checks = []
    for depth in (1, 2, 5, 9):
        variables = ('p', 'q', 'x') + tuple(f'z{i}' for i in range(depth + 1))
        constraints = (('p', 'q', 'x'),) + tuple(('p', 'x', f'z{i}') for i in range(depth + 1))
        far = relation_on(variables, constraints, ('p', 'x', f'z{depth}'))
        near = relation_on(variables, constraints, ('p', 'x', 'z0'))
        assert is_bond(far, 3) and is_bond(near, 3)
        assert len(relation_on(variables, constraints, ('p', 'x'))) == 4
        assert len(relation_on(variables, constraints, ('q', 'x'))) == 4
        assert far == near
        assert subset_projections(far, 3) == subset_projections(near, 3)
        fan_checks.append(dict(side_depth=depth, projection_size=len(far),
                               all_subset_projections_equal=True, least_bond=True))
    return dict(branch_support=list(support), joint_projection=sorted(map(list, old)),
                is_four_member_bond=True, all_subset_projections_checked=len(old_subsets),
                side_branch_erasure_projection_size=len(erased),
                side_branch_erasure_rejected=True, lost_non_main_carry_projection_size=len(lost_carry),
                lost_non_main_carry_rejected=True, fan_least_bond_controls=fan_checks,
                universal_all_least_localisation_refuted_symbolically=True)


@dataclass
class Node:
    kind: int
    own: tuple[str, ...] = ()
    children: tuple['Node', ...] = ()


def selected(node):
    return set(node.own).union(*(selected(child) for child in node.children))


def depths(node, d=0):
    answer = {name: d for name in node.own}
    for child in node.children:
        answer.update(depths(child, d + 1))
    return answer


def lengthen_to(node, distance):
    """Add alternating-type unary source copies above an endpoint."""
    out = node
    for _ in range(distance - 1):
        out = Node(1 - out.kind, (), (out,))
    return out


def contract(node, anchor=False):
    # Keep every selected allocation and every branchpoint with selected arms.
    children = tuple(contract(child) for child in node.children if selected(child))
    out = Node(node.kind, node.own, children)
    if anchor:
        return out
    while not out.own and len(out.children) == 1:
        child = out.children[0]
        if child.own or len(child.children) != 1:
            break
        lower = child.children[0]
        if lower.kind != out.kind:
            break
        out = lower  # equal typed identity-transfer prefix state after two steps.
    return out


def side_tree_controls():
    # Long source-copy runs with branching and selected allocations internally.
    a = Node(0, ('a',))
    b = Node(0, ('b',))
    c = Node(0, ('c',))
    branch = Node(1, (), (lengthen_to(a, 21), lengthen_to(b, 17)))
    inside = Node(0, ('d',), (lengthen_to(branch, 15), lengthen_to(c, 20)))
    root = Node(1, (), (lengthen_to(inside, 25),))
    def legal(node):
        return all(child.kind != node.kind and legal(child) for child in node.children)
    assert legal(root)
    old_ids = selected(root)
    repaired = contract(root, anchor=True)
    assert selected(repaired) == old_ids
    assert legal(repaired)
    m = 2  # identity transfer, alternating copy type.
    C = len(old_ids)
    assert max(depths(repaired).values()) <= C * (m + 1)

    # Own-only path occupancy would mark no intermediate node on the path to
    # b before the terminal allocation, and would permit erasing branch 'a'.
    bad = Node(1, (), (lengthen_to(b, 1),))
    assert legal(bad)
    assert selected(bad) != {'a', 'b'}
    return dict(selected_members=sorted(old_ids), m=m, C=C,
                original_depths=depths(root), compressed_depths=depths(repaired),
                bound=C * (m + 1), selected_members_preserved=True,
                unselected_branchpoints_preserved=True,
                own_only_side_cut_loses_member_control_rejected=True)


def arithmetic_controls():
    checked = 0
    for m in (1, 2, 3, 4):
        period = math.factorial(m)
        K = m * (period + 1)
        for C in range(2, 8):
            # Deliberately permit t=C, looser than the actual t<=C-2 bound.
            for t in range(C + 1):
                for longest in range(t + 1):
                    for edge_choices in itertools.product((0, K - 1), repeat=t):
                        gaps, it = [], iter(edge_choices)
                        for j in range(t + 1):
                            gaps.append((C + 2) * K if j == longest else next(it))
                        for wrapper in (0, 1):
                            assert shape_holds(gaps, longest, wrapper, C, K)[0]
                            checked += 1
            H = (C + 1) * K + C
            # If no gap reaches K, n<= (t+1)(K-1)+t <= (C+1)K-1.
            assert max((t + 1) * (K - 1) + t for t in range(C + 1)) < H
    return dict(endpoint_shape_extreme_cases=checked, wrapper_offsets=[0, 1],
                B_equals_C_m_Pi_plus_one_passed=True,
                stated_threshold_suffices_for_a_long_gap=True,
                actual_pre_target_occupancy_is_at_most_C_minus_two=True)


def synthetic_cnf_control():
    # Reuse only the explicitly permitted earlier referee implementation.
    # It builds raw clauses and exact finite tail masks, never study objects.
    previous = ROOT / 'research/READ-RULE-20261114-001/referee-R1/codex/pumping_audit.py'
    spec = importlib.util.spec_from_file_location('prior_referee_pumping', previous)
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    raw = [[3, 1, [['K', [0, 1, 3]], ['SELF', [0, 1, 3]], ['SELF', [0, 3, 1]]]]]
    _, masks, flat, _ = audit.prepare(raw)
    generators = audit.generators(flat, masks, 0)
    states, complete = audit.monoid(generators)
    assert complete and masks[0] == set(range(8))
    m = len(states)
    period = math.factorial(m)
    C = 3
    K = m * (period + 1)
    B = C * K
    H = (C + 1) * K + C
    s = H + 1
    descent = C * (m + 1) + 2
    word = (0,) * s + (1,) + (0,) * (descent - 1)
    direct = audit.Direct(raw, 0, word)
    target = direct.envs[s][3]
    far_support = (0, target, direct.envs[-1][3])
    near_support = (0, target, direct.envs[s + 1][3])
    far = direct.projection(far_support)
    near = direct.projection(near_support)
    assert far == near == list(range(1, 7))
    subset_checks = 0
    for size in range(4):
        for positions in itertools.combinations(range(3), size):
            f = direct.projection(tuple(far_support[j] for j in positions))
            n = direct.projection(tuple(near_support[j] for j in positions))
            assert f == n
            if size < 3:
                assert len(f) == 2**size
            subset_checks += 1

    # Independently inspect every transfer state to exclude every possible
    # root-port/target-own tie, hence every size-2 eligible bond at any depth.
    pair_checks = 0
    for relation, _carry in states:
        for root_port in range(3):
            pairs = set()
            for alpha in range(8):
                for beta in range(8):
                    if not (relation[alpha] >> beta) & 1:
                        continue
                    for own in (0, 1):
                        if len({beta & 1, (beta >> 1) & 1, own}) > 1:
                            pairs.add(((alpha >> root_port) & 1, own))
            assert pairs == set(itertools.product((0, 1), repeat=2))
            pair_checks += 1
    clauses_json = json.dumps(direct.clauses, separators=(',', ':')).encode()
    return dict(
        synthetic_outside_65=True, raw_family=raw, covered_definition=0,
        usual_limit_mask=sorted(masks[0]), m=m, period=period, C=C, K=K, B=B, H=H,
        target_depth=s, side_descent=descent, side_bound=C * (m + 1),
        word_run_length_encoding=[[0, s], [1, 1], [0, descent - 1]],
        variables=direct.n, clauses=len(direct.clauses),
        canonical_clauses_json_sha256=hashlib.sha256(clauses_json).hexdigest(),
        far_support=list(far_support), near_support=list(near_support),
        joint_projection=far, all_subset_projection_checks=subset_checks,
        all_transfer_states_root_target_pair_checks=pair_checks,
        far_support_is_least=True, near_support_is_least=True,
        disproves_every_least_local_but_not_existential_statement=True,
        helper='permitted prior referee pumping_audit.py; no study Python',
    )


def source_hashes():
    names = (
        'research/TOP-INFO-20261114-001/top_info.md',
        'research/TOP-INFO-20261114-001/preregistration.md',
        'research/TOP-INFO-20261114-001/advisor_proof_answer.md',
        'proofs/TOP-INFO-20261114-001B/TOP-INFO-20261114-001B-P001_top_info/proof.md',
        'research/READ-RULE-20261114-001/referee-R1/codex/pumping_proof_audit.md',
        'research/READ-RULE-20261114-001/referee-R1/codex/pumping_audit.py',
    )
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in names}


def main():
    started = time.monotonic()
    output = dict(
        validation='V1: separate algorithm authored in the same research task; no producer functions',
        scope='localisation proof only; finite controls do not prove the uniform theorem',
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        semigroups=semigroup_controls(), typed_words=typed_controls(),
        projections=projection_controls(), side_trees=side_tree_controls(),
        arithmetic=arithmetic_controls(), synthetic_cnf=synthetic_cnf_control(),
        sources=source_hashes(),
        prohibited_study_python_opened_or_imported=False,
    )
    output.update(seconds=round(time.monotonic() - started, 4),
                  peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    path = HERE / 'localisation_checks.json'
    path.write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps({key: output[key] for key in ('seconds', 'peak_rss_kib', 'validation')}))
    print(json.dumps({key: output[key] for key in ('semigroups', 'typed_words', 'side_trees', 'arithmetic')}))


if __name__ == '__main__':
    main()
