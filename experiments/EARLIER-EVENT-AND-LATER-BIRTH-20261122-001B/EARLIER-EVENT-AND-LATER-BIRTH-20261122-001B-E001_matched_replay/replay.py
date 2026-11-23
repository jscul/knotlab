"""Replay the frozen founder contrasts with the original complete-cut operator."""

from collections import Counter, defaultdict
from functools import cache
from gzip import compress
from hashlib import sha256
from itertools import combinations, permutations, product
import json
import os
from pathlib import Path
from runpy import run_path
import subprocess
import sys

from pysat.solvers import Minisat22


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name
FREEZE_HASH = "578e09391c1af520d681061b7b3e107f528e69fc64e1f26b568bbecebb191d72"
LAWS = ("parity", "nae")
ANCHORS = {"A": "R", "A'": "R'", "C": "S", "C'": "S'"}
PAIRS = tuple(product(("R", "R'"), ("S", "S'")))


def archived_script(ticket, name):
    path, = (ROOT / "experiments" / ticket).glob("*/" + name)
    return run_path(str(path))


NAE = archived_script("NAE-GROWTH-20261119-001B", "naelib.py")
END = archived_script("ORDINARY-DYNAMICS-20261120-001A", "end_operator.py")
PARITY = archived_script("ORDINARY-DYNAMICS-20261120-001A", "source_cert.py")


def founder(family, switches, tagged=True):
    e, f, *rest = switches
    a = ("A'", "A")[e]
    c = ("C'", "C")[f]
    live = list(ANCHORS)
    if family == "direct":
        live += ["K", "B"]
        sizes = (3, 4, 5, 6, 7, 3)
        pairs = ((a, "B"), (c, "B"), ("K", "B"))
        opening = {"B": 3}
        donor_slots = {"B": ("A", "C", "K")}
    else:
        live += ["P", "Q", "U"]
        sizes = (3, 4, 5, 6, 3, 4, 7)
        w, = rest
        donors = ("P", "Q")
        j = "A" if e == w else "A'"
        pairs = (*zip(ANCHORS, (donors[e], donors[1-e], donors[f], donors[1-f])),
                 (j, "U"), ("U", donors[w]))
        opening = {"P": 2, "Q": 2}
        donor_slots = {role: ("A", "C") for role in opening}

    witnesses = [f"pair-{i}" for i in range(len(pairs))]
    markers = [f"marker-{role}" for role in live]
    spent = witnesses + markers
    stars = {role: [] for role in live + spent}
    names, word = [], {}

    def meeting(label, holders, count, ones=0):
        marks = []
        for slot in range(count):
            mark = len(names)
            names.append(f"{label}/{slot}")
            word[mark] = int(slot < ones)
            for role in holders:
                stars[role].append(mark)
            marks.append(mark)
        return tuple(marks)

    for w, endpoints in zip(witnesses, pairs, strict=True):
        for slot, role in enumerate(endpoints):
            meeting(f"{w}/endpoint-{slot}", (w, role), 2)
    for role, marker, width in zip(live, markers, sizes, strict=True):
        meeting(marker, (role, marker), width if tagged else 3, 2)
    for a, b in zip(spent, spent[1:] + spent[:1], strict=True):
        meeting(f"cycle-{a}-{b}", (a, b), 2, 2)
    openings = {role: meeting(f"open-{role}", (role,), opening.get(role, 1)) for role in live}
    return {
        "stars": tuple(tuple(row) for row in stars.values()),
        "roles": {name: i for i, name in enumerate(stars)},
        "marks": names,
        "word": word,
        "openings": openings,
        "marker_signatures": {role: (opening.get(role, 1), width)
                              for role, width in zip(live, sizes, strict=True)},
        "donor_slots": donor_slots,
    }


def owners(stars):
    answer = defaultdict(list)
    for k, row in enumerate(stars):
        assert len(set(row)) == len(row)
        for mark in row:
            answer[mark].append(k)
    assert all(1 <= len(holders) <= 2 for holders in answer.values())
    return {mark: tuple(holders) for mark, holders in answer.items()}


def neighbors(stars, incidence):
    adjacent = [set() for _ in stars]
    for row in incidence.values():
        if len(row) == 2:
            a, b = row
            adjacent[a].add(b)
            adjacent[b].add(a)
    return adjacent


