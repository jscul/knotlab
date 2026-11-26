"""thr.py: laws whose threshold a new knot reads from itself.  Study of SELF-THRESHOLD-20261126-001; README.md has the
design and the expectations, written before the full run.  The readings are HOLD-BACK-20261126-001's (hold.py): B1 the
census of 101 receivers against five senders, changes after rounds 1, 2, 3; B2 the 28 far ends that stay linked to the
cap's switch kind, changes after rounds 3, 5, 8.  Each law is min(ordinary count, a threshold), kept above the floor
max(3 - p, 1); the floor is the ordinary count's own.

    PLACES        threshold p + 1: no more fresh distinctions than one more than it was given
    HALF          threshold ceil(D / 2) + 1: at most a little over half of what it is owed (binds where D >= 4)
    CAP3-JOINS    the cap of three on joins only, offshoots the ordinary count (the advisor's control for PLACES)
    CAP-3         the cap of three (the positive control)      ORD    the ordinary count (the negative control)
    PLACES-JOINS, PLACES-OFFSHOOTS   PLACES on one kind of birth only (added after the referee of the hold-back study
                  found a join given three and owed four where PLACES and the cap differ; README, "Where PLACES differs")
Also read, on the growth with no change: how many births the law gives less than the ordinary count, by kind.

    thr.py census I0 I1        B1 for sampled receivers I0..I1-1
    thr.py linked I0 I1 [LAWS]   B2 for the linked far ends I0..I1-1 (LAWS: comma-separated, default all five)"""
import sys, os, json, random, gzip, collections
HERE = os.path.dirname(os.path.abspath(__file__))
HB = os.path.join(HERE, '..', 'HOLD-BACK-20261126-001')
sys.path.insert(0, HB)
import hold
eng, bench, jam, ring_line, linked, second, receivers, shortage = (hold.eng, hold.bench, hold.jam, hold.ring_line, hold.linked,
                                                                   hold.second, hold.receivers, hold.shortage)


class Threshold(eng.Law):
    FORMS = {'PLACES': lambda kind, p, D, o: p + 1,
             'HALF': lambda kind, p, D, o: -(-D // 2) + 1,
             'CAP3-JOINS': lambda kind, p, D, o: 3 if kind == 'join' else 10 ** 9,
             'PLACES-JOINS': lambda kind, p, D, o: p + 1 if kind == 'join' else 10 ** 9,
             'PLACES-OFFSHOOTS': lambda kind, p, D, o: p + 1 if kind != 'join' else 10 ** 9}
    def __init__(self, form):
        eng.Law.__init__(self, 'ORD', 'CANCEL-WAIT', None, 'nae'); self.form = form; self.binds = collections.Counter()
    def fresh(self, kind, p, D, o):
        q = max(D, 3 - p, 1)
        f = max(min(q, self.FORMS[self.form](kind, p, D, o)), 3 - p, 1)
        if f < q: self.binds[kind] += 1
        return f
    def name(self):
        return 'THRESHOLD-%s/CANCEL-WAIT/RELEASE/no-take/nae' % self.form


def make(spec):
    return Threshold(spec) if spec in Threshold.FORMS else eng.Law(spec, 'CANCEL-WAIT', None, 'nae')

LAWS = ['PLACES', 'HALF', 'CAP3-JOINS', 'CAP-3', 'ORD']


def run_pair(A, B, spec, t0s, rounds, bound):
    st, ro, _ = jam.changed(A, B, 3, None, 'meeting')
    lw = make(spec); W = ring_line.Growth(st, ro, lw); W.run(rounds, bound)
    binds = dict(getattr(lw, 'binds', {}))
    lk = linked.linked_rounds(W)
    nb = lambda g: [sum(r['births by'].values()) for r in g.rows]
    out = {'A': A, 'B': B, 'law': spec, 'rounds': len(W.rows), 'ended': W.stop or 'rounds', 'made short': shortage.made_short(W),
           'linked': lk, 'births': nb(W), 'binds on the growth with no change': binds, 'changes': []}
    for t0 in t0s:
        if len(W.rows) <= t0 or lk[t0 - 1] is None: continue
        for want, n in ((True, 5), (False, 2)):
            ms, dist = linked.far_members(W, t0, want)
            for u in ms[:n]:
                H = ring_line.fork_at(W, t0); ring_line.mark(H, u); H.run(rounds, bound)
                r, m = ring_line.first_own_diff(W, H, t0)
                out['changes'].append({'t0': t0, 'linked': want, 'sharings': dist.get(u), 'heard': r, 'rounds': m,
                                       'births with': nb(H) if r is not None else None})
    return out


if __name__ == '__main__':
    bench.MULT = 4
    R = receivers.register()
    if sys.argv[1] == 'census':
        names = [n for n, st, s in R]
        sample = sorted(random.Random(hold.SEED).sample(range(646), 100))
        sample = sample + [names.index(n) for n in ('n3:g7:122@0', 'n4:g15:2123@0') if names.index(n) not in sample]
        for i in sample[int(sys.argv[2]):int(sys.argv[3])]:
            for B in receivers.SENDERS:
                for spec in LAWS:
                    print(json.dumps(run_pair(R[i][0], B, spec, (1, 2, 3), 12, 1500)), flush=True)
    else:
        A = 'tri:122@0'; bench.STARS[A], bench.SITE[A] = second.tri(1), 0
        LK = os.path.join(HERE, '..', 'LINKED-UNDER-CAP-20261126-001')
        far = sorted({json.loads(l)['B'] for l in gzip.open(os.path.join(LK, 'linked_runs.jsonl.gz'), 'rt')
                      if json.loads(l).get('law') == 'CAP-3' and json.loads(l)['A'] == 'tri:122@0' and json.loads(l)['linked'][15]})
        laws = sys.argv[4].split(',') if len(sys.argv) > 4 else LAWS
        for B in far[int(sys.argv[2]):int(sys.argv[3])]:
            for spec in laws:
                print(json.dumps(run_pair(A, B, spec, (3, 5, 8), 24, 6000)), flush=True)
