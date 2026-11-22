"""Independent local-bank weighting, matched physical witnesses, and full-board projection checks."""
from collections import Counter
from fractions import Fraction
from functools import cache
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
import json
from math import prod
from pathlib import Path


HERE = Path(__file__).resolve().parent
OLD = HERE.parent / "WRITTEN-BIT-AND-JOIN-VETO-20261122-001" / "verify.py"
spec = spec_from_file_location("witnessed_groups_check", OLD)
board = module_from_spec(spec)
spec.loader.exec_module(board)
CONFIG = (("parity", "zero", (0, 0, 0)), ("nae", "lex", (1, 1, 0)), ("nae", "opposite", (1, 1, 0)))


@cache
def bank(law, extension, inputs, reference_inputs, width, free):
    possible = tuple(word for word in product((0, 1), repeat=width) if board.lawful(inputs + word, law))
    refs = tuple(word for word in product((0, 1), repeat=width)
                 if board.lawful(reference_inputs + word, law))
    if law == "parity":
        ref = (0,) * width
    elif extension == "opposite" and len(set(reference_inputs)) == 1:
        ref = (1 - reference_inputs[0],) * width
    else:
        ref = min(refs)
    assert ref in refs
    if free:
        return ref, possible
    costs = dict((word, sum(x != y for x, y in zip(word, ref))) for word in possible)
    return ref, tuple(word for word in possible if costs[word] == min(costs.values()))


def banks(law, extension, paid, fresh, ref, actual, free):
    return [bank(law, extension, tuple(actual[i] for i in p), tuple(ref[i] for i in p), len(f), free)
            for p, f in zip(paid, fresh, strict=True)]


def policy_allows_all(policy, cut):
    return policy == "A" or policy == "F" and cut == 1


def join_words(old, new):
    return old + sum(new, ())


def quiet_horizon(law, extension, source, policy):
    """Only the entirely quiet prefix can have its first deviation on the next cut."""
    stars, blocks, ref = ((0, 1, 2),), [{0}], source
    survival = Fraction(1)
    earliest = {}
    for cut in (1, 2, 3):
        _, _, paid, fresh, stars, blocks = board.roster(stars, blocks, ref, ref, law, True)
        local = banks(law, extension, paid, fresh, ref, ref, policy_allows_all(policy, cut))
        mass = Fraction(1, prod(len(opts) for _, opts in local))
        earliest[f"cut_{cut}"] = str(survival * (1 - mass))
        survival *= mass
        ref = join_words(ref, [r for r, _ in local])
    earliest["none"] = str(survival)
    assert sum(Fraction(x) for x in earliest.values()) == 1
    return earliest


def final_word_count(law, extension, policy, stars, blocks, ref, before, options, cache_by_roster):
    """Check all reachable rosters. Factor disjoint final banks only at a fixed full input."""
    total = 0
    groups = board.candidate_groups(blocks)
    offset = len(stars) - len(options)
    for second in product(*(possible for _, possible in options)):
        actual = join_words(before, second)
        hot = {v for v in range(offset, len(stars)) if any(actual[d] != ref[d] for d in stars[v])}
        refused = tuple(g for g in groups if hot.intersection(g))
        key = stars, refused
        if key not in cache_by_roster:
            _, _, paid, fresh, _, _ = board.roster(stars, blocks, ref, actual, law, True)
            cache_by_roster[key] = paid, fresh
        paid, fresh = cache_by_roster[key]
        choices = banks(law, extension, paid, fresh, ref, actual, policy_allows_all(policy, 3))
        total += prod(len(allowed) for _, allowed in choices)
    return total


