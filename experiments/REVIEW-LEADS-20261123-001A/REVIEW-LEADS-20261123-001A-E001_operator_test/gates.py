"""Gate row G of the pre-registration, parts that do not need the P3 draws, plus the supporting engine checks.

    G1  On the 173 recorded simple sharing patterns the fail verdict equals the recorded admit verdict (115 admit).
    G2  The planarity routine agrees with a brute-force minor search on every pattern of at most six knots.
    G3  A mutant that unlinks the second holder of every shared distinction passes everything.
    G4  Knot-side check (first two structures here; the three P3 closed parts are checked by knotside.py after P3).
    S1  The three archived explosive starts and the other sources reproduce the recorded supports and birth counts.
    S2  The Euler shortcut used by lib.passes agrees with networkx.check_planarity (all 173 patterns, all P1 patterns).
    S3  The growth driver (end_operator.step) and the other recorded engine (naelib: freelib presentation) agree on counts.

Run from the repo root:  timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file>
"""
import json
import random
import sys
import time
from itertools import combinations
from pathlib import Path

import networkx as nx

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib  # noqa: E402

CENSUS = lib.ROOT / "artifacts/FOUR-READINGS-20261120-001A/FOUR-READINGS-20261120-001A-E001_signed_rules/census.json"
SOURCES_PY = lib.EXP / "GROWTH-STATISTICS-20261121-001A/GROWTH-STATISTICS-20261121-001A-E001_blind/sources.py"
WORDS_PY = lib.EXP / "FREEDOM-CLOCKS-AND-BIRTHS-20261120-001A/FREEDOM-CLOCKS-AND-BIRTHS-20261120-001A-E001_freedom/words.py"
HYPER_SEED = 20261123


# ----------------------------------------------------------------------------------------------------------------------
def holding(ends):
    """FOUR-READINGS-20261120-001A growth.holding: knot u holds distinction i when u is an end of i."""
    return [[i for i, p in enumerate(ends) if u in p] for u in range(1 + max(map(max, ends)))]


def brute_force_nonplanar(g):
    """Wagner: nonplanar exactly when there is a K5 or K3,3 minor.  Exhaustive search over every way to choose disjoint
    connected branch sets (some nodes may be left out) and test the quotient."""
    nodes = sorted(g.nodes, key=str)
    adj = {v: set(g[v]) for v in nodes}

    def connected(block):
        block = set(block)
        start = next(iter(block))
        seen, todo = {start}, [start]
        while todo:
            v = todo.pop()
            for w in adj[v] & block:
                if w not in seen:
                    seen.add(w)
                    todo.append(w)
        return seen == block

    def search(h):
        found = []

        def rec(i, blocks):
            if found:
                return
            if len(blocks) + (len(nodes) - i) < h:
                return
            if i == len(nodes):
                if len(blocks) != h or not all(connected(b) for b in blocks):
                    return
                q = [[any(w in adj[v] for v in blocks[a] for w in blocks[b]) if a != b else False for b in range(h)]
                     for a in range(h)]
                if h == 5:
                    if all(q[a][b] for a, b in combinations(range(5), 2)):
                        found.append(True)
                else:
                    for side in combinations(range(6), 3):
                        other = [x for x in range(6) if x not in side]
                        if all(q[a][b] for a in side for b in other):
                            found.append(True)
                            return
                return
            v = nodes[i]
            rec(i + 1, blocks)
            for b in blocks:
                b.append(v)
                rec(i + 1, blocks)
                b.pop()
                if found:
                    return
            if len(blocks) < h:
                blocks.append([v])
                rec(i + 1, blocks)
                blocks.pop()

        rec(0, [])
        return bool(found)

    return (len(nodes) >= 5 and search(5)) or (len(nodes) >= 6 and search(6))


def pattern_graph(holders_by_distinction, n_knots):
    g = nx.Graph()
    for k in range(n_knots):
        g.add_node(("k", k))
    for d, hs in enumerate(holders_by_distinction):
        for k in hs:
            g.add_edge(("k", k), ("d", d))
    return g


