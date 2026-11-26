"""Recount the sampling ticket's screens, confirmations, controls and denominators."""

import argparse
import gzip
import json
import math
import random
import resource
import time
from collections import Counter, defaultdict
from functools import cache
from hashlib import sha256
from itertools import islice, product
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EPIC = "MADE-COPIER-20261125-001"
TICKET = EPIC + "C"
DATA = next((ROOT / "artifacts" / TICKET).glob("*E001*"))
TRIAL = next((ROOT / "experiments" / TICKET).glob("*E001*"))
MAIN = ("R1a", "R1b", "R1c", "R1d", "R2")
FOLLOW = ("R5", "R6")
OUTSIDE = "R1d_beyond_quarter"
RATIONS = ("FLOOR1", "FBP", "CAP-2", "CAP-3", "CAP-4", "ORD", "RATION-2")
TREATMENTS = ("CANCEL-RETIRE", "CANCEL-OFFSHOOT", "CANCEL-WAIT")
CLAIMED = {"form", "both", "vX"}
ALL_READINGS = CLAIMED | {"v1b", "vbb", "vA"}
PREFIX = {"R1a": 836, "R1b": 1000, "R1c": 250, "R1d": 30, "R2": 500}
RUN_DESCRIPTIONS = {
    "R1a": "Parity, take from a met knot.",
    "R1b": "Parity, take one parent step back.",
    "R1c": "Not-all-equal, take from a met knot.",
    "R1d": "Not-all-equal, take one parent step back.",
    "R2": "Parity, holder weighting of takes.",
    "R3": "Confirmation of the main screens at 100.",
    "R5": "Changes to the law, with holding or a take two parent steps back.",
    "R6": "All pairs, screening at 300, on the originally specified small-start lists.",
    "Rcond": "Confirmation of both follow-up screens.",
    OUTSIDE: "Retained growths outside the 30-start prefix, excluded from every reported test."}


def read(path):
    return json.loads(path.read_text())


@cache
def greater(x, n, y, m):
    """Hypergeometric upper tail, summed as integers before the final division."""
    successes = x + y
    lo = max(0, successes - m)
    hi = min(n, successes)
    assert lo <= x <= hi
    den = math.comb(n + m, n)
    # Use the shorter tail. Every step in the recurrence is exact.
    upper = hi - x + 1 <= x - lo
    a, b = (x, hi + 1) if upper else (lo, x)
    term = math.comb(successes, a) * math.comb(n + m - successes, n - a)
    numerator = 0
    for j in range(a, b):
        numerator += term
        term = term * (successes - j) * (n - j) // ((j + 1) * (m - successes + j + 1))
    numerator = numerator if upper else den - numerator
    return numerator / den


def contrasts(rates, controls):
    return {arm: greater(rates["q1"], rates["n1"], rates["q" + arm], rates["n" + arm])
            for arm in controls}


def id_of(run, row, case):
    return run, row["seed"], case["s"], tuple(case["X"]), tuple(case["Y"]), case["reading"]


def family(run, reading):
    return ("main" if run in MAIN else "follow-up", "claimed" if reading in CLAIMED else "reported")


def hierarchy():
    meta = read(ROOT / "research" / TICKET / "starts_c.json")
    starts = meta["starts"]
    permutation = random.Random("C|order").sample(range(len(starts)), len(starts))
    all_ids = [starts[i]["id"] for i in permutation]
    parity = [starts[i]["id"] for i in permutation if not starts[i]["set_aside_parity"]]
    return {r["id"]: r for r in starts}, all_ids, parity, meta["registered_samples"]


def laws(takes, knot, release="RELEASE", weight="T1"):
    return {"/".join((r, t, release, take, knot, weight))
            for r, t, take in product(RATIONS, TREATMENTS, takes)}


