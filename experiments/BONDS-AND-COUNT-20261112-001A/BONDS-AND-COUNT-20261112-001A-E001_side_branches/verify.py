"""Independent scalar enumeration and SAT/CLI replay of witness.json.

Does not import compare.py or its semantic/projection functions. Scalar
relations use tuples of booleans instead of the producer's integer bitsets.
"""
from __future__ import annotations

import gzip
import hashlib
import itertools
import json
import os
from pathlib import Path
import subprocess
import sys

from pysat.solvers import Solver

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUT = ROOT / "artifacts/BONDS-AND-COUNT-20261112-001A/BONDS-AND-COUNT-20261112-001A-E001_side_branches"
ALL = set(itertools.product((0, 1), repeat=3))
NAE = ALL - {(0, 0, 0), (1, 1, 1)}


def apply(definition, self_relation):
    ports, local_count, body = definition
    allowed = set()
    for assignment in itertools.product((0, 1), repeat=ports + local_count):
        if all(tuple(assignment[v] for v in args) in (NAE if cl == "K" else self_relation)
               for cl, args in body):
            allowed.add(assignment[:ports])
    return allowed


def gfp(definition):
    current = ALL
    history = [sorted(current)]
    while True:
        updated = apply(definition, current)
        if updated == current:
            return current, history
        assert updated < current
        current = updated
        history.append(sorted(current))


def construct(definition, expanded):
    relation, _ = gfp(definition)
    names = {"a", "b", "c"}
    factors = []
    def expand(path, arguments):
        local_names = [f"{'r' if not path else '.'.join(map(str,path))}:x{j}"
                       for j in range(definition[1])]
        names.update(local_names)
        environment = list(arguments) + local_names
        call_number = 0
        for callee, indices in definition[2]:
            actual = tuple(environment[j] for j in indices)
            if callee == "K":
                factors.append((actual, NAE))
            else:
                child = path + (call_number,)
                call_number += 1
                if child in expanded:
                    expand(child, actual)
                else:
                    factors.append((actual, relation))
    expand((), ("a", "b", "c"))
    return sorted(names), factors


def enumerate_states(names, factors):
    rows = []
    for values in itertools.product((0, 1), repeat=len(names)):
        assignment = dict(zip(names, values))
        if all(tuple(assignment[name] for name in variables) in relation for variables, relation in factors):
            rows.append(assignment)
    return rows


def forest_certificate(names, factors):
    # Count incidences component by component, independently of the
    # producer's union-find check. TOP frontier factors impose no rule.
    graph = {("v",name):set() for name in names}
    number = 0
    for variables,relation in factors:
        if relation == ALL:
            continue
        assert relation == NAE
        knot = ("k",str(number));number += 1
        graph[knot]=set()
        for name in variables:
            variable=("v",name)
            graph[knot].add(variable);graph[variable].add(knot)
    components=[]
    seen=set()
    for vertex in graph:
        if vertex in seen:
            continue
        stack=[vertex];component=set()
        while stack:
            current=stack.pop()
            if current in component:
                continue
            component.add(current);stack.extend(graph[current]-component)
        seen.update(component)
        edges=sum(len(graph[v]) for v in component)//2
        components.append(dict(vertices=len(component),incidences=edges))
    return dict(is_forest=all(c["incidences"]==c["vertices"]-1 for c in components),
                components=components)


def sat_states(names, factors):
    ids = {name:j+1 for j, name in enumerate(names)}
    clauses = []
    for variables, relation in factors:
        for row in ALL - relation:
            clauses.append([(-1 if value else 1) * ids[name] for name, value in zip(variables, row)])
    rows = []
    with Solver(name="g4", bootstrap_with=clauses) as solver:
        for values in itertools.product((0, 1), repeat=len(names)):
            if solver.solve(assumptions=[(1 if value else -1)*ids[name] for name,value in zip(names,values)]):
                rows.append(dict(zip(names, values)))
    return rows


def project(rows, support):
    return sorted({tuple(row[name] for name in support) for row in rows})


def projected_certificate(rows, support):
    allowed = project(rows, support)
    full = set(itertools.product((0,1),repeat=len(support)))
    excluded = sorted(full-set(allowed))
    deletions = {}
    for dropped in support:
        keep = [x for x in support if x != dropped]
        table = project(rows, keep)
        assert len(table) == 1 << len(keep)
        deletions[dropped] = dict(variables=keep, allowed=["".join(map(str,t)) for t in table])
    witnesses = {}
    for state in allowed:
        assignment = next(r for r in rows if tuple(r[x] for x in support) == state)
        witnesses["".join(map(str,state))] = assignment
    return dict(variables=support, allowed=["".join(map(str,t)) for t in allowed],
                excluded=["".join(map(str,t)) for t in excluded],
                deletions=deletions, finite_cut_completion_for_each_allowed_state=witnesses)


def knotlab_cli(certificate, label):
    # Feed the independently projected truth table to the canonical CLI.
    letters = [f"x{j}" for j in range(len(certificate["variables"]))]
    clauses = [" ".join(("~" if bit == "1" else "") + name for name,bit in zip(letters,row))
               for row in certificate["excluded"]]
    command = [sys.executable,"-B","-m","knotlab","check","--cnf","; ".join(clauses),
               "--loops",*letters[:-1],"--contact",letters[-1],"--json"]
    completed = subprocess.run(command,cwd=ROOT,env={**os.environ,"PYTHONPATH":str(ROOT/"tools")},
                               text=True,capture_output=True,check=True)
    report = json.loads(completed.stdout)
    assert report["is_knot"] and report["binding"] and report["loss_on_erasure"] and report["coexistence"]
    (OUT/f"knotlab_{label}.json").write_text(json.dumps(dict(command=command,variable_map=dict(zip(letters,certificate["variables"])),report=report),indent=2)+"\n")
    return report


