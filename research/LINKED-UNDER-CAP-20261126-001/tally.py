"""tally.py RUNS [AGAIN]: the linked-pairs tables (README.md, "What was found")."""
import sys, json, gzip, collections
def load(p): return [json.loads(l) for l in (gzip.open(p, 'rt') if p.endswith('.gz') else open(p))]
rows = load(sys.argv[1]); runs = [r for r in rows if 'law' in r]; lost = [r for r in rows if 'not run' in r]
def kind(r): return 'switch kind' if r['A'].startswith('tri') else 'census receivers'
print('| law | pairs | read | linked after round 3 / 8 / 16 | far changes heard where linked (of) | where not linked (of) | heard at t0 + s + 1 |')
print('|---|---|---|---|---|---|---|')
for law in ('CAP-3', 'CAP-4', 'CAP-5', 'CAP-6', 'CAP-7'):
    for kd in ('switch kind', 'census receivers'):
        rs = [r for r in runs if r['law'] == law and kind(r) == kd]
        if not rs: continue
        at = lambda i: sum(1 for r in rs if len(r['linked']) >= i and r['linked'][i - 1])
        ch = [c for r in rs for c in r['changes']]
        yes = [c for c in ch if c['linked']]; no = [c for c in ch if not c['linked']]
        hy = [c for c in yes if c['heard'] is not None]; hn = [c for c in no if c['heard'] is not None]
        exact = sum(1 for c in hy if c['sharings'] is not None and c['heard'] == c['t0'] + c['sharings'] + 1)
        print('| %s | %s | %d | %d / %d / %d | %d of %d | %d of %d | %d of %d |' % (law, kd, len(rs), at(4), at(9), at(16) if True else 0,
              len(hy), len(yes), len(hn), len(no), exact, len(hy)))
print('\nnot run', len(lost), lost[:3])
if len(sys.argv) > 2:
    ag = load(sys.argv[2]); print('\n| law | pairs | first change heard | second heard | third | fourth | still linked 4 rounds after the first change |')
    print('|---|---|---|---|---|---|---|')
    for law in ('CAP-3', 'CAP-4', 'CAP-5', 'CAP-6', 'CAP-7'):
        rs = [r for r in ag if r['law'] == law]
        if not rs: continue
        k = lambda i: sum(1 for r in rs if len(r['changes']) > i and r['changes'][i].get('heard') is not None)
        still = sum(1 for r in rs if r['changes'] and 'linked after it' in r['changes'][0] and len(r['changes'][0]['linked after it']) > 6 and r['changes'][0]['linked after it'][6])
        print('| %s | %d | %d | %d | %d | %d | %d |' % (law, len(rs), k(0), k(1), k(2), k(3), still))
