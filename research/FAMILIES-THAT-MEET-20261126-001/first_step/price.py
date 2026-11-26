"""The generator study's 21-knot start, grown by the shared growth engine under the ordinary count, to check two
things against that study's note on meetings (research/GENERATORS-20261120-001/meeting.md):
  (1) the totals it gives at size four: 113 knots and 584 distinctions;
  (2) its formula for the fresh supply of a knot: f(C) = 2 + sum over the points x of the cluster C of (deg_H(x) - 2).
Written BEFORE its first run.  Expected: both hold exactly; every made knot is a join (no offshoot, no short knot)."""
import sys, os, json, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get('PROBE_ROOT') or os.path.abspath(os.path.join(HERE, '..', '..', '..'))
XDIR = ROOT + '/experiments/WHAT-A-BIRTH-CARRIES-20261125-001B/WHAT-A-BIRTH-CARRIES-20261125-001B-E001_link_through_a_made_knot'
sys.path.insert(0, XDIR); os.chdir(XDIR)
import eng

MULT = 100          # the engine's guard limits are for safety on long runs; here they are widened a hundredfold and never met

def source(extra=()):
    """Nine live originals and one spent witness for each of the 12 candidate pairs, each witness holding one
    distinction with its first endpoint and two with its second (the note's orientation).  `extra` adds candidate
    pairs with new originals, to change one original's degree."""
    live = ['v', 'r1', 'r2', 'r3', 's', 't', 'b0', 'b1', 'b2']
    pairs = [('v', 'r1'), ('r1', 'r2'), ('r2', 'r3'), ('r3', 'v'), ('v', 's'), ('t', 'v'), ('s', 'b0'), ('t', 'b0'),
             ('s', 'b1'), ('b1', 't'), ('t', 'b2'), ('b2', 's')] + list(extra)
    for a, b in extra:
        for x in (a, b):
            if x not in live: live.append(x)
    deg = collections.Counter(x for p in pairs for x in p)
    places = {x: [] for x in live}; wit = []; nxt = 0
    for a, b in pairs:
        w = []
        for x, k in ((a, 1), (b, 2)):
            for _ in range(k):
                places[x].append(nxt); w.append(nxt); nxt += 1
        wit.append(w)
    for x in live:
        for _ in range(deg[x]):
            places[x].append(nxt); nxt += 1
    stars = [places[x] for x in live] + wit
    return live, deg, stars

def grow(extra=(), rounds=3, knot_law='nae'):
    live, deg, stars = source(extra)
    law = eng.Law('ORD', 'CANCEL-RETIRE', None, knot_law)
    run = eng.Run(law, stars=stars, rounds=rounds, knot_bound=10 ** 6, mult=MULT)       # the engine's guard, widened (below)
    assert run.stop is None and run.rounds_read == rounds, (run.stop, run.guard)
    S = run.S
    types = {i: collections.Counter({x: 1}) for i, x in enumerate(live)}      # the cluster of each knot, by original type
    out = {'start': (len(stars), 1 + max(d for k in stars for d in k)), 'rounds': run.rounds_read, 'stop': run.stop, 'by round': []}
    bad = []; kinds = collections.Counter(); shorts = 0; inc = collections.Counter(); pairs_checked = [0]
    table = collections.defaultdict(collections.Counter)                      # cluster by type -> price -> how many knots
    for t in range(1, run.rounds_read + 1):
        rec = run.recs[t - 1]; shorts += len(rec['short'])
        for b in rec['births']:
            kinds[b['kind']] += 1
            ps = list(b['parents'])
            if len(ps) == 1:
                bad.append(('one parent', t, b['id'])); continue
            c = types[ps[0]] + types[ps[1]]
            if t >= 2:
                common = set(S.parents[ps[0]]) & set(S.parents[ps[1]])
                assert len(common) >= 1, (t, b['id'])
                c = c - types[sorted(common)[0]]
            for p in ps[2:]:                                                   # more than two parents: add what is new
                c = c | types[p]
            types[b['id']] = c
            assert sum(c.values()) == t + 1, (t, b['id'], c)
            want = 2 + sum((deg[x] - 2) * n for x, n in c.items())
            if b['f'] != want: bad.append(('price', t, b['id'], b['f'], want, dict(c)))
            for p in ps:
                fp = len([d for d in S.places[p] if S.maker[d] == p]) if S.made[p] > 0 else deg[live[p]]
                added = c - types[p]                                          # the one point the child has and this parent has not
                assert sum(added.values()) == 1, (t, b['id'], p)
                x = next(iter(added)); inc[b['f'] - fp] += 1; pairs_checked[0] += 1
                if b['f'] - fp != deg[x] - 2: bad.append(('step', t, b['id'], p, b['f'], fp, x))
            table[tuple(sorted(c.items()))][b['f']] += 1
        snap = run.snaps[t]
        out['by round'].append({'size': t + 1, 'knots': snap.n_knots, 'distinctions': snap.n_distinctions, 'births': len(rec['births'])})
    out['kinds'] = dict(kinds); out['short knots'] = shorts; out['price mismatches'] = len(bad); out['examples'] = bad[:3]
    out['child price minus parent price'] = dict(sorted(inc.items())); out['parent and child pairs checked'] = pairs_checked[0]
    out['table'] = table; out['deg'] = dict(deg)
    return out

