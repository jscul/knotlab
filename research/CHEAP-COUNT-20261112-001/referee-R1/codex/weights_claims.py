"""Independent arithmetic/description/claim audit of CHEAP-COUNT.

Interface: read the frozen note and original JSON only; never import/call census.py.
Compute ideal code self-information, labelled-template embeddings, strict-NAE
boundary validity and equality-repair cost. Reclassify stored life strings; do
not independently reproduce S1 optimality or S2/S3 satisfiability (other lanes).
Write only sibling weights_claims.json. Standard library; finite tiny checks.

Run from any directory with the repository's .venv/bin/python -B.
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import resource
import sys
import time


ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).with_suffix(".json")
DATA = ROOT / "artifacts/CHEAP-COUNT-20261112-001A/CHEAP-COUNT-20261112-001A-E001_cheapest_counter"
STUDY = ROOT / "research/CHEAP-COUNT-20261112-001"
RULES = {
    "rule 60": ("new", "old-1", "old0", "R"),
    "rule 90": ("new", "old-1", "old+1", "R"),
    "rule 150": ("new", "old-1", "old0", "old+1"),
    "rule 102": ("new", "old0", "old+1", "R"),
    "hop": ("new", "half", "old0", "R"),
}


def gamma_length(n):
    if n < 1:
        raise ValueError("Elias gamma requires n >= 1")
    return 2 * n.bit_length() - 1


def arithmetic(h, m, n_known=None):
    slots = 5 * (1 + h) + 1
    triples = math.comb(slots, 3)
    choices = math.comb(triples, m)
    header = gamma_length(h) + gamma_length(m + 1)
    ideal = header + math.log2(choices)
    result = {
        "h": h,
        "m": m,
        "relative_slots": slots,
        "available_triples": triples,
        "m_subset_choices": str(choices),
        "gamma_h_bits": gamma_length(h),
        "gamma_m_plus_1_bits": gamma_length(m + 1),
        "ideal_self_information_bits": ideal,
        "literal_fixed_width_code_bits": header + (choices - 1).bit_length(),
    }
    if n_known is not None:
        weight = Fraction(n_known, (1 << header) * choices)
        result.update({"known_template_count_for_arithmetic_only": n_known,
                       "known_template_mass_fraction": str(weight),
                       "known_template_mass": float(weight),
                       "known_template_log2_mass": math.log2(n_known) - ideal,
                       "conditional_template_fraction_at_this_h_m": float(Fraction(n_known, choices))})
    return result


def canonical(gadget):
    return tuple(sorted(tuple(sorted(k)) for k in gadget))


def projected_states(gadget, f=3):
    return {
        state[:4]
        for state in itertools.product((0, 1), repeat=4 + f)
        if all(len({state[v] for v in knot}) > 1 for knot in gadget)
    }


def orbit_closure(stored):
    # Independent reconstruction of the labelled family from the stored 50.
    # This checks each recovered member, but is not an exhaustiveness proof.
    out = set()
    for gadget in stored:
        for named in itertools.permutations(range(4)):
            for helpers in itertools.permutations(range(4, 7)):
                mapping = named + helpers
                out.add(canonical(tuple(mapping[v] for v in knot) for knot in gadget))
    return sorted(out)


def embedded(gadget, rule, h=3):
    # Slot blocks: old i-1, old i, old i+1, new i-1, new i; then R.
    width = 1 + h
    mains = {"old-1": 0, "old0": width, "old+1": 2 * width,
             "new-1": 3 * width, "new": 4 * width, "R": 5 * width}
    mapping = tuple(mains[s] for s in RULES[rule]) + tuple(4 * width + j for j in range(1, h + 1))
    assert len(set(mapping)) == 7
    return canonical(tuple(mapping[v] for v in knot) for knot in gadget)


def actual_named_slots(rule, old_length, position):
    old = [("old", j) for j in range(old_length)]
    values = {"new": ("new", position), "R": ("R", 0)}
    for slot, j in (("old-1", position - 1), ("old0", position),
                    ("old+1", position + 1), ("half", position // 2)):
        values[slot] = old[j] if 0 <= j < old_length else values["R"]
    return tuple(values[s] for s in RULES[rule])


def raw_boundary_valid(gadget, rule):
    # For old length L >= 3, the only possible equalities of named slots are
    # present already for these L; check additional large representatives.
    for length in (3, 4, 67):
        for i in range(length + 1):
            named = actual_named_slots(rule, length, i)
            mapping = named + tuple(("helper", h) for h in range(3))
            if any(len({mapping[v] for v in knot}) != 3 for knot in gadget):
                return False
    return True


def equality_check():
    # Two four-knot inequality definitions sharing the middle distinction.
    # Variables x,y,m,a,b,c,d,e,f. This verifies eq uses seven helpers.
    constraints = ((0, 2, 3), (0, 2, 4), (0, 2, 5), (3, 4, 5),
                   (2, 1, 6), (2, 1, 7), (2, 1, 8), (6, 7, 8))
    relation = {
        s[:2] for s in itertools.product((0, 1), repeat=9)
        if all(len({s[v] for v in k}) > 1 for k in constraints)
    }
    assert relation == {(0, 0), (1, 1)}
    weakened = tuple(k for k in constraints if k != (3, 4, 5))
    wrong_relation = {
        s[:2] for s in itertools.product((0, 1), repeat=9)
        if all(len({s[v] for v in k}) > 1 for k in weakened)
    }
    assert wrong_relation == set(itertools.product((0, 1), repeat=2))
    return {"relation": sorted(relation), "constraints": 8,
            "internal_helpers": 7, "helpers_including_new_tied_copy": 8,
            "negative_control_removed_one_nae_relation": sorted(wrong_relation),
            "negative_control_rejected_as_equality": wrong_relation != relation}


def boundary_inventory(rule, depth=64, h=3, m=12):
    repeats = 0
    repeated_positions = 0
    for r in range(1, depth + 1):
        length = 2 + r
        for i in range(length + 1):
            named = actual_named_slots(rule, length, i)
            n = 4 - len(set(named))
            repeats += n
            repeated_positions += bool(n)
    position_updates = 3 * depth + depth * (depth + 1) // 2
    mains = 3 * (depth + 1) + depth * (depth + 1) // 2
    return {
        "depth": depth,
        "position_updates": position_updates,
        "positions_with_collision": repeated_positions,
        "tied_copies_inserted_by_census_policy": repeats,
        "added_nae_constraints": 8 * repeats,
        "added_used_distinctions": 8 * repeats,
        "total_used_distinctions_including_global_R": mains + h * position_updates + 1 + 8 * repeats,
        "total_nae_constraints_including_last_generation_closure": m * position_updates + 8 * repeats + depth + 1,
        "scope": "Structural inventory of the disclosed always-copy policy; no SAT execution; excludes accidentally allocated unused IDs.",
    }


def classify_string(sequence):
    if len(set(sequence)) == 1:
        return {"class": "constant", "period": 1, "tail_start_depth": 1}
    for period in range(1, 17):
        for start in range(32):
            if sequence[start:len(sequence) - period] == sequence[start + period:]:
                return {"class": "eventually constant" if period == 1 else f"period {period}",
                        "period": period, "tail_start_depth": start + 1}
    return {"class": "unexplained", "period": None, "tail_start_depth": None}


SOURCES = [
    {
        "title": "Martin, Odlyzko and Wolfram, Algebraic Properties of Cellular Automata (1984), author-hosted reprint",
        "url": "https://www-users.cse.umn.edu/~odlyzko/doc/arch/cellular.automata.pdf",
        "verified_locations": "Sections 2, 3A, 4A and 4F; reprint pp. 75-77, 90-91, 99-101; PDF pages 5-7, 20, 29-31.",
        "establishes": "Additive cellular automata have a polynomial representation; rule 90 uses x+x^-1 and rule 150 uses x+1+x^-1. The paper analyzes finite fixed-size systems, primarily periodic boundaries, and also certain twisted/fixed boundaries.",
        "does_not_establish_in_this_audit": "No verified statement for a width-3 seed growing by one position per generation and NAE closure of every consecutive triple of the last generation. The study's exact life bands or nonperiodicity require an explicit transfer/derivation.",
        "authority": "Primary paper, background only; not admitted as new proof lineage.",
    },
    {
        "title": "Elmar Boehler, Algebraic Closures in Complexity Theory (2005), doctoral dissertation",
        "url": "https://d-nb.info/978707176/34",
        "verified_locations": "Definition 3.11 / Proposition 3.12 (p. 37), complementive IN2 discussion (p. 39), Figure 3.5 IN2 row (p. 44; PDF page 44).",
        "establishes": "The IN2 co-clone consists of complementive relations and has NAE3 as a base; the displayed alternative base includes EVEN4. The closure corresponds to existential conjunction with equality, allowing variable identification. Thus ordinary pp-definability of EVEN4 from NAE3 is standard.",
        "does_not_establish_in_this_audit": "No optimum knot/helper count, enumeration of exact positive strict-distinct gadgets, custom growth boundary result or novelty claim.",
        "authority": "Primary author source, background only; not admitted as new proof lineage.",
    },
    {
        "title": "Boehler, Reith, Schnoor and Vollmer, Bases for Boolean co-clones (2005), publisher record",
        "url": "https://www.sciencedirect.com/science/article/pii/S0020019005001614",
        "doi": "10.1016/j.ipl.2005.06.003",
        "verified_locations": "Search-visible publisher title, authors, date and abstract; full text open returned 403.",
        "establishes": "Bibliographic identity and scope: finite simple bases for Boolean co-clones. The author's dissertation supplies the accessible table used above.",
        "does_not_establish_in_this_audit": "The inaccessible publisher full text was not used to verify a particular gadget or size bound.",
        "authority": "Primary publisher metadata; no precise-boundary theorem attributed to it.",
    },
]


def main():
    started = time.perf_counter()
    s1 = json.loads((DATA / "s1.json").read_text())
    s2 = json.loads((DATA / "s2.json").read_text())
    summary = json.loads((DATA / "summary.json").read_text())
    original_gadgets = s1["gadgets"]
    recovered = orbit_closure(original_gadgets)
    even = {s for s in itertools.product((0, 1), repeat=4) if sum(s) % 2 == 0}
    assert len(original_gadgets) == 50
    assert len(recovered) == 168
    assert all(len(g) == 12 and projected_states(g) == even for g in recovered)
    assert all(set(itertools.chain.from_iterable(g)) == set(range(7)) for g in recovered)
    templates = {(rule, g): embedded(g, rule) for rule in ("rule 60", "rule 90", "rule 150") for g in recovered}
    assert len(set(templates.values())) == 504
    raw_valid = {rule: sum(raw_boundary_valid(g, rule) for g in recovered)
                 for rule in ("rule 60", "rule 90", "rule 150")}
    assert raw_valid == {"rule 60": 12, "rule 90": 12, "rule 150": 48}
    weights = [arithmetic(3, 12, 504), arithmetic(4, 10)]
    assert round(weights[0]["ideal_self_information_bits"], 2) == summary["description_bits"]
    assert round(weights[0]["known_template_log2_mass"], 2) == summary["weight_share_log2"]
    weights[1]["count_caveat"] = "Only length recomputed; no h=4 enumeration was performed in the original study."
    life = {}
    for rule, row in s2.items():
        sequence = row["direct"]
        depths = [j + 1 for j, bit in enumerate(sequence) if bit == "1"]
        measured = classify_string(sequence)
        assert len(sequence) == 64
        assert depths == row["alive_depths"]
        assert measured["class"] == row["cls"]
        life[rule] = {"stored_sequence": sequence, "alive_depths": depths, **measured,
                      "independent_sat_recomputation": False}
    assert life["hop"]["tail_start_depth"] == 12
    mutant_rows = [json.loads(line) for file in sorted(DATA.glob("s3_*.jsonl"))
                   for line in file.read_text().splitlines() if line]
    mutant_counts = dict(Counter(row["cls"] for row in mutant_rows))
    assert len(mutant_rows) == 240
    assert mutant_counts == summary["mutant_classes"]
    assertions = {
        "formula_arithmetic_matches_original_summary": True,
        "recovered_168_relabelled_gadgets_each_project_to_even_parity": True,
        "formal_local_embedding_is_injective_for_all_504": True,
        "raw_strict_NAE_templates_without_collision_repair": raw_valid,
        "equality_repair_truth_table": equality_check(),
        "stored_life_strings_match_original_finite_classifier": True,
        "mutant_class_inventory_matches_summary_not_independent_SAT": mutant_counts,
    }
    weakened_parity = projected_states(recovered[0][1:])
    assert weakened_parity != even
    assertions["negative_control_one_deleted_nae_rejected_as_parity"] = {
        "relation_size": len(weakened_parity), "rejected": weakened_parity != even}
    result = {
        "scope_kind": "epic",
        "scope_id": "CHEAP-COUNT-20261112-001",
        "audit_lane": "weights_claims",
        "verdict": "Confirmed with fixes: arithmetic and formal template injectivity pass; rarity headline is unsupported.",
        "evidence": "Independently authored standard-library recomputation inside the same AI task; no producer imports, no external replication.",
        "interface": {
            "question": "Does the reported description arithmetic and candidate count support the claimed rarity, and which conclusions are bounded data versus known/compositional?",
            "branch": "code_analysis",
            "inputs": "Original preregistration, note, read-only census.py, s1.json, s2.json, s3_*.jsonl and summary.json; accessible primary sources for background.",
            "forbidden_inputs": "Importing or executing census.py; changing source data, scope or tickets; assuming finite 'unexplained' means nonperiodic.",
            "outputs": "This script and sibling JSON only.",
            "resource_budget": "Each calculation <10 minutes and <8 GB; recovered family has 168 gadgets over seven Boolean variables.",
            "stop_rule": "Arithmetic, embeddings, boundary checks, existing-classifier reconciliation and prose classification complete; S1 and SAT growth/mutants remain other audit lanes.",
            "nonclaims": "No unrestricted optimum gadget theorem, exact asymptotic counter theorem, global probability, intrinsic measure or external novelty certification.",
        },
        "arithmetic": weights,
        "template_check": {
            "original_stored_gadgets": len(original_gadgets),
            "recovered_by_named_S4_helper_S3_orbit": len(recovered),
            "is_exhaustive_synthesis": False,
            "formal_embeddings_distinct": len(set(templates.values())),
            "used_slot_supports": {rule: sorted(set(itertools.chain.from_iterable(embedded(recovered[0], rule))))
                                   for rule in ("rule 60", "rule 90", "rule 150")},
            "injectivity_argument": "Each fixed slot embedding is injective on seven distinct formal variables. Every parity gadget must use all four named variables; rule60/90/150 have different named-main slot supports, so their image sets cannot coincide. Labels of helpers are already part of the subset choice; no extra rule-selector or helper-factorial charge is required.",
            "description_identity": "Helper renamings may expand to isomorphic patterns, yet remain different labelled descriptions. A79 explicitly sums description weights, so quotienting by relabelling is a different weighting.",
            "count_classification": "504 is the exact count of this Cartesian family of labelled local templates, conditional on the separately audited exhaustive count 168. The frozen census growth code already supplies a valid collision-repair decoder for these gadget embeddings. Conditional on a demonstrated counting property for all three growths, 504 is a lower bound on counting descriptions and mass under this chosen weighting, never an exhaustive counter count. Without the all-depth counting bridge for rule90/150 it is a count of decoded candidate descriptions rather than an unconditional lower bound on proven counters.",
        },
        "boundary_checks": {rule: boundary_inventory(rule) for rule in RULES},
        "description_critique": [
            {"severity": "Block", "claim": "Astronomically rare / 10^-29 likely / among the rarest",
             "finding": "Summing a found subset supplies a LOWER bound on total counting mass once descriptions and counting are valid. A tiny lower bound supplies no upper bound; all remaining descriptions could count. No exhaustion or bound on the unexamined counting descriptions is given."},
            {"severity": "Narrowing", "claim": "The formula is the counter's code length",
             "finding": "It encodes h, m and an unordered m-subset of labelled local triples, conditional on a fixed growth decoder. The frozen preregistration and census.py ALREADY specify initial width3, growth+1, unrestricted initial mains, one global R, missing=R, terminal NAE closure and equality-copy repairs. Shared decoder conventions can legitimately have zero per-description charge in this chosen language. The required qualification is conditional ideal local-template length under that fixed decoder, not a missing-decoder Block or a shortest description over other languages."},
            {"severity": "Narrowing", "claim": "All 504 raw templates are valid strict NAE growth descriptions",
             "finding": "Without copies, only 12 rule60, 12 rule90 and 48 rule150 templates avoid repeated identities within every NAE at the ends. This does NOT invalidate the other compiled descriptions: census.py already supplies the fixed equality-copy convention. A copy adds eight NAE constraints and eight used distinctions, including the copy, so h helpers and m knots per position describe the bulk gadget inventory rather than the full boundary inventory. These additions need not add per-description bits when built into the shared decoder."},
            {"severity": "Narrowing", "claim": "104-106 bits are literal binary codeword lengths",
             "finding": "log2(binomial(...)) is generally fractional. These are exact ideal self-information values for uniform subset selection, not lengths of individual finite binary words. A simple fixed-width rank code uses 106 and 104 bits respectively. Exact uniform choices from fair coins can instead use variable-length rejection; the semantic object's probability is 1/M, but it aggregates multiple coin prefixes."},
            {"severity": "Not a block", "claim": "Rule150 needs a fifth parity argument/reference in the interior",
             "finding": "It does not: the four named parity variables are new i and all three old mains. R remains needed only as the globally shared value for missing old positions; rule60 and rule90 also use R in every interior update. The declared slot set includes all four distinct main slots used by rule150."},
            {"severity": "Narrowing", "claim": "Cheapest counting description",
             "finding": "The calculation compares two known parity constructions in this selected local-template language. Minimum knot number is not shortest code length across arbitrary descriptions or alternative counting constructions, and h=4 gadgets were not exhaustively counted. The 504 numerator includes h=3 only."},
            {"severity": "Narrowing", "claim": "Weight share / probability",
             "finding": "Name the sampling and rejection convention and denominator. Gamma headers plus uniform subsets define a particular subprobability mass when out-of-range m is rejected. Conditioning on accepted descriptions changes shares; neither version is a probability over realities selected by the mathematics."},
        ],
        "stored_finite_growth_classification": life,
        "conclusion_classification": [
            {"number": 1, "primary_class": "new bounded data", "secondary_classes": ["global bound supplied by separate parent audit"],
             "finding": "The original S1 m*(f) table for f<=6 and the labelled f=3 family are bounded synthesis data. This lane verifies recovered gadget relations, not optimality. The parent audit reports a new extension proving the unrestricted 'at least 10': remove helpers of degree<=1, then 2f+4<=3m<=27 gives f<=11 for m<=9, and synthesize f=7..11 as UNSAT. This requires integration of that independent parent evidence; it was absent from the original argument. General pp-definability is standard; the exact minima are not supplied by that reference."},
            {"number": 2, "primary_class": "definitional/composition", "secondary_classes": ["known additive algebra", "new bounded data", "unsupported count-too extrapolation"],
             "finding": "Replacing parity by an exact existential definition with disjoint fresh helpers, and faithful collision handling, preserves the named relation by composition. S2 checks wiring. Additive CA algebra is standard. Exact depth life strings are new bounded data for this boundary contract. The stored rule90 and rule150 classes are only 'unexplained' through 64; MOW does not by itself verify this expanding-seed/terminal-NAE satisfiability criterion or prove these growths count."},
            {"number": 3, "primary_class": "unsupported", "secondary_classes": ["definitional arithmetic"],
             "finding": "The two ideal local-template lengths and -96.64199 arithmetic are reproducible conditional on the fixed growth decoder, which already states the growth and collision conventions. They do not establish a shortest description across constructions, total counting probability, rarity upper bound or comparison with other capabilities."},
            {"number": 4, "primary_class": "new bounded data", "secondary_classes": ["definitional mutation inventory", "minimality implication"],
             "finding": "240=12 deletions +12*(31-12) replacements in the declared one-gadget neighbourhood. Minimality alone prevents any deletion from preserving parity; the three parity-preserving replacements and other finite life classes are substantive bounded data, being checked by the other lane. A 1.25% local mutation survival rate is not a global rarity estimate; settling is finite-classifier terminology here."},
            {"number": 5, "primary_class": "new bounded data", "secondary_classes": ["honest registered failure", "unsupported infinite extrapolation if read literally"],
             "finding": "P3 failure is stated explicitly and honestly: the stored sequence lives at 1..7,9,11 and is dead throughout 12..64, so the registered small-period test fails. Finite data alone does not prove death at all later depths; keep the heading local to the tested construction/horizon unless an independent mechanism is supplied."},
        ],
        "honesty_and_rhetoric": {
            "P3": "Honest negative outcome and failed-prediction label; avoid turning a finite observed tail into an all-depth theorem.",
            "rule90_rule150": "The words 'count too' outrun the actual 'unexplained within 64' classifier. A separate analytic bridge to the precise boundary/closure predicate is required, rather than citing general additive-CA algebra.",
            "fragility": "The finite predeclared result is meaningful in its one-gadget mutation neighbourhood; it does not establish global fine tuning or probability of arithmetic-capable patterns.",
        },
        "checks": assertions,
        "decoder_followup": {
            "finding": "Growth decoder conventions already exist in the frozen study; withdraw the initial missing-decoder Block. A79 alone does not define a row language.",
            "references": [
                {"path": "docs/ASSUMPTIONS.md", "lines": [2073, 2080],
                 "establishes": "A79's general sum-over-descriptions convention and its link to SHORT-DESC, not a row-growth decoder."},
                {"path": "research/SHORT-DESC-20261112-001/preregistration.md", "lines": [34, 46],
                 "establishes": "The directly linked authoritative definition is the separate macro/SELF description language; its weighting is not CHEAP's row-template formula."},
                {"path": "research/CHEAP-COUNT-20261112-001/preregistration.md", "lines": [31, 40],
                 "establishes": "Design explicitly frozen in census.py; initial width3, missing=R, terminal NAE closure and row-template formula stated."},
                {"path": "experiments/CHEAP-COUNT-20261112-001A/CHEAP-COUNT-20261112-001A-E001_cheapest_counter/census.py", "lines": [100, 105],
                 "establishes": "All widths are 3+r. Exactly one R is allocated before the generation and position loops; all mains are unconstrained until the stated transition and terminal constraints."},
                {"path": "experiments/CHEAP-COUNT-20261112-001A/CHEAP-COUNT-20261112-001A-E001_cheapest_counter/census.py", "lines": [123, 132],
                 "establishes": "Every explicit reference slot and every missing old position returns that one R identity, across all positions and generations."},
                {"path": "experiments/CHEAP-COUNT-20261112-001A/CHEAP-COUNT-20261112-001A-E001_cheapest_counter/census.py", "lines": [116, 121],
                 "establishes": "The inequality/equality gadget compiler used for copy ties is defined."},
                {"path": "experiments/CHEAP-COUNT-20261112-001A/CHEAP-COUNT-20261112-001A-E001_cheapest_counter/census.py", "lines": [145, 162],
                 "establishes": "Duplicate named occurrences receive fresh equal copies; helpers are mapped per-position; terminal consecutive mains receive NAE closure."},
            ],
            "remaining_scope": "A global probability still requires an explicit whole-language sampling/rejection convention and a counting-property criterion; these growth conventions are already legitimate fixed interpreter data.",
        },
        "primary_sources": SOURCES,
        "unresolved_questions": [
            "Integrate the parent's useful-helper bound and f=7..11 UNSAT evidence before promoting the unrestricted ten-knot lower bound; this lane does not recheck its SAT runs.",
            "What full row-language sampling/rejection/normalization convention is intended beyond the known gadget embeddings? The frozen study already fixes their growth decoder, global-reference identity and collision policy.",
            "What theorem maps the precise rule90/rule150 expanding growth with terminal NAE closure to an unbounded counting property?",
            "Is any upper bound on total counting weight available? Current subset arithmetic provides none.",
        ],
        "input_sha256": {},
        "runtime": {},
    }
    paths = [STUDY / "preregistration.md", STUDY / "cheap_count.md", DATA / "s1.json", DATA / "s2.json", DATA / "summary.json"]
    paths += sorted(DATA.glob("s3_*.jsonl"))
    paths += [ROOT / "experiments/CHEAP-COUNT-20261112-001A/CHEAP-COUNT-20261112-001A-E001_cheapest_counter/census.py"]
    result["input_sha256"] = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    result["runtime"] = {"seconds": time.perf_counter() - started,
                         "max_rss_kib_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                         "python": sys.executable,
                         "codex_thread_id": os.environ.get("CODEX_THREAD_ID"),
                         "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"output": str(OUT.relative_to(ROOT)), "bits_h3_m12": weights[0]["ideal_self_information_bits"],
                      "bits_h4_m10": weights[1]["ideal_self_information_bits"],
                      "log2_mass_504_h3_m12": weights[0]["known_template_log2_mass"],
                      "formal_templates": len(set(templates.values())), "raw_strict_valid": raw_valid,
                      "seconds": result["runtime"]["seconds"], "max_rss_kib": result["runtime"]["max_rss_kib_linux"]}, indent=2))


if __name__ == "__main__":
    main()
