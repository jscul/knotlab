"""Independent initial funding, preservation of separate live groups, and exact population weights."""

from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
import gzip
import json

from cycle_counts import OUT, classes, encode
from source_mechanisms import initial_read, named_witness, source_rank
from representatives import source_rows
from end_operator import from_stars, step


LAWS = ('parity','nae')
WEIGHTS = ('distinct','histories')


def unpack(code):
    length = len(code)
    flags = [x[0] for x in code]
    edges = [tuple(sorted((i,(i+1)%length))) for i in range(length)]
    def visit(parent, children):
        for flag, branches in children:
            child = len(flags)
            flags.append(flag)
            edges.append((parent,child))
            visit(child, branches)
    for parent, (_, children) in enumerate(code):
        visit(parent, children)
    return tuple(sorted(edges)), tuple(flags)


def follow(rows, law):
    end = from_stars(rows)
    history = []
    h = len(rows)
    w = len({x for support in rows for x in support})
    for age in range(1,5):
        turn = step(end,law)
        if turn.status == 'stall':
            return ('stalled',len(history),None,h,w), history
        assert turn.status == 'extend'
        h += len(turn.parents)
        w += sum(turn.fresh)
        profile = sorted((len(p),q) for p,q in zip(turn.parents,turn.fresh,strict=True))
        history.append([h,w,profile])
        if not any(turn.fresh):
            assert len(turn.fresh) == 1
            return ('closed',age,len(turn.parents[0]),h,w), history
        end = turn.end
    return ('open',len(history),None,h,w), history


def dumpz(path,data):
    with path.open('wb') as handle, gzip.GzipFile(fileobj=handle,mode='wb',mtime=0,filename='') as stream:
        stream.write((json.dumps(data,sort_keys=True,separators=(',',':'))+'\n').encode())


def anchored(n):
    outputs = {}
    for code, weight in classes(n).items():
        edges, flags = unpack(code)
        assert len(flags) == n and encode(n,edges,flags) == code
        first = initial_read(n,edges,flags)
        status = ('stalled' if first['shortages'] else
                  'separate_live_groups' if len(first['live_components']) >= 2 else
                  'paid_connected')
        physical = source_rows(n,edges,flags)
        whole = {}
        for law in LAWS:
            result, history = follow(physical,law)
            assert status != 'stalled' or (result[0],result[1]) == ('stalled',0)
            assert not (status == 'separate_live_groups' and result[0] == 'closed')
            assert not (len(code)%2 == 0 and status == 'paid_connected')
            whole[law] = (result,history)
        outputs[code] = (status,weight,whole)
    return outputs


def preliminary():
    for n in (6,7,8):
        totals = Counter()
        for code, (status, weight, whole) in anchored(n).items():
            result,_ = whole['parity']
            totals[(len(code),status,result[0])] += 1
            if result[0] == 'closed':
                print('CLOSURE',n,len(code),result,unpack(code),flush=True)
        print(n,totals,flush=True)


def raw_serial(path):
    # The producer emits one dictionary per line inside a JSON list.
    with gzip.open(path,'rt') as f:
        if f.readline().strip() != '[':
            f.seek(0)
            yield from json.load(f)
            return
        for line in f:
            line = line.strip()
            if line and line != ']':
                yield json.loads(line.rstrip(','))


def get_ratio(a,b):
    return str(Fraction(a,b)) if b else None


def leaf_stats(types):
    groups = {}
    for k, rows in sorted(types.items(),key=lambda entry:str(entry[0])):
        total = sum(rows.values())
        groups[str(k)] = {'denominator':total,'masses':dict(sorted(rows.items())),
                          'probability':{s:get_ratio(z,total) for s,z in sorted(rows.items())}}
    return groups


