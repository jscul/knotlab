"""Literal four-name supports, canonical physical projections and constructive counterchecks."""

import argparse
import gzip
import json
import os
import subprocess
import sys
from fractions import Fraction as Q
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "word_checks.json"
BITS = ("0", "1")
PAIRS = ["".join(w) for w in product(BITS, repeat=2)]
TRIPLES = ["".join(w) for w in product(BITS, repeat=3)]
WORDS = ["".join(w) for w in product(BITS, repeat=4)]
LAWS = {"even": [w for w in TRIPLES if w.count("1") % 2 == 0],
        "not_all_equal": [w for w in TRIPLES if len(set(w)) == 2]}


def select(word, names):
    return "".join(word["acbd".index(name)] for name in names)


def sources(names, first, companion):
    return [w for w in WORDS if w[:3] in LAWS[first] and select(w, names) in LAWS[companion]]


def projected_knots(physical_rules):
    clauses = []
    for names, rule in physical_rules:
        for bad in set(TRIPLES) - set(LAWS[rule]):
            clauses.append(" ".join(x if b == "0" else "~" + x for x, b in zip(names, bad)))
    out = {}
    for names, rule in physical_rules:
        aux = next(x for x in "acbd" if x not in names)
        command = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", ";".join(sorted(clauses)),
                   "--loops", *names[:2], "--contact", names[2], "--witnesses", aux, "--json"]
        check = json.loads(subprocess.check_output(command, cwd=ROOT, text=True,
                           env=dict(os.environ, PYTHONPATH=str(ROOT / "tools"))))
        assert check["is_knot"] and sorted(check["allowed"]) == sorted(LAWS[rule])
        out[names] = {"loop_names": names[:2], "contact_name": names[2], "forgotten": aux,
                      "allowed": check["allowed"], "K1_K2_K3": check["is_knot"]}
    return out


def connected(start, nodes):
    current = {start}
    while True:
        larger = {y for y in nodes if any(x[:2] == y[:2] or x[2] == y[2] for x in current)}
        if larger == current:
            return sorted(current)
        current = larger


def transitions(extensions):
    by_d = {}
    for d in BITS:
        nodes = {x for x in TRIPLES if d in extensions[x]}
        by_d[d] = sorted({tuple(connected(x, nodes)) for x in nodes})
    from_known = {}
    for x, ds in extensions.items():
        if ds:
            safe = {y for y in TRIPLES if set(ds) <= set(extensions[y])}
            from_known[x] = connected(x, safe)
    return {"fixed_d_comparison_components": by_d,
            "reachable_from_publicly_measured_start_without_d": from_known}


def transpose(m):
    return list(map(list, zip(*m)))


def multiply(m, n):
    return [[sum(a * b for a, b in zip(row, col)) for col in zip(*n)] for row in m]


def raw_tables(extensions):
    mats = [[[int(d in extensions[ac + b]) for b in BITS] for ac in PAIRS] for d in BITS]
    trace = [[len(set(extensions[x]) & set(extensions[y])) for y in TRIPLES] for x in TRIPLES]
    norm = sum(trace[i][i] for i in range(len(TRIPLES)))
    gram = [[sum(mats[i][a][b] * mats[j][a][b] for a in range(4) for b in range(2))
             for j in range(2)] for i in range(2)]
    assert gram[0][0] + gram[1][1] == norm
    dg = [[v if i == j else 0 for j, v in enumerate(row)] for i, row in enumerate(trace)]
    return {"unnormalized_hidden_coefficient_matrices": mats, "matrix_A_row_order": PAIRS,
            "matrix_B_columns": BITS, "Gram_d_order_01": gram, "norm_squared": norm,
            "visible_basis_acb": TRIPLES, "trace_d_positive_numerator": trace,
            "trace_d_diagonal_numerator": dg,
            "slice_probabilities": [str(Q(gram[i][i], norm)) for i in range(2)]}


def restricted_split_certificate(sources_, mats, reachable):
    possible = {}
    for final in PAIRS:
        allow_rows = []
        for n, ac in enumerate(PAIRS):
            a, c = ac
            b = str(1 - int(a))
            assert all(ac + b + d in sources_ for d in BITS)
            assert {x[0] + x[2] for x in reachable[ac + b]} == {a + b}
            if final == a + b:
                allow_rows.append(n)
        if final[0] == final[1]:
            assert not allow_rows
        else:
            r = int(final[0])
            assert len(allow_rows) == 2
            common = [mats[d][n][1-r] for d in range(2) for n in allow_rows]
            assert common == [1] * 4
            assert [mats[r][n][r] for n in allow_rows] == [0, 0]
            assert sorted(mats[1-r][n][r] for n in allow_rows) == [0, 1]
        possible[final] = {"A_input_rows_remaining_if_B_invertible": [PAIRS[i] for i in allow_rows],
                           "remaining_a": final[0] if allow_rows else None}
    return possible