def expected_jobs(starts, all_ids, parity, stored):
    by_run = {}
    def jobs(ids, rules):
        return set(product(ids, rules))
    for run in MAIN:
        is_parity = run not in ("R1c", "R1d")
        knot = "parity" if is_parity else "nae"
        takes = ("MET", "STEPS-1") if run == "R2" else (
            ("MET",) if run in ("R1a", "R1c") else ("STEPS-1",))
        ids = (parity if is_parity else all_ids)[:PREFIX[run]]
        by_run[run] = jobs(ids, laws(takes, knot, weight="T2" if run == "R2" else "T1"))
    small_all = {i for i in all_ids if starts[i]["n"] < 5}
    small_parity = small_all.intersection(parity)
    first_five = [i for i in parity if starts[i]["n"] == 5][:300]
    assert first_five == stored["R5 five-knot starts"]
    swap_laws = laws(("MET", "STEPS-1"), "parity", "HOLD") | laws(("STEPS-2",), "parity")
    by_run["R5"] = jobs(small_parity.union(first_five), swap_laws) | jobs(
        small_all, laws(("MET",), "nae", "HOLD"))
    by_run["R6"] = jobs(small_parity, laws(("MET",), "parity")) | jobs(
        small_parity.intersection(parity[:2000]), laws(("STEPS-1",), "parity"))
    return by_run


def audit_controls():
    controls = read(DATA / "controls_R0b.json")["controls"]
    result = {"machinery": [], "planted": [], "negative": []}
    for cell in controls:
        if cell["group"] == "machinery":
            entry = {}
            for label in ("at 100", "at 1,000"):
                unbarred, barred = (cell[label][k] for k in ("nothing barred", "Y barred"))
                entry[label] = {"nothing barred": unbarred, "Y barred": barred,
                                "pass at .01": greater(*unbarred, *barred) <= .01}
            result["machinery"].append({"design": cell["design"], **entry})
            continue
        rows = {}
        for name, screen in cell["readings_at_100"].items():
            rates = screen["rates"]
            item = {"unbarred, Y barred, Y own": [rates[k] for k in ("q1", "q0", "qY")],
                    "stopped": rates["stopped"], "passes": max(contrasts(rates, ("0", "Y")).values()) <= .01}
            assert item["passes"] == screen["first_stage"]["passes_at_100"]
            confirmation = cell.get("readings_at_1000", {}).get(name)
            if confirmation:
                r = confirmation["rates"]
                item.update({"unbarred, Y barred, Y own, fully masked at 1000":
                             [r[k] for k in ("q1", "q0", "qY", "qT")],
                             "confirmed": max(contrasts(r, ("0", "Y", "T")).values()) <= .01})
                assert item["confirmed"] == confirmation["confirmation"]["confirmed"]
            rows[name] = item
        group = "planted" if "arm" in cell else "negative"
        result[group].append({"name": cell["name"], "same forms": cell["same_form"], "readings": rows})
    return result


