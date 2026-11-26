"""Reconstruct the registered setting families and check the two countings."""

import argparse
import gzip
import json
import math
import os
import resource
import runpy
import sys
import time
from collections import Counter, defaultdict
from contextlib import redirect_stdout
from fractions import Fraction
from functools import cache
from io import StringIO
from itertools import combinations, product
from pathlib import Path

for variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[variable] = "1"
cap = 2_000_000_000
resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
import numpy as np
from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REGISTERED = ROOT / "research/TWO-COUNTINGS-20261125-001A"
OUTPUT = next((ROOT / "artifacts/TWO-COUNTINGS-20261125-001A").iterdir())
SETTINGS = tuple(product(range(2), repeat=2))
RECORDS = (("x1", "x2", "x3", "za"), ("y1", "y2", "y3", "zb"))


def read(path):
    return json.loads(path.read_text())


def rule(law, *places):
    assert len(places) == len(set(places))
    assert law in ("nae", "even", "odd")
    return (law, tuple(places))


def parse(text):
    law, places = text[:-1].split("(")
    return rule(law, *places.split(","))


def names(rules):
    return {place for _, places in rules for place in places}


def frozen_structures():
    return {k: tuple(rule(law, *places) for law, places in rows)
            for k, rows in read(REGISTERED / "structures.json").items()}


def ordinary_settings(options=(("x2", "x3"), ("y2", "y3")), fresh=("za", "zb")):
    return {ab: (rule("nae", "x1", options[0][ab[0]], fresh[0]),
                 rule("nae", "y1", options[1][ab[1]], fresh[1])) for ab in SETTINGS}


def valid(law, bits):
    if law == "nae":
        return any(bits) and not all(bits)
    return sum(bits) % 2 == (law == "odd")


@cache
def one_start_state(rules):
    positions = {name: i + 1 for i, name in enumerate(sorted(names(rules)))}
    clauses = []
    for law, places in rules:
        for bits in product((0, 1), repeat=len(places)):
            if not valid(law, bits):
                clauses.append([(-1 if bit else 1) * positions[name]
                                for name, bit in zip(places, bits)])
    with Solver(bootstrap_with=clauses) as solver:
        return solver.solve()


def private_extensions(old, additions):
    """Test a sufficient all-old-assignment certificate for a simultaneous stage."""
    fresh = [set(places) - old for _, places in additions]
    return (
        all(fresh)
        and all(a.isdisjoint(b) for a, b in combinations(fresh, 2))
        and all(law in ("nae", "even", "odd") and len(places) >= 2
                for law, places in additions)
    )


def hand_cases():
    source = frozen_structures()
    opts = tuple(combinations(("x2", "x3", "c"), 2))
    for x, y in product(opts, combinations(("y2", "y3", "t"), 2)):
        yield ("eleven " + "-".join(x) + "/" + "-".join(y), "only",
               source["eleven (start)"], (), ordinary_settings((x, y)), ())
    before = source["smallest gain: part"]
    after = source["smallest gain: part + rule-Q round 1"]
    assert after[:len(before)] == before
    yield "smallest gain", "only", before, after[len(before):], ordinary_settings(), ()
    for label, key in [("seven", "seven (start)"), ("eight", "eight (start)"),
                       ("nine", "nine, the pencil (start)"), ("eighteen", "eighteen (start)")]:
        yield label, "only", source[key], (), ordinary_settings(), ()
    for label in ("ten A", "ten B"):
        start = next(v for k, v in source.items() if k.startswith(label))
        holders = Counter(v for _, row in start for v in row)
        live = next(row for _, row in start if "y1" in row)
        second = tuple(v for v in ("y2", "y3", "t") if v in live and holders[v] > 1)
        loose = next(v for v in ("y2", "y3") if holders[v] == 1)
        for x, take in product(opts, second):
            ident = label + " " + "-".join(x) + "/" + "-".join(second)
            yield (ident, "third birth takes " + take, start, (),
                   ordinary_settings((x, second)), (rule("nae", loose, take, "f3"),))
    start = tuple(parse(r) for r in ("odd(x1,x3,s1)", "odd(h1,h2,h3)",
                                    "even(x2,h1,h2,h3)", "even(y1,y3,s1)",
                                    "odd(k1,k2,k3)", "even(y2,k1,k2,k3)"))
    yield "eight-thirds case", "only", start, (), ordinary_settings(), ()


