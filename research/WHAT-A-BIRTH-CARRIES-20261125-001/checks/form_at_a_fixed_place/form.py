"""A probe for sub-goal B335, third part (the thread's own run; not a registered study): the place held fixed, the
form changed.

Written BEFORE its first run.  A start is built from a first seed (the first part's), one link distinction, and a
second seed (the second part's) that holds the link distinction on one of its knots.  The first seed and the place of
the link are held fixed while the second seed runs over a family of forms.  Grown under one law, the course from the
first seed only (knots descended from its start knots and from none of the second seed's) is read round by round with
ticket B's reading, and two forms are put in one class through round R when those courses are the same through R.
Asked: (1) does the course separate forms at all, and how many; (2) does it go on separating them in later rounds, so
that the course keeps following the second part after the first contact; (3) are the classes the same from another
first seed or another place (then the course follows the form, not the place); (4) what in the form decides the class.
Expected, before the run: (1) yes, by a count at the first contact; (2) not known; under laws with no taking rule
perhaps not at all, since without a take a knot meets only what its own parents and siblings hold."""
import sys, os, json, time, itertools, collections, resource
from collections import Counter, defaultdict
sys.setrecursionlimit(100000)
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get('PROBE_ROOT') or os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
XDIR = ROOT + '/experiments/WHAT-A-BIRTH-CARRIES-20261125-001B/WHAT-A-BIRTH-CARRIES-20261125-001B-E001_link_through_a_made_knot'
import eng
assert os.path.dirname(os.path.abspath(eng.__file__)) == HERE and hasattr(eng, 'MET_KIND')
sys.path.append(XDIR); os.chdir(XDIR)
import read
from read import View

# ---------------------------------------------------------------------------------------------------------- seeds
def seed(shape, loose):
    """Knots of a seed as lists of local distinction names.  shape: 'one' (a single knot), 'two' (two knots sharing
    one distinction), 'chain3' (three in a row), 'ring3' (three, each sharing one with each other); loose[i] = the
    number of loose distinctions of knot i."""
    n = len(loose) if shape == 'chain' else {'one': 1, 'two': 2, 'chain3': 3, 'ring3': 3, 'star3': 4}[shape]
    assert len(loose) == n
    knots = [[] for _ in range(n)]; nxt = 0
    pairs = [(i, i + 1) for i in range(n - 1)] if shape == 'chain' else \
        {'one': [], 'two': [(0, 1)], 'chain3': [(0, 1), (1, 2)], 'ring3': [(0, 1), (1, 2), (0, 2)],
         'star3': [(0, 1), (0, 2), (0, 3)]}[shape]
    for a, b in pairs:
        knots[a].append(nxt); knots[b].append(nxt); nxt += 1
    for i in range(n):
        for _ in range(loose[i]):
            knots[i].append(nxt); nxt += 1
    return knots

def build(first, site, second, at):
    """The start: the first seed, the second seed, and one link distinction held by knot `site` of the first and knot
    `at` of the second.  Returns (stars, which start knots are the first seed's).  second = None: no second seed; the
    link distinction is then a loose distinction of the first seed's knot."""
    stars = []; off = 0
    for k in first: stars.append([d + off for d in k])
    off = 1 + max(d for k in stars for d in k)
    nf = len(stars)
    link = off; off += 1
    stars[site].append(link)
    if second is not None:
        for k in second: stars.append([d + off for d in k])
        stars[nf + at].append(link)
    return stars, nf

def places_ok(shape, loose, at):
    """Every knot of the seed has three or more places, the link distinction counted on the knot that holds it."""
    ks = seed(shape, loose)
    return all(len(k) + (1 if i == at else 0) >= 3 for i, k in enumerate(ks))

