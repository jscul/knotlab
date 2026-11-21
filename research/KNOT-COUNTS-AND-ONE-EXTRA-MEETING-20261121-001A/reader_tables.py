"""Exact reconstruction of the seven-question, three-reader signed-count probe."""

from collections import Counter
from contextlib import redirect_stdout
from dataclasses import dataclass
from fractions import Fraction as F
from functools import cache
from hashlib import sha256
from io import StringIO
from itertools import combinations, product
import json
from math import gcd, lcm, sqrt
from pathlib import Path
import runpy


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ORIGINAL = ROOT / "docs/prompts/postulate_leads_checks/knot_phases.py"
ORIGINAL_SHA256 = "79a5c015781f05ceec62c372cc0d12598d9f94a48d50d822e77986fb2c50acaf"
PRIOR = "THREE-READERS-AND-GROWTH-20261120-001A"
PRIOR_TABLE = ROOT / "artifacts" / PRIOR / f"{PRIOR}-E001_three_readers" / "lead.json"
MENU = (("read", None), ("change", 0), ("change+60", 2), ("change-60", -2),
        ("change+90", 3), ("change+30", 1), ("change-30", -1))
SETTINGS = tuple(product((0, 1), repeat=3))
LISTS = tuple(tuple((word >> j) & 1 for j in range(6)) for word in range(64))


@dataclass(frozen=True, slots=True)
class Real:
    """A real element a+b sqrt(3) with exact rational coefficients."""

    a: F = F(0)
    b: F = F(0)

    def __bool__(self):
        return bool(self.a or self.b)

    def __add__(self, other):
        if isinstance(other, Real):
            return Real(self.a+other.a, self.b+other.b)
        return Real(self.a+other, self.b)

    __radd__ = __add__

    def __neg__(self):
        return Real(-self.a, -self.b)

    def __sub__(self, other):
        return self + -other

    def __mul__(self, other):
        if isinstance(other, Real):
            return Real(self.a*other.a + 3*self.b*other.b, self.a*other.b + self.b*other.a)
        return Real(self.a*other, self.b*other)

    __rmul__ = __mul__

    def __truediv__(self, other):
        if isinstance(other, Real):
            return self * Real(other.a, -other.b) / (other.a*other.a - 3*other.b*other.b)
        return self * (F(1)/other)

    def sign(self):
        a, b = self.a, self.b
        if not a:
            return (b > 0)-(b < 0)
        if not b or (a > 0) == (b > 0):
            return 1 if a > 0 else -1
        return (1 if a > 0 else -1) * (1 if a*a > 3*b*b else -1)

    def __lt__(self, other):
        return (self-other).sign() < 0

    def __abs__(self):
        return -self if self.sign() < 0 else self

    def __float__(self):
        return float(self.a) + sqrt(3)*float(self.b)

    def __str__(self):
        if not self.b:
            return str(self.a)
        join = "+" if self.b > 0 else "-"
        return f"{self.a}{join}{abs(self.b)}*sqrt(3)"


ZERO = Real()
ONE = Real(F(1))


@dataclass(frozen=True, slots=True)
class Complex:
    re: Real = ZERO
    im: Real = ZERO

    def __add__(self, other):
        return Complex(self.re+other.re, self.im+other.im)

    def __sub__(self, other):
        return Complex(self.re-other.re, self.im-other.im)

    def __mul__(self, other):
        if isinstance(other, Complex):
            return Complex(self.re*other.re-self.im*other.im, self.re*other.im+self.im*other.re)
        return Complex(self.re*other, self.im*other)

    def conjugate(self):
        return Complex(self.re, -self.im)

    def norm(self):
        return self.re*self.re + self.im*self.im


C0, C1 = Complex(), Complex(ONE)
STEP = Complex(Real(b=F(1, 2)), Real(F(1, 2)))
ANGLES = [C1]
for _ in range(11):
    ANGLES.append(ANGLES[-1] * STEP)
ANGLES = tuple(ANGLES)


def _phase(angle):
    return ANGLES[angle % 12]


def _bit(word, slot):
    return (word >> slot) & 1


