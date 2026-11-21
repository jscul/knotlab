"""Paid fixed preparations, finite forecasts and physical port-coupled counterfactuals."""
from collections import Counter, defaultdict
from dataclasses import replace
from hashlib import sha256
from itertools import pairwise
from pathlib import Path
from random import Random
import json
import sys

import networkx as nx

import model
sys.path.insert(1, str(model.PRIOR))
import cases

LAWS = ('nae', 'parity')
RULES = ('ordinary', 'spent', 'local')
OUT = model.ROOT / 'artifacts' / model.HERE.parent.name / model.HERE.name
source_from = cases.baseline.fixtures.source_from


def jsonbytes(item):
    return json.dumps(item, sort_keys=True, separators=(',', ':')).encode()


def receipt(step, age):
    row = cases.row(step, age)
    if step.status == 'extend':
        row['fresh_first'] = [f[0] if f else None for f in step.fresh]
    return row


def detour(lengths, edit):
    a, b = lengths
    n = 4 + a + b
    means = [range(4, 4 + a), range(4 + a, n)]
    pairs = [(0, 1), (0, 2), (1, 3)]
    for side, strand in enumerate(means):
        pairs.extend(pairwise((side, *strand)))
    stars = source_from(pairs, [0, 0] + [6] * (n - 2))
    return cases.additional_name(stars, 3 + a, n - 1) if edit else stars


def branch_price(h):
    pairs = [(0, 1), (0, 2), (0, 3), (1, 4), (1, 5)]
    supply = [0, 0, 3, 2, 2, 2]
    last = 2
    for i in range(h):
        t, x = len(supply), len(supply) + 1
        pairs.extend(((last, t), (t, x), (t, x)))
        supply.extend((0, 1 if i == h - 1 else 2))
        last = x
    source = source_from(pairs, supply)
    return source, cases.baseline.extra(source, last)


def remaining_detour(physical, key):
    a, b = next(pair for pair, bits in physical.shared.items() if key in bits)
    if len(physical.shared[a,b]) > 1:
        return 1
    graph = physical.graph.copy()
    graph.remove_edge(a, b)
    return nx.shortest_path_length(graph, a, b) if nx.has_path(graph, a, b) else None


def rooted_graph(record, boundary_counts=True, radius=2):
    a, b, name = record['root']
    graph = nx.Graph()
    physical = nx.Graph()
    physical.add_nodes_from(k for k, _, _ in record['holders'])
    physical.add_edges_from((u, v) for u, v, _ in record['shared'])
    at_boundary = {k for k in physical if min(nx.shortest_path_length(physical, p, k)
                                               for p in (a, b)) == radius}
    for k, loose, degree in record['holders']:
        counts = (loose, degree) if boundary_counts or k not in at_boundary else (None, None)
        graph.add_node(('h', k), label=('holder', k in (a, b), *counts))
    for u, v, names in record['shared']:
        for d in names:
            graph.add_node(('n', d), label=('name', d == name))
            graph.add_edge(('n', d), ('h', u))
            graph.add_edge(('n', d), ('h', v))
    return graph


def isomorphic(records, annotations=True):
    return nx.is_isomorphic(*(rooted_graph(rec, annotations) for rec in records),
                            node_match=lambda a,b:a['label'] == b['label'])


def rename(stars, bit, seed):
    rng = Random(seed)
    ids = list(range(len(stars)))
    rng.shuffle(ids)
    names = sorted(set().union(*map(set, stars)))
    targets = names[:]
    rng.shuffle(targets)
    translate = dict(zip(names, targets, strict=True))
    grown = [None] * len(stars)
    for old, row in enumerate(stars):
        grown[ids[old]] = tuple(translate[d] for d in row)
    return tuple(grown), translate[bit]


def available(record, radius):
    graph = nx.MultiGraph()
    w, z, bit = record['root']
    for a, b, names in record['shared']:
        for n in names:
            graph.add_edge(a, b, key=n)
    local = graph.subgraph(model.ball(graph, w, z, radius)).copy()
    local.remove_edge(w, z, key=bit)
    return not nx.has_path(local, w, z)


def central(detail, physical, key, donors):
    ordinary, _, _ = model.propose(physical, 'ordinary', 8192)
    union = tuple(sorted(donors))
    base = Counter(v for group in ordinary for v in group)
    extra = Counter(v for group in detail.added for v in group)
    i = detail.parents.index(union) if detail.status == 'extend' and union in detail.parents else None
    target = []
    for k in union:
        source = physical.loose[k]
        target.append(dict(holder=k, supply=source, ordinary=base[k], added=extra[k],
                           unary_remainder=len(source)-base[k]-extra[k],
                           paid_children=[(j, row, len(detail.fresh[j])) for j, row in enumerate(detail.parents)
                                          if detail.status == 'extend' and k in row]))
    return dict(status=detail.status, funded=detail.funded, proposed=union in detail.added,
                name_eligible=any(r[0]==key for r in detail.bridges), actual=i is not None,
                focal_inputs=detail.inputs[i] if i is not None else None,
                focal_grant=len(detail.fresh[i]) if i is not None else None,
                donors=target, births=len(detail.parents) if detail.status=='extend' else None,
                whole_grant=sum(map(len, detail.fresh)) if detail.status=='extend' else None,
                shortages=detail.shortages)


