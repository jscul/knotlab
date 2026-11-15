"""Query original joined and split guarded CNFs under the very same switch assignment."""
from itertools import product
import hashlib
import importlib.util
import json
import os
from pathlib import Path
from random import Random
import sys


def compiler(root):
    ticket="TWO-RELAY-PADDING-20261115-001C"
    path=root/"proofs"/ticket/(ticket+"-P001_pairwise_sharing")/"check.py"
    spec=importlib.util.spec_from_file_location("cost_source",path)
    mod=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=mod
    spec.loader.exec_module(mod)
    return mod


def construct(mod,n,roster,split):
    original,signals=mod.compile_stages(n,roster)
    gate=len(original)
    left=(("shared-cut",0),mod.ON,mod.OFF)
    right=(("shared-cut",int(split)),mod.ON,mod.ON)
    stages=original+[(left,(("gate-unused",0),mod.OFF,mod.OFF)),
                     (right,(("gate-unused",1),mod.OFF,mod.OFF))]
    raw=mod.StrictTemplate(stages,signals)
    assert len(raw.stages)==4*len(roster)+12*n+10
    assert max(raw.middle_uses.values())<=2 and max(raw.pad_uses.values())<=2
    parts=[{name for st in block for name,_,_ in st} for block in (stages[:-1],stages[-1:])]
    assert parts[0]&parts[1] == (set() if split else {("shared-cut",0)})
    assert not (set(raw.edge_records[i][2] for i in range(4*(gate+1))) &
                set(raw.edge_records[i][2] for i in range(4*(gate+1),len(raw.edge_records))))
    return raw,[raw.var(("boundary",j)) for j in (0,gate+1,gate+2)]


def pin_switches(raw,selected):
    endpoints={g for row in raw.half_slots[:8] for g in row}
    return [(-abs(g) if abs(g) in endpoints else g) for g in raw.guards(selected)]


def run(n,roster,menus,mod,solver_type):
    joined,jvars=construct(mod,n,roster,False)
    split,svars=construct(mod,n,roster,True)
    points=list(product((0,1),repeat=3))
    good=bad=queries=0
    shape=hashlib.sha256(repr(joined.cnf).encode()).hexdigest()
    fixed_gate=None
    with solver_type(name="g3",bootstrap_with=joined.cnf) as sj, solver_type(name="g3",bootstrap_with=split.cnf) as ss:
        for menu in menus:
            source_sat=bool(mod.allowed_sources(n,roster,menu))
            jp,sp=pin_switches(joined,menu),pin_switches(split,menu)
            def read_gate(raw, pins):
                on={g for g in pins if g>0}
                return tuple(g in on for row in raw.half_slots[-16:] for g in row)
            gate=read_gate(joined,jp)
            assert gate==read_gate(split,sp)
            if fixed_gate is None:
                fixed_gate=gate
            assert gate==fixed_gate
            lost=[]
            for a,b,z in points:
                state=a,b,z
                janswer=sj.solve(assumptions=jp+[v if bit else -v for v,bit in zip(jvars,state)])
                sanswer=ss.solve(assumptions=sp+[v if bit else -v for v,bit in zip(svars,state)])
                assert sanswer==(b<=z) and janswer==((b<=z) and (a<=z or source_sat))
                if sanswer and not janswer:
                    lost.append(state)
                queries+=2
            assert lost==([] if source_sat else [(1,0,0)])
            good+=source_sat
            bad+=not source_sat
    assert shape==hashlib.sha256(repr(joined.cnf).encode()).hexdigest()
    return {"fixed_stages":len(joined.stages),"safe_menus":good,"unsafe_menus":bad,
            "raw_triple_queries":queries,"fixed_joined_cnf_sha256":shape}


def main(root):
    from pysat.solvers import Solver
    mod=compiler(root)
    rng=Random(188)
    results={}
    for n in (3,4,5):
        roster=mod.clauses_on(n)
        if n==3:
            menus=[{i for i in range(8) if mask>>i&1} for mask in range(256)]
        else:
            menus=[set(),set(range(len(roster))),set(range(7)),set(range(8))]
            menus+= [set(rng.sample(range(len(roster)),rng.randrange(len(roster)+1))) for _ in range(12)]
        results[str(n)]=run(n,roster,menus,mod,Solver)
    assert results["3"]["safe_menus"]==255 and results["3"]["unsafe_menus"]==1
    return {"status":"passed","catalogues":results,"one_middle_crosses":True,
            "guard_vectors_identical_on_the_two_stage_suffix":True}


if __name__=="__main__":
    root=Path(__file__).resolve().parents[3]
    python=root/".venv/bin/python"
    if python.exists() and Path(sys.prefix).resolve()!=python.parent.parent.resolve():
        os.execv(str(python),[str(python),"-B",str(Path(__file__).resolve())])
    print(json.dumps(main(root),sort_keys=True))
