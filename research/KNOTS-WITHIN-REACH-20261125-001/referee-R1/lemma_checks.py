"""Check the five lemmas using new complete rounds, exact state counts and frozen rows."""

import argparse
import gzip
import json
import resource
from collections import Counter, defaultdict, deque
from functools import lru_cache
from itertools import combinations, islice
from math import comb
from pathlib import Path
from time import monotonic

from regrow_engine import Growth, connected_parts

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET = 'KNOTS-WITHIN-REACH-20261125-001A'
INPUT = ROOT / 'research' / TICKET
RAW = ROOT / 'artifacts' / TICKET / (TICKET + '-E001_knots_within_reach')
resource.setrlimit(resource.RLIMIT_AS, (1_400_000_000, 1_400_000_000))


def search(neighbors, sources, limit=None):
    steps = {s: 0 for s in sources}
    pending = deque(steps)
    while pending:
        u = pending.popleft()
        d = steps[u] + 1
        if limit is not None and d > limit:
            continue
        for v in neighbors[u]:
            if v not in steps:
                steps[v] = d
                pending.append(v)
    return steps


def cumulative(steps, limit):
    shell = Counter(steps.values())
    total = 0
    out = []
    for r in range(limit + 1):
        total += shell[r]
        out.append(total)
    return out


def sizes(neighbors, source, upto):
    return cumulative(search(neighbors, [source], upto), upto)


def holder_neighbors(places):
    owners = defaultdict(list)
    adj = [set() for _ in places]
    for u, row in enumerate(places):
        for bit in row:
            for v in owners[bit]:
                adj[u].add(v)
                adj[v].add(u)
            owners[bit].append(u)
    return adj


def parent_neighbors(parents):
    adj = [set() for _ in parents]
    for u, row in enumerate(parents):
        for v in row:
            adj[u].add(v)
            adj[v].add(u)
    return adj


def graph_run(stars, law, hold, t0=40, horizon=10):
    growth = Growth(stars, law, hold=hold)
    n0 = len(stars)
    def within_sample():
        m = len(growth.members)
        loose_counts = list(map(len, growth.members.values()))
        if m <= 128 and sum(loose_counts) <= 512:
            return True
        if m > 1024 or max(loose_counts,default=0) > 3:
            return False
        return max(map(len,growth.roster().neighbors.values()),default=0) <= 6

    for _ in range(t0):
        if not within_sample() or not growth.step():
            break
    snap_t = growth.round
    before = holder_neighbors(growth.places)
    start_d = search(before, range(n0))
    members = set(growth.members)
    if members:
        m = min(start_d[u] for u in members)
        eligible = [u for u in range(n0, len(before)) if 4 * start_d[u] <= m and u not in members]
        # Deterministic first eight; a different sample from the author's seeded eight.
        chosen = list(range(n0)) + eligible[:8]
        reference = {u: sizes(before, u, m - start_d[u]) for u in chosen}
    for _ in range(horizon):
        if not within_sample() or not growth.step():
            break
    g = holder_neighbors(growth.places)
    parents = parent_neighbors(growth.parents)
    s = search(g, range(n0))
    assert all(g[u] - ({v for v in g[u] if v < n0} if u < n0 else set()) == parents[u] for u in range(len(g)))
    assert search(parents, range(n0)) == s
    synced = law not in ('L1', 'L2', 'L5') and not hold
    witness = next(([p, u, growth.birth_rounds[p], growth.birth_rounds[u], s[u]]
                    for u, ps in enumerate(growth.parents) for p in ps
                    if growth.birth_rounds[p] != growth.birth_rounds[u] - 1), None)
    if synced:
        assert witness is None and all(s[u] == t for u, t in enumerate(growth.birth_rounds))
    original = holder_neighbors(stars)
    furthest = max(s.values())
    all_starts = cumulative(s, furthest)
    for u in range(n0):
        e = max(search(original, [u]).values())
        hs = sizes(g, u, furthest)
        assert all((all_starts[r - e] if r >= e else 0) <= h <= all_starts[r] for r, h in enumerate(hs))
    f = int(bool(members) and growth.round > snap_t)
    if f:
        assert all(sizes(g, u, len(h) - 1) == h for u, h in reference.items())
    return dict(E=1, R=1, R_round=synced, F=f, F_full_horizon=int(f and growth.round == snap_t+horizon),
                stopped_by_referee_size=int(not within_sample()),
                F_knots=len(reference) if f else 0, example_of_older_parent=witness, final_knots=len(g))


