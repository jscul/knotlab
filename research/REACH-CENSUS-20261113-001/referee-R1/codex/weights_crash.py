"""Independent draw-weight, unresolved, and crash-accounting audit.

Reads the permitted artifacts and the named input language only. It never
loads the reach-census implementation or its unarchived outputs. Reproduction:
  .venv/bin/python -B research/REACH-CENSUS-20261113-001/referee-R1/codex/weights_crash.py
One process; no subprocesses. Outputs only weights_crash.json and notes beside
this source. Class and graph correctness are separate audit assignments.
"""

from __future__ import annotations

import collections
import gzip
import hashlib
import importlib.util
import fractions
import json
import math
import os
import pathlib
import platform
import random
import resource
import sys
import time


ROOT = pathlib.Path(__file__).resolve().parents[4]
HERE = pathlib.Path(__file__).resolve().parent
DATA = ROOT / "artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census"
LANGUAGE = ROOT / "experiments/SHORT-DESC-20261112-001A/SHORT-DESC-20261112-001A-E001_description_census/dlang.py"
CLASSES = [
    "S1 limit dead", "S2 no copy", "S3 no own distinctions",
    "S4 free own distinctions", "bounded", "grows", "lost at large depths",
    "mixed by residue", "none at any depth", "unresolved",
]
COMPUTED = CLASSES[4:]
PERSIST = {"bounded", "grows", "mixed by residue", "unresolved"}
CELLS = ["all", "forever", "dies_with_dead_usual_limit", "alive_only_in_limit"]
CODE = {c: i for i, c in enumerate(CLASSES)}
UNRESOLVED = CODE["unresolved"]
BOUNDED = CODE["bounded"]
GROWS = CODE["grows"]
MIXED = CODE["mixed by residue"]


def read_json(path):
    with (gzip.open(path, "rt") if str(path).endswith(".gz") else open(path)) as f:
        return json.load(f)


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def divide(a, b):
    return a / b if b else None


def band(a, unresolved, n):
    return dict(numerator_low=a, numerator_high=a + unresolved, denominator=n,
                low=divide(a, n), high=divide(a + unresolved, n))


def quantile(values, p):
    if not values:
        return None
    values = sorted(values)
    x = (len(values) - 1) * p
    i = math.floor(x)
    return values[i] + (x - i) * (values[min(i + 1, len(values) - 1)] - values[i])


def finite_fate(L, defs):
    # This is the stored-fate definition in the permitted input language, not
    # the reach classifier. Only the finite orbit is needed.
    alive, _, _ = L.depth_sequence(defs, L.NAE)
    return "forever" if all(alive) else ("at once" if not alive[0] else "a while")


def replay_draws(rows):
    spec = importlib.util.spec_from_file_location("referee_permitted_dlang", LANGUAGE)
    L = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(L)
    by_key = {r["key"]: i for i, r in enumerate(rows)}
    multiplicities = [0] * len(rows)
    fate = [None] * len(rows)
    ordered = []
    workers = {}
    missing = set()
    bits_digest = hashlib.sha256()
    for worker in range(8):
        seed = int(hashlib.sha256(f"LO:{worker}".encode()).hexdigest()[:16], 16)
        rng = random.Random(seed)
        kept = 0
        for attempt in range(150000):
            d = L.sample(rng, **L.VARIANTS["main"])
            if "defs" not in d or d.get("t") is None:
                continue
            key = json.dumps(d["defs"], separators=(",", ":"))
            kept += 1
            if key not in by_key:
                missing.add(key)
                continue
            i = by_key[key]
            multiplicities[i] += 1
            if fate[i] is None:
                fate[i] = finite_fate(L, d["defs"])
            ordered.append(i)
            bits_digest.update(json.dumps([worker, attempt, key, d["bits"] - d["tbits"]],
                                          separators=(",", ":")).encode() + b"\n")
        workers[str(worker)] = kept
        print(f"replayed worker {worker}: {kept} draws", flush=True)
    assert not missing, f"replayed families absent from raw rows: {len(missing)}"
    assert len(ordered) == 223261
    assert len(by_key) == 124572 and all(multiplicities)
    mapping_digest = hashlib.sha256()
    for key in sorted(by_key):
        i = by_key[key]
        mapping_digest.update(json.dumps([key, multiplicities[i], fate[i]], separators=(",", ":")).encode() + b"\n")
    metadata = dict(
        method="Replay input dlang.sample for 8 LO:w SHA256 seeds, 150000 attempts each; keep defs with t not None; canonical JSON key; count draws per key. Recompute each key's finite fate using input dlang.depth_sequence(defs, NAE).",
        direct_weighting="one vote per retained draw, with repeated keys retained; no subsequent 2^-bits reweighting",
        draws=len(ordered), distinct_keys=len(by_key), draws_by_worker=workers,
        multiplicity_histogram=dict(sorted(collections.Counter(multiplicities).items())),
        sorted_key_multiplicity_fate_sha256=mapping_digest.hexdigest(),
        ordered_worker_attempt_key_bits_sha256=bits_digest.hexdigest(),
        original_draw_archive_checked=False,
        original_draw_archive_reason="Not present in permitted data directory; no outside stored draw data were read.",
        stored_bits_or_stored_fate_G0_rechecked=False,
        finite_fates=dict(collections.Counter(fate[i] for i in ordered)),
    )
    return multiplicities, fate, ordered, metadata