def _states():
    positive = tuple(C1 if 0 < w.bit_count() < 3 else C0 for w in range(8))
    primary = tuple((C1-_phase(4*w.bit_count())) * Real(b=F(1, 3)) for w in range(8))
    even = tuple(C1 if w.bit_count() % 2 == 0 else C0 for w in range(8))
    assert all(a.norm() == b.norm() for a, b in zip(primary, positive, strict=True))
    for word, (p,z) in enumerate(zip(positive, primary, strict=True)):
        assert p * _phase(2 * word.bit_count() - 3) == z
    assert _phase(11)*STEP == C1
    return positive, primary, even


def _move(word, operators, subset):
    end, angle = word, 0
    for reader, theta in enumerate(operators):
        if not _bit(subset, reader):
            continue
        if theta is None:
            angle += 6*_bit(word, reader)
        else:
            angle += theta*(1-2*_bit(word, reader))
            end ^= 1 << reader
    return end, _phase(angle)


@cache
def _probabilities(state, operators):
    """Born probabilities via exact signed permutation moments and binary inversion."""
    total = sum((a.norm() for a in state), ZERO)
    moments = []
    for subset in range(8):
        count = C0
        for word, a in enumerate(state):
            next_word, phase = _move(word, operators, subset)
            count = count + state[next_word].conjugate() * phase * a
        assert not count.im
        moments.append(count.re / total)
    answer = tuple(sum((weight*(-1)**((outcome & subset).bit_count()) for subset, weight in enumerate(moments)), ZERO)/8
                   for outcome in range(8))
    assert sum(answer, ZERO) == ONE and all(p.sign() >= 0 for p in answer)
    return answer


@cache
def _direct_bra_probabilities(state, operators):
    """Use tensor-product eigenvector bras, independently of moment inversion."""
    total = sum((a.norm() for a in state),ZERO)
    divisor = total * 2**sum(theta is not None for theta in operators)
    answers = []
    for outcome in range(8):
        amplitude = C0
        for word,a in enumerate(state):
            phase = 0
            for reader, theta in enumerate(operators):
                if theta is None:
                    if _bit(word,reader) != _bit(outcome,reader):
                        break
                elif _bit(word,reader):
                    phase += 6*_bit(outcome,reader)-theta
            else:
                amplitude = amplitude + a*_phase(phase)
        answers.append(amplitude.norm()/divisor)
    return tuple(answers)


def _shift(menu, steps):
    return tuple((name, None if theta is None else theta+steps) for name,theta in menu)


def _menu_estimates(state, first, second):
    operators = (first[1], second[1])
    picked = [tuple(operators[s] for s in setting) for setting in SETTINGS]
    result = tuple(_probabilities(state, row) for row in picked)
    assert result == tuple(_direct_bra_probabilities(state,row) for row in picked)
    return result


def _marginals(table):
    result = {}
    for n in (1, 2):
        for readers in combinations(range(3), n):
            mask = sum(1 << r for r in readers)
            keys = tuple(w for w in range(8) if not w & ~mask)
            distributions = {}
            for setting, outputs in zip(SETTINGS, table, strict=True):
                selected = tuple(setting[r] for r in readers)
                held = tuple(sum((p for w,p in enumerate(outputs) if w & mask == key), ZERO) for key in keys)
                if selected in distributions:
                    assert distributions[selected] == held
                else:
                    distributions[selected] = held
            result["/".join(map(str, readers))] = [{"own_settings": selected, "outcomes": dict(zip(keys, map(str, held), strict=True))}
                                                     for selected, held in distributions.items()]
    return result


def _deterministic_columns():
    return tuple(tuple(8*i + sum(answer[2*r + setting[r]] << r for r in range(3))
                       for i,setting in enumerate(SETTINGS)) for answer in LISTS)


COLUMNS = _deterministic_columns()
MATRIX = tuple(tuple(int(i in col) for col in COLUMNS) for i in range(64))
FORMS = {
    "111_plus_100_010_001": ("111", ("100", "010", "001"), +1),
    "111_minus_100_010_001": ("111", ("100", "010", "001"), -1),
    "000_plus_011_101_110": ("000", ("011", "101", "110"), +1),
    "000_minus_011_101_110": ("000", ("011", "101", "110"), -1),
}
MERMIN = tuple(name for name, (_,_,sgn) in FORMS.items() if sgn == -1)


