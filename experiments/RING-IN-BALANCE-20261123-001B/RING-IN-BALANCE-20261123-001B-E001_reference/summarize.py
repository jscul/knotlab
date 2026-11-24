"""Verdicts of ticket B: gate G and P1 to P7 with the numbers behind them, from b1.json, b3_a4.json, b4.json, b5.json,
census_count.json, the census (census_io.load_census: the runner's census/results.jsonl and census/extra_blocks.jsonl;
or the runner directory given as the first argument) and p3_census_detail.json (p3_detail.py).  Readings are those of
deviations.md.  Writes summary.json (and census_tables.json when the census is complete)."""
import json
import os
import sys
from collections import Counter, defaultdict

from bref import OUT, ROOT, canonical_loose, census_stars, graph_autos, graph_edges, is_cycle_graph, load, write
from census_io import has_off, law_view, load_census

V = {}
CENSUS_DIR = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(OUT, 'census')
LAWS = ('ordinary', 'two', 'three')
WAITING = {'ordinary': False, 'two': True, 'three': True}
KINDS = ('stalled', 'jammed', 'stopped', 'returns giving parts off', 'returns giving none off',
         'grows to the bound with no return found', 'not completed')


def verdict(name, ok, numbers):
    word = {True: 'HOLDS', False: 'FAILS', None: 'PENDING (census)'}[ok]
    V[name] = {'verdict': word, 'numbers': numbers}
    print('%-5s %-17s %s' % (name, word, json.dumps(numbers, sort_keys=True) if not isinstance(numbers, str)
                              else numbers))


# --------------------------------------------------------------------------------------------------- P3 tallies

def p3_tally():
    keys = ('all', 'size 1-3', 'size 4+', 'ring-like', 'not ring-like', 'the ring itself', 'ring-like, not uniform',
            's even', 's odd')
    return {'runs_with_off': 0, 'y_all_waited': 0, 'by': {k: [0, 0] for k in keys}}


def p3_add(tal, rets):
    """rets: every return giving parts off of one run, as dicts with size, ring_like, ring_itself, s, copy_all_waited,
    y_all_waited."""
    if rets:
        tal['runs_with_off'] += 1
    for d in rets:
        w = int(bool(d['copy_all_waited']))
        tal['y_all_waited'] += int(bool(d['y_all_waited']))
        keys = ['all', 'size 1-3' if d['size'] <= 3 else 'size 4+',
                'ring-like' if d['ring_like'] else 'not ring-like', 's even' if d['s'] % 2 == 0 else 's odd']
        if d['ring_itself']:
            keys.append('the ring itself')
        elif d['ring_like']:
            keys.append('ring-like, not uniform')
        for k in keys:
            tal['by'][k][0] += 1
            tal['by'][k][1] += w


def full_detail(d):
    sh = d['shape']
    uniform = len(set(zip(sh['h'], sh['k']))) == 1
    return {'s': d['s'], 't': d['t'], 'size': d['part_size'], 'n_off': d['n_off'], 'off_sizes': d['off_sizes'],
            'copy_all_waited': d['copy_all_waited'], 'copy_n_waited': d['copy_n_waited'],
            'y_all_waited': d['y_all_waited_in_s'], 'ring_like': d['ring_like'],
            'ring_itself': d['ring_like'] and uniform, 'h': sh['h'], 'k': sh['k'], 'metsets': sh['metset_sizes']}


def part_class(d):
    if d['ring_itself']:
        return 'the ring itself (%d members, h = %d)' % (d['size'], d['h'][0])
    if d['ring_like']:
        return 'ring-like, not uniform (%d members)' % d['size']
    if d['size'] <= 3:
        return 'small part (%d members)' % d['size']
    return 'other (%d members)' % d['size']


# ------------------------------------------------------------------------------------------------------- main

