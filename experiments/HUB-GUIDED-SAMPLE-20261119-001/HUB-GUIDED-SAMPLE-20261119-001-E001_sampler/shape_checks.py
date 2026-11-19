"""Compare block and replacement diagnostics against direct subsets on small inputs."""
from itertools import combinations, product
from pathlib import Path
from tempfile import TemporaryDirectory
import json
from group_profile import Stage, members, pack


def test():
    counter = dict(graphs=0,large_maximal_groups=0,replacement_choices=0)
    with TemporaryDirectory() as directory:
        filename = Path(directory)/'input.txt'
        for n in range(3,6):
            pairs = list(combinations(range(n),2))
            for mark in range(1 << len(pairs)):
                edges={frozenset(pair) for j,pair in enumerate(pairs) if mark>>j&1}
                def clique(seq):
                    return all(frozenset(pair) in edges for pair in combinations(seq,2))
                valid=[[v for v in range(n) if mask>>v&1] for mask in range(1,1<<n)]
                peaks=[row for row in valid if len(row)>=3 and clique(row) and
                       not any(clique(row+[v]) for v in range(n) if v not in row)]
                # Alternate between input pair blocks and already held maxima.
                blocks=[tuple(sorted(e)) for e in edges]
                if mark.bit_count()%2:
                    blocks+=list(map(tuple,peaks))
                if not blocks:continue
                filename.write_text(f'{n} {len(blocks)}\n'+''.join(' '.join(map(str,b))+'\n' for b in blocks))
                stage=Stage(filename)
                counter['graphs']+=1
                for group in peaks:
                    counter['large_maximal_groups']+=1
                    profile=stage.profile(group,details=True)
                    G=set(group)
                    exact=min([3]+[k for k in (1,2) for choice in combinations(blocks,k)
                                   if G<=set().union(*choice)])
                    assert exact==(len(profile['cover_up_to_two']) if profile['cover_up_to_two'] else 3)
                    choices=[[w for w in range(n) if w not in G and frozenset((w,u)) not in edges and
                              clique([v for v in G if v!=u]+[w])] for u in group]
                    assert profile['partner_upper']==sum(bool(c) for c in choices)
                    best=0
                    for alts in product(*[[None]+c for c in choices]):
                        live=[w for w in alts if w is not None]
                        if clique(live):best=max(best,len(live))
                        counter['replacement_choices']+=1
                    pairs_w=profile['witness_pairs']
                    assert profile['partner_lower']<=best<=profile['partner_upper']
                    assert clique([w for u,w in pairs_w])
                    assert all(w in choices[group.index(u)] for u,w in pairs_w)
                stage.hood.cache_clear()
    return counter


if __name__=='__main__':
    print(json.dumps(test(),indent=1))
