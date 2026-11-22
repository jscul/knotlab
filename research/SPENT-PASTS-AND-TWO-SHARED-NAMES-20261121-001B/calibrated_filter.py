"""Verify the rescaled final filter for the alternative legality test over exact reals."""

import argparse
import json
from itertools import product
from pathlib import Path

import sympy as s


HERE = Path(__file__).resolve().parent
INPUT = HERE / "word_checks.json"
OUTPUT = HERE / "calibrated_filter.json"


def clean(matrix):
    return matrix.applyfunc(s.simplify)


def encoded(matrix):
    return [[str(e) for e in row] for row in matrix.tolist()]


def check():
    own = json.loads(INPUT.read_bytes())
    section = own["cases"]["abd/not_all_equal/not_all_equal"]["prepared_state_only_control"]
    cd = [s.Matrix([[s.Rational(x) for x in line] for line in matrix]) for matrix in section["post_F_private_slice_matrices"]]
    u = s.Matrix([[2,0,1],[0,1,-1]])
    assert u*cd[0] == s.eye(2) and u*cd[1] == s.zeros(2,2)
    hi, lo = (7+s.sqrt(13))/2, (7-s.sqrt(13))/2
    assert set((u*u.T).eigenvals()) == {hi,lo}
    assert hi>lo>0
    gram = u.T*u
    n = s.Matrix([1,-2,-2])
    p0 = n*n.T/(n.T*n)[0]
    pm = clean((hi*(s.eye(3)-p0)-gram)/(hi-lo))
    pp = clean(s.eye(3)-p0-pm)
    parts = ((p0,0),(pm,lo),(pp,hi))
    for (p,e),(q,f) in product(parts, repeat=2):
        assert clean(p*q) == (p if e==f else s.zeros(3,3))
        assert clean(gram*p-e*p) == s.zeros(3,3)
    assert clean(s.eye(3)-gram/hi-p0-(1-lo/hi)*pm) == s.zeros(3,3)
    # D=p0+sqrt(1-lo/hi) pm, hence D^T D=I-gram/hi. The source is fixed.
    intensity = s.simplify(2/(10*hi))
    assert s.simplify(intensity-(7-s.sqrt(13))/90) == 0
    weights = []
    for d in range(2):
        a = cd[d]
        pre = s.trace(a.T*a)/10
        yes = s.simplify(s.trace(a.T*gram*a)/(10*hi))
        no = s.simplify(s.trace(a.T*(s.eye(3)-gram/hi)*a)/10)
        assert s.simplify(pre-yes-no) == 0
        weights.append([pre,yes,no])
    assert s.simplify(weights[0][1]-intensity) == weights[1][1] == 0
    first_pass = s.Rational(section["first_pass"])
    prior_stops = [s.Rational(9,20),s.Rational(1,40)]
    final_refuse = s.simplify(first_pass-intensity)
    assert s.simplify(sum(prior_stops)+final_refuse+intensity-1) == 0
    assert s.simplify(weights[0][2]+weights[1][2]-final_refuse) == 0
    assert intensity > s.Rational(1,45)
    # The target part is a real data map. Include all matrix units and independent local spectators.
    j = s.Matrix([[0,-1],[1,0]])
    m = -s.kronecker_product(j,j)
    proj = {t:(s.eye(4)+t*m)/2 for t in (-1,1)}
    assert proj[1]+proj[-1] == s.eye(4) and proj[1]*proj[-1] == s.zeros(4)
    fine = {f"{i}{j}":(1 if i==j else -1) for i,j in product(range(2),repeat=2)}
    for i,j in product(range(4),repeat=2):
        x = s.zeros(4); x[i,j] = 1
        for t,p in proj.items():
            y = p*x*p
            assert p*y*p == y and proj[-t]*y*proj[-t] == s.zeros(4)
            assert sum((s.Rational(1,2)*y for v in fine.values() if v==t),s.zeros(4)) == y
    # Exact Choi density on the product of two independent lab-local probe pairs, using
    # indices (original spectator pair, returned data pair). Its trace gives that outcome.
    for t,p in proj.items():
        vec = s.Matrix([p[o,i] for i,o in product(range(4),repeat=2)])
        probe = vec*vec.T/4
        assert s.trace(probe) == s.Rational(1,2)
        for i,o,j,h in product(range(4),repeat=4):
            assert probe[4*i+o,4*j+h] == p[o,i]*p[h,j]/4
    def fmt(x):
        return str(s.simplify(x))
    records = {"first_plus_refusal":{"probability":str(prior_stops[0]),"data":"identity"},
               "first_minus_refusal":{"probability":str(prior_stops[1]),"data":"identity"},
               "first_pass_final_refusal":{"probability":fmt(final_refuse),"data":"identity",
                                           "source":"100d; e_d goes through D C_d", "d0_d1_masses":[fmt(w[2]) for w in weights]}}
    for flag,t in fine.items():
        records["first_pass_final_pass_flags_"+flag] = {
            "sign":t,"fine_target_map":"q P_t rho P_t / 2","fine_weight_on_00":fmt(intensity/4),
            "given_full_input_trace":"q Tr(P_t rho)/2","physical_source":"1000"}
    return {"legality":"prepared-state-only; divided not-all-equal positive source",
            "old_fine_evidence":"two_shared_evidence.json.gz (original fixed filter 1/45)",
            "source_denominator":10,"physical_paths_through_final_private_offer":section["raw_F_paths"],
            "refused_original_wordwise_B_offers":section["forbidden_wordwise_paths"],
            "profile_for_diagonal_and_tags":"same first flags and B refusal; final calibrated filter is never reached",
            "initial_matrix_before_normalizing_by_sqrt_10": [encoded(c) for c in cd],
            "U":encoded(u),"UUt":encoded(u*u.T),"upper_eigenvalue":fmt(hi),"lower_eigenvalue":fmt(lo),
            "passing_K":"U/sqrt(upper_eigenvalue)","refusing_D":"P0+sqrt(1-lower_eigenvalue/upper_eigenvalue)*Pminus",
            "P0":encoded(p0),"Pminus":encoded(pm),"Pplus":encoded(pp),
            "returned_source_registers":"the private matrices are (K C_d or D C_d)/sqrt(10), joined to the physical 100d; sum coherently in d and trace only equal d",
            "d0_d1_pre_final_pass_or_refuse": [[fmt(x) for x in w] for w in weights],
            "whole_launch_meter_q":fmt(intensity),"given_first_pass_final_conditional":fmt(intensity/first_pass),
            "records":records,"two_fresh_admissions":fmt(intensity**2),"fine_probability_given_ready_00":"1/4",
            "fine_given_ready":"P_t rho P_t/2","s_t_sign_repeat_given_two_admissions":"delta_{s,t} P_s rho P_s",
            "conditional_signed_map_weight_per_launch":fmt(intensity),"fixed_filter_direction_upper_bound_attained":True,
            "global_prepared_state_only_optimum":"open"}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--write",action="store_true")
    args = p.parse_args()
    data = json.dumps(check(),ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    if args.write:
        OUTPUT.write_text(data)
    else:
        assert OUTPUT.read_text() == data
    print("Verified calibrated rate (7-sqrt(13))/90, its exact complementary Kraus action, both hidden constituents, all fine outputs and local data-spectator probes.")
