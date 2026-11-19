"""UNIQUE-TABLE-20261119-001A readout: G and U1-U6.  Run: .venv/bin/python -B readout.py runs/unique-table [runs/unique-table-amend] -> summary.json (an ok record in a later run
replaces a timed-out one)."""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from longrun import load_results  # noqa: E402


def verdict(r):
    if r['forced_spans_C']:
        return 'same_state_rival' if r['same_code_rivals'] else 'unique'
    om = r.get('one_missing', {})
    if om.get('applicable') and not om.get('capped'):
        if om['codes_matching_other_than_C']:
            return 'other_equations_candidate'
        return 'same_state_rival' if r['same_code_rivals'] else 'unique_one_missing'
    return 'undecided'


def main(*out_dirs):
    recs = {}
    for d in out_dirs:
        for c, r in load_results(d).items():
            if c not in recs or r["status"] == "ok":
                recs[c] = r
    s = {'case_status': dict(Counter(r['status'] for r in recs.values()))}
    pop = [r['result'] for c, r in recs.items() if c.startswith('pop') and r['status'] == 'ok']
    ctrl = [r['result'] for c, r in recs.items() if c.startswith('ctrl') and r['status'] == 'ok']
    dev = [st for c, r in recs.items() if c.startswith('dev') and r['status'] == 'ok' for st in r['result']['stages']]
    s['G_rivals_verified'] = all(r['rivals_verified'] for r in pop + ctrl + dev)
    s['G_rivals_found'] = {'population': sum(r['same_code_rivals'] > 0 for r in pop), 'controls': sum(r['same_code_rivals'] > 0 for r in ctrl),
                           'dev': sum(r['same_code_rivals'] > 0 for r in dev)}
    s['same_code_capped'] = sum(r['same_code_capped'] for r in pop + ctrl)
    for name, rows in (('population', pop), ('controls', ctrl)):
        v = Counter(verdict(r) for r in rows)
        s[f'{name}_stages'] = len(rows)
        s[f'{name}_verdicts'] = dict(v)
        s[f'{name}_by_connectivity'] = {c: dict(Counter(verdict(r) for r in rows if r['connectivity'] == c))
                                        for c in sorted({r['connectivity'] for r in rows})}
        s[f'{name}_forcing_spans'] = sum(r['forced_spans_C'] for r in rows)
        s[f'{name}_forced_rank_gap'] = dict(Counter(r['rank_C'] - r['rank_F'] for r in rows))
        s[f'{name}_one_missing'] = dict(Counter(
            ('capped' if r['one_missing'].get('capped') else ('other' if r['one_missing'].get('codes_matching_other_than_C') else 'none'))
            if r.get('one_missing', {}).get('applicable') else 'not_applicable' for r in rows if not r['forced_spans_C']))
    s['U1_forcing_spans_fraction'] = round(s['population_forcing_spans'] / max(1, len(pop)), 4)
    s['U2_other_equation_candidates'] = sum(verdict(r) == 'other_equations_candidate' for r in pop + ctrl)
    closed = [r for r in pop if r['connectivity'] == 'zero']
    s['U3_closed'] = {'stages': len(closed), 'with_same_state_rival': sum(r['same_code_rivals'] > 0 for r in closed),
                      'decided': sum(verdict(r) != 'undecided' for r in closed)}
    three = [r for r in pop + ctrl if r['connectivity'] == 'three' and verdict(r) != 'undecided']
    agree = Counter()
    for r in three:
        crit = r['loose'] >= 3 and r['max_loose_at_one_junction'] <= 1
        agree[(crit, r['same_code_rivals'] > 0)] += 1
    s['U4_three_connected_criterion_vs_rival'] = {f'criterion={a},rival={b}': c for (a, b), c in agree.items()}
    decided = [r for r in pop if verdict(r) != 'undecided']
    s['U5_decided_with_same_state_rival'] = f"{sum(r['same_code_rivals'] > 0 for r in decided)} of {len(decided)}"
    s['U6_controls_with_same_state_rival'] = f"{sum(r['same_code_rivals'] > 0 for r in ctrl)} of {len(ctrl)}"
    s['population_by_junctions'] = {str(k): dict(Counter(verdict(r) for r in pop if r['junctions'] == k))
                                    for k in sorted({r['junctions'] for r in pop})}
    s['undecided_examples'] = [[r['key'], r['round'], r['rank_C'] - r['rank_F']] for r in pop if verdict(r) == 'undecided'][:8]
    s['rival_examples'] = [[r['key'], r['round'], r['rival_examples'][:1]] for r in pop if r['same_code_rivals']][:4]
    dest = ROOT / 'artifacts/UNIQUE-TABLE-20261119-001A/UNIQUE-TABLE-20261119-001A-E001_unique'
    dest.mkdir(parents=True, exist_ok=True)
    (dest / 'summary.json').write_text(json.dumps(s, indent=1))
    print(json.dumps(s, indent=1))


if __name__ == '__main__':
    main(*sys.argv[1:])
