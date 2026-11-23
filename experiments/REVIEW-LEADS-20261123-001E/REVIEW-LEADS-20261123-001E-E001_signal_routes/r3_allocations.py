"""R3, allocations.  For every knot that must choose which named loose distinction goes to which child,
enumerate every allocation at the first two funded steps of a structure and compare

  (i)   the later births (parents and fresh counts, up to renaming of distinctions),
  (ii)  the number of allowed words of the grown structure,
  (iii) the joint distribution of all OLD distinctions under uniform present words and under the
        old-word weighting,

under parity and under not-all-equal.

Run from the repository root:
  timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file> --structure seven --law nae
Structures: seven (seven-knot source, to six rounds), clock (five-founder clock, to three returns),
stall (smallest two-sided stall with both optional additions, i.e. the funded setting 11), minimal
(search for the smallest lawful start with an allocation effect).
"""

import argparse
from fractions import Fraction
import json
from pathlib import Path
import random
import time

import numpy as np

import allocations as A
import counting
import engine as E
import starts as S

ARTIFACTS = E.ROOT / "artifacts/REVIEW-LEADS-20261123-001E/REVIEW-LEADS-20261123-001E-E001_signal_routes"
CAP = 26                       # old distinctions allowed for exhaustive enumeration (reading of "about 24")
SEED = 2026112305


def frac(num, den):
    f = Fraction(num, den)
    return f"{f.numerator}/{f.denominator}"


def apply_pi(frame, pi):
    return tuple(tuple(sorted(pi.get(d, d) for d in row)) for row in frame)


def later_signature(frame, law, rounds):
    """Parents, fresh counts and demands of the next rounds under the canonical allocation."""
    out = []
    for _ in range(rounds):
        plan = E.plan_round(frame, law)
        if plan.status != "extend":
            out.append(plan.status)
            break
        out.append((plan.parents, plan.fresh_counts, plan.demand))
        frame, _ = E.apply_plan(frame, plan)
    return out


def full_joint_tv(frame, plan, law, sigma0, sigma, words, names):
    """TV on the full joint of ALL old distinctions (explicit words), both weightings, exact."""
    w0 = A.weights_on_words(plan, sigma0, law, words, names)
    w1 = A.weights_on_words(plan, sigma, law, words, names)
    uni = A.tv_from_weights(w0, w1)
    old = A.tv_from_weights((w0 >= 1).astype(np.int64), (w1 >= 1).astype(np.int64))
    return uni, old


