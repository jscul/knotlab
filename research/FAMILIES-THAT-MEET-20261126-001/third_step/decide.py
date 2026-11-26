"""decide.py SPEC: at the first round the outside differs between two starts, name the cause knot by knot.
SPEC is JSON: d, ration, treatment, rounds, bound, ma, mb.  (Written after the advisor's review, which pointed out
that "28 groups, 28 births" in cross.py's table was a match of counts only.)

A member that is not short makes one offshoot for each loose distinction its kept groups leave over.  So for every
member of the outside that both starts have, with the same loose distinctions, the offshoots it makes in one start
and not in the other are as many as the groups it has kept in the other start and not in this one.  For each such
group the program records why it is not kept here: a member of it is short here (and of which sort), or the group
is not there.  Knots are named by how they were made, as in front.py."""
import sys, os, json, collections, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); import reach, front
price, eng, eng_cap = reach.price, reach.eng, reach.eng_cap
OUTSIDE = ('first', 'rest')

def grow(d, m, ration, treatment, rounds, bound):
    live, deg, stars = price.source(reach.tail(d, m))
    E = eng_cap if (ration.startswith('CAP-') and ration != 'CAP-3') else eng
    law = E.Law(ration, treatment, None, 'nae'); G = E.Guard(price.MULT)
    S = E.from_stars(stars); stop = None
    name = {i: x for i, x in enumerate(live)}; anc = {i: frozenset([x]) for i, x in enumerate(live)}
    for i in range(len(live), len(stars)): name[i] = 'w%d' % i; anc[i] = frozenset()
    rows = []
    while stop is None and S.round < rounds:
        T = S.copy(); rec = E.play_round(T, law, G); S = T
        seen = collections.Counter(); short = set(rec['short'])
        members = {name[u]: (front.sort_of(anc[u], d), u in short, rec['h'][u]) for u in rec['members']}
        groups = [(frozenset(name[u] for u in g), not any(u in short for u in g)) for g in rec['groups']]
        births = []
        for b in rec['births']:
            ps = tuple(sorted(name[p] for p in b['parents']))
            key = (b['kind'], ps); k = seen[key]; seen[key] += 1
            name[b['id']] = hashlib.sha1(repr((b['kind'], ps, k)).encode()).hexdigest()[:14]
            anc[b['id']] = frozenset().union(*[anc[p] for p in b['parents']])
            births.append((name[b['id']], b['kind'], ps, front.sort_of(anc[b['id']], d), b['f']))
        rows.append((members, groups, births)); del rec
        if S.n_knots > bound: stop = 'knots'
    return rows

def report(spec):
    d = spec['d']; a, b = spec['ma'], spec['mb']
    A = grow(d, a, spec['ration'], spec['treatment'], spec['rounds'], spec['bound'])
    B = grow(d, b, spec['ration'], spec['treatment'], spec['rounds'], spec['bound'])
    n = min(len(A), len(B))
    out_births = lambda X, t: {x[0]: x for x in X[t][2] if x[3] in OUTSIDE}
    t = next((i for i in range(n) if {k: v[4] for k, v in out_births(A, i).items()} != {k: v[4] for k, v in out_births(B, i).items()}), None)
    out = {'spec': spec, 'rounds compared': n, 'first round the outside differs': None if t is None else t + 1}
    if t is None: return out
    (ma, ga, ba), (mb, gb, bb) = A[t], B[t]
    oa, ob = out_births(A, t), out_births(B, t)
    res = {}
    for tag, X, Y, mem_x, mem_y, gx, gy in (('m=%d' % a, oa, ob, ma, mb, ga, gb), ('m=%d' % b, ob, oa, mb, ma, gb, ga)):
        only = [X[k] for k in X if k not in Y]
        kinds = collections.Counter((x[1], x[3]) for x in only)
        extra_off = collections.Counter(x[2][0] for x in only if x[1] == 'offshoot')          # by parent name
        kept_y = collections.defaultdict(list); status_x = {}
        for g, kept in gy:
            if kept:
                for u in g: kept_y[u].append(g)
        for g, kept in gx: status_x[g] = kept
        explained = 0; why = collections.Counter(); unexplained = 0; parents_same = 0
        for p, k in extra_off.items():
            if p in mem_x and p in mem_y and mem_x[p][2] == mem_y[p][2] and not mem_x[p][1] and not mem_y[p][1]: parents_same += 1
            lost = [g for g in kept_y.get(p, []) if not status_x.get(g, False)]            # kept there, not kept here
            gained = sum(1 for g, kept in gx if kept and p in g and not any(g == h and kk for h, kk in gy))
            if len(lost) - gained == k: explained += k
            else: unexplained += k
            for g in lost:
                if g not in status_x: why['the group is not there'] += 1
                else:
                    sh = sorted({mem_x[u][0] for u in g if mem_x[u][1]})
                    why['a member is short here: ' + ', '.join(sh)] += 1
        res[tag] = {'outside births here only': len(only), 'by kind and sort': {'%s, %s' % k: v for k, v in kinds.items()},
                    'parents of the offshoots here only': len(extra_off), 'of them members of both starts, not short, with the same loose distinctions': parents_same,
                    'offshoots accounted for by groups kept in the other start and not here': explained, 'not accounted for': unexplained,
                    'why those groups are not kept here': dict(why)}
    out['by start'] = res
    return out

if __name__ == '__main__':
    print(json.dumps(report(json.loads(sys.argv[1])), indent=1))
