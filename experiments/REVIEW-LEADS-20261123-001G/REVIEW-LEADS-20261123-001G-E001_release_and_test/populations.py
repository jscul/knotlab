"""Recover the two populations with their recorded verdicts (no verdict is recomputed).

Q1: the 53 uniform single edits of the seven-knot source, READS-HOLDERS-SOURCES-20261120-001C edits.json `catalogue`
    (stars = `supports`; verdict = `recurrence_including_residual_proof`, the frozen reader plus the later parent-map proof;
    yes = proved to release repeatedly, no = proved not / ineligible, unknown = undecided).  Regenerated with that study's own
    `edits.py` (`edit_population`, `Edit.applied` on `source_from(MEETINGS, LOOSE)`) and compared.
Q2: the demand-supplied draws at sizes nine to twelve, draws.jsonl rows with supply `funded_sensitivity`, size group 9-12
    (96 with two extra meetings, 96 with three); stars = `fixtures.source_from(edges, loose)` as in survey.source; verdict =
    the event `underlying_indefinite_recurrence` of that study's own `rates.events` (yes = proved; unknown = unresolved;
    otherwise proved not).  Regenerated with that study's own `survey.draw_specs` and the supply formula of `survey.source`,
    and compared; the five proved draws are compared with certificates.json `proved_draws`.

Gate G (second clause): the recorded counts 16 / 33 / 4 (Q1, each law and horizon) and 5 of 192 (Q2, each law) are recovered.

Run from the repo root:  timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file>
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402

sys.path.insert(0, str(C.RHS_EXP))
import networkx as nx  # noqa: E402
import rates as rhs_rates  # noqa: E402  (READS-HOLDERS-SOURCES-20261120-001C rates.py; imports its survey.py)
import survey as rhs_survey  # noqa: E402

rhs_edits = C.A.load_module("rhs_edits", C.RHS_EXP / "edits.py")

Q1_MAP = {"yes": "proved_source", "no": "proved_not", "unknown": "undecided"}


def tup(stars):
    return tuple(tuple(s) for s in stars)


def q1():
    data = json.loads((C.RHS_ART / "edits.json").read_text())
    _, physical, _ = rhs_edits.libraries()
    source = physical.source_from(rhs_edits.MEETINGS, rhs_edits.LOOSE)
    checks = {"original_supports_regenerated": tup(source) == tup(data["original_supports"])}
    regenerated = rhs_edits.edit_population(source)
    checks["edit_count_regenerated"] = len(regenerated)
    starts, counts, agree = [], Counter(), 0
    for entry, edit in zip(data["catalogue"], regenerated, strict=True):
        same = (tup(edit.applied(source)) == tup(entry["supports"])
                and {"operation": edit.operation, "holders": list(edit.holders), "distinction": edit.distinction} == entry["edit"])
        agree += same
        verdicts, frozen, reasons, trace = {}, {}, {}, {}
        for law in C.LAWS:
            for h in ("16", "32"):
                b = entry["by_law"][law][h]
                counts[(law, h, b["recurrence_including_residual_proof"])] += 1
            b = entry["by_law"][law]["32"]
            verdicts[law] = Q1_MAP[b["recurrence_including_residual_proof"]]
            frozen[law] = b["recurrence"]
            reasons[law] = b.get("reason")
            trace[law] = [[t["age"], t.get("live"), t.get("planned_births")] for t in b.get("trace", [])]
            assert entry["by_law"][law]["16"]["recurrence_including_residual_proof"] == b["recurrence_including_residual_proof"]
        e = entry["edit"]
        name = f"{e['operation']}:{'-'.join(map(str, e['holders']))}:d{e['distinction']}"
        starts.append({"id": f"Q1-{entry['atom']:02d}", "atom": entry["atom"], "name": name, "edit": e,
                       "stars": [list(s) for s in entry["supports"]], "verdict": verdicts, "frozen_reader": frozen,
                       "reason": reasons, "legal": entry["by_law"]["parity"]["32"]["legal"],
                       "funded": entry["by_law"]["parity"]["32"]["funded"], "recorded_trace": trace})
    checks["edits_regenerated_equal"] = f"{agree}/{len(starts)}"
    checks["law_verdicts_equal"] = sum(s["verdict"]["parity"] == s["verdict"]["nae"] for s in starts)
    count_table = {f"{law}@{h}": {v: counts[(law, h, v)] for v in ("yes", "no", "unknown")}
                   for law in C.LAWS for h in ("16", "32")}
    gate = all(v == {"yes": 16, "no": 33, "unknown": 4} for v in count_table.values())
    return {"original_supports": data["original_supports"], "starts": starts, "checks": checks,
            "recorded_counts": count_table, "gate_counts_16_33_4": gate}


def q2():
    rows = [json.loads(line) for line in (C.RHS_ART / "draws.jsonl").open()]
    rows = [r for r in rows if r["supply"] == "funded_sensitivity" and r["size_group"] == "9-12"]
    certs = json.loads((C.RHS_ART / "certificates.json").read_text())["proved_draws"]
    cert_by = {(c["extra"], c["draw"]): c for c in certs}
    fix = rhs_survey.fix
    end = rhs_survey.end
    specs = [s for s in rhs_survey.draw_specs() if s["supply"] == "funded_sensitivity" and s["size_group"] == "9-12"]
    spec_by = {(s["extra"], s["draw"]): s for s in specs}
    starts, counts, regen_ok, cert_ok = [], Counter(), 0, 0
    for r in rows:
        stars = fix.source_from([tuple(e) for e in r["edges"]], r["loose"])
        # regenerate with the study's own generator and supply formula (survey.draw_specs, survey.source)
        s = spec_by[(r["extra"], r["draw"])]
        g = nx.Graph()
        g.add_nodes_from(range(s["n"]))
        g.add_edges_from(s["edges"])
        all_live = end.End(dict.fromkeys(range(s["n"]), 1), [tuple(g[w]) for w in g])
        demand = Counter(v for group in end.proposals(all_live) for v in group)
        h = [max(2, 3 - g.degree(v), demand[v]) + s["coins"][v] for v in g]
        regen_ok += ([list(e) for e in s["edges"]] == r["edges"] and h == r["loose"] and s["word"] == r["word"]
                     and s["coins"] == r["coins"])
        verdicts = {}
        for law in C.LAWS:
            yes, unknown = rhs_rates.events(r["laws"][law], 32, True)["underlying_indefinite_recurrence"]
            y16, u16 = rhs_rates.events(r["laws"][law], 16, True)["underlying_indefinite_recurrence"]
            assert (bool(yes), bool(unknown)) == (bool(y16), bool(u16))
            verdicts[law] = "proved_source" if yes else ("unresolved" if unknown else "proved_not")
            counts[(law, verdicts[law])] += 1
        key = (r["extra"], r["draw"])
        if key in cert_by:
            cert_ok += tup(cert_by[key]["holders"]) == tup(stars)
        starts.append({"id": f"Q2-x{r['extra']}-{r['draw']:02d}", "extra": r["extra"], "draw": r["draw"], "n": r["n"],
                       "edges": r["edges"], "loose": r["loose"], "stars": [list(x) for x in stars], "verdict": verdicts,
                       "recorded_widths": {law: [[c["age"], c["width"]] for p in r["laws"][law]["parts"] for c in p["cuts"]]
                                           for law in C.LAWS},
                       "recorded_parts": {law: len(r["laws"][law]["parts"]) for law in C.LAWS}})
    by_extra = Counter((s["extra"], s["verdict"]["parity"]) for s in starts)
    proved = [s["id"] for s in starts if s["verdict"]["parity"] == "proved_source"]
    checks = {"rows": len(rows), "per_extra": dict(Counter(s["extra"] for s in starts)),
              "regenerated_equal": f"{regen_ok}/{len(rows)}", "certificates_equal": f"{cert_ok}/{len(cert_by)}",
              "law_verdicts_equal": sum(s["verdict"]["parity"] == s["verdict"]["nae"] for s in starts),
              "by_extra_and_verdict": {f"+{e}:{v}": n for (e, v), n in sorted(by_extra.items())}, "proved": proved}
    count_table = {law: {v: counts[(law, v)] for v in ("proved_source", "proved_not", "unresolved")} for law in C.LAWS}
    gate = all(count_table[law]["proved_source"] == 5 for law in C.LAWS) and len(rows) == 192
    return {"starts": starts, "checks": checks, "recorded_counts": count_table, "gate_5_of_192": gate}


def main():
    out = {"Q1": q1(), "Q2": q2()}
    C.OUT.mkdir(parents=True, exist_ok=True)
    (C.OUT / "populations.json").write_text(json.dumps(out, sort_keys=True) + "\n")
    report = {k: {kk: vv for kk, vv in v.items() if kk != "starts" and kk != "original_supports"} for k, v in out.items()}
    (C.OUT / "gate_populations.json").write_text(json.dumps(report, indent=1, sort_keys=True) + "\n")
    print(json.dumps(report, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