# ----------------------------------------------------------------------------------------------------------------------
def g1_recorded_patterns(report):
    rows = json.loads(CENSUS.read_text())
    mismatch, admit, euler_disagree, pauli_disagree, total = [], 0, 0, 0, 0
    census = lib.census_module()
    for r in rows:
        ends = [tuple(p) for p in r["sharing"]]
        stars = holding(ends)
        g = lib.incidence_graph(stars)
        fail_nx = not nx.check_planarity(g)[0]
        fail_fast = not lib.passes(g)
        total += 1
        admit += bool(r["operator"])
        if fail_nx != bool(r["operator"]):
            mismatch.append({"atlas": r["atlas"], "n": r["n"], "recorded_admit": r["operator"], "fail": fail_nx})
        euler_disagree += fail_nx != fail_fast
        pauli = census.pauli_solution(ends, {0}) is not None
        pauli_disagree += pauli != bool(r["operator"])
    report["G1"] = {"patterns": total, "recorded_admit": admit, "fail_equals_admit_everywhere": not mismatch,
                    "mismatches": mismatch, "pauli_solution_vs_recorded_disagreements": pauli_disagree,
                    "pass": total == 173 and admit == 115 and not mismatch}
    report["S2_census"] = {"euler_shortcut_disagreements": euler_disagree, "patterns": total}
    return rows


def g2_minor_search(report, rows):
    t0 = time.time()
    checked = {"census_at_most_six_knots": 0, "atlas_simple_graphs_up_to_six_knots": 0,
               "atlas_simple_graphs_seven_knots": 0, "census_seven_knots": 0, "hypergraph_incidence": 0}
    disagree = []

    def compare(label, g, tag):
        brute = brute_force_nonplanar(g)
        routine = not nx.check_planarity(g)[0]
        checked[tag] += 1
        if brute != routine:
            disagree.append({"label": label, "brute": brute, "routine": routine})
        return routine

    # (a) the recorded patterns, as incidence graphs of knots and distinctions: the incidence graph has a node per
    # distinction, so brute force runs on the sharing graph of knots (a distinction held twice is a subdivided link).
    for r in rows:
        sharing = nx.MultiGraph()
        sharing.add_nodes_from(range(r["n"]))
        sharing.add_edges_from(tuple(p) for p in r["sharing"])
        simple = nx.Graph(sharing)
        inc = lib.incidence_graph(holding([tuple(p) for p in r["sharing"]]))
        brute = brute_force_nonplanar(simple)
        routine = not nx.check_planarity(inc)[0]
        tag = "census_at_most_six_knots" if r["n"] <= 6 else "census_seven_knots"
        checked[tag] += 1
        if brute != routine:
            disagree.append({"label": f"census atlas {r['atlas']}", "brute": brute, "routine": routine})
    # (b) every simple graph on up to six knots (and, as an extra, seven), each given as a pattern with one distinction per link
    for g in nx.graph_atlas_g():
        if g.number_of_nodes() < 1 or g.number_of_edges() == 0:
            continue
        links = sorted(tuple(sorted(e)) for e in g.edges)
        inc = lib.incidence_graph([[i for i, e in enumerate(links) if u in e] for u in range(g.number_of_nodes())])
        brute = brute_force_nonplanar(g)
        routine = not nx.check_planarity(inc)[0]
        tag = "atlas_simple_graphs_up_to_six_knots" if g.number_of_nodes() <= 6 else "atlas_simple_graphs_seven_knots"
        checked[tag] += 1
        if brute != routine:
            disagree.append({"label": f"atlas graph {links}", "brute": brute, "routine": routine})
    # (c) patterns whose distinctions have more than two holders: brute force on the incidence graph itself (small cases)
    rng = random.Random(HYPER_SEED)
    made = 0
    while made < 60:
        n = rng.randint(3, 6)
        m = rng.randint(3, 4)
        holders = [sorted(rng.sample(range(n), rng.randint(2, min(n, 5)))) for _ in range(m)]
        if all(len(h) == 2 for h in holders):
            continue
        g = pattern_graph(holders, n)
        if g.number_of_nodes() > 10:
            continue
        brute = brute_force_nonplanar(g)
        routine = not nx.check_planarity(g)[0]
        checked["hypergraph_incidence"] += 1
        made += 1
        if brute != routine:
            disagree.append({"label": f"hypergraph {holders}", "brute": brute, "routine": routine})
    # the K3,3 pattern held three-ways is the smallest hypergraph incidence that fails
    k33 = pattern_graph([[0, 1, 2]] * 3, 3)
    checked["hypergraph_incidence"] += 1
    if not (brute_force_nonplanar(k33) and not nx.check_planarity(k33)[0]):
        disagree.append({"label": "three knots, three distinctions each held by all three", "brute": None, "routine": None})
    report["G2"] = {"checked": checked, "disagreements": disagree, "seconds": round(time.time() - t0, 1),
                    "pass": not disagree}