class Audit:
    def __init__(self, starts, wanted):
        self.starts = starts
        self.wanted = wanted
        self.seen = defaultdict(set)
        self.counts = defaultdict(Counter)
        self.cells = defaultdict(Counter)
        self.passed = {}
        self.outside = []
        self.screens = Counter()
        self.omitted = defaultdict(list)
        self.pc6 = Counter()
        self.pairs_by_weight = {}
        self.repeated = {}
        self.elapsed = {}

    def scan(self, run, limit):
        started = time.perf_counter()
        with gzip.open(DATA / (run + ".jsonl.gz"), "rt") as stream:
            for line in islice(stream, limit):
                self.row(run, json.loads(line))
        self.elapsed[run] = time.perf_counter() - started

    def row(self, run, r):
        start, law = r["start"], r["law"]
        pair = (start, law)
        assert pair not in self.seen[run]
        self.seen[run].add(pair)
        counts = self.counts[run]
        counts["rows"] += 1
        n = self.starts[start]["n"]
        cell = self.cells[run, law, n]
        if "error" in r:
            counts["unread " + r["error"]] += 1
            cell["unread"] += 1
            self.omitted[run, law].append(start)
            return
        counts["read"] += 1
        cell["read"] += 1
        cell["weight of starts read"] += self.starts[start]["labelled"]
        cell["with pair"] += bool(r["pairs"])
        assert r["n_pairs"] == len(r["pairs"]) and r["has_pair"] == bool(r["pairs"])
        counts["pairs"] += len(r["pairs"])
        counts["met pairs"] += sum(p["meet"] is not None for p in r["pairs"])
        counts["rounds over eight eligible pairs"] += len(r["more_than_eight"])
        counts["pairs removed by wholly apart"] += r["removed"]
        counts["knot test disagreements"] += r["knot_test"]["disagree"]
        counts["growths with a failing knot"] += bool(r["knot_test"]["n_fails"])
        counts["failing knots"] += r["knot_test"]["n_fails"]
        ties = r.get("nae_last_round_ties")
        if ties:
            counts["last-round tie checks"] += 1
            counts["last-round tie classes"] += ties["classes"]
        if run in ("R1a", "R1b", "R2"):
            self.pairs_by_weight[(run, start, law.replace("/T2", "/T1"))] = bool(r["pairs"])
        if r["seed"] in self.wanted and run in ("R1a", "R1b", "R6"):
            for p in r["pairs"]:
                key = r["seed"], p["s"], tuple(p["X"]), tuple(p["Y"])
                self.repeated[run, key] = {"eligible pairs in round": r["pair_rounds"][str(p["s"])][1],
                                          "pairs selected": sum(q["s"] == p["s"] for q in r["pairs"])}
        observed = {(p["s"], tuple(p["X"]), tuple(p["Y"]), k)
                    for p in r["pairs"] for k in p["after"] if k in ALL_READINGS}
        actual = {(c["s"], tuple(c["X"]), tuple(c["Y"]), c["reading"]) for c in r["cases"]}
        assert actual == observed and len(actual) == len(r["cases"])
        passed_here = set()
        for c in r["cases"]:
            rates = c["rates100"]
            screened = max(contrasts(rates, ("0", "Y")).values()) <= .01
            assert screened == c["first_stage"]["passes_at_100"]
            assert rates["n1"] == rates["n0"] == rates["nY"] == (300 if run == "R6" else 100)
            pairkey = r["seed"], c["s"], tuple(c["X"]), tuple(c["Y"])
            if (run, pairkey) in self.repeated:
                comparison = self.repeated[run, pairkey].setdefault("first stages by reading", {})
                comparison[c["reading"]] = {"n": rates["n1"], "q1 q0 qY":
                                            [rates[k] for k in ("q1", "q0", "qY")], "passes": screened}
            self.screens[run, c["reading"], screened] += 1
            if run in MAIN and law.startswith("FLOOR1/") and c["reading"] in ("form", "both"):
                self.pc6[law, c["y_loose_max"]] += 1
            if not screened:
                continue
            passed_here.add("claimed" if c["reading"] in CLAIMED else "reported")
            if run == OUTSIDE:
                self.outside.append({"start": start, "law": law, "s": c["s"], "X": c["X"], "Y": c["Y"],
                                     "counts": [rates[k] for k in ("q1", "q0", "qY")]})
                continue
            self.passed[id_of(run, r, c)] = {
                "law": law, "start": start, "xform": c["xform"], "yform": c["yform"],
                "rates": rates, "failing knot": bool(r["knot_test"]["n_fails"]),
                "made questions": c["made_questions"], "meet": c["meet"],
                "outcome round": c["round_met"]}
        for kind in passed_here:
            cell["growths with " + kind + " screen pass"] += 1
            cell["positive start weights " + kind] += self.starts[start]["labelled"]


def validate_membership(audit, expected, all_ids):
    for run, intended in expected.items():
        assert audit.seen[run] == intended, (
            run, sorted(intended - audit.seen[run])[:1], sorted(audit.seen[run] - intended)[:1])
    assert all(start in all_ids[30:120] for start, law in audit.seen[OUTSIDE])
    assert audit.seen["R1d"].isdisjoint(audit.seen[OUTSIDE])
    return {"runs matched to frozen census order and documented run sizes": list(expected),
            "outside prefix, distinct starts": len({s for s, _ in audit.seen[OUTSIDE]}),
            "outside prefix, rows": len(audit.seen[OUTSIDE]),
            "not in retained files out of the full last run of 2520":
                len(all_ids[:120]) * 21 - len(audit.seen["R1d"]) - len(audit.seen[OUTSIDE])}


