"""Raw record recounts, rational tests and independently constructed controls."""

import gzip
import hashlib
import itertools
import json
import math
import random
from bisect import bisect_right
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

import networkx as nx
from pysat.solvers import Solver

from c_checks_growth import State, births_for, finish, start_from_counts, state_hash


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET = 'MADE-COPIER-20261125-001C'
DATA = ROOT / 'research' / TICKET
RAW = next((ROOT / 'artifacts' / TICKET).glob('*-E001_*'))
RENAMINGS = ('none', 'reversed', 'perm', 'shift', 'knots', 'distinctions')
ATLAS = nx.graph_atlas_g()


def read_json(path):
    return json.loads(path.read_bytes())


def lines(path):
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rt') as f:
        yield from (json.loads(line) for line in f if line.strip())


@lru_cache(maxsize=2048)
def fisher(a, n, b, m, both=False):
    """Fixed-margin tables carry integer weights; the two-sided tail sums ties."""
    k = a + b
    lo, hi = max(0, k - m), min(k, n)
    observed = math.comb(n, a) * math.comb(m, b)
    weight = math.comb(n, lo) * math.comb(m, k - lo)
    numerator = 0
    for x in range(lo, hi + 1):
        in_tail = weight <= observed if both else x >= a
        if in_tail:
            numerator += weight
        if x < hi:
            weight = weight * (n - x) * (k - x) // ((x + 1) * (m - k + x + 1))
    return Fraction(numerator, math.comb(n + m, k))


def matched_p(losses, gains):
    discordant = losses + gains
    low = min(gains, losses)
    mass = sum(math.comb(discordant, x) for x in range(low + 1))
    return min(Fraction(1), Fraction(2 * mass, 1 << discordant))


def rename(state, how, sid):
    n = len(state.places)
    d = len(state.holders)
    names, ds = list(range(n)), list(range(d))
    if how == 'reversed':
        names.reverse()
        ds.reverse()
    elif how in ('perm', 'knots', 'distinctions'):
        rng = random.Random(f'C|rename|{sid}|{how}')
        if how in ('perm', 'knots'):
            rng.shuffle(names)
        if how in ('perm', 'distinctions'):
            rng.shuffle(ds)
    elif how == 'shift':
        ds = ds[1:] + ds[:1]
    rows = tuple(frozenset(ds[v] for v in state.places[u]) for u in names)
    return State(rows, state.parents, state.made, state.kinds)


def enumerate_histories(state, depth, treatment, parity):
    end = Counter()
    n = 0

    def visit(current, t, weight):
        nonlocal n
        if t == depth:
            n += 1
            end[state_hash(current)] += weight
            return
        prep = births_for(current, treatment, 'MET')
        trials = [cs or [None] for _, _, cs in prep[0]]
        p = weight / math.prod(map(len, trials))
        for choice in itertools.product(*trials):
            nxt = finish(current, t + 1, 'FLOOR1', parity, prep, choice)
            visit(nxt, t + 1, p)

    visit(state, 0, Fraction(1))
    return n, end


