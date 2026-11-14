#!/usr/bin/env python3
"""Independent WEIGHTS audit; only permitted data and earlier referee imports.

Run with the repository .venv Python -B. No multiprocessing, network, producer
imports or writes outside this directory. Glucose4 builds explicit witnesses;
the earlier referees' CaDiCaL check separately verifies each final forcing.
"""
import argparse
import itertools as it
import json
import os
from pathlib import Path
import resource
import signal
import sys
import time

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"
resource.setrlimit(resource.RLIMIT_AS, (5 * 1024**3, 5 * 1024**3))
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "research/SHIFT-COUNT-20261112-001/referee-R1"))
import ref_shiftcount as S
RF = S.RF
from pysat.solvers import Glucose4

DATA = ROOT / "artifacts/WEIGHTS-20261112-001A/WEIGHTS-20261112-001A-E001_two_shifts"


def load_rows():
    rows = {}
    for line in (DATA / "census.jsonl").read_text().splitlines():
        x = json.loads(line)
        if "by r" in x:
            key = (x["beta"], x["sample"])
            assert key not in rows
            rows[key] = (x, "before pause")
    for line in (DATA / "resume_census/results.jsonl").read_text().splitlines():
        wrapper = json.loads(line)
        if wrapper["status"] == "ok":
            x = wrapper["result"]
            key = (x["beta"], x["sample"])
            assert key not in rows
            rows[key] = (x, "resumed")
    return rows


def clean_fix(fix):
    out = {}
    for c, v in fix:
        c = tuple(c)
        if c in out and out[c] != v:
            return None
        out[c] = v
    return sorted(out.items())


def bit_model(solver, idx):
    model = set(solver.get_model())
    return "".join("1" if v in model else "0" for v in idx.values())


def verify_torus(K, fix, w):
    P, shift, Q = w["P"], w["shift"], w["Q"]
    bits = w["bits"]
    if not all(type(x)is int for x in (P,shift,Q)) or P<1 or Q<1:
        return False
    if len(bits) != P * Q or set(bits)-{"0","1"}:
        return False
    def val(c):
        k, x = divmod(c[0], P)
        y = (c[1] - k * shift) % Q
        return int(bits[x * Q + y])
    if any(val(c) != v for c, v in fix):
        return False
    return all(len({val((x+a, y+b)) for a, b in kind}) == 2
               for x in range(P) for y in range(Q) for kind in K)


def torus(K, fix, P, shift, Q):
    fix = clean_fix(fix)
    if fix is None:
        return None
    def red(c):
        k, x = divmod(c[0], P)
        return x, (c[1] - k * shift) % Q
    idx = {(x,y): x * Q + y + 1 for x in range(P) for y in range(Q)}
    cl = []
    for x,y in idx:
        for kind in K:
            vs = [idx[red((x+a, y+b))] for a,b in kind]
            cl.extend((vs, [-v for v in vs]))
    ass = [idx[red(c)] if v else -idx[red(c)] for c,v in fix]
    with Glucose4(bootstrap_with=cl) as so:
        if not so.solve(assumptions=ass):
            return None
        out = {"type":"torus", "P":P, "shift":shift, "Q":Q,
               "bits":bit_model(so,idx)}
    assert verify_torus(K, fix, out)
    return out


def fold(x, lo, hi, period):
    if x < lo:
        return lo - period + (x - lo) % period
    if x >= hi:
        return hi + (x - hi) % period
    return x


def eventual_setup(K, fix, direction, P, Q, bounds=None):
    u, co = S.frame(direction)
    fk = [[co(c) for c in kind] for kind in K]
    fc = [(co(c),v) for c,v in fix]
    if bounds is None:
        a0 = min(c[0] for c,v in fc)-1
        a1 = max(c[0] for c,v in fc)+2
        b0 = min(c[1] for c,v in fc)-1
        b1 = max(c[1] for c,v in fc)+2
    else:
        a0,a1,b0,b1 = bounds
    sa = max(max(c[0] for c in k)-min(c[0] for c in k) for k in fk)
    sb = max(max(c[1] for c in k)-min(c[1] for c in k) for k in fk)
    # Outside these anchor ranges every translated kind lies wholly in one
    # periodic tail, so subtraction/addition of periods moves it into range.
    amin = min(c[0] for k in fk for c in k)
    amax = max(c[0] for k in fk for c in k)
    bmin = min(c[1] for k in fk for c in k)
    bmax = max(c[1] for k in fk for c in k)
    ar = range(a0-amax-P, a1-amin+P)
    br = range(b0-bmax-Q, b1-bmin+Q)
    return u,co,fk,fc,(a0,a1,b0,b1),(sa,sb),ar,br