def weak_control(sources_):
    # On F-success the original c is in A's work. F uses opposite signs when a=0.
    amps = {}
    component_paths = {}
    for w in sources_:
        a, c, b, d = w
        ac = a + str(1 - int(a))
        index = 0 if a == "0" else 1 + int(c)
        coefficient = Q((-1) ** int(c), 2) if a == "0" else Q(1)
        key = (ac, index, b, d)
        amps[key] = amps.get(key, Q(0)) + coefficient
        component_paths[w] = {"post_transfer": ac + b + d, "proposed_B_clear": ac + "0" + d,
                              "B_clear_lawful_on_constituent": ac + "0" + d in sources_,
                              "F_success_component_amplitude": str(coefficient)}
        assert ac + b + d in sources_
    first_mass = sum(a*a for a in amps.values()) / len(sources_)
    assert first_mass == Q(21, 40)
    weak_forbidden_basis = [w for w, path in component_paths.items() if not path["B_clear_lawful_on_constituent"]]
    assert weak_forbidden_basis == ["0010", "0110"]
    matrices = [[[Q(0), Q(0)] for _ in range(3)] for _ in range(2)]
    for (ac, index, b, d), amplitude in amps.items():
        if amplitude:
            assert ac + "0" + d in sources_ and "100" + d in sources_
        matrices[int(d)][index][int(b)] += amplitude
    k = [[Q(2,3), 0, Q(1,3)], [0, Q(1,3), Q(-1,3)]]
    gram = multiply(k, transpose(k))
    assert 1 - gram[0][0] > 0 and 1 - gram[1][1] > 0
    assert (1-gram[0][0]) * (1-gram[1][1]) - gram[0][1]**2 > 0
    end = [multiply(k, part) for part in matrices]
    assert end == [[[Q(1,3), 0], [0, Q(1,3)]], [[0, 0], [0, 0]]]
    success = sum(v*v for mat in end for row in mat for v in row) / len(sources_)
    assert success == Q(1,45)
    diagonal_forbidden_mass = sum(Q(component_paths[w]["F_success_component_amplitude"])**2
                                  for w in weak_forbidden_basis) / len(sources_)
    assert diagonal_forbidden_mass == Q(1,20)
    return {"frozen_primary_test_accepts_protocol": False, "weaker_prepared_coherent_test_accepts": True,
            "raw_F_paths": component_paths, "forbidden_wordwise_paths": weak_forbidden_basis,
            "diagonal_if_B_clear_attempted_forbidden_mass_per_launch": str(diagonal_forbidden_mass),
            "post_F_private_slice_matrices": matrices, "second_filter": k, "second_filter_KKt": gram,
            "post_second_positive_slice_matrices": end, "first_pass": str(first_mass),
            "first_refusal": str(1-first_mass), "second_conditional_pass": str(success/first_mass),
            "second_refusal_per_launch": str(first_mass-success), "whole_launch_Bell": str(success)}


def main():
    cases = {}
    for names in ("acd", "abd"):
        for first, companion in product(LAWS, repeat=2):
            words = sources(names, first, companion)
            extensions = {x: [w[-1] for w in words if w[:3] == x] for x in TRIPLES}
            compare = transitions(extensions)
            stats = raw_tables(extensions)
            key = f"{names}/{first}/{companion}"
            cases[key] = {"whole_allowed_acbd": words, "extensions_of_acb": extensions,
                          "physical_projection": projected_knots([("acb", first), (names, companion)]),
                          "marginal": stats, "reachability": compare}
            assert len(words) == {("even","even"):4, ("even","not_all_equal"):6,
                                  ("not_all_equal","even"):6, ("not_all_equal","not_all_equal"):10}[first,companion]
            renamed = [w[1]+w[0]+w[2:] for w in words]
            assert set(renamed) == set(sources("acd" if names == "acd" else "cbd", first, companion))
            if first == companion == "not_all_equal":
                mats = stats["unnormalized_hidden_coefficient_matrices"]
                if names == "acd":
                    left, right = transpose(mats[0])[1], transpose(mats[1])[0]
                    assert left == right == [0,1,1,0]
                    cases[key]["shared_opposite_column"] = left
                else:
                    cases[key]["product_record_certificate"] = restricted_split_certificate(
                         words, mats, compare["reachable_from_publicly_measured_start_without_d"])
                    cases[key]["prepared_state_only_control"] = weak_control(words)
    return {"named_word_order": "acbd", "slice_order": BITS,
            "tested_offer": "one reader may update all of its physical names in a single primitive",
            "number_of_candidate_words_tested_across_settings": 8 * 16, "cases": cases}


