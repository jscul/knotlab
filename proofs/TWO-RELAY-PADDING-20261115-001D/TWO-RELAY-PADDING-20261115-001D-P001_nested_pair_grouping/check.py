"""Exact interval evaluation and raw guarded-CNF checks for nested name pairs."""

from functools import lru_cache
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
import json
from pathlib import Path
from random import Random
import sys


STATES = range(8)
IDENTITY = tuple(1 << q for q in STATES)
BASE = Path(__file__).resolve().parents[3] / 'proofs' / 'SIGNED-KNOT-OVERLAP-20261114-001C' / 'SIGNED-KNOT-OVERLAP-20261114-001C-P001_many_easy_obstructions' / 'check.py'


def named_word(middles, pads):
    """Use disjoint, dense middle/pad identifiers and the supplied six-position order."""
    if len(middles) % 2 or len(pads) != 2 * len(middles):
        raise ValueError('expected two middle positions and four pad positions per stage')
    n = len(middles) + len(pads)
    if any(not isinstance(v, int) or not 0 <= v < n for seq in (middles, pads) for v in seq):
        raise ValueError('expected indexed names between 0 and the word length minus one')
    word = []
    for i, name in enumerate(middles):
        word.extend((2 * name, 2 * pads[2*i] + 1, 2 * pads[2*i+1] + 1))
    return word


def partner_positions(word):
    first = [-1] * (2 * len(word))
    mate = [-1] * len(word)
    for i, name in enumerate(word):
        previous = first[name]
        if previous == -1:
            first[name] = i
        elif mate[previous] == -1:
            mate[previous], mate[i] = i, previous
        else:
            raise ValueError('name occurs more than twice')
    return mate


def check_stack(word, mate, removed):
    """The first unmatched close provides the two names of an alternating pair."""
    opened = []
    depth = 0
    for i, partner in enumerate(mate):
        if removed[word[i]]:
            continue
        if partner > i:
            opened.append(i)
            depth = max(depth, len(opened))
        elif partner >= 0:
            latest = opened.pop()
            if latest != partner:
                return (word[partner], word[latest]), depth
    return None, depth


def match_positions(word, omitted=()):
    mate = partner_positions(word)
    removed = bytearray(2 * len(word))
    for name in omitted:
        removed[name] = 1
    pair, depth = check_stack(word, mate, removed)
    if pair is not None:
        raise ValueError('two pairs interleave in the joint order')
    return [-1 if removed[name] else mate[i] for i, name in enumerate(word)], depth


def find_removal(word, budget=None):
    """Find names covering all alternating pairs, branching without forming the graph."""
    mate = partner_positions(word)
    pair_count = sum(j > i for i, j in enumerate(mate))
    limits = range(pair_count+1) if budget is None else (budget,)
    for limit in limits:
        if limit < 0:
            raise ValueError('negative removal budget')
        removed = bytearray(2 * len(word))
        chosen = []
        jobs = [('visit', 0)]
        while jobs:
            operation, name = jobs.pop()
            if operation == 'add':
                chosen.append(name)
                removed[name] = 1
            elif operation == 'undo':
                chosen.pop()
                removed[name] = 0
            else:
                pair, _ = check_stack(word, mate, removed)
                if pair is None:
                    return tuple(chosen)
                if len(chosen) < limit:
                    for alternative in pair:
                        jobs.extend((('undo', alternative), ('visit', 0), ('add', alternative)))
    return None


def union(left, right):
    return tuple(a | b for a, b in zip(left, right))


def compose(left, right):
    result = []
    for reachable in left:
        targets = 0
        while reachable:
            bit = reachable & -reachable
            targets |= right[bit.bit_length()-1]
            reachable ^= bit
        result.append(targets)
    return tuple(result)


@lru_cache(maxsize=48)
def transition(phase, active, value):
    """State is (old boundary, guessed new boundary, current branch middle)."""
    rows = []
    for q in STATES:
        old, new, middle = q >> 2, (q >> 1) & 1, q & 1
        if phase == 0:
            targets = (1 << (4*old + value)) | (1 << (4*old + 2 + value)) if q == 4*old else 0
        elif phase == 3:
            targets = 1 << (4*old + 2*new + value)
        else:
            tail, head = (old, middle) if phase in (1, 4) else (middle, new)
            enforced = (active >> value) & 1
            targets = 0 if enforced and tail > head else 1 << (4*new if phase == 5 else q)
        rows.append(targets)
    return tuple(rows)


