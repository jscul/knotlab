"""Fresh finite-monoid and interface audit from the READ/CARRY mathematics.

No study Python is imported. Only standard library and installed PySAT are
used. The old referee's JSON records supply sample syntax, never a relation.
Run from the repository root with .venv/bin/python -B <this file>.
"""
from __future__ import annotations

import gzip
import hashlib
import itertools
import json
import math
import resource
import sys
import time
from collections import deque
from pathlib import Path

from pysat.solvers import Solver

ROOT = Path('/home/jscul/p-vs-np-contact-first')
HERE = ROOT / 'research/READ-RULE-20261114-001/referee-R1/codex'
READS = {}
resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))


def read_json(relative):
    path = ROOT / relative
    raw = path.read_bytes()
    READS[relative] = hashlib.sha256(raw).hexdigest()
    return json.loads(raw)


def project(value, positions):
    return sum(((value >> a) & 1) << j for j, a in enumerate(positions))


def prepare(raw):
    defs = []
    for arity, own, calls in raw:
        body = [(callee, tuple(args)) for callee, args in calls]
        # The usual-limit correction is explicitly documented in prior referee
        # notes/code, and is part of the raw census language's semantics.
        if any(c == 'SELF' and sorted(a) == [0, 1, 2] for c, a in body):
            body.append(('K', (0, 1, 2)))
        defs.append((arity, own, body))
    recursive = {i for i, (_, _, body) in enumerate(defs)
                 if any(c == 'SELF' for c, _ in body)}
    masks = {i: set(range(1 << defs[i][0])) for i in recursive}
    rounds = 0
    while True:
        all_masks = []
        for i, (arity, own, body) in enumerate(defs):
            allowed = set()
            for value in range(1 << (arity + own)):
                good = True
                for callee, args in body:
                    v = project(value, args)
                    relation = (set(range(1, 7)) if callee == 'K' else
                                masks[i] if callee == 'SELF' else all_masks[callee])
                    if v not in relation:
                        good = False
                        break
                if good:
                    allowed.add(value & ((1 << arity) - 1))
            all_masks.append(allowed)
        following = {i: all_masks[i] for i in recursive}
        rounds += 1
        assert all(following[i] <= masks[i] for i in recursive)
        if following == masks:
            break
        masks = following

    flattened = {}
    for top in range(len(defs)):
        count = defs[top][0]
        calls = []

        def visit(which, actual):
            nonlocal count
            arity, own, body = defs[which]
            env = tuple(actual) + tuple(range(count, count + own))
            count += own
            for callee, args in body:
                mapped = tuple(env[a] for a in args)
                if callee == 'K':
                    calls.append(('K', mapped))
                elif callee == 'SELF':
                    calls.append((which, mapped))
                elif callee in recursive:
                    calls.append((callee, mapped))
                else:
                    visit(callee, mapped)

        visit(top, range(defs[top][0]))
        flattened[top] = (count, calls)
    return defs, all_masks, flattened, rounds


def local_values(size, body, masks, skip=None):
    for value in range(1 << size):
        if all(j == skip or project(value, args) in
               (set(range(1, 7)) if callee == 'K' else masks[callee])
               for j, (callee, args) in enumerate(body)):
            yield value


def generators(flat, masks, S):
    size, body = flat[S]
    result = []
    for chosen, (callee, args) in enumerate(body):
        if callee != S:
            continue
        pairs = {(value & 7, project(value, args))
                 for value in local_values(size, body, masks, chosen)}
        # Eight row bit masks give a Boolean relation on source/end ports.
        rows = tuple(sum(1 << b for a0, b in pairs if a0 == a) for a in range(8))
        result.append((rows, args))
    return result


IDENTITY = tuple(1 << a for a in range(8))


def product(left, right):
    output = []
    for row in left:
        combined = 0
        for middle in range(8):
            if (row >> middle) & 1:
                combined |= right[middle]
        output.append(combined)
    return tuple(output)


def carry_step(carry, args):
    # Source identities are 0,1,2. Canonical labels >=3 record newly allocated
    # identities, including equal endpoint positions if syntax repeats args.
    actual = [carry[a] if a < 3 else ('fresh', a) for a in args]
    fresh = {}
    return tuple(v if isinstance(v, int) and v < 3 else
                 fresh.setdefault(v, 3 + len(fresh)) for v in actual)


