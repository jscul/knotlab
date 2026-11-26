"""run.py OUT.jsonl COUNT SEED: the frozen test (README, "Frozen").  COUNT ring structures drawn by random.Random(SEED):
k rings (2 to 4) of lengths drawn from 4, 5, 6, 7, 9, 11 (and, for P3, some of length 3), joined in one start by one
kind of join (a shared knot for all, two rings sharing two knots, a shared run of two knots, touches in a path or a
cycle, chains of 1 to 3 knots), each knot funded as in layers.build; and the same rings apart as the control.  Read at
rounds 1 to 3 of ordinary growth under parity and at round 1 under the two forbidding arms: the number of classes,
which sums of ring parities are labels, and whether the old distinctions' allowed changes are kept.  A stage of more
than MAX_DISTINCTIONS distinctions is not read."""
import sys, os, json, random, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import layers as LY
MAX_DISTINCTIONS = 2500
LENGTHS = (4, 5, 6, 7, 9, 11)
JOINS = ('one shared knot', 'two rings sharing two knots', 'a shared run of two knots', 'touches in a path',
         'touches in a cycle', 'chains')


def draw(rng, with_three):
    k = rng.choice((2, 3, 4)); L = [rng.choice(LENGTHS) for _ in range(k)]
    if with_three: L[rng.randrange(k)] = 3
    kind = rng.choice(JOINS); joins = []
    if kind == 'one shared knot':
        joins = [('share', (0, 0), (r, 0)) for r in range(1, k)]
    elif kind == 'two rings sharing two knots':
        for r in range(1, k):
            g = rng.randrange(2, L[r - 1] - 1) if L[r - 1] > 3 else 1
            joins += [('share', (r - 1, 0), (r, 0)), ('share', (r - 1, g), (r, min(g, L[r] - 1)))]
    elif kind == 'a shared run of two knots':
        for r in range(1, k):
            joins += [('share', (r - 1, 0), (r, 0)), ('share', (r - 1, 1), (r, 1))]
    elif kind == 'touches in a path':
        joins = [('touch', (r - 1, rng.randrange(L[r - 1])), (r, rng.randrange(L[r]))) for r in range(1, k)]
    elif kind == 'touches in a cycle':
        joins = [('touch', (r - 1, rng.randrange(L[r - 1])), (r, rng.randrange(L[r]))) for r in range(1, k)]
        if k >= 3: joins.append(('touch', (k - 1, rng.randrange(L[k - 1])), (0, rng.randrange(L[0]))))
    else:
        joins = [('chain', (r - 1, rng.randrange(L[r - 1])), (r, rng.randrange(L[r])), rng.randint(1, 3)) for r in range(1, k)]
    return k, L, kind, joins


def read(start, rd, arm, rounds):
    st = start; out = []
    for t in range(1, rounds + 1):
        nxt, status, births = LY.forbid.grown(st, 'parity', arm)
        if status != 'funded': out.append({'round': t, 'end': status}); break
        n = len({x for r in nxt for x in r})
        if n > MAX_DISTINCTIONS: out.append({'round': t, 'end': 'not read: %d distinctions' % n}); break
        a = LY.analyse(nxt, rd)[0]
        out.append({'round': t, 'classes': a['classes'], 'labels': a['sums of ring parities that are labels'],
                    'old allowed changes kept': LY.projection_kept(start, nxt)['same'], 'ties capped': a['ties capped'],
                    'births with no fresh distinction': sum(1 for b in births if b['f'] == 0)})
        st = nxt
    return out


if __name__ == '__main__':
    out, count, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    rng = random.Random(seed)
    with open(out, 'w') as f:
        for i in range(count):
            k, L, kind, joins = draw(rng, with_three=(i % 5 == 4))
            rec = {'index': i, 'rings': L, 'join': kind, 'joins': joins}
            t0 = time.time()
            try:
                start, rd = LY.build(L, joins)
                rec['joined'] = {arm: read(start, rd, arm, 3 if arm == 'ordinary' else 1) for arm in ('ordinary', 'one_fewer', 'arity_floor')}
                apart, rda = LY.build(L, [])
                rec['apart'] = {'ordinary': read(apart, rda, 'ordinary', 1)}
            except Exception as e:
                rec['error'] = repr(e)[:300]
            rec['seconds'] = round(time.time() - t0, 2)
            f.write(json.dumps(rec) + '\n'); f.flush()