def archive_cases():
    for prefix, pattern in (
        ("Q", "ONE-PARENT-REREAD-20261123-001A/*/census_gains_c_*.jsonl.gz"),
        ("R", "REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C/*/arm1_gains_three_*.jsonl.gz"),
    ):
        i = 0
        for path in sorted((ROOT / "artifacts").glob(pattern)):
            with gzip.open(path, "rt") as stream:
                for line in stream:
                    data = json.loads(line)
                    if data["t"] != 1:
                        continue
                    rows = tuple(parse(row) for row in data["knots"])
                    born = len(data["births"][0])
                    assert born > 0
                    yield (prefix, i, data.get("arm")), "only", rows[:-born], rows[-born:], ordinary_settings(), ()
                    i += 1


def data_rows():
    recorded = read(OUTPUT / "part2_lemma.json")
    rows = {(entry["result"]["name"], variant["label"]): variant
            for entry in recorded["items"] for variant in entry["result"]["variants"]}
    for entry in recorded["records"]:
        data = entry["record"]
        ident = ("Q" if data["arm"] else "R", data["index"], data["arm"])
        (variant,) = entry["variants"]
        rows[ident, "only"] = variant
    return rows


def structural(case, stored):
    ident, label, start, growth, setting, extra = case
    prefix = start + growth
    old = names(prefix)
    assert one_start_state(start)
    assert not growth or private_extensions(names(start), growth)
    name_sets = [{frozenset(setting[ab][i][1]) - old for ab in SETTINGS} for i in (0, 1)]
    assert all(len(s) == 1 for s in name_sets)
    a, b = (next(iter(s)) for s in name_sets)
    assert a == {"za"} and b == {"zb"} and a.isdisjoint(b)
    assert set(RECORDS[0]) <= old | a and set(RECORDS[1]) <= old | b
    for ab in SETTINGS:
        left, right = setting[ab]
        assert left == setting[ab[0], 1 - ab[1]][0]
        assert right == setting[1 - ab[0], ab[1]][1]
        assert not b.intersection(left[1]) and not a.intersection(right[1])
        additions = (left, right) + extra
        assert private_extensions(old, additions)
        for _, places in extra:
            assert set(places).isdisjoint(a | b)
        actual = tuple(parse(r) for r in stored["finished"][str(ab)])
        assert Counter(prefix + additions) == Counter(actual), (ident, label, ab)
    expected_rows = ["from the start"] + (["from stage 1"] if growth else [])
    compared = []
    for row, stats in stored["rows"].items():
        if "verdict" not in stats:
            continue
        h = stats["hypotheses"]
        assert h["h0"] and all(h["h1p"].values()) and h["h2"]
        assert all(h["h3p"].values()) and all(h["h4"].values()) and h["met"] and not h["fails"]
        assert h["lost-weight rule"] and not h["weight lost at the setting stage"]
        assert not h["weight lost at a later stage"]
        assert stats["score_all"] == "2" and stats["change_first"] == stats["change_second"] == "0"
        compared.append(row)
    assert sorted(compared) == sorted(expected_rows)
    return len(compared)