def one_setting(law, extension, source, policy):
    source_stars = ((0, 1, 2),)
    board.check_board(source_stars, law)
    first = board.roster(source_stars, [{0}], source, source, law, True)
    _, _, paid1, fresh1, stars1, blocks1 = first
    options1 = banks(law, extension, paid1, fresh1, source, source, policy_allows_all(policy, 1))
    ref1 = join_words(source, [r for r, _ in options1])
    h = 1 + paid1.index((0,))
    h_bank = fresh1[h - 1]
    first_mass = Fraction(1, prod(len(options) for _, options in options1))
    mass, causes, count_bins = Counter(), Counter(), Counter()
    witness, solo = [], []
    terminal_count, terminal_plans = 0, {}
    for words1 in product(*(opts for _, opts in options1)):
        actual1 = join_words(source, words1)
        _, parents, paid2, fresh2, stars2, blocks2 = board.roster(stars1, blocks1, ref1, actual1, law, True)
        options2 = banks(law, extension, paid2, fresh2, ref1, actual1, policy_allows_all(policy, 2))
        ref2 = join_words(ref1, [r for r, _ in options2])
        terminal_count += final_word_count(law, extension, policy, stars2, blocks2, ref2, actual1,
                                           options2, terminal_plans)
        indices = [i for i, (parent, paid) in enumerate(zip(parents, paid2))
                   if parent == (h,) and len(paid) == 1 and paid[0] in h_bank]
        carriers = tuple(d for d in h_bank if actual1[d] != ref1[d])
        if len(indices) != 2:
            assert not carriers
            mass[f"missing_{len(indices)}_recipients"] += first_mass
            count_bins[f"missing_{len(indices)}_recipients"] += prod(len(o) for _, o in options2)
            continue
        others = prod(len(o) for i, (_, o) in enumerate(options2) if i not in indices)
        target = tuple(len(stars1) + i for i in indices)
        assert target in board.candidate_groups(blocks2)
        for two in product(*(options2[i][1] for i in indices)):
            companions = tuple(d for w,i in zip(two,indices) for d,v in zip(fresh2[i],w) if ref2[d] != v)
            mode = "veto_H" if carriers else "veto_later_only" if companions else "join"
            local_mass = first_mass / prod(len(options2[i][1]) for i in indices)
            mass[mode] += local_mass
            count_bins[mode] += others
            if mode == "veto_H":
                causes[f"{len(carriers)} H marks, {len(companions)} recipient marks"] += local_mass
        # For a transcribed whole paid history fix the other two simultaneous banks before
        # inspecting the target. Their words come from the permitted first-cut choices.
        if policy != "F":
            continue
        is_matched = all(words1[i] == min(w for w in options1[i][1] if w != options1[i][0])
                         for i in (1, 2))
        h_only = bool(carriers) and all(words1[i] == options1[i][0] for i in (1, 2))
        if not (is_matched or h_only):
            continue
        actual2 = join_words(actual1, [min(o) for _, o in options2])
        signature = []
        for guarded in (True, False):
            group3, par3, p3, f3, stars3, _ = board.roster(stars2, blocks2, ref2, actual2, law, guarded)
            assert target in group3
            fill3 = banks(law, extension, p3, f3, ref2, actual2, False)
            r3 = join_words(ref2, [r for r,_ in fill3])
            a3 = join_words(actual2, [min(opts) for _,opts in fill3])
            assert all(board.lawful(tuple(w[d] for d in row),law) for w in (r3,a3) for row in stars3)
            signature.append({"guard_enabled":guarded, "keeps_joint":target in par3, "all_births":len(par3),
                              "target_payments":[p for p,q in zip(p3,par3) if set(q)&set(target)]})
        exhibit = {"first_words":words1,"actual_at_founder":source,"H_new_marks":h_bank,
                        "second_all_payments":paid2,"target_parents":target,"holdings":[stars2[v] for v in target],
                        "target_reference":[[ref2[d] for d in stars2[v]] for v in target],
                        "target_actual":[[actual2[d] for d in stars2[v]] for v in target],
                        "all_predecision_deviations":[d for d in range(len(ref2)) if ref2[d] != actual2[d]],
                        "actual_decision":signature}
        (witness if is_matched else solo).append(exhibit)
    assert sum(mass.values()) == 1 and sum(causes.values()) == mass["veto_H"]
    if policy == "F":
        baseline = witness[0]
        assert baseline["first_words"][0] == options1[0][0]
        for exhibit in witness[1:]:
            assert exhibit["first_words"][1:] == baseline["first_words"][1:]
            assert exhibit["target_reference"] == baseline["target_reference"]
            assert exhibit["second_all_payments"] == baseline["second_all_payments"]
            difference = set(exhibit["all_predecision_deviations"]) ^ set(baseline["all_predecision_deviations"])
            exhibit["complete_matched_predecision_word_difference"] = sorted(difference)
            if law == "nae" and extension == "lex":
                assert len(difference) == 1 and difference <= set(h_bank)
    return {"first_bank_reference_and_allowed":options1, "first_cohort_count":first_mass.denominator,
            "probability_of_guard_outcome":{k:str(v) for k,v in mass.items()},
            "paid_mark_and_companions":{k:str(v) for k,v in causes.items()},
            "predecision_histories":dict(count_bins), "first_cut_with_deviation":quiet_horizon(law,extension,source,policy),
            "matched_witnesses":witness, "only_H_writes_at_first_cut":solo,
            "terminal_history_count":terminal_count,"terminal_rosters_checked":len(terminal_plans)}