def monoid(gens, cap=30000):
    start = (IDENTITY, (0, 1, 2))
    seen = {start: ()}
    todo = deque([start])
    while todo:
        state = todo.popleft()
        for label, (relation, args) in enumerate(gens):
            nxt = (product(state[0], relation), carry_step(state[1], args))
            if nxt not in seen:
                if len(seen) >= cap:
                    return seen, False
                seen[nxt] = seen[state] + (label,)
                todo.append(nxt)
    return seen, True


def describe_sample(name, raw, S, metadata):
    started = time.monotonic()
    defs, masks, flat, rounds = prepare(raw)
    gens = generators(flat, masks, S)
    assert masks[S] and masks[-1] and gens
    states, complete = monoid(gens)
    m = len(states)
    answer = dict(name=name, key=json.dumps(raw, separators=(',', ':')), S=S,
                  main=len(raw)-1, wrapper_offset=int(S != len(raw)-1),
                  living=True, limit_rounds=rounds, generators=len(gens),
                  generator_relations=[list(g[0]) for g in gens],
                  generator_arguments=[list(g[1]) for g in gens],
                  reachable_states=m, complete=complete,
                  boolean_relations=len({s[0] for s in states}),
                  carry_maps=len({s[1] for s in states}), metadata=metadata,
                  longest_shortest_word=max(map(len, states.values())),
                  all_flat_calls_injective=all(len(a) == len(set(a)) for _, a in flat[S][1]),
                  seconds=round(time.monotonic()-started, 4))
    if complete:
        answer.update(m=m, period_expression=f'{m}!',
                      linear_constant_exact=f'1/{m+1}',
                      linear_constant_float=1/(m+1))
        if m <= 1000:
            answer['period_exact'] = str(math.factorial(m))
        else:
            answer['period_decimal_digits'] = int(math.lgamma(m+1)/math.log(10))+1
    return answer


def add_relation(clauses, actual, allowed):
    for value in range(1 << len(actual)):
        if value not in allowed:
            clauses.append([-(v+1) if (value >> j) & 1 else v+1
                            for j, v in enumerate(actual)])


class Direct:
    """Independent CNF for an explicitly decorated selected derivation word."""
    def __init__(self, raw, S, word):
        self.defs, self.masks, self.flat, _ = prepare(raw)
        self.S = S
        assert S == len(raw)-1 and self.defs[S][0] == 3
        self.n = 3
        self.clauses = []
        self.envs = []
        self.side_envs = {}
        _, body = self.flat[S]
        self.child_indices = [j for j, (c, _) in enumerate(body) if c == S]
        current = (0, 1, 2)
        for depth in range(len(word)+1):
            chosen = self.child_indices[word[depth]] if depth < len(word) else None
            env = self.block(current, chosen, depth)
            self.envs.append(env)
            if chosen is not None:
                current = tuple(env[a] for a in body[chosen][1])

    def block(self, actual, chosen, depth, decorate=True):
        size, body = self.flat[self.S]
        env = tuple(actual) + tuple(range(self.n, self.n+size-3))
        self.n += size-3
        for j, (callee, args) in enumerate(body):
            if j == chosen:
                continue
            mapped = tuple(env[a] for a in args)
            if callee == self.S and decorate and depth in (0, -1):
                side = self.block(mapped, None, depth, decorate=False)
                self.side_envs[(depth, j)] = side
            else:
                add_relation(self.clauses, mapped,
                             set(range(1, 7)) if callee == 'K' else self.masks[callee])
        return env

    def projection(self, support):
        assert len(support) == len(set(support))
        allowed = []
        with Solver(name='minisat22', bootstrap_with=self.clauses) as sat:
            for value in range(1 << len(support)):
                cube = [v+1 if (value >> j) & 1 else -(v+1)
                        for j, v in enumerate(support)]
                if sat.solve(assumptions=cube):
                    allowed.append(value)
        return allowed