def original_cases():
    stars = [[0, 1, 2], [0, 3, 4]]
    ordinary = Growth(stars)
    ordinary.step()
    h = holder_neighbors(ordinary.places)
    p = parent_neighbors(ordinary.parents)
    u = next(i for i, ps in enumerate(ordinary.parents) if ps == (0,))
    E = {'from_first_child_of_first_start': [sizes(h, u, 3), sizes(p, u, 3)],
         'holder_steps_to_other_start': search(h, [u])[1], 'parent_reaches_other_start': 1 in search(p, [u])}
    assert E['holder_steps_to_other_start'] == 2 and not E['parent_reaches_other_start']
    # A single extra take of the two starts' already-shared distinction adds a nonparent holder step.
    extra = holder_neighbors(stars + [[0, 1, 5]])
    assert 1 in extra[2] and 1 not in parent_neighbors([[], [], [0]])[2]
    # A local additional take reaches a nonmember. Compare the protected range under the two rules.
    before = [[0, 1, 2], [2, 3, 4], [4, 5, 6]]
    f0 = sizes(holder_neighbors(before), 0, 2)
    f_clean = sizes(holder_neighbors(before + [[6, 7, 8]]), 0, 2)
    f_extra = sizes(holder_neighbors(before + [[2, 6, 7]]), 0, 2)
    assert f0 == f_clean and f0 != f_extra
    # One parent relation skips a round when a live knot is allowed to keep a distinction.
    return {'E': E, 'E_extra_take': {'nonparent_met': 1, 'birth': 2},
            'F_local_attachment_control': {'only_usable_loose_distinction':6, 'old_loose_distinctions_barred':[0,1,3,5],
                                           'start_knot':0, 'member_at_stage':2, 's_min': 2, 'before': f0,
                                           'ordinary_attachment': f_clean, 'additional_take': f_extra}}


def plus_one(pilot):
    # A live start and an unchanged single roster test the strongest registered reading.
    # Each pair of successive members of the bare ring shares one distinction and each has two loose ones.
    n = 67
    ring = [[(u - 1) % n, u, n + 2*u, n + 2*u + 1] for u in range(n)]
    places = [row.copy() for row in ring]
    next_bit = 3*n

    def connect(u, v, count=2):
        nonlocal next_bit
        for _ in range(count):
            places[u].append(next_bit)
            places[v].append(next_bit)
            next_bit += 1

    layers = []
    for d in range(32):
        layer = []
        for _ in range(comb(d+2, 2)):
            layer.append(len(places))
            places.append([])
        if layers:
            for i, u in enumerate(layer):
                connect(layers[-1][0], u)
                connect(u, layer[(i+1) % len(layer)])
        layers.append(layer)
    connect(0, layers[0][0], 1)
    growth = Growth(places, 'L0')
    # For a state fixed on any one start knot, each other added knot has a pair of its own
    # shared distinctions untouched by that state. Give every untouched pair values 0 and 1.
    # Each other ring knot can use its two loose distinctions the same way. Thus every
    # nonconstant state of each start knot extends to an allowed state of the entire start.
    assert all(len(k) >= 3 for k in places)
    assert all(len(b) <= 2 for b in growth.holders.values())
    for u in range(n,len(places)):
        partners = Counter(v for d in places[u] for v in growth.holders[d] if v != u and v >= n)
        assert sum(q >= 2 for q in partners.values()) >= 2
    upto = 1 if pilot else 32
    observations = []
    for t in range(upto + 1):
        roster = growth.roster()
        assert sorted(map(len, connected_parts(roster.neighbors))) == [67]
        assert set(map(len, growth.members.values())) == {2} and not growth.barred
        assert {len(m) for m in roster.met_sets} == {2}
        assert {len(neigh) for neigh in roster.neighbors.values()} == {2}
        observations.append(len(growth.members))
        if t < upto:
            assert growth.step() == n
    adj = holder_neighbors(growth.places)
    H = sizes(adj, 0, upto)
    P = sizes(growth.roster().neighbors, min(growth.members), upto)
    assert H == [2*r*r + 2*r + 1 + comb(r + 2, 3) for r in range(upto + 1)]
    assert P == [2*r + 1 for r in range(upto + 1)]
    from_start = search(adj, range(len(places)))
    assert min(from_start[u] for u in growth.members) == upto
    return dict(ordinary_not_all_equal=True, initial_live_knots=n, initial_knots=len(places),
                added_start_knots_have_no_loose_distinctions=True, layer_sizes=list(map(len, layers)),
                distinct_other_holders_carrying_a_pair_at_each_added_knot_at_least=2,
                rounds=upto, members_every_round=observations, one_part_every_round=True,
                minimum_steps_of_last_member=min(from_start[u] for u in growth.members),
                history_at_live_start=H, roster_at_one_round=P,
                history_formula='2r^2+2r+1+C(r+2,3)', roster_formula='2r+1')