def check_part2(pilot):
    rows = data_rows()
    cases = list(hand_cases()) + list(archive_cases())
    keys = {(ident, label) for ident, label, *_ in cases}
    assert len(keys) == len(cases) and keys == rows.keys()
    selected = (cases[:2] + [case for case in cases if isinstance(case[0], tuple)
                              and case[0][0] == "R"][:2]) if pilot else cases
    families = defaultdict(Counter)
    for case in selected:
        ident, label = case[:2]
        group = ident if isinstance(ident, str) else ("rule Q " + ident[2] if ident[0] == "Q" else "rule R")
        if isinstance(ident, str):
            group = ident.split()[0] if ident.startswith(("ten ", "eleven ")) else ident
        n = structural(case, rows[ident, label])
        families[group].update({"four-setting histories": 1, "pre-setting verdicts": n,
                                "setting histories with a third private birth": int(bool(case[-1]))})
    return {"families": dict(families), "histories examined": len(selected),
            "pre-setting verdicts": sum(row["pre-setting verdicts"] for row in families.values()),
            "hypotheses failing": 0, "histories with stages after the setting stage": 0,
            "method": "One satisfying start state, a common prefix, and disjoint private fresh sets in each added stage certify extension for every allowed old state. Both records use only that prefix and their own setting's fresh distinction. Each reconstructed finished rule multiset is compared with the recorded four-setting family."}


def checks_signs(pilot):
    start = frozen_structures()["eleven (start)"]
    settings = ordinary_settings()
    signs = range(2 if pilot else 512)
    for sign in signs:
        j = 0
        changed = []
        for law, places in start:
            if law != "nae":
                law = ("even", "odd")[(sign >> j) & 1]
                j += 1
            changed.append(rule(law, *places))
        assert j == 9 and one_start_state(tuple(changed))
        old = names(changed)
        for ab in SETTINGS:
            assert private_extensions(old, settings[ab])
            assert set(RECORDS[0]) <= old | {"za"} and set(RECORDS[1]) <= old | {"zb"}
    return {"nonempty starts and both private setting births": len(signs)}


def states_for(rules, positions):
    if not rules:
        return [0]
    clauses = []
    used = sorted(names(rules))
    ids = {name: i+1 for i, name in enumerate(used)}
    for law, places in rules:
        for bits in product((0, 1), repeat=len(places)):
            if not valid(law, bits):
                clauses.append([(-1 if bit else 1) * ids[name] for name, bit in zip(places, bits)])
    states = []
    with Solver(bootstrap_with=clauses) as solver:
        while solver.solve():
            model = solver.get_model()
            states.append(sum(1 << positions[name] for name in used if model[ids[name]-1] > 0))
            solver.add_clause([-v for v in model])
    return states


def compact(state, bits):
    return sum(bool(state & flag) << i for i, flag in enumerate(bits))


def project_example(start, stages, records, finish=False):
    universe = sorted(names(start) | set().union(*(names(ss) for ss in stages)))
    positions = {p: i for i, p in enumerate(universe)}
    bit = lambda p: 1 << positions[p]
    record_masks = tuple(tuple(bit(p) for p in side) for side in records)
    old_states = states_for(start, positions)
    n = len(old_states)
    weights = {o: Fraction(1, n) for o in old_states}
    held = names(start)
    initial_mask = sum(bit(p) for p in held)
    retained_trace = []
    for rules in stages:
        fresh = names(rules) - held
        add = [sum(bit(p) for p in chosen)
               for size in range(len(fresh)+1) for chosen in combinations(sorted(fresh), size)]
        masks = [(law, sum(bit(p) for p in row), len(row)) for law, row in rules]
        next_weights = {}
        for old, mass in weights.items():
            completions = []
            for ext in add:
                word = old | ext
                for law, mask, arity in masks:
                    ones = (word & mask).bit_count()
                    if not (0 < ones < arity if law == "nae" else (ones % 2 == (law == "odd"))):
                        break
                else:
                    completions.append(word)
            if completions:
                share = mass / len(completions)
                next_weights.update((word, share) for word in completions)
        held.update(fresh)
        weights = next_weights
        survival = Counter()
        for word, mass in weights.items():
            survival[word & initial_mask] += mass * n
        retained_trace.append(tuple(survival[o] for o in old_states))
    joint = Counter()
    for word, mass in weights.items():
        joint[tuple(compact(word, flags) for flags in record_masks)] += 1 if finish else mass
    mass = sum(joint.values())
    return {key: Fraction(value, mass) for key, value in joint.items()}, mass, retained_trace