def controls():
    # One selected identity occurs in every block, but has one allocation.
    unary = [[3, 1, [['K', [0, 1, 3]], ['SELF', [0, 1, 3]]]]]
    _, masks, flat, _ = prepare(unary)
    gens = generators(flat, masks, 0)
    states, complete = monoid(gens)
    assert complete
    m = len(states)
    period = math.factorial(m)
    depth = max(20, 5*(m+1))
    instance = Direct(unary, 0, (0,)*depth)
    support = (0, 1, instance.envs[-1][3])
    projection = instance.projection(support)
    assert len(projection) == 6
    proper = [instance.projection(support[:j]+support[j+1:]) for j in range(3)]
    assert all(len(p) == 4 for p in proper)
    literal_occupied = sum(bool(set(env).intersection(support)) for env in instance.envs)
    assert literal_occupied == depth+1
    assert len(support) < depth/(m+1)-1

    # Pump by the actual factorial period in this tiny complete monoid.
    longer = Direct(unary, 0, (0,)*(depth+period))
    longer_support = (0, 1, longer.envs[-1][3])
    pumped = longer.projection(longer_support)
    assert projection == pumped
    all_subsets = 0
    for n in range(4):
        for positions in itertools.combinations(range(3), n):
            old = instance.projection(tuple(support[j] for j in positions))
            new = longer.projection(tuple(longer_support[j] for j in positions))
            assert old == new
            all_subsets += 1

    # Abstracting a block containing u_0 loses its local NAE constraint if
    # u_0 is treated as an unconstrained retained name outside that product.
    root_support = (0, 1, instance.envs[0][3])
    correct = instance.projection(root_support)
    collapsed = IDENTITY
    for _ in range(depth):
        collapsed = product(collapsed, gens[0][0])
    naive_clauses = []
    for a in range(8):
        for b in range(8):
            if not ((collapsed[a] >> b) & 1):
                value = a | (b << 3)
                naive_clauses.append([-(v+1) if (value >> j) & 1 else v+1
                                      for j, v in enumerate((0, 1, 2, 0, 1, 3))])
    add_relation(naive_clauses, (0, 1, 3), masks[0])
    # Variable 4 is the member u_0 that the wrong cut treats as dangling.
    naive_projection = []
    with Solver(name='minisat22', bootstrap_with=naive_clauses) as sat:
        for value in range(8):
            if sat.solve(assumptions=[v+1 if (value >> j) & 1 else -(v+1)
                                      for j, v in enumerate((0, 1, 4))]):
                naive_projection.append(value)
    assert len(correct) == 6 and correct != naive_projection

    # A prefix-owned non-main member is carried along the stretch's second
    # port. A genuine side subtree is attached at every stretched copy.
    branched = [[3, 1, [['K', [0, 2, 3]], ['SELF', [0, 3, 2]],
                        ['SELF', [0, 1, 3]]]]]
    _, masks_b, flat_b, _ = prepare(branched)
    gs = generators(flat_b, masks_b, 0)
    q = (IDENTITY, (0, 1, 2))
    history = {q: 0}
    repetitions = []
    for t in range(1, 100):
        q = (product(q[0], gs[1][0]), carry_step(q[1], gs[1][1]))
        if q in history:
            repetitions = [history[q], t]
            break
        history[q] = t
    assert repetitions
    i, j = repetitions
    oldword = (0,) + (1,)*(j+2)
    newword = (0,) + (1,)*(j+2+j-i)
    old = Direct(branched, 0, oldword)
    new = Direct(branched, 0, newword)
    oldside = next(iter(old.side_envs.values()))[3]
    newside = next(iter(new.side_envs.values()))[3]
    old_support = (0, old.envs[0][3], oldside, old.envs[-1][3])
    new_support = (0, new.envs[0][3], newside, new.envs[-1][3])
    assert old.envs[-1][1] == old.envs[0][3]
    assert new.envs[-1][1] == new.envs[0][3]
    carried_projection = old.projection(old_support)
    assert carried_projection == new.projection(new_support)
    subset_checks = 0
    for n in range(5):
        for positions in itertools.combinations(range(4), n):
            assert old.projection(tuple(old_support[a] for a in positions)) == new.projection(tuple(new_support[a] for a in positions))
            subset_checks += 1
    return dict(
        occupied_occurrences_negative_control=dict(
            key=unary, depth=depth, m=m, period=period, W_size=3,
            literal_occupied_levels=literal_occupied,
            claimed_no_long_lower_bound=depth/(m+1)-1,
            W_projection=projection, proper_projection_sizes=list(map(len, proper)),
            literal_counting_implication_rejected=True),
        exact_period_pump=dict(old_depth=depth, new_depth=depth+period,
                               identical_full_projection=True,
                               all_subset_projections_checked=all_subsets),
        off_by_one_negative_control=dict(correct_projection=correct,
                                         dangling_member_projection=naive_projection,
                                         naive_factorisation_rejected=True),
        non_main_carriage_and_side_subtrees=dict(
            key=branched, repeated_prefix_lengths=repetitions,
            old_depth=len(oldword), new_depth=len(newword),
            non_main_member_carried_by_identity=True,
            retained_member_in_prefix_side_subtree=True,
            other_side_subtrees_summarised_by_exact_limit=True,
            joint_projection=carried_projection,
            full_projection_equal=True, all_subset_projections_checked=subset_checks))


