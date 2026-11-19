"""Replay two simple starts and verify every entry on both sides of each marked swap."""
import argparse
from collections import defaultdict
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET = "GROWN-END-MEET-ONCE-20261119-001"
OUT = ROOT / "artifacts" / TICKET / (TICKET + "-E001_rounds") / "two_histories.json"
sys.path.insert(0, str(ROOT / "experiments/EXTEND-ROUND-20261119-001A/EXTEND-ROUND-20261119-001A-E001_extend"))
import extend as law

sys.path.insert(0, str(ROOT / "experiments/GROWN-END-SWAP-20261119-001/GROWN-END-SWAP-20261119-001-E001_reached"))
import verify as independent

# A,B are the two ends. C,D are the middle junctions.
# 0=AC, 1=BC, 2=AD, 3=BD, 4=CD in both starts.
CASES = {
    "six_at_round_two": (2, [[0,2,7,8,9],[1,3,5,6],[0,1,4],[2,3,4],[5,10,11],[6,12,13]]),
    "seven_at_round_one": (1, [[0,2,5,6,7],[1,3,8,9],[0,1,4],[2,3,4],[5,10,11],[6,12,13],[7,14,15]]),
}

def canonical_digest(obj):
    return sha256(json.dumps(obj, separators=(",", ":")).encode()).hexdigest()

def all_readings(engine, rows):
    holders = defaultdict(list)
    for site, row in enumerate(rows):
        for x in row:
            holders[x].append(site)
    labels = sorted(holders)
    assert labels == list(range(len(labels)))
    ends = [v if len(v)==2 else [v[0],len(rows)] for x in labels for v in [holders[x]]]
    data = [f"{len(rows)} {len(labels)}", *(f"{u} {v}" for u,v in ends)]
    raw = subprocess.check_output([str(engine)], input="\n".join(data)+"\n", text=True).split()
    bonds, *values = map(int, raw)
    pairs = list(combinations(labels,2))
    assert len(values)==len(pairs)
    return bonds, dict(zip(pairs,values)), holders

def read_case(engine, age, start):
    syslaw = law.C.S.from_junctions(start)
    stages = [[sorted(s) for s in syslaw.bits_of]]
    rounds = []
    for _ in range(age+1):
        added = syslaw.step(law.C.S.gf2(law.C.F.fewest), None)
        assert added is not None and added['new']>0
        stages.append([sorted(s) for s in syslaw.bits_of])
        previous, grown = map(independent.Arrangement.parse,stages[-2:])
        records = independent.round_replay(previous,grown)
        rounds.append([{'parents':sorted(r['taken']), 'fresh':r['fresh']} for r in records])
    for stage in stages:
        audit = independent.start_audit(independent.Arrangement.parse(stage))
        assert audit['meets_once'] and not audit['forced_distinctions'] and not audit['non_outside_cut_holders']
    result = {'start':start, 'age':age, 'stages':stages, 'new_junctions_by_round':rounds,
              'distinctions_at_the_four_junctions':{'AC':0,'BC':1,'AD':2,'BD':3,'CD':4},
              'exchanged':[0,1], 'other_distinctions':'fixed',
              'sizes':[[len(rows),len(set().union(*map(set,rows)))] for rows in stages],
              'tables':{}}
    for label,rows in zip(('current','next'),stages[-2:]):
        bonds, table, holders=all_readings(engine,rows)
        phi={x:1-x if x in (0,1) else x for x in holders}
        live=sorted({u for v in holders.values() if len(v)==1 for u in v})
        assert all(all(phi[x]==x for x in rows[u]) for u in live)
        errors=[[list(pair),list(sorted(phi[x] for x in pair)),k,table[tuple(sorted(phi[x] for x in pair))]]
                for pair,k in table.items() if k!=table[tuple(sorted(phi[x] for x in pair))]]
        result['tables'][label]={'bond_count':bonds,'pair_count':len(table),'live':live,
          'D_02_and_D_12':[table[(0,2)],table[(1,2)]],
          'all_disagreements_with_identity_on_fresh':errors,
          'lexicographic_distance_table_sha256':canonical_digest(list(table.values()))}
    cur,nxt=result['tables']['current'],result['tables']['next']
    assert not cur['all_disagreements_with_identity_on_fresh']
    assert cur['D_02_and_D_12']==[3,3] and nxt['D_02_and_D_12']==[2,3]
    return result

def main():
    arg=argparse.ArgumentParser(description=__doc__)
    arg.add_argument('--write',action='store_true')
    arg.add_argument('--engine',type=Path)
    args=arg.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        executable = args.engine or Path(tmp)/'cut_tables'
        if not args.engine:
            subprocess.run(['c++','-O3','-std=c++20',str(HERE/'cut_tables.cpp'),'-o',str(executable)],check=True)
        record={name:read_case(executable,age,rows) for name,(age,rows) in CASES.items()}
    if args.write:
        OUT.write_text(json.dumps(record,indent=2)+'\n')
    else:
        assert json.loads(OUT.read_text())==record
    for name,r in record.items():
        print(name,r['sizes'],[(v['pair_count'],v['D_02_and_D_12']) for v in r['tables'].values()])

if __name__=='__main__':
    main()