def max_scores(tables):
    denominator = math.lcm(*(p.denominator for table in tables.values() for p in table.values()))
    assert denominator < 2**58
    matrix = {}
    for ab, values in tables.items():
        matrix[ab] = np.zeros((16, 16), dtype=np.int64)
        for (u, v), p in values.items():
            matrix[ab][u, v] = int(p * denominator)
    # For fixed first-observer outcomes, each second-observer value can choose the sign of its own sum.
    responses = {}
    for a in range(2):
        ids = [i for i in range(16) if matrix[a, 0][i].any() or matrix[a, 1][i].any()]
        choices = np.array(list(product((1,-1), repeat=len(ids))), dtype=np.int64)
        for b in range(2):
            responses[a,b] = choices @ matrix[a,b][ids,:]
    best = 0
    for f0_b0, f0_b1 in zip(responses[0,0], responses[0,1]):
        s0 = np.abs(f0_b0 + responses[1,0]).sum(axis=1)
        s1 = np.abs(f0_b1 - responses[1,1]).sum(axis=1)
        best = max(best, int((s0+s1).max()))
    parities = np.array([[(-1)**((i & v).bit_count()) for v in range(16)] for i in range(1, 16)])
    cs = {ab: parities @ matrix[ab] @ parities.T for ab in SETTINGS}
    broad = (cs[0,0][:,None,:,None], cs[0,1][:,None,None,:],
             cs[1,0][None,:,:,None], cs[1,1][None,:,None,:])
    total = sum(broad)
    pmax = max(int((total-2*c).max()) for c in broad)
    pabs = max(int(np.abs(total-2*c).max()) for c in broad)
    return {"score_all": str(Fraction(best,denominator)), "score_parity": str(Fraction(pmax,denominator)),
            "score_parity_abs": str(Fraction(pabs,denominator))}


def marginal(table, observer):
    counts = Counter()
    for values, mass in table.items():
        counts[values[observer]] += mass
    return counts


def variation(first, second):
    return sum(abs(first[k] - second[k]) for k in first.keys() | second.keys()) / 2


def both_changes(tables):
    first = max(variation(marginal(tables[a,0],0), marginal(tables[a,1],0)) for a in range(2))
    second = max(variation(marginal(tables[0,b],1), marginal(tables[1,b],1)) for b in range(2))
    return {"change_first": str(first), "change_second": str(second)}


def example_specs():
    base = frozen_structures()["eleven (start)"]
    orders = read(REGISTERED / "construction_orders.json")["eleven_registered_400"]["orders"]
    for key in ("E0","E1","E2","E2 index 10","E3","E4","E5","E6","E7",
                "Alternative setting reuses h1","Alternative setting reuses h2"):
        first, second = RECORDS
        start = base
        settings = ordinary_settings()
        later = ()
        if key.startswith("E2"):
            i = 10 if key.endswith("10") else 11
            start = ()
            plans = {ab: tuple(((base + ss)[j],) for j in orders[i]) for ab, ss in settings.items()}
        else:
            if key == "E3" or key.startswith("Alternative setting"):
                substitute = "s1" if key == "E3" else key.split()[-1]
                settings = ordinary_settings(fresh=(substitute, "zb"))
                first = first[:3] + (substitute,)
            elif key == "E4":
                settings = ordinary_settings(fresh=("z","z"))
                first, second = first[:3] + ("z",), second[:3] + ("z",)
            elif key == "E5":
                later = ((rule("even","za","zb","x1"),),)
            elif key == "E6":
                first = first[:3] + ("zb",)
            elif key == "E7":
                later = ((rule("even","zb","w","x1"),),)
                first = first[:3] + ("w",)
            plans = {ab: (ss,) + later for ab, ss in settings.items()}
        yield key, start, plans, (first,second)


