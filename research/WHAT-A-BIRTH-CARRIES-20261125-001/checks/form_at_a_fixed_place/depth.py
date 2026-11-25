"""A probe for sub-goal B335, third part, second program (the thread's own run; not a registered study): how deep into
the second part does the first part's course see?

Written BEFORE its first run, after form.py showed that with no taking rule and short knots waiting the course from
the first seed only tells apart second seeds that differ in a knot NOT next to the link, and only from a later round.
The second seed is a chain of L knots hanging from the link: knot 0 holds the link distinction, knot i shares one
distinction with knot i+1, and knot i holds loose[i] loose distinctions.  Two chains that differ in the loose count of
ONE knot, at depth i, are grown from the same first seed; the round at which the courses from the first seed only
first differ is recorded (ticket B's course reading), and beside it the round at which a cruder signature first
differs (the first seed's own births by round, with their numbers of places and of fresh distinctions).
Asked: is a change at depth i seen, and from which round?  Expected: under the laws where short knots wait, yes for
every depth, later for deeper knots; under the others only depth 0 or 1."""
import sys, os, json, time, itertools, collections, resource
from collections import Counter
import form
from form import eng, read, View, seed, build, FIRSTS

def chain(loose):
    n = len(loose); knots = [[] for _ in range(n)]; nxt = 0
    for i in range(n - 1):
        knots[i].append(nxt); knots[i + 1].append(nxt); nxt += 1
    for i in range(n):
        for _ in range(loose[i]):
            knots[i].append(nxt); nxt += 1
    return knots

def valid(loose):
    n = len(loose)
    for i, l in enumerate(loose):
        places = l + (1 if i == 0 else 0) + (1 if i > 0 else 0) + (1 if i < n - 1 else 0)
        if places < 3: return False
    return True

def grow(law, first_name, loose, rounds, knot_bound):
    shape, fl, site = FIRSTS[first_name]
    stars, nf = build(seed(shape, fl), site, chain(loose), 0)
    run = eng.Run(law, stars=stars, rounds=rounds, knot_bound=knot_bound)
    bits = read.desc_bits(run, 0, {u: (0 if u < nf else 1) for u in range(len(stars))})
    v = View(run, read.Keys(run), bits, 0, 1, 0, list(range(nf)), list(range(nf, len(stars))))
    S = run.S
    crude = []
    for t in range(1, run.rounds_read + 1):
        crude.append(tuple(sorted((b['kind'], len(S.places[b['id']]), b['f']) for b in run.recs[t - 1]['births'] if bits[b['id']] == 1)))
    return v, crude

def first_diff(va, ca, vb, cb):
    last = min(va.run.rounds_read, vb.run.rounds_read)
    rc = None
    for R in range(1, last + 1):
        if not read.same_course(read.course(va, R), read.course(vb, R)): rc = R; break
    rs = next((t + 1 for t in range(last) if ca[t] != cb[t]), None)
    return rc, rs, last

def study(law, first_name, L, base, rounds, knot_bound):
    out = {'law': law.name(), 'first': first_name, 'L': L, 'base': base, 'rows': []}
    b = tuple([base] * L)
    if not valid(b): return out
    vb, cb = grow(law, first_name, b, rounds, knot_bound)
    out['rounds read (base)'] = vb.run.rounds_read; out['stop'] = vb.run.stop; out['knots'] = vb.run.S.n_knots
    for i in range(L):
        for delta in (+1, -1, +2):
            v2 = list(b); v2[i] += delta; v2 = tuple(v2)
            if min(v2) < 0 or not valid(v2): continue
            va, ca = grow(law, first_name, v2, rounds, knot_bound)
            rc, rs, last = first_diff(vb, cb, va, ca)
            out['rows'].append({'depth': i, 'loose': '%d -> %d' % (base, base + delta), 'course first differs': rc, 'crude first differs': rs, 'read to': last})
    return out

if __name__ == '__main__':
    resource.setrlimit(resource.RLIMIT_AS, (8 << 30, 8 << 30))
    spec = json.loads(sys.argv[1])
    law = eng.Law(spec['ration'], spec['treatment'], spec.get('take'), spec.get('knot_law', 'nae'))
    t0 = time.time()
    o = study(law, spec['first'], spec['L'], spec.get('base', 2), spec.get('rounds', 12), spec.get('knot_bound', 4000))
    o['seconds'] = round(time.time() - t0, 1); o['spec'] = spec
    print(json.dumps(o))
