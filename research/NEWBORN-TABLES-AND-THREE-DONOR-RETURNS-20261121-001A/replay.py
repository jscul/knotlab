"""Reconstruct all joint answers and independently verify the physical port ledger."""
import argparse
from collections import Counter
from fractions import Fraction as F
import gzip
import hashlib
from itertools import combinations, permutations, product
import json
from math import comb, prod
from pathlib import Path

import numpy as np

from answers import (BITS, BOUND, DETERMINISTIC, INDEX, LISTS, all_physical_words,
                     certify, gram_from_vectors, inequality, joint, sign_score,
                     symmetric_weights)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREVIOUS = "SPENT-PASTS-AND-TWO-SHARED-NAMES-20261121-001A"
STAGE_DATA = ROOT/"research"/PREVIOUS/"stage_observations.json.gz"
SOURCE_DATA = next((ROOT/"artifacts/FREEDOM-CLOCKS-AND-BIRTHS-20261120-001A").glob("*/histories.json.gz"))
TURN = next((ROOT/"experiments/ORDINARY-DYNAMICS-20261120-001A").glob("*/end_operator.py"))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def as_json(record):
    return json.dumps(record,sort_keys=True,indent=2,default=str,allow_nan=False).encode()+b"\n"


def certificate_of(gram):
    rows = joint(gram)
    cert = certify(rows)
    return {"gram":gram,"denominator":sum(gram[i][i] for i in range(8)),
            "settings":rows,"M_minus":sign_score(rows),"M_with_plus":sign_score(rows,True),
            "ordinary_mixed":sum(rows[0][1:7]),"all_change_plus":rows[7][0],
            "at_most_one_negative_change":sum(rows[7][x] for x in (0,1,2,4)),
            "certificate":cert}


def legal(word,law):
    return sum(word)%2 == 0 if law=="parity" else len(set(word))==2


def conditioned_stars(width, law):
    """Group unread loose sibling words by the old values they allow.

    Multiplicities count literal fresh words. Keep the original source's whole allowed
    bit patterns and Fourier-transform only their indicator, with all character branches.
    """
    fresh = width-1
    siblings = Counter(tuple(legal((old,*end),law) for old in (0,1))
                       for end in product((0,1),repeat=fresh))
    old = [x for x in product((0,1),repeat=width) if legal(x,law)]
    signs = np.array([[(-1)**sum(j*k for j,k in zip(h,x)) for x in old]
                      for h in product((0,1),repeat=width)],dtype='int64')
    ports = np.zeros((1<<width,8,8),dtype='int64')
    ordinary = np.zeros((8,8),dtype='int64')
    orient = np.zeros((2,8,8),dtype='int64')
    sources = np.array(old,dtype='int64')
    for factors in product(siblings,repeat=width-1):
        scale = prod(siblings[f] for f in factors)
        permits = np.array([all(f[b] for f,b in zip(factors,x[1:])) for x in old],dtype='int64')
        for other in product((0,1),repeat=fresh-3):
            blocks = np.array([[legal((x[0],*observed,*other),law) for observed in BITS] for x in old],
                              dtype='int64')*permits[:,None]
            ordinary += scale*(blocks.T @ blocks)
            for value in (0,1):
                c = blocks[sources[:,0]==value]
                orient[value] += scale*(c.T @ c)
            changed = signs @ blocks
            ports += scale*changed[:,:,None]*changed[:,None,:]
    assert np.array_equal(ports.sum(axis=0),len(ports)*ordinary)
    assert np.array_equal(orient.sum(axis=0),ordinary)
    return ordinary.tolist(),ports.tolist(),orient.tolist()


def conditioned_bound(value):
    # If Xi=-, the two other Z must both be 'value'.
    coeff = []
    for s in range(8):
        block=[]
        for a in range(8):
            wrong = (a & (7^s)) != ((7^s) if value else 0)
            block.append(int(s==7 and a.bit_count()>=2)-int(s==0 and a==7*value)
                         -int(s.bit_count()==1 and a&s !=0 and wrong))
        coeff.append(block)
    return coeff


