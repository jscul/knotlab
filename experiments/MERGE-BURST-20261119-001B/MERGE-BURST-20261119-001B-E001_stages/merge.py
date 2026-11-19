"""Score MERGE-BURST-20261119-001B-E001.  python3 -B merge.py <runner out dir> <results.json>"""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / 'scripts'))
from longrun import load_results  # noqa: E402


def merges(rounds):
    ev = []
    for a, b in zip(rounds, rounds[1:]):
        if a['group'] and b['group'] >= 10 * a['group'] and b['group'] >= 50:
            ev.append(b['t'])
    return ev


def main():
    R = load_results(sys.argv[1])
    rows, not_ok = [], []
    for cid, r in sorted(R.items()):
        if r.get('status') != 'ok':
            not_ok.append(cid)
            continue
        x, f = r['result']['start'], r['result']['follow']
        rd = f.get('reading')
        got = f.get('check') or []
        if rd:
            match = got == rd['predicted'][:len(got)]
            verdict = rd['reading']
        else:
            match, verdict = None, 'unresolved'
        ev = merges(f['rounds'])
        rows.append({'case': cid, 'n': x['n'], 'sizes': x['sizes'], 'control': x['outcome_then'] == 'alive', 'end': f['end'],
                     'rounds_reached': len(f['rounds']), 'read_at': rd['t'] if rd else None, 'verdict': verdict,
                     'stage_class_at_read': rd['class'] if rd else None, 'ranks': rd['ranks'] if rd else None,
                     'maximal_blocks': rd['maximal_blocks'] if rd else None, 'largest_block': rd['largest_block'] if rd else None,
                     'rate1': rd['rate1'] if rd else None, 'checked_rounds': len(got), 'check_equal': match,
                     'stability': f.get('stability'), 'merges': ev,
                     'after_merge': bool(rd and any(t <= rd['t'] for t in ev)),
                     'largest_group': max((q['group'] for q in f['rounds']), default=None),
                     'last_rounds': [(q['t'], q['count'], q['group'], q['reduced']) for q in f['rounds'][-4:]],
                     'seconds': f['seconds']})
    test = [r for r in rows if not r['control']]
    read = [r for r in test if r['verdict'] != 'unresolved']
    checked = [r for r in rows if r['verdict'] != 'unresolved' and r['checked_rounds'] >= 3]
    out = {'not_ok': not_ok, 'rows': rows,
           'R1': all(r['check_equal'] for r in rows if r['verdict'] != 'unresolved'),
           'R1_checked_at_least_3': len(checked), 'R1_read_but_unchecked': sum(1 for r in rows if r['verdict'] != 'unresolved' and r['checked_rounds'] < 3),
           'R2a': all(r['maximal_blocks'] == 1 for r in read),
           'R2b': all(r['verdict'] == 'closes' for r in read),
           'R3': len(read) >= 5,
           'R4_stable': all(r['stability'] in (None, r['verdict']) or r['stability'] in ('stall', 'two blocks share two points', 'cycle of three blocks', 'one loose or none') for r in rows if r['verdict'] != 'unresolved'),
           'R4_next_stage_in_class': sum(1 for r in rows if r['verdict'] != 'unresolved' and r['stability'] not in (None, 'stall', 'two blocks share two points', 'cycle of three blocks', 'one loose or none')),
           'tally': dict(Counter(r['verdict'] for r in test)),
           'no_reading_by': dict(Counter(r['end'] for r in test if r['verdict'] == 'unresolved')),
           'merges_before_reading': dict(Counter(len([t for t in r['merges'] if r['read_at'] is None or t <= r['read_at']]) for r in test))}
    Path(sys.argv[2]).parent.mkdir(parents=True, exist_ok=True)
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1, default=str) + '\n')
    print(json.dumps({k: out[k] for k in ('not_ok', 'R1', 'R1_checked_at_least_3', 'R1_read_but_unchecked', 'R2a', 'R2b', 'R3', 'R4_stable', 'R4_next_stage_in_class', 'tally', 'no_reading_by', 'merges_before_reading')}, indent=1))
    for r in rows:
        print(r['case'], r['n'], r['sizes'], 'control' if r['control'] else '', r['end'], r['rounds_reached'], r['verdict'], 'at', r['read_at'],
              'ranks', r['ranks'], 'blocks', r['maximal_blocks'], r['largest_block'], 'check', r['checked_rounds'], r['check_equal'], 'stable', r['stability'], 'merges', r['merges'], 'max group', r['largest_group'], r['last_rounds'][-2:])


if __name__ == '__main__':
    main()