def confirmation_rows(audit, records):
    multiplicity = Counter(family(k[0], k[-1]) for k in audit.passed)
    rows = []
    overlap = []
    seen = set()
    for c in records:
        run = c["run"]
        key = id_of(run, c, c)
        seen.add(key)
        initial = audit.passed[key]
        f = family(run, c["reading"])
        alpha = .01 / multiplicity[f]
        rates = c["rates1000"]
        assert initial["rates"] == c["rates100"]
        assert all(rates["n" + a] == 1000 for a in ("1", "0", "Y", "M", "T"))
        ps = contrasts(rates, ("0", "Y", "M", "T"))
        worst = max(ps[a] for a in ("0", "Y", "T"))
        confirm = worst <= alpha
        joining = confirm and ps["M"] <= alpha
        need = confirm and rates["q0"] == rates["qT"] == 0
        assert confirm == c["confirmation"]["confirmed"]
        assert initial["failing knot"] == c["growth_has_failing_knot"]
        assert all(math.isclose(c["confirmation"]["p_vs_" + label], ps[a], rel_tol=1e-10, abs_tol=1e-305)
                   for label, a in (("Ybarred", "0"), ("Yown", "Y"), ("masked", "M"), ("fully_masked", "T")))
        assert c["made_questions"] == initial["made questions"]
        row = {"run": run, "family": list(f), "reading": c["reading"], "start": initial["start"],
               "law": initial["law"], "seed": c["seed"], "s": c["s"], "X": c["X"], "Y": c["Y"],
               "X form": initial["xform"]["key"], "Y form": initial["yform"],
               "initial meeting and outcome rounds": [initial["meet"], initial["outcome round"]],
               "screen sample size per arm": initial["rates"]["n1"],
               "screen counts q1 q0 qY": [initial["rates"][k] for k in ("q1", "q0", "qY")],
               "confirmation counts q1 q0 qY qM qT": [rates["q" + a] for a in ("1", "0", "Y", "M", "T")],
               "meeting counts": rates["meetings"], "stopped": rates["stopped"], "p by control": ps,
               "largest p over three defining contrasts": worst, "registered threshold": alpha,
               "confirmed": confirm, "through joining": joining, "needs the meeting by the registered rule": need,
               "growth has failing knot": initial["failing knot"], "link answers recorded": c["made_questions"]}
        rows.append(row)
        if run == "R6":
            pairkey = c["seed"], c["s"], tuple(c["X"]), tuple(c["Y"])
            tested = {r: audit.repeated[r, pairkey] for r in ("R1a", "R1b", "R6")
                      if (r, pairkey) in audit.repeated}
            overlap.append({"seed": c["seed"], "reading": c["reading"], "pair selected in": tested,
                            "main growth on disk": (c["start"], c["law"]) in
                              audit.seen["R1a"].union(audit.seen["R1b"])})
    assert seen == set(audit.passed)
    return rows, overlap