def analyse_step(label, frame, law, later_rounds, rng, verify_sample):
    t0 = time.time()
    plan = E.plan_round(frame, law)
    record = {"label": label, "status": plan.status}
    if plan.status != "extend":
        return record, None
    names, loose = A.structure_columns(frame)
    n_old = len(names)
    record.update({
        "old_knots": len(frame), "old_distinctions": n_old, "old_loose": len(loose),
        "births": len(plan.parents), "fresh_counts": list(plan.fresh_counts),
        "implied": plan.implied,
        "plan_matches_reference_operator": E.agrees_with_reference(frame, law, plan),
        "raw_allocations": A.raw_total(plan), "allocation_classes": A.class_count(plan),
        "knots": {}})
    marginal = A.loose_marginal_counts(frame, law)
    record["old_allowed_words"] = int(marginal.sum())

    classes = list(A.all_classes(plan))
    sigma0 = classes[0]
    assert sigma0 == E.canonical_allocation(plan)
    grown0, births0 = E.apply_plan(frame, plan, sigma0)
    base_births = E.birth_signature(births0)
    base_later = later_signature(grown0, law, later_rounds)
    record["later_rounds_compared"] = len(base_later)

    ext0 = A.weights_on_loose(plan, sigma0, law, loose)
    W0 = marginal * ext0
    V0 = marginal * (ext0 >= 1)
    assert int(((marginal > 0) & (ext0 < 1)).sum()) == 0      # every old allowed word extends
    Z0 = int(W0.sum())
    record["grown_allowed_words_canonical"] = Z0
    record["grown_allowed_words_independent_count"] = counting.count_words(grown0, law)
    assert record["grown_allowed_words_independent_count"] == Z0

    own = E.births_of_knot(plan)
    qualifying = [k for k, ds in plan.loose.items() if len(ds) >= 2]
    for k in qualifying:
        groups = sum(1 for i in own[k] if len(plan.parents[i]) > 1)
        record["knots"][str(k)] = {
            "loose": len(plan.loose[k]), "group_births": groups, "unary_births": len(own[k]) - groups,
            "raw_orders": A.raw_count(plan, k), "classes": len(A.knot_classes(plan, k)),
            "uniform_max_tv": [0, 1], "old_word_max_tv": [0, 1],
            "uniform_all_zero": True, "old_word_all_zero": True, "only_this_knot_varies": 0}

    changed_births = changed_later = nonisomorphic = bad_count = 0
    worst = {"uniform": (Fraction(0), None), "old_word": (Fraction(0), None)}
    z_values = set()
    tv_uniform_nonzero = tv_old_nonzero = 0
    best_single = {}
    verify_idx = set(rng.sample(range(len(classes)), min(verify_sample, len(classes))))
    verified = 0
    per_class_uniform = {}
    full_words = None
    full_names = None
    if n_old <= CAP and (len(classes) <= 64 or verify_sample):
        full_words, full_names = A.full_allowed_words(frame, law)
    for idx, sigma in enumerate(classes):
        grown, births = E.apply_plan(frame, plan, sigma)
        changed_births += E.birth_signature(births) != base_births
        pi = A.relabelling(plan, sigma0, sigma)
        nonisomorphic += apply_pi(grown0, pi) != tuple(tuple(sorted(r)) for r in grown)
        if E.birth_signature(births) == base_births:
            changed_later += later_signature(grown, law, later_rounds) != base_later
        ext = A.weights_on_loose(plan, sigma, law, loose)
        W, V = marginal * ext, marginal * (ext >= 1)
        z_values.add(int(W.sum()))
        if idx < 64 or idx in verify_idx or idx % 97 == 0:
            bad_count += counting.count_words(grown, law) != int(W.sum())
        un, un_den = A.tv_from_weights(W0, W)
        ov, ov_den = A.tv_from_weights(V0, V)
        tvu, tvo = Fraction(un, un_den), Fraction(ov, ov_den)
        per_class_uniform[idx] = tvu
        tv_uniform_nonzero += tvu != 0
        tv_old_nonzero += tvo != 0
        for key, tv in (("uniform", tvu), ("old_word", tvo)):
            if tv > worst[key][0]:
                worst[key] = (tv, idx)
        diff = [k for k in sigma0 if sigma[k] != sigma0[k]]
        if len(diff) == 1 and str(diff[0]) in record["knots"]:
            info = record["knots"][str(diff[0])]
            info["only_this_knot_varies"] += 1
            for key, tv in (("uniform_max_tv", tvu), ("old_word_max_tv", tvo)):
                if Fraction(*info[key]) < tv:
                    info[key] = [tv.numerator, tv.denominator]
            info["uniform_all_zero"] &= tvu == 0
            info["old_word_all_zero"] &= tvo == 0
            if tvu > best_single.get(diff[0], (Fraction(0), None))[0]:
                best_single[diff[0]] = (tvu, sigma)
        if full_words is not None and (len(classes) <= 64 or idx in verify_idx):
            (fu, fu_den), (fo, fo_den) = full_joint_tv(frame, plan, law, sigma0, sigma, full_words, full_names)
            # full-joint weights are over words, so normalise by their own totals
            assert Fraction(fu, fu_den) == tvu and Fraction(fo, fo_den) == tvo, (idx, fu, fu_den, tvu)
            verified += 1
    for k, (tvu, sigma_best) in best_single.items():
        record["knots"][str(k)]["supplementary_marginal_change_at_other_knots"] = elsewhere_report(
            frame, plan, loose, marginal, law, sigma0, sigma_best, k)
    for info in record["knots"].values():
        info["uniform_max_tv"] = frac(*info["uniform_max_tv"])
        info["old_word_max_tv"] = frac(*info["old_word_max_tv"])
        info["interchangeable_uniform_present"] = info.pop("uniform_all_zero")
        info["interchangeable_old_word"] = info.pop("old_word_all_zero")
    record.update({
        "classes_with_changed_round_births": int(changed_births),
        "classes_with_changed_later_births": int(changed_later),
        "classes_not_isomorphic_to_canonical_by_relabelling": int(nonisomorphic),
        "distinct_grown_allowed_word_counts": sorted(z_values),
        "independent_count_mismatches": int(bad_count),
        "classes_with_uniform_present_tv_nonzero": int(tv_uniform_nonzero),
        "classes_with_old_word_tv_nonzero": int(tv_old_nonzero),
        "max_tv_uniform_present_vs_canonical": frac(worst["uniform"][0].numerator, worst["uniform"][0].denominator),
        "max_tv_old_word_vs_canonical": frac(worst["old_word"][0].numerator, worst["old_word"][0].denominator),
        "max_tv_uniform_present_decimal": float(worst["uniform"][0]),
        "max_tv_old_word_decimal": float(worst["old_word"][0]),
        "argmax_uniform_class": worst["uniform"][1],
        "full_joint_verifications": verified,
        "seconds": round(time.time() - t0, 1)})

    # all-pairs identity (max over all pairs equals max against the canonical allocation) on a sample
    if len(classes) > 1:
        pairs = [(i, j) for i in range(len(classes)) for j in range(i + 1, len(classes))] \
            if len(classes) <= 64 else [tuple(sorted(rng.sample(range(len(classes)), 2))) for _ in range(300)]
        top = Fraction(0)
        for i, j in pairs:
            wi = marginal * A.weights_on_loose(plan, classes[i], law, loose)
            wj = marginal * A.weights_on_loose(plan, classes[j], law, loose)
            num, den = A.tv_from_weights(wi, wj)
            top = max(top, Fraction(num, den))
        record["pairs_compared"] = len(pairs)
        record["max_tv_uniform_present_over_compared_pairs"] = frac(top.numerator, top.denominator)
        record["pair_max_not_above_canonical_max"] = bool(top <= worst["uniform"][0])
        if len(classes) <= 64:
            record["pair_max_equals_canonical_max"] = bool(top == worst["uniform"][0])
    return record, grown0


