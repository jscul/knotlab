"""Try exact bounded enumeration of all maximal sets and their residual pair marks on shorter inputs."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from group_profile import Stage,members,pack


def maximal_formula(stage, filename):
    representatives={}
    for v,s in enumerate(stage.at):
        # Closed equality is tested on the full literal roster.
        closed=stage.hood(s) if s else (1<<v)
        representatives.setdefault(closed,v)
    indices=list(representatives.values())
    index_bits=pack(indices,stage.n)
    position={v:i+1 for i,v in enumerate(indices)}
    clauses=0
    # Write the compact quotient with a fixed-width placeholder for clause count.
    with filename.open('w+') as f:
        def header(count):return f'p cnf {len(indices)} {count:012}\n'
        f.write(header(0))
        for closed,u in representatives.items():
            missing=[position[v] for v in members(index_bits & ~closed)]
            i=position[u]
            for v in missing:
                if v>i:
                    f.write(f'-{i} -{v} 0\n')
                    clauses+=1
            f.write(' '.join(map(str,[i,*missing,0]))+'\n')
            clauses+=1
        f.seek(0);f.write(header(clauses))
    return dict(quotient_size=len(indices),clauses=clauses,sha256=hashlib.sha256(filename.read_bytes()).hexdigest())


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('roster',type=Path);p.add_argument('work',type=Path);p.add_argument('solver',type=Path)
    p.add_argument('result',type=Path);args=p.parse_args()
    stage=Stage(args.roster);formula=args.work/(args.roster.stem+'.maxima.cnf')
    info=maximal_formula(stage,formula)
    run=subprocess.run([str(args.solver),'--prob','0','--verb','0',str(formula)],capture_output=True,text=True,check=True)
    assert 'epsilon: 0 delta: 0' in run.stdout
    count=int(next(l for l in run.stdout.splitlines() if l.startswith('c s exact arb int ')).split()[-1])
    info.update(source=args.roster.stem,raw_maxima=count,solver_receipt=run.stdout,
                scope='Physical maximal candidate sets. Each true-twin class contributes all its members together.')
    args.result.write_text(json.dumps(info,indent=1)+'\n');print(args.roster.stem,count,flush=True)


if __name__=='__main__':main()
