"""Physical completion counts, local certificates, heralds and funded-stage minima."""
from collections import Counter, defaultdict
from functools import cache
from fractions import Fraction as F
from itertools import combinations, permutations, product
from pathlib import Path
import json
import math
import os
import subprocess
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "holders.json"
PRIOR = "ORDINARY-DYNAMICS-20261120-001A"
sys.path.append(str(ROOT / "experiments" / PRIOR / (PRIOR + "-E001_ordinary")))
import end_operator as ordinary


def mask(names):
    return sum(1 << name for name in names)


def pack(x, names):
    return sum(((x >> name) & 1) << i for i, name in enumerate(names))


def frozen(stars):
    return tuple(tuple(sorted(row)) for row in stars)


@cache
def words(stars, law):
    n = 1 + max(max(row) for row in stars)
    masks = tuple(map(mask, stars))
    if law == "parity":
        return tuple(x for x in range(1 << n) if all((x & k).bit_count() % 2 == 0 for k in masks))
    return tuple(x for x in range(1 << n) if all((x & k) not in (0, k) for k in masks))


@cache
def lawful(stars, law):
    allowed = words(stars, law)
    return bool(allowed) and all(len({pack(x, row) for x in allowed}) ==
                                 (2 ** (len(row)-1) if law == "parity" else 2 ** len(row)-2)
                                 for row in stars)


def physical_gram(stars, marks, law):
    states = words(stars, law)
    shown = mask(marks)
    hidden = defaultdict(list)
    for word in states:
        hidden[word & ~shown].append(pack(word, marks))
    g = np.zeros((8,8), dtype=np.int64)
    for subset in hidden.values():
        g[np.ix_(subset,subset)] += 1
    return g


def moment(g, flip, read=0):
    n = len(g)
    return F(sum((-1)**((x & read).bit_count()) * int(g[x, x ^ flip]) for x in range(n)),
             int(np.trace(g)))


def exact_ternary(g):
    assert int(g[0,0]) == int(g[7,7]) == 0 and (g >= 0).all() and (g[::-1,::-1] == g).all()
    total = int(np.trace(g))
    p = [F(int(g[1<<i,1<<i]+g[7^(1<<i),7^(1<<i)]),total) for i in range(3)]
    assert sum(p) == 1
    xmom = [moment(g, s) for s in range(8)]
    assert all(moment(g,1<<i,7^(1<<i)) == -xmom[1<<i] for i in range(3))
    gaps = []
    for keep in (6,5,3,7):
        probability = sum(xmom[t] for t in range(8) if t & keep == t)/(1 << keep.bit_count())
        bound = 1 - sum((p[i]/2 for i in range(3) if keep >> i & 1), F(0))
        gaps.append(probability-bound)
    m = xmom[7]+sum(xmom[1<<i] for i in range(3))
    return dict(local=max(gaps)<=0, minority=list(map(str,p)), plus_probability_minus_bound=list(map(str,gaps)),
                inequality_order=["BC","AC","AB","ABC"], m=str(m))


