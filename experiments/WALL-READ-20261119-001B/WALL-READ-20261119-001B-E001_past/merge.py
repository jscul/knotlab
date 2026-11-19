"""Merge WALL-READ-20261119-001B-E001's run into results.json: python3 -B merge.py <out dir> <results.json>."""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
from longrun import load_results  # noqa: E402

UNREAD = ['start-%02d' % i for i in range(16) if i not in (0, 4)]


def follow_summary(r):
    rounds = [m for m in r['records'] if m.get('kind') == 'round' and 'count' in m]
    keys = {m['t']: m for m in r['records'] if m.get('kind') == 'round' and 'open_sum' in m}
    stages = {}
    for m in r['records']:
        if m.get('kind') == 'stage':
            stages[m['t']] = m                     # the full record replaces the partial one
    counts = {m['t']: m for m in rounds}
    checks = []
    for t, s in stages.items():
        if (t + 1) in counts and 'k_any' in s:
            g = counts[t + 1]['groups']
            checks.append({'t': t, 'groups_next': g, 'bound_k': s['bound_k'], 'bound_w': s.get('bound_w'),
                           'ok': s['bound_k'] <= g and (s.get('bound_w') is None or s['bound_w'] <= g)})
    last_t = max(counts) if counts else 0
    last = stages.get(last_t, {})
    best = max(last.get('bound_k', -1), last.get('bound_w', -1) if last.get('bound_w') is not None else -1)
    return {'end': r['end'], 'counts': [counts[t]['count'] for t in sorted(counts)],
            'largest': [counts[t]['largest'] for t in sorted(counts)],
            'largest_block': [counts[t]['largest_block'] for t in sorted(counts)],
            'one_block_rounds': [t for t in sorted(counts) if counts[t]['one_block']],
            'last_t': last_t, 'last_count': counts[last_t]['count'] if counts else None,
            'last_stage': {k: v for k, v in last.items() if k != 'kind'},
            'best_bound_next': best, 'checks': checks,
            'stages': {t: {k: v for k, v in s.items() if k not in ('kind',)} for t, s in sorted(stages.items())},
            'double_count': {t: [keys[t]['open_sum'], keys[t + 1]['parent_sum'] if (t + 1) in keys else None] for t in keys}}


def main(out, dest):
    R = load_results(out)
    not_ok = {k: v.get('status') for k, v in R.items() if v.get('status') != 'ok'}
    res = {k: v['result'] for k, v in R.items() if v.get('status') == 'ok'}
    b1 = Counter()
    b1_bad = []
    for k, r in res.items():
        if k.startswith('eq-census') or k.startswith('eq-rand'):
            b1.update({k.split('-')[1] + ' ' + a: b for a, b in r['tally'].items()})
            b1_bad += r['bad']
        if k.startswith('eq-read'):
            rr = r['result']
            b1['read ' + ('equal' if rr and rr['equal'] else ('differ' if rr else 'skip ' + r['end']))] += 1
    F = {r['start']: follow_summary(r) for k, r in res.items() if k.startswith('follow-')}
    s3 = F.get('start-03', {})
    s7 = s3.get('stages', {}).get(7, {})
    dc = s3.get('double_count', {}).get(7)
    b2 = {'double_count_7_8': dc, 'fastlib': s7.get('fastlib'),
          'held': bool(dc) and dc[0] == dc[1] and s7.get('fastlib') == {'groups': 28064, 'largest': 109}}
    b3_checks = [c for f in F.values() for c in f['checks']]
    b4_bound = s3.get('stages', {}).get(8, {}).get('bound_w')
    b5 = {s: (F[s]['best_bound_next'], F[s]['last_count'], F[s]['best_bound_next'] > (F[s]['last_count'] or 0))
          for s in UNREAD if s != 'start-03' and s in F}
    b6 = {s: F[s]['one_block_rounds'] for s in UNREAD if s in F}
    out_ = {
        'B1': {'tally': dict(b1), 'bad': b1_bad[:10], 'held': not any('differ' in k for k in b1)},
        'B2': b2,
        'B3': {'checks': len(b3_checks), 'failed': [c for c in b3_checks if not c['ok']], 'held': all(c['ok'] for c in b3_checks)},
        'B4': {'bound': b4_bound, 'stage8': {k: v for k, v in s3.get('stages', {}).get(8, {}).items()}, 'held': (b4_bound or 0) >= 10 ** 6},
        'B5': {'per_start': b5, 'count': sum(1 for v in b5.values() if v[2]), 'of': len(b5),
               'held': sum(1 for v in b5.values() if v[2]) >= 10},
        'B6': {'one_block_rounds': b6, 'held': all(not v for v in b6.values())},
        'follow': F,
        'not_ok': not_ok,
    }
    Path(dest).parent.mkdir(parents=True, exist_ok=True)
    Path(dest).write_text(json.dumps(out_, indent=1, default=str) + '\n')
    for k in ('B1', 'B2', 'B3', 'B4', 'B5', 'B6'):
        v = out_[k]
        print(k, v['held'], json.dumps({x: y for x, y in v.items() if x not in ('held', 'stage8', 'per_start', 'one_block_rounds', 'failed')})[:400])
    for s, f in sorted(F.items()):
        print(s, f['end'], f['counts'], 'last', f['last_t'], 'best bound', f['best_bound_next'],
              'k', f['last_stage'].get('k_any'), 'k_iso', f['last_stage'].get('k_iso'))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
