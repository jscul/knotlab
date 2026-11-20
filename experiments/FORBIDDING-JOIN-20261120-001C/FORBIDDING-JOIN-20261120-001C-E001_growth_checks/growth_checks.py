"""Replay the pre-birth bond and sibling demand comparisons on actual rival stages."""
from argparse import ArgumentParser
from collections import Counter, deque
from fractions import Fraction
from functools import cache
from itertools import combinations
from pathlib import Path
import json
import os
import subprocess
import sys
import time


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "growth_checks.json"
for ticket, family in (
    ("ENTANGLEMENT-READ-20261120-001B", "separated_readings"),
    ("ORDINARY-DYNAMICS-20261120-001A", "ordinary"),
    ("BOND-CLOSURE-20261120-001A", "proposals"),
    ("FRESH-DEMAND-20261120-001A", "orders"),
    ("JOIN-GROWTH-20261118-001B", "joins"),
):
    sys.path.insert(0,str(ROOT / "experiments" / ticket / f"{ticket}-E001_{family}"))

import bond_checks
import end_operator
import exact_counts
import joinlib
import rulers
import scaffolds
from pysat.solvers import Minisat22


def fixed(rows):
    return tuple(tuple(sorted(row)) for row in rows)


def from_links(n, meetings, loose_holders):
    rows = [[] for _ in range(n)]
    for bit, holders in enumerate([*meetings, *((i,) for i in loose_holders)]):
        for i in holders:
            rows[i].append(bit)
    return fixed(rows)


def specimens():
    out = {}
    for spare in (0, 1):
        raw, _ = rulers.source(None, bool(spare))
        out[f"four_{spare}"] = (fixed(raw), 2)
        meetings = sorted(tuple(sorted(pair)) for pair in joinlib.ring_edges(5))
        sizes = [n + spare for n in joinlib.bare_sizes(5,meetings)]
        out[f"five_ring_{spare}"] = (fixed(joinlib.stars_from(sizes,meetings)), 1)
    meetings = [(i,(i+1) % 6) for i in range(6) for _ in range(2)]
    for label, extra in (("witness", 1), ("parent", 0)):
        out[f"six_{label}"] = (from_links(6,meetings,[0,2,4,extra,extra]), 1)
    for location in ("W","Z"):
        links, n, *_ = scaffolds.family(2,2,multiplicity=2,destination=location)
        out[f"demand_{location}"] = (fixed(tuple(bit for bit, pair in enumerate(links) if j in pair)
                                            for j in range(n)), 1)
    out["continuing_three"] = (from_links(3,[(0,1),(0,1),(1,2)],[0,2,2]), 4)
    return out


def granted(q, p, rival):
    floor = max(0,3-p)
    if rival == "ordinary":
        return q
    if rival == "one_fewer":
        return min(q, max(floor,q-1))
    if rival == "floor":
        return min(q,floor)
    raise ValueError(rival)


def sibling_demand(i, parents):
    """Rebuild the witness sets through i, using traces and actual sibling identities."""
    P = set(parents[i])
    siblings = {j:set(row) for j,row in enumerate(parents) if i != j and P.intersection(row)}
    candidates = set()
    for n in range(2,len(siblings)+1):
        for subset in combinations(siblings,n):
            rows = [siblings[j] for j in subset]
            if len(set.intersection(P,*rows)) == 0 and all(a & b for a,b in combinations(rows,2)):
                candidates.add(frozenset(subset))
    maximal = [s for s in candidates if not any(s < t for t in candidates)]
    covered = set().union(*maximal)
    return len(maximal) + len(siblings.keys()-covered)


@cache
def nae_factor(row):
    return exact_counts.Factor.from_function(row,lambda word: int("0" in word and "1" in word))


@cache
def state_count(law, rows):
    if law == "parity":
        return exact_counts.Parity(rows).total
    universe = set().union(*map(set,rows))
    histogram,_ = exact_counts.eliminate([nae_factor(row) for row in rows],universe,())
    return histogram[0]


def input_implied(law, rows, bits):
    if law == "parity":
        return bond_checks.parity_implied(map(bond_checks.mask,rows),bond_checks.mask(bits))
    clauses = [line for row in rows for line in ([b+1 for b in row],[-b-1 for b in row])]
    with Minisat22(bootstrap_with=clauses) as oracle:
        return all(not oracle.solve(assumptions=[sign*(b+1) for b in bits]) for sign in (-1,1))


@cache
def canonical_projection(width, words):
    names = [f"x{i}" for i in range(width)]
    missing = [w for w in range(1<<width) if w not in words]
    clauses = [" ".join(("~" if w>>i & 1 else "") + name for i,name in enumerate(names)) for w in missing]
    cnf = ";".join(clauses) or "x0 ~x0"
    verdict = json.loads(subprocess.check_output(
        [sys.executable,"-B","-m","knotlab","check","--cnf",cnf,"--loops",*names[:-1],"--contact",names[-1],"--json"],
        cwd=ROOT,env=dict(os.environ,PYTHONPATH=str(ROOT / "tools")),text=True))
    assert set(verdict["allowed"]) == {"".join(str((w>>i)&1) for i in range(width)) for w in words}
    return {k: verdict[k] for k in ("binding","loss_on_erasure","coexistence","is_knot")}