def r7():
    groups = defaultdict(dict)
    for row in lines(RAW / 'R7.jsonl'):
        key = (row['label'], row['start'], row['law'])
        assert row['renaming'] not in groups[key] and 'error' not in row
        row['dist'] = {k: Fraction(v) for k, v in row['dist'].items()}
        assert sum(row['dist'].values()) == 1 and all(v > 0 for v in row['dist'].values())
        groups[key][row['renaming']] = row
    flags = Counter()
    history_flags = Counter()
    depths = Counter()
    hist = single = one_hash = strict = renamed_total = 0
    reruns = []
    for (_, sid, law), rows in sorted(groups.items()):
        ref = rows['none']
        assert set(rows) == set(RENAMINGS)
        assert all(row['dist'] == ref['dist'] and row['depth'] == ref['depth']
                   and row['histories'] == ref['histories'] for row in rows.values())
        renamed_total += len(rows) - 1
        hist += ref['histories']
        single += ref['histories'] == 1
        one_hash += len(ref['dist']) == 1
        strict += len(ref['dist']) == 1 and ref['histories'] > 1
        depths[ref['depth']] += 1
        for name, count in ref['flags'].items():
            flags[name] += count > 0
            history_flags[name] += count
        if sid == 'n3-g6-122' and law in {
                'FLOOR1/CANCEL-WAIT/RELEASE/MET/parity/T1',
                'FLOOR1/CANCEL-WAIT/RELEASE/MET/nae/T1',
                'FLOOR1/CANCEL-RETIRE/RELEASE/MET/parity/T1'}:
            for kind in RENAMINGS:
                initial = rename(start_from_counts(ATLAS[6], [1, 2, 2]), kind, sid)
                n, classes = enumerate_histories(initial, ref['depth'], law.split('/')[1],
                                                  law.split('/')[4] == 'parity')
                assert n == rows[kind]['histories'] and classes == rows[kind]['dist']
            reruns.append({'law': law, 'start': sid, 'original_histories': n,
                           'all_six_hash_distributions_reproduced': True})
    return {'complete': len(groups), 'renamed_comparisons': renamed_total,
            'distinct_starts': len({key[1] for key in groups}), 'depth': depths, 'histories': hist,
            'single_history': single, 'single_terminal_hash': one_hash,
            'multiple_histories_with_one_hash': strict, 'checks_with': flags,
            'histories_with': history_flags, 'small_exhaustive_regrowth': reruns}


def r8():
    rows = defaultdict(dict)
    capped = stopped = 0
    total = 0
    for r in lines(RAW / 'R8.jsonl.gz'):
        total += 1
        assert 'error' not in r and r['has_pair'] == any(r['pairs_by_s'].values())
        key = (r['law'], r['index'])
        assert r['renaming'] not in rows[key]
        rows[key][r['renaming']] = r['has_pair']
        capped += max(r['pairs_by_s'].values(), default=0) > 8
        stopped += r['stop'] is not None
    out = {'growths': total, 'stopped_at_a_bound': stopped, 'growths_over_eight_pairs': capped}
    laws = sorted({k[0] for k in rows})
    starts = read_json(DATA / 'starts_c.json')['starts']
    for select in ('all', 'parity_eligible'):
        ix = sorted({k[1] for k in rows
                     if select == 'all' or not starts[k[1]]['set_aside_parity']})
        trials, pooled = [], []

        def test(laws_here, kind, threshold):
            vals = [(rows[law, i]['none'], rows[law, i][kind]) for law in laws_here for i in ix]
            n = len(vals)
            a, b = map(sum, zip(*vals))
            p = fisher(a, n, b, n, True)
            diff = Counter(vals)
            losses, gains = diff[(True, False)], diff[(False, True)]
            pm = matched_p(losses, gains)
            k = a + b
            minimum = fisher(min(n, k), n, max(0, k - n), n, True)
            return {'renaming': kind, 'start_count': a, 'renamed_count': b, 'per_side': n,
                    'fisher_p': float(p), 'reject': p <= threshold, 'losses': losses, 'gains': gains,
                    'paired_p': float(pm), 'paired_reject': pm <= threshold,
                    'can_reject_given_total_hits': minimum <= threshold,
                    'can_reject_given_discordance': matched_p(losses + gains, 0) <= threshold}

        for kind in RENAMINGS[1:]:
            for law in laws:
                tr = test([law], kind, Fraction(1, 4200))
                trials.append(dict(tr, law=law))
            pooled.append(test(laws, kind, Fraction(1, 100)))
        out[select] = {'starts': len(ix), 'laws': len(laws), 'tests': len(trials),
                       'rejections': sum(p['reject'] for p in trials),
                       'min_fisher_p': min(p['fisher_p'] for p in trials),
                       'min_paired_p': min(p['paired_p'] for p in trials),
                       'matched_rejections': sum(p['paired_reject'] for p in trials),
                       'fisher_could_reject_given_total_hits': sum(p['can_reject_given_total_hits'] for p in trials),
                       'matched_could_reject_given_discordance': sum(p['can_reject_given_discordance'] for p in trials),
                       'tests_with_no_discordance': sum(p['gains'] + p['losses'] == 0 for p in trials),
                       'pooled': pooled}
        expected = read_json(RAW / 'R8.json')['starts read' if select == 'all' else 'starts read, not set aside']
        compare = {(t['law'], t['renaming']): t for t in expected['tests']}
        for t in trials:
            old = compare[t['law'], t['renaming']]
            assert abs(t['fisher_p'] - old['p']) < 1e-11
            assert old['start'] == [t['start_count'], t['per_side']] and old['rejected'] == t['reject']
            assert old['renamed'] == [t['renamed_count'], t['per_side']]
        for new, old in zip(pooled, expected['pooled'], strict=True):
            assert abs(new['fisher_p'] - old['p']) < 1e-11 and new['renaming'] == old['renaming']
    return out