def legal(law, word):
    count = sum(word)
    return count % 2 == 0 if law == "parity" else 0 < count < len(word)


def whole_word(law, word, stars):
    return set(word) == set(owners(stars)) and all(
        legal(law, tuple(word[mark] for mark in row)) for row in stars
    )


def full_from_free_marks(stars, incidence):
    """After prescribing one holding, each component can finish at a free mark."""
    adjacent = neighbors(stars, incidence)
    loose = {row[0] for row in incidence.values() if len(row) == 1}
    answer = []
    for fixed in range(len(stars)):
        seen = {fixed} | loose
        frontier = list(loose - {fixed})
        while frontier:
            unseen = adjacent[frontier.pop()] - seen
            frontier.extend(unseen)
            seen.update(unseen)
        answer.append(len(seen) == len(stars))
    return answer


@cache
def projection(law, stars):
    """Certify each full physical holding's allowed relation, with exact fallbacks."""
    incidence = owners(stars)
    if min(map(len, stars)) < 3:
        return {"gate": False, "reason": "a physical holding has fewer than three distinctions"}
    span = full_from_free_marks(stars, incidence)
    result = {"gate": True, "free_mark_certified": sum(span), "fallback": []}
    if all(span):
        return result
    if law == "parity":
        equations = PARITY["row_masks"](stars)
        for k, ok in enumerate(span):
            if not ok:
                supported = PARITY["supported_equations"](equations, stars[k])
                exact = supported == [(1 << len(stars[k])) - 1]
                result["fallback"].append({"holder": k, "parity_projection": supported, "exact": exact})
                result["gate"] &= exact
        return result

    clauses = [clause for row in stars for clause in ([d+1 for d in row], [-d-1 for d in row])]
    with Minisat22(bootstrap_with=clauses) as solver:
        for k, ok in enumerate(span):
            if ok:
                continue
            row = stars[k]
            missing = []
            for bits in product((0, 1), repeat=len(row)):
                if legal(law, bits):
                    pins = [d+1 if bit else -d-1 for bit, d in zip(bits, row, strict=True)]
                    if not solver.solve(assumptions=pins):
                        missing.append("".join(map(str, bits)))
            result["fallback"].append({"holder": k, "missing_legal_words": missing, "exact": not missing})
            result["gate"] &= not missing
    return result


def canonical_check(law, width):
    variables = [f"d{i}" for i in range(width)]
    exclusions = [row for row in product((0, 1), repeat=width) if not legal(law, row)]
    cnf = ";".join(" ".join(("~" if b else "") + x for x, b in zip(variables, row, strict=True))
                   for row in exclusions)
    args = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", cnf,
            "--loops", *variables[:-1], "--contact", variables[-1], "--json"]
    check = subprocess.run(args, cwd=ROOT, env={**os.environ, "PYTHONPATH": str(ROOT / "tools")},
                           capture_output=True, check=True, text=True)
    report = json.loads(check.stdout)
    return {"law": law, "arity": width, "allowed": len(report["allowed"]),
            **{key: report[key] for key in ("binding", "loss_on_erasure", "coexistence", "is_knot")}}


def plan(stars, law):
    """Run the archived physical mutator and compare its plan to the end operator."""
    physical = NAE["S"].from_junctions(stars)
    style = NAE["S"].gf2 if law == "parity" else NAE["nae_rule"]
    full = END["from_stars"](stars)
    turn = END["step"](full, law)
    expected_groups = END["proposals"](full)
    live = list(full.opens)
    assert tuple(tuple(sorted(g)) for g in physical.groups_among(live)) == expected_groups
    incidence = owners(stars)
    moved = physical.step(style(NAE["F"].fewest), None)
    if moved is None:
        assert turn.status == "stall"
        return {"status": "stall", "proposed_groups": expected_groups, "shortages": turn.shortages, "births": []}
    if not moved["new"]:
        assert turn.status == "closed"
        return {"status": "closed", "proposed_groups": expected_groups, "births": []}
    assert turn.status == "extend" and moved["new"] == len(turn.parents)
    births = []
    for k in range(len(stars), len(physical.bits_of)):
        paid = tuple(physical.bits_of[k][:physical.parents[k]])
        row = dict(knot=k, parents=tuple(incidence[d][0] for d in paid), paid=paid,
                   fresh=tuple(physical.bits_of[k][physical.parents[k]:]), demand=physical.demand_at_birth[k])
        births.append(row)
    assert tuple(row["parents"] for row in births) == turn.parents
    assert tuple(len(row["fresh"]) for row in births) == turn.fresh
    assert tuple(row["demand"] for row in births) == turn.demand
    return {"status": "extend", "proposed_groups": expected_groups, "implied": turn.implied, "births": births}


