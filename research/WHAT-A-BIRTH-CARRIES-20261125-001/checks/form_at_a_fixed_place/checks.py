"""Checks of form.py on a sample of studies, every form of the mixed family:
  renumbering : the start with its distinctions renamed, the places of each knot and the knots themselves shuffled
                (seeded); what the first seed's descent makes, round by round, must be the same;
  knot test   : ticket B's routine on every knot of every round of the run;
  start knots : the last round at which a start knot is still a member of the roster.  A difference that first shows
                in a later round reached the first seed's descent through knots the growth made."""
import sys, json, random, collections
import form
from form import eng, read, View, seed, build, FIRSTS, forms

def made_of(law, stars, first_ids, rounds, knot_bound=3000):
    run = eng.Run(law, stars=stars, rounds=rounds, knot_bound=knot_bound)
    fi = set(first_ids)
    bits = read.desc_bits(run, 0, {u: (0 if u in fi else 1) for u in range(len(stars))})
    S = run.S; out = []
    for t in range(1, run.rounds_read + 1):
        out.append(tuple(sorted((b['kind'], len(b['parents']), len(S.places[b['id']]), b['f'], len(b['takes'])) for b in run.recs[t - 1]['births'] if bits[b['id']] == 1)))
    return run, out

spec = json.loads(sys.argv[1])
law = eng.Law(spec['ration'], spec['treatment'], spec.get('take'), 'nae')
shape, loose, site = FIRSTS[spec['first']]
res = collections.Counter(); last_start = collections.Counter(); kt = collections.Counter()
for name, sh, lo, at in forms():
    stars, nf = build(seed(shape, loose), site, seed(sh, lo), at)
    run, base = made_of(law, stars, range(nf), spec.get('rounds', 9))
    n0 = len(stars)
    ls = 0
    for t in range(1, run.rounds_read + 1):
        if any(u < n0 for u in run.recs[t - 1]['members']): ls = t
    last_start[ls] += 1
    k = read.knot_test_full(run)
    kt['verdicts'] += sum(k['verdicts'].values()) if isinstance(k['verdicts'], dict) else k['verdicts']
    kt['failing'] += k['n_fail']; kt['untested'] += k['n_untested']; kt['methods disagree'] += k['n_disagree']
    ds = sorted({d for st in stars for d in st})
    for sd in range(3):
        rng = random.Random(7000 + sd)
        perm = ds[:]; rng.shuffle(perm); m = dict(zip(ds, perm))
        order = list(range(n0)); rng.shuffle(order)
        st2 = []
        for u in order:
            k2 = [m[d] for d in stars[u]]; rng.shuffle(k2); st2.append(k2)
        first_ids = [i for i, u in enumerate(order) if u < nf]
        run2, got = made_of(law, st2, first_ids, spec.get('rounds', 9))
        res['renumberings'] += 1; res['same'] += got == base
print(json.dumps({'spec': spec, 'law': law.name(), 'forms': len(forms()), 'renumbering': dict(res), 'knot test': dict(kt),
                  'last round with a start knot in the roster (runs)': sorted(last_start.items())}))