def census(limit=None):
    registered = read_json(DATA / 'starts_c.json')
    entries = registered['starts']
    ordered = []
    subtotal, labels, labels_kept = Counter(), Counter(), Counter()
    excluded, nae_flips, nae_local = Counter(), 0, 0
    for g, graph in enumerate(ATLAS):
        n = len(graph)
        if n not in (3, 4, 5) or not nx.is_connected(graph):
            continue
        auts = list(nx.isomorphism.GraphMatcher(graph, graph).isomorphisms_iter())
        admissible = [range(max(0, 3 - graph.degree(u)), 4) for u in range(n)]
        for h in itertools.product(*admissible):
            if limit is not None and len(ordered) >= limit:
                break
            if not any(h):
                continue
            orbit = {tuple(h[p[i]] for i in range(n)) for p in auts}
            if h != min(orbit):
                continue
            # Each permutation of the knot names contributes once modulo its stabilizer.
            weight = math.factorial(n) * len(orbit) // len(auts)
            state = start_from_counts(graph, h)
            rows = [sum(1 << d for d in s) for s in state.places]
            span = {0}
            for v in rows:
                span |= {w ^ v for w in span}
            bad = any(chk != row and chk & ~row == 0 for row in rows for chk in span - {0})
            entry = dict(id=f"n{n}-g{g}-" + ''.join(map(str, h)), n=n, g=g, loose=list(h),
                         labelled=weight, set_aside_parity=bad)
            assert entry == entries[len(ordered)]
            ordered.append(entry['id'])
            subtotal[n] += 1
            labels[n] += weight
            if bad:
                excluded[n] += 1
            else:
                labels_kept[n] += weight
            # Deleting d from every clause has a solution exactly when some two
            # allowed global states differ in d alone. That rules out every tie involving d.
            rows = [tuple(d + 1 for d in row) for row in state.places]
            for d in range(1, len(state.holders) + 1):
                shorter = [[v for v in p if v != d] for p in rows]
                clauses = shorter + [[-v for v in p] for p in shorter]
                with Solver(bootstrap_with=clauses) as solver:
                    assert solver.solve()
                nae_flips += 1
            if bad:
                clauses = list(rows) + [[-v for v in p] for p in rows]
                with Solver(bootstrap_with=clauses) as solver:
                    for p in rows:
                        for vs in itertools.product((-1, 1), repeat=len(p)):
                            assignment = [v * val for v, val in zip(p, vs)]
                            assert solver.solve(assumptions=assignment) == (len(set(vs)) > 1)
                        nae_local += 1
    if limit is None:
        assert len(ordered) == len(entries)
        perm = random.Random('C|order').sample(ordered, len(ordered))
        assert perm == registered['registered_samples']['order']['ids']
        assert [s for s in perm if s.startswith('n5-')][:300] == registered['registered_samples']['R5 five-knot starts']
    return {'by_size': subtotal, 'labelled': labels, 'labelled_parity_eligible': labels_kept,
            'parity_set_aside': excluded, 'individual_nae_flips_witnessed': nae_flips,
            'full_nae_local_projections_on_set_aside_starts': nae_local, 'order_compared': limit is None}


