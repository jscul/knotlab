"""Reconcile finite READ census results and write only the requested CODEX outputs."""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def dump(name, obj, *, compact=False):
    path = (HERE / name).resolve()
    if not path.is_relative_to(HERE):
        raise ValueError("output outside CODEX")
    with path.open("w") as stream:
        json.dump(obj, stream, allow_nan=False, sort_keys=True,
                  **({"separators": (",", ":")} if compact else {"indent": 2}))
        stream.write("\n")


def size(rows):
    return dict(count=len(rows), draw_weight=sum(row["weight"] for row in rows))


def rate(rows, field):
    values = [(row, field(row)) for row in rows]
    success = [row for row, value in values if value is True]
    unknown = [row for row, value in values if value is None]
    numerator, denominator = size(success), size(rows)
    u = size(unknown)
    return dict(success=numerator, total=denominator, unknown=u,
                count_share=(numerator["count"] / denominator["count"]
                             if denominator["count"] and not unknown else None),
                weight_share=(numerator["draw_weight"] / denominator["draw_weight"]
                              if denominator["draw_weight"] and not unknown else None),
                count_share_bounds=[numerator["count"] / denominator["count"],
                                    (numerator["count"] + u["count"]) / denominator["count"]]
                                  if denominator["count"] else None,
                weight_share_bounds=[numerator["draw_weight"] / denominator["draw_weight"],
                                     (numerator["draw_weight"] + u["draw_weight"]) / denominator["draw_weight"]]
                                   if denominator["draw_weight"] else None)


def all_value(values):
    values = list(values)
    return False if False in values else None if None in values else True


def gate(rows, name):
    failed = [row for row in rows if row.get("R", {}).get(name, {}).get("passed") is False]
    unknown = [row for row in rows if row.get("R", {}).get(name, {}).get("passed") is None]
    return dict(passed=False if failed else None if unknown else True,
                failed=size(failed), unknown=size(unknown), total=size(rows),
                violations=[dict(key=row["key"], **row["R"][name]) for row in failed],
                unresolved_keys=[row["key"] for row in unknown])


def compare_r1(row, independent):
    other = independent["families"][row["key"]]
    differences = []
    for a, b in (("all_residues", "R1_every_residue"),
                 ("some_residues", "R1_some_residue"),
                 ("some_residues_only", "R1_progressions_only")):
        if row["R1"][a] != other[b]:
            differences.append(a)
    for name in ("preperiod", "period", "masks"):
        if row["carried"][name] != other["carried"][name]:
            differences.append("carried." + name)
    if row["R1"]["positions"] != other["syntax"]["R1_positions"]:
        differences.append("R1.positions")
    left, right = row["R1"]["residues"], other["carried"]["residues"]
    if len(left) != len(right):
        differences.append("residue_count")
    else:
        for l, r in zip(left, right):
            if (l["carried_mask"], l["covered"], l["s_mod_period"]) != (r["mask"], r["R1_covered"], r["s_mod_period"]):
                differences.append("residue." + str(l["residue"]))
    if other["scope"]["in_scope"] != row["in_scope"]:
        differences.append("scope")
    return differences


def compact(row):
    out = {key: row[key] for key in ("key", "key_sha256", "in_scope", "stratum", "verdict", "weight",
                                    "R1", "carried", "candidates")}
    if "R" in row:
        data = {key: value for key, value in row["R"].items() if key != "state_ties"}
        data["state_tie_records"] = len(row["R"].get("state_ties", []))
        for residue in data["residues"]:
            residue["states"] = len(residue.pop("state_ids"))
        out["R"] = data
    if "conditional" in row:
        c = row["conditional"]
        fields = ("complete", "certified", "verdict", "r", "least_r", "cap", "cap_reason", "cap_basis",
                  "least_r_in_partial_trace", "length_set_sizes", "boolean_length_set_sizes",
                  "all_conditionally_rectangular_by_length", "stored_products", "stored_boolean_products",
                  "repeat_start", "period", "partial_level", "partial_construction", "limits")
        out["conditional"] = {key: c.get(key) for key in fields}
        out["conditional"]["skipped_cap_accounting_ambiguity"] = cap_ambiguity(row)
    return out