def local_relations(raw, n):
    if len(raw) != 24 + 4*n or any(bit not in (0, 1) for bit in raw):
        raise ValueError('expected all indexed raw guard bits')
    steps = []
    j = 24
    for i in range(n):
        active = 0
        if i % 3:
            # The predecessor emits the negatively padded slot first, then the positive one.
            active = 2 * int(all(raw[j:j+3])) + int(all(raw[j+3:j+6]))
            j += 6
        steps.append((transition(i % 6, active, 0), transition(i % 6, active, 1)))
    return steps


def solve(middles, pads, raw, fixed=None):
    """Return boundaries and occurrence values, or None; reject inputs outside the promise."""
    word = named_word(middles, pads)
    fixed = {} if fixed is None else fixed
    mate, _ = match_positions(word, fixed)
    steps = local_relations(raw, len(word))
    zero = (0,)*8
    for i, name in enumerate(word):
        if name in fixed:
            a, b = steps[i]
            steps[i] = (a, zero) if fixed[name] == 0 else (zero, b)
    # Each record stores its relation and the constant-size data for witness reconstruction.
    records = [(IDENTITY, 'empty', ())]

    def add(relation, operation, arguments):
        records.append((relation, operation, arguments))
        return len(records)-1

    def append(prefix, suffix):
        if not prefix:
            return suffix
        return add(compose(records[prefix][0], records[suffix][0]), 'append', (prefix, suffix))

    frames = []
    segment = 0
    for i, partner in enumerate(mate):
        if partner > i:
            frames.append(segment)
            segment = 0
        elif partner < 0:
            node = add(union(*steps[i]), 'single', (i,))
            segment = append(segment, node)
        else:
            interior = records[segment][0]
            alternatives = [compose(compose(steps[partner][v], interior), steps[i][v]) for v in (0, 1)]
            node = add(union(*alternatives), 'pair', (partner, segment, i))
            segment = append(frames.pop(), node)

    starts = (4,) if all(raw[:12]) else (0, 4)
    ends = (0,) if all(raw[12:24]) else (0, 4)
    allowed = records[segment][0]
    pair = next(((a, b) for a in starts for b in ends if allowed[a] & (1 << b)), None)
    if pair is None:
        return None
    states = [None] * (len(word)+1)
    values = [None] * len(word)
    work = [(segment, *pair)]
    while work:
        node, a, b = work.pop()
        _, operation, args = records[node]
        if operation == 'append':
            left, right = args
            middle = next(u for u in STATES if records[left][0][a] & (1 << u) and records[right][0][u] & (1 << b))
            work.extend(((right, middle, b), (left, a, middle)))
        elif operation == 'single':
            i, = args
            values[i] = next(v for v in (0, 1) if steps[i][v][a] & (1 << b))
            states[i], states[i+1] = a, b
        elif operation == 'pair':
            i, inside, j = args
            v, u, t = next((v, u, t) for v in (0, 1) for u in STATES for t in STATES
                           if steps[i][v][a] & (1 << u) and records[inside][0][u] & (1 << t)
                           and steps[j][v][t] & (1 << b))
            values[i] = values[j] = v
            states[i], states[i+1], states[j], states[j+1] = a, u, t, b
            work.append((inside, u, t))
    if not word:
        states[0] = pair[0]
    return [states[i] >> 2 for i in range(0, len(states), 6)], values


def solve_with_exceptions(middles, pads, raw):
    removed = find_removal(named_word(middles, pads))
    for values in product((0, 1), repeat=len(removed)):
        witness = solve(middles, pads, raw, dict(zip(removed, values)))
        if witness is not None:
            return witness
    return None


def raw_layout(middles, pads, base):
    """Rename originals in the predecessor's literal CNF, independently of the interval evaluator."""
    stages = len(middles)//2
    groups = base.strict_groups(base.source(stages))
    clauses, _, guards = base.guarded_formula(groups)
    first = {}
    rename = {}
    hidden = []
    for k, middle in enumerate(middles):
        mi = stages + 2 + k
        pi = [abs(groups[2+2*k+j][0][-1]) for j in (0, 1)]
        for var, name in zip((mi, *pi), (('m', middle), ('p', pads[2*k]), ('p', pads[2*k+1]))):
            rename[var] = first.setdefault(name, var)
            hidden.append(rename[var])
    formula = [[(1 if lit > 0 else -1) * rename.get(abs(lit), abs(lit)) for lit in c] for c in clauses]
    return formula, guards, hidden