def reconcile(own):
    peer_path = HERE / "two_shared_evidence.json.gz"
    peer = json.loads(gzip.decompress(peer_path.read_bytes()))
    laws = {"even": "parity", "not_all_equal": "nae"}
    for key, row in own["cases"].items():
        nam, f, g = key.split("/")
        place = "together" if nam == "acd" else "split"
        other = peer["populations"][f"{place}/{laws[f]}-{laws[g]}"]
        assert other["allowed_acbd"] == row["whole_allowed_acbd"]
        for d in BITS:
            comparison = other["d_slices_only_mathematical"][d]
            assert comparison["A_rows_00_01_10_11_B_columns_0_1"] == row["marginal"]["unnormalized_hidden_coefficient_matrices"][int(d)]
            comparable = sorted(tuple(x[:3] for x in comp) for comp in comparison["mutually_reachable_sets"])
            assert comparable == row["reachability"]["fixed_d_comparison_components"][d]
        for shape, field in (("coherent","trace_d_positive_numerator"),("diagonal","trace_d_diagonal_numerator")):
            m = other["reduced_after_tracing_d"][shape]
            assert [[Q(x, m["den"]) for x in line] for line in m["rows"]] == [
                [Q(x, row["marginal"]["norm_squared"]) for x in line] for line in row["marginal"][field]]
        for nm in ("acb", nam):
            h = other["named_projections"][nm]
            assert h["K1_K2_K3"]["is_knot"] and row["physical_projection"][nm]["K1_K2_K3"]
            assert h["extensions"] == {x: sum(select(w, nm) == x for w in row["whole_allowed_acbd"]) for x in TRIPLES}

    def verify_channel(name, projection, rate):
        encoded = peer["maps"][name]
        def rational(ids):
            m, radical = (peer["matrix_catalogue"][idx] for idx in ids)
            assert all(x == 0 for line in radical["rows"] for x in line)
            return [[Q(x, m["den"]) for x in line] for line in m["rows"]]
        for i,j in product(range(4), repeat=2):
            got = rational(encoded["matrix_unit_output_ids_in_row_major_input_order"][4*i+j])
            assert got == [[rate*row[i]*col[j] for col in projection] for row in projection]
        external = rational(encoded["two_local_target_spectator_probe"])
        assert all(external[4*i+u][4*j+v] == rate*projection[u][i]*projection[v][j]/4
                   for i,u,j,v in product(range(4),repeat=4))

    signs = {t: [[Q(int(i == j)+t*(-1,1,1,-1)[j]*int(i == 3-j),2)
                  for j in range(4)] for i in range(4)] for t in (-1,1)}
    identity = [[int(i==j) for j in range(4)] for i in range(4)]
    setting = peer["instrument_settings"]["split/nae-nae/coherent/prepared_state_only/baseline"]
    refusals = {"plus_refusal": Q(9,20), "minus_refusal": Q(1,40), "first_pass/refusal_1": Q(97,1800),
                "first_pass/refusal_2": Q(113,360), "first_pass/refusal_3": Q(27,200)}
    for record in setting["all_probes_all_flags"].values():
        s = record["sign_if_both_actual_flags_arrive"]
        source = record["source_record"]
        if s is None:
            verify_channel(record["target_channel"], identity, refusals[source])
        else:
            verify_channel(record["target_channel"], signs[s], Q(1,90))
    for s in (-1,1):
        verify_channel(setting["joined_sign_maps_per_launch"][str(s)], signs[s], Q(1,45))
    repeats = peer["fresh_prepared_state_only_repeat"]["joined_two_successful_signs"]
    for (s,t) in product((-1,1), repeat=2):
        verify_channel(repeats[f"{s}/{t}"], signs[s], Q(int(s==t),2025))
    assert len(peer["explicit_primary_lawful_00_failures"]) == 16
    print("Independent archive comparison passed on every word, projection, hidden slice, reduced matrix, fixed-d component and all weak-protocol fine maps, both spectator probes and repeat signs.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--peer", action="store_true", help="also compare the separate physical-instrument archive")
    args = parser.parse_args()
    result = main()
    raw = json.dumps(result, sort_keys=True, indent=2, default=str) + "\n"
    if args.write:
        OUTPUT.write_text(raw)
    else:
        assert raw == OUTPUT.read_text()
    if args.peer:
        reconcile(result)
    print("Verified 128 assignment tests, 16 native projections, both unread traces, reachability, rank certificates and the 1/45 comparison.")
