"""Independent maximum shared occurrence/minimum gap over all admissible launch members."""
from pathlib import Path
import gzip
import hashlib
import json

import networkx as nx


HERE=Path(__file__).resolve().parent
OUT=HERE.parents[2]/'artifacts'/HERE.parent.name/HERE.name


def physical_role(x):
    if '.' in x:return x.replace('.','')
    if x.startswith('p') and x[1:].isdigit():return 'h'+x[1:]
    return x


def reach(g,lam):
    layers=[{('', 'Rb1')}]
    for i in range(1,lam+1):
        nxt=set()
        for prev,cur in layers[-1]:
            for v in g[cur]:
                if v==prev:continue
                if i<=3 and v!=('Rt','Rb2','a')[i-1]:continue
                if i>3 and v.startswith('R'):continue
                nxt.add((cur,v))
        assert nxt
        layers.append(nxt)
    return layers


def all_member_distance(g,row):
    word=tuple(row['true_phase']['originals'])
    m=len(word);lam=(m-1)//2
    layers=reach(g,lam)
    # The left arm is identical on every member; the certificate gives one such arm.
    launch=row['certificates'][0]['launch_anchor']
    fixed=launch[:m//2+1]
    types=set(fixed)|{v for layer in layers for _,v in layer}
    best=0
    for orient in (word,word[::-1]):
        for i,x in enumerate(orient):
            for depth,states in enumerate(layers):
                for prev,now in states:
                    if now!=x:continue
                    n=min(lam-depth+1,m-i)
                    if n>1 and orient[i+1]==prev:n=1
                    best=max(best,n)
    gap=min(nx.multi_source_dijkstra_path_length(g,set(word))[v] for v in types)
    assert bool(best)==(gap==0)
    lag=m-best if best else m+gap-1
    return {'eligible_launch_right_endpoint_states':len(layers[-1]),'maximum_common_originals':best,
            'minimum_original_gap':gap,'least_inclusive_parent_steps':lag}


def run():
    physical=json.loads(gzip.decompress((OUT/'physical.json.gz').read_bytes()))
    source=json.loads(gzip.decompress((OUT/'registered.json.gz').read_bytes()))
    variants={'inert_short':'short','active_sham':'one_port'}
    native={(variants.get(q['variant'],q['variant']),q['d']):q for q in physical['cases']}
    totals={'preparations':0,'sends':0,'strict_members':0,'calibration_sends':len(source['archived_direct_outputs'])}
    cells=[]
    for case in source['preparations']:
        raw=native[case['variant'],case['d']]
        g=nx.Graph()
        for a,b in raw['candidate_pairs']:g.add_edge(physical_role(a),physical_role(b))
        assert {frozenset(p) for p in g.edges}=={frozenset(p) for p in case['candidate_pairs']}
        assert dict(g.degree())==case['ordinary_live_degrees']
        totals['preparations']+=1
        for row in case['sends']:
            proof=all_member_distance(g,row)
            assert proof['least_inclusive_parent_steps']==row['inclusive_launch_separation']
            for cert in row['certificates']:
                assert cert['inclusive_hull_from_this_launch_member']['inclusive_lag']==proof['least_inclusive_parent_steps']
                ticks=cert['tick_sizes'];m=row['send_size'];n=row['strict_registration_size']
                assert ticks==list(range(24,n+1,24))
                assert cert['ticks_since_receiver_launch_anchor']==len([t for t in ticks if m<t<=n])
                incoming=cert['incoming_input']['originals'];target=row['true_phase']['originals']
                a,b=cert['incoming_to_send'][-1]
                assert incoming[a:b] in (target,target[::-1]) and len(incoming[a:b])==m
                for a,b in cert['sending_cut_c_ancestor_windows']:
                    assert b-a==m and all(x.startswith('c') for x in incoming[a:b])
                totals['strict_members']+=1
            cells.append({'variant':case['variant'],'d':case['d'],'send_size':m,**proof})
            totals['sends']+=1
    out=OUT/'cross_check.json'
    out.write_text(json.dumps({'verified':totals,'all_member_minima':cells},sort_keys=True,indent=2)+'\n')
    print(totals,hashlib.sha256(out.read_bytes()).hexdigest())


if __name__=='__main__':run()