def packed(flags, start=True, end=True):
    raw = bytearray([int(start)]*12 + [int(end)]*12)
    for flag in flags:
        raw.extend([int(bool(flag & 2))]*3 + [flag & 1]*3)
    return raw


def compare(middles, pads, vectors, base, solver_type, reader=solve):
    clauses, guards, hidden = raw_layout(middles, pads, base)
    yes = no = 0
    with solver_type(name='g3', bootstrap_with=clauses) as oracle:
        for raw in vectors:
            answer = reader(middles, pads, raw)
            fixed = [v if bit else -v for v, bit in zip(guards, raw)]
            assert oracle.solve(assumptions=fixed) == (answer is not None)
            if answer is None:
                no += 1
            else:
                x, values = answer
                model = [i+1 if v else -(i+1) for i, v in enumerate(x)]
                model.extend(var if value else -var for var, value in zip(hidden, values))
                assert oracle.solve(assumptions=fixed+model)
                yes += 1
    return {'sat_witnesses': yes, 'unsat': no, 'raw_clauses': len(clauses)}


def small_partitions(n, prefix=()):
    if len(prefix) == n:
        yield prefix
    else:
        for name in range(max(prefix, default=-1)+2):
            if prefix.count(name) < 2:
                yield from small_partitions(n, prefix+(name,))


def deep_layout(pair_layers):
    stages = 2*pair_layers
    mids = list(range(2*stages))
    pads = list(range(4*stages))
    for i in range(pair_layers):
        opposite = stages-1-i
        mids[2*opposite+1] = mids[2*i]
        pads[4*opposite] = pads[4*i]
    return mids, pads


def upper_schedule(labels):
    """Put a prescribed paired word only on upper middles, keeping other names fresh."""
    offset = max(labels)+1
    middles = [name for i, upper in enumerate(labels) for name in (upper, offset+i)]
    return middles, list(range(4*len(labels)))


def exception_checks(base, solver_type):
    crossed = ([0,0], [0,1,0,2])
    word = named_word(*crossed)
    assert find_removal(word, 0) is None
    assert len(find_removal(word)) == 1
    effective = (packed(flags) for flags in product(range(4), repeat=4))
    all_masks = compare(*crossed, effective, base, solver_type, solve_with_exceptions)

    t = 17
    star = upper_schedule([*range(t), t, *reversed(range(t)), t])
    assert find_removal(named_word(*star)) == (2*t,)
    # The outer B meets the source and the boundary just before the last stage.
    # The final lower branch leads from there to the sink.
    flags = [0]*len(star[1])
    for pos in (0, len(flags)-7, len(flags)-2, len(flags)-1):
        flags[pos] = 3
    live = packed(flags)
    split = bytearray(live)
    split[24] = 0
    star_cases = compare(*star, [live, split], base, solver_type, solve_with_exceptions)
    assert (star_cases['sat_witnesses'], star_cases['unsat']) == (1, 1)

    clique = upper_schedule([0,1,2,0,1,2])
    clique_word = named_word(*clique)
    assert find_removal(clique_word, 1) is None
    assert len(find_removal(clique_word, 2)) == len(find_removal(clique_word)) == 2
    rng = Random(17321)
    vectors = [packed([3]*len(clique[1])), packed([0]*len(clique[1]))]
    vectors.extend(packed([rng.randrange(4) for _ in clique[1]]) for _ in range(128))
    clique_cases = compare(*clique, vectors, base, solver_type, solve_with_exceptions)
    return {'single_joint_crossing_all_half_masks': all_masks,
            'star_crossings': t, 'star_minimum_removed': 1, 'star_raw': star_cases,
            'three_pair_clique_minimum_removed': 2, 'three_pair_clique_raw': clique_cases}