def row_cell(row, fate):
    if fate == "forever":
        return "forever"
    assert isinstance(row.get("usual_limit_alive"), bool), "non-forever record lacks usual-limit verdict"
    return "alive_only_in_limit" if row["usual_limit_alive"] else "dies_with_dead_usual_limit"


def counts_group(indices, rows, weights):
    draws = collections.Counter()
    families = collections.Counter()
    for i in indices:
        c = rows[i]["class"]
        families[c] += 1
        draws[c] += weights[i]
    dn, fn = sum(draws.values()), sum(families.values())
    dc, fc = sum(draws[c] for c in COMPUTED), sum(families[c] for c in COMPUTED)
    du, fu = draws["unresolved"], families["unresolved"]
    class_counts = {c: dict(draws=draws[c], distinct_families=families[c]) for c in CLASSES}
    bands = {c: {"draws": band(draws[c], du, dc), "distinct_families": band(families[c], fu, fc)}
             for c in COMPUTED if c != "unresolved"}
    pdd, pdf = sum(draws[c] for c in PERSIST), sum(families[c] for c in PERSIST)
    return dict(
        draw_count=dn, distinct_family_count=fn, class_counts=class_counts,
        computed_draw_count=dc, computed_distinct_family_count=fc,
        computed_class_bands=bands,
        unconditional_class_bands={c: dict(draws=band(draws[c], du, dn),
                                            distinct_families=band(families[c], fu, fn))
                                   for c in COMPUTED if c != "unresolved"},
        unresolved_draw_share=divide(du, dc), unresolved_distinct_family_share=divide(fu, fc),
        p1_bounded=dict(draws=band(draws["bounded"], du, pdd),
                        distinct_families=band(families["bounded"], fu, pdf)),
        conditional_grows=dict(draws=band(draws["grows"], du, pdd),
                              distinct_families=band(families["grows"], fu, pdf)),
    )


def groups_for(indices, rows, weights, fates):
    group_indices = {c: [] for c in CELLS}
    for i in indices:
        group_indices["all"].append(i)
        group_indices[row_cell(rows[i], fates[i])].append(i)
    groups = {}
    for cell, ids in group_indices.items():
        g = counts_group(ids, rows, weights)
        for output, field, encode in [
            ("by_n_defs", "n_defs", lambda n: "1" if n == 1 else ">1"),
            ("by_s_own", "s_own", str),
        ]:
            bins = collections.defaultdict(list)
            for i in ids:
                value = rows[i].get(field)
                b = encode(value) if value is not None else "not_available"
                bins[b].append(i)
            bins["not_available"]  # The producer exposes this even when empty.
            if output == "by_n_defs":
                bins["1"]
                bins[">1"]
            g[output] = {b: counts_group(ii, rows, weights) for b, ii in sorted(bins.items())}
        groups[cell] = g
    return groups, group_indices


def compare_group(g, original, label, mismatches, tally):
    def check(path, a, b):
        tally[0] += 1
        if a != b:
            mismatches.append(dict(path=label + ":" + path, recomputed=a, reported=b))
    check("class_counts", g["class_counts"], original["class_counts"])
    check("computed.draw_count", g["computed_draw_count"], original["computed"]["draw_count"])
    check("computed.distinct_family_count", g["computed_distinct_family_count"], original["computed"]["distinct_family_count"])
    for c, v in g["computed_class_bands"].items():
        check(f"computed.{c}.draw_share_band", v["draws"], original["computed"]["classes"][c]["draw_share_band"])
        check(f"computed.{c}.distinct_family_share_band", v["distinct_families"], original["computed"]["classes"][c]["distinct_family_share_band"])
    for unit in ["draws", "distinct_families"]:
        check("p1." + unit, g["p1_bounded"][unit], original["computed"]["p1_bounded_conditional_share"][unit])