def bind_donors(turn, source, permutations_by_donor):
    """Rebind only outgoing marks of the named donor, by fixed family slots."""
    assignments = {}
    labels = {k: role for role, k in source["roles"].items()}
    for role, binding in permutations_by_donor.items():
        actor = source["roles"][role]
        slots = dict(zip(source["donor_slots"][role], binding, strict=True))
        for row in turn["births"]:
            if actor in row["parents"]:
                family, = {labels[k][0] for k in row["parents"] if labels[k][0] in slots}
                assignments[row["paid"][row["parents"].index(actor)]] = source["openings"][role][slots[family]]
    assert set(assignments) == set(assignments.values())
    for row in turn["births"]:
        row["paid"] = tuple(assignments.get(d, d) for d in row["paid"])


def fill(law, word, stars, turn, alternate=False):
    """Materialize a lawful receipt and retain every pre-existing value."""
    if turn["status"] != "extend":
        return word, stars
    incidence = owners(stars)
    grown, after = list(stars), dict(word)
    payments = Counter()
    for row in turn["births"]:
        incoming = row["paid"]
        bank = row["fresh"]
        assert row["knot"] == len(grown)
        assert all(incidence[d] == (k,) for d, k in zip(incoming, row["parents"], strict=True))
        assert not set(bank) & set(after)
        paid = tuple(word[d] for d in incoming)
        bit_order = (1, 0) if alternate else (0, 1)
        # Only the recorded certificate word uses this representative.
        fresh = next((f for f in product(bit_order, repeat=len(bank)) if legal(law, paid + f)), None)
        if fresh is None:
            raise ValueError(f"No legal completion at physical holder {row['knot']}")
        grown.append(incoming + bank)
        after.update(zip(bank, fresh, strict=True))
        payments.update(incoming)
    assert payments == Counter({d: 1 for d, holders in incidence.items() if len(holders) == 1})
    after_owners = owners(grown)
    for row in turn["births"]:
        assert all(after_owners[d] == (k, row["knot"]) for d, k in zip(row["paid"], row["parents"], strict=True))
        assert all(after_owners[d] == (row["knot"],) for d in row["fresh"])
    assert all(after[mark] == bit for mark, bit in word.items())
    assert whole_word(law, after, grown)
    return after, tuple(grown)


def enroll(turn, source):
    births = turn["births"]
    return {label: next((row["knot"] for row in births if source["openings"][role][0] in row["paid"]), None)
            for role, label in ANCHORS.items()}


def recover(stars, source):
    incidence = owners(stars)
    doubles = {pair for pair, n in Counter(row for row in incidence.values() if len(row) == 2).items() if n >= 2}
    founders = {k for row in doubles for k in row}
    internal = {d: tuple(k for k in row if k in founders) for d, row in incidence.items()}
    signatures = defaultdict(list)
    for k in sorted(founders):
        if old_private := tuple(d for d in stars[k] if internal[d] == (k,)):
            multiplicities = Counter(row for row in internal.values() if len(row) == 2 and k in row)
            signatures[(len(old_private), max(multiplicities.values(), default=0))].append(k)
    recovered = {}
    paid = {}
    for role, signature in source["marker_signatures"].items():
        candidates = signatures[signature]
        if len(candidates) == 1:
            k, = candidates
            recovered[role] = k
            if role in ANCHORS:
                mark, = [d for d in stars[k] if internal[d] == (k,)]
                paid[role] = [mark, [other for other in incidence[mark] if other not in founders]]
    return {"founder_ids": sorted(founders),
            "founder_set_recovered": founders == set(source["roles"].values()),
            "role_candidates": [[list(signature), candidates] for signature, candidates in sorted(signatures.items()) if candidates],
            "roles_recovered_by_tagged_signatures": recovered, "sole_anchor_payments": paid}