def counterexamples():
    start = start_from_counts(ATLAS[6], [1, 2, 2])
    original, _, _ = births_for(start, 'CANCEL-RETIRE', 'MET')
    swapped = frozenset({3, 4})
    assert set(start.usable[1]) == swapped
    # The prescribed swap takes the old distinction used by the only two-parent
    # birth to the one used by an offshoot. As sets of places, the start is unchanged.
    moved = lambda d: 7 - d if d in swapped else d
    ren = State(tuple(frozenset(map(moved, p)) for p in start.places),
                start.parents, start.made, start.kinds)
    plans = births_for(ren, 'CANCEL-RETIRE', 'MET')[0]
    assert plans == original
    joins = [p for p in plans if len(p[0]) == 2]
    assert len(joins) == 1 and 3 in joins[0][1] and 4 not in joins[0][1]

    start4 = start_from_counts(ATLAS[18], [0, 1, 2, 3])
    plans4, _, _ = births_for(start4, 'CANCEL-RETIRE', 'MET')
    target = [p for p in plans4 if p[0] == (2,)]
    assert len(target) == 1
    candidates = target[0][2]
    assert candidates == [0, 2, 4]
    assert [len(start4.holders[d]) for d in candidates] == [2, 2, 2]
    # Exact counts of 53-bit random() variates in each interval used by choices.
    M = 1 << 53
    def lower_bound(rank):
        lo, hi = 0, M
        while lo < hi:
            k = (lo + hi) // 2
            dest = bisect_right((2, 4, 6), (k / M) * 6.0, 0, 2)
            if dest < rank:
                lo = k + 1
            else:
                hi = k
        return lo
    counts = [lower_bound(r + 1) - lower_bound(r) for r in range(3)]
    assert sum(counts) == M and counts[0] == counts[1] + 1
    return {'fixed_original_distinctions': {'start': 'n3-g6-122', 'swap': sorted(swapped),
                                           'join_parents': joins[0][0], 'join_inputs_before_takes': joins[0][1],
                                           'offshoot_using_4': [list(p[0]) for p in plans if 4 in p[1]]},
            'holder_weighting': {'start': 'n4-g18-0123',
                                 'law': 'FLOOR1/CANCEL-RETIRE/RELEASE/MET/parity/T2',
                                 'parent_of_unique_offshoot': 2, 'candidates': candidates,
                                 'original_holders': [sorted(start4.holders[d]) for d in candidates],
                                 'candidate_slot_counts': counts, 'denominator': M,
                                 'difference_after_interchanging_first_two_labels': '1/9007199254740992'}}


def gate_calls():
    archived = read_json(RAW / 'test_mcc.json')['tests']
    def recorded(prefix):
        item, = [v['info'] for k, v in archived.items() if k.startswith(prefix)]
        return item
    rng = random.Random('x')
    uniform = [c[rng.randrange(len(c))] for c in ([3, 5, 9], [7], [1, 2], [4])]
    assert uniform == recorded('T1 sampler:')['got']
    rng = random.Random('y')
    holder = [rng.choices(c, weights=[3] * len(c))[0] for c in ([0, 1], [0], [1, 0])]
    assert holder == recorded('T2 sampler: choices')['got']
    rng = random.Random('z')
    successes = sum(rng.choices([0, 1], weights=[3, 2])[0] == 0 for _ in range(20000))
    assert successes / 20000 == recorded('T2 sampler: chance')
    ordered = [(i, j) for i in range(10) for j in range(10) if i != j]
    kept = sorted(random.Random('SEED|P|2').sample(ordered, 8))
    assert list(map(list, kept)) == recorded('pair rule: more than eight')['got']
    expected = read_json(RAW / 'gate_R0.json')['engine_hashes']
    for key, digest in expected.items():
        base = 'MADE-COPIER-20261125-001A' if key == 'mc.py' else 'PARTS-MEET-AGAIN-20261124-001A'
        engine, = (ROOT / 'experiments' / base).glob('*-E001_*/' + key)
        assert hashlib.sha256(engine.read_bytes()).hexdigest() == digest
    return {'engine_sources_matching_recorded_digests': sorted(expected), 'uniform_draws': uniform,
            'holder_draws': holder, 'holder_3_versus_2': [successes, 20000],
            'selected_pairs_from_ninety': kept}
