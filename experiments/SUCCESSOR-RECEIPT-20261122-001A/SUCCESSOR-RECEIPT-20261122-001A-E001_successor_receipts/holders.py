"""Independently bind each third-cut successor to its receipt mark and fourth-cut finish."""
from collections import defaultdict
from functools import cache
from importlib.util import module_from_spec,spec_from_file_location
from pathlib import Path
import gzip,json,sys

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SRC='HIDDEN-SENDER-MARKS-20261122-001A';OLD='REPEATED-SENDS-20261122-001'
INP=ROOT/'artifacts'/SRC/(SRC+'-E001_hidden_sends')/'growth.json.gz'
OUT=ROOT/'artifacts'/HERE.parent.name/HERE.name


@cache
def module():
    spec=spec_from_file_location('successor_fourth_prior',ROOT/'research'/OLD/'check_fixed_holder.py')
    mod=module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod);return mod


@cache
def data():
    with gzip.open(INP,'rt') as f:return json.load(f)


@cache
def grown(law,route):
    s=data();case=s['cases'][route][law];stars=[tuple(row) for row in s['original_stars']]
    for c in case['cuts']:
        stars.extend(tuple(b['consumed_names']+b['fresh_names']) for b in c['births'])
    fourth,new=module().append_fourth(stars,law)
    assert len(new)==964 and len(fourth)==1611
    return fourth


def owners(stars):
    r=defaultdict(list)
    for h,row in enumerate(stars):
        for d in row:r[d].append(h)
    return r


def main():
    stages={};src=data(); prior=json.loads((ROOT/'research'/OLD/'fixed_holder_replay.json').read_text())
    for route in ('intact','interrupted','sham'):
        for law in ('parity','nae'):
            fourth=grown(law,route);c=src['cases'][route][law]['cuts'];third=fourth[:647]; o3,o4=owners(third),owners(fourth)
            assert prior[law][route]['further_births']==len(fourth)-len(third)
            bs={b['holder']:b for cut in c for b in cut['births']}; rr=bs[294]; H=[]
            for position,d in enumerate(rr['fresh_names']):
                h,=set(o3[d])-{294};node=bs[h];assert h==(631,633,634)[position]
                inputs=node['consumed_names'];own=node['fresh_names'];other,=set(node['parents'])-{294}
                assert len(inputs)==2 and len(set(third[h])&set(rr['fresh_names']))==1
                assert not set(third[h])&{510,563}
                assert all(len(o3[n])==2 and o3[n]==o4[n] for n in inputs)
                assert len({tuple(o3[n]) for n in inputs})==2 and other!=294
                receivers=[next(iter(set(o4[n])-{h})) for n in own]
                assert all(o3[n]==[h] and len(o4[n])==2 for n in own) and len(set(receivers))==len(own)
                H.append({'holder':h,'R_fresh_position':position,'old_inputs':inputs,'all_parents':node['parents'],
                          'own_new':own,'fourth_recipients':receivers,'old_incoming_clock':'two distinct anonymous coholders persist',
                          'own_clock':[[None]*len(own),list(range(len(own)))]})
            stages[f'{law}-{route}']=H
    (OUT/'holders.json').write_text(json.dumps(stages,sort_keys=True,indent=2)+'\n');print(stages['parity-intact'])


if __name__=='__main__':main()