def sensitivity(rows, all_screens):
    claimed = [r for r in rows if r["family"][1] == "claimed"]
    def count(rule):
        return sum(r["largest p over three defining contrasts"] <= rule(r) for r in claimed)
    cases = {r["law"]: sorted({v["Y form"]["key"] for v in claimed
                               if v["law"] == r["law"] and v["confirmed"]}) for r in claimed}
    grouped = defaultdict(set)
    for r in claimed:
        if r["confirmed"] and not r["growth has failing knot"]:
            grouped[r["law"], r["X form"]].add(r["Y form"]["key"])
    n_raw = sum(n for (run, rd, passed), n in all_screens.items() if run != OUTSIDE and rd in CLAIMED)
    return {"claimed screens main, follow-up": dict(Counter(r["family"][0] for r in claimed)),
            "claimed screening pairs": len(claimed),
            "confirmed, registered": sum(r["confirmed"] for r in claimed),
            "through joining": sum(r["through joining"] for r in claimed),
            "needs the meeting by the registered rule": sum(r["needs the meeting by the registered rule"] for r in claimed),
            "distinct growth seeds": len({r["seed"] for r in claimed}),
            "distinct starts": len({r["start"] for r in claimed}),
            "full mask still meets, range out of 1000":
                [min(r["meeting counts"]["BT"] for r in claimed), max(r["meeting counts"]["BT"] for r in claimed)],
            "all claimed cases, one family at .01": count(lambda r: .01 / len(claimed)),
            "claimed cases under one .01 family including the reported screens": count(lambda r: .01 / len(rows)),
            "fixed .005 for each of the two claimed families":
                count(lambda r: r["registered threshold"] / 2),
            "separate .01 pooled Bonferroni over every individual defining contrast (stronger question)":
                count(lambda r: .01 / (3 * len(claimed))),
            "claimed raw screen occurrences, counting repeated follow-up cases separately": n_raw,
            "pooled Bonferroni over all claimed raw screen occurrences without using the fresh screen discount":
                count(lambda r: .01 / n_raw),
            "largest three-control p among the claimed cases":
                max(r["largest p over three defining contrasts"] for r in claimed),
            "separate one-sided 95 percent upper rate after 0 of 1000": 1 - .05 ** (1 / 1000),
            "Y forms per law among confirmations": cases,
            "number of groups by law and X form": len(grouped),
            "groups with two or more confirmed Y forms": sum(len(v) >= 2 for v in grouped.values()),
            "confirmed cases where a Y member has more than one loose distinction":
                sum(any(h + k > 1 for h, k in r["Y form"]["hk"]) for r in claimed if r["confirmed"])}


def upper_with_unknown(n, k):
    """Fixed-prefix upper rate if all k unread outcomes are hits; Chernoff bound."""
    if k == 0:
        return 1 - .05 ** (1 / n)
    q = k / n
    lo, hi = q, 1.0
    for _ in range(60):
        p = (lo + hi) / 2
        divergence = q * math.log(q / p) + (1 - q) * math.log((1 - q) / (1 - p))
        if n * divergence < -math.log(.05):
            lo = p
        else:
            hi = p
    return hi


def zero_bounds(starts, parity, audit):
    output = {}
    for run in MAIN:
        rule = "nae" if run in ("R1c", "R1d") else "parity"
        population = [v for v in starts.values() if rule == "nae" or not v["set_aside_parity"]]
        factor = max(x["labelled"] for x in population) * len(population) / sum(x["labelled"] for x in population)
        n = PREFIX[run]
        output[run] = {"starts in the retained prefix": n, "population weight factor": factor,
                       "registered unweighted 3/N": 3 / n, "population labelled 3/N times factor": 3 * factor / n}
    by_missing = Counter()
    for (run, law, size), cell in audit.cells.items():
        if run == "R1a" and cell["unread"]:
            by_missing[law] += cell["unread"]
    n = PREFIX["R1a"]
    factor = output["R1a"]["population weight factor"]
    missing = {}
    for law, k in by_missing.items():
        positions = sorted((parity.index(i) + 1, i) for i in audit.omitted["R1a", law])
        before = positions[0][0] - 1
        missing[law] = {"unread growths counted as possible hits": k,
                        "unread one-based positions and starts": positions,
                        "completed prefix preceding first omission": before,
                        "census 3/N using uninterrupted prefix": 3 / before,
                        "labelled 3/N times population factor using uninterrupted prefix": 3 * factor / before,
                        "conservative census upper rate on fixed 836": upper_with_unknown(n, k),
                        "conservative labelled upper rate on fixed 836": factor * upper_with_unknown(n, k)}
    output["unread cases in the fixed 836-start minimum prefix"] = missing
    return output


