"""Exact conditional and common-ensemble scores of six marked distinctions."""
from fractions import Fraction
from itertools import product
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET = HERE.parent.name
OUTPUT = ROOT / "artifacts" / TICKET / HERE.name
DESIGN = ROOT / "research" / TICKET / "preregistration.md"
WORDS = tuple(product((0, 1), repeat=6))
CONTEXTS = tuple(product((0, 1), repeat=2))
SIGNS = tuple(signs for signs in product((1, -1), repeat=4) if signs.count(-1) % 2)
PRIOR = next((ROOT / "experiments/ENTANGLEMENT-READ-20261120-001B").glob("*_separated_readings"))


def freeze():
    expected = json.loads((HERE / "contract.json").read_text())["design_sha256"]
    assert expected == hashlib.sha256(DESIGN.read_bytes()).hexdigest()


def put(name, rows):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / name).write_text(json.dumps(rows, indent=2, default=str) + "\n")


def cells(hist, embodied):
    masses, local, table_i, table_ii = [], [], [], []
    for s, t in CONTEXTS:
        a_record, b_record, outcomes_i, outcomes_ii = ([0] * 4 for _ in range(4))
        for (a0, a1, sa, b0, b1, tb), n in zip(WORDS, hist, strict=True):
            if not n or embodied and (s != sa or t != tb):
                continue
            a_record[2*a0+a1] += n
            b_record[2*b0+b1] += n
            outcomes_i[2*(a0, a1)[s] + (b0, b1)[t]] += n
            outcomes_ii[2*int(a0 == a1 == s)+int(b0 == b1 == t)] += n
        masses.append(sum(a_record))
        local.append([a_record, b_record])
        table_i.append(outcomes_i)
        table_ii.append(outcomes_ii)
    return masses, local, table_i, table_ii


def chsh(tables):
    corr = [Fraction(a-b-c+d, a+b+c+d) for a,b,c,d in tables]
    scores = [sum(s * e for s, e in zip(signs, corr)) for signs in SIGNS]
    return {"joint": tables, "correlations": list(map(str, corr)),
            "signed": str(sum(corr[:3]) - corr[3]), "maximum": str(max(scores)),
            "all_eight": list(map(str, scores))}


def measure(hist, embodied=True):
    masses, local, table_i, table_ii = cells(hist, embodied)
    out = {"masses": masses, "full_pair_counts": local}
    if not all(masses):
        return {**out, "full_hidden": None, "I": None, "II": None}
    tests = [[(0,1), (2,3)], [(0,2), (1,3)]]
    tv = [[sum(abs(Fraction(l,masses[i])-Fraction(r,masses[j]))
               for l,r in zip(local[i][side],local[j][side]))/2 for i,j in pairs]
          for side,pairs in enumerate(tests)]
    return {**out, "full_pair_tv": [[str(v) for v in side] for side in tv],
            "full_hidden": not any(v for side in tv for v in side),
            "I": chsh(table_i), "II": chsh(table_ii)}


def prior_score_check(hist, our):
    import sys
    sys.path.insert(0, str(PRIOR))
    from readings import score
    theirs = score(hist, 3)
    for arm, pred_arm in (("embodied", "embodied"), ("external", "external")):
        if our[arm]["full_hidden"] is None:
            assert theirs[pred_arm]["I"]["maximum"] is None and theirs[pred_arm]["II"]["maximum"] is None
            continue
        for protocol in ("I", "II"):
            assert Fraction(our[arm][protocol]["maximum"]) == Fraction(*theirs[pred_arm][protocol]["maximum"])
            assert Fraction(our[arm][protocol]["signed"]) == Fraction(*theirs[pred_arm][protocol]["signed_s"])
            assert our[arm][protocol]["joint"] == [c[protocol]["joint"] for c in theirs[pred_arm]["contexts"]]
        for lhs, rhs in zip(our[arm]["full_pair_tv"], theirs[pred_arm]["pair_marginal_remote_tv"]):
            assert [Fraction(v) for v in lhs] == [Fraction(*v) for v in rhs]
    return True


def abstract_control():
    def allows(w):
        a0, a1, s, b0, b1, t = w
        return a0 == b0 and a1 != b1 if s == t else a0 == b1 and a1 == b0
    hist = [int(allows(w)) for w in WORDS]
    allowed = [i for i,n in enumerate(hist) if n]
    assert len(allowed) == 16 and hist == hist[::-1]
    # An affine binary set is closed under a three-word exclusive-or.
    failure = next((x,y,z,x^y^z) for x in allowed for y in allowed for z in allowed
                   if not hist[x^y^z])
    arms = {}
    for key, counts in (("uniform",hist),("tilt_a0",[n*(1+w[0]) for n,w in zip(hist,WORDS)])):
        arms[key] = {"embodied": measure(counts), "external": measure(counts,False)}
        assert prior_score_check(counts, arms[key])
    assert arms["uniform"]["embodied"]["I"]["signed"] == "4"
    assert arms["uniform"]["embodied"]["full_hidden"]
    assert arms["uniform"]["embodied"]["II"]["correlations"][0] == arms["uniform"]["embodied"]["II"]["correlations"][3]
    return {"order":"a0,a1,s,b0,b1,t in binary order", "uniform_histogram":hist,
            "affine_closure_counterexample":[format(i,"06b") for i in failure],
            "complement_preserves_all_64_membership_tests": True,
            "scores":arms, "two_scorers_agreed":True}


if __name__ == "__main__":
    freeze()
    control = abstract_control()
    put("abstract_control.json",control)
    for weight, arms in control["scores"].items():
        print(weight, *(tuple((arm, arms[arm]["I"]["maximum"], arms[arm]["II"]["maximum"],
                              arms[arm]["full_pair_tv"])) for arm in arms))