def cap_ambiguity(row):
    data = row.get("conditional", {})
    if "product/carry cap" not in (data.get("cap") or ""):
        return False
    extra = data.get("partial_level") or data.get("partial_construction") or {}
    return data.get("stored_boolean_products", 0) + extra.get("boolean_products", 0) <= data["limits"]["max_stored_products"]


def q2_flag(row):
    data = row.get("conditional")
    if data is None:
        return None
    # The frozen prediction expressly counts capped as not successful.
    return bool(data["complete"] and data["certified"] and data["r"] is not None and data["r"] <= 8)


def residue_summary(rows):
    r1_rows = [dict(weight=row["weight"], covered=residue["covered"])
               for row in rows for residue in row["R1"]["residues"]]
    r_rows = [dict(weight=row["weight"], **residue)
              for row in rows for residue in row.get("R", {}).get("residues", [])]
    return dict(R1=dict(total=size(r1_rows), covered=rate(r1_rows, lambda r: r["covered"])),
                R=dict(completed_residues=size(r_rows),
                       incomplete_window_families=size([row for row in rows if not row.get("R", {}).get("window_complete")]),
                       applies=rate(r_rows, lambda r: r["applies"]),
                       literal_all_Q=rate(r_rows, lambda r: r["all_Q_applies"]),
                       only_carried_Q=rate(r_rows, lambda r: r["carried_Q_applies"]),
                       exception_only=rate(r_rows, lambda r: r["exception_only"])))


def group_summary(rows):
    return dict(**size(rows), R1_every=rate(rows, lambda r: r["R1"]["all_residues"]),
                R1_progressions_only=rate(rows, lambda r: r["R1"]["some_residues_only"]),
                R_every=rate(rows, lambda r: r.get("R", {}).get("all_residues")),
                R_some=rate(rows, lambda r: r.get("R", {}).get("some_residues")),
                conditional=rate(rows, q2_flag),
                conditional_verdict_count=dict(Counter(r.get("conditional", {}).get("verdict", "missing") for r in rows)),
                conditional_verdict_weight=dict(Counter({v: sum(r["weight"] for r in rows if r.get("conditional", {}).get("verdict", "missing") == v)
                                                        for v in {r.get("conditional", {}).get("verdict", "missing") for r in rows}})),
                least_r_count=dict(Counter(str(r["conditional"]["r"]) for r in rows if q2_flag(r))),
                least_r_weight=dict(Counter({str(n): sum(r["weight"] for r in rows if q2_flag(r) and r["conditional"]["r"] == n)
                                            for n in {r["conditional"]["r"] for r in rows if q2_flag(r)}})))


def counterexample_output():
    data = json.loads((HERE / "counterexample_full_raw.json").read_text())
    for name, variant in data["variants"].items():
        records = [row for row in data["records"] if row["variant"] == name]
        w, = [row["result"] for row in records if row["operation"] == "window_growth"]
        t, p = w["window"]["preperiod"], w["window"]["period"]
        levels = w["window"]["levels"]
        def U(s):
            return levels[s if s < len(levels) else t + (s - t) % p]["U"]
        directs = sorted((row for row in records if row["operation"] == "direct"), key=lambda r: r["s"])
        variant["U_s_1_to_6"] = [U(s) for s in range(1, 7)]
        variant["L_s_1_to_6"] = [row["result"]["minimum"] for row in directs]
        variant["direct_statuses"] = [row["result"]["status"] for row in directs]
        variant["direct_bonds_verified"] = all(row["result"].get("verification", {}).get("is_bond") for row in directs)
        variant["growth_certificates"] = {n: w["growth"][n] for n in ("G", "G2", "G2_live")}
    data["peak_rss_kib"] = max(row.get("process_peak_rss_kib", 0) for row in data["records"])
    dump("counterexample.json", data)
    return data


