"""tally_ring_line.py RUNS: the ring-line table (RING_LINE.md)."""
import sys, json, gzip
def load(p): return [json.loads(l) for l in (gzip.open(p, 'rt') if p.endswith('.gz') else open(p))]
rows = load(sys.argv[1]); runs = [r for r in rows if 'marks' in r]; lost = [r for r in rows if 'not run' in r]
def start(xs):
    """the first round after round 1 in which the source makes a knot of its own, after making none, or None"""
    for i in range(1, len(xs)):
        if xs[i] and not all(xs[1:i]) and 0 in xs[1:i]: return i + 1
    return None
def none_after_1(xs): return all(x == 0 for x in xs[1:])
def shifted(a, b):
    """the same numbers after each start, up to the shorter run"""
    i, j = start(a), start(b)
    if i is None or j is None: return None
    x, y = a[i - 1:], b[j - 1:]; n = min(len(x), len(y)); return x[:n] == y[:n]
print('| law | join | d | rounds | ring returns (first) | own births as with a stub | source makes none, rounds | starts again: ring / stub | same numbers after | marks heard | sent again |')
print('|---|---|---|---|---|---|---|---|---|---|---|')
for law in ('CAP-3', 'REC-ONE-FEWER', 'ONE-FEWER', 'JOIN-FEWER', 'ORD'):
    for join in ('meeting', 'share'):
        for r in sorted([r for r in runs if r['law'] == law and r['join'] == join], key=lambda r: r['d']):
            w, s = r['whole']['own births'], r['stub']['own births']
            zeros = [i + 1 for i, x in enumerate(w) if x == 0 and i > 0]
            zr = ('%d to %d' % (zeros[0], zeros[-1]) if zeros and zeros == list(range(zeros[0], zeros[-1] + 1)) else (str(len(zeros)) + ' rounds' if zeros else 'none'))
            ret = r['ring returns']; heard = [m for m in r['marks'] if m[2] is not None]
            print('| %s | %s | %d | %d | %s | %s | %s | %s / %s | %s | %d of %d%s | %s |' % (
                law, join, r['d'], r['rounds'], '%d (%d to %d)' % (len(ret), ret[0][0], ret[0][1]) if ret else 'none',
                'yes' if not r['own births differ from with a stub, rounds'] else 'no, from round %d' % r['own births differ from with a stub, rounds'][0],
                zr, start(w) or ('never' if none_after_1(w) else '-'), start(s) or ('never' if none_after_1(s) else '-'),
                {True: 'yes', False: 'no', None: '-'}[shifted(w, s)], len(heard), len(r['marks']),
                (' (rounds %s)' % sorted({(m[0], m[2]) for m in heard})) if heard else '', len([a for a in r['again'] if a[2] is not None]) if r['again'] else '-'))
print('\nruns read', len(runs), 'not run', len(lost), lost[:3])