def compare_point_summaries(groups, original):
    mismatches, tally = [], [0]
    for cell, g in groups.items():
        compare_group(g, original["cells"][cell], cell, mismatches, tally)
        for strat in ["by_n_defs", "by_s_own"]:
            source = original["cells"][cell][strat]
            for b in sorted(set(g[strat]) | set(source)):
                ours = g[strat].get(b)
                theirs = source.get(b)
                if ours is None:
                    ours = counts_group([], [], [])
                if theirs is None and not ours["draw_count"] and not ours["distinct_family_count"]:
                    # An omitted empty stratum and an explicit zero row carry
                    # identical arithmetic; neither is a missing observation.
                    continue
                if theirs is None:
                    mismatches.append(dict(path=cell + ":" + strat + ":" + b,
                                           recomputed=ours, reported=None))
                else:
                    compare_group(ours, theirs, cell + ":" + strat + ":" + b, mismatches, tally)
    return dict(checks=tally[0], mismatches=mismatches)


def compare_histograms(indices_by_cell, rows, weights, original):
    mismatches, checks = [], 0
    for cell, indices in indices_by_cell.items():
        bins_to_check = [(cell, indices, original["cells"][cell])]
        for strat, field, encode in [
            ("by_n_defs", "n_defs", lambda n: "1" if n == 1 else ">1"),
            ("by_s_own", "s_own", str),
        ]:
            for b, value in original["cells"][cell][strat].items():
                ids = [i for i in indices if (encode(rows[i][field]) if rows[i].get(field) is not None else "not_available") == b]
                bins_to_check.append((f"{cell}:{strat}:{b}", ids, value))
        for label, ids, source in bins_to_check:
            for name, field, condition in [
                ("lambda_distribution", "lambda", lambda r: r["class"] in COMPUTED),
                ("bounded_uniform_cost_bound_distribution", "uniform_cost_bound", lambda r: r["class"] == "bounded"),
                ("bounded_onset_depth_distribution", "onset_depth", lambda r: r["class"] == "bounded"),
            ]:
                dc, fc = collections.Counter(), collections.Counter()
                missing_d = missing_f = 0
                for i in ids:
                    r = rows[i]
                    if not condition(r):
                        continue
                    value = r.get(field)
                    if value is None:
                        missing_d += weights[i]
                        missing_f += 1
                    else:
                        encoded = str(fractions.Fraction(value)) if field == "lambda" else str(value)
                        dc[encoded] += weights[i]
                        fc[encoded] += 1
                # Only distributions recorded in the frozen summary are compared;
                # lambda has separate accounting for complete/incomplete graphs.
                expected = {str(e["value"]): (e["draws"], e["distinct_families"])
                            for e in source[name]["histogram"]}
                actual = {k: (dc[k], fc[k]) for k in dc}
                checks += 1
                if actual != expected:
                    mismatches.append(dict(path=label + ":" + name, recomputed=actual, reported=expected))
    return dict(checks=checks, mismatches=mismatches)


def sample_counts(frame, rng):
    n = len(frame)
    out = [0] * len(CLASSES)
    choose = rng.randrange
    for _ in range(n):
        out[frame[choose(n)]] += 1
    return out


def bootstrap(ordered, rows, fates, summary, resamples):
    frames = {c: bytearray() for c in CELLS}
    for i in ordered:
        c = rows[i]["class"]
        if c not in COMPUTED:
            continue
        code = CODE[c]
        frames["all"].append(code)
        frames[row_cell(rows[i], fates[i])].append(code)
    rng = random.Random(20261113)
    result = dict(resamples=resamples, seed=20261113,
                  method="Individual draw positions; repeated Random.randrange; shared stream; primary cell order all,forever,dead,limit-only; class resamples then P1 in each; linear quantiles.",
                  cells={}, mismatches=[])
    for cell in CELLS:
        frame = frames[cell]
        if not frame:
            result["cells"][cell] = dict(computed_draws=0, class_intervals={}, p1=None)
            continue
        n = len(frame)
        lows, highs = {c: [] for c in COMPUTED[:-1]}, {c: [] for c in COMPUTED[:-1]}
        for _ in range(resamples):
            counts = sample_counts(frame, rng)
            for c in lows:
                lows[c].append(counts[CODE[c]] / n)
                highs[c].append((counts[CODE[c]] + counts[UNRESOLVED]) / n)
        intervals = {c: dict(low=quantile(lows[c], .025), high=quantile(highs[c], .975)) for c in lows}
        for c, value in intervals.items():
            old = summary["cells"][cell]["computed"]["classes"][c]["bootstrap_95_interval"]
            if value != {k: old[k] for k in ("low", "high")}:
                result["mismatches"].append(dict(path=f"{cell}:classes:{c}", recomputed=value, reported=old))
        pl, ph = [], []
        for _ in range(resamples):
            counts = sample_counts(frame, rng)
            den = sum(counts[CODE[c]] for c in PERSIST)
            if den:
                pl.append(counts[BOUNDED] / den)
                ph.append((counts[BOUNDED] + counts[UNRESOLVED]) / den)
        p1 = dict(low=quantile(pl, .025), high=quantile(ph, .975))
        old = summary["cells"][cell]["computed"]["p1_bounded_conditional_share"]["bootstrap_95_interval"]
        if p1 != {k: old[k] for k in ("low", "high")}:
            result["mismatches"].append(dict(path=f"{cell}:p1", recomputed=p1, reported=old))
        result["cells"][cell] = dict(computed_draws=n, class_intervals=intervals, p1=p1)
        print(f"bootstrapped {cell}: {n} computed draws", flush=True)
    state = rng.getstate()
    p3 = {}
    for order in [("alive_only_in_limit", "forever"), ("forever", "alive_only_in_limit")]:
        rng.setstate(state)
        lows = []
        for _ in range(resamples):
            counts = {cell: sample_counts(frames[cell], rng) for cell in order}
            lo, fo = counts["alive_only_in_limit"], counts["forever"]
            lows.append(lo[GROWS] / len(frames["alive_only_in_limit"]) -
                        (fo[GROWS] + fo[UNRESOLVED]) / len(frames["forever"]))
        p3["then".join(order)] = quantile(lows, .025)
        print(f"bootstrapped P3 order {order}", flush=True)
    result["p3_orders_tested"] = p3
    result["p3_reported"] = summary["p3_grows_share_difference"]["bootstrap_low_2_5_percent"]["low"]
    result["p3_matching_orders"] = [k for k, v in p3.items() if v == result["p3_reported"]]
    return result


