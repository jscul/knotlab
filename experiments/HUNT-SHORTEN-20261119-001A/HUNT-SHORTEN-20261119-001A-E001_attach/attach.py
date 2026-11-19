"""HUNT-SHORTEN-20261119-001A: construct the advisor's configuration and test the table version of the extension.

Part 1 (the mechanism).  For every static other-states pair (a, b) of PARENT-RULE part S (1,034 pairs, at most 7 junctions; the
complete list of such collisions within its bounds) and every full-table isometry phi (VF2, no twin quotient, cap 20,000):
for every set S of 1 to 3 live junctions of a that phi carries onto live junctions of b with their loose distinctions, and every
fresh count f in {1, 2} with |S| + f >= 3, attach to a one new junction n taking one loose distinction from each member of S and f
fresh ones, and to b its counterpart under phi.  Does the extension of phi match the two new tables entry by entry?  Are the two
new tables isometric at all?  (Loose distinctions of one junction are interchangeable, so the choice among them is immaterial.)
Part 2 (the law).  For every attached pair whose extension matches, does the extension keep what the round reads (EXTEND-ROUND's
R)?  If so, run the law's round on both and check its extension entry by entry: a failure is a counterexample to Claim B.
New tables by bonds (plib) when at most 15 vertices; the law's next tables as in EXTEND-ROUND (bonds or exact_table_v2).
Run: .venv/bin/python -B attach.py -> attach.json beside the artifacts."""
import importlib.util
import json
import signal
import sys
from collections import Counter, defaultdict
from itertools import combinations
from multiprocessing import Pool
from pathlib import Path

from networkx.algorithms import isomorphism

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
_e = importlib.util.spec_from_file_location('extend_round', ROOT / 'experiments/EXTEND-ROUND-20261119-001A/EXTEND-ROUND-20261119-001A-E001_extend/extend.py')
EX = importlib.util.module_from_spec(_e)
sys.modules[_e.name] = EX
_e.loader.exec_module(EX)
L = EX.L
CAP_ISO = 20000
CAP_PHI_PER_ATTACH = 20
LIMIT = 900


def attachments(a, b, phi):
    own_a, own_b = L.owners(a), L.owners(b)
    star_b = {s: j for j, s in enumerate(b)}
    ok = []
    for u in L.live_set(a, own_a):
        img = frozenset(phi[x] for x in a[u])
        if img in star_b:
            v = star_b[img]
            la = {x for x in a[u] if len(own_a[x]) == 1}
            lb = {x for x in b[v] if len(own_b[x]) == 1}
            if {phi[x] for x in la} == lb:
                ok.append((u, v, min(la)))
    out = []
    for k in (1, 2, 3):
        for S in combinations(ok, k):
            for f in (1, 2):
                if k + f >= 3:
                    out.append((S, f))
    return out


def attach(stars, taken, f):
    labels = sorted(L.owners(stars))
    top = max(labels) + 1
    fresh = list(range(top, top + f))
    return stars + [frozenset(list(taken) + fresh)], fresh


