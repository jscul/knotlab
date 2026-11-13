#!/usr/bin/env python3
"""Base-16 finite observations, with an exact infinite-state extension.

In flip form p_x(r)=c_x(r)+x mod 2, an update may change r only
when both r+1 and r-2 have the opposite value. Keeping every value
is always an allowed update. The cone includes all predecessors of
every observed site. Any satisfying cone assignment extends to the
infinite base by keeping values outside the cone, and keeping whole
columns before/after it. See proof.md; no finite-period failure is used.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import subprocess
import sys
from pathlib import Path

from pysat.solvers import Minisat22

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))


class Cone:
    """Exact finite causal model for all observations in `support` (flip values)."""

    def __init__(self, support):
        self.support = tuple(sorted(set(map(tuple, support))))
        self.x0 = min(x for x, _ in self.support)
        self.x1 = max(x for x, _ in self.support)
        cone = set(self.support)
        for x in range(self.x1, self.x0, -1):
            for _, r in [p for p in cone if p[0] == x]:
                cone.update(((x - 1, r), (x - 1, r + 1), (x - 1, r - 2)))
        self.idx = {p: i + 1 for i, p in enumerate(sorted(cone))}
        clauses = []
        for x, r in sorted(cone):
            if x == self.x0:
                continue
            out = self.idx[(x, r)]
            own = self.idx[(x - 1, r)]
            for rr in (r + 1, r - 2):
                nb = self.idx[(x - 1, rr)]
                clauses.extend(([-own, -nb, out], [own, nb, -out]))
        self.clauses = clauses
        self.solver = Minisat22(bootstrap_with=clauses)
        self.aux = len(self.idx)

    def close(self):
        self.solver.delete()

    def lits(self, cells, bits):
        return [self.idx[tuple(c)] * (1 if b else -1) for c, b in zip(cells, bits)]

    def carries(self, cells, bits):
        return self.solver.solve(assumptions=self.lits(cells, bits))

    def relation(self, cells):
        cells = tuple(cells)
        return [list(b) for b in itertools.product((0, 1), repeat=len(cells)) if self.carries(cells, b)]

    def classify(self, cells):
        cells = tuple(cells)
        allowed = self.relation(cells)
        if len(allowed) == 1 << len(cells):
            return {"verdict": "free", "allowed": allowed}
        for i in range(len(cells)):
            shadow = {tuple(p[:i] + p[i+1:]) for p in allowed}
            if len(shadow) < 1 << (len(cells) - 1):
                return {"verdict": "proper-part-constrained", "allowed": allowed, "drop": i}
        from knotlab.relations import Relation
        from knotlab.knots import check_knot
        names = tuple(f"z{i}" for i in range(len(cells)))
        rel = Relation(names, frozenset(tuple(map(bool, p)) for p in allowed))
        report = check_knot(rel, names[:-1], names[-1])
        assert report.is_knot
        return {"verdict": "bond", "allowed": allowed, "knotlab": report.as_dict()}

    def backbone(self, assumptions, candidates):
        """All candidate variables logically fixed by these assumptions."""
        # Old guarded queries are logically inert but need not accumulate.
        if self.aux > len(self.idx)+512:
            self.solver.delete()
            self.solver=Minisat22(bootstrap_with=self.clauses)
            self.aux=len(self.idx)
        s = self.solver
        if not s.solve(assumptions=assumptions):
            return None
        model = {abs(v): (v > 0) for v in s.get_model()}
        remaining = {v: model[v] for v in candidates}
        while remaining:
            self.aux += 1
            guard = self.aux
            s.add_clause([-guard] + [-v if b else v for v, b in remaining.items()])
            if not s.solve(assumptions=assumptions + [guard]):
                break
            model = {abs(v): (v > 0) for v in s.get_model()}
            remaining = {v: b for v, b in remaining.items() if model[v] == b}
        return remaining


class Rectangle(Cone):
    """A second exact model, using the three-row folding extension lemma."""

    def __init__(self, support):
        self.support = tuple(sorted(set(map(tuple, support))))
        self.x0 = min(x for x, _ in self.support)
        self.x1 = max(x for x, _ in self.support)
        lo = min(r for _, r in self.support)
        hi = max(r for _, r in self.support)
        hi = max(hi, lo+2)
        self.lo, self.hi = lo, hi
        cells = [(x,r) for x in range(self.x0,self.x1+1) for r in range(lo,hi+1)]
        self.idx = {c:i+1 for i,c in enumerate(cells)}
        clauses=[]
        # Original-colour NAE clauses are encoded first, then gauged into p.
        for x in range(self.x0,self.x1):
            for r in range(lo,hi+1):
                for edge in (((x,r),(x,r+1),(x+1,r)),
                             ((x,r),(x,r+2),(x+1,r+2))):
                    if not all(c in self.idx for c in edge):
                        continue
                    clause=[self.idx[c] * (-1 if c[0]%2 else 1) for c in edge]
                    clauses.extend((clause,[-v for v in clause]))
        self.clauses=clauses
        self.solver=Minisat22(bootstrap_with=clauses)
        self.aux=len(self.idx)


def fold_row(r, lo, hi):
    assert hi-lo >= 2
    if r < lo:
        return lo+(r-lo)%3
    if r > hi:
        return hi-2+(r-(hi-2))%3
    return r


def heddle(y, k):
    rows = ([0, 1, 2] + list(range(4, y+1, 2)) if y % 2 == 0
            else [-1, 0, 1] + list(range(3, y+1, 2)))
    return [(0, r) for r in rows] + [(k, y)]


def downward(y, k):
    n = -y
    if n % 2 == 0:
        j = (n-2)//2
        mids = [(1, -2*i) for i in range(j)]
        bottom = [(0, -2*j-2), (0, -2*j-1)]
    else:
        j = (n-3)//2
        mids = [(1, -2*i) for i in range(j+1)]
        bottom = [(0, -2*j-3), (0, -2*j-1)]
    return sorted([(0, 0)] + mids + bottom) + [(k, y)]


def path_values(a0, ds, end=None):
    """A path a_i=a_(i+1) => d_i=a_i; optional prescribed last value."""
    paths={a0:[a0]}
    for d in ds:
        nxt={}
        for a,path in paths.items():
            for b in (0,1):
                if a != b or a == d:
                    nxt.setdefault(b,path+[b])
        paths=nxt
    if end is None:
        return next(iter(paths.values()))
    return paths.get(end)


def downward_expected(cells, bits, y, k):
    vals=dict(zip(cells,bits))
    ell=(-y-1)//2
    ds=[vals[(1,-2*i)] for i in range(ell)]
    a=vals[(0,0)]
    for d in ds:
        if a == d:
            return True
        a=d
    v=vals[(0,y)]
    w=vals[(0,y+(1 if (-y)%2==0 else 2))]
    return not (a==v==w and vals[(k,y)] != v)


def construct_downward(y, k, cells, bits):
    """Three full flip-form columns, given as finite modifications of a constant.

    For every allowed pattern of the theorem, the columns 0,1,2 below
    realize it. Keep column 0 to the left and column 2 to the right.
    """
    assert y <= -3 and k >= 2
    if not downward_expected(cells,bits,y,k):
        return None
    vals=dict(zip(cells,bits))
    ell=(-y-1)//2
    ds=[vals[(1,-2*i)] for i in range(ell)]
    v=vals[(0,y)]
    other=y+(1 if (-y)%2==0 else 2)
    w=vals[(0,other)]
    target=vals[(k,y)]
    # When the target differs, avoid the persistent bottom triple.
    path=path_values(vals[(0,0)],ds,1-v) if target != v else None
    if path is None:
        path=path_values(vals[(0,0)],ds)
    default=1-v
    c0={-2*i:a for i,a in enumerate(path)}
    c0.update({y:v,other:w})
    for i,d in enumerate(ds):
        if path[i] != d:
            c0[-2*i+1]=d
    c1=dict(c0)
    for i,d in enumerate(ds):
        c1[-2*i]=d
    if target != v:
        middle=c0.get(y+1,default)
        if middle != v:
            c1[y]=target
        else:
            assert c0.get(y+2,default) != v
            c1[y+1]=target
    c2=dict(c1)
    c2[y]=target
    return {"default":default,"columns":[c0,c1,c2]}


def validate_constructed(witness, cells, bits):
    default=witness["default"]
    columns=witness["columns"]
    def value(x,r):
        return columns[min(2,max(0,x))].get(r,default)
    for x in (0,1):
        keys=set(columns[x]) | set(columns[x+1])
        for r in keys:
            own,nxt=value(x,r),value(x+1,r)
            if own != nxt and (value(x,r+1) != nxt or value(x,r-2) != nxt):
                return False
    return all(value(x,r)==b for (x,r),b in zip(cells,bits))


def search4(k, y, xmin=-1, xmax=None, rmin=-3, rmax=None):
    """All four-site bonds in a named box, found through exact backbones."""
    xmax = k+1 if xmax is None else xmax
    rmax = y+3 if rmax is None else rmax
    cells = [(x,r) for x in range(xmin, xmax+1) for r in range(rmin, rmax+1)]
    origin, target = (0,0), (k,y)
    assert origin in cells and target in cells
    co = Rectangle(cells)
    obs = {co.idx[c]: c for c in cells if c not in (origin,target)}
    found = []
    seen = set()
    for b in (0, 1):
        for a in obs:
            for av in (False, True):
                ass = co.lits((origin,target),(0,b)) + [a if av else -a]
                forced = co.backbone(ass, [v for v in obs if v != a])
                if forced is None:
                    continue
                for v, bv in forced.items():
                    support = tuple(sorted((origin,target,obs[a],obs[v])))
                    if support in seen:
                        continue
                    seen.add(support)
                    test = co.classify(support)
                    if test["verdict"] == "bond":
                        found.append({"cells": support, **test})
    co.close()
    return {"k": k, "y": y, "box": [xmin,xmax,rmin,rmax], "four_bonds": found}


def search5(k, y, xmin=-1, xmax=None, rmin=-2, rmax=None):
    xmax=k+1 if xmax is None else xmax
    rmax=y+2 if rmax is None else rmax
    cells=[(x,r) for x in range(xmin,xmax+1) for r in range(rmin,rmax+1)]
    origin,target=(0,0),(k,y)
    co=Rectangle(cells)
    obs={co.idx[c]:c for c in cells if c not in (origin,target)}
    variables=list(obs)
    found=[]
    seen=set()
    prefixes=0
    for b in (0,1):
        for ia,a in enumerate(variables):
            for ib in range(ia+1,len(variables)-1):
                q=variables[ib]
                for av,qv in itertools.product((0,1),repeat=2):
                    ass=co.lits((origin,target),(0,b))+[a if av else -a,q if qv else -q]
                    forced=co.backbone(ass,variables[ib+1:])
                    prefixes+=1
                    if forced is None:
                        continue
                    for v,bv in forced.items():
                        support=tuple(sorted((origin,target,obs[a],obs[q],obs[v])))
                        if support in seen:
                            continue
                        seen.add(support)
                        test=co.classify(support)
                        if test["verdict"] == "bond":
                            found.append({"cells":support,**test})
    co.close()
    return {"k":k,"y":y,"box":[xmin,xmax,rmin,rmax],"prefixes":prefixes,
            "candidate_supports_classified":len(seen),"five_bonds":found}


def serial_attack():
    """Remove two old helpers and add one arbitrarily timed helper."""
    out=[]
    for n,k in ((5,5),(7,5),(5,11),(7,11)):
        y=-n
        base=downward(y,k)
        origin,target=(0,0),(k,y)
        helpers=[c for c in base if c not in (origin,target)]
        xs=sorted(set((-16,-4,-1,0,1,2,4,k//2,k,k+1,2*k,32)))
        pool=[(x,r) for x in xs for r in range(y-2,4)]
        co=Rectangle(base+pool)
        counts={"free":0,"proper-part-constrained":0,"bond":0}
        seen=set()
        witnesses=[]
        for drop in itertools.combinations(helpers,2):
            retained=[c for c in base if c not in drop]
            for add in pool:
                if add in retained:
                    continue
                support=tuple(sorted(retained+[add]))
                if support in seen:
                    continue
                seen.add(support)
                allowed=co.relation(support)
                if len(allowed) == 1 << len(support):
                    counts["free"]+=1
                elif any(len({tuple(p[:i]+p[i+1:]) for p in allowed}) < 1 << (len(support)-1)
                         for i in range(len(support))):
                    counts["proper-part-constrained"]+=1
                else:
                    counts["bond"]+=1
                    witnesses.append({"cells":support,**co.classify(support)})
        co.close()
        out.append({"n":n,"k":k,"base_size":len(base),"tested_size":len(base)-1,
                    "added_along_counts":xs,"added_across_interval":[y-2,3],
                    "counts":counts,"smaller_bonds":witnesses})
    # Two opposed-change constraints cannot simply be concatenated through
    # an unobserved middle event: the middle event can remain unchanged.
    concatenation=[]
    for t in (0,2,4,8,16,32):
        support=[(0,0),(1,0),(t,6),(t+1,6)]
        co=Rectangle(support)
        allowed=co.relation(support)
        co.close()
        concatenation.append({"later_event_along_count":t,"allowed_patterns":len(allowed),
                              "free":len(allowed)==16})
    return {"replacement_family":out,"serial_opposed_changes":concatenation,
            "scope":"finite attempted counterexamples; no global lower bound inferred"}


def replay():
    from knotlab.knots import check_knot
    from knotlab.relations import Relation
    # Both folding boundaries, every legal pair of words, and more than one
    # exterior period. The proof supplies the infinite/all-width quantifier.
    fold_cases=0
    for width in range(3,7):
        lo,hi=-2,width-3
        for p,q in itertools.product(itertools.product((0,1),repeat=width),repeat=2):
            legal=all(not(p[i]==p[j] and q[i]!=p[i])
                      for i in range(width) for j in (i+1,i-2) if 0<=j<width)
            if not legal:
                continue
            for r in range(lo-12,hi+13):
                a=p[fold_row(r,lo,hi)-lo]
                b=q[fold_row(r,lo,hi)-lo]
                if a != b:
                    assert all(p[fold_row(s,lo,hi)-lo]==b for s in (r+1,r-2))
            fold_cases+=1
    downward_cases=[]
    total_constructed=0
    for n in range(3,25):
        for k in (2,3,11):
            support=downward(-n,k)
            co=Rectangle(support)
            missing=[]
            realized=0
            for p in itertools.product((0,1),repeat=len(support)):
                expected=downward_expected(support,p,-n,k)
                assert co.carries(support,p)==expected,(n,k,p)
                witness=construct_downward(-n,k,support,p)
                assert (witness is not None)==expected
                if witness is not None:
                    assert validate_constructed(witness,support,p),(n,k,p)
                    total_constructed+=1
                    realized+=1
                else:
                    missing.append(list(p))
            co.close()
            assert len(missing)==2
            assert all(a!=b for a,b in zip(*missing))
            downward_cases.append({"n":n,"k":k,"size":len(support),
                                   "realized_patterns":realized,"excluded":missing,
                                   "single_deletions_full":True})
    comparisons=[]
    examples=[heddle(y,7) for y in (2,3,4,5,6)]
    examples += [downward(y,7) for y in (-3,-4,-5,-6,-7,-8)]
    examples += [[(0,0),(1,0),(0,3),(1,3)],[(0,0),(0,2),(1,4),(2,4)],
                 [(0,0),(2,2),(4,-1),(5,3)]]
    for support in examples:
        a,b=Cone(support),Rectangle(support)
        ar,br=a.relation(support),b.relation(support)
        a.close();b.close()
        assert ar==br,support
        comparisons.append({"cells":support,"allowed_patterns":len(ar)})
    # Public K1--K3 operation on exact relations, including a malformed claim
    # that must reject. Keep these small; minimum_width is exhaustive.
    reports=[]
    for n,k in ((3,2),(4,2),(5,3),(6,11)):
        support=downward(-n,k)
        co=Rectangle(support);allowed=co.relation(support);co.close()
        names=tuple(f"z{i}" for i in range(len(support)))
        relation=Relation(names,frozenset(tuple(map(bool,p)) for p in allowed))
        report=check_knot(relation,names[:-1],names[-1]).as_dict()
        assert report["is_knot"]
        reports.append({"n":n,"k":k,"report":report})
    support=downward(-4,1)
    co=Rectangle(support);allowed=co.relation(support);co.close()
    names=tuple(f"z{i}" for i in range(len(support)))
    wrong=check_knot(Relation(names,frozenset(tuple(map(bool,p)) for p in allowed)),names[:-1],names[-1])
    assert not wrong.is_knot
    # The claimed separator is actually a bond, not independent halves.
    support=[(0,0),(1,0),(0,3),(1,3)]
    co=Rectangle(support);separator=co.classify(support);co.close()
    assert separator["verdict"]=="bond"
    # CLI check built from the relation computed on the infinite base.
    support=downward(-3,2)
    co=Rectangle(support);allowed=co.relation(support);co.close()
    allowed_set=set(map(tuple,allowed))
    forbidden=[p for p in itertools.product((0,1),repeat=len(support)) if p not in allowed_set]
    names=[f"z{i}" for i in range(len(support))]
    cnf="; ".join(" ".join(("~" if bit else "")+name for name,bit in zip(names,p)) for p in forbidden)
    cmd=[sys.executable,"-B","-m","knotlab","check","--cnf",cnf,
         "--loops",*names[:-1],"--contact",names[-1],"--json"]
    env=dict(os.environ,PYTHONPATH=str(ROOT/"tools"))
    cli=subprocess.run(cmd,cwd=ROOT,env=env,text=True,capture_output=True,check=True)
    cli_report=json.loads(cli.stdout)
    assert cli_report["is_knot"]
    return {"folding_legal_word_pairs_checked":fold_cases,
            "downward_exact_cases":downward_cases,"constructed_extensions_checked":total_constructed,
            "two_exact_encodings":comparisons,"knotlab_reports":reports,
            "k_one_overstatement_rejected":not wrong.is_knot,
            "empty_gap_separator_rejected":separator,
            "knotlab_cli":{"command":cmd,"report":cli_report}}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--search4",nargs=2,type=int)
    ap.add_argument("--search5",nargs=2,type=int)
    ap.add_argument("--attack",action="store_true")
    ap.add_argument("--write",action="store_true")
    args=ap.parse_args()
    if args.search4:
        print(json.dumps(search4(*args.search4),indent=1))
        return
    if args.search5:
        print(json.dumps(search5(*args.search5),indent=1))
        return
    if args.attack:
        print(json.dumps(serial_attack(),indent=1))
        return
    checks=replay()
    # Preserve completed searches without treating their finite box as a
    # theorem about unrestricted support. --write consolidates the records.
    searches=[]
    for name in ("search4_5_3.json","search4_2_4.json","search5_5_5.json"):
        path=HERE/name
        if path.exists() and path.stat().st_size:
            searches.append(json.loads(path.read_text()))
    old_path=HERE/"result.json"
    old=json.loads(old_path.read_text()) if old_path.exists() else {}
    if not searches:
        searches=old.get("finite_mixed_support_searches",[])
    attack_path=HERE/"serial_attack.json"
    attacks=(json.loads(attack_path.read_text()) if attack_path.exists() and attack_path.stat().st_size
             else old.get("serial_conflict_attack"))
    manifest=json.loads((HERE/"manifest.json").read_text())
    parents=[ROOT/"proofs/ACROSS-FOLD-20261112-001A/ACROSS-FOLD-20261112-001A-P001_ladders/proof.md",
             ROOT/"proofs/FOLD-20261112-001A/FOLD-20261112-001A-P001_folded_direction/proof.md"]
    result={"schema_version":3,"artifact_id":manifest["artifact_id"],"kind":"proof",
            "ticket":manifest["ticket"],"proof":manifest["proof"],"status":"passed",
            "target_status":"Partial","claim":manifest["claim"],
            "uniform_statements":"argued-in-prose: exact downward relation for every n>=3,k>=2; exact rectangle extension",
            "sharp_unrestricted_lower_bound":"open",
            "source_status":"K1-K3 relation proved; not native at the uniform flip-value solution",
            "validation_level":"V1: hand proof and two same-task exact finite encodings",
            "checks":checks,"finite_mixed_support_searches":searches,"serial_conflict_attack":attacks,
            "dependencies_sha256":{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in parents},
            "owned_sources_sha256":{name:hashlib.sha256((HERE/name).read_bytes()).hexdigest()
                                    for name in ("proof.md","check.py","manifest.json")},
            "failures":[]}
    if args.write:
        (HERE/"result.json").write_text(json.dumps(result,indent=1)+"\n")
    print(json.dumps({"status":result["status"],"target_status":result["target_status"],
                      "downward_cases":len(checks["downward_exact_cases"]),
                      "constructed_extensions":checks["constructed_extensions_checked"],
                      "failures":result["failures"]},indent=1))


if __name__ == "__main__":
    main()