def verify_eventual(K, fix, w):
    P,Q = w["P"],w["Q"]
    if not all(type(x)is int and x>0 for x in (P,Q)):
        return False
    bounds=w["bounds"]
    if len(bounds)!=4 or not all(type(x)is int for x in bounds):
        return False
    if bounds[0]>=bounds[1] or bounds[2]>=bounds[3]:
        return False
    if set(w["bits"])-{"0","1"}:
        return False
    u,co,fk,fc,bb,spans,ar,br = eventual_setup(K,fix,tuple(w["frame"]),P,Q,w["bounds"])
    if list(u) != w["u"]:
        return False
    a0,a1,b0,b1 = bb
    lowa,hia = a0-2*P,a1+2*P
    lowb,hib = b0-2*Q,b1+2*Q
    bits = w["bits"]
    if len(bits) != (hia-lowa)*(hib-lowb):
        return False
    def raw(a,b):
        return int(bits[(a-lowa)*(hib-lowb)+b-lowb])
    def val(a,b):
        return raw(fold(a,a0,a1,P),fold(b,b0,b1,Q))
    if any(val(*c)!=v for c,v in fc):
        return False
    # Check equalities on *all* rows/columns, including the four corners.
    for a in range(lowa,hia):
        for b in range(lowb,hib):
            if raw(a,b)!=val(a,b):
                return False
    for a in ar:
        for b in br:
            for k in fk:
                if len({val(a+x,b+y) for x,y in k}) != 2:
                    return False
    return True


def eventual(K, fix, direction, P, Q, exact_cover=True):
    fix = clean_fix(fix)
    if fix is None:
        return None
    u,co,fk,fc,bb,spans,ar,br = eventual_setup(K,fix,direction,P,Q)
    a0,a1,b0,b1 = bb
    idx = {(a,b):i+1 for i,(a,b) in enumerate(it.product(range(a0-2*P,a1+2*P),range(b0-2*Q,b1+2*Q)))}
    cl = []
    for a,b in idx:
        for kind in fk:
            pts=[(a+x,b+y) for x,y in kind]
            if all(c in idx for c in pts):
                vs=[idx[c] for c in pts]
                cl.extend((vs,[-v for v in vs]))
        if a0-2*P <= a < a0-P or a1 <= a < a1+P:
            v,w=idx[a,b],idx[a+P,b]
            cl.extend(([-v,w],[v,-w]))
        if b0-2*Q <= b < b0-Q or b1 <= b < b1+Q:
            v,w=idx[a,b],idx[a,b+Q]
            cl.extend(([-v,w],[v,-w]))
    # For small periods the two-copy sufficient span condition need not hold.
    # Fold every infinite constraint representative explicitly as well. This
    # independently prevents any omitted seam or long-kind constraint.
    if exact_cover:
        for a in ar:
            for b in br:
                for kind in fk:
                    vs=[idx[fold(a+x,a0,a1,P),fold(b+y,b0,b1,Q)] for x,y in kind]
                    cl.extend((vs,[-v for v in vs]))
    ass=[idx[c] if v else -idx[c] for c,v in fc]
    with Glucose4(bootstrap_with=cl) as so:
        if not so.solve(assumptions=ass):
            return None
        out={"type":"four-tail", "frame":list(direction), "u":list(u),
             "P":P,"Q":Q,"bounds":list(bb),"kind_spans":list(spans),
             "span_sufficient":P>=spans[0] and Q>=spans[1],
             "exact_folded_coverage":exact_cover,"bits":bit_model(so,idx),
             "variables":len(idx),"clauses":len(cl),
             "representative_anchors":len(ar)*len(br)}
    out["infinite_extension_verified"]=verify_eventual(K,fix,out)
    if not out["infinite_extension_verified"]:
        return None
    return out