def compatible_local_words(law, word, birth):
    paid = tuple(word[d] for d in birth["paid"])
    return ["".join(map(str, f)) for f in product((0, 1), repeat=len(birth["fresh"])) if legal(law, paid + f)]


def witnesses(stars, pair):
    incidence = owners(stars)
    adjacent = neighbors(stars, incidence)
    older = adjacent[pair[0]] & adjacent[pair[1]]
    return [{"holder": witness,
             "paid_sharings": [[d for d in stars[receiver] if set(incidence[d]) == {witness, receiver}]
                               for receiver in pair]}
            for witness in sorted(older)]


def current_candidates(stars):
    """List maximal pairwise candidates, including groups held by one witness."""
    end = END["from_stars"](stars)
    pairs = END["neighbors"](end)
    physical = neighbors(stars, owners(stars))
    groups = []
    for width in range(3, len(pairs) + 1):
        for group in combinations(pairs, width):
            if all(b in pairs[a] for a, b in combinations(group, 2)):
                groups.append(group)
    return [{"candidate_holders": group, "holders_witnessing_every_candidate":
             sorted(set.intersection(*(physical[k] for k in group)))}
            for group in groups if not any(set(group) < set(larger) for larger in groups)]


def observed(law, source, levels, cuts):
    first, second, third = cuts
    enrollment = enroll(first, source)
    founders = {k: key for key, k in source["roles"].items()}
    report = {"enrollment": enrollment, "first": {}, "pairs": {}, "alternatives": {},
              "birth_counts": [len(cut["births"]) for cut in cuts],
              "statuses": [cut["status"] for cut in cuts]}
    if any(value is None for value in enrollment.values()):
        return report
    natural = {v: k for k, v in enrollment.items()}
    if "K" in source["roles"]:
        k = source["openings"]["K"][0]
        natural[next(row["knot"] for row in first["births"] if k in row["paid"])] = "K's child"
    births = {row["knot"]: row for row in first["births"]}
    stars, word = levels[1]
    report["maximal_candidates_with_three_or_more_parents"] = current_candidates(stars)
    report["next_opportunities_by_fresh_mark"] = {}
    for label, k in enrollment.items():
        row = births[k]
        report["first"][label] = {"older_roles": [founders[parent] for parent in row["parents"]],
            "older_payments": dict(zip((founders[p] for p in row["parents"]), row["paid"], strict=True)),
            "older_payment_values": [word[d] for d in row["paid"]],
            "shared": len(row["paid"]), "loose": len(row["fresh"]), "total": len(stars[k]),
            "fresh_words_at_fixed_founder": compatible_local_words(law, word, row),
            "witness_word_by_holding_count": [sorted(word[d] for d in row["paid"]), sorted(word[d] for d in row["fresh"])]}
        slots = [child for child in second["births"] if k in child["parents"]]
        report["next_opportunities_by_fresh_mark"][label] = {
            d: {"recorded_payee": next((child["knot"] for child in slots if d in child["paid"]), None),
                "available_payees": [child["knot"] for child in slots]} for d in row["fresh"]
        }
    for labels in PAIRS:
        pair = tuple(enrollment[label] for label in labels)
        partner_set = set(pair)
        exact = [row for row in second["births"] if set(row["parents"]) == partner_set]
        report["pairs"]["+".join(labels)] = {
            "older_witnesses": witnesses(stars, pair),
            "all_proposed_supersets": [row for row in second["proposed_groups"] if partner_set < set(row)],
            "is_proposed_pair": any(partner_set == set(row) for row in second["proposed_groups"]),
            "actual": exact}
    for label, k in enrollment.items():
        report["alternatives"][label] = [
            {"parents": [natural[p] for p in row["parents"]], "birth": row}
            for row in second["births"] if k in row["parents"]
        ]
    return report