def analyse(item):
    kind, A, B, meta = item
    a = [frozenset(s) for s in A]
    b = [frozenset(s) for s in B]
    out = {'meta': meta, 'junctions': [len(a), len(b)]}
    signal.signal(signal.SIGALRM, EX._late)
    signal.alarm(LIMIT)
    c = Counter()
    fails = []
    try:
        ta, la = L.table(a)
        tb, lb = L.table(b)
        m = isomorphism.GraphMatcher(L.coloured(ta, la), L.coloured(tb, lb), node_match=lambda x, y: x['k'] == y['k'],
                                     edge_match=lambda x, y: x['d'] == y['d'])
        cache = {}
        seen_phi = defaultdict(int)
        n = 0
        for phi in m.isomorphisms_iter():
            n += 1
            if n > CAP_ISO:
                c['capped'] += 1
                break
            for S, f in attachments(a, b, phi):
                key = (tuple((u, v) for u, v, _ in S), f)
                if seen_phi[key] >= CAP_PHI_PER_ATTACH:
                    continue
                seen_phi[key] += 1
                a1, fa = attach(a, [x for _, _, x in S], f)
                b1, fb = attach(b, [phi[x] for _, _, x in S], f)
                ka, kb = frozenset(a1), frozenset(b1)
                if ka not in cache:
                    cache[ka] = L.table(a1)
                if kb not in cache:
                    cache[kb] = L.table(b1)
                (ta1, la1), (tb1, lb1) = cache[ka], cache[kb]
                phi1 = dict(phi)
                phi1.update(dict(zip(fa, fb)))
                ext_ok = all(ta1[(x, y)] == tb1[tuple(sorted((phi1[x], phi1[y])))] for (x, y) in ta1)
                c['attachments_tested'] += 1
                c[f'size_{len(S)}_fresh_{f}'] += 1
                if not ext_ok:
                    c['extension_fails'] += 1
                    c[f'fails_size_{len(S)}_fresh_{f}'] += 1
                    iso_any = L.iso(L.coloured(ta1, la1), L.coloured(tb1, lb1))
                    c['fails_tables_not_isometric_at_all'] += not iso_any
                    # the advisor's diagnostic: does each side's new table follow the path formula
                    # d'(x,y) = min(d(x,y), d(x,p)+2+d(q,y), d(x,q)+2+d(p,y)) through the taken distinctions p, q?
                    if len(S) == 2:
                        for side, (t_old, t_new, taken) in (('a', (ta, ta1, [x for _, _, x in S])), ('b', (tb, tb1, [phi[x] for _, _, x in S]))):
                            p, q = taken

                            def d(x, y, t=t_old):
                                if x == y:
                                    return 0
                                v = t[(x, y)] if (x, y) in t else t[(y, x)]
                                return 10 ** 6 if v == 'none' else v
                            dev = sum(1 for (x, y) in t_old if t_new[(x, y)] != min(d(x, y), d(x, p) + 2 + d(q, y), d(x, q) + 2 + d(p, y)))
                            c[f'fails_side_{side}_entries_off_path_formula'] += dev
                    if len(fails) < 3:
                        bad = [(x, y, ta1[(x, y)], tb1[tuple(sorted((phi1[x], phi1[y])))]) for (x, y) in ta1
                               if ta1[(x, y)] != tb1[tuple(sorted((phi1[x], phi1[y])))]][:6]
                        fails.append({'S': [[u, v] for u, v, _ in S], 'fresh': f, 'tables_isometric_at_all': iso_any,
                                      'a1': [sorted(s) for s in a1], 'b1': [sorted(s) for s in b1], 'differing_entries': bad})
                    continue
                # Part 2: does the extension keep what the round reads?  Then the law's round.
                psi = EX.keeps_reading(phi1, a1, b1, EX.reading(a1), EX.reading(b1))
                if psi is None:
                    continue
                c['keeps_reading'] += 1
                a2, b2 = EX.grow1(a1), EX.grow1(b1)
                if a2 is None or b2 is None:
                    c['law_round_stalls'] += 1
                    continue
                phi2 = EX.extension(phi1, psi, a1, b1, a2, b2)
                if phi2 is None:
                    c['law_rounds_do_not_correspond'] += 1
                    continue
                (ta2, la2), (tb2, lb2) = EX.full_table(a2), EX.full_table(b2)
                ok2 = all(ta2[(x, y)] == tb2[tuple(sorted((phi2[x], phi2[y])))] for (x, y) in ta2)
                c['law_extension_is_isometry' if ok2 else 'law_extension_fails_CLAIM_B'] += 1
                if not ok2 and len(fails) < 6:
                    fails.append({'claim_B_counterexample': True, 'a1': [sorted(s) for s in a1], 'b1': [sorted(s) for s in b1]})
        c['isometries'] += n
    except EX.Late:
        out['undecided_late'] = True
    finally:
        signal.alarm(0)
    out['counts'] = dict(c)
    out['fails'] = fails
    return out


def main():
    its = [x for x in EX.items() if x[0] == 'static']
    with Pool(8) as pool:
        rows = pool.map(analyse, its, chunksize=2)
    s = Counter()
    for r in rows:
        s['pairs'] += 1
        s['late'] += bool(r.get('undecided_late'))
        for k, v in r['counts'].items():
            s[k] += v
        s['pairs_with_an_attachment'] += r['counts'].get('attachments_tested', 0) > 0
        s['pairs_with_a_failure'] += r['counts'].get('extension_fails', 0) > 0
        s['pairs_with_reading_kept_after_attaching'] += r['counts'].get('keeps_reading', 0) > 0
        s['pairs_with_a_claim_B_counterexample'] += r['counts'].get('law_extension_fails_CLAIM_B', 0) > 0
    dest = ROOT / 'artifacts/HUNT-SHORTEN-20261119-001A/HUNT-SHORTEN-20261119-001A-E001_attach'
    dest.mkdir(parents=True, exist_ok=True)
    (dest / 'attach.json').write_text(json.dumps({'summary': dict(sorted(s.items())), 'rows': rows}, indent=1, default=str))
    print(json.dumps(dict(sorted(s.items())), indent=1))


if __name__ == '__main__':
    main()