def main():
    comprehensive = {n:anchored(n) for n in (6,7,8)}
    path = OUT/'physical_population.json.gz'
    groups = {n:defaultdict(Counter) for n in comprehensive}
    unweighted = {n:Counter() for n in comprehensive}
    by_cycle = {n:defaultdict(Counter) for n in comprehensive}
    fees = {n:defaultdict(Counter) for n in comprehensive}
    by_age = {n:defaultdict(Counter) for n in comprehensive}
    ranking = []
    examples = {}
    seen = {n:set() for n in comprehensive}
    all_stalls = Counter()
    for row in raw_serial(path):
        n,ell = row['n'],row['cycle_length']
        code = encode(n,row['edges'],row['extra'])
        assert code not in seen[n] and len(code) == ell
        seen[n].add(code)
        initial, weights, history = comprehensive[n][code]
        assert row['labelled'] == weights['distinct'] and row['aut'] == weights['aut']
        k = weights['extras']
        priors = {w:weights[w] * 3 ** (n - k) for w in WEIGHTS}
        first = initial_read(n,row['edges'],row['extra'])
        if initial != 'stalled':
            sample_key = (n,len(code),sum(row['extra']),code)
            interests = {'double_witness':any(len(p['witnesses'])>1 for p in first['witnessed_pairs']),
                         'unheld_triple':bool(first['unheld_maximal_groups']),
                         'funded_connected':initial == 'paid_connected'}
            for role, fits in interests.items():
                if fits and (role not in examples or sample_key < examples[role][0]):
                    examples[role] = sample_key,row
        for law in LAWS:
            observed = row['laws'][law]
            compressed, trace = history[law]
            assert (observed['termination'],observed['age'],observed['terminal_arity'],observed['final_holders'],observed['final_width']) == compressed
            if observed['stall'] is not None:
                assert dict(observed['stall']['shortages']) == {int(h):s for h,s in first['shortages'].items()}
                all_stalls[(law,observed['stall']['attempted_age'])] += 1
            else:
                actual = [tuple(b['parents']) for b in observed['cuts'][0]['births']]
                assert Counter(actual) == Counter(first['funded_parents'])
            for cut, (h,w,profile) in zip(observed['cuts'],trace,strict=True):
                assert (h,w) == (cut['after_holders'],cut['after_names'])
                assert sorted((len(b['parents']),b['fresh']) for b in cut['births']) == profile
            terminal = observed['termination']
            cell = terminal if terminal != 'closed' else 'closing_admits' if observed['positive'] else 'closing_refuses'
            unweighted[n][law+'_'+cell] += 1
            excluded = 'initial_shortage' if initial=='stalled' else 'separate_live_groups' if initial=='separate_live_groups' else cell
            unweighted[n][law+'_structural_'+excluded] += 1
            for wt, mass in priors.items():
                groups[n][law+'_'+wt][cell] += mass
                groups[n][law+'_'+wt+'_structural'][excluded] += mass
                by_cycle[n][(ell,law,wt)][cell] += mass
                if terminal=='closed':
                    by_age[n][(law,wt)][observed['age']] += mass
                    fees[n][(law,wt)][f"cut-{observed['age']}_arity-{observed['terminal_arity']}_odd-{observed['positive']}"] += mass
        if row['laws']['parity']['termination'] == 'closed':
            rec = source_rank(row,code)
            ranking.append((rec,row))
    assert all(seen[n] == set(comprehensive[n]) for n in comprehensive)
    out = {'physical_archive_sha256':sha256(path.read_bytes()).hexdigest(),'size':{},'mixture':{},'first_stalls_by_attempted_age':{str(k):v for k,v in all_stalls.items()}}
    for n in comprehensive:
        out['size'][n]={'types':len(seen[n]),'unweighted':dict(unweighted[n]),'groups':leaf_stats(groups[n]),
                        'by_cycle_length':leaf_stats(by_cycle[n]),'closed_by_age_arity':{str(k):v for k,v in fees[n].items()}}
    for law in LAWS:
        for wt in WEIGHTS:
            field=law+'_'+wt
            mixed=Counter()
            for n in comprehensive:
                cells=groups[n][field]
                den=sum(cells.values())
                for k,a in cells.items():
                    mixed[k] += Fraction(a,den*len(comprehensive))
                closure = cells['closing_admits'] + cells['closing_refuses']
                odd_share = get_ratio(cells['closing_admits'],closure) if law=='parity' else None
                out['size'][n][field+'_odd_share_given_closure'] = odd_share
                out['size'][n].setdefault('endpoints',{})[field] = {
                    'source_mass':den,'covered_mass':den,'unresolved_mass':0,
                    'whole_closure_mass':closure,'single_odd_joint_mass':cells['closing_admits'] if law=='parity' else None,
                    'single_odd_conditional':odd_share,'signed_reading_applicable':law=='parity',
                    'closure_by_paid_cut':{age:by_age[n][(law,wt)][age] for age in range(1,5)},
                    'stall_by_attempted_cut':{age:(cells['stalled'] if age==1 else 0) for age in range(1,5)}}
            assert sum(mixed.values()) == 1
            closure=mixed['closing_admits']+mixed['closing_refuses']
            out['mixture'][field]={s:str(v) for s,v in mixed.items()} | {'closure':str(closure),'admitting_joint':str(mixed['closing_admits']) if law=='parity' else None,'odd_share_given_closure':str(mixed['closing_admits']/closure) if law=='parity' and closure else None}
    paths={}
    for sign, pool in [('ordinary',ranking),('operator',[(r,x) for r,x in ranking if x['laws']['parity']['positive']])]:
        if not pool:
            for ordering in ('whole','founder'):
                paths[sign+'_'+ordering]=None
            continue
        for ordering in ('whole','founder'):
            ordered = min(pool,key=lambda item:item[0] if ordering=='whole' else (item[0][2],item[0][5],item[0]))
            record, row = ordered
            key=sign+'_'+ordering
            paths[key]={'rank':record,'named':named_witness(row)}
    controls = {}
    for role, (key,row) in examples.items():
        controls[role] = named_witness(row)
    if 'funded_connected' in controls:
        ring = controls['funded_connected']['founder']['laws']['parity']
        count = controls['funded_connected']['n']
        assert all(len(c['births']) == count and all(len(b['parents'])==2 and b['fresh']==2 for b in c['births']) for c in ring['cuts'])
        assert controls['funded_connected']['fresh_sign_control'] is not None
    out['descriptive_funded_examples'] = {k:{'knots':a['n'],'edges':a['edges'],'flags':a['flags']} for k,a in controls.items()}
    dumpz(OUT/'mechanism_controls.json.gz',controls)
    out['ranked_minima']={k:None if v is None else v['rank'] for k,v in paths.items()}
    out['closed_types']=[{'rank':r,'operator':row['laws']['parity']['positive'],'cycle_length':len(r[-1]),'labelled':row['labelled'],'extra':sum(row['extra'])} for r,row in sorted(ranking,key=lambda x:x[0])]
    (OUT/'population_table.json').write_text(json.dumps(out,indent=2)+'\n')
    dumpz(OUT/'named_minima.json.gz',paths)
    print('verified', {n:len(x) for n,x in seen.items()},'closed',len(ranking),'mixture',out['mixture'])


if __name__=='__main__':
    import sys
    if '--initial-pass' in sys.argv:
        preliminary()
    else:
        main()