def history(stars, law, rule, marks, depth):
    targets = [{k} for k in marks]
    first = None
    exact = None
    rows = []
    for age in range(depth):
        detail = model.step(stars, law, rule)
        rows.append(receipt(detail, age))
        if age == 1 and first is None and model.read(stars).loose:
            old = model.read(stars)
            groups, _, _ = model.propose(old, rule, 8192)
            if groups is not None and all(len(b) >= sum(k in g for g in groups)
                                          for k,b in old.loose.items()):
                d = cases.separation(old, groups, *targets)
                exact = d+1 if isinstance(d, int) else d
        if detail.status != 'extend':
            if first is None and detail.status in ('stall', 'closed'):
                exact = 'never'
            break
        targets = [{len(stars)+i for i, ps in enumerate(detail.parents) if aim.intersection(ps)}
                   for aim in targets]
        if first is None and targets[0] & targets[1]:
            first = age+1
        if age >= 2:
            assert not detail.bridges and not detail.next_added
        stars = detail.stars
    return {'actions':rows, 'first_observed':first, 'first_certified':first or exact}


def detour_rows():
    results = {}
    for lengths in ((1,1),(2,2),(2,3),(3,3),(5,5),(8,8)):
        starts = [detour(lengths, edit) for edit in (False, True)]
        physical = [model.read(s) for s in starts]
        key = physical[0].shared[0,1][0]
        donors = (2, 3, 4, 4+lengths[0])
        records = [model.rooted_record(p, key) for p in physical]
        renamed = [rename(s, key, 20261120850+i) for i, s in enumerate(starts)]
        alt = [model.rooted_record(model.read(s), k) for s, k in renamed]
        assert all(isomorphic(rs) for rs in zip(records, alt, strict=True))
        detach = [remaining_detour(p,key) for p in physical]
        arm = {'holdings':starts,'rooted_records':records,'renamed_records':alt,
               'same_addressed_record':records[0]==records[1],'isomorphic_under_renaming':isomorphic(alt),
               'isomorphic_without_boundary_counts':isomorphic(records,False),
               'detour_meetings':detach,'radius_one_no_detour':[available(r,1) for r in records],
               'radius_two_no_detour':[available(r,2) for r in records], 'laws':{}}
        for law in LAWS:
            pair = []
            for j, (s,p) in enumerate(zip(starts,physical,strict=True)):
                cases.baseline.law_record(s,law)
                policies = {}
                for rule in RULES:
                    current = model.step(s,law,rule)
                    item = central(current,p,key,donors)
                    item['first_cut'] = receipt(current,0)
                    hist = history(s,law,rule,(2,3),2)
                    item.update((k,v) for k,v in hist.items() if k!='actions')
                    if lengths==(3,3) and rule=='local':
                        suppressed = model.step(s,law,rule,suppress_name=key)
                        item['same_cut_suppressed']=central(suppressed,p,key,donors)
                        item['suppressed_receipt']=receipt(suppressed,0)
                    policies[rule]=item
                pair.append(policies)
            arm['laws'][law]=pair
        results['+'.join(map(str,lengths))]=arm
    return results


def all_controls():
    output={}
    for name,(source,r,s,depth) in cases.frames().items():
        both={}
        for law in LAWS:
            cases.baseline.law_record(source,law)
            both[law]={rule:history(source,law,rule,(r,s),depth) for rule in RULES}
        output[name]={'holdings':source,'marks':[r,s],'laws':both}
    return output


def labels_for(slots, before):
    counts=Counter()
    keys=[]
    for group in slots:
        ps=tuple(sorted(before[k] for k in group))
        keys.append((ps,counts[ps]))
        counts[ps]+=1
    return keys


def coupled_ports(stars, steps, keys, previous, tokens):
    """Give a common child the very same previous input tokens at every common true parent."""
    common=sorted(set(keys[0]) & set(keys[1]))
    remaining=[]
    allocations=[]
    for i in range(2):
        opens=model.read(stars[i]).loose
        remaining.append({previous[i][p]:{tokens[i][bit]:bit for bit in bs} for p,bs in opens.items()})
        allocations.append({})
    for group in common:
        for p in group[0]:
            token=min(remaining[0][p].keys() & remaining[1][p].keys())
            for i in range(2):
                allocations[i][(group,p)]=remaining[i][p].pop(token)
    for i in range(2):
        for group in keys[i]:
            for p in group[0]:
                if (group,p) not in allocations[i]:
                    token=min(remaining[i][p])
                    allocations[i][group,p]=remaining[i][p].pop(token)
    for group in common:
        assert all(tokens[0][allocations[0][group,p]] == tokens[1][allocations[1][group,p]] for p in group[0])
    result=[]
    for i in range(2):
        inputs=tuple(tuple(allocations[i][key,previous[i][p]] for p in ps)
                     for key,ps in zip(keys[i],steps[i].parents,strict=True))
        assert all(not pool for pool in remaining[i].values())
        born=tuple(bs+fs for bs,fs in zip(inputs,steps[i].fresh,strict=True))
        result.append(replace(steps[i],stars=stars[i]+born,inputs=inputs))
    return result


