"""Independent whole-round comparisons, using the no-take growth implementation."""
import argparse
import gzip
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from time import perf_counter

from growth import start

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
SEED = 26112643
A = 'tri:122@0'


def records(filename):
    with gzip.open(STUDY / filename, 'rt') as f:
        return [json.loads(line) for line in f]


def reads(state):
    parts, direct, classes = state.partition()
    def compare(a,b):
        if not a or not b:
            return [None]*3
        pa,pb = {parts[u] for u in a}, {parts[u] for u in b}
        same = bool(pa & pb)
        immediate = same or any((p in pa and q in pb) or (p in pb and q in pa) for p,q in direct)
        return [same, immediate, not {classes[u] for u in a}.isdisjoint(classes[u] for u in b)]
    a = [u for u in parts if state.role[u]==1]
    b = [u for u in parts if state.role[u]==2]
    broad_a = [u for u in parts if state.role[u]&1]
    broad_b = [u for u in parts if state.role[u]&2]
    near = state.distances()
    waited = [u for u in b if state.born[u] < state.r]
    return {'strict':compare(a,b), 'any_far_ancestor':compare(a,broad_b)[2],
            'any_receiver_ancestor':compare(broad_a,b)[2], 'both_inclusive':compare(broad_a,broad_b)[2],
            'near':min((near[u] for u in b),default=None),
            'waiting':min((near[u] for u in waited),default=None),
            'waited':{u:near[u] for u in waited}, 'parts':parts,'classes':classes}


def study(pilot):
    census = records('recede_runs.jsonl.gz')
    raw_parts = json.loads((STUDY / 'parts.json').read_text())
    original = {k.split()[0]:v for k,v in raw_parts.items()}
    original['n1:g1:3@0'] = original.pop('g1:3@0')
    original['n2:g3:22@0'] = original.pop('g3:22@0')
    rng = random.Random(SEED)
    rng.shuffle(census)
    canonical_sample = [r['B'] for r in census[:16]]
    if pilot:
        census = census[:3]
    structural = {}
    census_first = Counter()
    census_runs = []
    mismatches = Counter()
    lengths = Counter()
    ref_readings = Counter()
    checked_cells = Counter()
    all_waiters = {}
    for row in census:
        b = row['B']
        state = start(A,b,'CAP-3')
        labels = []
        inclusive = []
        all_wait = []
        for _ in range(16):
            state.step()
            r = state.r
            got = reads(state)
            labels.append(got['strict'])
            inclusive.append([got[k] for k in ('any_far_ancestor','any_receiver_ancestor','both_inclusive')])
            if r >= 3:
                all_wait.append(got['waited'])
            for k,val in [('own births',len(state.own)), ('nearest far member',got['near']),
                          ('nearest far member that waited',got['waiting'])]:
                checked_cells[k] += 1
                mismatches[k] += (r>len(row[k]) or row[k][r-1]!=val)
            if b in original:
                arr = original[b]
                mismatches['parts by round'] += (r>len(arr) or arr[r-1]!=got['strict'][2])
                checked_cells['parts by round'] += 1
                ref_readings['same part differs from class'] += got['strict'][0]!=got['strict'][2]
                ref_readings['direct differs from class'] += got['strict'][1]!=got['strict'][2]
            if len(state.h)>3000:
                break
        mismatches['census lengths'] += state.r!=row['rounds']
        lengths[str(state.r)] += 1
        if b in original:
            mismatches['parts lengths'] += len(original[b])!=state.r
        if all_wait:
            # No substitution of a different waiting knot at the same distance.
            for at,ws in enumerate(all_wait,3):
                if not ws:
                    continue
                fixed = [(u,d) for u,d in ws.items() if all(later.get(u)==d for later in all_wait[at-3:])]
                if fixed:
                    all_waiters[b] = {'from':at,'through':state.r,'fixed':sorted(fixed)}
                    break
        first = next((i for i,ls in enumerate(labels,1) if ls[2] is not True),None)
        key = ('all linked' if first is None else f'{first} {"absent" if labels[first-1][2] is None else "apart"}')
        census_first[key] += 1
        census_runs.append({'far':b, 'rounds':state.r, 'first_loss':key,
                           'class_after_round_3':labels[2][2], 'class_at_end':labels[-1][2]})
        if b in original or b in canonical_sample:
            structural[b] = {'recorded_parts':b in original,'strict_by_round':labels,
                             'inclusive_by_round':inclusive,'rounds':state.r}
    out = {'seed':SEED,'uniform_sample_without_replacement':canonical_sample,'census_runs':len(census),
           'census_class_records':census_runs,'rounds_reached':lengths,'census_first_loss_of_class_or_absence':census_first,
           'recounted_cells':checked_cells,'mismatches':mismatches,'parts_comparisons':ref_readings,
           'examples_and_recorded_parts':structural,'fixed_waiting_members':all_waiters}
    raw = records('second_runs.jsonl.gz')
    windows = defaultdict(list)
    for row in raw:
        if row['reading'] in ('horizon','change'):
            windows[row['A'],row['B'],row['law'],row['t0']].append(row)
    dists = {(r['A'],r['B'],r['law']):r['by round'] for r in raw if r['reading']=='far end distance'}
    group_counts = Counter()
    ord_short = Counter()
    official = []
    cases = [row for row in raw if row['reading']=='base']
    if pilot:
        cases = [next(row for row in cases if row['law']=='CAP-7' and row['B']=='g3:22@0')]
    for row in cases:
        a,b,law = (row[k] for k in ('A','B','law'))
        st = start(a,b,law)
        trace = []
        for _ in range(24):
            st.step()
            r = st.r
            view = reads(st)
            mismatches['18 own births'] += r>row['rounds'] or len(st.own)!=row['own births'][r-1]
            mismatches['18 distances'] += r>row['rounds'] or view['near']!=dists[a,b,law][r-1]
            trace.append({'r':r,'class':view['strict'][2], 'part':view['strict'][0],
                          'inclusive_far_with_strict_receiver':view['any_far_ancestor'],
                          'both_inclusive':view['both_inclusive'],'own_count':len(st.own),'short':len(st.short)})
            cls,pt = view['classes'],view['parts']
            own = [u for u in pt if st.role[u]==1]
            ac,ap = {cls[u] for u in own},{pt[u] for u in own}
            for w in windows[a,b,law,r]:
                u = w['knot']
                assert u in pt
                bucket = (w['reading'],law=='ORD',w['heard'] is not None, cls[u] in ac,pt[u] in ap)
                group_counts[str(bucket)] += 1
                if law=='ORD' and w.get('sign')=='bar':
                    test = st.copy()
                    test.mark(u,'bar')
                    test.step()
                    ord_short['barred']+=1
                    ord_short['changed knot short in next round']+=u in test.short
            if len(st.h)>6000:
                break
        mismatches['18 limits'] += (len(st.h),st.r)!=(row['knots'],row['rounds'])
        official.append({'receiver':a,'far':b,'law':law,'trace':trace})
    out.update({'main_runs':official,'site_cross_tab_fields':['reading','ordinary','heard','in receiver class','in receiver part'],
                'sites_by_reading':group_counts,'ordinary_far_bars':ord_short})
    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pilot',action='store_true')
    args=parser.parse_args()
    before = perf_counter()
    result = study(args.pilot)
    if not args.pilot:
        (HERE/'structure.json').write_text(json.dumps(result,indent=1)+'\n')
    print('seconds',round(perf_counter()-before,3),'runs',result['census_runs'],'mismatches',result['mismatches'])
