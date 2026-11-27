"""rings.py: values and changes on the joined-ring starts (README.md, part C; frozen in preregistration.md). Starts are
the built binding study's (BUILT-BINDING-20261126-001, repro.rings_start: rings of n knots, each ring knot holding two
loose distinctions; for every pair of rings a connecting knot attached to each ring, linked directly or through a chain
of knots). Ordinary parity growth on the canonical engine, rounds 0 to ROUNDS. A knot's lineage is its start ring, or
the union of its parents' lineages (connecting knots carry none). Two choices of reader (a scaffold, both run):
    'places'  every place of the knots whose lineage is ring r alone (apart in sides.py's sense: no knot holds a
              distinction of each; the holders of the two regions' attachments meet through the link)
    'own'     those places held by no knot outside ring r's lineage (apart in forbid.meets' sense too)
Per stage and pair of rings: separated or not, e with the middle unread, read for changes, read for values (css.ebits),
the advisor's identities as an independent route, and with only the one distinction the pair's two connecting knots
share read for its change (the rest unread). Also: a control (two adjacent knots of ring 0), one reader holding rings 0
and 2 against ring 1 (with the square of css.square where e >= 2), and the family with one loose distinction at the
first chain's middle knot.
    rings.py ROUNDS"""
import sys, json, itertools
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / 'BUILT-BINDING-20261126-001'))
import css, repro                    # noqa: E402
forbid = repro.forbid

FAMILIES = [('three rings of five, detour (the referee\'s 30 knots)', dict(R=3, n=5)),
            ('three rings of five, direct links', dict(R=3, n=5, link='double')),
            ('three rings of four, detour', dict(R=3, n=4)),
            ('two rings of five, detour', dict(R=2, n=5)),
            ('three rings of five, detour, one loose distinction at the first chain\'s middle knot', dict(R=3, n=5, middle_loose=True))]


def regions(knots, lineage, R):
    places = {r: sorted({d for u, k in enumerate(knots) if lineage[u] == frozenset([r]) for d in k}) for r in range(R)}
    h = css_holders(knots)
    own = {r: [d for d in places[r] if all(lineage[u] == frozenset([r]) for u in h[d])] for r in range(R)}
    return {'places': places, 'own': own}


def css_holders(knots):
    h = {}
    for u, k in enumerate(knots):
        for d in k: h.setdefault(d, []).append(u)
    return h


def link_distinction(knots, lineage, A, B):
    """the distinction held by two middle knots, one holding a distinction of A and the other one of B"""
    h = css_holders(knots); A, B = set(A), set(B)
    for d, hs in h.items():
        if len(hs) == 2 and all(lineage[u] == frozenset(['middle']) for u in hs):
            u, v = hs
            if (set(knots[u]) & A and set(knots[v]) & B) or (set(knots[v]) & A and set(knots[u]) & B): return [d]
    return None


def reads(knots, A, B):
    out = {'separated': css.separated(knots, A, B), 'held': [len(A), len(B)]}
    for mid in ('unread', 'changes', 'values'): out['e, middle ' + mid] = css.ebits(knots, A, B, mid)
    ids = css.identities(knots, A, B)
    out['identities agree'] = ids['changes'] == out['e, middle changes'] and ids['values'] == out['e, middle values']
    return out


def run(rounds):
    for label, kw in FAMILIES:
        S, rings, loose = repro.rings_start(**kw)
        R = len(rings)
        lineage = {k: frozenset([r]) for r, ring in enumerate(rings) for k in ring}
        for k in range(len(S)): lineage.setdefault(k, frozenset(['middle']))
        st = S
        for t in range(rounds + 1):
            if t > 0:
                new, status, births = forbid.grown(st, 'parity', 'ordinary')
                if status != 'funded': print(json.dumps({'family': label, 'round': t, 'end': status})); break
                for b in births: lineage[b['knot']] = frozenset().union(*(lineage[p] for p in b['parents']))
                st = new
            knots = [list(k) for k in st]
            row = {'family': label, 'round': t, 'knots': len(knots), 'distinctions': len({d for k in knots for d in k})}
            reg = regions(knots, lineage, R)
            for choice in ('places', 'own'):
                for r, s in itertools.combinations(range(R), 2):
                    A, B = reg[choice][r], reg[choice][s]
                    key = 'readers %s, rings %d and %d' % (choice, r, s)
                    if set(A) & set(B): row[key] = 'a distinction in both'; continue
                    row[key] = reads(knots, A, B)
                    if choice == 'places':
                        link = link_distinction(knots, lineage, A, B)
                        row[key]['e, only the link distinction read for its change'] = css.ebits(knots, A, B, link) if link else 'no link distinction'
                if R == 3:
                    A, B = reg[choice][0] + reg[choice][2], reg[choice][1]
                    key = 'readers %s, rings 0 and 2 against ring 1' % choice
                    row[key] = reads(knots, A, B)
                    if row[key]['e, middle changes'] >= 2: row[key]['square'] = css.square(knots, A, B)
            u, v = rings[0][0], rings[0][1]
            A, B = knots[u], [d for d in knots[v] if d not in knots[u]]
            row['control: two adjacent knots of ring 0'] = reads(knots, A, B)
            print(json.dumps(row), flush=True)


if __name__ == '__main__':
    run(int(sys.argv[1]))