def _score_rows():
    labelled = tuple("".join(map(str,s)) for s in SETTINGS)
    rows = {}
    for name, (primary, rest, orientation) in FORMS.items():
        signs = {primary: 1, **{s: orientation for s in rest}}
        c = tuple(signs.get(s,0)*(-1)**out.bit_count() for s in labelled for out in range(8))
        det = tuple(sum(c[i] for i in col) for col in COLUMNS)
        rows[name] = c, min(det), max(det), max(map(abs,det)), det
    return rows


SCORES = _score_rows()


def _scores(table):
    flatten = sum(table, ())
    values = {name: sum((x*p for x,p in zip(row[0], flatten, strict=True) if x), ZERO) for name,row in SCORES.items()}
    literal = max(map(abs,values.values()))
    canonical = max(abs(values[name]) for name in MERMIN)
    detail = {name: {"signed": str(value), "absolute": str(abs(value)), "local_minimum": SCORES[name][1],
                     "local_maximum": SCORES[name][2], "absolute_local_bound": SCORES[name][3],
                     "violates_own_bound": (abs(value)-SCORES[name][3]).sign() > 0,
                     "absolute_over_its_bound": str(abs(value) / SCORES[name][3])}
              for name,value in values.items()}
    return literal, canonical, {"literal_scan_maximum": str(literal),
                                 "literal_maximizing_forms": [name for name,value in values.items() if abs(value) == literal],
                                 "standard_mermin_maximum": str(canonical),
                                 "standard_maximizing_forms": [name for name in MERMIN if abs(values[name]) == canonical],
                                 "forms": detail}


def _check_primal(weights, target):
    if any(w.sign() < 0 for w in weights.values()) or sum(weights.values(), ZERO) != ONE:
        return None
    reproduced = [ZERO]*64
    for strategy, weight in weights.items():
        for i in COLUMNS[strategy]:
            reproduced[i] += weight
    if tuple(reproduced) != target:
        return None
    return {"local": True, "deterministic_lists": 64,
            "weights": [[i,str(w)] for i,w in sorted(weights.items()) if w],
            "normalization_and_all_entries_verified": True}