def example_hypotheses(key, start, plans, records, traces):
    if key.startswith("E2"):
        return {"applicability": "Ordinary rules intervene between the two setting births."}
    held = names(start)
    jointly = {ab: [set(places) - held for _, places in plans[ab][0]] for ab in SETTINGS}
    failures = []
    if key == "E1":
        failures.append("h0")
    different_names = any(len({frozenset(sides[i]) for sides in jointly.values()}) > 1 for i in (0,1))
    shared = any(a & b for a, b in jointly.values())
    if shared or different_names:
        failures.append("h1′")
    def old_only(stage):
        rows = [traces[ab][stage] for ab in SETTINGS]
        return len(set(rows)) == 1 and all(v in (0,1) for v in rows[0])
    setting_loss = any(any(p != 1 for p in tr[0]) for tr in traces.values())
    if setting_loss and not old_only(0):
        failures.append("h2")
    later_cross = any(a.intersection(places) and b.intersection(places)
                      for ab,(a,b) in jointly.items() for stage in plans[ab][1:] for _,places in stage)
    if shared or later_cross:
        failures.append("h3′")
    later_loss = any(len(tr)>1 and tr[-1] != tr[0] for tr in traces.values())
    foreign = any(not set(records[i]) <= held | jointly[ab][i] for ab in SETTINGS for i in (0,1))
    if (later_loss and not old_only(-1)) or foreign:
        failures.append("h4")
    return {"failures": failures, "setting loss": setting_loss,
            "later loss": later_loss, "record exceeds its allowed distinctions": foreign}


def check_examples(pilot):
    official = {row["example"]: row for row in read(OUTPUT / "part4_examples.json")["examples"]}
    result = {}
    for key, start, plans, rec in example_specs():
        if pilot and key not in ("E2", "E5"):
            continue
        tables, masses, traces = {}, {}, {}
        for ab in SETTINGS:
            t, m, survived = project_example(start, plans[ab], rec, finish=(key == "E1"))
            tables[ab], traces[ab] = t, survived
            masses["".join(map(str,ab))] = str(Fraction(1) if key == "E1" else m)
        row = max_scores(tables) | both_changes(tables)
        if key in official:
            assert all(row[k] == official[key][k] for k in row), (key, row)
        row["kept by setting pair"] = masses
        check = example_hypotheses(key,start,plans,rec,traces)
        row["hypotheses for the counting used"] = check
        if key in official and not key.startswith("E2"):
            reported = official[key]["hypotheses (counting from the start)"]
            found = [failure for failure in check["failures"] if key != "E1" or failure != "h0"]
            assert found == reported["fails"] and check["setting loss"] == reported["weight lost at the setting stage"]
            assert check["later loss"] == reported["weight lost at a later stage"]
            assert masses == {a+b: official[key]["kept"][str((int(a),int(b)))]
                              for a,b in ("00","01","10","11")}
        result[key] = row
    return result


