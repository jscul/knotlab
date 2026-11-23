"""Tables, predictions and the fixed reading for REVIEW-LEADS-20261123-001G-E001 (reads the read_*.jsonl outputs only).

Codings (deviations.md): a start with no failing stage within the horizon has knots at first failure = +infinity for a median
(none occurs); 'not proved sources' = recorded proved not + undecided (Q1) + unresolved (Q2); growth kind is ticket A's
`growth_kind` as computed, with a sensitivity line for histories stopped by the cap or the time limit within four steps.

Run from the repo root:  timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file>
"""
import glob
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402

KINDS = ("stalled", "bounded", "growing")
VERDICTS = {"Q1": ("proved_source", "proved_not", "undecided"), "Q2": ("proved_source", "proved_not", "unresolved")}


def load():
    rows = []
    for f in sorted(glob.glob(str(C.OUT / "read_Q*_*.jsonl"))):
        rows += [json.loads(line) for line in open(f)]
    keys = Counter((r["id"], r["law"]) for r in rows)
    assert all(v == 1 for v in keys.values()), "duplicate rows"
    assert len(rows) == 2 * (53 + 192), len(rows)
    return rows


def med(xs):
    xs = [float("inf") if x is None else x for x in xs]
    return statistics.median(xs) if xs else None


def rng(xs):
    xs = [x for x in xs if x is not None]
    return [min(xs), max(xs)] if xs else None


def kind_sensitive(r):
    """Sensitivity: a history stopped by the cap or the time limit within four steps, called bounded by the code, read as growing
    when its births per step never fell."""
    b = r["births_per_step"]
    if r["growth_kind"] == "bounded" and r["outcome"] in ("cap", "time") and r["steps"] <= 4 and all(
            x <= y for x, y in zip(b, b[1:])):
        return "growing"
    return r["growth_kind"]


def cross_table(rows, pop, law):
    t = {v: {k: {"fail": 0, "pass": 0} for k in KINDS} for v in VERDICTS[pop]}
    for r in rows:
        if r["population"] == pop and r["law"] == law:
            t[r["verdict"]][r["growth_kind"]]["fail" if r["fails_within_horizon"] else "pass"] += 1
    return t


