"""Check which finite NAE reached populations satisfy the all-size structural promise."""
from collections import Counter,defaultdict
from itertools import combinations
import gzip
import json
import networkx as nx

from tree_reading import OUT, read_definition


def classify(rows):
    who=defaultdict(list)
    for i,row in enumerate(rows):
        for name in row:
            who[name].append(i)
    pairs=[(a,b) for holders in who.values() if len(holders)==2 for a,b in [tuple(holders)]]
    assert all(len(x) in (1,2) for x in who.values())
    threes={i for i,h in enumerate(rows) if len(h)==3}
    ternary=nx.Graph()
    ternary.add_nodes_from(threes)
    ternary.add_edges_from((a,b) for a,b in pairs if a in threes and b in threes)
    parts=list(map(set,nx.connected_components(ternary)))+[{i} for i in range(len(rows)) if i not in threes]
    index={h:k for k,p in enumerate(parts) for h in p}
    between=[(index[a],index[b]) for a,b in pairs if index[a]!=index[b]]
    graph=nx.Graph()
    graph.add_nodes_from(range(len(parts)))
    graph.add_edges_from(between)
    assert nx.is_connected(graph)
    return {'covered':len(between)==len(parts)-1,'parts':len(parts),'links_between_parts':len(between),
            'all_ternary':len(threes)==len(rows),'whole_holding_is_tree':len(pairs)==len(rows)-1}


def main():
    with gzip.open(OUT/'census_cases.json.gz','rt') as f:
        cases=json.load(f)['nae']
    summary=Counter()
    bywidth=defaultdict(Counter)
    residual=[]
    for row in cases:
        if row['first_status']!='births':
            continue
        stage=row['stage_rows']
        val=classify(stage)
        val['source_width']=row['source_width']
        for t in ('covered','all_ternary','whole_holding_is_tree'):
            summary[t]+=val[t];bywidth[row['source_width']][t]+=val[t]
        summary['total']+=1
        bywidth[row['source_width']]['total']+=1
        if val['covered']:
            result=read_definition(stage,True)
            assert result['recovered_exact_relation']
        else:
            residual.append({'source_width':row['source_width'],'source':row['source_rows'],'stage_width':row['stage_width'],
                             'reached':stage,'next_count':row['next_birth_count'],**val})
    residual.sort(key=lambda r:(r['source_width'],r['stage_width'],len(r['source']),r['source']))
    out={'summary':dict(summary),'by_source_width':bywidth,'first_outside':residual[0] if residual else None,
         'all_outside':residual}
    (OUT/'class_coverage.json').write_text(json.dumps(out,indent=2)+'\n')
    print(summary,residual[:1])


if __name__=='__main__':
    main()