def bfs_distances(frame, source):
    nbrs = E.neighbours_of(frame)
    dist, todo = {source: 0}, [source]
    for v in todo:
        for w in nbrs[v]:
            if w not in dist:
                dist[w] = dist[v] + 1
                todo.append(w)
    return dist


def marginal_vector(weights, positions, size_bits):
    """Marginal weights on the loose distinctions at the given bit positions (y = sum bit_j << j)."""
    cube = weights.reshape((2,) * size_bits)
    keep = {size_bits - 1 - p for p in positions}
    summed = tuple(a for a in range(size_bits) if a not in keep)
    return cube.sum(axis=summed).reshape(-1) if summed else cube.reshape(-1)


def elsewhere_report(frame, plan, loose, marginal, law, sigma0, sigma, u):
    """Supplementary (not part of the frozen definition): how far from knot u the old-word distribution
    moves when only u's allocation changes, as the total variation of each other knot's loose marginal."""
    L = len(loose)
    W0 = marginal * A.weights_on_loose(plan, sigma0, law, loose)
    W1 = marginal * A.weights_on_loose(plan, sigma, law, loose)
    dist = bfs_distances(frame, u)
    own = [loose.index(d) for d in plan.loose[u]]
    onum, oden = A.tv_from_weights(marginal_vector(W0, own, L), marginal_vector(W1, own, L))
    out = {"_own_loose_marginal_tv": frac(onum, oden), "_own_loose_marginal_tv_decimal": float(Fraction(onum, oden))}
    for v, ds in plan.loose.items():
        if v == u or not ds:
            continue
        positions = [loose.index(d) for d in ds]
        a, b = marginal_vector(W0, positions, L), marginal_vector(W1, positions, L)
        num, den = A.tv_from_weights(a, b)
        both = positions + [loose.index(d) for d in plan.loose[u]]
        a2, b2 = marginal_vector(W0, both, L), marginal_vector(W1, both, L)
        num2, den2 = A.tv_from_weights(a2, b2)
        out[str(v)] = {"end_distance_in_shared_distinctions": dist.get(v), "tv_of_loose_of_v": frac(num, den),
                       "tv_of_loose_of_v_decimal": float(Fraction(num, den)),
                       "tv_of_loose_of_u_and_v": frac(num2, den2), "tv_of_loose_of_u_and_v_decimal": float(Fraction(num2, den2))}
    return out