def main():
    suffix = "_acyclic" if "--acyclic" in sys.argv else ""
    witness = json.loads((OUT/f"witness{suffix}.json").read_text())
    source = witness["source"]
    source_path = ROOT/source["file"]
    with gzip.open(source_path,"rt") as stream:
        source_row = json.loads(next(line for n,line in enumerate(stream,1) if n == source["line"]))
    definition = source_row["defs"][0]
    assert definition == source["definition"] and source_row["limit_only"]
    assert not any(cl == "SELF" and set(args) == {0,1,2} for cl,args in definition[2])
    greatest, greatest_history = gfp(definition)
    assert greatest == ALL
    # Check the advertised finite death independently, through a full orbit.
    current = NAE
    orbit = []
    while current not in orbit:
        orbit.append(current)
        current = apply(definition,current)
    depth_tables = [apply(definition,r) for r in orbit]
    first_dead = next((n for n,r in enumerate(depth_tables,1) if not r),None)
    assert first_dead == source["first_dead"]
    result = dict(source=source, source_sha256=hashlib.sha256(source_path.read_bytes()).hexdigest(),
                  independent_gfp=[list(r) for r in sorted(greatest)], independent_first_dead=first_dead,
                  validation_level="V1-separate-algorithm-same-task", native_source_label="not assessed: finite-flip witness absent",
                  semantics="usual limit equals bottomless here: no pass-through SELF calls")
    reconstructed = {}
    for label in ("ray","branch"):
        cut = witness[f"{label}_cut"]
        names,factors=construct(definition,{tuple(p) for p in cut["expanded_paths"]})
        rows=enumerate_states(names,factors)
        sat_rows=sat_states(names,factors)
        assert rows == sat_rows
        numeric = sorted(sum(r[name] << j for j,name in enumerate(cut["names"])) for r in rows)
        assert numeric == witness[f"{label}_allowed_assignments"]
        reconstructed[label]=rows
        result[label+"_model_count"]=len(rows)
        result[label+"_incidence"]=forest_certificate(names,factors)
    if suffix:
        assert result["ray_incidence"]["is_forest"]
    # The side-expanded cut must project exactly to the ray-only relation.
    ray_names=witness["ray_cut"]["names"]
    assert project(reconstructed["branch"],ray_names)==project(reconstructed["ray"],ray_names)
    result["side_projection_equals_ray"]=True
    ray_cert=projected_certificate(reconstructed["ray"],witness["ray_support"])
    side_cert=projected_certificate(reconstructed["branch"],witness["global_support"])
    ray_cli=knotlab_cli(ray_cert,"ray"+suffix)
    side_cli=knotlab_cli(side_cert,"side"+suffix)
    endpoints=witness["endpoints"]
    assert len(project(reconstructed["branch"],endpoints))==4
    exclusions=[]
    for size in (2,3):
        for extra in itertools.combinations([x for x in ray_names if x not in endpoints],size-2):
            support=sorted(endpoints+list(extra))
            allowed=project(reconstructed["ray"],support)
            assert len(allowed)==1 << len(support)
            exclusions.append(dict(variables=support,allowed=["".join(map(str,t)) for t in allowed]))
    assert len(exclusions)==6
    target_names=[witness["ray_cut"]["names"][j] for j in witness["ray_cut"]["target"]]
    eligible_pair_tables=[]
    for first,second in itertools.product(("a","b","c"),target_names):
        table=project(reconstructed["ray"],[first,second])
        assert len(table)==4
        eligible_pair_tables.append(dict(variables=[first,second],allowed=["".join(map(str,t)) for t in table]))
    if suffix:
        aggregate_witness=projected_certificate(reconstructed["ray"],["c","r:x0","0:x1"])
        assert len(aggregate_witness["allowed"])==6
    else:
        aggregate_witness=projected_certificate(reconstructed["ray"],["b","c","0:x0"])
        assert len(aggregate_witness["allowed"])==6
    # Side-free control: two NAE knots sharing x have the same 4-place
    # projected bond and do not gain supports from nonexistent side copies.
    control_names=["a","b","c","d","x"]
    control_factors=[(("a","b","x"),NAE),(("x","c","d"),NAE)]
    control_rows=enumerate_states(control_names,control_factors)
    assert control_rows==sat_states(control_names,control_factors)
    control=projected_certificate(control_rows,["a","b","c","d"])
    assert len(control["allowed"])==14
    knotlab_cli(control,"chain_control"+suffix)
    result.update(ray=ray_cert,side=side_cert,cheaper_ray_exclusions=exclusions,
                  pair_only_table=["".join(map(str,t)) for t in project(reconstructed["branch"],endpoints)],
                  exact_same_pair_minima=dict(ray=4,unrestricted=3),
                  eligible_pair_minima_at_depth_one=dict(ray=3,unrestricted=3),
                  all_eligible_pair_tables=eligible_pair_tables,
                  eligible_pair_minimum_witness=aggregate_witness,
                  side_free_control=dict(full_assignments=len(control_rows),certificate=control))
    (OUT/f"verification{suffix}.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k in ("independent_first_dead","validation_level","native_source_label","ray_model_count","branch_model_count","side_projection_equals_ray","exact_same_pair_minima","eligible_pair_minima_at_depth_one")},indent=2))


if __name__ == "__main__":
    main()