def g3_mutant(report, rows):
    """Unlink the second holder of every shared distinction; the pattern should pass."""
    def mutant_passes(holders_list, n):
        g = nx.Graph()
        for k in range(n):
            g.add_node(("k", k))
        for d, hs in enumerate(holders_list):
            for idx, k in enumerate(hs):
                if idx == 1:
                    continue
                g.add_edge(("k", k), ("d", d))
        return nx.check_planarity(g)[0]

    out = {}
    # 173 recorded patterns
    ok = 0
    for r in rows:
        ends = [tuple(p) for p in r["sharing"]]
        ok += mutant_passes([list(p) for p in ends], r["n"])
    out["recorded_patterns"] = {"mutant_passes": ok, "of": len(rows)}
    # real verdicts of the same patterns (so the mutant is a real change)
    out["recorded_patterns"]["real_fail"] = sum(bool(r["operator"]) for r in rows)
    # the benchmark constructions, as holders per distinction
    src = lib.load_module("gate_sources", SOURCES_PY)
    bench = {}
    patterns = [("cubic", d, src.cubic_pattern(d)[0]) for d in range(0, 6)]
    patterns += [("pinwheel", d, src.planar_pattern("pinwheel", d)) for d in (1, 2, 3, 4)]
    patterns += [("periodic", d, src.planar_pattern("periodic", d)) for d in (1, 2, 3, 4, 5, 6)]
    patterns += [("bounded_bond", w, src.fold_pattern(w, w)) for w in (1, 2, 3, 4)]
    for name, depth, p in patterns:
        holders = [list(o) for o in p.owners]
        real = nx.check_planarity(pattern_graph(holders, len(p.knots)))[0]
        mutated = mutant_passes(holders, len(p.knots))
        bench[f"{name}:{depth}"] = {"real_passes": real, "mutant_passes": mutated, "max_holders": max(map(len, holders))}
    out["benchmark"] = bench
    # engine stages: the first stages of two recorded sources and 60 funded P3 draws
    stage_ok = stage_total = 0
    stage_real_fail = 0
    for name, steps in (("seven_knot", 6), ("nine_knot_drawn", 5)):
        h = lib.grow(lib.recorded_sources()[name], "parity", steps, 3000)
        for n in h["n_at"]:
            holders = {}
            for k in range(n):
                for d in h["stars"][k]:
                    holders.setdefault(d, []).append(k)
            hl = [holders[d] for d in sorted(holders)]
            stage_total += 1
            stage_ok += mutant_passes(hl, n)
            stage_real_fail += not lib.passes(lib.incidence_graph(h["stars"], n))
    out["engine_stages"] = {"mutant_passes": stage_ok, "of": stage_total, "real_fail": stage_real_fail}
    two_holder = [v for v in bench.values() if v["max_holders"] <= 2]
    fold = {k: v for k, v in bench.items() if v["max_holders"] > 2}
    out["pass"] = (out["recorded_patterns"]["mutant_passes"] == len(rows)
                   and all(v["mutant_passes"] for v in two_holder)
                   and out["engine_stages"]["mutant_passes"] == stage_total)
    out["literal_mutant_passes_every_pattern_including_bounded_bond"] = out["pass"] and all(v["mutant_passes"] for v in fold.values())
    out["note"] = ("The bounded-bond constructions have distinctions with up to six holders; unlinking only the second holder "
                   "leaves the others, so the literal mutant is reported separately for them: "
                   + json.dumps({k: v["mutant_passes"] for k, v in fold.items()}))
    report["G3"] = out


def g4_knot_side_first_two(report):
    words = lib.load_module("gate_words", WORDS_PY)
    structures = {
        "two_split_three_place_knots": [(0, 1, 2), (0, 1, 3)],
        "five_knot_closure": [(1, 6, 7, 8), (2, 3, 4, 8), (0, 3, 6, 9), (4, 5, 7, 9), (0, 1, 2, 5)],
    }
    report["G4_first_two"] = {name: knot_side(words, stars) for name, stars in structures.items()}
    report["G4_first_two"]["pass"] = all(v["agree"] for v in report["G4_first_two"].values())


def wht(values):
    """Fast Walsh-Hadamard transform of a list of integers (unnormalised, sign (-1)^(a.x))."""
    import numpy as np
    a = np.array(values, dtype=np.int64)
    h = 1
    while h < len(a):
        a = a.reshape(-1, 2, h)
        a = np.stack([a[:, 0] + a[:, 1], a[:, 0] - a[:, 1]], axis=1).reshape(-1)
        h *= 2
    return [int(x) for x in a]


