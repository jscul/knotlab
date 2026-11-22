"""Join the private answer key to released guesses and count every registered stratum."""

from collections import Counter, defaultdict


def cell(rows):
    n = len(rows)
    return {"total": n, "correct": {arm: sum(x["actions"][arm] == expected(x["label"], arm)
                                               for x in rows) for arm in rows[0]["actions"]}}


def expected(label, arm):
    # An exchanged checkpoint is read under the recipient's unchanged convention.
    return int(label == "T") ^ int(arm.endswith("-opposite"))


def summarize(predictions, key_rows, public, known_histograms):
    keys = {k["id"]: k for k in key_rows}
    order = [p["id"] for p in predictions]
    if set(keys) != set(public) or order != list(public) or len(keys) != len(key_rows):
        raise ValueError("The scored roster does not match the blind predictions")
    cells = defaultdict(list)
    examples = {}
    novelty = defaultdict(Counter)
    committee = defaultdict(Counter)
    causal = defaultdict(Counter)
    for blind in sorted(predictions, key=lambda b: b["id"]):
        key = keys[blind["id"]]
        row = {**key, **blind}
        stratum, style, cond = key["style_stratum"], key["style"], key["condition"]
        turn, label = f"q{key['q']}", key["label"]
        tag = f"{stratum}/{cond}/{turn}/{label}"
        for group in (tag, f"{stratum}/{cond}/all/{label}", f"{stratum}/{cond}/all/all",
                      f"{stratum}/{cond}/{turn}/all", f"{stratum}/{style}/{cond}/{turn}/{label}"):
            cells[group].append(row)
        a = row["actions"]
        truth = int(label == "T")
        signature = tuple(row["counts"])
        overlap = known_histograms.get(signature, set())
        novelty[f"{stratum}/{cond}"]["new" if not overlap else
                    ("same_label" if overlap == {label} else "different_or_mixed")] += 1
        votes = row["votes"]
        c = committee[f"{stratum}/{cond}/{turn}"]
        c["total"] += 1
        c["both_actions_received_votes"] += int(min(votes) > 0)
        c["at_least_one_abstention"] += int(row["abstentions"] > 0)
        c["final_tie"] += int(votes[0] == votes[1])
        for law in ("parity", "nae"):
            left, right = (a[f"{law}-{v}"] for v in ("ordinary", "opposite"))
            for where in ("all", stratum, f"{stratum}/{cond}/{turn}"):
                counter = causal[law + "/" + where]
                counter["total"] += 1
                counter["originals_disagree"] += int(left != right)
                counter["both_donors_match"] += int(a[f"{law}-swapped-ordinary"] == right and
                                                     a[f"{law}-swapped-opposite"] == left)
                counter["both_reverse"] += int(left != right and a[f"{law}-swapped-ordinary"] == right and
                                                a[f"{law}-swapped-opposite"] == left)
                counter["both_shams_preserve"] += int(a[f"{law}-sham-ordinary"] == left and
                                                       a[f"{law}-sham-opposite"] == right)
                counter["both_restored"] += int(a[f"{law}-restored-ordinary"] == left and
                                                 a[f"{law}-restored-opposite"] == right)
                counter["both_clear_to_zero"] += int(a[f"{law}-clear-ordinary"] ==
                                                      a[f"{law}-clear-opposite"] == 0)
                counter["erase_selection_changes"] += int(a[f"{law}-erase-ordinary"] != left)
                counter["all_size_agrees"] += int(a[f"{law}-allsize-ordinary"] == left)
                counter["ordinary_twin_matches_all_schedules"] += int(all(
                    a[f"{law}-{v}"] == a[f"integer-{v}"] for v in ("ordinary","opposite","shifted")))
        category = tag + ("/correct" if a["parity-ordinary"] == truth else "/error")
        if category not in examples:
            raw = public[row["id"]]
            examples[category] = {**key, "bitmap": [raw[i:i+8] for i in range(0,64,8)],
                   "guess": "LT"[a["parity-ordinary"]], "previous": "LT"[a["previous-parity"]],
                   "donor_guess_in_ordinary_reader": "LT"[a["parity-swapped-ordinary"]],
                   "cleared_guess": "LT"[a["parity-clear-ordinary"]], "votes": votes,
                   "abstentions": row["abstentions"], "counts": list(signature)}
    scores = {name: cell(group) for name, group in sorted(cells.items())}
    primary = [f"blind/{style}/{condition}/q{q}/{letter}" for style in ("E","F")
               for condition in ("orientation","combined") for q in (2,3) for letter in "LT"]
    if len(predictions) != 704 or any(scores[g]["total"] != 8 for g in primary):
        raise ValueError("A frozen primary gate cell was missing or unbalanced")
    gate = {}
    for law in ("parity", "nae"):
        failed = [g for g in primary if 2*scores[g]["correct"][law+"-ordinary"] <= scores[g]["total"]]
        gate[law] = {"passed": not failed, "cell_count": len(primary), "failed_cells": failed}
    return {"cells": scores, "primary_gate": gate, "causal": causal, "novelty": novelty,
            "committee": committee, "representatives": examples}

