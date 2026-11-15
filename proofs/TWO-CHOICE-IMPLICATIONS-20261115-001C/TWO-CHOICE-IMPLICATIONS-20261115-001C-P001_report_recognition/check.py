"""Query the actual pinned ternary routes on fixed catalogues and test the two reports."""
import importlib.util
from itertools import product
from pathlib import Path
import json
import os
from random import Random
import sys


def compiler(root):
    t = "TWO-RELAY-PADDING-20261115-001C"
    spec = importlib.util.spec_from_file_location("positive_routes", root/"proofs"/t/(t+"-P001_pairwise_sharing")/"check.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def template(c, n, roster, mode):
    stages, signals = c.compile_stages(n,roster)
    h,k = ("report",0),("report",1)
    if mode == "given":
        stages += [((h,c.ON,c.ON),(("unused",0),c.OFF,c.OFF)),
                   ((k,c.ON,c.OFF),(("unused",1),c.OFF,c.OFF))]
    else:
        pad = ("choose-which-input",0)
        stages += [((h,c.Edge("half",pad,1),c.OFF),(k,c.Edge("half",pad,-1),c.OFF))]
    # The two ports are physically present and constrain the right block. At b=0 both are free.
    cut = len(stages)
    stages += [((h,c.ON,c.OFF),(k,c.ON,c.OFF))]
    raw = c.StrictTemplate(stages,signals)
    left = {name for stage in stages[:cut] for name,_,_ in stage}
    right = {name for stage in stages[cut:] for name,_,_ in stage}
    assert left & right == {h,k} and max(raw.middle_uses.values()) == 2 and max(raw.pad_uses.values()) == 2
    boundary = [raw.var(("boundary",v)) for v in (0,cut,len(stages))]
    ports = [raw.var(("middle",v)) for v in (h,k)]
    return raw,boundary,ports


def run(root):
    from pysat.solvers import Solver
    c = compiler(root)
    rng = Random(610710)
    result = {}
    for n in (3,4,5):
        roster = c.clauses_on(n)
        menus = ([set(i for i in range(8) if mask>>i & 1) for mask in range(256)] if n==3 else
                 [set(),set(range(len(roster))),set(range(7)),set(range(8))]+
                 [set(rng.sample(range(len(roster)),rng.randrange(len(roster)+1))) for _ in range(12)])
        for mode in ("given","language"):
            raw,bounds,ports = template(c,n,roster,mode)
            a,b,z = bounds
            endpoint_guards={g for row in raw.half_slots[:8] for g in row}
            outputs = []
            with Solver(name="g3",bootstrap_with=raw.cnf) as sat:
                fixed_suffix=None
                for menu in menus:
                    source = bool(c.allowed_sources(n,roster,menu))
                    guards = [(-abs(g) if abs(g) in endpoint_guards else g) for g in raw.guards(menu)]
                    pins = [a,-b,-z,*guards]
                    active=set(g for g in guards if g>0)
                    suffix = tuple(g in active for row in raw.half_slots[-(24 if mode=="given" else 16):] for g in row)
                    assert fixed_suffix is None or suffix==fixed_suffix
                    fixed_suffix=suffix
                    report = set()
                    for bits in product(range(2), repeat=2):
                        if sat.solve(assumptions=pins+[v if bit else -v for v,bit in zip(ports,bits)]):
                            report.add(bits)
                    if mode=="given":
                        expected=({(0,0),(0,1),(1,1)} if source else {(1,1)})
                    else:
                        expected=(set(product(range(2),repeat=2)) if source else {(1,0),(0,1),(1,1)})
                    assert report==expected
                    outputs.append(source)
            result[str(n)+"_"+mode]={"source_satisfiable":sum(outputs),"menus":len(menus),
                                      "raw_queries":4*len(menus),"stages":len(raw.stages)}
    assert result["3_given"]["source_satisfiable"]==255
    return {"status":"passed","catalogues":result,"total_raw_queries":sum(r["raw_queries"] for r in result.values())}


if __name__ == "__main__":
    root=Path(__file__).resolve().parents[3]
    venv=root/".venv/bin/python"
    if venv.exists() and Path(sys.prefix).resolve()!=venv.parent.parent.resolve():
        os.execv(str(venv),[str(venv),"-B",str(Path(__file__).resolve())])
    print(json.dumps(run(root),sort_keys=True))
