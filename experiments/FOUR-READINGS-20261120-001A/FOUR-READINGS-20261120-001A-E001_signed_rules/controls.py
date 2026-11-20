"""Negative controls, sign conventions, marker collisions and whole-record receipts."""
from collections import Counter
from itertools import combinations
import json
import os
import subprocess
import sys
import networkx as nx

from census import OUT, ROOT, pauli_solution, solve, verify_paulis, save
from games import allowed, state_word, tables, variation


def cancel_planar_words(ends, orders):
    """Use cyclic rotation, adjacent equal-pair cancellation and multiplication of signed equations."""
    n=len(orders)
    edge={frozenset(pair):i for i,pair in enumerate(ends)}
    words={u:[edge[frozenset((u,v))] for v in orders[str(u)]] for u in range(n)}
    steps=[]
    for u,v in reversed(list(nx.bfs_edges(nx.Graph(ends),0))):
        e=edge[frozenset((u,v))]
        a=words[u];b=words.pop(v)
        i=a.index(e);j=b.index(e)
        words[u]=a[i+1:]+a[:i]+b[j+1:]+b[:j]
        steps.append([u,v,e])
    word=words[0].copy()
    end=[]
    while word:
        i=next((i for i,x in enumerate(word) if x==word[(i+1)%len(word)]),None)
        assert i is not None and len(word)>=2
        rotated=word[i:]+word[:i]
        end.append([i,rotated[0]])
        word=rotated[2:]
    return dict(merged=steps,final_word=words[0],removed_adjacent=end)


def check_local_relations():
    """Canonical K1--K3 on every isolated support width used by the declared starts."""
    results=[]
    for width in range(3,8):
        names=[f'x{j}' for j in range(width)]
        for law in ('even','odd','nae'):
            excluded=[]
            for word in range(1<<width):
                parity=word.bit_count()%2
                allowed=(parity==0 if law=='even' else parity==1 if law=='odd' else word not in (0,(1<<width)-1))
                if not allowed:
                    excluded.append(' '.join(('~' if word>>j&1 else '')+name for j,name in enumerate(names)))
            command=[sys.executable,'-B','-m','knotlab','check','--cnf',';'.join(excluded),
                     '--loops',*names[:-1],'--contact',names[-1],'--json']
            report=json.loads(subprocess.check_output(command,cwd=ROOT,env=dict(os.environ,PYTHONPATH=str(ROOT/'tools'))))
            assert report['is_knot']
            results.append(dict(width=width,law=law,allowed=len(report['allowed']),K123=True))
    return results


def main():
    rows=json.loads((OUT/'census.json').read_text())
    changes=[]
    negative=[]
    scalar=[]
    for r in rows:
        ends=r['sharing']
        equations=[(sum(1<<i for i,p in enumerate(ends) if v in p),int(v==r['n']-1)) for v in range(r['n'])]
        assert solve(equations,r['m']) is None
        witnesses=[solve(equations[:j]+equations[j+1:],r['m']) for j in range(r['n'])]
        assert all(x is not None for x in witnesses)
        scalar.append(dict(atlas=r['atlas'],one_deletion_witnesses=witnesses))
        if not r['operator']:
            negative.append(dict(atlas=r['atlas'],**cancel_planar_words(ends,r['cyclic_orders'])))

        changed=pauli_solution(ends,{0})
        even=pauli_solution(ends,set())
        assert (changed is not None)==r['operator'] and even is not None
        if changed:
            assert all(x or z for p,x,z in changed)
        changes.append(dict(atlas=r['atlas'],odd_first=changed is not None,even=even is not None,
                            both_eigenvalues_on_every_distinction=bool(changed and all(x or z for p,x,z in changed))))
    save('sign_checks.json',changes)
    save('arbitrary_operator_refutations.json',negative)
    save('scalar_one_deletion_witnesses.json',scalar)
    mult=[]
    for name,ends in [('two_holders_three_distinctions',[(0,1)]*3),
                      ('all_four_pairs_one_doubled',list(combinations(range(4),2))+[(0,1)]),
                      ('three_by_three_one_doubled',list(nx.complete_bipartite_graph(3,3).edges)+[(0,3)])]:
        ops=pauli_solution(ends,{0})
        assert (ops is not None)==(not nx.check_planarity(nx.Graph(ends))[0])
        mult.append(dict(name=name,ends=ends,one_odd_paulis=ops,even_paulis=pauli_solution(ends,set())))
    keys=['n','m','arities','loop_count','has_odd_holder_loop','literal_Fano_piece','relaxed_Fano_four_triples']
    def collisions(fields):
        pairs=[(a,b) for a,b in combinations(rows,2) if a['operator']!=b['operator']
               and all(a[k]==b[k] for k in fields)]
        return [[a['atlas'],b['atlas']] for a,b in sorted(pairs,key=lambda ab:(ab[0]['m'],ab[0]['n'],ab[0]['atlas'],ab[1]['atlas']))]
    six=json.loads((OUT/'six_parts.json').read_text())
    assert all(all(s['K123']==[True,True,True] for s in r['stars'] if s['imposed'])
               for r in six if len(r['retained']) in range(1,6))
    trials=json.loads((OUT/'games.json').read_text())
    fair=trials['cube_all_pairs']
    a=sorted({r['inputs'][0] for r in fair});b=sorted({r['inputs'][1] for r in fair})
    biased=tables(trials['cube_stars'],a,b,7,shared_bias=True)
    assert variation(fair)==['0','0'] and variation(biased)!=['0','0']
    bad_sign_rejected=False
    pos=next(r for r in rows if r['operator'])
    tampered=[tuple(op) for op in pos['pauli_i_phase_X_bits_Z_bits']]
    p,x,z=tampered[0];tampered[0]=((p+2)%4,x,z)
    try:
        verify_paulis(pos['sharing'],tampered,{pos['n']-1})
    except AssertionError:
        bad_sign_rejected=True
    assert bad_sign_rejected
    positive_subset_groups=[[1],[2],[4],[0],[3,5,6,7],list(range(8,16))]
    source=nx.Graph((u,u^(1<<j)) for u in range(16) for j in range(4))
    assert all(nx.is_connected(source.subgraph(g)) for g in positive_subset_groups)
    assert all(any(source.has_edge(a,b) for a in lo for b in hi)
               for lo in positive_subset_groups[:3] for hi in positive_subset_groups[3:])
    receipt=dict(canonical_local_relations=check_local_relations(),parallel=mult,strict_positive_count=sum(t['both_eigenvalues_on_every_distinction'] for t in changes),
                 six_all_retained_stars_full_in_all_proper_nonempty_parts=True,
                 readings_with_fano_degree_and_loop_count=collisions([k for k in keys if k!='has_odd_holder_loop']),
                 readings_including_odd_length=collisions(keys), cube_biased_TV=variation(biased),
                 bad_sign_certificate_rejected=bad_sign_rejected,
                 four_label_subset_three_against_three=positive_subset_groups)
    save('additional_controls.json',receipt)
    print('strict operator witnesses',receipt['strict_positive_count'],'first collisions',receipt['readings_with_fano_degree_and_loop_count'][0],receipt['readings_including_odd_length'][0])
    h=json.loads((OUT/'growth_histories.json').read_text())
    print('sampled end fates',Counter((r['family'],law,t['stages'][-1]['status']) for r in h for law,t in r['laws'].items()))


if __name__=='__main__':
    main()