def compare_sets(values, seen, sets):
    cohorts=[{key:values[i][j] for j,key in enumerate(seen[i]) if j in sets[i]} for i in range(2)]
    a,b=cohorts
    return {'total':[len(a),len(b)],'matched':len(a.keys() & b.keys()),
            'unmatched':[len(a.keys()-b.keys()),len(b.keys()-a.keys())],
            'changed_grants':[(key,a[key],b[key]) for key in sorted(a.keys() & b.keys()) if a[key]!=b[key]]}


def private_pair(starts, law):
    stars=list(starts)
    previous=[{j:j for j in range(len(s))} for s in stars]
    tokens=[{bit:(0,bit,0) for row in s for bit in row} for s in stars]
    tags=[{'A':{2},'G':set()} for _ in range(2)]
    result=[]
    for age in range(1,5):
        details=[model.step(s,law,'local') for s in stars]
        step_status=[d.status for d in details]
        row={'age':age,'status':step_status}
        if any(st!='extend' for st in step_status):
            row['arms']=[receipt(d,age-1) for d in details]
            result.append(row)
            break
        keys=[labels_for(d.parents,ps) for d,ps in zip(details,previous,strict=True)]
        ids={key:n for n,key in enumerate(sorted(set(keys[0])|set(keys[1])))}
        details=coupled_ports(stars,details,keys,previous,tokens)
        values=[[len(fs) for fs in d.fresh] for d in details]
        result_tags=[]
        for i,d in enumerate(details):
            old=tags[i]
            new={'A':{n for n,ps in enumerate(d.parents) if old['A'].intersection(ps)}}
            if age==1:
                new['G']={d.parents.index((2,3,4,5))}
            else:
                new['G']={n for n,ps in enumerate(d.parents) if old['G'].intersection(ps)}
            result_tags.append(new)
        row['arms']=[receipt(d,age-1) for d in details]
        row['ancestry']={tag:compare_sets(values,keys,[t[tag] for t in result_tags]) for tag in ('A','G')}
        for i,d in enumerate(details):
            first=len(stars[i])
            for j,new in enumerate(d.fresh):
                for n,bit in enumerate(new):
                    tokens[i][bit]=(age,ids[keys[i][j]],n)
            previous[i]={first+j:ids[k] for j,k in enumerate(keys[i])}
            tags[i]={tag:{first+n for n in indices} for tag,indices in result_tags[i].items()}
            stars[i]=d.stars
        result.append(row)
    return result


def price_controls():
    result={}
    for h in (1,2,3):
        starts=branch_price(h)
        physical=[model.read(s) for s in starts]
        key=physical[0].shared[0,1][0]
        records=[model.rooted_record(p,key) for p in physical]
        laws={}
        for law in LAWS:
            for s in starts:
                cases.baseline.law_record(s,law)
            laws[law]={'first':[{r:central(model.step(s,law,r),p,key,(2,3,4,5)) for r in RULES}
                                for s,p in zip(starts,physical,strict=True)],
                       'physical_match':private_pair(starts,law)}
        result[h]={'holdings':starts,'rooted_records_equal':records[0]==records[1],
                   'rooted_records':records,'laws':laws}
    return result


def shortage():
    old,_,_=cases.pace_train(4)
    p=model.read(old)
    cut=p.loose[15][-1]
    short=tuple(tuple(b for b in row if b!=cut) if k==15 else row for k,row in enumerate(old))
    assert len(short[15])>=3
    key=p.shared[1,2][0]
    result={'holdings':[old,short],'lost_loose':cut,'holder':15,'laws':{}}
    records=[model.rooted_record(model.read(s),key) for s in (old,short)]
    result.update(rooted_records=records, records_equal=records[0]==records[1])
    for law in LAWS:
        cells=[]
        for s in (old,short):
            cases.baseline.law_record(s,law)
            physical=model.read(s)
            cells.append({rule:central(model.step(s,law,rule),physical,key,(0,3,4,5)) for rule in RULES})
        result['laws'][law]=cells
    return result


def main():
    OUT.mkdir(exist_ok=True,parents=True)
    for filename,make in [('detours',detour_rows),('old_controls',all_controls),
                          ('private_edits',price_controls),('remote_shortage',shortage)]:
        out=OUT/(filename+'.json')
        out.write_bytes(jsonbytes(make())+b'\n')
        print(filename,out.stat().st_size,sha256(out.read_bytes()).hexdigest(),flush=True)


if __name__=='__main__':
    main()