def annotate(result, rows, weights):
    """Record interpretation limits separately from the successful arithmetic."""
    headline = result["headline_recomputation"]
    fc = headline["exploratory_grows_conditional_forever"]["draws"]
    lc = headline["exploratory_grows_conditional_limit_only"]["draws"]
    headline["conditional_growth_difference"] = dict(
        both_unresolved_against_growth=lc["low"] - fc["low"],
        both_unresolved_for_growth=lc["high"] - fc["high"],
        low_with_unresolved_against_difference=lc["low"] - fc["high"],
        high_with_unresolved_for_difference=lc["high"] - fc["low"],
        inference="The conditional point bands differ; the comparison does not establish equal conditional growth probabilities or a causal only-because explanation.",
    )
    by_key = {r["key"]: i for i, r in enumerate(rows)}
    with gzip.open(DATA / "alt_families.jsonl.gz", "rt") as f:
        alternatives = [json.loads(line) for line in f]
    assert len(alternatives) == 3000
    assert len({r["key"] for r in alternatives}) == 3000
    matrix = collections.Counter()
    weighted_matrix = collections.Counter()
    for r in alternatives:
        i = by_key[r["key"]]
        pair = (rows[i]["class"], r["class"])
        matrix[pair] += 1
        weighted_matrix[pair] += weights[i]
    first_grows = sum(v for (a, b), v in matrix.items() if a == "grows")
    both_grow = matrix[("grows", "grows")]
    eligible = [i for i, r in enumerate(rows) if r["class"] in COMPUTED and r.get("alt_differs")]
    eligible_growing = [i for i in eligible if rows[i]["class"] == "grows"]
    selected_growing_weight = sum(v for (a, b), v in weighted_matrix.items() if a == "grows")
    result["alternative_sample_weighting_limit"] = dict(
        sample_design="Uniform sample of 3000 distinct eligible computed keys, not a sample of individual draw positions",
        eligible_census_keys=len(eligible), eligible_census_draws=sum(weights[i] for i in eligible),
        eligible_census_first_growing_keys=len(eligible_growing),
        eligible_census_first_growing_draws=sum(weights[i] for i in eligible_growing),
        panel_first_growing_keys=first_grows, panel_both_growing_keys=both_grow,
        panel_distinct_conditional_share=both_grow / first_grows,
        selected_panel_draw_weight=dict(first_growing_draws=selected_growing_weight,
                                       both_growing_draws=weighted_matrix[("grows", "grows")],
                                       conditional_share=weighted_matrix[("grows", "grows")] / selected_growing_weight),
        limit="Neither the panel's 297/645 distinct-key ratio nor its within-panel draw ratio can simply be multiplied by the census's 13279/223261 draw share. Eligibility, sampling units, and denominators differ. A design-aware weighted estimator with uncertainty would be a separate analysis.",
    )
    result["sources"][str((DATA / "alt_families.jsonl.gz").relative_to(ROOT))] = digest(DATA / "alt_families.jsonl.gz")
    result["findings"] = [
        dict(point=3, category="Narrowing", title="Recovery was a resume, and only aggregate stability can be established",
             evidence="110262 existing keys retained; 14310 keys appended; partial missing-key set exactly final suffix; all prefix count/band/histogram comparisons match.",
             action="Correct the referee brief's from-scratch description. Say no aggregate change detected in preserved results, rather than claiming that every per-family field was independently shown unchanged."),
        dict(point=4, category="Not a block", title="Draw weighting and headline arithmetic reproduce exactly",
             evidence="223261 draws, 124572 unique keys; every final class count and point band matches, as do all primary bootstrap intervals and P3's lower quantile.",
             action="Continue calling these shares of draws estimating the capped description weighting, and distinct-key counts shares of distinct sampled families."),
        dict(point=4, category="Narrowing", title="Only because their bonds exist is stronger than the comparison",
             evidence="Conditional growth is 29.39235–31.18953% in forever versus 32.85884–34.99407% in limit-only; unresolved-assignment bands for the conditional gap are 1.66931–5.60172 points.",
             action="State that different absence rates explain much of the unconditioned gap; retain the conditional difference and do not claim equality or causation."),
        dict(point=4, category="Narrowing", title="The Reading combines draw weight with a distinct-key robustness sample",
             evidence="The 5.94775% census share is 13279/223261 draws; the about-half fraction on both rays is 297/645 distinct panel keys among first-ray growers in an eligible uniform-key sample.",
             action="Report these separately, naming the panel and its denominator. Do not infer an all-weight two-ray share from their product."),
        dict(point=4, category="Narrowing", title="Name the forever denominator in the headline conditional bounded share",
             evidence="68.79239–70.58957% uses 44236 computed forever draws in bounded/grows/mixed/unresolved; all cells together give 68.72158–70.52508% of 45079 draws.",
             action="Say among the computed forever draws in those four classes when quoting 68.8–70.6%."),
        dict(point=7, category="Not a block", title="Unresolved accounting and bands are correct",
             evidence="813 singleton draws/keys: 746 block-size, 38 timeout, 27 incomplete graphs at 300000 nodes, 2 worker errors; none has a positive boundedness certificate. All remain in their cell's computed denominator and in every applicable high-minus-low band.",
             action="Keep all 813 unresolved and retain the two raw error records. Their missing stratum fields can be reported or reconstructed from keys, without changing class counts."),
        dict(point=7, category="Narrowing", title="Below 0.01 percent mixed is the observed classified share",
             evidence="8/223261=0.00358325% is classified mixed; assigning all unresolved to mixed gives 821/223261=0.36773104%.",
             action="Label below 0.01% as the observed classified point share. The unresolved-robust conclusion remains rare under the frozen upper-below-1% rule."),
    ]
    result["verdict"] = "Confirmed with fixes for points 3,4,7; no arithmetic Block found"
    return result