def four_place_exterior(law, n, w):
    """Actually project the nine other loose names at the first reached stage."""
    rows = {}
    gkeep = {}
    gclean = {}
    for orientation in (0,1):
        ex = (orientation,)*3
        old = [word for word in product((0,1),repeat=4) if legal(word,law)
               and all(legal((s,*ex),law) for s in word[1:])]
        vectors = [[int(legal((s[0],*x),law)) for x in BITS] for s in old]
        d = gram_from_vectors((1,v) for v in vectors)
        f = [sum(v[i] for v in vectors) for i in range(8)]
        q = gram_from_vectors([(1,f)])
        gkeep[orientation] = d
        gclean[orientation] = q
        item = {"values_of_the_nine_unread_fresh":str(orientation)*9,"compatible_past_words":old,
                "retained_exterior_probability":F(sum(d[i][i] for i in range(8)),n),
                "exterior_probability_given_clean":F(sum(q[i][i] for i in range(8)),w),
                "joint_clean_and_exterior_launch":F(sum(q[i][i] for i in range(8)),16*n),
                "retained_table":certificate_of(d),"clean_table":certificate_of(q)}
        if law=="nae":
            for g in (d,q):
                b=inequality(conditioned_bound(orientation),joint(g))
                assert b["gap"]==F(1,14)
            item["simple_separator"]=b
        rows[str(orientation)] = item
    for lab,pair in (("retained",gkeep),("clean",gclean)):
        add=[[pair[0][i][j]+pair[1][i][j] for j in range(8)] for i in range(8)]
        packet=certificate_of(add)
        assert packet["certificate"]["type"]=="common"
        rows["accept_both_orientations_without_identifying_them_"+lab]=packet
    return rows


def archived_tables(d):
    inventory = {}
    for law in ("nae","parity"):
        count = Counter()
        sources = {}
        for key,both in d["structural_inventory"].items():
            source = both[law]
            if source["source_mode"]=="built":
                continue
            count["sources"] += 1
            age = source["inventory_for_all_age_slots"][1]
            if not age["reached"]:
                count["stage_absent"] += 1
                sources[key]={"status":age["status"]}
                continue
            count["funded"] += 1
            choices=age["all_single_holder_three_loose_choices"]
            count["sources_with_eligible_newborn"] += int(bool(choices))
            count["eligible_knots"] += len(choices)
            count["eligible_triples"] += sum(comb(len(x["once_held_names_in_holder"]),3) for x in choices)
            entry={"status":"funded","placements":{}}
            if choices:
                data=d["quantitative_panel"][key][law]["bounded_numerical_stages"]["1"]
                whole=data["whole_current_weights"]
                entry["N"]=whole["N_complete_words"]
                entry["W"]=whole["W_sum_squared_past_counts"]
                entry["clean_launch"]=whole["all_plus_erasure_probability"]
                for found, table in zip(choices,data["single_holder_results"],strict=True):
                    assert found["holder_first_exists_after_source"]
                    assert found["holder"]==table["holder"]
                    u=found["once_held_names_in_holder"]
                    rec={"fresh":u,"all_three_subsets":list(combinations(u,3)),"readings":{}}
                    for mode in ("unread_past_D","pure_squared_count"):
                        reading=table["read"][mode]
                        if reading["status"]=="exact":
                            gram=reading["integer_matrix"]
                            q=certificate_of(gram)
                            comparison(q["settings"],reading["settings_and_scores"]["every_joint_probability"])
                            assert q["certificate"]["type"]=="common"
                            rec["readings"][mode]=q
                        else:
                            rec["readings"][mode]={"status":reading["status"],
                               "execution":reading["execution"],"common":"proved by the general newborn theorem",
                               "specific_numeric_weights":None}
                    entry["placements"][str(found["holder"])]=rec
            sources[key]=entry
        inventory[law]={"counts":dict(count),"sources":sources}
    return inventory


def comparison(rows, archival):
    # The older buffers address the first reader by the least-significant output bit.
    for s,q in zip(BITS,rows):
        item=archival["".join("X" if t else "Z" for t in s)]
        values=tuple(F(v,item["denominator"]) for v in item["numerators"])
        assert tuple(values[INDEX[o[::-1]]] for o in BITS)==q


def old_controls():
    targets={"isolated_three":(((0,1,2),),(0,1,2)),
             "central_three_with_two_attachments":(((0,1,2),(0,3,4),(1,5,6)),(0,1,2)),
             "original_four_place_subset":(((0,1,2,3),),(0,1,2)),
             "three_distinct_first_children":(((0,1,2),(0,3,4),(1,5,6),(2,7,8)),(3,5,7))}
    result={}
    for name,(held,marks) in targets.items():
        result[name]={}
        for law in ("nae","parity"):
            d,q=all_physical_words(held,law,marks)
            packet={"retained":certificate_of(d)}
            if q:
                packet["clean"]=certificate_of(q)
            packet["holdings"]=held
            packet["address"]=marks
            result[name][law]=packet
    for sign,bound in ((False,2),(True,4)):
        vals=[]
        for row in DETERMINISTIC:
            a = [(-1)**j.bit_count() for j in row]
            vals.append(a[7]+(1 if sign else -1)*sum(a[i] for i in (1,2,4)))
        assert max(vals)==bound and min(vals)==-bound
    return result