def forms():
    """The family of second seeds: (name, shape, loose, the knot that holds the link); every knot of three or more
    places."""
    out = []
    for k in (2, 3, 4, 5): out.append(('one:%d' % k, 'one', (k,), 0))
    for a in (1, 2, 3):
        for b in (2, 3, 4): out.append(('two:%d,%d' % (a, b), 'two', (a, b), 0))
    for a, b, c in itertools.product((1, 2), (1, 2, 3), (2, 3)):
        out.append(('chain3:%d,%d,%d@end' % (a, b, c), 'chain3', (a, b, c), 0))
    for a, b, c in itertools.product((2, 3, 4), (0, 1), (2, 3)):
        if a >= c: out.append(('chain3:%d,%d,%d@mid' % (a, b, c), 'chain3', (a, b, c), 1))
    for a, b, c in itertools.product((0, 1, 2), (1, 2, 3), (1, 2)):
        if b >= c: out.append(('ring3:%d,%d,%d' % (a, b, c), 'ring3', (a, b, c), 0))
    assert all(places_ok(sh, lo, at) for _, sh, lo, at in out)
    return out

def chains(values=(2, 3), lengths=(1, 2, 3, 4)):
    """Second seeds that are chains hanging from the link by their first knot, every knot of three or more places."""
    out = []
    for L in lengths:
        for lo in itertools.product(values, repeat=L):
            ok = all(l + (1 if i == 0 else 0) + (1 if i > 0 else 0) + (1 if i < L - 1 else 0) >= 3 for i, l in enumerate(lo))
            if ok: out.append(('chain:' + ','.join(map(str, lo)), 'chain', lo, 0))
    return out

def unseen():
    """A second family, fixed BEFORE any of it was run, to repeat the probe on forms and first seeds not looked at
    while it was built (first seeds F to J below).  Predictions written before the run:
      U1  for every law and first seed, what the first seed's descent makes falls into three or more classes among
          the forms (four or more with the bare start);
      U2  under each of the four rows with short knots retiring or making offshoots (with and without the take of a
          sole candidate), some pairs of forms are first told apart in round 2 or later;
      U3  in at least half of the studies the first seed's line has two or more of the fates ends, steady, grows."""
    out = [('one:6', 'one', (6,), 0), ('one:7', 'one', (7,), 0)]
    for a in (4, 5):
        for b in (2, 5): out.append(('two:%d,%d' % (a, b), 'two', (a, b), 0))
    for b, c in itertools.product((1, 2), (2, 4)): out.append(('chain3:3,%d,%d@end' % (b, c), 'chain3', (3, b, c), 0))
    for a in (2, 3): out.append(('chain3:%d,2,2@mid' % a, 'chain3', (a, 2, 2), 1))
    for b, c in ((1, 1), (2, 1), (2, 2), (3, 1), (3, 2)): out.append(('ring3:3,%d,%d' % (b, c), 'ring3', (3, b, c), 0))
    for lo in itertools.product((1, 4), repeat=3): out.append(('chain:' + ','.join(map(str, lo)) + ',4', 'chain', lo + (4,), 0))
    for h in (0, 1):
        for arms in ((2, 2, 2), (2, 2, 3), (3, 3, 3)):
            out.append(('star3:%d;%d,%d,%d@hub' % ((h,) + arms), 'star3', (h,) + arms, 0))
            out.append(('star3:%d;%d,%d,%d@arm' % ((h,) + arms), 'star3', (h,) + arms, 1))
    assert all(places_ok(sh, lo, at) for _, sh, lo, at in out), [n for n, sh, lo, at in out if not places_ok(sh, lo, at)]
    return out

FIRSTS = {  # name: (shape, loose, site)
    'F one knot, two loose':   ('one', (2,), 0),
    'G two knots, the larger': ('two', (3, 2), 0),
    'H ring of three, other':  ('ring3', (2, 1, 1), 0),
    'I chain 1,2,2 at the end': ('chain3', (1, 2, 2), 0),
    'J two knots, the smaller': ('two', (1, 3), 0),
    'A one knot':            ('one', (3,), 0),
    'B two knots':           ('two', (2, 3), 0),
    'C ring of three':       ('ring3', (1, 2, 2), 0),
    'D chain, at the end':   ('chain3', (2, 1, 3), 0),
    'E chain, in the middle': ('chain3', (2, 1, 3), 1),
}