def compare_record(independent, replay):
    score = replay["all_launches"]
    assert independent["terminal_history_count"] == score["terminal_histories"]
    assert independent["first_cohort_count"] == score["first_bank_assignments"]
    assert independent["first_cut_with_deviation"] == score["initial_mass_by_first_deviation"]
    mapping = {"join":"join", "veto_H":"veto_with_H_payment_deviation",
               "veto_later_only":"veto_without_H_payment_deviation"}
    for local_name, replay_name in (("probability_of_guard_outcome","initial_mass_by_outcome"),
                                    ("predecision_histories","predecision_count_by_outcome")):
        aggregate = Counter()
        for category, value in independent[local_name].items():
            aggregate[mapping.get(category, "missing")] += Fraction(value)
        assert sum(aggregate.values()) == (1 if local_name.startswith("probability") else score["predecision_histories"])
        assert aggregate == Counter({k:Fraction(v) for k,v in score[replay_name].items()})
    h_sole = Fraction(independent["paid_mark_and_companions"].get("1 H marks, 0 recipient marks", 0))
    measured = score["veto_diagnostics_initial_mass"]
    assert h_sole == sum(Fraction(v) for k, v in measured.items() if k.startswith("sole_H_mark_"))


if __name__ == "__main__":
    result={f"{law}-{extension}-{policy}":one_setting(law,extension,source,policy)
            for law,extension,source in CONFIG for policy in ("M","F","A")}
    stored_path, = (HERE.parents[1]/"artifacts"/(HERE.name+"A")).glob("*/results.json")
    from hashlib import sha256
    binary = stored_path.read_bytes()
    stored = json.loads(binary)["replay"]
    for prefix,setting in (("parity-zero", "parity_zero"), ("nae-lex","nae_lexicographic"),
                           ("nae-opposite","nae_opposite_on_homogeneous_reference")):
        for policy in ("M","F","A"):
            compare_record(result[f"{prefix}-{policy}"],stored[setting]["feedback_by_policy"][policy])
    data={"comparisons":result,"projected_full_board_supports":dict(board.PROJECTIONS),
          "canonical_local_relations":board.KNOT_CHECKS,
          "primary_replay_sha256":sha256(binary).hexdigest(),
          "projection_scope":"Whole static boards on all distinct reached feedback rosters, and matched ordinary controls.",
          "agreement":"Nine first supports, outcome counts and weights, earliest-deviation weights, sole H marks, final valued history counts."}
    print(json.dumps(data,indent=2,sort_keys=True))