def scope_cases(pilot):
    start = tuple(rule(law,name,"h","k") for law,name in (
        ("even","x1"), ("even","x2"), ("odd","x3"),
        ("even","y1"), ("odd","y2"), ("odd","y3")))
    setting = ordinary_settings()
    coupled = (rule("nae","za","u","v"), rule("nae","zb","u","v"))
    result = {}
    scenarios = [("Two extra rules at the setting stage", start,
                  {ab:(ss+coupled,) for ab,ss in setting.items()})]
    if not pilot:
        scenarios.extend([
            ("The same two rules one stage later", start,
             {ab:(ss,coupled) for ab,ss in setting.items()}),
            ("A later extending rule holds both fresh distinctions", start,
             {ab:(ss,(rule("even","za","zb","w"),)) for ab,ss in setting.items()}),
            ("Only the later-loss condition fails", tuple(
                rule("even" if places[0] == "y2" else law, *places) for law,places in start),
             {ab:(ss,(rule("even","zb","x1","y1"),)) for ab,ss in setting.items()}),
        ])
    for label, old_rules, plans in scenarios:
        support = {}
        tables = {}
        for ab, stages in plans.items():
            table, mass, trace = project_example(old_rules,stages,RECORDS)
            tables[ab] = table
            q_zb = Counter()
            for (aval, bval), prob in table.items():
                q_zb[(aval & 1, bval >> 3)] += prob
            support["".join(map(str,ab))] = {
                "kept weight": str(mass),
                "weight of (old x1, second setting distinction) in 00,01,10,11 order":
                    [str(q_zb[i,j]) for i,j in SETTINGS],
                "record joint probabilities, first observer then second, bit order as in the definitions":
                    [[f"{a:04b}"[::-1],f"{b:04b}"[::-1],str(prob)]
                     for (a,b),prob in sorted(table.items())]
            }
        result[label] = {"start":old_rules, "stages at setting pair 00": plans[0,0],
                         "both record changes":both_changes(tables), "setting pairs":support,
                         "all-functions score":max_scores(tables)["score_all"]}
        if label == "Two extra rules at the setting stage":
            # A0=A1=B0=+1, and B1=+1 exactly when y1 and zb differ.
            witness = []
            for ab in SETTINGS:
                witness.append(sum(prob * (1 if not ab[1] or (v & 1) != (v >> 3) else -1)
                                   for (_,v),prob in tables[ab].items()))
            assert witness == [1,Fraction(1,5),1,0]
            result[label]["correlations of the constant/inequality witness"] = list(map(str,witness))
    completion_counts = {}
    for a,b in SETTINGS:
        completion_counts[f"{a}{b}"] = sum(valid("nae",(a,u,v)) and valid("nae",(b,u,v))
                                              for u,v in SETTINGS)
    result["Completions for the two extra rules at each (za,zb)"] = completion_counts
    if not pilot:
        old = (rule("nae","x","y","t"),)
        positions = {name:i for i,name in enumerate(("x","y","t","z"))}
        before = states_for(old,positions)
        agrees = sum((int(bool(o & 1)) == int(bool(o & 2))) for o in before)
        p = Fraction(agrees,len(before))
        text_value = p * (1-p)/(2-p)
        distance = {}
        for law in ("even","nae"):
            next_stage = ((rule(law,"x","y","z"),),)
            rec = (("x","y","t","z"),("x","y","t","z"))
            seq,_,_ = project_example(old,next_stage,rec)
            uniform,_,_ = project_example(old,next_stage,rec,True)
            distance[law] = str(variation(Counter(seq),Counter(uniform)))
        result["One-birth formula"] = {"start":"nae(x,y,t)", "new rule places":["x","y","z"],
                                        "old states":len(before), "old states with x=y":agrees,
                                        "formula":str(text_value), "measured distances":distance}
        assert distance == {"even":"0","nae":str(text_value)}
        assert result["Two extra rules at the setting stage"]["both record changes"]["change_second"] == "1/10"
        assert result["The same two rules one stage later"]["both record changes"]["change_second"] == "0"
        assert result["A later extending rule holds both fresh distinctions"]["both record changes"]["change_second"] == "0"
        assert result["Only the later-loss condition fails"]["both record changes"]["change_first"] == "1/2"
        # The agreement theorem is an iff about agreement at every stage.
        # Two variable completion counts can compensate by the finish.
        old = tuple(parse(r) for r in ("even(y,h,k)","odd(b,h,k)","even(x,p,q)"))
        stage = (rule("nae","x","y","z"),)
        last = (rule("nae","x","b","w"),)
        distances = {}
        for label, stages, extra_names in (("after first birth",(stage,),("z",)),
                                          ("at the finish",(stage,last),("z","w"))):
            # The paired records contain all variables, so this checks equality of the full distributions.
            rec = (("x","y","b","h","k"), ("p","q") + extra_names)
            seq,_,_ = project_example(old,stages,rec)
            uniform,_,_ = project_example(old,stages,rec,True)
            distances[label] = str(variation(Counter(seq),Counter(uniform)))
        assert distances == {"after first birth":"1/6","at the finish":"0"}
        result["Agreement can return at the finish"] = {
            "start":old, "stages":[stage,last], "full-distribution variation":distances}
    return result