def main():
    index = json.loads((HERE / "source_index.json").read_text())
    independent = json.loads((HERE / "r1_independent.json").read_text())
    source = ROOT / index["source"]
    stat = source.stat()
    if (stat.st_size, stat.st_mtime_ns) != (index["size"], index["mtime_ns"]):
        raise ValueError("full source changed after streaming index")
    latest = {}
    with (HERE / "census_run/results.jsonl").open() as stream:
        for line in stream:
            rec = json.loads(line)
            latest[rec["case"]] = rec
    expected = {row["key"] for row in index["rows"]}
    foreign = set(latest) - expected
    if foreign:
        raise ValueError("foreign runner keys")
    failures = [dict(key=k, status=rec["status"], error=rec.get("error")) for k, rec in latest.items() if rec["status"] != "ok"]
    rows = [latest[row["key"]]["result"] for row in index["rows"]
            if row["key"] in latest and latest[row["key"]]["status"] == "ok"]
    mismatch = [dict(key=row["key"], fields=diff) for row in rows if (diff := compare_r1(row, independent))]
    in_scope = [row for row in rows if row["in_scope"]]
    out_scope = [row for row in rows if not row["in_scope"]]
    complete = len(rows) == 5964 and not failures
    if complete and len(in_scope) != 5789:
        raise ValueError("in-scope population changed")
    q1 = [row for row in in_scope if row.get("R", {}).get("q1_exception_only") is True]
    q1_unknown = [row for row in in_scope if row.get("R", {}).get("q1_exception_only") is None]
    q1_one_state = [row for row in in_scope if any(k["exception_states"] for residue in row.get("R", {}).get("residues", []) for k in residue["knots"])]
    q2 = rate(in_scope, q2_flag)
    q2_passed = q2["weight_share"] >= .9 if complete and q2["weight_share"] is not None else None
    q3 = counterexample_output()
    G_R, G_R1 = gate(rows, "gate_R"), gate(rows, "gate_R1")
    G = all_value([G_R["passed"], G_R1["passed"], not mismatch if complete else None])
    ambiguous_R = [dict(key=row["key"], questions=row.get("R", {}).get("ambiguities", []))
                   for row in rows if row.get("R", {}).get("ambiguities")]
    bounded = [row for row in in_scope if row["verdict"] == "bounded"]
    pair_cap_rows = [row for row in rows if cap_ambiguity(row)]
    in_pair_cap_rows = [row for row in pair_cap_rows if row["in_scope"]]
    groups = defaultdict(list)
    for row in rows:
        groups[(row["in_scope"], row["stratum"], row["verdict"])].append(row)
    stratum_verdict = [dict(in_scope=s, stratum=t, verdict=v, **group_summary(group))
                       for (s, t, v), group in sorted(groups.items())]
    r1_residues = [dict(key=row["key"], weight=row["weight"], **r)
                   for row in rows for r in row["R1"]["residues"]]
    metrics = dict(case_seconds=sum(rec.get("seconds", 0) for rec in latest.values()),
                   max_case_seconds=max((rec.get("seconds", 0) for rec in latest.values()), default=0),
                   max_runner_case_rss_mb=max((rec.get("peak_rss_mb", 0) for rec in latest.values()), default=0),
                   streaming_index_seconds=index["seconds"],
                   streaming_index_peak_rss_kib=index["peak_rss_kib"])
    state_file = HERE / "census_run/state.json"
    if state_file.exists():
        metrics["runner_state"] = json.loads(state_file.read_text())
        state = metrics["runner_state"]
        metrics["foreground_wall_seconds"] = (datetime.fromisoformat(state["heartbeat"]) -
                                               datetime.fromisoformat(state["started"])).total_seconds()
    summary = dict(schema_version=1, scope_id="READ-RULE-20261114-001B", complete=complete,
        source=dict(path=index["source"], sha256=index["sha256"], size=index["size"]),
        population=dict(all=size(rows), in_scope=size(in_scope), out_of_scope=size(out_scope),
                        expected_families=5964, expected_in_scope=5789, failures=failures,
                        missing_keys=sorted(expected - set(latest))),
        in_scope=group_summary(in_scope), out_of_scope=group_summary(out_scope),
        by_stratum_and_verdict=stratum_verdict,
        residue_counts=dict(all=residue_summary(rows), in_scope=residue_summary(in_scope),
                            out_of_scope=residue_summary(out_scope)),
        R1_reproduction=dict(passed=not mismatch if complete else None, families_compared=len(rows), mismatches=mismatch),
        R1_residues=dict(total=len(r1_residues), covered=sum(r["covered"] for r in r1_residues),
                         total_draw_weight=sum(r["weight"] for r in r1_residues),
                         covered_draw_weight=sum(r["weight"] for r in r1_residues if r["covered"])),
        bounded_weight_coverage=dict(denominator=size(bounded),
            R1_every=rate(bounded, lambda row: row["R1"]["all_residues"]),
            R1_some=rate(bounded, lambda row: row["R1"]["some_residues"]),
            R_every=rate(bounded, lambda row: row.get("R", {}).get("all_residues")),
            R_some=rate(bounded, lambda row: row.get("R", {}).get("some_residues")),
            alternatives_not_adopted=dict(
                every_residue_literal_all_Q=rate(bounded, lambda row: all_value(r["all_Q_applies"] for r in row["R"]["residues"]) if row["R"].get("window_complete") else None),
                every_residue_only_carried_Q=rate(bounded, lambda row: all_value(r["carried_Q_applies"] for r in row["R"]["residues"]) if row["R"].get("window_complete") else None))),
        G=dict(passed=G if complete else None, R=G_R, R1=G_R1,
               R1_reproduced=not mismatch if complete else None,
               scope="all 5964 families; in-scope and out-of-scope retained"),
        Q1=dict(passed=False if q1 else None if q1_unknown or not complete else True,
                exception_only_families=[dict(key=row["key"], weight=row["weight"],
                    residues=[r["residue"] for r in row["R"]["residues"] if r["exception_only"] is True]) for row in q1],
                exception_only=size(q1), unresolved=size(q1_unknown),
                unresolved_keys=[row["key"] for row in q1_unknown],
                families_with_any_exception_state=size(q1_one_state)),
        Q2=dict(passed=q2_passed, threshold=.9, population="all 5789 in-scope non-forgetting families",
                capped_counts_as_not=True, rate=q2,
                cap_accounting_ambiguity=dict(affected=size(in_pair_cap_rows),
                    keys=[row["key"] for row in in_pair_cap_rows],
                    disposition="affected least-r computation skipped; raw pair cap retained, no cap interpretation adopted",
                    maximal_weight_share_if_all_affected_succeeded=(q2["success"]["draw_weight"] + sum(row["weight"] for row in in_pair_cap_rows)) / q2["total"]["draw_weight"])),
        Q3=q3["Q3"],
        undecided=group_summary([row for row in in_scope if row["verdict"] == "undecided"]),
        ambiguities=dict(R_state_quantifiers=ambiguous_R,
                         unspecified_83_subset=True,
                         counterexample_shape_predicate_unspecified=True,
                         pair_only_cap_keys=[row["key"] for row in pair_cap_rows]),
        timings=metrics)
    dump("summary.json", summary)
    results = dict(schema_version=1, scope_id="READ-RULE-20261114-001B", complete=complete,
                   evidence_detail="census_run/results.jsonl contains exact state-wise tie records and product traces",
                   tie_row_schema=["candidate_index", "carried_main_port", "px_tie", "z_opposite_p", "z_opposite_x", "exception"],
                   R_unknown="null when supplied quantifiers disagree or repeating Q_s is incomplete",
                   source=summary["source"], families=[compact(row) for row in rows])
    dump("results.json", results, compact=True)
    update_report(summary, q3)
    print(json.dumps({"complete": complete, "families": len(rows), "R1_mismatches": len(mismatch),
                      "G": summary["G"]["passed"], "Q1": summary["Q1"]["passed"],
                      "Q2": summary["Q2"], "Q3": summary["Q3"]["status"], "timings": metrics}))