def pair_weight_swap(audit, parity):
    common = set(parity[:500])
    rates = {"holder": Counter(), "take by take": Counter(), "both observed": Counter()}
    for (run, start, law), has_pair in audit.pairs_by_weight.items():
        if run != "R2" or start not in common:
            continue
        rates["holder"]["read"] += 1
        rates["holder"]["with pair"] += has_pair
        source = "R1a" if "/MET/" in law else "R1b"
        other = audit.pairs_by_weight.get((source, start, law))
        if other is not None:
            rates["take by take"]["read"] += 1
            rates["take by take"]["with pair"] += other
            rates["both observed"]["matched"] += 1
            rates["both observed"]["with pair under holder"] += has_pair
    return rates


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--time-rows", type=int, help="time this prefix of each growth record file")
    args = parser.parse_args()
    starts, all_ids, parity, stored = hierarchy()
    documents = {name: read(DATA / (name + ".json"))["cases"] for name in ("R3", "Rcond")}
    records = documents["R3"] + documents["Rcond"]
    audit = Audit(starts, {r["seed"] for r in records if r["run"] == "R6"})
    controls = audit_controls()
    for run in (*MAIN, *FOLLOW, OUTSIDE):
        audit.scan(run, args.time_rows)
    print(json.dumps({"rows timed": {k: v["rows"] for k, v in audit.counts.items()},
                      "seconds per file": audit.elapsed,
                      "peak resident KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}, sort_keys=True))
    if args.time_rows:
        return
    expected = expected_jobs(starts, all_ids, parity, stored)
    membership = validate_membership(audit, expected, all_ids)
    rows, overlap = confirmation_rows(audit, records)
    screens = [{"run": r, "reading": k, "screen passes": passed, "count": n}
               for (r, k, passed), n in sorted(audit.screens.items())]
    cells = [{"run": r, "law": law, "start size": size, **counts}
             for (r, law, size), counts in sorted(audit.cells.items())]
    bound_table = zero_bounds(starts, parity, audit)
    contract = read(TRIAL / "contract.json")
    frozen_inputs = dict(contract["data_files"])
    for item in ("claim", "preregistration", "definitions"):
        frozen_inputs[contract[item]] = contract[item + "_sha256"]
    assert all(sha256((ROOT / path).read_bytes()).hexdigest() == digest
               for path, digest in frozen_inputs.items())
    out = {
        "sources": {f.name: sha256(f.read_bytes()).hexdigest() for f in
                    [*(DATA / (n + ".jsonl.gz") for n in (*MAIN, *FOLLOW, OUTSIDE)),
                     *(DATA / n for n in ("R3.json", "Rcond.json", "controls_R0b.json")),
                     ROOT / "research" / EPIC / "definitions_c.md",
                     ROOT / "research" / TICKET / "preregistration.md"]},
        "freeze": {"commit": "72dcd9c23efe11d94faeb1acf50d9e44650590c0",
                   "time Pacific": "2026-11-25 01:04:52", "results commit": "542405e68c7bf57cff954b5dddd0d4842fea4edf",
                   "current inputs checked against contract": frozen_inputs,
                   "rules": ["definitions_c.md section 4.4", "preregistration.md, The conditional runs"]},
        "runs": RUN_DESCRIPTIONS, "counts from raw growth and confirmation records": sensitivity(rows, audit.screens),
        "confirmation rows": rows, "follow-up every-pair screen vs main": overlap,
        "run membership": membership, "run totals": audit.counts, "screens": screens,
        "planted, machinery and negative controls": controls, "outside-prefix screens passing": audit.outside,
        "rates": {"zero bounds for laws with zero observed passes": bound_table,
                  "by run, law and start size": cells, "holder comparison, first 500 starts": pair_weight_swap(audit, parity)},
        "loose distinctions on the second part in the registered form cases": [
            {"law": law, "most loose on one member": maximum, "cases": count}
            for (law, maximum), count in sorted(audit.pc6.items())]}
    (HERE / "c_counts.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