def verify(K, fix, w):
    if w["type"]=="torus":
        return verify_torus(K,fix,w)
    return verify_eventual(K,fix,w)


def carry(K,fix,d):
    for P,shift,Q in RF.TORI:
        w=torus(K,fix,P,shift,Q)
        if w:
            return w
    for dd in dict.fromkeys((tuple(d),(1,0),(0,1))):
        _,co=S.frame(dd)
        fk=[[co(c) for c in kind]for kind in K]
        sa=max(max(c[0]for c in kind)-min(c[0]for c in kind)for kind in fk)
        sb=max(max(c[1]for c in kind)-min(c[1]for c in kind)for kind in fk)
        periods=[(P,Q)for P,Q in S.PERIODS if P>=sa and Q>=sb]
        for pq in it.product(sorted({max(1,sa),sa+1,sa+2,sa+3,sa+4,2*sa}),
                             sorted({max(1,sb),sb+1,sb+2,sb+3,sb+4,sb+5,sb+6,2*sb})):
            if pq not in periods:
                periods.append(pq)
        for P,Q in periods:
            if P<1 or Q<1:
                continue
            w=eventual(K,fix,dd,P,Q)
            if w:
                return w
    return None


class ForceWindow:
    def __init__(self,K):
        self.idx,cl=RF.window_clauses(K,(-30,30,-30,30))
        self.solver=Glucose4(bootstrap_with=cl)
    def forced(self,A,p,t,sigma):
        idx=self.idx
        ass=[idx[tuple(c)] if v else -idx[tuple(c)] for c,v in zip(A,p)]
        if not self.solver.solve(assumptions=ass):
            return False
        for c,v in zip(A,p):
            target=(c[0]+t[0],c[1]+t[1])
            if target not in idx:
                return False
            want=v^sigma
            if self.solver.solve(assumptions=ass+[-idx[target] if want else idx[target]]):
                return False
        return True
    def close(self):
        self.solver.delete()


def fixed_direction(K,d,cert,fw=None,reported_periods=None):
    A=[tuple(c)for c in cert["A"]]
    p=cert["p"]
    k=cert["k"]
    sigma=cert["sigma"]
    t=(k*d[0],k*d[1])
    own=fw is None
    fw=fw or ForceWindow(K)
    try:
        forced=[fw.forced(A,p,t,s)for s in (0,1)]
    finally:
        if own: fw.close()
    inherited=S.window_forces(K,A,p,t,sigma)
    assert inherited==forced[sigma]
    fix=list(zip(A,p))+[((c[0]+t[0],c[1]+t[1]),v^sigma)for c,v in zip(A,p)]
    attempts=[]
    image=None
    if reported_periods:
        P,Q=reported_periods
        for dd in dict.fromkeys((tuple(d),(1,0),(0,1))):
            w=eventual(K,fix,dd,P,Q)
            attempts.append({"frame":list(dd),"P":P,"Q":Q,"sat":bool(w)})
            if w:
                image=w
                break
    if image is None:
        image=carry(K,fix,d)
    free=[]
    for tail in it.product((0,1),repeat=len(A)-1):
        q=(0,)+tail
        qfix=list(zip(A,q))
        w=image if image and all(v==pv for (_,v),pv in zip(qfix,p)) else carry(K,qfix,d)
        free.append({"pattern":list(q),"witness":w})
    image_valid=bool(image) and verify(K,fix,image)
    free_valid=all(e["witness"] and verify(K,list(zip(A,e["pattern"])),e["witness"])for e in free)
    okay=forced[sigma] and inherited and image_valid and free_valid
    return {"direction":list(d),"A":[list(c)for c in A],"p":list(p),"k":k,"sigma":sigma,
            "forced_by_polarity":forced,"referee_forcing_agrees":inherited==forced[sigma],
            "reported_period_attempts":attempts,"image_witness":image,"free_patterns":free,
            "complement_symmetry_covers_other_half":True,"certified":bool(okay)}


