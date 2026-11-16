"""Aggregate every paid search trial, failure, and exact return in the bound depth panel."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
from statistics import median
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TICKET = HERE.name
OUT = ROOT/'artifacts'/TICKET/(TICKET+'-E001_supplied_fold')
ROUTES = {'factor':'', 'pair':'peel-'}
ARMS = tuple(prefix+arm for prefix in ROUTES.values() for arm in ('primitive','named','flat'))


def read_json(path):
    return json.loads(path.read_bytes())


def samples(folder):
    streams = {}
    for raw in (folder/'results.jsonl').read_text().splitlines():
        record = json.loads(raw)
        if record['status'] != 'ok':
            raise ValueError(f"runner failed for {record['case']}: {record['status']}: {record['error']}")
        case = record['result']
        file = folder/case['file']
        if hashlib.sha256(file.read_bytes()).hexdigest() != case['sha256']:
            raise ValueError(f'cost receipt changed at {file}')
        with gzip.open(file,'rt') as source:
            items = [json.loads(line) for line in source]
        streams[(case['cache'],case['arm'],case['repeat'])] = {r['id']:r for r in items}
    if len(streams) != 36:
        raise ValueError('incomplete measured streams')
    return streams


def measure(row, truth):
    s = row['result']
    w, t = s['work'], s['timing']
    return dict(exact=int(s.get('truth')==truth and s.get('circuit') is not None),
                tests=w['binary_placement_trials']+w['ternary_placement_tests'],
                binary=w['binary_placement_trials'], compound=w['ternary_placement_tests'],
                reads=w['factor_truth_bit_reads'], uses=s.get('template_uses',0),
                nands=s.get('expanded_NANDs') or 0, search_cpu_ns=t['search_cpu_ns'],
                search_wall_ns=round(t['search_seconds']*1e9), build_ns=round(t['build_seconds']*1e9),
                verify_ns=round(t['verification_seconds']*1e9),
                reported_wall_ns=row['wall_ns'], total_cpu_ns=row['cpu_ns'],
                setup_ns=row['setup_wall_ns'])


def totals(records):
    result=Counter()
    for record in records:
        result.update(record)
    return dict(result)


def summarize(folder=OUT):
    streams=samples(folder)
    public={r['id']:r for r in read_json(folder/'public.json')}
    grading=read_json(folder/'grading.json')
    measures={}
    for key, rows in streams.items():
        if rows.keys()!=public.keys():
            raise ValueError(f'missing tasks in {key}')
        measures[key]={ident:measure(row,public[ident]['truth']) for ident,row in rows.items()}
    for arm in ARMS:
        first=streams['cold',arm,0]
        for repeat in range(1,5):
            current=streams['cold',arm,repeat]
            for ident in public:
                one, two = (group[ident]['result'] for group in (first,current))
                for field in ('status','expr','circuit','truth','work'):
                    if one.get(field)!=two.get(field):
                        raise ValueError(f'cold repeats disagree for {arm} {ident} {field}')
    tables = {}
    for split, metadata in grading.items():
        tables[split]={}
        for cache, repeats in [('cold',5),('warm',1)]:
            cells={}
            for depth in (2,3,4):
                for kind in sorted({v['kind'] for v in metadata.values()}):
                    ids=[i for i,g in metadata.items() if g['depth']==depth and g['kind']==kind]
                    if not ids:
                        raise ValueError('missing condition')
                    cell={'n_tasks':len(ids),'depth':depth,'kind':kind}
                    for arm in ARMS:
                        observations=[totals(measures[cache,arm,r][i] for i in ids) for r in range(repeats)]
                        cell[arm]={k:median(v[k] for v in observations) for k in observations[0]}
                        cell[arm]['search_cpu_repeats']=[v['search_cpu_ns'] for v in observations]
                        first=streams[cache,arm,0]
                        cell[arm]['work_totals']=totals(first[i]['result']['work'] for i in ids)
                        cell[arm]['fold_use_distribution']=dict(Counter(first[i]['result'].get('template_uses',0) for i in ids))
                        cell[arm]['status_counts']=dict(Counter(first[i]['result']['status'] for i in ids))
                    for route,prefix in ROUTES.items():
                        plain, named = prefix+'primitive',prefix+'named'
                        comparison = {}
                        for metric in ('tests','reads','search_cpu_ns','reported_wall_ns'):
                            base=cell[plain][metric]; macro=cell[named][metric]
                            per_rule=[median(measures[cache,plain,r][i][metric] for r in range(repeats))
                                      -median(measures[cache,named,r][i][metric] for r in range(repeats)) for i in ids]
                            comparison[metric]=dict(per_task=(base-macro)/len(ids),
                                                   fraction=(base-macro)/base if base else 0,
                                                   n_positive=sum(value>0 for value in per_rule),
                                                   n_equal=sum(value==0 for value in per_rule),
                                                   n_negative=sum(value<0 for value in per_rule))
                        cell[route+'_savings']=comparison
                    cells[f'{depth}-{kind}']=cell
            tables[split][cache]=cells
    primary=tables['primary']['cold']
    positive=next(g['kind'] for g in grading['primary'].values() if g['kind'] in ('recurring','intact','recurrent','repeat','repeated','positive'))
    cells=[primary[f'{d}-{positive}'] for d in (2,3,4)]
    all_exact=all(row['exact'] for group in measures.values() for row in group.values())
    gate={'all_exact':all_exact,'strategies':{}}
    for route in ROUTES:
        points=[cell[route+'_savings'] for cell in cells]
        def grows(metric):
            shallow,deep=points[0][metric],points[-1][metric]
            return (deep['per_task']>shallow['per_task'] and deep['fraction']>=.10
                    and deep['n_positive']>cells[-1]['n_tasks']/2)
        row4=points[-1]['reads']['per_task']
        count_pass=grows('tests')
        time_pass=grows('search_cpu_ns') and row4>0 and row4>points[0]['reads']['per_task']
        gate['strategies'][route]={'work_criterion':count_pass,'time_and_row_criterion':time_pass}
    gate['discover']=all_exact and any(any(flags.values()) for flags in gate['strategies'].values())
    stats={'unique_tasks':len(public),'exact_possible_rule_input_pairs':sum(1<<v['n'] for v in public.values()),
           'failed_logical_runs':sum(1-v['exact'] for record in measures.values() for v in record.values()),
           'timed_rule_runs':sum(map(len,measures.values())), 'gate':gate,'tables':tables}
    stats['whole_panel']={}
    for cache,repeats in [('cold',5),('warm',1)]:
        stats['whole_panel'][cache]={}
        for arm in ARMS:
            parts=[totals(measures[cache,arm,rep].values()) for rep in range(repeats)]
            entry={k:median(p[k] for p in parts) for k in parts[0]}
            entry['work_totals']=totals(row['result']['work'] for row in streams[cache,arm,0].values())
            entry['setup_work_totals']=totals(row['setup_work'] for row in streams[cache,arm,0].values())
            stats['whole_panel'][cache][arm]=entry
    return stats


if __name__=='__main__':
    d=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else OUT
    result=summarize(d)
    (d/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('tables','whole_panel')},indent=2))