CHANGED = (('b2', 'q1'), ('q1', 'q2'), ('q2', 'q3'), ('q3', 'b2'))            # b2 gains two candidate pairs: degree 4 for 2

def compare(rounds, knot_law='nae'):
    """The same source with one original's degree changed (the mark of the second family): every knot whose cluster
    avoids that original and the new ones must be there as before, at the same price; a knot whose cluster holds
    it n times must cost 2n more."""
    a = grow(rounds=rounds, knot_law=knot_law); b = grow(extra=CHANGED, rounds=rounds, knot_law=knot_law)
    new = {'b2', 'q1', 'q2', 'q3'}
    avoid = lambda key: not any(x in new for x, _ in key)
    A = {k: dict(v) for k, v in a['table'].items() if avoid(k)}; B = {k: dict(v) for k, v in b['table'].items() if avoid(k)}
    with_b2 = {k: dict(v) for k, v in a['table'].items() if not avoid(k)}
    shifted = sum(1 for k, v in with_b2.items() if b['table'].get(k) and
                  {f + 2 * dict(k)['b2']: n for f, n in v.items()} == dict(b['table'][k]))
    return {'knot law': knot_law, 'sizes': [x['size'] for x in a['by round']],
            'as given': {'knots and distinctions by size': [(x['knots'], x['distinctions']) for x in a['by round']], 'kinds': a['kinds'],
                         'short knots': a['short knots'], 'price mismatches': a['price mismatches'], 'steps checked': a['parent and child pairs checked'],
                         'child price minus parent price': a['child price minus parent price']},
            'with the mark of the second family changed': {'knots and distinctions by size': [(x['knots'], x['distinctions']) for x in b['by round']],
                         'kinds': b['kinds'], 'short knots': b['short knots'], 'price mismatches': b['price mismatches'], 'steps checked': b['parent and child pairs checked']},
            'clusters that avoid the changed original': {'kinds of cluster': len(A), 'knots': sum(sum(v.values()) for v in A.values()), 'the same in both, with the same prices': A == B},
            'clusters that hold the changed original': {'kinds of cluster': len(with_b2), 'knots': sum(sum(v.values()) for v in with_b2.values()),
                                                         'kinds present in the changed source and dearer by two for each time they hold it': shifted}}

if __name__ == '__main__':
    r = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    out = [compare(r, 'nae'), compare(r, 'parity')]
    print(json.dumps(out, indent=1))