def check_all_open_parts(pilot):
    """Test the same-stage issue when every rule passes on the finished structure."""
    base = (rule("nae","x1","x2","y1"), rule("nae","x3","y2","y3"))
    extra = (rule("nae","za","u","v"), rule("nae","zb","u","v"))
    tables = {}
    canonical = []
    finished = {}
    sys.path.insert(0,str(ROOT / "tools"))
    for ab, setting in ordinary_settings().items():
        stage = setting + extra
        structure = base + stage
        ab_name = "".join(map(str,ab))
        finished[ab_name] = structure
        tables[ab], mass, _ = project_example(base,(stage,),RECORDS)
        assert mass == 1
        atoms = names(structure)
        # All six rules are not-all-equal.
        cnf = "; ".join(" ".join(prefix + p for p in places)
                        for _,places in structure for prefix in ("","~"))
        for i,(_,places) in enumerate(structure):
            if pilot and (ab != (0,0) or i > 0):
                continue
            old_argv = sys.argv
            sys.argv = ["knotlab","check","--cnf",cnf,"--loops",*places[:-1],
                        "--contact",places[-1],"--witnesses",*sorted(atoms-set(places)),"--json"]
            output = StringIO()
            try:
                with redirect_stdout(output):
                    try:
                        runpy.run_module("knotlab",run_name="__main__")
                    except SystemExit as stop:
                        assert stop.code in (0,None)
            finally:
                sys.argv = old_argv
            check = json.loads(output.getvalue())
            assert check["is_knot"] and len(check["allowed"]) == 6
            canonical.append({"setting pair":ab_name,"places":places,"allowed":check["allowed"]})
    score = max_scores(tables)
    changes = both_changes(tables)
    assert score["score_all"] == "61/30" and changes == {"change_first":"0","change_second":"1/60"}
    # The second observer's value with positive difference under the first observer's choices
    # supplies a witness with the other three outcome functions constant.
    b = 1
    m0,m1 = (marginal(tables[a,b],1) for a in range(2))
    plus = sorted(v for v in m0.keys() | m1.keys() if m0[v] >= m1[v])
    witness = [sum(p * (1 if not ab[1] or v in plus else -1) for (_,v),p in tables[ab].items())
               for ab in SETTINGS]
    assert witness[0]+witness[1]+witness[2]-witness[3] == Fraction(61,30)
    return {"start":base,"setting-stage rules include two additional rules sharing u and v":extra,
            "four finished structures":finished,"canonical whole-structure tests":canonical,
            "canonical invocation":"The knotlab check command is run in-process with the whole structure converted to clauses and all other distinctions as witnesses.",
            "scores":score,"record changes":changes,"kept mass in each history":"1",
            "joint record probabilities by setting pair, first and second records in their declared bit order":
                {"".join(map(str,ab)):{f"{u:04b}"[::-1] + " " + f"{v:04b}"[::-1]:str(prob)
                                       for (u,v),prob in sorted(table.items())}
                 for ab,table in tables.items()},
            "exact witness":{"A0,A1,B0":"+1","B1 takes +1 on the following record values":
                             [f"{v:04b}"[::-1] for v in plus],"correlations":list(map(str,witness))}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("size", choices=("pilot","full"))
    parser.add_argument("part", choices=("examples","part2","signs","scope","six_rules"))
    args = parser.parse_args()
    started = time.perf_counter()
    run = {"examples": check_examples, "part2": check_part2, "signs": checks_signs,
           "scope": scope_cases, "six_rules":check_all_open_parts}[args.part]
    result = run(args.size == "pilot")
    seconds = time.perf_counter() - started
    path = HERE / f"lemma_{args.part}_{args.size}.json"
    path.write_text(json.dumps({"selection":args.size, "seconds":round(seconds,6),
                                "maximum resident KiB":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                                "result":result}, indent=2, ensure_ascii=False) + "\n")
    print(f"{path.name}: {seconds:.3f} seconds")


if __name__ == "__main__":
    main()