def main():
    cc = load('census_count.json')
    b1 = load('b1.json')
    a4 = load('b3_a4.json')
    b4 = load('b4.json')
    b5 = load('b5.json')
    census, cstate = load_census(CENSUS_DIR)
    detail = None
    if census is not None and os.path.exists(os.path.join(OUT, 'p3_census_detail.json')):
        detail = load('p3_census_detail.json')
    gate_a = json.load(open(os.path.join(ROOT, 'artifacts', 'RING-IN-BALANCE-20261123-001A',
                                         'RING-IN-BALANCE-20261123-001A-E001_ring', 'gate.json')))
    out = {}
    live = [s for s in census['starts'] if not s.get('set_aside') and not s.get('timeout')] if census else []

    # ---------------------------------------------------------------------------------------------------- G
    g = {}
    g['ticket A gate (gate.json, all computed items)'] = {
        'ok': bool(gate_a['all_computed_ok']), 'items': {k: v['ok'] for k, v in gate_a['items'].items()}}
    kt = b1['knot_tests']
    g['every B1 start passes the parity knot test (both methods agree)'] = {
        'ok': all(v['parity_all_pass'] and not v['disagree'] for v in kt.values()), 'starts': len(kt),
        'fail': [k for k, v in kt.items() if not v['parity_all_pass']]}
    g['not-all-equal test of each B1 start (reported)'] = {
        'ok': None, 'pass': sum(v['nae_all_pass'] for v in kt.values()), 'of': len(kt),
        'fail': {k: v['nae_fail'] for k, v in kt.items() if not v['nae_all_pass']}}
    sd = b1['same_D2_DW']
    g['D2(n,3) and DW(n,3) the same roster at every round under each law'] = {
        'ok': all(v['all_same'] for v in sd.values()), 'pairs': len(sd),
        'rounds_compared': sum(len(v['rows']) for v in sd.values()),
        'method': sorted({x[2] for v in sd.values() for x in v['rows'] if len(x) > 2})}
    ordn = {('B1', k): v for k, v in b1['ordinary'].items()}
    ordn.update({('B4', k): v['ordinary'] for k, v in b4['runs'].items()})
    ordn[('B5', 'generator')] = b5['ordinary']
    g['ordinary law: no part gives parts off, no knot a member for two rounds (B1, B4, B5)'] = {
        'ok': all(v['ok'] for v in ordn.values()), 'runs': len(ordn),
        'stalled_rounds': sum(v['stalled_rounds'] for v in ordn.values()),
        'fail': [list(k) for k, v in ordn.items() if not v['ok']],
        'B1 strong form (descendants of a part never in two parts)': all(v['ok_strong'] for v in b1['ordinary'].values())}
    if census is not None:
        bad = [s for s in live if not law_view(s, 'ordinary')['ord']['ok']]
        nc = [s for s in live if s['laws']['ordinary'].get('not_completed')]
        g['ordinary law: no part gives parts off, no knot a member for two rounds (B2 census)'] = {
            'ok': not bad, 'runs': len(live), 'fail': [[s['g'], s['loose']] for s in bad[:10]],
            'runs_that_stall': sum(1 for s in live if law_view(s, 'ordinary')['ord']['stalled_rounds']),
            'stalled_rounds': sum(law_view(s, 'ordinary')['ord']['stalled_rounds'] for s in live),
            'runs not completed (checked over their completed rounds only)': [
                {'g': s['g'], 'loose': s['loose'], 'rounds_completed': s['laws']['ordinary']['rounds_completed'],
                 'round_not_completed': s['laws']['ordinary']['round_not_completed']} for s in nc]}
    else:
        g['ordinary law (B2 census)'] = {'ok': None, 'state': cstate}
    computed = [v['ok'] for v in g.values() if v['ok'] is not None]
    pending = any(v['ok'] is None and 'state' in v for v in g.values())
    print('Gate G, item by item:')
    for k, v in g.items():
        print('   %-92s %s' % (k, {True: 'pass', False: 'FAIL', None: 'reported / pending'}[v['ok']]))
    verdict('G', (all(computed) if not pending else (None if all(computed) else False)),
            {k: {kk: vv for kk, vv in v.items() if kk != 'items'} for k, v in g.items()})
    out['G'] = g

    # --------------------------------------------------------------------------------------------------- P1
    rows = {}
    for fam in ('D2', 'DW'):
        for n in range(3, 13):
            for law in ('two', 'three'):
                p = b1['P1']['%s(%d,3)|%s' % (fam, n, law)]
                ec, oc = p.get('even_chain'), p.get('odd_chain')
                rows['%s(%d,3)|%s' % (fam, n, law)] = {
                    'start_one_part_past_start': p['start_parts'] == 1 and p['start_past_start'],
                    'even_chain_full_n_off': bool(ec and ec['full_chain_n_off']),
                    'even_steps': ec['n_steps'] if ec else 0, 'even_n_offs': ec['n_offs'] if ec else [],
                    'odd_chain_full_n_off': bool(oc and oc['full_chain_n_off']),
                    'odd_steps': oc['n_steps'] if oc else 0, 'odd_n_offs': oc['n_offs'] if oc else [],
                    'kind': b1['runs']['%s(%d,3)|%s' % (fam, n, law)]['kind']}
    p1_bad = [k for k, v in rows.items() if k.startswith('D2(') and k.endswith('|two') and
              int(k[3:k.index(',')]) >= 4 and not (v['start_one_part_past_start'] and v['even_chain_full_n_off'])]
    verdict('P1', not p1_bad, {'D2 n=4..12 under the two added rules, chain from round 0 returning at rounds 2, 4, ..., 12 '
                               'with n parts off each time': 'all 9 hold' if not p1_bad else p1_bad,
                               'D2(3,3) two added rules (no prediction)': rows['D2(3,3)|two'],
                               'DW n=4..12 two added rules, same chain': all(
                                   rows['DW(%d,3)|two' % n]['even_chain_full_n_off'] for n in range(4, 13)),
                               'three added rules, same chain (reported)': all(
                                   rows['%s(%d,3)|three' % (f, n)]['even_chain_full_n_off'] for f in ('D2', 'DW')
                                   for n in range(4, 13)),
                               'odd chain from round 1, two added rules: returns every two rounds with n parts off':
                                   all(rows['%s(%d,3)|two' % (f, n)]['odd_chain_full_n_off'] for f in ('D2', 'DW')
                                       for n in range(4, 13)),
                               'odd chain from round 1, three added rules: n_offs': sorted({
                                   tuple(rows['%s(%d,3)|three' % (f, n)]['odd_n_offs']) for f in ('D2', 'DW')
                                   for n in range(4, 13)})})
    out['P1_rows'] = rows

    # --------------------------------------------------------------------------------------------------- P3
    groups, worst = {}, {}

    def consider(key, cand, info):
        if key not in worst or cand < worst[key][0]:
            worst[key] = (cand, info)

    for src, runs in (('B1', b1['runs']), ('A4', a4['runs'])):
        for k, v in runs.items():
            w = 'waiting' if v['waiting_law'] else 'no waiting'
            rets = [full_detail(d) for d in (v.get('off_all') or [])]
            p3_add(groups.setdefault((src, w), p3_tally()), rets)
            knots0 = {'D2': 2 * v['n'], 'DW': 2 * v['n']}.get(v.get('family'), v['n'])
            for d in rets:
                if w == 'no waiting' or not d['copy_all_waited']:
                    consider((src, w), (knots0, d['size'], d['s'], d['t']), {'run': k, **d})
    if detail is not None:
        for r in detail['runs']:
            w = 'waiting' if WAITING[r['law']] else 'no waiting'
            p3_add(groups.setdefault(('B2', w), p3_tally()), r['returns'])
            for d in r['returns']:
                if w == 'no waiting' or not d['copy_all_waited']:
                    consider(('B2', w), (r['n'], r['members'], d['size'], d['s'], d['t']),
                             {'start_g': r['g'], 'loose': r['loose'], 'law': r['law'],
                              'stars': census_stars(r['g'], r['loose']), **d})
    p3 = {'%s|%s' % k: v for k, v in sorted(groups.items())}
    wait_bad = sum(v['by']['all'][0] - v['by']['all'][1] for k, v in groups.items() if k[1] == 'waiting')
    nowait_off = sum(v['by']['all'][0] for k, v in groups.items() if k[1] == 'no waiting')
    ring_itself = {('%s|%s' % k): v['by']['the ring itself'] for k, v in sorted(groups.items())}
    p3_ok = (wait_bad == 0 and nowait_off == 0)
    if detail is None:
        p3_ok = False if not p3_ok else None
    verdict('P3', p3_ok, {
        'tallies: [returns giving parts off, of them with every copy member waited] by class': p3,
        'returns under waiting laws whose copy did not all wait': wait_bad,
        'returns giving parts off under laws without waiting': nowait_off,
        'beside it: returns whose part is the ring itself (cycle of met pairs, every member the same h, k): '
        '[returns, all waited]': ring_itself,
        'smallest counterexamples': {'%s|%s' % k: v[1] for k, v in sorted(worst.items())},
        'census included': detail is not None,
        'census detail rerun mismatches': detail['n_mismatches'] if detail else None})
    out['P3'] = {'tallies': p3, 'counterexamples': {'%s|%s' % k: v[1] for k, v in worst.items()}}
    out['P3_by_law'] = {}
    for src, runs in (('B1', b1['runs']), ('A4', a4['runs'])):
        for k, v in runs.items():
            dets = [full_detail(d) for d in (v.get('off_all') or [])]
            if not dets:
                continue
            lk = '%s|%s' % (src, v['law_name'] if src == 'A4' else v['law'])
            t = out['P3_by_law'].setdefault(lk, {'waiting_law': v['waiting_law'], 'runs': 0, 'n': 0,
                                                 'copy_all_waited': 0, 'ring_itself': 0, 'sizes': set()})
            t['runs'] += 1
            t['n'] += len(dets)
            t['copy_all_waited'] += sum(d['copy_all_waited'] for d in dets)
            t['ring_itself'] += sum(d['ring_itself'] for d in dets)
            t['sizes'] |= {d['size'] for d in dets}
    if detail is not None:
        for r in detail['runs']:
            lk = 'B2|%s' % r['law']
            t = out['P3_by_law'].setdefault(lk, {'waiting_law': WAITING[r['law']], 'runs': 0, 'n': 0,
                                                 'copy_all_waited': 0, 'ring_itself': 0, 'sizes': set()})
            t['runs'] += 1
            t['n'] += len(r['returns'])
            t['copy_all_waited'] += sum(d['copy_all_waited'] for d in r['returns'])
            t['ring_itself'] += sum(d['ring_itself'] for d in r['returns'])
            t['sizes'] |= {d['size'] for d in r['returns']}
    for t in out['P3_by_law'].values():
        t['sizes'] = sorted(t['sizes'])

    # --------------------------------------------------------------------------------------------------- P6
    p6a = {k: v['P6a'] for k, v in b4['runs'].items() if 'P6a' in v}
    a_ok = all(v['all_formula_ok'] and v['all_lineage_ok'] for v in p6a.values())
    rn2 = {k: v['all_p2_f2'] for k, v in b4['runs'].items() if v['leftovers'] == 'none'}
    rem = {k: {'max_spread_by_round_12': v['max_spread_by_round_12'], 'pf_with_spread_over_4': v['pf_with_spread_over_4']}
           for k, v in b4['runs'].items() if v['leftovers'] == 'removed'}
    b_ok = all(rn2.values()) and any(v['max_spread_by_round_12'] > 4 for v in rem.values())
    verdict('P6', a_ok and b_ok, {
        '(a) knots checked': {k: [v['checked'], v['formula_ok'], v['e_formula_counts']] for k, v in p6a.items()},
        '(a) e from the line of descent (stretches shorter than the ring): checked, equal, r=L+j-1, p=j+e, D=L-j+2': {
            k: [v['short_stretch'], v['lineage_e_equal'], v['round_free_ok'], v['p_ok'], v['D_ok']]
            for k, v in p6a.items()},
        '(a) greatest spread of rounds among knots of equal (p, f) on full rings': {
            k: b4['runs'][k]['max_spread_by_round_12'] for k in p6a},
        '(b) Ring(n,2): every knot p = 2, f = 2': rn2,
        '(b) leftovers removed: greatest spread by round 12': {k: v['max_spread_by_round_12'] for k, v in rem.items()},
        '(b) holds on each such ring alone': all(v['max_spread_by_round_12'] > 4 for v in rem.values()),
        'rounds done': {k: v['rounds_done'] for k, v in b4['runs'].items()}})
    out['P6_tables'] = {k: v['pf_table'] for k, v in b4['runs'].items()}

    # --------------------------------------------------------------------------------------------------- P7
    verdict('P7', b5['P7_ok'], {'rounds_done': b5['rounds_done'], 'knots': b5['knots'], 'failures': b5['n_fail'],
                                'least f by round (bound (t+9)/5)': {k: [v['min_f'], v['bound']]
                                                                    for k, v in b5['bound_by_round'].items()},
                                'births': b5['births'], 'fresh': b5['fresh']})
    out['P7_table'] = b5['pf_table']

    # ------------------------------------------------------------------------------------------- census (B2)
    if census is None:
        for p in ('P2', 'P4', 'P5'):
            verdict(p, None, 'census state: %s' % cstate)
    else:
        census_part(census, live, detail, out)
    out['census_count'] = {k: cc[k] for k in ('total', 'dead_total', 'ok')}
    out['verdicts'] = V
    write('summary.json', out)