@lru_cache(maxsize=32)
def columns(n):
    states = 1 << n
    full = (1 << states) - 1
    chars = []
    for q in range(n):
        stride = 1 << q
        mask = ((1 << stride) - 1) << stride
        length = stride * 2
        while length < states:
            mask |= mask << length
            length *= 2
        chars.append(mask)
    return full, chars


def state_truth(places, parity=False):
    n = max(d for k in places for d in k) + 1
    full, bits = columns(n)
    allowed = full
    for knot in places:
        either = 0
        every = full
        for d in knot:
            if parity:
                either ^= bits[d]
            else:
                either |= bits[d]
                every &= bits[d]
        allowed &= full ^ either if parity else either & (full ^ every)
    return full, bits, allowed


def split_places(places):
    occurs = Counter(d for row in places for d in row)
    return [[d for d in k if occurs[d] == 1] for k in places], [[d for d in k if occurs[d] > 1] for k in places]


@lru_cache(maxsize=3000)
def nae_check(places, members):
    full, bits, allowed = state_truth(places)
    Z = allowed.bit_count()
    assert Z > 0
    loose, shared = split_places(places)
    g = {}
    for u in members:
        if shared[u]:
            zero = one = allowed
            for d in shared[u]:
                zero &= full ^ bits[d]
                one &= bits[d]
            g[u] = (zero, one)
    pairs = measurements = 0
    for u,v in combinations(g, 2):
        z1, o1 = g[u]
        z2, o2 = g[v]
        gamma = ((z1 & z2) | (o1 & o2)).bit_count() - ((z1 & o2) | (o1 & z2)).bit_count()
        scale = ((1 << len(loose[u])) - 1) * ((1 << len(loose[v])) - 1)
        for a in loose[u]:
            for b in loose[v]:
                agreement = Z - 2 * (allowed & (bits[a] ^ bits[b])).bit_count()
                assert agreement * scale == gamma and abs(gamma) <= Z
                measurements += 1
        pairs += 1
    return pairs, measurements


def nae_enumeration(keys, laws):
    counts = Counter()
    for _, stars in keys:
        for law in laws:
            growth = Growth(stars, law)
            for t in range(5):
                if len(growth.holders) > 20:
                    break
                pairs, measurements = nae_check(tuple(map(tuple, growth.places)), tuple(sorted(growth.members)))
                counts['stages'] += 1
                counts['start_stages'] += (t == 0)
                counts['stages_with_a_pair'] += bool(pairs)
                counts['member_pairs'] += pairs
                counts['loose_distinction_pairs'] += measurements
                if t == 4 or growth.status != 'running':
                    break
                # The recorded stages include the terminal round even when it has no births.
                growth.step()
    return dict(counts)