def completion():
    rows=load_rows()
    claims=json.loads((ROOT/"research/WEIGHTS-20261112-001/completion.json").read_text())
    out=[]
    for e in claims:
        start=time.monotonic()
        beta,i,r=e["beta"],e["sample"],e["r"]
        x,source=rows[beta,i]
        b=x["by r"][r]
        c=e["detail"]
        cert={k:c[k]for k in ("A","p","k")}
        # The JSON omits polarity: check both; the true one is then recorded.
        cert["sigma"]=1
        check=fixed_direction(b["kinds"],tuple(c["direction"]),cert,
                              reported_periods=(c["certificate"]["P"],c["certificate"]["Q"]))
        d=c["direction"]
        independent=any(a*d[1]-bb*d[0] for a,bb in b["main"]["certified directions"])
        main_d=min((tuple(dd)for dd in b["main"]["certified directions"]
                    if dd[0]*d[1]-dd[1]*d[0]),key=lambda dd:(max(map(abs,dd)),sum(map(abs,dd)),dd))
        fw=ForceWindow(b["kinds"])
        try:
            main_check=search_direction(b["kinds"],main_d,fw)
        finally:
            fw.close()
        res={"beta":beta,"sample":i,"r":int(r),"source":source,"kinds":b["kinds"],
             "independent_of_main":independent,"check":check,"main_direction_check":main_check,
             "both_directions_independently_certified":check["certified"] and main_check["certified"],
             "seconds":time.monotonic()-start}
        out.append(res)
        print(beta,i,r,"certified",check["certified"],"period attempts",check["reported_period_attempts"],
              "seconds",round(res["seconds"],2),flush=True)
        (HERE/"completion_checks.json").write_text(json.dumps(out,indent=2)+"\n")
    return out


def search_direction(K,d,fw):
    box=[(x,y)for x in range(3)for y in range(3)]
    attempts=0
    for size in (2,3,4):
        for tailcells in it.combinations(box[1:],size-1):
            A=[(0,0)]+list(tailcells)
            free_failed=False
            for tail in it.product((0,1),repeat=size-1):
                if free_failed: break
                p=(0,)+tail
                for k in range(1,5):
                    if free_failed: break
                    t=(k*d[0],k*d[1])
                    for sigma in (0,1):
                        attempts+=1
                        if not fw.forced(A,p,t,sigma):
                            continue
                        checked=fixed_direction(K,d,{"A":A,"p":p,"k":k,"sigma":sigma},fw=fw)
                        if checked["certified"]:
                            checked["search_candidates"]=attempts
                            return checked
                        if any(not q["witness"]for q in checked["free_patterns"]):
                            free_failed=True
                            break
    return {"direction":list(d),"certified":False,"search_candidates":attempts}


# Fixed coverage, selected before recomputation: three beta0 originals;
# three beta1 originals (including old box), one beta1 resumed; three beta2
# resumed, both strata. Beta0 has no resumed main rank-two base.
PICKS=[(0,4,5),(0,33,4),(0,35,4),(1,4,4),(1,7,5),(1,14,4),
       (1,50,4),(2,0,3),(2,1,3),(2,6,4)]


def spots():
    rows=load_rows()
    out=[]
    for beta,i,r in PICKS:
        start=time.monotonic()
        x,source=rows[beta,i]
        b=x["by r"][str(r)]
        K=b["kinds"]
        dirs=sorted(map(tuple,b["main"]["certified directions"]),key=lambda d:(max(map(abs,d)),sum(map(abs,d)),d))
        d1=dirs[0]
        d2=next(d for d in dirs if d[0]*d1[1]-d[1]*d1[0])
        reading=RF.read(K)
        reading["class"]=RF.classify(reading)
        fw=ForceWindow(K)
        try:
            checks=[search_direction(K,d,fw)for d in (d1,d2)]
        finally:
            fw.close()
        res={"beta":beta,"sample":i,"r":r,"source":source,"stratum":b["stratum"],
             "kinds":K,"recorded_class":b["class"],"referee_reading":reading,"checks":checks,
             "agrees":reading["class"]==b["class"] and all(c["certified"]for c in checks),
             "seconds":time.monotonic()-start}
        out.append(res)
        print(beta,i,r,source,b["stratum"],"class",reading["class"],"directions",d1,d2,
              "agree",res["agrees"],"seconds",round(res["seconds"],2),flush=True)
        (HERE/"spot_checks.json").write_text(json.dumps(out,indent=2)+"\n")
    return out


