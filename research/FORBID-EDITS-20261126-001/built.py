"""built.py: the built starts of FORBID-EDITS-20261126-001 (README.md, "Built starts"), recorded as a scaffold.  The
census and its sampled extension hold no placement where forbidding answers every reader's own setting, so the
mechanism is built: two placements of the sampled extension where forbidding answers one reader's setting and the
round splits (`xcount_*.jsonl`), each copied, the two copies joined by one more shared distinction between a knot of
each that holds nothing loose and is no reader's holder (so no live knot gains a partner and growth in each copy is
unchanged, which the run checks), Alice the answering reader of the first copy, Bob of the second.  The tables are
then those of forbid.py.

    built.py list KIND              the built starts for a kind of edit (E1 or E2), one JSON line each
    built.py run KIND I0 I1         their tables"""
import sys, json, glob, itertools
import forbid


def examples(kind):
    out = []
    for f in sorted(glob.glob('xcount_%s_*.jsonl' % kind)):
        for l in open(f):
            r = json.loads(l)
            if r['kind'] != 'read' or r['law'] != 'nae' or not r['splits']: continue
            d = r['forbidding changes with own setting']
            if any(d) and not all(d):
                side = d.index(True)
                out.append({'arm': r['arm'], 'n': r['n'], 'supports': [tuple(x) for x in r['supports']], 'reader': tuple(r['readers'][side]),
                            'start': r['start']})
    seen, uniq = set(), []
    for e in out:
        key = (e['arm'], tuple(e['supports']), e['reader'])
        if key not in seen: seen.add(key); uniq.append(e)
    return uniq


def spent(supports, readers):
    held = forbid.holders(supports)
    return [i for i, row in enumerate(supports) if all(len(held[d]) == 2 for d in row) and i not in readers]


def join(a, ra, b, rb):
    """copy a, then b with its distinctions renamed past a's; one more shared distinction between a spent knot of each"""
    off = 1 + max(d for row in a for d in row)
    bb = [tuple(d + off for d in row) for row in b]
    sa, sb = spent(a, ra), spent(b, rb)
    if not sa or not sb: return None
    new = off + 1 + max(d for row in b for d in row)
    rows = [list(r) for r in a] + [list(r) for r in bb]
    rows[sa[0]].append(new); rows[len(a) + sb[0]].append(new)
    return tuple(tuple(r) for r in rows), ra, tuple(len(a) + h for h in rb)


def built(kind):
    ex = examples(kind)
    out = []
    for ea, eb in itertools.product(ex, repeat=2):
        if ea['arm'] != eb['arm'] or ea['n'] > 6 or eb['n'] > 6: continue
        j = join(ea['supports'], ea['reader'], eb['supports'], eb['reader'])
        if j: out.append({'from': [[ea['n'], ea['start'], ea['reader']], [eb['n'], eb['start'], eb['reader']]], 'arm answering': ea['arm'],
                          'supports': j[0], 'readers': [j[1], j[2]]})
    return out


if __name__ == '__main__':
    kind = sys.argv[2]
    B = built(kind)
    if sys.argv[1] == 'list':
        for b in B: print(json.dumps(b))
    else:
        for i in range(int(sys.argv[3]), min(int(sys.argv[4]), len(B))):
            b = B[i]
            for law in forbid.LAWS:
                for arm in forbid.ARMS:
                    p = forbid.placement(b['supports'], tuple(map(tuple, b['readers'])), kind, law, arm, True)
                    row = {'built': i, 'from': b['from'], 'arm answering': b['arm answering'], 'supports': b['supports'],
                           'readers': b['readers'], 'kind of edit': kind, 'law': law, 'arm': arm, 'start': i, 'n': len(b['supports'])}
                    row.update({a: v for a, v in p.items() if a != 'tables'})
                    if p['kind'] == 'read':
                        T = p['tables']; width = next(iter(T.values()))['width']
                        row['status'] = {''.join(map(str, s)): t['status'] for s, t in T.items()}
                        row['retained of old'] = {''.join(map(str, s)): [t['retained'], t['old']] for s, t in T.items()}
                        for w in ('U', 'S'):
                            single, full = forbid.checks(T, 2, w, width)
                            scores = {'fixed old value': forbid.chsh(T, w, 0, 1, width)[0]}
                            if kind == 'E2': scores['added value'] = forbid.chsh(T, w, 2, 3, width)[0]
                            row[w] = {'scores': {a: str(v) for a, v in scores.items()}, 'single unchanged': single, 'record unchanged': full,
                                      'correlations': {a: [str(x) for x in forbid.chsh(T, w, *ab, width)[1].values()]
                                                       for a, ab in (('fixed old value', (0, 1)),) }}
                    print(json.dumps(row), flush=True)