def run(law, source, binding, alternate=False, rename_from=None, rebind_receiver=False):
    stars, word = source["stars"], source["word"]
    holder_map, mark_map = {}, {}
    if rename_from is not None:
        holder_map = {i: len(stars) - 1 - i for i in range(len(stars))}
        mark_map = {d: 5 * (len(word) - d) + 13 for d in word}
        stars = tuple(tuple(mark_map[d] for d in row) for row in reversed(stars))
        word = {mark_map[d]: value for d, value in word.items()}

    assert whole_word(law, word, stars)
    cuts, levels = [], [(stars, word)]
    for step in range(3):
        turn = plan(stars, law)
        if rename_from is not None:
            transport(steps=rename_from["cuts"][step], turn=turn, holders=holder_map, marks=mark_map)
        elif step == 0 and turn["status"] == "extend":
            bind_donors(turn, source, binding)
        elif step == 1 and rebind_receiver and turn["status"] == "extend":
            receiver = enroll(cuts[0], source)["R"]
            for born in cuts[0]["births"]:
                if born["knot"] == receiver:
                    swap = dict(zip(born["fresh"], reversed(born["fresh"]), strict=True))
                    for row in turn["births"]:
                        row["paid"] = tuple(swap.get(d, d) for d in row["paid"])
        word, stars = fill(law, word, stars, turn, alternate)
        cuts.append(turn)
        levels.append((stars, word))
    gates = [projection(law, current) for current, _ in levels]
    result = {"cuts": cuts, "levels": [{"holdings": current, "word": values, "projection": gate}
                                      for (current, values), gate in zip(levels, gates, strict=True)]}
    if rename_from is not None:
        for original, renamed in zip(rename_from["levels"], result["levels"], strict=True):
            assert {holder_map[p]: {mark_map[d] for d in row} for p, row in enumerate(original["holdings"])} == {
                p: set(row) for p, row in enumerate(renamed["holdings"])}
            assert {mark_map[d]: value for d, value in original["word"].items()} == renamed["word"]
        result["holder_renaming"] = holder_map
        result["distinction_renaming"] = mark_map
    else:
        result["observation"] = observed(law, source, levels, cuts)
        result["recovered"] = [recover(current, source) for current, _ in levels]
    return result


def transport(steps, turn, holders, marks):
    """Transport each prior receipt and re-run its funding with audit names reversed."""
    assert steps["status"] == turn["status"]
    assert {tuple(sorted(holders[p] for p in row)) for row in steps["proposed_groups"]} == {
        tuple(row) for row in turn["proposed_groups"]}
    assert {holders[p]: count for p, count in steps.get("shortages", ())} == dict(turn.get("shortages", ()))
    bins = defaultdict(list)
    for row in turn["births"]:
        bins[row["parents"]].append(row)
    for old in reversed(steps["births"]):
        parents = tuple(sorted(holders[p] for p in old["parents"]))
        row = bins[parents].pop()
        assert len(row["fresh"]) == len(old["fresh"]) and row["demand"] == old["demand"]
        payment_map = {holders[p]: marks[d] for p, d in zip(old["parents"], old["paid"], strict=True)}
        row["paid"] = tuple(payment_map[p] for p in row["parents"])
        holders[old["knot"]] = row["knot"]
        marks.update(zip(old["fresh"], row["fresh"], strict=True))
    assert not any(bins.values())


def bindings(source):
    donors = tuple(source["donor_slots"])
    permutations_per_donor = [tuple(permutations(range(len(source["donor_slots"][d])))) for d in donors]
    return [dict(zip(donors, order, strict=True)) for order in product(*permutations_per_donor)]


def shape(result):
    return [(cut["status"], cut["proposed_groups"],
             [(row["parents"], len(row["fresh"]), row["demand"]) for row in cut["births"]])
            for cut in result["cuts"]]


def ledger(raw, checks):
    result = {}
    for law in LAWS:
        law_set = result.setdefault(law, {})
        for family in ("direct", "balanced"):
            sample = [case for case in raw if case["law"] == law and case["family"] == family]
            law_set[family] = [summarize_one(case) for case in sample]
    projections = [level["projection"] for case in raw
                   for trial in [*case["runs"], case["coherent_relabelling"], case["neutral_markers"],
                                 case["alternate_word"], case["next_payment_sham"]] for level in trial["levels"]]
    return {"knotlab_canonical_relations": checks, "literal_projections_all_saved_runs": len(projections),
            "literal_projections_failing": sum(not x["gate"] for x in projections),
            "literal_projection_holder_fallbacks": sum(len(x.get("fallback", ())) for x in projections),
            "law_and_preparation": result}