def input_samples():
    grow = read_json('research/CARRY-BOUND-20261114-001/referee-R1/codex/grow_sample.json')
    windows = read_json('research/CARRY-BOUND-20261114-001/referee-R1/codex/window_inputs.json')
    samples = []
    # Initial eight are the relation-free global-exact chain sample; include
    # both root conventions and two harder branching growers.
    for index in (0, 1, 4, 6, 8, 10):
        row = grow[index]
        raw = json.loads(row['key'])
        recursive = [i for i, (_, _, b) in enumerate(raw) if any(c == 'SELF' for c, _ in b)]
        S = len(raw)-1 if not row['wrapper'] else max(recursive)
        samples.append((f'grow_{index}', raw, S, {k: row.get(k) for k in ('key_sha256', 'wrapper', 'stratum', 'verdict')}))
    for index in (0, 1, 2, 3):
        record = windows['records'][index]
        d = record['digest']
        samples.append((f'bounded_{index}', json.loads(d['key']), record['census']['S'],
                        {k: d.get(k) for k in ('key_sha256', 'wrapper', 'stratum', 'verdict')}))
    samples.append(('synthetic_read_carried', [[3, 1, [['K', [0, 1, 3]], ['SELF', [0, 1, 3]]]]], 0, {}))
    return samples


def census_identity_audit():
    path = ROOT / 'artifacts/READ-RULE-20261114-001B/READ-RULE-20261114-001B-E001_coverage/census_run_results.jsonl.gz'
    READS[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    families = 0
    repeats = []
    with gzip.open(path, 'rt') as source:
        for line in source:
            row = json.loads(line)['result']
            families += 1
            raw = json.loads(row['key'])
            for which, (_, _, body) in enumerate(raw):
                for callee, args in body:
                    if len(args) != len(set(args)):
                        repeats.append(dict(key_sha256=row['key_sha256'], definition=which,
                                            callee=callee, arguments=args))
    return dict(families=families, repeated_argument_calls=len(repeats), examples=repeats[:20])


def main():
    started = time.monotonic()
    output = dict(evidence_stage='independent finite recomputation plus symbolic audit',
                  scientific_scope='covered S copies only',
                  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  controls=controls(), samples=[])
    for sample in input_samples():
        row = describe_sample(*sample)
        output['samples'].append(row)
        print(json.dumps({k: row[k] for k in ('name', 'reachable_states', 'complete', 'boolean_relations', 'carry_maps', 'seconds')}), flush=True)
    output['census_identity_arguments'] = census_identity_audit()
    output.update(sources=READS, seconds=round(time.monotonic()-started, 3),
                  peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  prohibited_study_python_opened_or_imported=False,
                  nonclaim='Finite controls are not a proof of the infinite dichotomy; the report supplies that argument.')
    (HERE / 'pumping_results.json').write_text(json.dumps(output, indent=2)+'\n')
    print(json.dumps({k: output[k] for k in ('seconds', 'peak_rss_kib', 'census_identity_arguments')}))


if __name__ == '__main__':
    main()
