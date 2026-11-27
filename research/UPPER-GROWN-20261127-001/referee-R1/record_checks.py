"""Check the freeze, opportunity counts, two weightings, and the independent witness images."""
import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from math import factorial
from pathlib import Path
import subprocess
import sys
from time import perf_counter

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
STUDY = HERE.parent
QUERIES = [
    'edge colourings of cubic graphs with no monochromatic vertex',
    'closed not-all-equal systems',
    'six disjoint agreements eight lower clauses one layer up',
    'fresh distinction ordinary not-all-equal birth two-colouring',
    'PINNING cubic systems not-all-equal solvability counting',
]


def json_lines(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def prior_queries(pilot):
    output = {}
    for q in QUERIES[:1] if pilot else QUERIES:
        cmd = [sys.executable,'-B','scripts/track.py','objects',q,'--exclude',STUDY.name,
               '--until','2026-11-27','--limit','12','--json']
        result = json.loads(subprocess.check_output(cmd,cwd=ROOT))
        output[q] = {group: [dict(id=r['id'],record=r['record']) for r in result[group]] for group in ('index','other_epics')}
    return output


def weighting(rows):
    result = []
    for row in rows:
        g = nx.Graph(row['links'])
        automorphisms = sum(1 for _ in nx.isomorphism.GraphMatcher(g,g).isomorphisms_iter())
        result.append((row['boxes'],factorial(g.number_of_nodes())//automorphisms))
    positive = sum(count for boxes,count in result if boxes)
    total = sum(count for _,count in result)
    return {'classes_with_boxes':sum(bool(boxes) for boxes,_ in result),'all_classes':len(result),
            'labelled_with_boxes':positive,'labelled_total':total,'labelled_fraction':str(Fraction(positive,total)),
            'labelled_percent':round(100*positive/total,4)}


def freeze():
    entries = []
    for line in (STUDY/'frozen.sha256').read_text().splitlines():
        expected,name = line.split()
        blob = subprocess.check_output(['git','show',f'b35af0be04:{name}'],cwd=ROOT)
        current = (ROOT/name).read_bytes()
        assert sha256(blob).hexdigest()==expected==sha256(current).hexdigest()
        entries.append({'file':str(Path(name).name),'freeze_matches_working_file':True})
    return entries


def grade_control():
    # Signed output convention for the study's all-positive forbidden lower words.
    all_words = list(product((0,1),repeat=6))
    lower = [(a,b,c) for a in (0,1) for b in (2,3) for c in (4,5)]
    allowed = [w for w in all_words if all(not all(w[i] for i in t) for t in lower)]
    def upper(w):
        return tuple(w[i] ^ w[i+1] for i in (0,2,4))
    trimmed = [w for w in allowed if upper(w)!=(0,0,0)]
    images = {''.join(map(str,w)) for w in map(upper,trimmed)}
    assert len(images)==6 and all(len({tuple(w[i] for i in t) for w in trimmed})==7 for t in lower)
    return dict(abstract_lower_words=len(allowed),abstract_upper_words=len(set(map(upper,allowed))),
                restricted_lower_words=len(trimmed),restricted_upper_words=sorted(images),
                transversal_projections_with_seven_words=8)


def ring_and_pilots():
    main = [r for p in (STUDY/'out').glob('census_*') for r in json_lines(p)]
    sample = {r['start'] for r in main}
    return {p.name:{'starts':len(rows),'stage_records':sum(len(r['rounds']) for r in rows),
                    'overlap_with_confirmatory_sample':sorted(sample & {r['start'] for r in rows})}
            for p in sorted((STUDY/'pilot').glob('*.jsonl')) for rows in [json_lines(p)]}


def check_certificates(pilot):
    from knotlab.cli import main as check
    import contextlib, io
    from upper_readings import agree, columns
    grown = json.loads((HERE/'open_witness.json').read_text())
    tests = {'grown':(grown['grown_supports'],grown['six_disjoint_carriers'])}
    for pattern in ['four','pairs']:
        alternative = json.loads((HERE/f'upper_{pattern}_closed.json').read_text())[-1]['witness']
        tests[pattern]=(alternative['knots'],alternative['carriers'])
    sampled = json.loads((HERE/'upper_sample.json').read_text())[-1]['witness']
    tests['sample'] = (sampled['source'], [c for c,v in sampled['raw_agreements_and_selected_value']])
    results={}
    for name,(knots,carriers) in tests.items():
        n=max(max(k) for k in knots)+1
        universe,raw = columns(n)
        satisfies=[~agree(k,raw,universe) & universe for k in knots]
        allowed=universe
        for s in satisfies:
            allowed &= s
        reads=[agree(c,raw,universe) for c in carriers]
        def distribution(allowed):
            cells={'':allowed}
            for r in reads:
                cells={p+str(k):m for p,t in cells.items() for k,m in enumerate((t&~r,t&r)) if m}
            return {p:t.bit_count() for p,t in cells.items()}
        lower_counts=distribution(allowed)
        if name=='grown':
            tested=tuple(product((0,1),(2,3),(4,5)))
            build_upper=lambda w:tuple(w[i]^w[i+1] for i in (0,2,4))
            assert lower_counts==grown['source_states_by_raw_six_reading_word']
        else:
            if name=='sample':
                tested=sampled['lower_clauses']
                j=sampled['both_tests_pair']
                assert all(v==1 for _,v in sampled['raw_agreements_and_selected_value'])
                assert sorted(int(w,2) for w in lower_counts)==sampled['actual_lower_words']
            else:
                sample=json.loads((HERE/f'upper_{name}_closed.json').read_text())[-1]['witness']
                tested=sample['lower_clauses_missing_111']
                j=sample['and_pair']
            build_upper=lambda w:tuple(w[2*i]&w[2*i+1] if i==j else w[2*i]|w[2*i+1] for i in range(3))
        lower_words=[tuple(map(int,w)) for w in lower_counts]
        abstract=[w for w in product((0,1),repeat=6) if all(not all(w[k] for k in tri) for tri in tested)]
        assert all(w in abstract for w in lower_words)
        canonical=[]
        def check_image(image):
            missing=set(product((0,1),repeat=3))-set(image)
            clauses='; '.join(' '.join(('~' if b else '')+x for x,b in zip('PQR',w)) for w in sorted(missing))
            rows=[]
            for c in 'PQR':
                out=io.StringIO()
                with contextlib.redirect_stdout(out):
                    status=check(['check','--cnf',clauses,'--loops',*(x for x in 'PQR' if x!=c),'--contact',c,'--json'])
                r=json.loads(out.getvalue()); assert status==0 and r['is_knot']
                rows.append(r['is_knot'])
            return rows
        for tri in tested:
            canonical.extend(check_image(tuple(w[k] for k in tri) for w in lower_words))
        canonical.extend(check_image(map(build_upper,lower_words)))
        canonical.extend(check_image(map(build_upper,abstract)))
        upper_read=[0]*3
        for i,(a,b) in enumerate(zip(reads[::2],reads[1::2])):
            upper_read[i] = a^b if name=='grown' else (a&b if i==j else a|b)
        blocked=upper_read[0]&upper_read[1]&upper_read[2]
        restored=[]
        for k in range(len(knots)):
            st=blocked
            for q,s in enumerate(satisfies):
                if q!=k:
                    st &= s
            restored.append(st.bit_count())
        expected=([r['new_upper_111_states'] for r in grown['source_law_deletions']] if name=='grown'
                  else sampled['restored_upper_111_by_dropped_law'] if name=='sample' else sample['restorations_by_dropped_source_law'])
        assert restored==expected
        results[name]=dict(allowed_states=allowed.bit_count(),lower_words=len(lower_words),lower_conjunction_words=len(abstract),
                           restored_by_source_deletion=restored,canonical_role_checks=sum(canonical))
        if pilot:
            break
    return results


def symmetry_of_witness(pilot):
    data=json.loads((HERE/'open_full_pilot.json').read_text())['complete_constructed_start_and_grown_stage']
    def graph_of(knots, k0):
        g=nx.Graph()
        for i,k in enumerate(knots):
            g.add_node(('law',i),kind='start' if i<k0 else 'birth')
            for d in k:
                g.add_node(('name',d),kind='distinction')
                g.add_edge(('name',d),('law',i))
        return g
    def maps(g):
        return nx.isomorphism.GraphMatcher(g,g,node_match=lambda a,b:a['kind']==b['kind']).isomorphisms_iter()
    def key(box,mapping):
        paired=[]
        for a,b in zip(box[::2],box[1::2]):
            paired.append(tuple(sorted((tuple(sorted(mapping[x] for x in group)),v) for group,v in (a,b))))
        return tuple(sorted(paired))
    g=graph_of(data[1]['knots'],len(data[0]['knots']))
    shuffles=[{d[1]:v[1] for d,v in m.items() if d[0]=='name'} for m in maps(g)]
    original={key(b,{x:x for x in range(19)}) for b in data[1]['boxes']}
    orbit_sets={frozenset(key(b,m) for m in shuffles) for b in data[1]['boxes']}
    assert set().union(*orbit_sets)==original and sum(map(len,orbit_sets))==len(original)
    source_count=sum(1 for _ in maps(graph_of(data[0]['knots'],len(data[0]['knots']))))
    assert source_count==len(shuffles)==len({tuple(m[i] for i in range(17)) for m in shuffles})
    unordered=graph_of(data[1]['knots'],12)
    return {'automorphisms_of_source':source_count,'extensions_to_marked_round':len(shuffles),
            'all_final_symmetries':sum(1 for _ in maps(unordered)),
            'sizes_of_orbits_of_boxes_preserving_birth_history':sorted(map(len,orbit_sets))}


def replay_all_grown(pilot):
    from upper_readings import agree, columns, words
    records=json.loads((HERE/'open_full_pilot.json').read_text())['complete_constructed_start_and_grown_stage']
    source,grown=records
    assert source['box_count']==0 and len(grown['boxes'])==grown['box_count']==18
    universe,raw=columns(max(max(k) for k in grown['knots'])+1)
    laws=[universe ^ agree(k,raw,universe) for k in grown['knots']]
    masks=[]
    for drop in [-1,*range(len(laws))]:
        st=universe
        for i,s in enumerate(laws):
            if i!=drop:
                st &= s
        masks.append(st)
    results=[]
    for box in grown['boxes'][:1] if pilot else grown['boxes']:
        assert all(len(carrier)==3 and v==1 for carrier,v in box)
        cols=[agree(carrier,raw,universe) for carrier,_ in box]
        upper=[a^b for a,b in zip(cols[::2],cols[1::2])]
        assert words(masks[0],upper)==list(range(7))
        missing=upper[0]&upper[1]&upper[2]
        drops=[(m&missing).bit_count() for m in masks[1:]]
        results.append(drops)
    return {'initial_boxes':source['box_count'],'grown_boxes':grown['box_count'],'enumerated_boxes':len(results),
            'needing_both_births':sum(all(row[10:]) for row in results),
            'needing_all_laws':sum(all(row) for row in results),'restorations_in_open_full_order':results}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot',action='store_true')
    args=parser.parse_args()
    t=perf_counter()
    sys.path.insert(0,str(ROOT/'tools'))
    rows=[r for path in sorted((STUDY/'out').glob('cubic_12*')) for r in json_lines(path)]
    capped=[r for r in rows if r['boxes']>r['boxes read']]
    result=dict(freeze=freeze(),pilot=ring_and_pilots(),weighting=weighting(rows[:2] if args.pilot else rows),
                over_cap=[{'found':r['boxes'],'read':r['boxes read']} for r in capped],
                source_symmetries=symmetry_of_witness(args.pilot),all_grown_deletions=replay_all_grown(args.pilot),abstract_control=grade_control(),certificate_checks=check_certificates(args.pilot),prior_work=prior_queries(args.pilot))
    result['seconds']=perf_counter()-t
    print(result['weighting'],result['certificate_checks'],round(result['seconds'],3))
    if not args.pilot:
        (HERE/'record_checks.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':
    main()
