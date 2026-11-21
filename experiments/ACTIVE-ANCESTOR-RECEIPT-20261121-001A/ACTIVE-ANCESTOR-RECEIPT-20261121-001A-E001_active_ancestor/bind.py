"""Bind every enrolled signal, middle interval and gate history to the literal paid cuts."""
from hashlib import sha256
from itertools import combinations, pairwise
from pathlib import Path
import gzip
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import clock


def normalized(role):
    return role.replace('.', '')


def portion(word, i, j):
    return {'trim_left':i, 'trim_right':len(word)-j,
            'remaining_ends':[word[i],word[j-1]], 'remaining_rank':j-i}


def census():
    physical_path = clock.OUTPUT / 'physical.json.gz'
    receipt_path = clock.OUTPUT / 'receipts.json.gz'
    physical = json.loads(gzip.decompress(physical_path.read_bytes()))
    receipts = json.loads(gzip.decompress(receipt_path.read_bytes()))
    sources = {c['case']:c for c in physical['cases']}
    expected = {c.name:c for c in clock.cases()}
    rows = []
    for observed in receipts['cases']:
        name = observed['case']
        source = sources[name]
        middle = clock.Middle(expected[name])
        ids = {normalized(role):i for role,i in source['live_roles'].items()}
        actual_pairs = {frozenset((normalized(a),normalized(b))) for a,b in source['candidate_pairs']}
        assert actual_pairs == {frozenset(edge) for edge in middle.graph.edges}
        c_mark = {a for a,b,n,h,w in source['circuit_arcs'] if n==3 and h==4}
        u_mark = {a for a,b,n,h,w in source['circuit_arcs'] if n==5 and h==4}
        assert c_mark == middle.c_nodes and c_mark|u_mark == middle.mixed_nodes
        assert {(a,b) for a,b,_,_,_ in source['circuit_arcs']} == set(middle.steps.edges)
        for law,record in source['laws'].items():
            first = {}
            for b in record['cuts'][0]['births']:
                for p in combinations(b['parents'],2):
                    key=frozenset(p)
                    assert key not in first
                    first[key]=b
            second = {frozenset(b['parents']):b for b in record['cuts'][1]['births'] if len(b['parents'])==2}
            for row in observed['rows']:
                for key in row['first_members']:
                    receipt=observed['receipts'][key]
                    right=tuple(receipt['right']);m=row['m']
                    word=clock.old.left(len(right))+('Rb1',)+right
                    outside=word[1:]
                    blocks=[]
                    for i,(u,v) in enumerate(pairwise(outside)):
                        literal=first[frozenset((ids[u],ids[v]))]
                        true_roles=clock.prior.tile(u,v,middle.cells)
                        assert set(literal['parents']) == {ids[w] for w in true_roles}
                        assert literal['grant'] == clock.price(middle,outside[i:i+2])
                        blocks.append(literal['holder'])
                    joins=[];shared_joins=[]
                    for i,(u,v) in enumerate(pairwise(blocks)):
                        literal=second[frozenset((u,v))]
                        assert literal['grant']==clock.price(middle,outside[i:i+3])
                        joins.append(literal['holder'])
                        if middle.cells and literal['holder']==record['gate_history']['through']['holder']:
                            shared_joins.append({**portion(outside,i,i+3),'first_paid':list(blocks[i:i+2]),
                                                 'joint_paid':literal['holder'],'joint_paid_names':literal['consumed_names']})
                    send=[portion(outside,i,i+m) for i in receipt['complete_signal_in_outside']]
                    assert send and not receipt['complete_signal_in_inside']
                    ancestors={group:[portion(outside,i,j) for i,j in arr['size_m_positions']]
                               for group,arr in receipt['ancestors'].items()}
                    rows.append({'case':name,'law':law,'m':m,'reader':row['reader'],'receipt':key,
                                 'incoming_rank':len(outside),'all_original_pair_births':blocks,
                                 'all_adjacent_block_joins':joins,'incoming_to_send':send,
                                 'incoming_to_middle':ancestors,'incoming_to_shared_ternary_join':shared_joins})
    return {'source_hash':sha256(physical_path.read_bytes()).hexdigest(),
            'receipt_hash':sha256(receipt_path.read_bytes()).hexdigest(),
            'trim_rule':'Apply trim_left deletions of the far left, then trim_right deletions of the far right. Each link is one complete actual endpoint parent. First and second original births indexed from the incoming word, position zero.',
            'records':rows}


if __name__=='__main__':
    result=census()
    out=clock.OUTPUT / 'bound_histories.json.gz'
    out.write_bytes(gzip.compress(json.dumps(result,separators=(',',':'),sort_keys=True).encode()+b'\n',mtime=0))
    print(f"{len(result['records'])} paid reader-history and original-roster bonds across both laws")