def run_one(law, stars, nf, rounds, knot_bound):
    run = eng.Run(law, stars=stars, rounds=rounds, knot_bound=knot_bound)
    member_part = {u: (0 if u < nf else 1) for u in range(len(stars))}
    bits = read.desc_bits(run, 0, member_part)
    v = View(run, read.Keys(run), bits, 0, 1, 0, list(range(nf)), list(range(nf, len(stars))))
    S = run.S
    per = []; made = []
    for t in range(1, run.rounds_read + 1):
        xo = [b for b in run.recs[t - 1]['births'] if bits[b['id']] == 1]
        yo = sum(1 for b in run.recs[t - 1]['births'] if bits[b['id']] == 2)
        mix = sum(1 for b in run.recs[t - 1]['births'] if bits[b['id']] == 3)
        per.append((len(xo), sum(b['f'] for b in xo), sum(len(b['takes']) for b in xo), yo, mix))
        # what the first seed's own descent makes this round: each birth by kind, parents, places, fresh, takes
        made.append(tuple(sorted((b['kind'], len(b['parents']), len(S.places[b['id']]), b['f'], len(b['takes'])) for b in xo)))
    v.made = made
    return run, v, per

def study(law, first_name, rounds=7, knot_bound=3000, fam=None):
    shape, loose, site = FIRSTS[first_name]
    first = seed(shape, loose)
    fam = fam or forms()
    views = {}; pers = {}; stops = {}
    for name, sh, lo, at in [('(none)', None, None, None)] + fam:
        stars, nf = build(first, site, None if sh is None else seed(sh, lo), at)
        run, v, per = run_one(law, stars, nf, rounds, knot_bound)
        views[name] = v; pers[name] = per; stops[name] = (run.rounds_read, run.stop, run.S.n_knots)
    names = list(views)
    last = max(v.run.rounds_read for v in views.values())
    classes_by_round = []; made_by_round = []; running = []
    cls_prev = {n: 0 for n in names}
    for R in range(1, last + 1):
        live = [n for n in names if views[n].run.rounds_read >= R and n in cls_prev]
        cs = {n: read.course(views[n], R) for n in live}
        reps = []; cls = {}
        for n in live:
            for i, (m, c) in enumerate(reps):
                if cls_prev[m] == cls_prev[n] and read.same_course(c, cs[n]):   # equal through R implies equal before
                    cls[n] = cls[m]; break
            else:
                cls[n] = len(reps); reps.append((n, cs[n]))
        classes_by_round.append(cls); cls_prev = cls; running.append(len(live))
        seen = {}
        made_by_round.append({n: seen.setdefault(tuple(views[n].made[:R]), len(seen)) for n in live})
    def fate(n):
        x = [p[0] for p in pers[n]]
        if len(x) < 4: return 'not read'
        tail = x[-3:]
        if tail == [0, 0, 0]: return 'ends'
        if tail[0] == tail[1] == tail[2]: return 'steady at %d' % tail[0]
        if tail[0] < tail[1] < tail[2]: return 'grows'
        if tail[0] > tail[1] > tail[2]: return 'shrinks'
        return 'other'
    return {'law': law.name(), 'first': first_name, 'forms': len(names) - 1, 'last': last, 'stops': stops,
            'forms still read, by round': running,
            'classes by round': [len(set(c.values())) for c in classes_by_round],
            'classes by round, by what it makes': [len(set(c.values())) for c in made_by_round],
            'classes': classes_by_round, 'classes by what it makes': made_by_round,
            'fate': {n: fate(n) for n in names},
            'per round (X only births, fresh, takes; second only births; of both)': pers}

if __name__ == '__main__':
    resource.setrlimit(resource.RLIMIT_AS, (8 << 30, 8 << 30))
    spec = json.loads(sys.argv[1])
    law = eng.Law(spec['ration'], spec['treatment'], spec.get('take'), spec.get('knot_law', 'nae'))
    t0 = time.time()
    fam = None
    if spec.get('family') == 'unseen':
        fam = unseen()
    if spec.get('family') == 'chains':
        fam = chains(tuple(spec.get('values', (2, 3))), tuple(spec.get('lengths', (1, 2, 3, 4))))
    o = study(law, spec['first'], rounds=spec.get('rounds', 7), knot_bound=spec.get('knot_bound', 3000), fam=fam)
    o['seconds'] = round(time.time() - t0, 1); o['spec'] = spec
    print(json.dumps(o))