def _check_separator(coeffs, target):
    scale = lcm(*(x.denominator for x in coeffs))
    ints = [int(x*scale) for x in coeffs]
    common = gcd(*ints) or 1
    ints = [x//common for x in ints]
    bound = max(sum(ints[i] for i in col) for col in COLUMNS)
    value = sum((c*t for c,t in zip(ints, target, strict=True)), ZERO)
    if (value-bound).sign() <= 0:
        return None
    return {"local": False, "deterministic_lists": 64,
            "inequality": [[i,c] for i,c in enumerate(ints) if c], "bound": bound,
            "exact_value": str(value), "exact_gap": str(value-bound), "bound_and_gap_verified": True}


def _supported_solution(cols, target):
    """Use the proposed support and solve its rational columns over Q(sqrt(3))."""
    linear = [[F(row[i]) for i in cols] for row in MATRIX]
    rhs = list(target)
    size = len(cols)
    for col in range(size):
        row = next((i for i in range(col,64) if linear[i][col]), None)
        if row is None:
            return None
        linear[row], linear[col] = linear[col], linear[row]
        rhs[row], rhs[col] = rhs[col], rhs[row]
        div = linear[col][col]
        linear[col] = [x/div for x in linear[col]]
        rhs[col] = rhs[col]/div
        for i, line in enumerate(linear):
            if i != col and (mul := line[col]):
                linear[i] = [a-mul*b for a,b in zip(line,linear[col],strict=True)]
                rhs[i] -= mul*rhs[col]
    return _check_primal(dict(zip(cols, rhs[:size], strict=True)), target)


@cache
def _independent_rows():
    pivots = {}
    selected = []
    for i, row in enumerate(MATRIX):
        residual = list(map(F,row))
        for j, pivot in sorted(pivots.items()):
            if factor := residual[j]:
                residual = [a-factor*b for a,b in zip(residual,pivot,strict=True)]
        decisive = next((j for j,v in enumerate(residual) if v), None)
        if decisive is not None:
            div = residual[decisive]
            pivots[decisive] = [v/div for v in residual]
            selected.append(i)
    return tuple(selected)


def _exact_phase_one(target):
    """Exact terminating fallback, with rational pivots and exact field RHS."""
    selected = _independent_rows()
    r, n = len(selected), len(COLUMNS)
    rows = [[F(x) for x in MATRIX[k]] + [F(i == j) for j in range(r)] for i,k in enumerate(selected)]
    rhs = [target[i] for i in selected]
    basis = list(range(n,n+r))
    costs = [sum(row[j] for row in rows) for j in range(n)] + [F(0)]*r
    while (entry := next((j for j,v in enumerate(costs) if v > 0),None)) is not None:
        _,_,i = min((rhs[i]/row[entry], basis[i], i) for i,row in enumerate(rows) if row[entry] > 0)
        div = rows[i][entry]
        new, val = [x/div for x in rows[i]], rhs[i]/div
        for k,row in enumerate(rows):
            if k != i and (mul := row[entry]):
                rows[k] = [a-mul*b for a,b in zip(row,new,strict=True)]
                rhs[k] -= mul*val
        rows[i], rhs[i], basis[i] = new, val, entry
        costs = [a-costs[entry]*b for a,b in zip(costs,new,strict=True)]
    if not any(v for j,v in zip(basis,rhs,strict=True) if j >= n):
        result = _check_primal({j:v for j,v in zip(basis,rhs,strict=True) if v}, target)
    else:
        y = [F(0)]*len(target)
        for j, idx in enumerate(selected):
            y[idx] = sum(rows[i][n+j] for i,b in enumerate(basis) if b >= n)
        result = _check_separator(y,target)
    if result is None:
        raise RuntimeError("an exact fallback certificate failed full verification")
    return result


@cache
def _certificate(target):
    """Float solvers only suggest certificates; all verdicts are exact."""
    import numpy as np
    from scipy.optimize import linprog

    observed = np.array(tuple(map(float,target)))
    arr = np.array(MATRIX)
    found = linprog(np.zeros(64), A_eq=arr, b_eq=observed, bounds=(0,None), method="highs-ds")
    if found.success:
        proposed = tuple(i for i,v in enumerate(found.x) if v > 1e-10)
        exact = _supported_solution(proposed,target)
        if exact is not None:
            return exact
    else:
        options = np.column_stack((arr.T, -np.ones(64)))
        tested = linprog(np.r_[-observed,1], A_ub=options, b_ub=np.zeros(64), bounds=[(-1,1)]*64+[(None,None)],method="highs-ds")
        if tested.success:
            for max_denominator in (100,1000,10000):
                exact = _check_separator([F(float(x)).limit_denominator(max_denominator) for x in tested.x[:-1]],target)
                if exact is not None:
                    return exact
    return _exact_phase_one(target)


def _frame(state, menu):
    records, tables = [], {}
    choices, canonical = [], []
    for first,second in combinations(menu,2):
        pair = (first[0],second[0])
        table = _menu_estimates(state, first, second)
        tables[pair] = table
        literal, real_mermin, scores = _scores(table)
        cert = _certificate(sum(table, ()))
        rows = [{"setting": s, "outcomes_little_endian": tuple(map(str,p))} for s,p in zip(SETTINGS,table,strict=True)]
        records.append({"questions": pair, "angles_deg": tuple(None if x[1] is None else x[1]*30 for x in (first,second)),
                        "rows": rows, "scores": scores, "all_proper_local_marginals": _marginals(table),
                        "common_joint": cert})
        choices.append(literal)
        canonical.append(real_mermin)
    high, std_high = max(choices),max(canonical)
    literal_equal = [r["questions"] for r,v in zip(records,choices,strict=True) if v == high]
    proper_equal = [r["questions"] for r,v in zip(records,canonical,strict=True) if v == std_high]
    scores_distribution = Counter(r["scores"]["literal_scan_maximum"] for r in records)
    source_norm = sum((a.norm() for a in state),ZERO)
    return {"source": {"raw_complex_amplitudes": [[str(x.re),str(x.im)] for x in state],
                       "unnormalized_squared_weights": [str(x.norm()) for x in state], "squared_norm": str(source_norm),
                       "normalized_ordinary_word_probs": [str(x.norm()/source_norm) for x in state]},
            "menu": [{"name":name,"angle_deg":None if angle is None else angle*30} for name,angle in menu],
            "angles_outside_the_unrotated_named_menu": sorted({theta*30 for _,theta in menu if theta is not None}
                                                              - {theta*30 for _,theta in MENU if theta is not None}),
            "pair_count": len(records), "setting_count_per_pair": len(SETTINGS), "outcome_count_per_setting": 8,
            "mutually_independent_uniform_setting_weights": "1/8", "records": records,
            "literal_scan_global_maximum": str(high), "literal_scan_every_maximizer": literal_equal,
            "standard_mermin_global_maximum": str(std_high), "standard_mermin_every_maximizer": proper_equal,
            "literal_score_distribution": dict(sorted(scores_distribution.items())),
            "pairs_lacking_common_explanation": sum(not r["common_joint"]["local"] for r in records),
            "exact_bra_vs_moment_checked_cells": 64*len(records)}, tables


def _replay_prior_baseline(tables):
    raw = json.loads(PRIOR_TABLE.read_text())
    verdict = {}
    for law in ("nae", "parity"):
        old = raw[law]["attachments"]["0"]
        here = tables[law][("read","change")]
        lookup = dict(zip(SETTINGS,here,strict=True))
        for row in old["rows"]:
            our_setting = tuple(1-s for s in row["settings"])
            expected = tuple(Real(F(i,row["denominator"])) for i in row["numerators"])
            assert lookup[our_setting] == expected
        assert _certificate(sum(here,()))["local"] == old["common"]["local"]
        scores = _scores(here)[2]
        assert scores["forms"]["111_minus_100_010_001"]["signed"] == old["m"]
        verdict[law] = {"setting_order_conversion": "The archive names change then read. Both store plus as bit zero and outcomes little endian.",
                        "cells_exactly_reproduced": 64, "archived_correctly_signed_score":old["m"],
                        "common_joint":old["common"]["local"]}
    return verdict


def reader_checks():
    """Return the complete public, byte-repeatable, algebraically certified reader record."""
    pos,phase,even = _states()
    frames, tables = {}, {}
    cases = {"nae_positive_fixed": (pos,MENU), "nae_primary_fixed": (phase,MENU), "parity_even_fixed": (even,MENU),
             "nae_positive_in_primary_frame": (pos,_shift(MENU,-2)),
             "nae_primary_cotransported": (phase,_shift(MENU,+2))}
    for name,(state,menu) in cases.items():
        frames[name], tables[name] = _frame(state,menu)
    equality = {}
    for one,two in (("nae_primary_fixed","nae_positive_in_primary_frame"),("nae_positive_fixed","nae_primary_cotransported")):
        assert tables[one] == tables[two]
        equality[f"{one} = {two}"] = {"paired_menus":len(tables[one]), "exact_cell_equalities":len(tables[one])*64}
    fixed_changes = sum(p != q for pair in tables["nae_positive_fixed"] for a,b in
                        zip(tables["nae_positive_fixed"][pair],tables["nae_primary_fixed"][pair],strict=True) for p,q in zip(a,b,strict=True))
    baseline = _replay_prior_baseline({"nae":tables["nae_positive_fixed"],"parity":tables["parity_even_fixed"]})
    corrected = {}
    for name in ("nae_positive_fixed", "nae_primary_fixed", "parity_even_fixed"):
        data = frames[name]
        at_best = []
        for row in data["records"]:
            if row["questions"] in data["literal_scan_every_maximizer"]:
                markers = row["scores"]["literal_maximizing_forms"]
                at_best.append({"menu":row["questions"], "maximizing_forms":{form:row["scores"]["forms"][form] for form in markers}})
        corrected[name] = {"literal_maximum_and_exact_bounds":at_best,
                           "largest_relative_minus_score":data["standard_mermin_global_maximum"],
                           "real_Z_and_X":next(row["scores"] for row in data["records"] if row["questions"] == ("read","change"))}
    return {"scope": "Finite named setting menus with independently supplied pure states and Born readings.",
            "exact_field": "Q(sqrt(3),i)", "answer_bit_zero_means_plus":True,
            "setting_order":SETTINGS,"outcome_labels":tuple(tuple(_bit(w,i) for i in range(3)) for w in range(8)),
            "deterministic_answer_index": "Bit 2*r+s answers setting s for reader r, with 0 meaning plus.",
            "deterministic_answers": LISTS,
            "deterministic_scores_for_all_forms": {name:{"scores":v[4],"min":v[1],"max":v[2],"absolute_bound":v[3]} for name,v in SCORES.items()},
            "frames":frames,"co_transport_equalities":equality,"changed_cells_at_fixed_frame": fixed_changes,
            "interpretation_of_original_scan": corrected,
            "prior_real_read_and_change_replay":baseline, "old_private_source_zero_sha256":ORIGINAL_SHA256,
            "source_digests": {str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest()
                               for p in (Path(__file__).resolve(),HERE/"preregistration.md",PRIOR_TABLE)}}


def check_source_zero():
    """Reconcile the private original at its actual interface when it is available."""
    digest = sha256(ORIGINAL.read_bytes()).hexdigest()
    if digest != ORIGINAL_SHA256:
        raise ValueError("private source zero has changed from its registered digest")
    captured = StringIO()
    with redirect_stdout(captured):
        old = runpy.run_path(str(ORIGINAL))
    assert tuple(old["menu"]) == tuple(name for name,_ in MENU)
    lines = captured.getvalue().splitlines()
    assert lines[0] == "rule as interference: True True"
    line = iter(lines[1:])
    report = {}
    tol = 1e-12
    for heading, state_name, state in zip(("positive uniform weighting","weighting with the knot phases"),
                                         ("positive","phased"),_states()[:2],strict=True):
        assert next(line) == heading
        field_format = _frame(state,MENU)
        frame, tables = field_format
        pairs = {tuple(row["questions"]):row for row in frame["records"]}
        legacy_scores = {}
        scalar_distance = 0.0
        total = sqrt(float(sum((a.norm() for a in state),ZERO)))
        for word,a in enumerate(state):
            bits = tuple(_bit(word,j) for j in range(3))
            scalar_distance = max(scalar_distance,abs(old[state_name][bits]-(float(a.re)+1j*float(a.im))/total))
        assert scalar_distance < tol
        worst = 0.0
        for pair,table in tables.items():
            for setting, outcomes in zip(SETTINGS,table,strict=True):
                old_out = old["probs"](old[state_name],[old["menu"][pair[s]] for s in setting])
                for x,p in enumerate(outcomes):
                    outcome = tuple(_bit(x,i) for i in range(3))
                    worst = max(worst, abs(float(old_out[outcome])-float(p)))
            approximate = old["score"](old[state_name],*pair)
            exact = _scores(table)[0]
            assert abs(approximate-float(exact)) < tol
            assert old["common"](old[state_name],*pair) == pairs[pair]["common_joint"]["local"]
            legacy_scores[pair] = approximate,exact
        assert worst < tol
        top = []
        for _ in range(5):
            a,slash,b,word,printed,common,explanation,verdict = next(line).split()
            assert (slash,word,common,explanation) == ("/","score","common","explanation:")
            pair = a,b
            assert printed == f"{legacy_scores[pair][0]:.4f}"
            assert verdict == str(pairs[pair]["common_joint"]["local"])
            top.append({"pair":pair,"printed_score":printed,"exact_score":str(legacy_scores[pair][1]),
                        "common_joint":pairs[pair]["common_joint"]["local"]})
        selected = {tuple(row["pair"]) for row in top}
        assert len(selected) == 5
        lowest = min(legacy_scores[pair][1] for pair in selected)
        assert all(not (lowest < exact) for pair,(_,exact) in legacy_scores.items() if pair not in selected)
        assert set(tuple(p) for p in frame["literal_scan_every_maximizer"]) <= selected
        total_line = next(line).strip()
        assert total_line == f"pairs of questions with no common explanation: {frame['pairs_lacking_common_explanation']} of 21"
        report[state_name] = {"original_printed_heading":heading,"all_original_cells_compared":21*64,
                              "all_original_scores_and_common_labels_compared":len(tables), "printed_top_rows":top,
                              "original_printed_total":total_line,"max_floating_probability_error":worst,
                              "max_floating_amplitude_error":scalar_distance}
    assert next(line,None) is None
    return {"verified_original_sha256":digest,"published_replay_does_not_need_private_probe":True,
            "printed_lines":lines,"checks":report}