def replay_and_controls():
    checked=0
    results=[]
    for name in ("completion_checks.json","spot_checks.json"):
        rows=json.loads((HERE/name).read_text())
        for row in rows:
            K=row["kinds"]
            checks=row.get("checks",[row.get("check")])
            if "main_direction_check"in row:
                checks=checks+[row["main_direction_check"]]
            for c in checks:
                A=list(map(tuple,c["A"]))
                p=c["p"];d=c["direction"];k=c["k"];sigma=c["sigma"]
                fix=list(zip(A,p))+[((x+k*d[0],y+k*d[1]),v^sigma)for (x,y),v in zip(A,p)]
                result=verify(K,fix,c["image_witness"])
                results.append(result)
                assert result
                checked+=1
                for q in c["free_patterns"]:
                    result=verify(K,list(zip(A,q["pattern"])),q["witness"])
                    results.append(result)
                    assert result
                    checked+=1
    first=json.loads((HERE/"completion_checks.json").read_text())[0]
    c=first["check"]; K=first["kinds"]
    A=list(map(tuple,c["A"]));p=c["p"]
    w=dict(c["image_witness"])
    # Contradict a required pattern bit: must reject the same valid model.
    bad=list(zip(A,p));bad[0]=(bad[0][0],1-bad[0][1])
    controls={"wrong_required_pattern_rejected":not verify(K,bad,w),
              "wrong_polarity_rejected":not c["forced_by_polarity"][1-c["sigma"]]}
    simple=[[(0,0),(1,0),(0,1)]]
    assert torus(simple,[((0,0),0)],2,0,2)
    controls["monochromatic_kind_rejected"]=carry(simple,[((0,0),0),((1,0),0),((0,1),0)],(1,0)) is None
    malformed={"type":"four-tail","frame":[1,0],"u":[0,1],"P":1,"Q":1,
               "bounds":[4,-4,4,-4],"bits":"0"*16}
    controls["reversed_bounds_rejected"]=not verify_eventual(simple,[((0,0),0)],malformed)
    malformed_bits=dict(w,bits="2"+w["bits"][1:])
    controls["nonbinary_model_rejected"]=not verify(K,list(zip(A,p)),malformed_bits)
    zero_period=dict(w,P=0)
    controls["zero_period_rejected"]=not verify(K,list(zip(A,p)),zero_period)
    fw=ForceWindow(simple)
    try:
        controls["unforced_singleton_rejected"]=not fw.forced([(0,0)],[0],(1,0),0)
    finally:
        fw.close()
    out={"witnesses_replayed":checked,"all_valid":all(results),"controls":controls,
         "all_controls_reject":all(controls.values())}
    assert out["all_controls_reject"]
    (HERE/"validation_checks.json").write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out),flush=True)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("part",choices=("completion","spots","replay"))
    args=parser.parse_args()
    started=time.monotonic()
    # A command is deliberately bounded below the user's 15-minute ceiling.
    signal.alarm(840)
    if args.part=="completion": completion()
    elif args.part=="spots": spots()
    else: replay_and_controls()
    metrics_path=HERE/"run_metrics.json"
    metrics=json.loads(metrics_path.read_text()) if metrics_path.exists() else {}
    usage=resource.getrusage(resource.RUSAGE_SELF)
    metrics[args.part]={"seconds":time.monotonic()-started,"peak_rss_mib":usage.ru_maxrss/1024,
                        "user_cpu_seconds":usage.ru_utime,"system_cpu_seconds":usage.ru_stime,
                        "processes":1,"memory_limit_gib":5,"command_limit_seconds":840}
    metrics_path.write_text(json.dumps(metrics,indent=2)+"\n")
