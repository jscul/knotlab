"""Run N2's comparison (BD2 7.3): for each law, knot law and start, every renamed run against the run on the
registered numbering: the whole structure after every round by its invariant (multiset of per-knot labels and a
Weisfeiler-Leman hash), and the multiset over pairs of the verdicts of BD2 6.1 to 6.3 with both courses from X only
in exact classes (ticket A's `wbc.Registry`: VF2 inside invariant buckets).

  python -B n2check.py
"""
import sys

sys.dont_write_bytecode = True

from collections import Counter, defaultdict

import common
from common import log
import eng  # noqa: F401  (puts the fold folder and ticket A's folder on the path)
import wbc


def main():
    common.check_frozen()
    common.cap_memory(6)
    groups = defaultdict(list)
    for rec in common.read_jsonl('runN2.jsonl.gz'):
        groups[(rec['law_id'], rec['law_name'].split('/')[-1], rec['start'])].append(rec)
    out = []
    tot = Counter()
    for key, recs in sorted(groups.items()):
        reg = wbc.Registry()
        sigs = {}
        for rec in recs:
            ms = Counter()
            for p in rec['pairs']:
                ca = reg.classify(p['course_A']) if p['course_A'] else None
                cb = reg.classify(p['course_barred']) if p['course_barred'] else None
                ms[(p['s'], p['link_verdict'], p['ancestral'], p['ancestral_every_member'], p['course_differs'],
                    p['dependence'], p['meeting_round'], ca, cb)] += 1
            for s, n in rec['no_meeting_pairs_by_s'].items():
                ms[(int(s), 'no meeting', n)] += 1
            sigs[rec['renaming']] = {'pairs': ms, 'inv': rec['structure_invariants'], 'rounds': rec['rounds_read'],
                                     'stop': rec['stop'], 'parts': rec['parts_by_s']}
        base_name = 'registered' if 'registered' in sigs else 'n000'
        base = sigs[base_name]
        for name, sg in sorted(sigs.items()):
            if name == base_name:
                continue
            inv_eq = sg['inv'] == base['inv'] and sg['rounds'] == base['rounds'] and sg['stop'] == base['stop']
            ver_eq = sg['pairs'] == base['pairs'] and sg['parts'] == base['parts']
            tot['compared'] += 1
            tot['invariant equal'] += inv_eq
            tot['verdicts and courses equal'] += ver_eq
            if not (inv_eq and ver_eq):
                log('DIFFERS', key, name, inv_eq, ver_eq)
            out.append({'law_id': key[0], 'knot_law': key[1], 'start': key[2], 'renaming': name,
                        'invariant_equal': inv_eq, 'verdicts_and_courses_equal': ver_eq,
                        'pairs_with_meeting': sum(v for k, v in sg['pairs'].items() if k[1] != 'no meeting'),
                        'strict': sum(v for k, v in sg['pairs'].items() if k[1] == 'only through made knots'),
                        'dependence': sum(v for k, v in sg['pairs'].items() if len(k) > 5 and k[5])})
        tot['course classes'] += reg.n
    res = {'totals': dict(tot), 'rows': out,
           'groups': {'|'.join(k): len(v) for k, v in sorted(groups.items())}}
    common.write_json('runN2_comparison.json', res)
    log(dict(tot))


if __name__ == '__main__':
    main()