def symmetry_checks(rows, weights):
    """Check every transported assignment and all cells under the 48 local bit/label recodings."""
    weights=tuple(weights)
    for p in permutations(range(3)):
        for flips in BITS:
            w = {}
            for t,prob in zip(LISTS,weights):
                w[tuple(v for i in range(3) for v in (t[2*p[i]]^flips[i],t[2*p[i]+1]))] = prob
            for s,picks in enumerate(BITS):
                original=[0]*3
                for i,j in enumerate(p):
                    original[j]=picks[i]
                oldrow=rows[INDEX[tuple(original)]]
                check=[F(0)]*8
                for t,v in w.items():
                    if v:
                        check[INDEX[tuple(t[2*i+k] for i,k in enumerate(picks))]]+=v
                for o in BITS:
                    for i,j in enumerate(p):
                        original[j] = o[i]^((1-picks[i])*flips[i])
                    assert check[INDEX[o]]==oldrow[INDEX[tuple(original)]]


def symbolic_theorem():
    import sympy as sp
    a,b=sp.symbols('a b',real=True)
    left=sp.Matrix([a,*([1]*6),b]); right=sp.Matrix([b,*([1]*6),a])
    gram=(left*left.T+right*right.T)/2
    trace=6+a*a+b*b
    # w's and p's here are unnormalized; this keeps each identity polynomial.
    raw=[]
    for s in range(8):
        row=[]
        for o in range(8):
            col=sp.Matrix([int((z & (7^s))==(o & (7^s)))*(-1)**(z&o&s).bit_count()
                           for z in range(8)])
            row.append(sp.expand((col.T*gram*col)[0]/(1<<s.bit_count())))
        assert sp.expand(sum(row)-trace)==0
        raw.append(row)
    px=raw[7]
    m=sum(raw[0][1:7])
    assert sp.expand(m-6)==0 and sp.expand(px[0]-(6+a+b)**2/8)==0
    assert sp.expand(sum(px[t] for t in (1,2,4))-3*(a-b)**2/8)==0
    polynomials=[]
    for t in LISTS:
        z,x=t[::2],t[1::2]
        i=INDEX[x]
        w=(px[i]-(m if i==0 else 0))/2 if len(set(z))==1 else (m/6 if i==0 else 0)
        polynomials.append(sp.expand(w))
    rows=[[0]*8 for _ in range(8)]
    for weight,picks in zip(polynomials,DETERMINISTIC):
        for s,o in enumerate(picks):
            rows[s][o]+=weight
    assert all(sp.expand(rows[s][o]-raw[s][o])==0 for s in range(8) for o in range(8))
    rng=[]
    for ai,bi in ((F(1),F(0)),(F(1,2),F(1,2)),(F(1),F(1)),(F(4,5),F(0)),(F(2,5),F(2,5)),(F(0),F(0))):
        vv=[ai,*([F(1)]*6),bi]
        entry=certificate_of(gram_from_vectors([(1,vv),(1,vv[::-1])]))
        answer=entry["certificate"]["type"]=="common"
        assert answer==((6+ai+bi)**2+3*(ai-bi)**2>=48)
        rng.append({"a":ai,"b":bi,"newborn_outer_domain":ai+bi>=1,
                    "all_plus_only_construction":bool(symmetric_weights(entry["settings"],use_one=False)),
                    "table":entry})
    orbits=set()
    for t in LISTS:
        images=set()
        for p in permutations(range(3)):
            for flip in (0,1):
                images.add(tuple(v for j in p for v in (t[2*j]^flip,t[2*j+1])))
        orbits.add(tuple(sorted(images)))
    assert sum(map(len,orbits))==64
    return {"symbolic_raw_paired_table": [[str(sp.factor(o)) for o in r] for r in raw],
            "symbolic_raw_64_list_weights":list(map(lambda e:str(sp.factor(e)),polynomials)),
            "all_64_polynomial_residuals_zero":True,"raw_normalizer":str(trace),
            "list_orbits":[{"representative":o[0],"size":len(o),"stabilizer_size":12//len(o),
                            "all_lists_indices":[LISTS.index(t) for t in o]} for o in sorted(orbits)],
            "outer_and_off_domain_checks":rng,
            "sharp_inequality":BOUND}


