"""Audit the degree-two source admission and its Boolean/syntactic boundaries."""
import argparse
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
from math import comb
from pathlib import Path
from random import Random
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from external_evidence_admission_schema_model import validate_admission_record

PDF_SHA256 = "9f7eb894da07496b4cba14cbf7a4a109d64e994837fc0478be541cc4aaa57306"


def truth_controls(n):
    points = list(product((0,1),repeat=n))
    def table(f):
        return sum(1 << i for i,x in enumerate(points) if f(x))
    def affine(mask, bit):
        return table(lambda x: (sum(x[j] for j in range(n) if mask>>j&1)+bit)%2==0)
    meanings={0}
    for form in (affine(mask,b) for mask in range(1<<n) for b in (0,1)):
        meanings |= {old|form for old in meanings}
    nonlinear=table(lambda x: x[0]*x[1]==x[2])
    assert nonlinear not in meanings
    falsifiers=[(0,0,1),(0,1,1),(1,0,1)]
    assert all(not (nonlinear >> points.index(f+(0,)*(n-3)) & 1) for f in falsifiers)
    assert (nonlinear >> points.index((1,1,1)+(0,)*(n-3)) & 1)
    return len(meanings)


def clause_roster(n):
    return [tuple(v*s for v,s in zip(variables,signs)) for variables in combinations(range(1,n+1),3)
            for signs in product((-1,1),repeat=3)]


def compare_weakening(n, formula):
    has_counterexample=False
    has_source_model=False
    attempts=0
    for source in product((0,1),repeat=n):
        indicators=[[int(source[abs(lit)-1] != (lit>0)) for lit in row] for row in formula]
        sat=all(not(u and v and w) for u,v,w in indicators)
        extensions=0
        for witnesses in product((0,1),repeat=len(formula)):
            # The disjunction contains the equations [p+1=0]. It is false iff all p vanish.
            disjunction=any((t^(u*v)) or (t*w) for t,(u,v,w) in zip(witnesses,indicators))
            extensions+=not disjunction
            attempts+=1
        assert extensions==int(sat)
        has_source_model |= sat
        has_counterexample |= bool(extensions)
    assert has_source_model==has_counterexample
    return attempts


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-pdf",type=Path)
    pdf=parser.parse_args().source_pdf
    if pdf and hashlib.sha256(pdf.read_bytes()).hexdigest()!=PDF_SHA256:
        raise ValueError("unexpected primary document version")
    doc=json.loads((HERE/"admission.json").read_text())
    schema=json.loads((ROOT/"schemas/external_evidence_admission.schema.json").read_text())
    verdict=validate_admission_record(ROOT,schema,doc)
    assert verdict.accepted,verdict.errors
    assert len(doc)==22 and not any(doc["contact_first_safe_conclusions"].values())
    assert {Path(p).parts[1] for p in doc["local_dependencies"]}=={"EVIDENCE-001A","ROUTE-PARITY-TRANSFER-20261115-001C"}
    assert PDF_SHA256 in (HERE/"proof.md").read_text()
    checks=0
    for n in range(3,8):
        roster=clause_roster(n)
        assert len(roster)==len(set(roster))==8*comb(n,3)
        for bits in product((0,1),repeat=n):
            assert sum(any(bits[abs(i)-1]==(i>0) for i in c) for c in roster)==7*comb(n,3)
            checks+=1
    roster=clause_roster(3)
    attempts=sum(compare_weakening(3,[row for i,row in enumerate(roster) if choice>>i&1]) for choice in range(256))
    rng=Random(175)
    four=clause_roster(4)
    for m in range(1,8):
        attempts+=compare_weakening(4,rng.choices(four,k=m))
    assert Fraction(2)*Fraction(7,8)**8 < 1
    print(json.dumps({"status":"passed","admission_fields":len(doc),"source_pdf_sha256":PDF_SHA256,
                      "declared_degree":2,"affine_clause_meanings_n3":truth_controls(3),
                      "affine_clause_meanings_n4":truth_controls(4),"population_assignment_checks":checks,
                      "weakening_clause_menus_n3":256,"weakening_cases_n4":7,
                      "tested_source_and_auxiliary_assignments":attempts},sort_keys=True))


if __name__=="__main__":
    main()
