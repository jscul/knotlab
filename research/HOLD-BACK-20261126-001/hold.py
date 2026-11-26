"""hold.py: late hearing from afar under the local taking rules (A) and under laws in which a new knot holds back part
of what it is owed (B).  Studies of HOLD-BACK-20261126-001; README.md has the design and the expectations, written
before the full runs.

A pair: a receiver of the census against one of five senders (the switch census's), joined by a meeting through two
link knots (d = 3), a short knot waiting; 12 rounds, 1,500 knots or the engine's guard at four times the fold engine's
limits.  After round t0, one more loose distinction at up to five members of the far end's own knots in a part linked
to the receiver's (nearest first) and at up to two in parts not linked; read the first round the receiver's own
births differ.  A hearing is LATE when it comes after round 2d = 6.

    hold.py run SET I0 I1      SET = takes or hold; sampled receivers I0..I1-1, a JSON line per pair and law
    hold.py linked I0 I1       B2: the 28 linked far ends I0..I1-1 against the cap's switch kind, under the two forms
                               and the cap of three"""
import sys, os, json, random
HERE = os.path.dirname(os.path.abspath(__file__))
TR = os.path.join(HERE, '..', 'TWO-RECEPTIONS-20261126-001')
sys.path.insert(0, TR)
import shortage
linked, second, receivers, ring_line, jam, bench, eng = (shortage.linked, shortage.second, shortage.receivers, shortage.ring_line,
                                                         shortage.jam, shortage.bench, shortage.eng)
ROUNDS, BOUND, SEED = 12, 1500, 20261126
T0 = (1, 2, 3)


class Hold(eng.Law):
    """the ordinary count with a hold-back rule in place of f = max(D, 3 - p, 1); FORMS below"""
    def __init__(self, form):
        eng.Law.__init__(self, 'ORD', 'CANCEL-WAIT', None, 'nae'); self.form = form
    def fresh(self, kind, p, D, o):
        return max(FORMS[self.form](kind, p, D, o), 3 - p, 1)
    def name(self):
        return 'HOLD-%s/CANCEL-WAIT/RELEASE/no-take/nae' % self.form

# the two forms frozen with the advisor (README.md, B), one from each class it named: a new knot takes no more fresh
# distinctions than it was given (cap-like: short only where it is owed more than it was given), and what it was given
# pays part of what it is owed (short by one at every join owed two or more)
FORMS = {'INHERIT': lambda kind, p, D, o: min(D, p),
         'NET-OWING': lambda kind, p, D, o: D - p + 1}


def law(spec):
    if spec[0] == 'HOLD': return Hold(spec[1])
    return eng.Law(spec[0], 'CANCEL-WAIT', spec[1], 'nae', spec[2])


def pair(A, B, spec):
    st, ro, _ = jam.changed(A, B, 3, None, 'meeting')
    W = ring_line.Growth(st, ro, law(spec)); W.run(ROUNDS, BOUND)
    lk = linked.linked_rounds(W)
    nb = lambda g: [sum(r['births by'].values()) for r in g.rows]
    out = {'A': A, 'B': B, 'law': list(spec), 'rounds': len(W.rows), 'ended': W.stop or 'rounds', 'made short': shortage.made_short(W),
           'linked': lk, 'births': nb(W), 'changes': []}
    for t0 in T0:
        if len(W.rows) <= t0 or lk[t0 - 1] is None: continue
        for want, n in ((True, 5), (False, 2)):
            ms, dist = linked.far_members(W, t0, want)
            for u in ms[:n]:
                H = ring_line.fork_at(W, t0); ring_line.mark(H, u); H.run(ROUNDS, BOUND)
                r, m = ring_line.first_own_diff(W, H, t0)
                out['changes'].append({'t0': t0, 'linked': want, 'sharings': dist.get(u), 'heard': r, 'rounds': m,
                                       'births with': nb(H) if r is not None else None})     # the advisor's jam check
    return out


TAKES = [('ORD', 'MET', 'OLDEST'), ('ORD', 'MET', 'NEWEST'), ('ORD', 'MET-SOLE', None), ('ORD', 'STEPS1-SOLE', None), ('ORD', 'STEPS2-SOLE', None)]

if __name__ == '__main__' and sys.argv[1] == 'run':
    bench.MULT = 4
    R = receivers.register()
    sample = sorted(random.Random(SEED).sample(range(646), 100))
    laws = TAKES if sys.argv[2] == 'takes' else [('HOLD', f) for f in FORMS] + [('ORD', None, None), ('CAP-3', None, None)]
    if sys.argv[2] == 'hold':                  # the positive controls: the cap's switch kind and FLOOR1's late receiver
        names = [n for n, st, s in R]
        sample = sample + [names.index(n) for n in ('n3:g7:122@0', 'n4:g15:2123@0') if names.index(n) not in sample]
    for i in sample[int(sys.argv[3]):int(sys.argv[4])]:
        for B in receivers.SENDERS:
            for spec in laws:
                print(json.dumps(pair(R[i][0], B, spec)), flush=True)


def linked_pair(B, spec, rounds=24, bound=6000):
    """B2: the switch kind of the cap of three (three mutually sharing knots holding one, two and two loose distinctions,
    sited at the one) against a far end of LINKED-UNDER-CAP-20261126-001's 28, as that study's census reads it: changes
    after rounds 3, 5 and 8 at up to five linked and two unlinked far members"""
    A = 'tri:122@0'; bench.STARS[A], bench.SITE[A] = second.tri(1), 0
    st, ro, _ = jam.changed(A, B, 3, None, 'meeting')
    W = ring_line.Growth(st, ro, law(spec)); W.run(rounds, bound)
    lk = linked.linked_rounds(W)
    nb = lambda g: [sum(r['births by'].values()) for r in g.rows]
    out = {'A': A, 'B': B, 'law': list(spec), 'rounds': len(W.rows), 'ended': W.stop or 'rounds', 'made short': shortage.made_short(W),
           'linked': lk, 'births': nb(W), 'changes': []}
    for t0 in (3, 5, 8):
        if len(W.rows) <= t0 or lk[t0 - 1] is None: continue
        for want, n in ((True, 5), (False, 2)):
            ms, dist = linked.far_members(W, t0, want)
            for u in ms[:n]:
                H = ring_line.fork_at(W, t0); ring_line.mark(H, u); H.run(rounds, bound)
                r, m = ring_line.first_own_diff(W, H, t0)
                out['changes'].append({'t0': t0, 'linked': want, 'sharings': dist.get(u), 'heard': r, 'rounds': m,
                                       'births with': nb(H) if r is not None else None})
    return out


if __name__ == '__main__' and sys.argv[1] == 'linked':
    bench.MULT = 4
    receivers.register()
    import gzip
    LK = os.path.join(HERE, '..', 'LINKED-UNDER-CAP-20261126-001')
    far = sorted({json.loads(l)['B'] for l in gzip.open(os.path.join(LK, 'linked_runs.jsonl.gz'), 'rt')
                  if json.loads(l).get('law') == 'CAP-3' and json.loads(l)['A'] == 'tri:122@0' and json.loads(l)['linked'][15]})
    for B in far[int(sys.argv[2]):int(sys.argv[3])]:
        for spec in [('HOLD', 'INHERIT'), ('HOLD', 'NET-OWING'), ('CAP-3', None, None)]:
            print(json.dumps(linked_pair(B, spec)), flush=True)
