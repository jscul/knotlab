"""Recount the saved records of the search for a meeting through made knots.

Run from any directory with the repository environment. --pilot applies the same
readings to a systematic sample before the full run. Neither mode runs growth.
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
import time
from collections import Counter, defaultdict
from itertools import combinations, permutations
from pathlib import Path

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET = "WHAT-A-BIRTH-CARRIES-20261125-001B"
ART = ROOT / "artifacts" / TICKET / (TICKET + "-E001_link_through_a_made_knot")
PLAN = ROOT / "research" / TICKET
ORDINARY = ("1a", "1b", "1c", "P1", "U1", "M2", "C0", "P2_x10", "P2_x100")


def json_file(path):
    return json.loads(path.read_text())


def rows(run):
    with gzip.open(ART / ("run" + run + ".jsonl.gz"), "rt") as stream:
        for line in stream:
            yield json.loads(line)


def course_key(course):
    if course is None:
        return None
    return (tuple(course["labels"]), tuple(sorted(map(tuple, course["edges"]))))


def last_course_round(key):
    if key is None:
        return None
    final = set()
    for label in key[0]:
        xs = label.split("|")
        if xs[0] == "K":
            final.add(int(xs[1]) + len(xs[4].split(",")) - 1)
    if len(final) != 1:
        raise ValueError("Round histories disagree")
    return final.pop()


class Courses:
    """Classify the printed courses exactly, retaining the direction of descent."""

    def __init__(self):
        self.by_numbering = {}
        self.by_signature = defaultdict(list)
        self.number = 0

    def classify(self, key):
        if key is None:
            return -1
        if key in self.by_numbering:
            return self.by_numbering[key]
        labels, ties = key
        signature = (tuple(sorted(Counter(labels).items())),
                     tuple(sorted(Counter(t[2] for t in ties).items())))
        graph = nx.DiGraph()
        graph.add_nodes_from((i, {"label": lab}) for i, lab in enumerate(labels))
        graph.add_edges_from((u, v, {"kind": kind}) for u, v, kind in ties)
        for index, previous in self.by_signature[signature]:
            if nx.is_isomorphic(graph, previous,
                                node_match=lambda a, b: a["label"] == b["label"],
                                edge_match=lambda a, b: a["kind"] == b["kind"]):
                break
        else:
            index = self.number
            self.number += 1
            self.by_signature[signature].append((index, graph))
        self.by_numbering[key] = index
        return index


def subset_counts(pair):
    record = pair["subsets"]
    subs = record["subsets"]
    member = frozenset(pair["Y"])
    actual = {frozenset(row["A"]) for row in subs}
    sizes = range(len(member) + 1) if len(member) <= 4 else (0, len(member) - 1, len(member))
    expected = {frozenset(s) for n in sizes for s in combinations(member, n)}
    assert len(subs) == len(actual) and actual == expected
    classes = {s["course_class"] for s in subs}
    c = Counter(subsets=len(subs))
    c["pairs with a sampled roster larger than four"] = len(member) > 4
    c["subset course classes " + str(len(classes))] = 1
    c["m reported " + str(record["m"]["m"])] = 1
    assert len(classes) == record["n_classes"]
    c["proper subsets whose link includes a start knot"] = sum(
        bool(frozenset(s["A"]) != member and s["link_verdict"] == "through a start knot") for s in subs)
    c["subset knot-bound stops"] = sum(s["stop"] == "knots" for s in subs)
    c["subset guard stops"] = sum(s["stop"] == "guard" for s in subs)
    which = how = 0
    for a, b in combinations(subs, 2):
        na, nb = len(a["A"]), len(b["A"])
        equal_number = na == nb
        both_meet = a["meeting_round"] is not None and b["meeting_round"] is not None
        both_strict = all(x["link_verdict"] == "only through made knots" for x in (a, b))
        distinct_courses = a["course_class"] != b["course_class"]
        if equal_number:
            c["equal-size distinct subset comparisons"] += 1
            if both_meet:
                c["equal-size distinct subset comparisons both meet"] += 1
                which += distinct_courses
        if min(na, nb) > 0 and not equal_number and both_strict:
            c["unequal positive sizes both meet strictly"] += 1
            how += distinct_courses
    assert len(record["how_many"]) == how and len(record["which_at_equal_number"]) == which
    c["Which at equal number"] = which
    c["pairs with a positive Which at equal number"] = int(which > 0)
    c["How many through made knots"] = how
    for metric in ("equal-size distinct subset comparisons both meet", "unequal positive sizes both meet strictly"):
        c["pairs with opportunity for " + metric] = int(c[metric] > 0)
    proper = [s for s in subs if frozenset(s["A"]) != member]
    full = next(s for s in subs if frozenset(s["A"]) == member)
    if proper and all(s["meeting_round"] is None for s in proper) and full["meeting_round"] is not None:
        c["only the full subset meets"] = 1
        if len({s["course_class"] for s in proper}) == 1 and full["course_class"] != proper[0]["course_class"]:
            c["subset course partition equals whether the meeting occurs"] = 1
    return c


def qualified_test(test):
    return isinstance(test, dict) and test["n_fail"] == test["n_disagree"] == test["n_untested"] == 0


def pair_counts(row, pair, courses):
    links = pair["linking"]
    strict = bool(links) and all(k["made"] > 0 for k in links)
    through_start = any(k["made"] == 0 for k in links)
    assert strict == pair["strict"]
    c = Counter(meetings=1, strict=int(strict))
    c["through a start knot"] = int(through_start)
    c["empty linking set"] = int(not links)
    c["whole run passes on this strict pair"] = int(strict and qualified_test(row["knot_test_A"]))
    c["barred run guard stops"] += int(row_guard(pair["barred_run"]))
    if not strict:
        return c
    c["strict pair with a start member"] = min(pair["X"] + pair["Y"]) < len(row["stars"])
    c["strict link count " + str(len(links))] = 1
    c["both descendants in a single linking knot's holder list"] = any(
        {"X only", "Y only"} <= {hold[2] for d in k["linking_distinctions"] for hold in d["holders"]}
        for k in links)
    start_holds = False
    for k in links:
        c["linking knot made in round " + str(k["made"])] += 1
        assert k["ancestry"] and min(anc[1] for anc in k["ancestry"]) == 0
        for d in k["linking_distinctions"]:
            holders = d["holders"]
            assert min(h[1] for h in holders) == d["first_holder_round"]
            assert any(h[0] == k["knot"] and h[1] == k["made"] for h in holders)
            start_holds |= d["first_holder_round"] == 0
    c["start knot holds a linking distinction"] = int(start_holds)
    c["start knot holds a linking distinction, unbarred knot test passes"] = int(start_holds and qualified_test(row["knot_test_A"]))
    assert start_holds == pair["start_knot_holds_linking_distinction"]
    c["ancestral from per-knot classification"] = any(k["ancestral_made"] for k in links)
    c["ancestral every member from per-knot classification"] = any(k["every_member_form"] for k in links)
    assert bool(c["ancestral from per-knot classification"]) == pair["ancestral"]
    assert bool(c["ancestral every member from per-knot classification"]) == pair["ancestral_every_member"]
    for r in pair.get("lasting", {}).get("reruns", []):
        c["lasting run guard stops"] += int(row_guard(r))
    recv = pair.get("checks", {}).get("symmetry_exchanging_X_Y_fixing_linking_knots", {})
    c["registered symmetry " + str(recv.get("answer"))] = 1
    c["unequal part sizes"] = len(pair["X"]) != len(pair["Y"])
    c["strict pair size " + str(len(pair["X"])) + " / " + str(len(pair["Y"]))] = 1
    a, b = course_key(pair["course_A"]), course_key(pair["course_barred"])
    differs = courses.classify(a) != courses.classify(b)
    assert differs == pair["course_differs"]
    c["course differs"] = int(differs)
    c.update(subset_counts(pair))
    if qualified_test(row["knot_test_A"]):
        c["Which at equal number on passing unbarred runs"] = c["Which at equal number"]
        c["pairs with positive Which on passing unbarred runs"] = c["pairs with a positive Which at equal number"]
    if not differs:
        return c
    c["strict course differs, round " + str(last_course_round(a))] = 1
    assert last_course_round(a) == pair["course_first_differs_round"]
    c["no barred meeting on differing pair"] = int(pair["barred_run"]["meeting_round"] is None)
    att = pair.get("attribution") or {}
    tags = [part[1] for part in att.get("part", [])]
    attributed = "Y only" in tags
    assert attributed == pair["attribution_accepted"]
    c["first differing entry includes a knot from Y only"] = int(attributed)
    c["attribution class agrees in reverse order"] = att.get("class") == att.get("class_in_other_order")
    data = pair.get("y_side_knots_first_differing_demand") or {}
    partners = data.get("y_side", [])
    own_join = (len(partners) == 1 and partners[0]["kind"] == "join"
                and partners[0]["descent"] == "Y only" and partners[0]["run"] == "run A"
                and set(partners[0]["parents"]) == set(pair["Y"]))
    c["sole extra demand partner is the two-member Y join"] = int(own_join and len(pair["Y"]) == 2)
    if data:
        vals = data["value_barred"][0], data["value_A"][0]
        value_pair = str(vals[0]) + " / " + str(vals[1])
        c["demand with Y barred / usable " + value_pair] = 1
        if isinstance(pair.get("knot_test_barred"), dict):
            c["tested pair demand with Y barred / usable " + value_pair] = 1
    if own_join and att.get("kind") == "demand" and len(tags) == 1 and attributed:
        # When a proper subset has no meeting, its X join cannot have a Y-only
        # demand partner in that round. The recorded composite entry itself
        # contains that tag. The equal-course proper subsets and the distinct
        # full subset then admit a one-entry separator independent of the m flag.
        c["one demand entry separates the saved subset course classes by its Y-only partner"] = int(
            bool(c["subset course partition equals whether the meeting occurs"]) and
            "Y only" in att["value_B"][1] and "Y only" not in att["value_A"][1]
            and att["round"] == pair["meeting_round"] and att["step"] == 6)
    test = pair.get("knot_test_barred")
    c["differing pair barred test present"] = isinstance(test, dict)
    c["registered dependence found"] = int(attributed and qualified_test(row["knot_test_A"]) and qualified_test(test))
    c["registered dependence undecided for missing barred test"] = int(
        attributed and qualified_test(row["knot_test_A"]) and not isinstance(test, dict))
    if "lasting" in pair:
        t = pair["lasting"]["t_d"]
        diffs = pair["lasting"]["rosters_differ"]
        c["lasting rosters differ at both following rounds"] = all(diffs.get(str(i)) for i in (t + 1, t + 2))
    return c


def row_guard(row):
    return bool(row.get("guard")) or row.get("stop") == "guard"


def test_counts(c, stage, test):
    if isinstance(test, dict):
        for key in ("verdicts", "n_fail", "n_untested", "n_disagree"):
            c[stage + " " + key] += test[key]


def item_counts(row, courses):
    c = Counter(items=1)
    c["unbarred guard stops"] = int(row_guard(row))
    c["unbarred stop " + str(row["stop"])] = 1
    c["unbarred rounds read " + str(row["rounds_read"])] = 1
    test_counts(c, "unbarred", row["knot_test_A"])
    partition = defaultdict(set)
    differing = []
    tested = set()
    barred_runs = set()
    sources = set()
    for pair in row["pairs"]:
        key = (pair["X_part"], pair["Y_part"])
        s = str(pair["s"])
        parts = row["s"][s]["parts"]
        assert pair["X"] == parts[key[0]] and pair["Y"] == parts[key[1]]
        assert key not in partition[s]
        partition[s].add(key)
        c.update(pair_counts(row, pair, courses))
        if pair["strict"]:
            sources.update(k["knot"] for k in pair["linking"])
        if pair["strict"] and pair["course_differs"]:
            position = (pair["s"], min(pair["X"]), min(pair["Y"]))
            differing.append(position)
            if isinstance(pair.get("knot_test_barred"), dict):
                tested.add(position)
                barred_runs.add((pair["s"],tuple(pair["Y"])))
        test_counts(c, "barred", pair.get("knot_test_barred"))
        for test in pair.get("knot_test_lasting") or []:
            test_counts(c, "lasting", test)
    assert tested == set(sorted(differing)[:8])
    c["distinct tested barred runs within items"] = len(barred_runs)
    c["distinct strict linking knots within items"] = len(sources)
    for s, r in row["s"].items():
        if "n_ordered_pairs" not in r:
            continue
        absent = set(map(tuple, r["no_meeting_pairs"]))
        assert len(absent) == len(r["no_meeting_pairs"]) and not (absent & partition[s])
        eligible = absent | partition[s]
        assert len(eligible) == r["n_ordered_pairs"]
        assert all((b, a) in eligible for a, b in eligible)
        c["ordered pairs"] += len(absent) + len(partition[s])
        c["no meeting"] += len(absent)
    return c


def ordinary(pilot):
    family = json_file(PLAN / "family.json")["search"]
    families = {law["id"]: law for law in family}
    groups = defaultdict(Counter)
    search = defaultdict(Counter)
    controls = defaultdict(Counter)
    cases = defaultdict(Counter)
    planted = {}
    completed = {}
    for run in ORDINARY:
        take = 0
        for i, row in enumerate(rows(run)):
            if pilot and i % 19:
                continue
            take += 1
            if row["law_id"] == "planted":
                planted[row["id"]] = {
                    k: {"linking rounds": [x["made"] for x in v["linking"]],
                        "meeting": v["meeting"], "guard": v.get("guard"),
                        "stop": v.get("stop")}
                    for k, v in row["runs"].items()}
                continue
            # Isomorphic courses need only be identified within a pair here.
            # Reuse the exact classifications within an item.
            c = item_counts(row, Courses())
            key = row["law_id"]
            kl = row["law"]["knot_law"]
            if run in ("1a", "1b", "1c"):
                f = families[key]
                assert all(f[k] == row["law"][k] for k in ("ration","treatment","take"))
                search[key + " " + kl].update(c)
                if run == "1a" and f["ration"] in ("ORD", "FLOOR1", "CAP-3") and f["treatment"] != "SHORT-BY":
                    groups["nine recorded laws with sole candidate"].update(c)
                if key in ("L02","L05","L10"):
                    cases[run + " " + key + " " + kl + " " + row["start"]].update(c)
            else:
                controls[run + " " + key + " " + kl].update(c)
                if run == "U1":
                    cases[run + " " + key + " " + kl + " " + row["start"]].update(c)
            groups[run].update(c)
            if run == "C0":
                groups[row["id"].split("|")[0]].update(c)
        completed[run] = take
    if not pilot:
        assert len(search) == len(families) * 2
    minimal = {}
    order = json_file(PLAN / "family.json")["values_order"]
    def cost(key):
        val = families[key]["cost"]
        return (val["holder_steps"], val["record_steps"], int(val["whole_roster"]),
                order.index(val["values_at_one_birth"]), val["new_rules"])
    for kl in ("parity","nae"):
        out = {}
        for desc, column in (("link","strict"),("ancestral","ancestral from per-knot classification"),
                             ("dependence","registered dependence found")):
            positive = sorted(k for k in families if search.get(k + " " + kl, {}).get(column, 0))
            lower = lambda a, b: cost(a) != cost(b) and all(x <= y for x,y in zip(cost(a),cost(b)))
            out[desc] = {"found":positive, "minimal":[k for k in positive if not any(lower(j,k) for j in positive)]}
        minimal[kl] = out
    decisions = {}
    for key, c in search.items():
        decisions[key] = {"link": ("found" if c["strict"] else "none"),
                          "ancestral": ("found" if c["ancestral from per-knot classification"] else "none"),
                          "dependence": ("found" if c["registered dependence found"] else
                                         "undecided" if c["registered dependence undecided for missing barred test"] else "none")}
    return {"items": completed, "decisions by search law and knot law":decisions, "totals":groups, "each search law and knot law":search,
            "each control and knot law":controls, "by start for the main contrasts":cases,
            "minimal among the listed":minimal,"planted control":planted}


def renaming(pilot):
    registry = Courses()
    signatures = defaultdict(dict)
    prevalence = Counter()
    for i, row in enumerate(rows("N2")):
        name = row["renaming"]
        if pilot and i % 19 and name not in ("registered", "n000"):
            continue
        ms = Counter()
        for p in row["pairs"]:
            a, b = course_key(p["course_A"]), course_key(p["course_barred"])
            classes = registry.classify(a), registry.classify(b)
            assert p["course_differs"] == (classes[0] != classes[1])
            ms[(p["s"],p["link_verdict"],p["ancestral"],p["ancestral_every_member"],
                p["meeting_round"],p["course_differs"],p["dependence"],classes)] += 1
        nm = tuple(sorted(row["no_meeting_pairs_by_s"].items()))
        key = (row["law_id"], row["start"], row["law_name"].split("/")[-1])
        assert name not in signatures[key]
        signatures[key][name] = (ms,nm,row["parts_by_s"],row["structure_invariants"],row["rounds_read"],row["stop"])
        if name not in ("registered","n000"):
            prevalence["renamings"] += 1
            prevalence["no meeting pairs with no saved course"] += sum(x[1] for x in nm)
            prevalence["meeting pairs with courses"] += len(row["pairs"])
            prevalence["renamings with a meeting"] += bool(row["pairs"])
            prevalence["renamings with at least one strict link"] += any(p["strict"] for p in row["pairs"])
            prevalence["renamings with at least one differing attributed strict pair"] += any(p["dependence"] for p in row["pairs"])
            for p in row["pairs"]:
                short = last_course_round(course_key(p["course_A"])) < row["rounds_read"]
                prevalence["meeting pairs with saved course ending early relative to unbarred run"] += short
                if p["dependence"]:
                    prevalence["differing attributed strict pairs without knot tests"] += 1
                    prevalence["differing attributed strict pairs ending before unbarred last round"] += short
    disp = Counter()
    for group in signatures.values():
        name = "registered" if "registered" in group else "n000"
        ref = group[name]
        for n, candidate in group.items():
            if n == name:
                continue
            disp["different stored course and verdict multisets"] += int(candidate[:3] != ref[:3])
            disp["different stored whole-structure invariants or stop"] += int(candidate[3:] != ref[3:])
    return {"reference groups": len(signatures), "rows": sum(map(len,signatures.values())),
            "exposure over nonreference rows":prevalence,"disagreements":disp,
            "isomorphism classes of saved courses":registry.number,
            "note":"The records store per-pair courses only for pairs with a meeting. A differing course is saved at its first difference. The renamings ran no knot tests."}


def gate(pilot):
    checks = Counter()
    cases = set()
    for p in sorted(ART.glob("G_engine_*.jsonl")):
        with p.open() as stream:
            for i, line in enumerate(stream):
                if pilot and i % 19:
                    continue
                o = json.loads(line)
                assert o["case"] not in cases
                cases.add(o["case"])
                checks["comparison records"] += 1
                checks["empty difference lists"] += not o["diffs"]
    g = json_file(ART / "G_rest.json")
    expected = [s for s in (PLAN / "gate_listing_b.txt").read_text().splitlines() if s.startswith(" ")]
    got = [s for s in g["gate_listing"]["got"] if s.startswith(" ")]
    checks["body lines"] = len(got)
    checks["body lines agree"] = got == expected
    checks["attribution fixtures compare exactly"] = sum(
        x["expected"] == x["got"] for x in g["attribution_records"])
    return checks


def extra_start():
    stars = json_file(PLAN / "starts.json")["extra"]["stars"]
    held = Counter(tuple(i for i, k in enumerate(stars) if d in k) for d in set().union(*map(set,stars)))
    compatible = [p for p in permutations(range(len(stars)))
                  if Counter({tuple(sorted(p[i] for i in s)): n for s,n in held.items()}) == held]
    return {"knot permutations preserving holder counts":len(compatible),
            "compatible renamings per permitted knot permutation":math.prod(math.factorial(n) for n in held.values()),
            "loose distinctions per knot":[held[(i,)] for i in range(len(stars))]}


def reported_symmetry(ordinary_counts):
    counts = Counter()
    for row in json_file(ART / "check_c_fixing_start_knots.json"):
        run = "U1" if row["start"].endswith("+1+2") else "1a"
        key = " ".join((run, row["law"], row["knot_law"], row["start"]))
        raw = ordinary_counts["by start for the main contrasts"].get(key, {})
        got = row["counts"]
        if raw and got["strict"] != raw.get("strict",0):
            raise ValueError(key)
        for verdict in ("yes", "no"):
            counts[run + " " + row["law"] + " fixed-start-knot exchange " + verdict] += got.get(
                "fixing start knots too: " + verdict, 0)
    return {"per-pair maps available":False, "counts in supplemental check":counts,
            "scope":"Supplement covers only the four usual rings and the extra ring, both knot laws, the waiting and uncapped owing laws. It fixes each start knot. Individual start distinctions were not specified as fixed."}


def comparison_summary(row):
    # The archive gives no complete birth records for this comparison.
    pairs = []
    for p in row["pairs"]:
        pairs.append((p["s"],p["X"],p["Y"],p["meeting_round"],p["linking"],
                      p.get("course_A"),p.get("course_barred"),p.get("course_A_invariant"),
                      p.get("course_barred_invariant"),p.get("attribution"),p.get("subsets")))
    return (row["knots"],row["rounds_read"],row["stop"],row["peaks"],row["s"],pairs)


def plain_control(pilot):
    reference = {}
    control = {}
    extra = "Ring(5,3)+1"
    for run, table, wanted in (("1a",reference,"PARENT-OWING"),("P1",control,"PARENT-OWING-PLAIN")):
        for row in rows(run):
            if row["law"]["ration"] != wanted or row["start"] not in ("Ring(5,3)", extra, "D2(5,3)","Ring(7,3)"):
                continue
            if pilot and (row["start"] != extra or row["law"]["treatment"] != "CANCEL-OFFSHOOT"):
                continue
            key = (row["start"],row["law"]["treatment"],row["law"]["knot_law"])
            table[key] = comparison_summary(row)
    assert reference.keys() == control.keys()
    return {"matched usual ring items":len(reference),
            "identical saved counts, parts, linking records, both courses, attribution and subset summaries":
                sum(reference[k] == control[k] for k in reference),
            "scope":"A different fresh count is possible only on a taking offshoot with owing at most one. These saved readings need not reveal every intermediate birth."}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot",action="store_true")
    args=parser.parse_args()
    timings={}
    out={}
    for key, fn in (("gate",gate),("stored pair recount",ordinary),("renamings",renaming),("plain owing control",plain_control)):
        t=time.monotonic()
        out[key]=fn(args.pilot)
        timings[key]=round(time.monotonic()-t,3)
    out["extra ring"] = extra_start()
    out["supplemental symmetry"] = reported_symmetry(out["stored pair recount"])
    out["chronology"] = {
        "before the first gate": "The deviations record labels items 1 through 30 as implementation readings made before the first gate.",
        "after the main sole-candidate run": "Item 31 changed the not-all-equal method for the full barred/control checks after the timing sample. Item 32 applies the predeclared minimal-law rule for which laws to rename. Item 33 describes a discrepancy already seen.",
        "after all registered runs": "Item 34 added the start-knot-fixing exchange check. Item 35 records the skipped timing sample for the extra ring and empty guard runs. Item 36 explains the aggregate meeting count.",
        "unarchived reported output": "The first definitions section 3.1 and the second claim promise a separate trace and joint-birth count for each course. The saved course records contain labels and typed incidences, and no such separate outputs.",
    }
    out["scope"] = ("Counts are ordered pair readings. Reverse order, knot laws and numberings can repeat one mechanism. "
        "Course graphs are reclassified exactly. Per-knot ancestral classifications, proper subsets' course class "
        "numbers, first differing-entry records, and knot-test counts are read as stored. The per-subset raw courses, "
        "complete value histories, tested knot relations, and symmetry maps are absent from the pair rows.")
    if not args.pilot:
        (HERE / "b_counts.json").write_text(json.dumps(out,indent=2,sort_keys=True) + "\n")
    print(json.dumps({"pilot":args.pilot,"seconds":timings,"gate":out["gate"],
        "items":out["stored pair recount"]["items"],"renamings":out["renamings"]},indent=2))


if __name__ == "__main__":
    main()
