"""Run the registered erasure experiment or verify its complete deterministic evidence."""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import json
import os
import resource
import subprocess
import sys

for variable in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"):
    os.environ[variable]="1"
CAP=4*(1024**3)
old_limit,hard_limit=resource.getrlimit(resource.RLIMIT_AS)
resource.setrlimit(resource.RLIMIT_AS,(CAP if old_limit==resource.RLIM_INFINITY else min(CAP,old_limit),hard_limit))
from sympy import Min, Rational, simplify, sqrt
import erasure
import panels

HERE, OUT, RESEARCH, ROOT = erasure.HERE, erasure.OUT, erasure.RESEARCH, erasure.ROOT


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(filename, obj, check):
    raw=(json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False)+"\n").encode()
    path=OUT/filename
    if check:
        assert raw==path.read_bytes(), f"registered output differs: {filename}"
    else:
        path.write_bytes(raw)


def symbolic_root(value):
    x=Fraction(value)
    return sqrt(Rational(x.numerator,x.denominator))


def fine_bounds(record):
    possible=record["outcomes"]
    for key in ("a","b","mixture","plus","minus"):
        assert sum(Fraction(o[key]) for o in possible)==1
    for o in possible:
        assert Fraction(o["plus"])==Fraction(o["minus"])==Fraction(o["mixture"])==(Fraction(o["a"])+Fraction(o["b"]))/2
    indices=record["target_pool_indices"]
    if indices is None:
        return dict(outcomes=len(possible),reports_with_identical_crossed_signs=len(possible),target_omitted=True)
    chosen=set(indices)
    masses=[];capacities=[]
    for side in (True,False):
        rows=[v for i,v in enumerate(possible) if (i in chosen)==side]
        masses.append([sum(Fraction(o[k]) for o in rows) for k in ("a","b")])
        overlaps=Counter(Fraction(o["a"])*Fraction(o["b"]) for o in rows)
        capacities.append(sum(number*symbolic_root(p) for p,number in overlaps.items()))
    fine=simplify(2*Min(*capacities))
    coarse=simplify(2*Min(*(symbolic_root(a*b) for a,b in masses)))
    assert bool(fine>=0) and bool(fine<=coarse)
    return dict(outcomes=len(possible),target_outcomes=len(chosen),reports_with_identical_crossed_signs=len(possible),
                singleton_target=list(map(str,masses[0])),target_and_other_fine_capacities=list(map(str,capacities)),
                sharp_fine_contrast=str(fine),binary_totals_only_bound=str(coarse),actual_ordinary_contrast="0")


def visit_records(obj, path=()):
    if isinstance(obj,dict):
        if "readings" in obj:
            for name, record in obj["readings"].items():
                yield "/".join((*path,name)),record
        for k,v in obj.items():
            if k!="readings": yield from visit_records(v,(*path,k))
    elif isinstance(obj,list):
        for i,v in enumerate(obj): yield from visit_records(v,(*path,str(i)))


def growth_crosschecks(r):
    output=[]
    for case in r["growth_cases"]:
        counts=[]
        fresh=[]
        width=1+max(map(max,case["source_holdings"]))
        occupied=(1<<width)-1
        for singleton in case["source_words"]:
            matches=[]
            for w in range(1<<(1+max(map(max,case["reached_holdings"])))):
                if w&occupied!=singleton: continue
                totals=[sum((w>>i)&1 for i in row) for row in case["reached_holdings"]]
                legal=(all(n%2==0 for n in totals) if case["law"]=="parity" else
                       all(0<n<len(row) for n,row in zip(totals,case["reached_holdings"])))
                if legal:matches.append(w)
            counts.append(len(matches));fresh.append({w>>width for w in matches})
        overlap=len(fresh[0]&fresh[1])
        assert counts==case["extension_counts"] and overlap==case["fresh_overlap_count"]
        gamma=overlap/symbolic_root(counts[0]*counts[1])
        assert not set(case["extensions"][0]["extensions"]) & set(case["extensions"][1]["extensions"])
        marks=set(case["holders_of_target_after"])-set(case["holders_of_target_before"])
        assert len(marks)==1 and len(case["holders_of_target_after"])==2
        output.append(dict(case=case["case"],law=case["law"],extensions=counts,shared=overlap,
                           fresh_overlap=str(gamma),p_plus_given_signed_plus=str(simplify((1+gamma)/2)),
                           p_plus_given_signed_minus=str(simplify((1-gamma)/2))))
    return output


def archive_check(panels_result):
    check_script=ROOT/"docs/prompts/postulate_leads_checks/ways_squared.py"
    actual=subprocess.check_output([sys.executable,"-B",str(check_script)],text=True,cwd=ROOT)
    nae=panels_result["laws"]["nae"]
    for line,tab in zip(actual.splitlines()[:2],[nae["unread"],nae["characters"][0]["panel"]]):
        assert f"{float(Fraction(tab['score'])):.4f}" in line and "common explanation exists: True" in line
        assert tab["common_table"]["common"]
    assert [0,1,2,3,6]==sorted(set(value for row in nae["characters"][0]["amplitudes_on_p_q"] for value in row))
    assert "5/6" in actual and "1/6" in actual and "1/2" in actual
    return actual.splitlines()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check",action="store_true",help="Require exact agreement with existing output files without changing them.")
    args=parser.parse_args()
    formal=erasure.run()
    save("formal.json",formal,args.check)
    panel=panels.run()
    save("four_knot.json",panel,args.check)
    command=[sys.executable,"-B",str(HERE/"physical.py")]
    if args.check:command.append("--check")
    subprocess.run(command,check=True,stdout=subprocess.PIPE)
    with gzip.open(OUT/"physical.json.gz","rt") as stream: physical=json.load(stream)
    bounds={name:fine_bounds(row) for name,row in visit_records(physical)}
    assert bounds
    summary=dict(fine_bounds=bounds, independently_enumerated_growth=growth_crosschecks(physical),
                 earlier_rounded_replay=archive_check(panel))
    save("physical_checks.json",summary,args.check)
    sources={*HERE.glob("*.py"),HERE/"contract.json",HERE/"identity.json",RESEARCH/"preregistration.md",
             RESEARCH/"design_for_review.md",RESEARCH/"review_candidate_v2.md",RESEARCH/"design_reviews.md",
             ROOT/"docs/prompts/postulate_leads_checks/ways_squared.py",ROOT/"docs/prompts/2026-11-20_postulate_leads.md"}
    sources.update((ROOT/"tools/knotlab").glob("*.py"))
    for path,hash_value in physical["sources"].items():
        file=ROOT/path;assert digest(file)==hash_value;sources.add(file)
    names=("formal.json","four_knot.json","physical.json.gz","physical_checks.json")
    receipt=dict(schema_version=1,ticket=HERE.parent.name,experiment=HERE.name,evidence_stage="exploratory",
                 scientific_referee="pending",resource_cap_bytes=CAP,numerical_threads=1,
                 inputs={p.relative_to(ROOT).as_posix():digest(p) for p in sorted(sources)},
                 outputs={name:digest(OUT/name) for name in names},
                 evidence=dict(census=formal["census"],full_four_knot_character_panels=sum(len(law["characters"]) for law in panel["laws"].values()),
                               rational_common_certificates=4,physical_readings=len(bounds),crosschecked_growth_cases=len(summary["independently_enumerated_growth"])))
    save("receipt.json",receipt,args.check)
    print(json.dumps(dict(check=args.check,receipt=digest(OUT/"receipt.json"),evidence=receipt["evidence"],outputs=receipt["outputs"]),sort_keys=True))


if __name__=="__main__":main()