def base_crosscheck():
    findings={}
    archive=json.loads(gzip.decompress(STAGE_DATA.read_bytes()))
    for width in (4,5):
        for law in ("parity","nae"):
            retained,ports,orient=conditioned_stars(width,law)
            n=sum(retained[i][i] for i in range(8))
            samples={}
            for label,g in [('retained',retained),('clean',ports[0])]:
                q=certificate_of(g)
                assert q["certificate"]["type"]=="common"
                symmetry_checks(q["settings"],q["certificate"]["weights"])
                samples[label]=q
            for value,g in enumerate(orient):
                q=certificate_of(g)
                q["parent_bit"]=value
                q["selection_probability"]=F(q["denominator"],n)
                if width==4 and law=="nae":
                    test=inequality(conditioned_bound(value),q["settings"])
                    assert test["gap"]==F(1,14)
                    q["simple_conditional_separator"]=test
                samples[f"retained_disclosed_paid_{value}"]=q
            signed={}
            for h,g in enumerate(ports):
                mass=sum(g[i][i] for i in range(8))
                prob=F(mass,n<<width)
                signed[format(h,f"0{width}b")]={"launch":prob,"table":certificate_of(g) if mass else None}
            assert sum(x["launch"] for x in signed.values())==1
            findings[f"{width}/{law}"]={"cases":samples,"character_ports":signed}
            if width==4:
                findings[f"{width}/{law}"]["actual_exterior_conditioning"] = four_place_exterior(
                    law,n,sum(ports[0][i][i] for i in range(8)))
                earlier=archive["built_histories"]["single4/1/0"][law]["bounded_numerical_stages"]["1"]
                for place in earlier["single_holder_results"]:
                    for label,mode in (("retained","unread_past_D"),("clean","pure_squared_count")):
                        record=place["read"][mode]
                        comparison(samples[label]["settings"],record["settings_and_scores"]["every_joint_probability"])
                        assert samples[label]["M_minus"]==F(record["settings_and_scores"]["signed_M_XXX_minus_three_XZZ"])
    return findings,archived_tables(archive)


def physical_crosscheck(reconstruction, helper):
    historical=json.loads(gzip.decompress(SOURCE_DATA.read_bytes()))["cases"]
    for label, record in reconstruction.items():
        width,law=label.split('/')
        fixture=helper["sources"][width][law]
        for code in ("retained","clean"):
            q=record["cases"][code]
            raw=fixture["representative"][code]
            assert tuple(tuple(F(v) for v in r) for r in raw["probabilities"])==q["settings"]
            assert raw["gram"]==q["gram"]
        if width=="4":
            actual=next(c for c in historical if c["id"]=="single4/1/0" and c["law"]==law)
            assert actual["stages"][1]==[list(row) for row in fixture["ordinary_growth"]["reached_rows"]]
        partial={}
        for code,v in fixture["representative"].items():
            if v["denominator"] is None:
                partial[code]={"status":"zero probability","certificate":None}
                continue
            q=certificate_of(v["gram"])
            assert q["settings"]==tuple(tuple(F(w) for w in r) for r in v["probabilities"])
            partial[code]={"status":"exact","certificate":q["certificate"]}
        record["certificates_for_other_preparations_and_complements"]=partial
        for text, rec in record["character_ports"].items():
            obj=fixture["character_ports"][str(int(text,2))]
            assert F(obj["launch_probability_of_this_branch"])==rec["launch"]
            if rec["launch"]:
                assert obj["gram"]==rec["table"]["gram"]
                assert tuple(tuple(F(v) for v in r) for r in obj["probabilities"])==rec["table"]["settings"]
            else:
                assert obj["probabilities"] is None


def build():
    import physical
    one,archive=base_crosscheck()
    two=physical.run()
    physical_crosscheck(one,two)
    return {"order":{"settings":"ZZZ, ZZX, ZXZ, ZXX, XZZ, XZX, XXZ, XXX",
                     "outcomes":"binary lexicographic; 0 means +",
                     "weights":"binary lexicographic (z0,x0,z1,x1,z2,x2)"},
            "symbolic":symbolic_theorem(),"reconstruction":one,"physical_words":two,
            "historical_controls":old_controls(),"archived_first_stage_inventory":archive}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    findings=build()
    data=gzip.compress(as_json(findings),compresslevel=9,mtime=0)
    source=[HERE/q for q in ('answers.py','physical.py','replay.py','preregistration.md','design_reviews.json')]
    source+=[STAGE_DATA,SOURCE_DATA,TURN]
    source.extend(ROOT/name for name in findings["physical_words"]["source_sha256"])
    receipt={"artifact":"newborn_evidence.json.gz", "bytes":len(data),"sha256":sha(data),
             "dependencies":{f.relative_to(ROOT).as_posix():sha(f.read_bytes()) for f in source},
             "review":"scientific referee pending","validation":"separately authored same-task physical measurement plus symbolic and exact 64-list reconstructions"}
    for path,value in ((HERE/"newborn_evidence.json.gz",data),(HERE/"receipt.json",as_json(receipt))):
        if args.check:
            if path.read_bytes()!=value:
                raise SystemExit(f"differing reproducible evidence: {path.name}")
        else:
            path.write_bytes(value)
    print("Exact reconstruction",receipt["sha256"],len(data),"bytes")


if __name__=="__main__":
    main()