def main():
    rows = load()
    out = {"cross_tables": {}, "knots_at_first_failure": {}, "breaking_birth": {}, "predictions": {}, "reading": {}}
    for pop in ("Q1", "Q2"):
        for law in C.LAWS:
            out["cross_tables"][f"{pop}:{law}"] = cross_table(rows, pop, law)

    by = defaultdict(list)
    for r in rows:
        by[(r["population"], r["law"])].append(r)

    for law in C.LAWS:
        q1, q2 = by[("Q1", law)], by[("Q2", law)]
        sources = [r for r in q1 + q2 if r["verdict"] == "proved_source"]
        grow_non = [r for r in q1 + q2 if r["verdict"] != "proved_source" and r["growth_kind"] == "growing"]
        grow_non_s = [r for r in q1 + q2 if r["verdict"] != "proved_source" and kind_sensitive(r) == "growing"]
        q1_src_g = [r for r in q1 if r["verdict"] == "proved_source" and r["growth_kind"] == "growing"]
        q1_not_g = [r for r in q1 if r["verdict"] == "proved_not" and r["growth_kind"] == "growing"]
        q1_not_g_legal = [r for r in q1_not_g if r["legal"]]
        k = lambda rs: [r["knots_at_first_failure"] for r in rs]  # noqa: E731
        out["knots_at_first_failure"][law] = {
            "proved_sources_Q1": {"n": sum(r["population"] == "Q1" for r in sources),
                                  "median": med(k([r for r in sources if r["population"] == "Q1"])),
                                  "range": rng(k([r for r in sources if r["population"] == "Q1"]))},
            "proved_sources_Q2": {"n": sum(r["population"] == "Q2" for r in sources),
                                  "median": med(k([r for r in sources if r["population"] == "Q2"])),
                                  "range": rng(k([r for r in sources if r["population"] == "Q2"])),
                                  "values": {r["id"]: r["knots_at_first_failure"] for r in sources if r["population"] == "Q2"}},
            "proved_sources_all": {"n": len(sources), "median": med(k(sources)), "range": rng(k(sources))},
            "growing_not_sources_Q1": {"n": sum(r["population"] == "Q1" for r in grow_non),
                                       "median": med(k([r for r in grow_non if r["population"] == "Q1"])),
                                       "range": rng(k([r for r in grow_non if r["population"] == "Q1"]))},
            "growing_not_sources_Q2": {"n": sum(r["population"] == "Q2" for r in grow_non),
                                       "median": med(k([r for r in grow_non if r["population"] == "Q2"])),
                                       "range": rng(k([r for r in grow_non if r["population"] == "Q2"]))},
            "growing_not_sources_all": {"n": len(grow_non), "median": med(k(grow_non)), "range": rng(k(grow_non))},
            "first_failing_step_counts": {
                "proved_sources": dict(Counter(str(r["first_failing_step"]) for r in sources)),
                "growing_not_sources_Q1": dict(Counter(str(r["first_failing_step"]) for r in grow_non if r["population"] == "Q1")),
                "growing_not_sources_Q2": dict(Counter(str(r["first_failing_step"]) for r in grow_non if r["population"] == "Q2"))},
        }
        bb = defaultdict(Counter)
        for r in q1 + q2:
            b = r["breaking_birth"]
            grp = "proved_source" if r["verdict"] == "proved_source" else (
                "growing_not_source" if r["growth_kind"] == "growing" else f"{r['growth_kind']}_not_source")
            if b is not None:
                bb[f"{r['population']}:{grp}:parents"][str(b["parents"])] += 1
                bb[f"{r['population']}:{grp}:fresh"][str(b["fresh"])] += 1
            elif r["fails_within_horizon"]:
                bb[f"{r['population']}:{grp}:parents"]["source fails at step 0"] += 1
        out["breaking_birth"][law] = {key: dict(v) for key, v in sorted(bb.items())}
        out["breaking_birth"][law]["any_breaking_birth_with_fewer_than_two_parents"] = sum(
            1 for r in q1 + q2 if r["breaking_birth"] and r["breaking_birth"]["parents"] < 2)

        # predictions
        p1_fail = [r["id"] for r in sources if not r["fails_within_horizon"]]
        out["predictions"][f"P1:{law}"] = {"proved_sources": len(sources), "fail_within_horizon": len(sources) - len(p1_fail),
                                           "pass_every_stage": p1_fail, "holds": not p1_fail}
        m_src, m_not = med(k(q1_src_g)), med(k(q1_not_g))
        out["predictions"][f"P2:{law}"] = {"Q1_growing_proved_sources": len(q1_src_g), "median_sources": m_src,
                                           "Q1_growing_proved_not": len(q1_not_g), "median_proved_not": m_not,
                                           "holds": m_src <= m_not,
                                           "sensitivity_legal_proved_not_only": {"n": len(q1_not_g_legal),
                                                                                 "median": med(k(q1_not_g_legal))},
                                           "values_sources": sorted(k(q1_src_g)), "values_proved_not": sorted(k(q1_not_g))}
        fails = sum(r["fails_within_horizon"] for r in grow_non)
        out["predictions"][f"P3:{law}"] = {"growing_not_sources": len(grow_non), "fail_within_horizon": fails,
                                           "share": fails / len(grow_non), "holds": fails <= len(grow_non) / 2,
                                           "by_population": {p: [sum(r["fails_within_horizon"] for r in grow_non if r["population"] == p),
                                                                 sum(r["population"] == p for r in grow_non)] for p in ("Q1", "Q2")},
                                           "sensitivity_growth_kind": {"n": len(grow_non_s),
                                                                       "fail": sum(r["fails_within_horizon"] for r in grow_non_s)}}
        share = fails / len(grow_non)
        all_sources_fail = not p1_fail
        if share >= 0.9:
            reading = "at least 90% fail: the test tracks growth; no argument is attempted"
        elif share <= 0.5 and all_sources_fail:
            reading = "at most 50% fail and every proved source fails: the test separates sources; attempt an argument"
        else:
            reading = "in between: both numbers reported; no argument is attempted"
        out["reading"][law] = {"share_growing_not_sources_failing": share, "every_proved_source_fails": all_sources_fail,
                               "reading": reading}

        # Q1 inheritance
        inh = defaultdict(Counter)
        detail = []
        for r in q1:
            if not r["fails_within_horizon"]:
                continue
            i = r["inheritance"]
            grp = r["verdict"]
            inh[grp]["first_failures"] += 1
            inh[grp]["subpattern_only_inherited"] += bool(i.get("subpattern_uses_only_inherited_knots"))
            inh[grp]["inherited_knots_alone_fail"] += bool(i.get("inherited_knots_alone_fail"))
            inh[grp]["subpattern_uses_edit_distinction"] += bool(i.get("subpattern_uses_edit_distinction"))
            inh[grp]["same_step_as_unedited"] += r["first_failing_step"] == i["unedited_first_failing_step"]
            detail.append({"id": r["id"], "name": r["name"], "verdict": r["verdict"], "kind": i.get("subpattern_kind"),
                           "only_inherited": i.get("subpattern_uses_only_inherited_knots"),
                           "inherited_alone_fail": i.get("inherited_knots_alone_fail"),
                           "uses_edit_distinction": i.get("subpattern_uses_edit_distinction"),
                           "knots_in_subpattern": i.get("subpattern_knots"),
                           "inherited_in_subpattern": i.get("subpattern_knots_inherited")})
        out.setdefault("q1_inheritance", {})[law] = {"by_verdict": {g: dict(v) for g, v in inh.items()}, "detail": detail}

        # limits and checks
        out.setdefault("limits", {})[law] = {
            "outcomes": {p: dict(Counter(r["outcome"] for r in by[(p, law)])) for p in ("Q1", "Q2")},
            "stopped_by_time": [r["id"] for r in q1 + q2 if r["outcome"] == "time"],
            "bounded_by_code_stopped_within_four_steps": [
                {"id": r["id"], "outcome": r["outcome"], "births_per_step": r["births_per_step"], "verdict": r["verdict"]}
                for r in q1 + q2 if r["growth_kind"] == "bounded" and r["outcome"] in ("cap", "time") and r["steps"] <= 4],
            "stalled_after_births": [r["id"] for r in q1 + q2 if r["growth_kind"] == "stalled" and r["steps"] > 0],
            "trace_agreement": {p: [sum(r["trace_agreement"]["equal"] for r in by[(p, law)]),
                                    sum(r["trace_agreement"]["compared"] for r in by[(p, law)])] for p in ("Q1", "Q2")},
        }
    nae = [r for r in rows if r["law"] == "nae"]
    out["laws"] = {
        "Q1_histories_equal_between_laws": sum(r["history_shared_with_parity"] for r in nae if r["population"] == "Q1"),
        "Q1_differ": [r["id"] for r in nae if r["population"] == "Q1" and not r["history_shared_with_parity"]],
        "Q1_parity_has_single_birth_step": [r["id"] for r in rows if r["population"] == "Q1" and r["law"] == "parity"
                                            and r["has_single_birth_step"]],
        "Q2_shared_by_engine_clause": sum(r["history_shared_with_parity"] for r in nae if r["population"] == "Q2"),
        "Q2_short_checks_equal": sum(1 for r in nae if r["population"] == "Q2" and r["nae_short_check"]
                                     and r["nae_short_check"]["equal"]),
        "Q2_grown_separately": [r["id"] for r in nae if r["population"] == "Q2" and not r["history_shared_with_parity"]],
        "verdict_differs_between_laws": sorted({r["id"] for r in rows if any(
            x["id"] == r["id"] and x["law"] != r["law"] and x["fails_within_horizon"] != r["fails_within_horizon"] for x in rows)}),
    }
    out["proved_sources_detail"] = [{"id": r["id"], "law": r["law"], "name": r.get("name"), "growth_kind": r["growth_kind"],
                                     "outcome": r["outcome"], "n_at": r["n_at"], "first_failing_step": r["first_failing_step"],
                                     "knots_at_first_failure": r["knots_at_first_failure"], "breaking_birth": r["breaking_birth"]}
                                    for r in rows if r["verdict"] == "proved_source"]
    (C.OUT / "summary.json").write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n")
    print(json.dumps({"predictions": out["predictions"], "reading": out["reading"], "laws": out["laws"]}, indent=1,
                     default=str))


if __name__ == "__main__":
    main()