def random_allocation(plan, rng):
    allocation = E.canonical_allocation(plan)
    for k in allocation:
        rng.shuffle(allocation[k])
    return allocation


def sampled_step(label, frame, law, later_rounds, samples, rng):
    """Second funded step where the old structure is too large to enumerate: random allocations only.
    Checks (i) and (ii) of R3; (iii) is not computed here."""
    t0 = time.time()
    plan = E.plan_round(frame, law)
    record = {"label": label, "status": plan.status, "sampled_not_enumerated": True}
    if plan.status != "extend":
        return record, None
    grown0, births0 = E.apply_plan(frame, plan)
    base_births, base_later = E.birth_signature(births0), later_signature(grown0, law, later_rounds)
    z0 = counting.count_words(grown0, law, big=True)
    changed = changed_later = noniso = zdiff = 0
    for _ in range(samples):
        sigma = random_allocation(plan, rng)
        grown, births = E.apply_plan(frame, plan, sigma)
        pi = A.relabelling(plan, E.canonical_allocation(plan), sigma)
        noniso += apply_pi(grown0, pi) != tuple(tuple(sorted(r)) for r in grown)
        changed += E.birth_signature(births) != base_births
        changed_later += later_signature(grown, law, later_rounds) != base_later
        zdiff += counting.count_words(grown, law, big=True) != z0
    record.update({"old_knots": len(frame), "old_distinctions": len({d for r in frame for d in r}),
                   "births": len(plan.parents), "raw_allocations": A.raw_total(plan),
                   "allocation_classes": A.class_count(plan), "allocations_sampled": samples,
                   "classes_with_changed_round_births": changed, "classes_with_changed_later_births": changed_later,
                   "classes_not_isomorphic_to_canonical_by_relabelling": noniso,
                   "grown_allowed_words_canonical": z0, "classes_with_different_grown_word_count": zdiff,
                   "later_rounds_compared": later_rounds, "seconds": round(time.time() - t0, 1)})
    return record, grown0


def horizon_for(structure):
    return {"seven": 6, "clock": 16, "stall": 6}[structure]


def start_for(structure):
    return {"seven": S.seven_knot_source(), "clock": S.five_founder_clock(),
            "stall": S.stall_start((1, 1))}[structure]


def run_structure(structure, law, include_beyond_cap, sample_step2=0):
    rng = random.Random(SEED)
    frame = start_for(structure)
    horizon = horizon_for(structure)
    out = {"structure": structure, "law": law, "horizon_rounds": horizon, "steps": []}
    for step in (1, 2):
        n_old = len({d for r in frame for d in r})
        if step == 2 and n_old > CAP and not include_beyond_cap:
            out["steps"].append({"label": f"funded step {step}", "skipped": f"{n_old} old distinctions exceed the cap {CAP}"})
            if sample_step2:
                record, _ = sampled_step(f"funded step {step} (sampled allocations only)", frame, law, horizon - step,
                                         sample_step2, rng)
                out["steps"].append(record)
            break
        result = analyse_step(f"funded step {step}" + (" (beyond cap, supplementary)" if n_old > CAP else ""),
                              frame, law, horizon - step, rng, 12)
        record, frame = result
        out["steps"].append(record)
        if frame is None:
            break
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--structure", required=True, choices=("seven", "clock", "stall"))
    parser.add_argument("--law", required=True, choices=E.LAWS)
    parser.add_argument("--beyond-cap", action="store_true")
    parser.add_argument("--sample-step2", type=int, default=0,
                        help="when step 2 exceeds the cap, check this many random allocations (R3 i and ii only)")
    args = parser.parse_args()
    result = run_structure(args.structure, args.law, args.beyond_cap, args.sample_step2)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    tag = "_beyond_cap" if args.beyond_cap else ""
    target = ARTIFACTS / f"r3_{args.structure}_{args.law}{tag}.json"
    target.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    for step in result["steps"]:
        print(json.dumps({k: v for k, v in step.items() if k != "knots"}, sort_keys=True))
        for knot, info in sorted(step.get("knots", {}).items(), key=lambda kv: int(kv[0])):
            print("  knot", knot, json.dumps(info, sort_keys=True))
    print("written", target)


if __name__ == "__main__":
    main()