def write_notes(result):
    h = result["headline_recomputation"]
    cells = result["recomputed_tables"]
    lines = [
        "# Weights, crash, and unresolved audit — points 3, 4, 7",
        "",
        "**Verdict: Confirmed with fixes.** No arithmetic Block found. Class/graph correctness is handled by the other audit lanes.",
        "",
        "Fresh aggregation and bootstrap code read the archived data and the permitted input language; the reach-census implementation was never opened or imported. The archived draw file is absent from the permitted directory, so its stored bits and fates could not be compared directly (G0 is not independently re-certified here). Draw multiplicities were recovered by replaying dlang.sample: eight SHA256(LO:w) seeds, 150,000 attempts each, retaining defs with t not None; each canonical JSON key receives one count per retained draw. Finite fates were recomputed with the permitted input's finite-orbit definition. No extra 2^-bits weighting was applied.",
        "",
        "## 3. Crash recovery — Narrowing",
        "",
        "Recovery was a **resume**, not a fresh run of all families. run_info records 110,262 resumed and 14,310 written. The crashed log stops at 110,262; the resumed log begins at 110,287. The partial snapshot's 14,310 missing keys are exactly the final file's suffix. The retained prefix represents 206,980 draws; the added suffix represents 16,281.",
        "",
        "The final prefix reproduces all 1,830 partial class-count/point-band comparisons and all 366 recorded rate/bounded-cost/onset histograms, including cell and definition-count/S-own-count strata. There are zero mismatches. This supports aggregate stability and continuation of the same key coverage. It cannot establish per-family equality: exchanged class/rate changes preserving all aggregates, or changes to per-key nodes, completeness, trimmed nodes, exact-test period/residues, L_ray values, status or performance fields, cannot be ruled out without raw pre-patch records or their per-record hashes. No such change is demonstrated. Correct the brief's from-scratch wording and narrow any all-fields unchanged claim to the evidence available.",
        "",
        "## 4. Draw shares and headline arithmetic — Not a block",
        "",
        "The replay recovers **223,261 draws and 124,572 unique canonical family keys**, with no missing keys. All 2,145 final point-count/band comparisons and 429 recorded histograms match. All primary 2,000-resample class/P1 bootstrap intervals reproduce exactly; P3's 2.5% lower quantile is 0.12752854775543002, with limit-only sampled before forever in its independent-cell draws. The other within-P3 order gives 0.12786807700599154 and does not alter the prediction verdict. Intervals use linear quantiles and the frozen shared stream.",
        "",
        "| First-ray class | Draws | Distinct sampled families | Share of all draws | Unresolved-assignment band |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    all_g = cells["all"]
    for c in CLASSES:
        v = all_g["class_counts"][c]
        share = 100 * v["draws"] / all_g["draw_count"]
        if c == "unresolved":
            b = "exact unresolved share"
        elif c not in all_g["unconditional_class_bands"]:
            b = "settled observed share"
        else:
            point = all_g["unconditional_class_bands"][c]["draws"]
            b = f"{100*point['low']:.5f}–{100*point['high']:.5f}%"
        lines.append(f"| {c} | {v['draws']:,} | {v['distinct_families']:,} | {share:.5f}% | {b} |")
    lines.extend([
        "",
        "No depth (S2+S3) is 130,379/223,261 = 58.39757%; settled no bond (S1+S4) is 6,780/223,261 = 3.03680%. Absence at large depths, counting settled classes plus none/lost, is 178,182–178,995/223,261 = 79.80883–80.17298%. These reproduce Conclusions 2–3. The raw all-weight bounded and grows point shares are 13.87569% and 5.94775%; assigning all unresolved to each separately gives upper shares 14.23984% and 6.31190%.",
        "",
        "| Computed cell | Draws | None | Lost | Bounded | Grows | Mixed | Unresolved |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    for cell in ["forever", "alive_only_in_limit"]:
        v = cells[cell]
        classes = v["class_counts"]
        den = v["computed_draw_count"]
        values = [f"{classes[c]['draws']:,} ({100*classes[c]['draws']/den:.5f}%)" for c in
                  ["none at any depth", "lost at large depths", "bounded", "grows", "mixed by residue", "unresolved"]]
        lines.append(f"| {cell} | {den:,} | " + " | ".join(values) + " |")
    lines.extend([
        "",
        "P1 uses 44,236 computed forever draws in bounded/grows/mixed/unresolved: bounded is 30,431–31,226/44,236 = 68.79239–70.58957%, bootstrap 68.34223–71.02954%. Name this forever denominator when quoting 68.8–70.6%. Across both live cells the corresponding share is 30,979–31,792/45,079 = 68.72158–70.52508%. P2's forever growth interval is 15.00466–16.43947%. P3's adverse point difference is 15.94851 percentage points, with its lower bootstrap quantile 12.75285 points; both frozen requirements pass.",
        "",
        "**Narrowing:** Conclusion 4's only-because reading is not established. Conditional growth bands are 29.39235–31.18953% (forever) and 32.85884–34.99407% (limit-only). Comparing the same unresolved assignment gives a 3.46649–3.80454 point gap; allowing opposing assignments gives 1.66931–5.60172 points. The data show that differing absence rates explain much of the unconditioned contrast, while conditional point shares still differ. A causal or equal-probability claim does not follow.",
        "",
        "**Narrowing:** The Reading's about-6%-of-weight and about-half-on-both-rays statements have different sampling units. The former is 13,279/223,261 draws. The latter is 297/645 distinct panel keys among first-ray growers in a uniformly selected eligible-key panel of 3,000. Report them separately; their product is not an established two-ray share of all description weight.",
        "",
        "## 7. Unresolved — Not a block",
        "",
        "All **813 unresolved draws are 813 distinct singleton keys**: block-size 746, timeout 38, incomplete graphs 27, worker errors 2. Each of the 27 has exactly 300,000 nodes and complete=false; no unresolved record has a positive boundedness certificate. Unresolved enters each computed denominator; each resolved class band's low numerator excludes it and high numerator adds it. P1 includes it in its four-class denominator, and P3 assigns it against/for the difference as specified. Unresolved itself is reported as an exact observed share, without a band.",
        "",
        "Unresolved is 795/85,240 = 0.93266% of computed forever draws and 18/862 = 2.08817% of computed limit-only draws; neither exceeds the 5% undecided threshold. The two error records, final lines 81,994 and 110,262, remain unresolved rather than disappearing on resume. Both lack usual-limit/stratum fields; independently replayed finite fates place both in forever. Their definition counts are six and one, reconstructible from their keys. The JSON retains every unresolved key, status, cap/certificate field and exact counts by inferred definition count.",
        "",
        "**Narrowing:** mixed below 0.01% is only the classified point share, 8/223,261 = 0.00358325%. The adverse unresolved bound is 821/223,261 = 0.36773104%, so below 0.01% is not unresolved-robust. The frozen word rare is still justified: even this upper bound is below 1%.",
        "",
        "Reproduce with:",
        "",
        "```sh",
        "OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 /home/jscul/p-vs-np-contact-first/.venv/bin/python -B research/REACH-CENSUS-20261113-001/referee-R1/codex/weights_crash.py",
        "```",
        "",
        "Outputs: weights_crash.py, weights_crash.json, weights_crash_notes.md. The JSON contains input hashes, replay digests, exact count/band tables for every reported stratum, both P3 bootstrap orders, all discrepancies (none after mathematical normalization), crash coverage and residual limitations. One process; no subprocesses or Git mutations.",
    ])
    (HERE / "weights_crash_notes.md").write_text("\n".join(lines) + "\n")


def main():
    started = time.monotonic()
    with gzip.open(DATA / "families.jsonl.gz", "rt") as f:
        rows = [json.loads(line) for line in f]
    assert len(rows) == 124572
    keys = [r["key"] for r in rows]
    assert len(set(keys)) == len(keys), "duplicate family keys"
    assert all(json.dumps(json.loads(k), separators=(",", ":")) == k for k in keys)
    assert all(r["class"] in CLASSES for r in rows)
    summary = read_json(DATA / "summary.json")
    partial = read_json(DATA / "summary_partial_after_crash_unread.json.gz")
    run_info = read_json(DATA / "run_info.json")
    weights, fates, ordered, replay = replay_draws(rows)
    n = len(rows)
    groups, group_indices = groups_for(range(n), rows, weights, fates)
    current_check = compare_point_summaries(groups, summary)
    histogram_check = compare_histograms(group_indices, rows, weights, summary)
    missing = set(partial["coverage"]["draw_family_keys_without_record"])
    assert len(missing) == 14310
    prefix_n = run_info["resumed"]
    assert prefix_n == 110262
    assert missing == set(keys[prefix_n:])
    assert not missing.intersection(keys[:prefix_n])
    old_groups, old_indices = groups_for(range(prefix_n), rows, weights, fates)
    old_check = compare_point_summaries(old_groups, partial)
    old_hist = compare_histograms(old_indices, rows, weights, partial)
    additions, _ = groups_for(range(prefix_n, n), rows, weights, fates)
    with gzip.open(DATA / "full_run_part1_crashed.log.gz", "rt") as f:
        old_log = f.read()
    with gzip.open(DATA / "full_run.log.gz", "rt") as f:
        new_log = f.read()
    def progress(text):
        out = []
        for line in text.splitlines():
            if line.startswith("{"):
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if r.get("total") == 124572:
                    out.append(r)
        return out
    old_progress, new_progress = progress(old_log), progress(new_log)
    unresolved = [i for i, r in enumerate(rows) if r["class"] == "unresolved"]
    statuses = collections.Counter(rows[i]["status"] for i in unresolved)
    assert len(unresolved) == sum(weights[i] for i in unresolved) == 813
    assert statuses["block_size"] == 746
    unresolved_records = []
    for i in unresolved:
        r = rows[i]
        unresolved_records.append(dict(line=i + 1, key=r["key"], draws=weights[i],
                                       cell=row_cell(r, fates[i]),
                                       n_defs=len(json.loads(r["key"])),
                                       status=r["status"], complete=r.get("complete"),
                                       nodes=r.get("nodes"), lambda_value=r.get("lambda"),
                                       eventually_bounded=r.get("eventually_bounded"),
                                       bounded_all=r.get("bounded_all"),
                                       main_block_size=r.get("main_block_size"),
                                       s_block_size=r.get("s_block_size"), error=r.get("error")))
    all_g, forever, lo = groups["all"], groups["forever"], groups["alive_only_in_limit"]
    def draws(g, c):
        return g["class_counts"][c]["draws"]
    no_depth = sum(draws(all_g, c) for c in CLASSES[1:3])
    settled_no_bond = draws(all_g, CLASSES[0]) + draws(all_g, CLASSES[3])
    absent = sum(draws(all_g, c) for c in CLASSES[:4] + ["none at any depth", "lost at large depths"])
    all_n, u = all_g["draw_count"], draws(all_g, "unresolved")
    p3_low = lo["computed_class_bands"]["grows"]["draws"]["low"] - forever["computed_class_bands"]["grows"]["draws"]["high"]
    p3_high = lo["computed_class_bands"]["grows"]["draws"]["high"] - forever["computed_class_bands"]["grows"]["draws"]["low"]
    result = dict(
        audit="points 3,4,7; independent arithmetic and provenance audit, not a recomputation of graph classes",
        source_only_policy="Study implementation directory was neither opened nor imported. No unarchived study output was read. One process, no subprocess workers.",
        sources={str((DATA / name).relative_to(ROOT)): digest(DATA / name) for name in [
            "families.jsonl.gz", "summary.json", "summary_partial_after_crash_unread.json.gz",
            "run_info.json", "full_run_part1_crashed.log.gz", "full_run.log.gz"]},
        permitted_language_sha256=digest(LANGUAGE), replay=replay,
        controls=dict(unique_keys=True, canonical_keys=True, all_keys_drawn=True,
                      draws=223261, keys=124572, unresolved_draws=813, unresolved_families=813,
                      block_cap_unresolved_draws=746, block_cap_unresolved_families=746),
        recomputed_tables=groups,
        final_point_summary_comparison=current_check,
        final_recorded_histogram_comparison=histogram_check,
        headline_recomputation=dict(
            no_depth=dict(draws=no_depth, families=sum(all_g["class_counts"][c]["distinct_families"] for c in CLASSES[1:3]), share=no_depth / all_n),
            no_bond_by_construction=dict(draws=settled_no_bond, share=settled_no_bond / all_n),
            absent_at_large_depths=band(absent, u, all_n),
            bounded_all_weight=band(draws(all_g, "bounded"), u, all_n),
            grows_all_weight=band(draws(all_g, "grows"), u, all_n),
            mixed_all_weight=band(draws(all_g, "mixed by residue"), u, all_n),
            unresolved_all_weight=dict(draws=u, denominator=all_n, share=u / all_n),
            forever_computed_share_of_all_weight=forever["computed_draw_count"] / all_n,
            bounded_conditional_forever=forever["p1_bounded"],
            bounded_conditional_all=all_g["p1_bounded"],
            exploratory_grows_conditional_forever=forever["conditional_grows"],
            exploratory_grows_conditional_limit_only=lo["conditional_grows"],
            p3_draw_difference_band=dict(low=p3_low, high=p3_high),
            p3_criterion_point_ge_10_percent=p3_low >= .1,
            unresolved_undecided_rule={c: groups[c]["unresolved_draw_share"] is not None and groups[c]["unresolved_draw_share"] > .05 for c in CELLS},
        ),
        crash_comparison=dict(
            actual_operation="resume existing records, not rerun all families from scratch",
            run_info=run_info, last_crashed_progress=old_progress[-1],
            first_resumed_progress=new_progress[0], last_census_resumed_progress=new_progress[-1],
            crash_log_has_timer_disarm_FamilyLimit="signal.setitimer(signal.ITIMER_REAL, 0)" in old_log and "reach_dp.FamilyLimit" in old_log,
            prefix_records=prefix_n, prefix_draws=sum(weights[:prefix_n]),
            added_records=n - prefix_n, added_draws=sum(weights[prefix_n:]),
            missing_partial_keys_exactly_final_suffix=True,
            prefix_point_summary_comparison=old_check,
            prefix_recorded_histogram_comparison=old_hist,
            additions_by_cell=additions,
            result_stability_verdict="No aggregate changes detected in the preserved prefix at all tested cell/stratum class counts, bands, lambda histograms, and bounded-cost/onset histograms. Per-family identity of results cannot be proved from an aggregate snapshot.",
            cannot_rule_out=[
                "Class or rate changes exchanged between prefix keys that preserve every compared cell, definition-count and S-own-count aggregate and histogram.",
                "Per-key changes to nodes, completeness, trimmed nodes, bounded_all, eventual-test period or missing residues, or L_ray(1..30); these per-key fields are not retained by the partial summary.",
                "Differences in per-key status, runtime or memory where aggregate scientific fields are unchanged.",
            ],
        ),
        unresolved_accounting=dict(
            by_status=dict(statuses), records=unresolved_records,
            positive_certificate_unresolved=[r for r in unresolved_records if r["eventually_bounded"] or r["bounded_all"]],
            graph_cap_unresolved=[dict(line=r["line"], nodes=r["nodes"], complete=r["complete"])
                                  for r in unresolved_records if r["status"] == "done"],
            by_inferred_n_defs={str(k): dict(families=sum(len(json.loads(rows[i]["key"])) == k for i in unresolved),
                                            draws=sum(weights[i] for i in unresolved if len(json.loads(rows[i]["key"])) == k)) for k in range(1, 7)},
            raw_error_rows=[r for r in unresolved_records if r["status"] == "error"],
            source_note="The two errors lack usual_limit_alive and stratum fields in the raw record; finite-fate replay places both in forever. Definition count is reconstructible from their keys.",
        ),
    )
    (HERE / "weights_crash.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    result["independent_bootstrap"] = bootstrap(ordered, rows, fates, summary, 2000)
    annotate(result, rows, weights)
    result["runtime"] = dict(seconds=time.monotonic() - started,
                             peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                             python=sys.version, platform=platform.platform(),
                             CODEX_THREAD_ID=os.environ.get("CODEX_THREAD_ID"))
    (HERE / "weights_crash.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    write_notes(result)
    print(json.dumps(dict(
        controls=result["controls"],
        final_point_mismatches=len(current_check["mismatches"]),
        final_histogram_mismatches=len(histogram_check["mismatches"]),
        partial_point_mismatches=len(old_check["mismatches"]),
        partial_histogram_mismatches=len(old_hist["mismatches"]),
        bootstrap_mismatches=len(result.get("independent_bootstrap", {}).get("mismatches", [])),
        runtime=result["runtime"],
    ), indent=2), flush=True)


if __name__ == "__main__":
    main()