@cache
def certifications(law, rows):
    out = []
    def record(row, cert, words):
        gate = canonical_projection(len(row),tuple(words)) if len(row) >= 3 else None
        if gate:
            assert gate["is_knot"] == (cert["k1"] and cert["k2"] and cert["k3"])
        out.append(dict(arity=len(row), projected=cert["projected_count"], full_law=cert["full_law"], gate=gate))
    if law == "parity":
        oracle = exact_counts.Parity(rows)
        for row in rows:
            # The legacy histogram lists its first listed bit as the most significant.
            words = [int(w[::-1],2) for w,n in zip(exact_counts.boolean_words(len(row)),oracle.histogram(row)) if n]
            record(row,oracle.certificate(row),sorted(words))
    else:
        with exact_counts.NotAllEqualSupport(rows) as oracle:
            for row in rows:
                cert = oracle.certificate(row)
                record(row,cert,cert["projected_patterns"])
    return out


def status(rows, law):
    turn = end_operator.step(end_operator.from_stars(rows),law)
    return {"verdict":turn.status, "shortages":turn.shortages, "planned_parents":turn.parents}


def snapshot(law, rows):
    checks = certifications(law,rows)
    return dict(knots=len(rows),distinctions=1+max(map(max,rows)),states=state_count(law,rows),
                all_stated_laws=all(c["full_law"] for c in checks),
                all_displayed_knots=all(c["gate"] and c["gate"]["is_knot"] for c in checks),
                supports=rows,projections=checks)


def loose_slots(rows):
    holders = Counter(b for row in rows for b in row)
    return [deque(b for b in row if holders[b] == 1) for row in rows]


def advance(law, rival, rows):
    turn = end_operator.step(end_operator.from_stars(rows),law)
    if turn.status != "extend":
        return rows, status(rows,law)
    slots = loose_slots(rows)
    cursor = 1 + max(map(max,rows))
    additions = []
    births = []
    old_n = state_count(law,rows)
    restrictions = []
    for i,(parents,D,q) in enumerate(zip(turn.parents,turn.demand,turn.fresh,strict=True)):
        p = len(parents)
        assert sibling_demand(i,turn.parents) == D
        spent = tuple(sorted(slots[j].popleft() for j in parents))
        implied = input_implied(law,rows,spent)
        oracle_q = 0 if implied and D==0 else max(1,3-p,D)
        assert q == oracle_q
        f = granted(q,p,rival)
        if f == 0:
            restrictions.append(spent)
        survivors = state_count(law,rows+(spent,)) if f == 0 else old_n
        born = spent + tuple(range(cursor,cursor+f))
        cursor += f
        additions.append(born)
        births.append(dict(id=len(rows)+i, parents=parents,p=p,D=D,q=q,f=f,spent=spent,
                           implied=implied,solo_survivors=survivors,old_states=old_n))
    assert all(not slot for slot in slots)
    following = rows+tuple(additions)
    retained = state_count(law,rows+tuple(restrictions))
    return following,dict(verdict="extend",births=births,old_states=old_n,surviving_old=retained,
                          retained_fraction=str(Fraction(retained,old_n)),next_status=status(following,law))


def bond_table(law, rows, marks, doubled=False):
    if law == "parity":
        bonds = bond_checks.small_bonds(rows)
    elif doubled:
        owners,_ = bond_checks.incidence(rows)
        repeated = Counter(tuple(v) for v in owners.values() if len(v)>1)
        assert all(k>=2 for k in repeated.values())
        assert all(any(len(owners[b])==2 for b in row) for row in rows)
        assert not any(set(a)<=set(b) or set(b)<=set(a) for a,b in combinations(rows,2))
        bonds = sorted(map(bond_checks.mask,rows),key=int.bit_count)
    else:
        names,states = bond_checks.exact_small_states(rows,nae=True)
        bonds = sorted(bond_checks.nae_bonds(names,states),key=int.bit_count)
    return {",".join(map(str,t)):bond_checks.minimum_size(bonds,bond_checks.mask(t)) for n in range(1,len(marks)+1)
            for t in combinations(marks,n)}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--supplement",action="store_true",help="run only the post-freeze split-spare example")
    args = parser.parse_args()
    started = time.perf_counter()
    arms = {}
    sources = specimens()
    target = OUTPUT
    if args.supplement:
        meetings = [(i,(i+1) % 6) for i in range(6) for _ in range(2)]
        sources = {"six_split_spares":(from_links(6,meetings,[0,2,4,1,1,3]),3)}
        target = OUTPUT.with_name("supplement_split_spares.json")
    for source,(start,round_limit) in sources.items():
        for law in ("parity","nae"):
            for rival in ("ordinary","one_fewer","floor"):
                rows = start
                record = {"stages":[snapshot(law,start)], "rounds":[]}
                assert record["stages"][0]["all_displayed_knots"] and record["stages"][0]["all_stated_laws"]
                for t in range(round_limit):
                    following,receipt = advance(law,rival,rows)
                    record["rounds"].append(receipt)
                    if following == rows:
                        break
                    for birth in receipt["births"]:
                        if birth["p"] == 3 and (source.startswith("six_") and t==0 or source.startswith("four_") and t==1):
                            birth["old_bond_size_by_input_subset"] = bond_table(law,rows,birth["spent"],source.startswith("six_"))
                    rows = following
                    record["stages"].append(snapshot(law,rows))
                arms.setdefault(source,{}).setdefault(law,{})[rival] = record
    target.parent.mkdir(parents=True,exist_ok=True)
    result = {"elapsed_seconds":round(time.perf_counter()-started,6),"arms":arms,
              "sources":{k:{"open_allocation":"in ascending distinction and proposal order","rows":v[0],
                             "funded_round_limit":v[1]} for k,v in sources.items()}}
    if args.supplement:
        result["status"] = "Post-freeze targeted existence check, separate from the frozen panel."
    target.write_text(json.dumps(result,separators=(",",":"))+"\n")
    print(f"{len(arms)} sources, {sum(len(rs) for a in arms.values() for rs in a.values())} arms, {result['elapsed_seconds']} s")


if __name__ == "__main__":
    main()