def primitive(g):
    entries = tuple(map(int,g.flat))
    div = math.gcd(*entries)
    return tuple(x//div for x in entries)


@cache
def certified(key):
    import three
    return three.basic(np.array(key, dtype=np.int64).reshape(8,8))


def classify(g):
    if g[0,0] == g[7,7] == 0 and np.array_equal(g, g[::-1,::-1]) and np.min(g)>=0:
        info=exact_ternary(g)
        return info["local"], info["m"]
    report = certified(primitive(g))
    return bool(report["common"]["local"]), report["m"]


def data(stars, marks, law):
    if max(max(s) for s in stars) <= 16:
        return physical_gram(stars, marks, law)
    import three
    return np.asarray(three.gram(stars, marks, law), dtype=np.int64)


def branch(parts, sizes):
    stars = [[0,1,2]]
    next_bit=3
    for inside, arity in zip(parts, sizes, strict=True):
        new = list(range(next_bit,next_bit+arity-len(inside)))
        stars.append([*inside,*new])
        next_bit+=len(new)
    return frozen(stars)


def core_cases():
    import three
    cases = {}
    placements = [([], []), ([[0]],[3]), ([[0],[1]],[3,3]), ([[0,1]],[3]),
                  ([[0,1],[2]],[3,3]), ([[0,1,2]],[3])]
    placements += [([[0],[1],[2]],[q,q,q]) for q in (3,4,5)]
    for groups, sizes in placements:
        stars=branch(groups,sizes)
        for law in ("parity","nae"):
            assert lawful(stars,law)
            g=physical_gram(stars,(0,1,2),law)
            second=np.asarray(three.gram(stars,(0,1,2),law))
            assert np.array_equal(g,second)
            report=certified(primitive(g))
            test=exact_ternary(g) if law=="nae" else None
            if test:
                assert test["local"]==report["common"]["local"] and F(test["m"])==F(report["m"])
            key=str((groups,sizes,law))
            if all(len(group)==1 for group in groups) and law=="nae":
                lambdas=[F(1),F(1),F(1)]
                for (i,),q in zip(groups,sizes):
                    lambdas[i]=F(2**(q-1)-2,2**(q-1)-1)
                predicted=math.prod(lambdas)+F(2,3)*sum(lambdas)
                assert predicted==F(report["m"])
                scale=int(g[1,1])
                assert all(F(int(g[x,y]),scale)==math.prod(lambdas[i] for i in range(3) if (x^y)>>i&1)
                           for x in range(1,7) for y in range(1,7))
            cases[key]=dict(stars=stars,law=law,marks=[0,1,2],gram=g.tolist(),criterion=test,behavior=report)
    return cases


def branch_readings():
    import three
    stars=branch([[0],[1],[2]],[3,3,3])
    remote=tuple(range(3,9))
    answers={}
    for law in ("parity","nae"):
        initial=words(stars,law)
        base=physical_gram(stars,(0,1,2),law)
        pure=physical_gram(frozen([[0,1,2]]),(0,1,2),law)
        target=certified(primitive(pure))
        look={x:pack(x,remote) for x in initial}
        # On the full pure weighting, a product of selected changes just permutes physical names.
        changes=[mask(stars[i+1] if law=="nae" else (i,3+2*i)) for i in range(3)]
        initial_set=set(initial)
        intervals={}
        for transition in range(8):
            t=0
            for i in range(3):
                if transition>>i&1: t ^= changes[i]
            for z in range(8):
                if z & transition: continue
                observed=F(sum((-1)**((w&z).bit_count()) for w in initial if (w^t) in initial_set),len(initial))
                assert observed==moment(pure,transition,z)
                intervals[str((transition,z))]=str(observed)
        protocols={}
        for basis_name in ("Z","X"):
            matrices={}
            records=[]
            coherent_sum=np.zeros((8,8),dtype=np.int64)
            corrected_sum=coherent_sum.copy()
            accepted_sum=coherent_sum.copy()
            total=0
            for h in range(64):
                amp=[0]*8
                for w,r in look.items():
                    if basis_name=="Z":
                        amp[w&7] += r==h
                    else:
                        amp[w&7] += (-1)**((r&h).bit_count())
                norm=sum(v*v for v in amp)
                if not norm:
                    records.append(dict(herald=h,probability="0"))
                    continue
                denom=len(initial)*(64 if basis_name=="X" else 1)
                g=np.outer(amp,amp)
                matrix_key=primitive(g)
                if matrix_key not in matrices:
                    matrices[matrix_key]=len(matrices)
                corrected_amp=amp[:]
                correction=0
                if basis_name=="X":
                    # NAE complements all private marks; parity flips just the first private mark.
                    for i in range(3):
                        local=(h>>(2*i))&3
                        affected=(local.bit_count()%2) if law=="nae" else local&1
                        correction|=affected<<i
                    corrected_amp=[v*(-1)**((x&correction).bit_count()) for x,v in enumerate(amp)]
                gc=np.outer(corrected_amp,corrected_amp)
                if basis_name=="X":
                    assert primitive(gc)==primitive(pure)
                accepted=all(((h>>(2*i))&3) in (1,2) for i in range(3)) if basis_name=="Z" else h==0
                coherent_sum+=g
                corrected_sum+=gc
                if accepted:
                    accepted_sum+=g
                total+=norm
                records.append(dict(herald=h,probability=str(F(norm,denom)),conditional=matrices[matrix_key],
                                    correction_mask=correction,accepted=accepted))
            assert total==denom and primitive(coherent_sum)==primitive(base)
            if basis_name=="X": assert primitive(corrected_sum)==primitive(pure)
            table_list=[certified(key) for key in matrices]
            nonlocal_weight=sum((F(r["probability"]) for r in records if r["probability"]!="0" and
                                 not table_list[r["conditional"]]["common"]["local"]),F(0))
            protocols[basis_name]=dict(heralds=records, distinct_tables=table_list,
                nonlocal_conditional_probability=str(nonlocal_weight),
                ignored=certified(primitive(coherent_sum)), all_trial_corrected=certified(primitive(corrected_sum)),
                accepted_probability=str(F(int(np.trace(accepted_sum)),total)),
                accepted_table=certified(primitive(accepted_sum)) if np.trace(accepted_sum)>0 else None)
        answers[law]=dict(stars=stars,central_reads=[0,1,2],remote_marks=remote,enlarged_changes=changes,
                          enlarged_moments=intervals,enlarged_table=target,heralds=protocols)
    return answers


def incidence(shared, loose):
    n=len(loose)
    stars=[[] for _ in loose]
    name=0
    for (a,b),count in zip(combinations(range(n),2),shared):
        both=list(range(name,name+count))
        stars[a]+=both
        stars[b]+=both
        name+=count
    for a,count in enumerate(loose):
        stars[a]+=range(name,name+count)
        name+=count
    return frozen(stars)


def connected(n, pairs, counts):
    reached={0}
    for _ in range(n-1):
        for (i,j),c in zip(pairs,counts):
            if c and (i in reached or j in reached):
                reached.update((i,j))
    return len(reached)==n


@cache
def symmetries(n):
    contacts=list(combinations(range(n),2))
    return [tuple(p)+tuple(n+contacts.index(tuple(sorted((p[i],p[j])))) for i,j in contacts)
            for p in permutations(range(n))]


def is_first(loose, links):
    code=tuple(loose)+tuple(links)
    return not any(tuple(code[i] for i in perm)<code for perm in symmetries(len(loose)))


def trivalent(n):
    contacts=list(combinations(range(n),2))
    def extend(i, degree, links):
        if i==len(contacts):
            loose=tuple(3-d for d in degree)
            if connected(n,contacts,links) and is_first(loose,links):
                yield incidence(links,loose)
            return
        a,b=contacts[i]
        for c in range(1+min(3-degree[a],3-degree[b])):
            degree[a]+=c
            degree[b]+=c
            yield from extend(i+1,degree,(*links,c))
            degree[a]-=c
            degree[b]-=c
    yield from extend(0,[0]*n,())


def compositions(total, parts):
    if parts==1:
        yield (total,)
    else:
        for count in range(total+1):
            for tail in compositions(total-count,parts-1):
                yield (count,*tail)


def by_width(m):
    # Every source enumerated here is open. The last growth under NAE brings a fresh distinction.
    for n in range(1,(2*m-1)//3+1):
        pairs=list(combinations(range(n),2))
        if not pairs:
            if m>=3: yield incidence((),(m,))
            continue
        for count in range(max(n-1,3*n-m),m):
            for links in compositions(count,len(pairs)):
                if not connected(n,pairs,links): continue
                degree=[0]*n
                for (a,b),c in zip(pairs,links):
                    degree[a]+=c
                    degree[b]+=c
                minimum=[max(0,3-d) for d in degree]
                available=m-count-sum(minimum)
                if available<0: continue
                for add in compositions(available,n):
                    loose=tuple(x+y for x,y in zip(minimum,add))
                    if is_first(loose,links): yield incidence(links,loose)


def forward(stars,law):
    actual=ordinary.from_stars(stars)
    plan=ordinary.step(actual,law)
    if plan.status!="extend": return plan.status,None
    n=max(max(s) for s in stars)+1
    holdings=Counter(b for h in stars for b in h)
    available=[iter(sorted(b for b in row if holdings[b]==1)) for row in stars]
    formed=list(stars)
    for parents,k in zip(plan.parents,plan.fresh):
        consumed=[next(available[i]) for i in parents]
        formed.append((*consumed,*range(n,n+k)))
        n+=k
    return plan.status,frozen(formed)


def largest(stars):
    return max(max(s) for s in stars)+1


def ternary_verdicts(stars,law="nae"):
    rows=[]
    degree=Counter(x for star in stars for x in star)
    for i,star in enumerate(stars):
        if len(star)!=3: continue
        g=data(stars,star,law)
        local,m=classify(g)
        rows.append(dict(i=i,loose=sum(degree[x]==1 for x in star),local=local,m=m))
    return rows


def examined(stars,law="nae",detailed=False):
    marked=ternary_verdicts(stars,law)
    wide=[]
    for i,star in enumerate(stars):
        if len(star)<=3: continue
        for c in combinations(star,3):
            g=data(stars,c,law)
            local,m=classify(g)
            wide.append(dict(i=i,marks=c,local=local,m=m))
    return dict(ternary=len(marked),nonlocal_ternary=sum(not r["local"] for r in marked),
                wide_triples=len(wide),nonlocal_wide_triples=sum(not r["local"] for r in wide),
                largest=max((F(r["m"]) for r in marked+wide),default=F(0)).__str__(),
                **(dict(marked=marked,wide=wide) if detailed else {}))


def all_ternary_census():
    rows=[]
    found_null=False
    for n in range(1,6):
        for stars in trivalent(n):
            if not lawful(stars,"nae"): continue
            status,_=forward(stars,"nae")
            verdict=ternary_verdicts(stars)
            if status=="extend" and all(r["local"] for r in verdict):
                found_null=True
            rows.append(dict(stars=stars,n=n,distinct=largest(stars),next=status,knots=verdict))
        if n>=4 and found_null: break
    return rows


def growth_fixtures():
    import three
    cases={}
    for n in range(3,7):
        cases["one_"+str(n)]=frozen([range(n)])
    cases.update(repeated_pair=frozen([[0,1,2],[0,1,3]]),
                 three_mutually_meeting_ternaries=incidence([1,1,1],[1,1,1]),
                 four_mutually_meeting=incidence([1]*6,[1]*4))
    out={}
    for name,stars in cases.items():
        for law in ("nae","parity"):
            assert lawful(stars,law)
            status,grown=forward(stars,law)
            initial=examined(stars,law,True)
            res=dict(source=stars,source_report=initial,first_status=status)
            if grown and largest(grown)<=16:
                res["reached_full_local_projections"]=lawful(grown,law)
                assert res["reached_full_local_projections"]
            # Single widths five and six have larger first stages; conditional independence
            # gives every local triple by the same one-mark branch calculation below.
            if grown and name in ("one_5","one_6"):
                n=int(name[-1]);assert len(grown)==n+1 and set(map(len,grown))=={n}
                # All coordinates of a split leaf or old holder fall into three orbits.
                res["reached"]=grown
                res["source_orbit_model"]="one central holder with independent single-mark branches"
                res["next_status"]=ordinary.step(ordinary.from_stars(grown),law).status
                report=[]
                for i,marks in ((0,grown[0][:3]),(1,grown[1][:3]),(1,grown[1][-3:])):
                    g=np.asarray(three.gram(grown,marks,law))
                    local,m=classify(g)
                    report.append(dict(i=i,marks=marks,local=local,m=m))
                res["representatives"]=report
            elif grown:
                res.update(reached=grown,reached_report=examined(grown,law,True),
                           next_status=ordinary.step(ordinary.from_stars(grown),law).status)
            out[name+"_"+law]=res
    return out


def wider_model():
    """The three-mark marginal of a single four-place NAE rule has this rational common model."""
    g=physical_gram(frozen([range(4)]),(0,1,2),"nae")
    answer=certified(primitive(g))
    # One unit is 1/56 before independently choosing one of the two orientations of Z.
    entries=[(0, None, 4)]+[(0,i,15) for i in range(3)]
    for neg in range(1,8):
        minority=neg.bit_length()-1 if neg.bit_count()==1 else None
        entries.append((neg,minority,1))
    for row in answer["rows"]:
        observed=Counter()
        axes=row["settings"]
        for neg,minority,count in entries:
            for reverse in (0,7):
                z=reverse^(0 if minority is None else 1<<minority)
                out=sum((((z if axis else neg)>>i)&1)<<i for i,axis in enumerate(axes))
                observed[out]+=count
        assert all(F(observed[i],112)==F(value,row["denominator"]) for i,value in enumerate(row["numerators"]))
    return dict(denominator_before_Z_orientation=56,entries=entries,verified_full_table=answer)


def three_holder_proof():
    """Linear coefficients for arbitrary private widths on the only remaining two-outside-holder shapes."""
    rows={}
    for left,right in (((0,),(1,)),((0,1),(2,))):
        for meet in (False,True):
            masks=[np.zeros((8,8),dtype=np.int64) for _ in range(4)]
            for x,y in product(range(1,7),repeat=2):
                forbidden=[]
                for group in (left,right):
                    values=set()
                    for word in (x,y):
                        within={(word>>b)&1 for b in group}
                        if len(within)==1:values.update(within)
                    forbidden.append(values)
                a,b=forbidden
                coefficients=(1,-len(a),-len(b),len(a&b) if meet else len(a)*len(b))
                for array,number in zip(masks,coefficients):array[x,y]=number
            expressions=[]
            for g in masks:
                trace=int(np.trace(g))
                p=[int(g[1<<i,1<<i]+g[7^(1<<i),7^(1<<i)]) for i in range(3)]
                xs=[sum(int(g[w,w^t]) for w in range(8)) for t in range(8)]
                if len(left)==2:
                    gap=2*sum(xs[t] for t in (0,1,2,3))-4*(trace+p[2])
                else:
                    gap=sum(xs)-4*trace
                expressions.append(gap)
            expected=([4,-4,-4,0 if meet else 4] if len(left)==2 else
                      [12,-30,-30,30 if meet else 58])
            assert expressions==expected
            checks=[]
            for u,v,w in product(range(4),range(4),range(3)):
                if bool(w)!=meet or u+w+len(left)<3 or v+w+len(right)<3:continue
                ambient=2**(u+v+w)
                multipliers=(ambient,2**v,2**u,1)
                g=sum(m*g for m,g in zip(multipliers,masks))
                gap=sum(m*c for m,c in zip(multipliers,expressions))
                assert gap>0
                remaining=3
                names=tuple(range(remaining,remaining+w))
                remaining+=w
                K=(*left,*names,*range(remaining,remaining+u))
                remaining+=u
                L=(*right,*names,*range(remaining,remaining+v))
                stars=frozen([(0,1,2),K,L])
                assert np.array_equal(physical_gram(stars,(0,1,2),"nae"),g)
                checks.append((u,v,w,gap))
            rows[str((left,right,meet))]=dict(excess_times_eight_trace=expressions,
                    coefficient_order=["2^(u+v+w)","2^v","2^u","1"],physical_crosschecks=checks)
    return rows


def new_minima():
    # Search by increasing physically distinct names, including multiple meetings and equal holders.
    # A target of width w has a predecessor of width at most w-1 under ordinary NAE.
    minima={}
    counts=[]
    def record(key,stars,source,kind):
        m=largest(stars)
        n=len(stars)
        prior=minima.get(key)
        if prior is None or (m,n)<(prior["width"],prior["holders"]):
            minima[key]=dict(width=m,holders=n,target=stars,source=source,kind=kind)
    for m in range(3,9):
        row=Counter()
        for stars in by_width(m):
            row["connected_open"]+=1
            if not lawful(stars,"nae"):continue
            row["lawful"]+=1
            status,grown=forward(stars,"nae")
            if status!="extend":continue
            row["funded"]+=1
            if ternary_verdicts(stars) and all(r["local"] for r in ternary_verdicts(stars)):
                record("funded_existing_ternary",stars,stars,"positive ternary denominator")
            if m<=4:
                q=examined(stars)
                if not q["nonlocal_ternary"] and not q["nonlocal_wide_triples"]:
                    record("funded_all_triples",stars,stars,"all triples including wider holders")
            if grown is None or largest(grown)>9:continue
            row["forward_width_at_most_nine"]+=1
            if all(len(s)>=3 for s in grown):
                assert lawful(grown,"nae")
                summary=examined(grown)
                next_step=ordinary.step(ordinary.from_stars(grown),"nae").status
                assert next_step=="extend" or next_step=="stall"
                conditions={"all_triples": not(summary["nonlocal_ternary"] or summary["nonlocal_wide_triples"]),
                            "existing_ternary":summary["ternary"]>0 and not summary["nonlocal_ternary"],
                            "empty_ternary":summary["ternary"]==0}
                for k,valid in conditions.items():
                    if valid:
                        record("reached_"+k,grown,stars,k)
                        if next_step=="extend":record("refunded_"+k,grown,stars,k)
        counts.append(dict(input_width=m,**row))
        needed={"reached_"+s for s in ("all_triples","existing_ternary","empty_ternary")}
        if m>=7 and needed<=minima.keys() and all(minima[k]["width"]<=m+1 for k in needed) and "funded_existing_ternary" in minima:
            break
    for row in minima.values():
        row["checks"]=examined(row["target"],"nae",True)
        row["next_status"]=ordinary.step(ordinary.from_stars(row["target"]),"nae").status
    return dict(exhausted=counts,minima=minima)


def gate_types():
    result={}
    for law in ("nae","parity"):
        for n in range(3,9):
            names=[f"a{i}" for i in range(n)]
            excluded=(0,(1<<n)-1) if law=="nae" else [w for w in range(1<<n) if w.bit_count()%2]
            cnf=";".join(" ".join(("~" if w>>i&1 else "")+v for i,v in enumerate(names)) for w in excluded)
            cmd=[sys.executable,"-B","-m","knotlab","check","--cnf",cnf,"--loops",*names[:-1],
                 "--contact",names[-1],"--json"]
            gate=json.loads(subprocess.check_output(cmd,cwd=ROOT,env={**os.environ,"PYTHONPATH":str(ROOT/"tools")}))
            assert gate["is_knot"]
            result[f"{law}_{n}"]={k:gate[k] for k in ("binding","loss_on_erasure","coexistence","is_knot")}
    return result


def run():
    return dict(core=core_cases(),protocols=branch_readings(),all_ternary=all_ternary_census(),
                named_growth=growth_fixtures(),width_search=new_minima(),wider_model=wider_model(),gate_types=gate_types(),
                three_holder_proof=three_holder_proof())


if __name__=="__main__":
    parts=dict(core=core_cases,protocols=branch_readings,all_ternary=all_ternary_census,
               named_growth=growth_fixtures,width_search=new_minima,wider_model=wider_model,gate_types=gate_types,
               three_holder_proof=three_holder_proof)
    if len(sys.argv)==1: d=run()
    else:
        d=json.loads(OUT.read_text()) if OUT.is_file() else {}
        for key in sys.argv[1:]:d[key]=parts[key]()
    OUT.write_text(json.dumps(d,indent=1)+"\n")