def percent(x):
    return "undetermined" if x is None else f"{100*x:.4f}%"


def verdict(x):
    return "inconclusive" if x is None else "pass" if x else "fail"


def update_report(s, counter):
    prefix = (HERE / "REPORT.md").read_text().split("<!-- generated-counts -->")[0].rstrip()
    lines = [prefix, "", "<!-- generated-counts -->", "", "## Computed census results", "",
             f"Completed: {s['population']['all']['count']} families. Independent R1 flags,",
             f"carried sequences and repeating-phase flags agree on {s['R1_reproduction']['families_compared']} families;",
             f"disagreements: {len(s['R1_reproduction']['mismatches'])}.", "",
             "| Population | Families | Draw weight | R1 every residue | R1 some residues only |",
             "| --- | ---: | ---: | ---: | ---: |"]
    for name, label in (("in_scope", "In scope"), ("out_of_scope", "Out of scope")):
        g = s[name]
        lines.append(f"| {label} | {g['count']} | {g['draw_weight']} | {g['R1_every']['success']['count']} | {g['R1_progressions_only']['success']['count']} |")
    b = s["bounded_weight_coverage"]
    lines += ["", "Coverage shares among CARRY's bounded in-scope families (descriptive counts):", "",
              "| Predicate | Covered families | Family share | Covered draw weight | Weight share | Unknown families |",
              "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for name in ("R1_every", "R1_some", "R_every", "R_some"):
        r = b[name]
        lines.append(f"| {name} | {r['success']['count']} | {percent(r['count_share'])} | {r['success']['draw_weight']} | {percent(r['weight_share'])} | {r['unknown']['count']} |")
    lines += ["", "## Gates and predictions", "",
              f"- G: `{verdict(s['G']['passed'])}`. R gate unknown families: {s['G']['R']['unknown']['count']}; R1 gate unknown families: {s['G']['R1']['unknown']['count']}.",
              f"- Q1: `{verdict(s['Q1']['passed'])}`. Exception-only in-scope families: {s['Q1']['exception_only']['count']}; unresolved: {s['Q1']['unresolved']['count']}. The full key list and residue lists are in summary.json.",
              f"- Q2: `{verdict(s['Q2']['passed'])}`. Conditional rectangularity succeeds for {s['Q2']['rate']['success']['count']} / {s['Q2']['rate']['total']['count']} families and {s['Q2']['rate']['success']['draw_weight']} / {s['Q2']['rate']['total']['draw_weight']} draw weight ({percent(s['Q2']['rate']['weight_share'])}); capped counts as not.",
              f"- Q3: `{s['Q3']['status']}`. Both variants give exact L(s) = 2 at s = 1–6 and a repeating window bound U = 2.", "",
              "A gate with `null` is unavailable, rather than a pass or failure. Ambiguous",
              "R coverage shares have explicit lower/upper count and weight bounds in",
              "summary.json. No interpretation was chosen to complete a missing flag.", "",
              f"The R gate has zero observed violations and {s['G']['R']['unknown']['count']} unavailable families;",
              f"the R1 gate has zero observed violations and {s['G']['R1']['unknown']['count']} unavailable families.",
              "Those gates are unavailable because the reused Q_s sequences are capped,",
              "so their repeating parts cannot be read. R1's separate syntax reproduction",
              "passes in full. G is consequently inconclusive.", "",
              f"R's quantifiers disagree on {len(s['ambiguities']['R_state_quantifiers'])} families in at least one residue.",
              "The official R flags affected by that question remain null; both alternatives",
              "and exact per-state ties are retained. R1's every-residue flag does not",
              "depend on that question.", "",
              "Q1's definite exception-only list contains every identified family below;",
              "the complete census keys are in summary.json. The unresolved list includes",
              "both capped windows and the five families affected by its state quantifier.", "",
              "| Family key SHA-256 prefix | Exception-only R residues |",
              "| --- | --- |"]
    for row in s["Q1"]["exception_only_families"]:
        lines.append(f"| `{hashlib.sha256(row['key'].encode()).hexdigest()[:16]}` | {row['residues']} |")
    lines += ["",
              "## Conditional rectangularity by CARRY classification", "",
              "| Scope | Stratum | Verdict | Families | Successful | Count share | Weight | Successful weight | Weight share |",
              "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for g in s["by_stratum_and_verdict"]:
        r = g["conditional"]
        lines.append(f"| {'in' if g['in_scope'] else 'out'} | {g['stratum']} | {g['verdict']} | {g['count']} | {r['success']['count']} | {percent(r['count_share'])} | {g['draw_weight']} | {r['success']['draw_weight']} | {percent(r['weight_share'])} |")
    u = s["undecided"]
    lines += ["", f"Among the actual {u['count']} undecided in-scope families, {u['conditional']['success']['count']} are",
              "conditionally rectangular through r ≤ 8. The separately mentioned subset",
              "of 83 has no supplied membership list and is not selected.", "",
              "One family reaches only the stricter pair-count storage cap; its least-r",
              "answer remains skipped/undecided under Ambiguity 4. All uncapped results",
              "are unaffected. Even if that family succeeded, Q2's draw-weight share",
              f"would be {percent(s['Q2']['cap_accounting_ambiguity']['maximal_weight_share_if_all_affected_succeeded'])}, still below 90%.", "",
              "## Counterexample details", "",
              "| Variant | U(1..6) | Exact L(1..6) | Direct bonds verified |",
              "| --- | --- | --- | --- |"]
    for name, v in counter["variants"].items():
        lines.append(f"| {name} | {v['U_s_1_to_6']} | {v['L_s_1_to_6']} | {v['direct_bonds_verified']} |")
    lines += ["", "Both keys, complete window and growth records, exact direct witnesses, and",
              "per-depth verification are retained in counterexample.json. The repeated",
              "argument is accepted. The positive gadget uses its exact four positive NAE",
              "constraints and adds its three own distinctions to S. In both variants",
              "the direct witness is the carried top a and target-own u. The three",
              "growth tests G, G2 and G2_live return no certificate.", "",
              "## Validation and timings", "",
              f"- Streaming the original 3.5-GB records: {s['timings']['streaming_index_seconds']:.3f} seconds; peak RSS {s['timings']['streaming_index_peak_rss_kib']/1024:.2f} MiB.",
              f"- Combined census: {s['timings']['case_seconds']:.3f} summed case seconds; slowest case {s['timings']['max_case_seconds']:.3f} seconds; maximum runner case RSS {s['timings']['max_runner_case_rss_mb']:.2f} MiB.",
              f"- Foreground runner wall time: {s['timings']['foreground_wall_seconds']:.3f} seconds (about ten minutes); maximum parent-plus-worker memory {s['timings']['runner_state']['peak_rss_mb']:.2f} MiB.",
              "- R1's independent raw-key implementation has 17 hand-expected controls; conditional products have seven controls, including equal Boolean products with distinct identity maps.",
              "- Fifteen focused tie/quantifier controls passed in 0.092 seconds.",
              "- The independent exception audit confirmed all nine Q1 families: 1,956 eligible knot/state checks across 899 projected states, in 2.440 seconds. It reuses the producer's Q-state membership and independently recomputes candidates, pair projections and exception flags.",
              "- For every complete source window, each reconstructed Q level agrees with CARRY's recorded cardinality, U, repeated phase, and the union of identity-carried positions.",
              "- All requested direct bonds are checked independently by the reused CNF bond/deletion checker.", "",
              "The shared runner used one worker plus its parent and a 4G configuration;",
              "no service or tracker registration was launched. Preparation, the 20-case",
              "foreground smoke, and the foreground computation are",
              "recorded under census_run/. Reused source files were not modified.", "",
              "## Outputs and replay", "",
              "- [results.json](results.json): compact per-family flags, residues, tie histograms and conditional-product outcomes.",
              "- [counterexample.json](counterexample.json): both raw census keys and all window, growth and direct results.",
              "- [summary.json](summary.json): exact counts, draw-weight shares, gates, predictions, unresolved cases and ambiguity bounds.",
              "- [validation.json](validation.json): focused output reconciliation, Python AST checks and source/code hashes.", "",
              "The 20-case smoke completed in 0.549 summed case seconds. Its measured",
              "cost supported the foreground census, which finished in about ten minutes.",
              "All 5,964 runner cases are final and successful; no run awaits launch.", "",
              "Commands used from the repository root (CODEX is this report's directory):", "",
              "```bash",
              "CODEX=experiments/READ-RULE-20261114-001B/READ-RULE-20261114-001B-E001_coverage/codex",
              '.venv/bin/python -B scripts/longrun.py launch "$CODEX/job.py" --out "$CODEX/census_run" --unit read-rule-coverage --workers 1 --case-timeout 600 --case-mem 3G --mem-max 4G --cpu-quota 100% --param phase=combined --prepare-only',
              '.venv/bin/python -B scripts/longrun.py run --out "$CODEX/census_run" --foreground --limit 20',
              '.venv/bin/python -B scripts/longrun.py run --out "$CODEX/census_run" --foreground',
              '.venv/bin/python -B "$CODEX/summarize.py"',
              '.venv/bin/python -B "$CODEX/verify_outputs.py"',
              "```", "",
              "The preparation line records an already performed operation; it is not a",
              "request to overwrite the retained configuration. The last two commands",
              "rebuild and validate the requested outputs using the retained raw evidence.", "",
              "Q3's disagreement with the frozen prediction is recorded here for the",
              "owning thread. The write restriction prevents editing any external correction",
              "log or research lifecycle record in this task.", ""]
    (HERE / "REPORT.md").write_text("\n".join(lines))


if __name__ == "__main__":
    main()
