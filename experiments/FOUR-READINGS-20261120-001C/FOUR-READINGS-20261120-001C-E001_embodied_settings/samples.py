"""Use the predecessor's literal reader placement, growth and exact counters."""
from collections import Counter
from fractions import Fraction
import gzip
import json
from itertools import product
from random import Random
import sys

from observables import HERE, ROOT, OUTPUT, PRIOR, freeze, put, measure, prior_score_check
sys.path.insert(0,str(PRIOR))
import run as prior


def sources():
    for source in prior.sources(False):
        if source.group=="archive" or source.name=="two_disjoint":
            yield source
    rng=Random(2026112003)
    for n,rep in product((4,5,6),range(4)):
        word=tuple(rng.randrange(n) for _ in range(n-2))
        meetings=prior.decode_prufer(word)
        sizes=tuple(prior.J.bare_sizes(n,meetings))
        for name,arity in (("bare",sizes),("extra",(sizes[0]+1,*sizes[1:]))):
            yield prior.Source(f"tree_{n}_{rep}_{name}",name,arity,meetings,
                               {"word":word,"size":n,"draw":rep,"possible_words":n**(n-2)})
    # A genuine repeated meeting; two old supports share two unmarked distinctions.
    yield prior.Source("two_unmarked_in_common","built",(5,5),((0,1),(0,1)),
                       {"method":"two independent shared distinctions and three private per reader"})


def extra_source():
    metadata = json.loads((HERE / "stress_addendum.json").read_text())
    import hashlib
    receipt = ROOT / "research" / HERE.parent.name / "stress_addendum.md"
    assert hashlib.sha256(receipt.read_bytes()).hexdigest() == metadata["preregistration_sha256"]
    archived=json.loads(prior.ARCHIVE.read_text())["named_archive_starts"]["start-03"]
    assert archived["identifier"]=="cap-7-06/163" and len(archived["sizes"])==6
    source=prior.Source("archive_03","prospective_jump",tuple(archived["sizes"]),
                        tuple(map(tuple,archived["meetings"])),
                        {"literal":archived["identifier"],"prior_parity_births":archived["round_junction_counts"],
                         "late_evidence":"386 to 28,065 births, steps seven and eight"})
    assert source.supports==tuple(map(tuple,archived["gate"]["literal_supports"]))
    literal=json.dumps(source.supports,separators=(",",":")).encode()
    assert hashlib.sha256(literal).hexdigest()==metadata["literal_supports_sha256"]
    return source


def study_source(source):
    old=source.supports
    old_n=1+max(map(max,old))
    record={"name":source.name,"group":source.group,"provenance":source.provenance,"old":old,"laws":{}}
    for law in ("nae","parity"):
        cert=prior.certify(old,law)
        assert all(r["eligible"] for r in cert)
        growth_status,growth,grown=prior.grow_once(old,law)
        res=[]
        record["laws"][law]={"growth_status":growth_status,"growth":growth,"stages":res}
        for age,pres in ((0,old),(1,grown)):
            if pres is None:
                res.append({"age":age,"status":growth_status})
                continue
            certificates = prior.certify(pres,law) if age else cert
            marks=prior.choose_placements(pres,certificates,old_n,3,source.fixed_marks(3))
            counter=prior.CountStage(old,pres,law)
            total=counter.histogram((),"U")[0][0]
            row={"age":age,"status":"measured","supports":pres,"gates":certificates,"complete_states":total,**marks}
            res.append(row)
            for slot in marks["slots"]:
                p=slot["placement"]
                if p is None:
                    continue
                hist=counter.histogram(tuple(p["alice"]+p["bob"]),"U")[0]
                assert sum(hist)==total
                d={"embodied":measure(hist),"external":measure(hist,False)}
                assert prior_score_check(hist,d)
                if law=="nae":
                    assert hist==hist[::-1] and Fraction(d["embodied"]["II"]["maximum"])<=2
                for name in ("I","II"):
                    assert Fraction(d["external"][name]["maximum"])<=2
                slot.update({"histogram":hist,**d})
    return record


def summarize(records):
    outs={}
    for record in records:
        for law, info in record["laws"].items():
            for stage in info["stages"]:
                key=(record["group"],law,stage["age"])
                if key not in outs:
                    outs[key]={"sources":0,"measured_stages":0,"eligible_sources":0,"placements":0,
                               "eligible_mark_options":0,"full_register_pass":0,"I_over2_hidden":0,
                               "II_over2_hidden":0,"sources_I_over2_hidden":0,"peaks":{},"band_origins":{}}
                o=outs[key]; o["sources"]+=1
                if stage["status"]!="measured":
                    continue
                o["measured_stages"]+=1
                yes=False; win=False
                for slot in stage["slots"]:
                    band=slot["band"]+"_"+slot["origin"]
                    counter=o["band_origins"].setdefault(band,{"seen":0,"all_options":0})
                    counter["all_options"]+=slot["eligible"]
                    if slot["placement"] is None:
                        continue
                    counter["seen"]+=1
                    yes=True;o["placements"]+=1;o["eligible_mark_options"]+=slot["eligible"]
                    body=slot["embodied"]
                    if body["full_hidden"] is None:
                        continue
                    hidden=body["full_hidden"]
                    o["full_register_pass"]+=int(hidden)
                    for read in ("I","II"):
                        if hidden and Fraction(body[read]["maximum"])>2:
                            o[read+"_over2_hidden"]+=1
                            if read=="I": win=True
                        for arm,obs in (("all",body),("external",slot["external"]),("hidden",body)):
                            if arm=="hidden" and not hidden:
                                continue
                            f=Fraction(obs[read]["maximum"]); level=arm+"_"+read
                            if level not in o["peaks"] or f>Fraction(o["peaks"][level]["score"]):
                                o["peaks"][level]={"score":str(f),"name":record["name"],"band":band,"ties":1}
                            elif f==Fraction(o["peaks"][level]["score"]):
                                o["peaks"][level]["ties"]+=1
                o["eligible_sources"]+=int(yes)
                o["sources_I_over2_hidden"]+=int(win)
    return [{"group":g,"law":law,"age":age,**value} for (g,law,age),value in sorted(outs.items())]


def main():
    freeze()
    extra="--extra" in sys.argv
    records=[study_source(s) for s in ([extra_source()] if extra else sources())]
    suffix="stress" if extra else "sample"
    put(suffix+"_summary.json",summarize(records))
    (OUTPUT/(suffix+"_tables.json.gz")).write_bytes(gzip.compress(json.dumps(records,separators=(",",":")).encode(),mtime=0))
    print("sources",len(records),"stages",sum(len(v["stages"]) for r in records for v in r["laws"].values()))
if __name__=="__main__":
    main()