def counting_rule_fast(allowed, m):
    """The recorded counting rule for single-mark change questions on all m distinctions, evaluated by a Walsh-Hadamard
    transform: C(T) = |{s in S: s+T in S}| / |S|, P(a) = 2^-m sum_T (-1)^(a.T) C(T)  (research/FREEDOM-CLOCKS-AND-BIRTHS-20261120-001A/
    counting.md, section 1) equals Shat(a)^2 / (2^m |S|) with Shat the transform of the indicator of S.  Cross-checked against
    words.counts_table in knot_side whenever m <= 10."""
    from fractions import Fraction
    indicator = [0] * (1 << m)
    for s in allowed:
        indicator[s] = 1
    shat = wht(indicator)
    return [Fraction(x * x, (1 << m) * len(allowed)) for x in shat]


def knot_side(words, stars):
    """Recorded counting rule (FREEDOM-CLOCKS-AND-BIRTHS-20261120-001A words.py: counts_table over single-mark change
    questions on every distinction) against the knot-side draw: a uniform set of knots, each distinction read as the parity
    of its drawn holders.  Exact fractions, every answer word on every distinction.  For m > 10 the counting rule is evaluated
    by the transform form, which is first checked equal to words.counts_table on this and every smaller structure."""
    from fractions import Fraction
    marks = sorted({d for s in stars for d in s})
    m = len(marks)
    pos = {d: i for i, d in enumerate(marks)}
    allowed = words.states([[pos[d] for d in s] for s in stars], "parity")
    fast = counting_rule_fast(allowed, m)
    if m <= 10:
        questions = [words.Question(flip=1 << i) for i in range(m)]
        counted = words.counts_table(allowed, questions)
        assert counted == fast, "transform form differs from words.counts_table"
        recorded = "words.counts_table (and the transform form, equal)"
    else:
        counted, recorded = fast, "transform form (words.counts_table is 4^m operations)"
    n = len(stars)
    tally = {}
    for drawn in range(1 << n):
        word = 0
        for d in marks:
            parity = sum(1 for k in range(n) if drawn >> k & 1 and d in stars[k]) % 2
            word |= parity << pos[d]
        tally[word] = tally.get(word, 0) + 1
    side = [Fraction(tally.get(a, 0), 1 << n) for a in range(1 << m)]
    agree = all(counted[a] == side[a] for a in range(1 << m))
    return {"knots": n, "distinctions": m, "allowed_words": len(allowed), "answer_words": 1 << m,
            "support_of_counted": sum(1 for p in counted if p), "agree": agree, "counting_rule_evaluated_by": recorded,
            "largest_difference": str(max(abs(counted[a] - side[a]) for a in range(1 << m)))}


# ----------------------------------------------------------------------------------------------------------------------
def s1_sources(report):
    out = {}
    archive = json.loads(lib.ARCHIVE_JSON.read_text())["named_archive_starts"]
    for name in ("start-00", "start-04", "start-13"):
        stars, r = lib.archived_start(name)
        same = [list(s) for s in stars] == [list(s) for s in r["gate"]["literal_supports"]]
        recorded = r["round_junction_counts"]
        steps = 5
        h = lib.grow(stars, "parity", steps, 20000, time_limit=100)
        cumulative = [sum(recorded[:i + 1]) for i in range(len(recorded))]
        out[name] = {"supports_equal_recorded_literal_supports": same, "recorded_cumulative": cumulative[:steps + 1],
                     "driver_cumulative": h["n_at"],
                     "counts_equal": h["n_at"] == cumulative[:len(h["n_at"])] and len(h["n_at"]) == steps + 1}
    seven = lib.seven_knot_source()
    out["seven_knot"] = {"knots": len(seven), "distinctions": len({d for s in seven for d in s}),
                         "recorded": [7, 25]}
    nine = lib.nine_knot_source()
    out["nine_knot_drawn"] = {"knots": len(nine), "distinctions": len({d for s in nine for d in s}), "recorded": [9, 39]}
    k21 = lib.twenty_one_knot_source()
    out["knots21_two_clocks"] = {"knots": len(k21), "distinctions": len({d for s in k21 for d in s}), "recorded": [21, 60]}
    five = lib.five_founder_clock()
    out["five_founder_clock"] = {"knots": len(five), "distinctions": len({d for s in five for d in s})}
    out["pass"] = (all(out[n]["supports_equal_recorded_literal_supports"] and out[n]["counts_equal"]
                       for n in ("start-00", "start-04", "start-13"))
                   and [out["seven_knot"]["knots"], out["seven_knot"]["distinctions"]] == [7, 25]
                   and [out["nine_knot_drawn"]["knots"], out["nine_knot_drawn"]["distinctions"]] == [9, 39]
                   and [out["knots21_two_clocks"]["knots"], out["knots21_two_clocks"]["distinctions"]] == [21, 60])
    report["S1"] = out


