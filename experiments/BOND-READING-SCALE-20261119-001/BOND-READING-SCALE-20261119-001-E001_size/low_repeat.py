"""Replay the reached-width pair census with unrestricted old multiplicities."""

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
import os
from pathlib import Path
from shutil import which
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CPP = HERE / 'low_repeat.cpp'


def size_cap(width):
    # The arity floor and at least three fresh distinctions in the observed
    # stage give 3J+3 <= 2W. The first two newborn counts are handled by proof.
    return (2*width - 3)//3


def generate(folder, width, junctions, geng, library):
    assert width == 0 or 12 <= width <= 24
    folder.mkdir(exist_ok=True, parents=True)
    env = dict(os.environ)
    if library is not None:
        env['LD_LIBRARY_PATH'] = library
    for n in range(1,junctions-2):
        name = folder / f'predecessor-{n}.g6'
        upper = min(n*(n-1)//2,width-6) if width else n*(n-1)//2
        args = [geng,'-cq',str(n),f'{n-1}:{upper}']
        with name.open('wb') as output:
            subprocess.run(args,stdout=output,env=env,check=True)
    subprocess.run(['c++','-std=c++20','-O3','-Wno-return-type',str(CPP),'-o',str(folder/'low_repeat')],check=True)


def setup(params):
    global engine,width,junctions,roster,source,shard,multiplicity
    source = Path(params['folder'])
    engine = str(source/'low_repeat')
    width = int(params['width'])
    junctions = int(params.get('junctions',size_cap(width)))
    shard = int(params.get('shard',256))
    multiplicity = int(params.get('multiplicity',0))
    roster = {n:(source/f'predecessor-{n}.g6').read_bytes().splitlines() for n in range(1,junctions-2)}


def cases():
    for n,rows in roster.items():
        for first in range(0,len(rows),shard):
            yield f'{n:02d}-{first//shard:06d}',[n,first,min(first+shard,len(rows))]


def run(case_id,payload):
    n,first,past = payload
    inp = b'\n'.join(roster[n][first:past])+b'\n'
    actual = subprocess.run([engine,str(n),str(junctions),str(width),str(multiplicity)],
                            input=inp,capture_output=True,check=True)
    values = [json.loads(line) for line in actual.stdout.splitlines()]
    assert values[-1]['supports'] == past-first, case_id
    assert values[-1]['predecessor'] == n
    return values


def collect(folder, allow_partial=False):
    sys.path.insert(0,str(ROOT/'scripts'))
    from longrun import load_results

    setup(json.loads((folder/'job.json').read_bytes())['params'])
    observed = load_results(folder)
    expected = dict(cases())
    assert set(observed) <= set(expected)
    missing = [{'case':key,'predecessor':n,'first':first,'past':past,
                'status':observed.get(key,{}).get('status','pending')}
               for key,(n,first,past) in expected.items() if observed.get(key,{}).get('status') != 'ok']
    assert allow_partial or not missing
    tiers = defaultdict(Counter)
    by_predecessor = defaultdict(Counter)
    failures = []
    grades = ('at_most_one_movable','offshoots_next','pooled_group_carries_span',
              'exact_group_carries_span','successor_extends','failed','unresolved')
    for key in sorted(observed):
        if observed[key]['status'] != 'ok':
            continue
        rows = observed[key]['result']
        failures.extend(row['failure'] for row in rows[:-1])
        scope = rows[-1]
        n = scope['predecessor']
        by_predecessor[n].update({k:scope[k] for k in ('supports','live_subsets','loose_shapes')})
        for entry in scope['tiers']:
            j,w = entry['junctions'],entry['width']
            values = {k:v for k,v in entry.items() if k not in ('junctions','width')}
            assert values['histories'] == sum(values[key] for key in grades)
            tiers[j,w].update(values)
            by_predecessor[n].update(values)
    assert len(failures) == sum(row['failed'] for row in tiers.values())
    for n,rows in roster.items():
        omitted = sum(case['past']-case['first'] for case in missing if case['predecessor']==n)
        assert by_predecessor[n]['supports'] == len(rows)-omitted
    result = {'current_width_cap':width or None,'current_junction_cap':junctions,
            'per_meeting_multiplicity_cap':multiplicity or None,'shards':len(observed),
            'ordinary_graphs_sha256':{n:sha256(b'\n'.join(rows)+b'\n').hexdigest() for n,rows in roster.items()},
            'by_predecessor':dict(sorted(by_predecessor.items())),
            'joint_tiers':[{'junctions':j,'width':w,**row} for (j,w),row in sorted(tiers.items())],
            'failures':failures}
    if allow_partial:
        result['omitted_shards'] = missing
        result['complete_junctions_through'] = min([junctions, *(case['predecessor']+2 for case in missing)])
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    commands = p.add_subparsers(dest='mode',required=True)
    pre = commands.add_parser('prepare')
    pre.add_argument('folder',type=Path)
    pre.add_argument('--width',type=int,default=20)
    pre.add_argument('--junctions',type=int)
    pre.add_argument('--geng',default=which('nauty-geng') or which('geng'))
    pre.add_argument('--geng-library')
    combine = commands.add_parser('collect')
    combine.add_argument('runner_output',type=Path)
    combine.add_argument('--partial',action='store_true')
    a = p.parse_args()
    if a.mode == 'prepare':
        if not a.geng:
            p.error('install nauty-geng or pass --geng')
        if a.width == 0 and a.junctions is None:
            p.error('specify --junctions when --width is 0')
        generate(a.folder,a.width,a.junctions or size_cap(a.width),a.geng,a.geng_library)
    else:
        print(json.dumps(collect(a.runner_output,a.partial),indent=2))


if __name__ == '__main__':
    main()