def census_part(census, live, detail, out):
    starts = census['starts']
    assert len(starts) == 86032, len(starts)
    timeouts = [s for s in starts if s.get('timeout')]
    aside = [s for s in starts if s.get('set_aside')]
    disagree = [s for s in starts if 'kt' in s and s['kt']['disagree']]
    by = {(s['g'], tuple(s['loose'])): s for s in starts}
    det = {}
    if detail is not None:
        for r in detail['runs']:
            det[(r['g'], tuple(r['loose']), r['law'])] = r['returns']
    tables = {'starts': defaultdict(int), 'set_aside': defaultdict(int), 'kinds': {}, 'share_off': {},
              'start_timeouts': len(timeouts), 'knot_test_disagreements': len(disagree),
              'mixed_parts': sum(law_view(s, l)['mixed'] for s in live for l in LAWS),
              'runs_cut_off': {l: sum(1 for s in live if law_view(s, l)['cut']) for l in LAWS},
              'sources': dict(Counter(census['sources'].values())),
              'blocks_from_extra': sorted(c for c, v in census['sources'].items() if v == 'extra_blocks')}
    for s in starts:
        tables['starts']['%d|%d' % (s['n'], s['loose'].count(0))] += 1
    for s in aside:
        tables['set_aside']['%d|%d' % (s['n'], s['dead'])] += 1
    tables['set_aside_total'] = len(aside)
    tables['set_aside_examples'] = [{'stars': census_stars(s['g'], s['loose']), 'rank_fail': s['kt']['rank_fail'],
                                     'cut_fail': s['kt']['cut_fail']}
                                    for s in sorted(aside, key=lambda s: (s['n'], s['edges']))[:3]]
    nc = {}
    for law in LAWS:
        rows = [s for s in live if s['laws'][law].get('not_completed')]
        nc[law] = [{'g': s['g'], 'loose': s['loose'], 'stars': census_stars(s['g'], s['loose']),
                    'reason': s['laws'][law]['reason'], 'rounds_completed': s['laws'][law]['rounds_completed'],
                    'round_not_completed': s['laws'][law]['round_not_completed'],
                    'partial_kind_facts': {k: s['laws'][law]['partial'][k] for k in ('event', 'n_ret', 'n_off', 'knots')}
                    if s['laws'][law]['partial'] else None,
                    'next_round': s['laws'][law]['next_round']} for s in rows]
    tables['not_completed'] = nc
    for law in LAWS:
        kt = defaultdict(Counter)
        sh = defaultdict(lambda: [0, 0, 0])
        for s in live:
            key = '%d|%d' % (s['n'], s['dead'])
            c = s['laws'][law]
            kt[key]['not completed' if c.get('not_completed') else c['kind']] += 1
            ho = has_off(s, law)
            sh[key][0] += 1
            sh[key][1] += int(ho is True)
            sh[key][2] += int(ho is None)
        tables['kinds'][law] = {k: {kk: v[kk] for kk in KINDS if v[kk]} for k, v in sorted(kt.items())}
        tables['kinds_total'] = tables.get('kinds_total', {})
        tables['kinds_total'][law] = {kk: sum(v[kk] for v in kt.values()) for kk in KINDS}
        tables['share_off'][law] = {k: {'with': v[1], 'of': v[0], 'unknown': v[2],
                                        'share': round(v[1] / v[0], 4) if v[0] else None}
                                    for k, v in sorted(sh.items())}
    tables['starts'] = dict(sorted(tables['starts'].items()))
    tables['set_aside'] = dict(sorted(tables['set_aside'].items()))

    def first_off_class(s, law):
        rets = det.get((s['g'], tuple(s['loose']), law))
        if not rets:
            return None
        return part_class(min(rets, key=lambda d: (d['s'], d['t'])))

    def classes_of(s, law):
        rets = det.get((s['g'], tuple(s['loose']), law)) or []
        return dict(Counter(part_class(d) for d in rets))

    # P2
    c4 = [s for s in live if s['dead'] == 0 and s['n'] <= 4 and has_off(s, 'two')]
    u4 = [s for s in live if s['dead'] == 0 and s['n'] <= 4 and has_off(s, 'two') is None]
    c5 = [s for s in live if s['dead'] == 0 and s['n'] == 5 and has_off(s, 'two')]
    c5_bad = [s for s in c5 if not is_cycle_graph(s['g'])]
    verdict('P2', not c4 and not c5_bad and not u4, {
        'all-live starts of <= 4 knots with a return giving parts off (two added rules)': len(c4),
        'of them not completed': len(u4),
        'examples (<= 4)': [{'stars': census_stars(s['g'], s['loose']), 'first_off': s['laws']['two']['first_off'],
                             'classes': classes_of(s, 'two')}
                            for s in sorted(c4, key=lambda s: (s['n'], s['edges']))[:5]],
        'all-live five-knot starts with one': len(c5),
        'of them not the five-cycle': len(c5_bad),
        'examples not the five-cycle': [{'stars': census_stars(s['g'], s['loose']), 'edges': graph_edges(s['g']),
                                         'first_off': s['laws']['two']['first_off'], 'classes': classes_of(s, 'two')}
                                        for s in sorted(c5_bad, key=lambda s: (s['edges'], s['g'], s['loose']))[:6]],
        'five-cycle starts among them': len(c5) - len(c5_bad),
        'all-live five-knot five-cycle starts in the census (not set aside)': sum(
            1 for s in live if s['dead'] == 0 and s['n'] == 5 and is_cycle_graph(s['g']))})

    # P4
    p4 = [s for s in live if s['members'] < 5 and has_off(s, 'two')]
    p4s = sorted(p4, key=lambda s: (s['members'], s['n'], s['edges'], s['g'], s['loose']))
    verdict('P4', bool(p4), {'census starts with < 5 members and a return giving parts off (two added rules)': len(p4),
                             'by members': dict(sorted(Counter(s['members'] for s in p4).items())),
                             'by knots|dead': dict(sorted(Counter('%d|%d' % (s['n'], s['dead']) for s in p4).items())),
                             'fewest members, first examples': [
                                 {'stars': census_stars(s['g'], s['loose']), 'members': s['members'], 'n': s['n'],
                                  'first_off': s['laws']['two']['first_off'], 'classes': classes_of(s, 'two')}
                                 for s in p4s[:6]]})

    # P5
    cls = Counter()
    matched_set = set()
    skipped = Counter()
    pairs_list = defaultdict(list)
    for s in starts:
        if s['n'] != 6 or s['loose'].count(0) != 1:
            continue
        v = s['loose'].index(0)
        lo = list(s['loose'])
        lo[v] = 1
        m = by[(s['g'], canonical_loose(tuple(lo), graph_autos(s['g'])))]
        if s.get('set_aside') or m.get('set_aside'):
            skipped['dead start set aside' if s.get('set_aside') else 'matched start set aside'] += 1
            continue
        a, b = has_off(s, 'two'), has_off(m, 'two')
        if a is None or b is None:
            skipped['a run not completed'] += 1
            continue
        matched_set.add((m['g'], tuple(m['loose'])))
        c = 'both' if a and b else 'only with the dead knot' if a else 'only the other' if b else 'neither'
        cls[c] += 1
        if c != 'neither' and len(pairs_list[c]) < 3:
            pairs_list[c].append({'dead_start': census_stars(s['g'], s['loose']),
                                  'matched_start': census_stars(m['g'], m['loose'])})
    p5_ok = cls['only with the dead knot'] > cls['only the other']
    verdict('P5', p5_ok, {'pairs': dict(cls), 'pairs not counted': dict(skipped),
                          'distinct matched starts': len(matched_set), 'examples': dict(pairs_list),
                          'share with a return giving parts off, two added rules, by "knots|dead knots"':
                              {k: [v['with'], v['of'], v['share']] for k, v in tables['share_off']['two'].items()}})

    # smallest starts with a return giving parts off
    smallest = {}
    for law in LAWS:
        for dead in (False, True):
            cand = [s for s in live if has_off(s, law) and (s['dead'] > 0) == dead]
            cand.sort(key=lambda s: (s['n'], s['members'], s['edges'], s['g'], s['loose']))
            rows = []
            for s in cand[:6]:
                c = law_view(s, law)
                rows.append({'n': s['n'], 'members': s['members'], 'dead': s['dead'],
                             'stars': census_stars(s['g'], s['loose']), 'edges': graph_edges(s['g']),
                             'loose': s['loose'], 'kind': c['kind'], 'first_off': c['first_off'],
                             'first_off_class': first_off_class(s, law), 'classes': classes_of(s, law),
                             'n_off_returns': c['n_off']})
            smallest['%s|%s' % (law, 'with dead knot' if dead else 'every knot live')] = {
                'count': len(cand), 'first': rows}
    tables['smallest_with_return_giving_parts_off'] = smallest
    cl = {}
    for law in LAWS:
        c = Counter()
        for s in live:
            rets = det.get((s['g'], tuple(s['loose']), law)) or []
            for d in rets:
                c[part_class(d).split(' (')[0]] += 1
            if rets:
                c['runs with the ring itself among them'] += int(any(d['ring_itself'] for d in rets))
                c['runs'] += 1
        cl[law] = dict(c)
    tables['classes_of_returning_parts'] = cl
    tables['resources'] = {'case_seconds_total': round(sum(census['case_seconds']), 1),
                           'case_seconds_max': round(max(census['case_seconds']), 1),
                           'case_peak_mb': census['case_peak_mb'],
                           'start_seconds_max': max(s['sec'] for s in starts)}
    out['census'] = tables
    write('census_tables.json', tables)


if __name__ == '__main__':
    main()