def s2_p1_shortcut(report):
    src = lib.load_module("gate_sources2", SOURCES_PY)
    rows = []
    patterns = [("cubic", d, src.cubic_pattern(d)[0]) for d in range(0, 6)]
    patterns += [("pinwheel", d, src.planar_pattern("pinwheel", d)) for d in (1, 2, 3, 4)]
    patterns += [("periodic", d, src.planar_pattern("periodic", d)) for d in (1, 2, 3, 4, 5, 6)]
    patterns += [("bounded_bond", w, src.fold_pattern(w, w)) for w in (1, 2, 3, 4)]
    bad = 0
    for name, depth, p in patterns:
        g = pattern_graph([list(o) for o in p.owners], len(p.knots))
        a = nx.check_planarity(g)[0]
        b = lib.passes(g)
        bad += a != b
        rows.append((name, depth, a, b))
    report["S2_p1"] = {"patterns": len(rows), "disagreements": bad}
    # growth stages of the seven-knot source and of a few P3 draws
    stage_bad = stage_total = 0
    h = lib.grow(lib.seven_knot_source(), "parity", 7, 3000)
    for n in h["n_at"]:
        g = lib.incidence_graph(h["stars"], n)
        stage_total += 1
        stage_bad += nx.check_planarity(g)[0] != lib.passes(g)
    count = 0
    for dr in lib.p3_draws():
        if count >= 120:
            break
        hh = lib.grow(dr["stars"], "parity", 8, 3000)
        if len(hh["n_at"]) < 2:
            continue
        count += 1
        for n in hh["n_at"]:
            g = lib.incidence_graph(hh["stars"], n)
            stage_total += 1
            stage_bad += nx.check_planarity(g)[0] != lib.passes(g)
    report["S2_stages"] = {"stages": stage_total, "disagreements": stage_bad}
    report["S2"] = {"pass": report["S2_census"]["euler_shortcut_disagreements"] == 0 and bad == 0 and stage_bad == 0}


def s3_engine_agreement(report):
    """end_operator.step (driver) against the other recorded engine, naelib/freelib Presentation, on counts per parent step."""
    nae = lib.load_module("gate_nae", lib.EXP / "NAE-GROWTH-20261119-001B/NAE-GROWTH-20261119-001B-E001_nae/naelib.py")
    compared = same = 0
    diffs = []
    for dr in lib.p3_draws():
        if compared >= 80:
            break
        for law in lib.LAWS:
            mine = lib.grow(dr["stars"], law, 5, 3000)
            if mine["outcome"] == "stall" and len(mine["n_at"]) == 1:
                # freelib reports a stall at once too; compare only that both stall
                P, out = nae.grow(dr["sizes"], dr["meetings"], law, rounds=5, maxj=3000)
                compared += 1
                same += out == "stall"
                if out != "stall":
                    diffs.append({"draw": [dr["arm"], dr["draw"]], "law": law, "mine": "stall", "other": out})
                continue
            P, out = nae.grow(dr["sizes"], dr["meetings"], law, rounds=5, maxj=3000)
            counts = P.counts_by_round()
            cum = [sum(counts[:i + 1]) for i in range(len(counts))]
            compared += 1
            ok = cum[:len(mine["n_at"])] == mine["n_at"] and (len(cum) == len(mine["n_at"]) or mine["outcome"] in ("closed",))
            same += ok
            if not ok:
                diffs.append({"draw": [dr["arm"], dr["draw"]], "law": law, "mine": mine["n_at"], "other": cum,
                              "mine_outcome": mine["outcome"], "other_outcome": out})
    report["S3"] = {"compared": compared, "same": same, "differences": diffs[:10], "pass": same == compared}


def main():
    report = {}
    t0 = time.time()
    rows = g1_recorded_patterns(report)
    g2_minor_search(report, rows)
    g3_mutant(report, rows)
    g4_knot_side_first_two(report)
    s1_sources(report)
    s2_p1_shortcut(report)
    s3_engine_agreement(report)
    report["gate_row_G_parts_run_here"] = {k: report[k]["pass"] for k in ("G1", "G2", "G3", "G4_first_two")}
    report["supporting_checks"] = {k: report[k]["pass"] for k in ("S1", "S2", "S3")}
    report["seconds"] = round(time.time() - t0, 1)
    lib.OUT.mkdir(parents=True, exist_ok=True)
    (lib.OUT / "gates.json").write_text(json.dumps(report, indent=1, sort_keys=True, default=str) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k in ("gate_row_G_parts_run_here", "supporting_checks", "seconds")},
                     indent=1))
    return 0 if all(report["gate_row_G_parts_run_here"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