def summarize_one(case):
    base, *shams = case["runs"]
    observe = base["observation"]
    bind_changes = [{"binding": binding,
                     "changed_first_payments": [
                        [a["knot"], a["paid"], b["paid"]] for a, b in zip(base["cuts"][0]["births"],
                           sham["cuts"][0]["births"], strict=True) if a["paid"] != b["paid"]],
                     "same_enrollment": sham["observation"]["enrollment"] == observe["enrollment"],
                     "same_parent_rosters_and_grants": shape(sham) == shape(base)}
                    for binding, sham in zip(case["bindings"][1:], shams, strict=True)]
    next_sham = case["next_payment_sham"]
    sham_labels = ("R", "S")
    return {"switches": case["switches"], "source_roles": case["source"]["roles"],
            "observation": observe, "binding_shams": bind_changes,
            "next_payment_sham": {"same_parent_rosters_and_grants": shape(next_sham) == shape(base),
                "changed_recorded_receiver_payees": {
                    name: next_sham["observation"]["next_opportunities_by_fresh_mark"][name]
                    for name in sham_labels if name in observe.get("next_opportunities_by_fresh_mark", {})
                    and next_sham["observation"]["next_opportunities_by_fresh_mark"][name]
                    != observe["next_opportunities_by_fresh_mark"][name]}},
            "unpointed_birth_types": [sorted([[p, n, count] for (p, n), count in Counter(
                (len(row["parents"]), len(row["fresh"])) for row in cut["births"]).items()])
                                      for cut in base["cuts"]],
            "all_completion_controls_same_structural_roster": shape(case["alternate_word"]) == shape(base),
            "actual_alternate_value_differences": sum(bit != case["alternate_word"]["levels"][-1]["word"][d]
                                                    for d, bit in base["levels"][-1]["word"].items()),
            "coherent_renaming": "physical transition and transported word agree",
            "founder_recovery": base["recovered"],
            "neutral_markers_same_parent_rosters_and_grants": shape(case["neutral_markers"]) == shape(base),
            "neutral_marker_recovery": case["neutral_markers"]["recovered"]}


def compare_preparations():
    raw, widths = [], defaultdict(set)
    for law in LAWS:
        for family, n in (("direct", 2), ("balanced", 3)):
            for switches in product((0, 1), repeat=n):
                source = founder(family, switches)
                shams = bindings(source)
                runs = [run(law, source, binding) for binding in shams]
                baseline = runs[0]
                relabel = run(law, source, shams[0], rename_from=baseline)
                neutral = run(law, founder(family, switches, tagged=False), shams[0])
                control = run(law, source, shams[0], alternate=True)
                next_sham = run(law, source, shams[0], rebind_receiver=True)
                raw.append({"law": law, "family": family, "switches": switches, "source": source,
                            "bindings": shams, "runs": runs, "coherent_relabelling": relabel,
                            "neutral_markers": neutral, "alternate_word": control, "next_payment_sham": next_sham})
                for receipt in [*runs, relabel, neutral, control, next_sham]:
                    for level in receipt["levels"]:
                        widths[law].update(map(len, level["holdings"]))
                print(law, family, switches, baseline["observation"]["statuses"],
                      baseline["observation"]["birth_counts"], flush=True)
    return raw, widths


def main():
    contract = json.loads((HERE / "contract.json").read_text())
    digest = sha256((ROOT / contract["preregistration"]).read_bytes()).hexdigest()
    assert digest == contract["preregistration_sha256"] == FREEZE_HASH
    raw, widths = compare_preparations()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    trace = compress((json.dumps(raw, separators=(",", ":")) + "\n").encode(), mtime=0)
    (OUTPUT / "physical_replay.json.gz").write_bytes(trace)
    checks = []
    for law, arities in widths.items():
        for width in sorted(arities):
            if width >= 3:
                checks.append(canonical_check(law, width))
                print(f"K1–K3 {law} arity {width}: {checks[-1]['is_knot']}", flush=True)
    report = ledger(raw, checks)
    report["freeze_sha256"] = digest
    report["physical_replay_sha256"] = sha256(trace).hexdigest()
    (OUTPUT / "results.json").write_text(json.dumps(report, indent=2) + "\n")
    assert all(item["is_knot"] for item in checks)


if __name__ == "__main__":
    main()