def loose_parity(places):
    _, bits, allowed = state_truth(places, parity=True)
    loose, _ = split_places(places)
    loose = sorted(d for k in loose for d in k)
    Z = allowed.bit_count()
    projection = {tuple((s >> d) & 1 for d in loose) for s in range(1 << len(bits)) if (allowed >> s) & 1}
    pair_rho = {}
    for a,b in combinations(range(len(bits)), 2):
        diff = (allowed & (bits[a] ^ bits[b])).bit_count()
        assert diff in (0, Z // 2)
        pair_rho[f'{a},{b}'] = [diff, Z]
    return dict(places=places, loose=loose, loose_projection_count=len(projection), allowed=Z,
                pair_disagreements=pair_rho, loose_states=sorted(''.join(map(str,k)) for k in projection))


def hypothesis_controls():
    cases = {
        'connected_no_loose': [[0,1,2],[0,1,2]],
        'connected_one_loose': [[0,1,2],[0,1,2,3]],
        'connected_two_loose': [[0,1,2],[0,1,3]],
        'connected_three_loose': [[0,1,2],[0,1,3,4]],
        'one_distinction_with_three_holders': [[0,1,2],[0,1,3],[0,4,5]],
        'two_parts_of_the_holder_relation': [[0,1,2],[0,1,3],[4,5,6],[4,5,7]],
        'one_frozen_distinction_in_a_half_disagreement_pair': [[0,1,2],[0,1,2,3],[0,4,5]],
    }
    p = {label: loose_parity(places) for label,places in cases.items()}
    for label, data in list(p.items())[:4]:
        loose = data['loose']
        assert len(data['loose_states']) == (2 ** (len(loose)-1) if loose else 1)
        assert all(sum(map(int, row)) % 2 == 0 for row in data['loose_states'])
    for label, key in (('one_distinction_with_three_holders', '2,3'), ('two_parts_of_the_holder_relation','2,3')):
        assert p[label]['pair_disagreements'][key][0] == 0
    ex = p['one_frozen_distinction_in_a_half_disagreement_pair']
    projection = sorted({row[:2] for row in ex['loose_states']})
    assert projection == ['00','01'] and 2*ex['pair_disagreements']['3,4'][0] == ex['allowed']
    ex['pair_3_4_projection'] = projection
    # With one odd parity equation, an opposite pair appears; homogeneity matters.
    affine_states = [x for x in range(16) if sum((x>>i)&1 for i in (0,1,2)) % 2 == 0
                     and sum((x>>i)&1 for i in (0,1,3)) % 2 == 1]
    assert all(((v >> 2) ^ (v >> 3)) & 1 for v in affine_states)
    # State-wise reweighting can break Lemma N even on two knots sharing just one distinction.
    _, bits, legal = state_truth([[0,1,2],[0,3,4]])
    disagreement = (legal & (bits[1] ^ bits[3])).bit_count()
    total = legal.bit_count()
    weighted_total = 2*(total-disagreement) + disagreement
    assert 9*(total-2*disagreement) == total and 9*(weighted_total-2*disagreement) != weighted_total
    return dict(P=p, odd_rhs_pair_disagreement=[len(affine_states), len(affine_states)],
                N_two_knot_uniform=[total-2*disagreement,total],
                N_two_knot_agreements_weighted_twice=[weighted_total-2*disagreement,weighted_total],
                N_two_knot_gamma=[1,1], N_two_knot_scale=9)


def raw_recount(limit):
    out = {}
    for name in ['run1', 'run2', 'run4'] + ['run5_' + law for law in ('L0','L1','L3','L6','L7','swaps')]:
        cnt = Counter()
        with gzip.open(RAW / (name + '.jsonl.gz'), 'rt') as f:
            for line in islice(f,limit):
                rec = json.loads(line)
                cnt['rows'] += 1
                for l in ('E','R'):
                    if 'check_' + l in rec:
                        cnt[l + '_checks'] += 1
                        cnt[l + '_failures'] += len(rec['check_' + l])
                if name == 'run2':
                    for at in ('at_T','at_2T'):
                        fc = rec.get(at,{}).get('check_F',{})
                        if 'checked' in fc:
                            cnt['F_no_later_round'] += int(fc['checked'] == 0)
                            cnt['F_stage_comparisons'] += int(fc['checked'] > 0)
                            cnt['F_full_ten_rounds'] += int(fc['t2'] - fc['t'] == 10)
                            cnt['F_knots_compared'] += fc['checked']
                            cnt['F_failures'] += fc.get('n_bad',0)
                if name == 'run4':
                    if rec['knot_law'] == 'parity':
                        d = rec['check_P']
                        cnt['P_parity_rows'] += 1
                        cnt['P_stages'] += d['stages']
                        cnt['P_enumerated_stages'] += d['small_stages']
                        cnt['P_failures'] += d['bad']
                if name.startswith('run5'):
                    for stage in rec['stages']:
                        sm = stage.get('small')
                        if isinstance(sm, dict) and 'pairs' in sm:
                            cnt['N_stages'] += 1
                            cnt['N_eligible_stages'] += bool(sm['pairs'])
                            cnt['N_member_pairs'] += sm['pairs']
                            cnt['N_failures'] += sm['N_bad']
                            cnt['I_failures'] += sm['I_bad'] + (not sm['Z_ok'])
        out[name] = dict(cnt)
    return out


def main(pilot):
    named = json.loads((INPUT/'named_starts.json').read_text())['named_starts']
    cdata = json.loads((INPUT/'census_starts.json').read_text())
    keys = list(named.items()) + [(f'census:{i}', c['stars']) for i,c in enumerate(cdata) if c['n'] in (3,4)]
    laws = [('L0',False),('L1',False),('L3',False),('L6',False),('L7',False),('L9',False),('L3',True),('L6',True)]
    counts = Counter()
    waiting = {}
    # Same exact round bounds in both modes; the pilot uses the first case of each configuration.
    chosen = [(label, stars) for label,stars in named.items() if label=='Ring(5,3)'] if pilot else list(named.items())
    for label,stars in chosen:
        for law,hold in laws:
            row = graph_run(stars, law, hold)
            witness = row.pop('example_of_older_parent')
            if witness:
                waiting.setdefault(('HOLD' if hold else 'WAIT'), [label,law,witness])
            row.pop('final_knots')
            counts.update(row)
    small = [('three-knot', named['three-knot'])] if pilot else keys
    out = {
        'scope':'Taking-free NAE rounds regenerated from the frozen definitions; parity examples and NAE state counts independently enumerated. Raw comparison denominators counted separately.',
        'E_F_R_run_bounds':'Through round 50 or the last reached round. Continue while there are at most 128 members and at most 512 usable loose distinctions. Larger rosters are continued up to 1,024 members when each has at most three usable loose distinctions and at most six one-step roster neighbors. Compare the round 40 count through ten further completed rounds when available.',
        'E_F_R_independent_named_runs': dict(counts), 'R_older_parent_examples': waiting,
        'E_F_controls':original_cases(), 'fixed_roster_counterexample':plus_one(pilot),
        'N_independent_run0': nae_enumeration(small, ['L0','L1','L3','L6','L7']),
        'N_P_controls': hypothesis_controls(), 'saved_run_checks':raw_recount(1 if pilot else None),
        'run0_recorded': json.loads((RAW/'run0_checks.json').read_text())['checks']['counts'],
        'arguments_in_order': {
            'E': [
                'A taking-free birth uses a different loose distinction of each parent, then only fresh distinctions. The used distinction had one holder and now has two. It cannot be used again.',
                'Every new meeting is thus a parent meeting, and each parent is met. The only other meetings are between start knots. Removing these meetings can change counts from a made knot if its paths use them.'
            ],
            'F': [
                'Fix the old structure at round t with at least one member. Every old knot meeting a later birth was already a member at t, since an old unusable distinction never becomes usable under a taking-free law. No step adds a direct meeting between two old knots.',
                'On a path from u to a knot made later, the step into its first new knot leaves an old member m. The preceding path lies in the old structure and has length at least s_t(m) minus s_t(u), hence at least s_min minus s_t(u). The added step puts the new knot outside the kept range. Any path of length within the range uses old meetings throughout.',
                'This proves equality of all kept counts even if other shortest paths had shortened. It allows waiting, holding, closing and retiring. Taking an already-shared distinction breaks the old-member argument.'
            ],
            'R': [
                'A shortest path to any start knot can stop as soon as it reaches the first start knot. E makes its length the least number of parent steps to the start set.',
                'When all old members give up all usable distinctions in every completed round, every parent of a round-t birth was born in round t-1. This holds under release with stalling, offshoots or retirement, including fillers and closings. A chain of parents realizes t steps. Each meeting changes the birth round by at most one, so no shorter path exists.',
                'For a connected start and any later structure, s(v) is at most the holder steps from a specified start knot c, which are at most e(c)+s(v). Counting yields B(r-e(c)) <= H(c,r) <= B(r), with B of a negative argument zero. Only the synchronized case identifies B with cumulative births including the start.',
                'Nothing here relates the shape of finite history counts from c to the shape of roster counts. The verified ordinary-law example keeps exactly one unchanged roster and yields different powers than the proposed degree-plus-one rule.'
            ],
            'N': [
                'Condition on every shared distinction. The loose distinctions of different knots have independent uniform choices among their local allowed completions, including barred loose distinctions. If a knot has a shared 0 and a shared 1, every loose string completes it.',
                'When its shared bits are all 0, exactly the all-zero loose string is excluded; when they are all 1, exactly the all-one loose string is excluded. Therefore the mean of 2a-1 is g_u/(2^lambda_u-1). Multiply the two conditional means for distinct holders and average with the stage weighting to obtain the formula and its bound.',
                'The formula requires at least one shared and one loose distinction at each holder. The sharper numerator bound is |gamma(u,v)| <= min(Pr(u has equal shared places),Pr(v has equal shared places)). Reweighting agreements twice in the two-knot example breaks the displayed identity.'
            ],
            'P': [
                'Under homogeneous parity, bitwise addition preserves all rules and the all-zero state is allowed. If any state distinguishes a pair, adding that state pairs every agreement with one disagreement in the uniform stage weighting. Otherwise the two distinctions agree throughout.',
                'All linear rules are sums of the local parity rules. Each row vanishes on the solution set, and elimination gives as many independent rows as the codimension of that set. A rule on loose distinctions cancels every shared distinction. With precisely two holders per shared distinction, cancellation requires equal coefficients on its two knots. With the holder relation connected, all coefficients are equal. The only possible nonzero loose rule is the sum of all loose distinctions.',
                'With zero loose distinctions there is no nonzero rule, with one its bit is fixed at zero, with two they are equal, and with at least three every pair takes all four values equally. Under arbitrary holder counts, half disagreement alone does not guarantee both are open. The connected three-holder example has pair projection {00,01}. An odd right-hand side or a changed weighting removes the general half-disagreement argument.'
            ],
        },
    }
    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true')
    arg = parser.parse_args()
    begun = monotonic()
    result = main(arg.pilot)
    elapsed = round(monotonic()-begun,3)
    if arg.pilot:
        print(json.dumps({'seconds':elapsed,'named':result['E_F_R_independent_named_runs'],'N':result['N_independent_run0']}))
    else:
        (HERE/'lemma_checks.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps({'seconds':elapsed,'named':result['E_F_R_independent_named_runs'],'N':result['N_independent_run0']}))
