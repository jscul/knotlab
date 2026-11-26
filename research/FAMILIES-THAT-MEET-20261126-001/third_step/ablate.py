"""ablate.py SPEC: a direct test of "apart for good" (README, "Why"), proposed by the advisor's review.
SPEC is JSON: d, m, ration, treatment, rounds, bound.

The start is grown twice.  The first growth is the whole one; each round from the second on it also checks that
every two joinable members share a parent and were born in the same round (the fact the argument rests on).  The
second growth is the same up to the round z in which no group joins the sides; there every member of the second
side is retired by hand (its loose distinctions barred), so that nothing of the second side ever acts again, and
the growth goes on.  If the outside acts alone once the sides are apart, everything outside the second side must
be the same in both growths, knot for knot and fresh count for fresh count, in every later round."""
import sys, os, json, hashlib, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); import reach
price, eng, eng_cap = reach.price, reach.eng, reach.eng_cap

def grow(spec, ablate_at=None):
    d, m, ration, treatment = spec['d'], spec['m'], spec['ration'], spec['treatment']
    live, deg, stars = price.source(reach.tail(d, m))
    E = eng_cap if (ration.startswith('CAP-') and ration != 'CAP-3') else eng
    law = E.Law(ration, treatment, None, 'nae'); G = E.Guard(price.MULT)
    S = E.from_stars(stars)
    other = {'b2'} | {x for x in live if x[0] in 'qz'}
    side = {}; name = {}
    for i, x in enumerate(live):
        side[i] = 'second' if x in other else 'outside'
        if side[i] == 'outside': name[i] = x
    for i in range(len(live), len(stars)): side[i] = 'witness'
    rows = []; pairs = bad = 0; barred_members = 0
    while S.round < spec['rounds']:
        T = S.copy()
        if ablate_at is not None and T.round + 1 == ablate_at:
            for u, h, k in E.live_members(T):
                if side[u] == 'second':
                    barred_members += 1
                    for x in T.usable(u): T.barred[x] = True
        try: rec = E.play_round(T, law, G)
        except E.GuardStop: break
        cross = sum(1 for g in rec['groups'] if len({side[u] for u in g}) > 1)
        if T.round >= 2:
            adj = rec['roster'].adj
            for a in adj:
                for b in adj[a]:
                    if a < b:
                        pairs += 1
                        if not (set(S.parents[a]) & set(S.parents[b])) or S.made[a] != S.made[b]: bad += 1
        S = T; out = []; seen = collections.Counter()
        for b in rec['births']:
            s = 'second' if any(side[p] == 'second' for p in b['parents']) else 'outside'; side[b['id']] = s
            if s == 'second': continue
            ps = tuple(sorted(name[p] for p in b['parents']))
            key = (b['kind'], ps); k = seen[key]; seen[key] += 1
            n = hashlib.sha1(repr((b['kind'], ps, k)).encode()).hexdigest()[:16]; name[b['id']] = n
            out.append((n, b['f']))
        out.sort(); rows.append({'round': S.round, 'groups joining the sides': cross, 'outside births': len(out),
                                 'outside': hashlib.sha1(repr(out).encode()).hexdigest()[:16], 'knots': S.n_knots})
        del rec
        if S.n_knots > spec['bound']: break
    return rows, pairs, bad, barred_members

if __name__ == '__main__':
    spec = json.loads(sys.argv[1])
    full, pairs, bad, _ = grow(spec)
    z = next((r['round'] for r in full if r['round'] >= 2 and r['groups joining the sides'] == 0), None)
    out = {'spec': spec, 'rounds read': len(full), 'joinable pairs checked from round 2': pairs,
           'of them without a common parent or born in different rounds': bad, 'round with no group joining the sides': z}
    if z is not None:
        cut, _, _, barred = grow(spec, ablate_at=z)
        n = min(len(full), len(cut)); later = [i for i in range(n) if full[i]['round'] >= z]
        out.update({'second-side members retired by hand at that round': barred, 'later rounds compared': len(later),
                    'outside births in them': sum(full[i]['outside births'] for i in later),
                    'later rounds in which the outside differs': sum(1 for i in later if full[i]['outside'] != cut[i]['outside']),
                    'earlier rounds in which it differs': sum(1 for i in range(n) if full[i]['round'] < z and full[i]['outside'] != cut[i]['outside']),
                    'knots at the last round, whole and cut': [full[n - 1]['knots'], cut[n - 1]['knots']]})
    print(json.dumps(out))
