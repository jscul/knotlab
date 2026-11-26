"""cross.py SPEC: can a difference between two starts of reach.py reach the first family's side in the next round?
SPEC is JSON: d, ration, treatment, rounds, bound, ma, mb.

By the engine's round (eng.py, play_round) a member that is not short makes one join for each of its groups in
which no member is short, and one offshoot for each loose distinction left over.  So a knot of the first family's
side, made and held alike in both starts, can act differently only if one of its groups holds a member that is
short in one start and not in the other (or is there in one start only), and no member of that group is short in
both.  This program counts those groups, round by round, with the same names for knots as front.py:

    differing members     members of the round that are short in one start only, or are in one start only, by sort
    groups that touch     groups with a member of the first family's side and a differing member (counted in the
                          start where that member is short, or where it is)
    ... and decide        those of them in which no other member is short: here the first side must differ"""
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
        T = S.copy()
        try: rec = E.play_round(T, law, G)
        except E.GuardStop: stop = 'guard'; break
        S = T; seen = collections.Counter(); short = set(rec['short'])
        members = {name[u]: (front.sort_of(anc[u], d), u in short) for u in rec['members']}
        groups = [tuple(sorted(name[u] for u in g)) for g in rec['groups']]
        for b in rec['births']:
            ps = tuple(sorted(name[p] for p in b['parents']))
            key = (b['kind'], ps); k = seen[key]; seen[key] += 1
            name[b['id']] = hashlib.sha1(repr((b['kind'], ps, k)).encode()).hexdigest()[:14]
            anc[b['id']] = frozenset().union(*[anc[p] for p in b['parents']])
        rows.append((members, groups)); del rec
        if S.n_knots > bound: stop = 'knots'
    return rows, stop

def compare(spec):
    d = spec['d']
    A, sa = grow(d, spec['ma'], spec['ration'], spec['treatment'], spec['rounds'], spec['bound'])
    B, sb = grow(d, spec['mb'], spec['ration'], spec['treatment'], spec['rounds'], spec['bound'])
    out = {'spec': spec, 'stops': [sa, sb], 'rounds': []}
    for t in range(min(len(A), len(B))):
        (ma, ga), (mb, gb) = A[t], B[t]
        differing = {n for n in set(ma) | set(mb) if (n not in ma) or (n not in mb) or ma[n][1] != mb[n][1]}
        by_sort = collections.Counter((ma.get(n) or mb.get(n))[0] for n in differing)
        first_same = sum(1 for n in ma if ma[n][0] == 'first' and n in mb)
        touch = decide = 0; touching_sorts = collections.Counter(); touch_out = decide_out = cross_any = 0
        for mem, groups in ((ma, ga), (mb, gb)):
            for g in groups:
                # the same count for a member of the whole outside (first side or rest) with a differing member of
                # the second side (added after the advisor's review: a change passes s and t, which are rest, first)
                if any(mem[n][0] in OUTSIDE for n in g) and any(mem[n][0] not in OUTSIDE for n in g):
                    cross_any += 1
                    d2 = [n for n in g if n in differing and mem[n][0] not in OUTSIDE and (mem[n][1] or (n not in ma) or (n not in mb))]
                    if d2:
                        touch_out += 1
                        if not any(mem[n][1] for n in g if n not in differing): decide_out += 1
                if not any(mem[n][0] == 'first' for n in g): continue
                dif = [n for n in g if n in differing and mem[n][0] != 'first']
                dif = [n for n in dif if mem[n][1] or (n not in ma) or (n not in mb)]      # short here, or here only
                if not dif: continue
                touch += 1
                for n in dif: touching_sorts[mem[n][0]] += 1
                if not any(mem[n][1] for n in g if n not in differing): decide += 1
        out['rounds'].append({'round': t + 1, 'members': [len(ma), len(mb)], 'first-side members in both': first_same,
                              'differing members by sort': dict(by_sort), 'groups that touch': touch,
                              'their differing members by sort': dict(touching_sorts), 'groups that touch and decide': decide,
                              'groups joining the outside and the second side, both starts': cross_any,
                              'of them with a differing second-side member': touch_out, 'and no other member short': decide_out})
    return out

if __name__ == '__main__':
    r = compare(json.loads(sys.argv[1]))
    if '--table' in sys.argv:
        s = r['spec']; print('d = %d, %s, %s, m = %d against %d; stops %s' % (s['d'], s['ration'], s['treatment'], s['ma'], s['mb'], r['stops']))
        for x in r['rounds']:
            print('round %d: members %s; differing %s; groups that touch the first side %d %s; and decide %d; outside-second groups %d, with a differing second-side member %d, deciding %d' % (
                x['round'], x['members'], x['differing members by sort'], x['groups that touch'], x['their differing members by sort'], x['groups that touch and decide'],
                x['groups joining the outside and the second side, both starts'], x['of them with a differing second-side member'], x['and no other member short']))
    else: print(json.dumps(r))