def exercise(base, solver_type):
    results = {}
    small = {'nested_layouts': 0, 'interleaving_layouts': 0, 'sat_witnesses': 0, 'unsat': 0}
    for mids in small_partitions(2):
        for pads in small_partitions(4):
            try:
                match_positions(named_word(mids, pads))
            except ValueError:
                small['interleaving_layouts'] += 1
                continue
            small['nested_layouts'] += 1
            vectors = (packed(flags, s, t) for flags in product(range(4),repeat=4) for s,t in product((0,1), repeat=2))
            count = compare(mids, pads, vectors, base, solver_type)
            for key in ('sat_witnesses', 'unsat'):
                small[key] += count[key]
    results['all_one_stage_layouts_and_effective_guards'] = small
    results['empty_schedule_endpoint_combinations'] = compare([],[],[packed([],s,t) for s,t in product((0,1),repeat=2)],base,solver_type)
    mids, pads = deep_layout(1)
    all_two_stage = (packed(flags) for flags in product(range(4), repeat=8))
    results['next_size_all_65536_half_masks'] = compare(mids, pads, all_two_stage, base, solver_type)

    crossed = ([0,0], [0,1,0,2])
    vector = packed([1,3,2,0])
    try:
        solve(*crossed, vector)
    except ValueError as exc:
        assert 'interleave' in str(exc)
    else:
        raise AssertionError('joint interleaving was accepted')
    clauses, guards, _ = raw_layout(*crossed, base)
    with solver_type(name='g3', bootstrap_with=clauses) as oracle:
        for raw, expected in ((vector, False), (packed([0,0,0,0]), True)):
            assert oracle.solve(assumptions=[g if b else -g for g,b in zip(guards,raw)]) == expected
    assert compare([0,1], crossed[1], [vector], base, solver_type)['sat_witnesses']==1
    assert compare(crossed[0], [0,1,2,3], [vector], base, solver_type)['sat_witnesses']==1
    for mids,pads in (([0]*4,list(range(8))),([0,1], [0,0,0,1])):
        try:
            solve(mids,pads,packed([0]*len(pads)))
        except ValueError as exc:
            assert 'more than twice' in str(exc)
        else:
            raise AssertionError('third occurrence was accepted')
    results['promise_controls'] = {'crossed_unsat': True, 'same_crossed_layout_sat': True, 'each_role_split_restores_sat': True, 'third_occurrence_rejections': 2}

    rng = Random(20261115)
    larger = {}
    for stages in (4, 6, 8, 9):
        mids,pads = deep_layout(stages//2)
        if stages % 2:
            mids.extend(range(len(mids), len(mids)+2))
            pads.extend(range(len(pads), len(pads)+4))
        def varied():
            for k in range(384):
                raw = packed([rng.randrange(4) for _ in pads])
                for i in range(24,len(raw)):
                    if not raw[i] and rng.randrange(5)==0:
                        raw[i]=1
                if k%8==0:
                    raw[rng.randrange(24)]=0
                yield raw
        larger[str(stages)] = compare(mids,pads,varied(),base,solver_type)
    results['mixed_raw_vectors_by_stages'] = larger
    layers = 600
    mids,pads = deep_layout(layers)
    depth = match_positions(named_word(mids,pads))[1]
    assert depth == 2*layers
    flags = [0]*len(pads)
    flags[0]=flags[-1]=3
    united = packed(flags)
    broken = bytearray(united)
    broken[24]=0
    deep = compare(mids,pads,[united,broken],base,solver_type)
    assert (deep['sat_witnesses'], deep['unsat']) == (1,1)
    results['unbounded_depth_family_replay'] = {'stages':2*layers, 'open_pairs_at_midpoint':depth, **deep}
    results['conditioning_on_cover_of_alternations'] = exception_checks(base, solver_type)
    return results


if __name__ == '__main__':
    try:
        from pysat.solvers import Solver
    except ImportError:
        venv = BASE.parents[3] / '.venv' / 'bin' / 'python'
        if venv.is_file() and Path(sys.prefix) != venv.parents[1]:
            import os
            os.execv(str(venv), [str(venv), '-B', __file__])
        raise
    spec = spec_from_file_location('literal_guarded_route_source', BASE)
    base = module_from_spec(spec)
    spec.loader.exec_module(base)
    result = exercise(base, Solver)
    result["status"] = "passed"
    print(json.dumps(result, indent=2, sort_keys=True))
