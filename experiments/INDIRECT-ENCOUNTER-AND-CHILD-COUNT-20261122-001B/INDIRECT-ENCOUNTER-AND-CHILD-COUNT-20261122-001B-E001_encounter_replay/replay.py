"""Materialize both frozen founders and trace funded children by their actual payments."""

from collections import Counter, defaultdict, deque
from gzip import compress
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
from runpy import run_path

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name
FREEZE_HASH = "bebde585685e9e009ed4dfdc1f79771705489c562e58f91ad157c5019ed67e86"
PRIOR, = (ROOT / "experiments/EARLIER-EVENT-AND-LATER-BIRTH-20261122-001B").glob("*/replay.py")
PHYSICAL = run_path(str(PRIOR))
END = PHYSICAL["END"]
LAWS = ("parity", "nae")
PAYERS = tuple(f"p{i}" for i in range(11))
ANCHORS = ("W", "P1", "P2", "D1", "D2", "Da", "P3")
RECEIVER = frozenset(("A", "B", "T"))
DONOR = frozenset(("D2", "D3"))

SECOND = {
    "A": ("W", "P1", "P2"), "B": ("W", "Z"), "T": ("Z",),
    "X": ("W", "D1", "D2"), "V1": ("P1", "D1"),
    "D2-P3": ("D2", "P3"), "DY": ("D2", "D3"), "DT": ("D3",),
    "source-unary": ("Zs",),
}
SLOTS = {
    "W": {"A": 0, "B": 1},
    "P1": {"A": 0},
    "P2": {"A": 0},
    "Z": {"B": 0, "T": 1},
    "D2": {"X": 0, "V2": 1, "D2-P3": 1, "DY": 2},
    "D3": {"DY": 0, "DT": 1},
}


class Marks:
    def __init__(self):
        self.names = []
        self.ids = {}

    def get(self, name):
        if name not in self.ids:
            self.ids[name] = len(self.names)
            self.names.append(name)
        return self.ids[name]


class GateError(Exception):
    """A falsifiable condition in the frozen comparison failed."""


def require(condition, explanation):
    if not condition:
        raise GateError(explanation)


def founder(connected, marks):
    recipients = [
        ["W", "P1", "D1"], ["W", "P2"], ["W", "D2", "P2"] if connected else ["W", "D2"],
        ["P1", "P2"], ["D1", "D2"], ["W", "Z"], ["D2", "D3"], ["Da", "Zs"],
        ["Da"] if connected else ["Da", "P2"], ["D2"] if connected else ["D2", "P3"],
        ["Da", "P3"] if connected else ["Da"],
    ]
    roster = defaultdict(set)
    for payer, targets in zip(PAYERS, recipients, strict=True):
        for child in targets:
            roster[child].add(payer)
    live = PAYERS + tuple(f"anchor-{target}" for target in ANCHORS)
    for target in ANCHORS:
        roster[target].add(f"anchor-{target}")
    candidate = nx.Graph()
    candidate.add_nodes_from(live)
    for parents in roster.values():
        candidate.add_edges_from(combinations(sorted(parents), 2))
    pair_witnesses = {f"pair/{'+'.join(pair)}": pair
                      for pair in sorted(tuple(sorted(p)) for p in candidate.edges)}
    barred = {f"blocked/{'+'.join(group)}": group
              for group in sorted(tuple(sorted(c)) for c in nx.find_cliques(candidate))
              if len(group) >= 3 and set(group) not in roster.values()}
    marker = {f"marker/{name}": (name,) for name in live}
    spent = list(pair_witnesses | barred | marker)
    # Pair witnesses, blocked larger witnesses and founder markers use one common
    # order. Their cycle is present in each actual preparation.
    holds = {role: [] for role in (*live, *spent)}
    values, openings = {}, {}

    def add(name, owners, bits):
        for i, value in enumerate(bits):
            mark = marks.get(f"{name}/{i}")
            values[mark] = value
            for owner in owners:
                holds[owner].append(mark)
            yield mark

    for witness, parents in (pair_witnesses | barred | marker).items():
        values_here = (1, 1) if witness in marker else (0, 0)
        for p in parents:
            tuple(add(f"{witness}/endpoint/{p}", (witness, p), values_here))
    for a, b in zip(spent, spent[1:] + spent[:1], strict=True):
        tuple(add(f"cycle/{a}/{b}", (a, b), (1, 0)))
    for target, parents in roster.items():
        for p in sorted(parents):
            bit, = add(f"open/{p}/{target}", (p,), (0,))
            openings[(p, target)] = bit
    return {"roles": list(holds), "holdings": tuple(map(tuple, holds.values())), "word": values,
            "openings": openings, "roster": dict(roster), "pair_witnesses": pair_witnesses,
            "blocked_source_cliques": barred, "spent_cycle": spent}


def first_labels(turn, source):
    ids = {role: i for i, role in enumerate(source["roles"])}
    expected = {frozenset(ids[p] for p in parents): target for target, parents in source["roster"].items()}
    observed = [frozenset(row["parents"]) for row in turn["births"]]
    require(len(observed) == len(expected) and set(observed) == expected.keys(),
            "The original physical operator does not produce exactly the requested first cohort.")
    return {row["knot"]: expected[frozenset(row["parents"])] for row in turn["births"]}


def later_labels(turn, roles, marks, cut, connected):
    if cut == 2:
        desired = {**SECOND, "V2": ("P2", "D2" if connected else "Da")}
    elif cut == 3:
        desired = {"G": ("A", "B"), "U": ("B", "T")}
    else:
        desired = {}
    by_parents = {frozenset(v): k for k, v in desired.items()}
    seen = Counter(tuple(row["parents"]) for row in turn["births"])
    labels = {}
    for row in turn["births"]:
        parents = frozenset(roles[p] for p in row["parents"])
        label = by_parents.get(parents)
        if label is not None and seen[row["parents"]] == 1:
            labels[row["knot"]] = label
            continue
        joined = "+".join(sorted(parents))
        if seen[row["parents"]] > 1:
            joined += "/" + marks.names[row["paid"][0]]
        labels[row["knot"]] = f"cut{cut}/({joined})"
    return labels


def choose_bindings(turn, source, marks, roles, labels, cut, sham, align_focal):
    if cut == 1:
        for row in turn["births"]:
            row["paid"] = tuple(source["openings"][(roles[p], labels[row["knot"]])] for p in row["parents"])
        return
    reservations = SLOTS if cut == 2 else {}
    if align_focal and cut == 3:
        reservations = {"A": {"G": 0}, "B": {"G": 0}}
    if not reservations:
        return
    incidence = defaultdict(list)
    for row in turn["births"]:
        for i, (payer, mark) in enumerate(zip(row["parents"], row["paid"], strict=True)):
            role, child = roles[payer], labels[row["knot"]]
            slot = reservations.get(role, {}).get(child)
            if sham and role == "D2" and slot in (0, 1):
                slot = 1 - slot
            incidence[role].append((row, i, mark, slot))
    for role, entries in incidence.items():
        by_slot = {slot: marks.ids[f"new/{role}/{slot}"] for *_, slot in entries if slot is not None}
        old = {d for _, _, d, _ in entries}
        require(set(by_slot.values()) <= old and len(by_slot) == sum(slot is not None for *_, slot in entries),
                f"Cannot reserve the enrolled payment slots at {role} in a complete cut.")
        others = iter(sorted(old - set(by_slot.values())))
        for row, i, _, slot in entries:
            pay = list(row["paid"])
            pay[i] = next(others) if slot is None else by_slot[slot]
            row["paid"] = tuple(pay)


def one_cut(stars, word, source, law, roles, marks, cut, connected, sham, align_focal):
    turn = PHYSICAL["plan"](stars, law)
    if turn["status"] != "extend":
        return turn, stars, word
    labels = first_labels(turn, source) if cut == 1 else later_labels(turn, roles, marks, cut, connected)
    choose_bindings(turn, source, marks, roles, labels, cut, sham, align_focal)
    for row in turn["births"]:
        role = labels[row["knot"]]
        row["fresh"] = tuple(marks.get(f"new/{role}/{i}") for i in range(len(row["fresh"])))
        row["role"] = role
        row["parent_roles"] = tuple(roles[p] for p in row["parents"])
    after, grown = write_values(law, cut, word, stars, turn)
    for row in turn["births"]:
        row["paid_values"] = tuple(word[d] for d in row["paid"])
        row["fresh_values"] = tuple(after[d] for d in row["fresh"])
    return turn, grown, after


def write_values(law, cut, word, stars, turn):
    """Use a lawful witness word, with every original value carried unchanged."""
    _, grown = PHYSICAL["fill"](law, word, stars, turn)
    fresh_value = int(law == "nae" and cut % 2 == 1)
    after = {**word, **{d: fresh_value for row in turn["births"] for d in row["fresh"]}}
    assert PHYSICAL["whole_word"](law, after, grown)
    return after, grown


def descendants(births, previous, pure):
    return {row["role"] for row in births if
            (set(row["parent_roles"]) <= previous if pure else bool(set(row["parent_roles"]) & previous))}


def new_families(births, cut, previous):
    source = descendants(births, previous["source"], pure=True)
    donor_pure = descendants(births, previous["donor_pure"], pure=True)
    donor_inclusive = descendants(births, previous["donor_inclusive"], pure=False)
    receiver = descendants(births, previous["receiver"], pure=True)
    focal = descendants(births, previous["focal"], pure=False) & receiver
    if cut == 1:
        require(DONOR <= source, "A donor release member is unavailable or lacks source-only parents.")
        donor_pure, donor_inclusive = set(DONOR), set(DONOR)
        source -= DONOR
    if cut == 2:
        require(RECEIVER <= source and not RECEIVER & donor_inclusive,
                "A receiver release member is unavailable or has a non-source parent or donor ancestry.")
        receiver = set(RECEIVER)
        source -= RECEIVER
    if cut == 3:
        require("G" in receiver, "No unique pure focal birth with actual parents A and B.")
        focal = {"G"}
    return {"source": source, "donor_pure": donor_pure, "donor_inclusive": donor_inclusive,
            "receiver": receiver, "focal": focal}


def run(law, connected, marks, sham=False, align_focal=False):
    source = founder(connected, marks)
    roles = source["roles"].copy()
    stars, values = source["holdings"], source["word"]
    levels = [{"holdings": stars, "word": values, "projection": PHYSICAL["projection"](law, stars),
               "roles": roles.copy(), "families": {"source": roles.copy(), "donor_pure": [],
               "donor_inclusive": [], "receiver": [], "focal": []}}]
    cuts = []
    result = {"law": law, "connected": connected, "sham": sham, "align_focal": align_focal,
              "levels": levels, "cuts": cuts,
              "source_cliques_held": source["blocked_source_cliques"], "spent_cycle": source["spent_cycle"]}
    try:
        require(PHYSICAL["whole_word"](law, values, stars), "The frozen founder word is unlawful.")
        for cut in range(1, 7):
            if cut > 4:
                guard = END["step"](END["from_stars"](stars), law, max_births=2048)
                if guard.status == "cap":
                    result["extra_cut_censor"] = {"cut": cut, "proposed_lower_bound": guard.planned_births_lower}
                    break
            try:
                turn, stars, values = one_cut(stars, values, source, law, roles, marks,
                                              cut, connected, sham, align_focal)
            except GateError:
                result["unmatched_cut_physical_plan"] = PHYSICAL["plan"](stars, law)
                raise
            cuts.append(turn)
            if turn["status"] != "extend":
                break
            roles.extend(row["role"] for row in turn["births"])
            require(len(set(roles)) == len(roles), "A birth receipt's audit role is ambiguous.")
            latest = {}
            try:
                latest = new_families(turn["births"], cut, {k: set(v) for k, v in levels[-1]["families"].items()})
            finally:
                levels.append({"holdings": stars, "word": values, "projection": PHYSICAL["projection"](law, stars),
                               "roles": roles.copy(), "families": {k: sorted(v) for k, v in latest.items()}})
    except GateError as err:
        result["failed_gate"] = str(err)
    return result


def relabel_trace(law, original):
    """Re-run every complete cut after reversing holder and distinction names."""
    first = original["levels"][0]
    holders = {i: len(first["holdings"]) - 1 - i for i in range(len(first["holdings"]))}
    marks = {d: 7 * (len(first["word"]) - i) + 13 for i, d in enumerate(sorted(first["word"]))}
    stars = tuple(tuple(marks[d] for d in box) for box in reversed(first["holdings"]))
    word = {marks[d]: value for d, value in first["word"].items()}
    levels = [{"holdings": stars, "word": word, "projection": PHYSICAL["projection"](law, stars),
               "roles": first["roles"][::-1], "families": first["families"]}]
    turns = []
    for cut, baseline in enumerate(original["cuts"], 1):
        turn = PHYSICAL["plan"](stars, law)
        PHYSICAL["transport"](baseline, turn, holders, marks)
        if turn["status"] != "extend":
            turns.append(turn)
            break
        by_new_id = {holders[row["knot"]]: row for row in baseline["births"]}
        for row in turn["births"]:
            row["role"] = by_new_id[row["knot"]]["role"]
            row["parent_roles"] = tuple(levels[-1]["roles"][k] for k in row["parents"])
            row["paid_values"] = tuple(word[d] for d in row["paid"])
        word, stars = write_values(law, cut, word, stars, turn)
        for row in turn["births"]:
            row["fresh_values"] = tuple(word[d] for d in row["fresh"])
        old = original["levels"][cut]
        assert {holders[k]: set(marks[d] for d in support) for k, support in enumerate(old["holdings"])} == {
            k: set(support) for k, support in enumerate(stars)}
        assert {marks[d]: bit for d, bit in old["word"].items()} == word
        levels.append({"holdings": stars, "word": word, "projection": PHYSICAL["projection"](law, stars),
                       "roles": levels[-1]["roles"] + [row["role"] for row in turn["births"]],
                       "families": old["families"]})
        turns.append(turn)
    return {"levels": levels, "cuts": turns, "holder_renaming": holders, "distinction_renaming": marks}


def births_at(result, cut):
    return {row["role"]: row for row in result["cuts"][cut-1]["births"]} if len(result["cuts"]) >= cut else {}


def actual_siblings(result, cut, anchor):
    return [row for row in births_at(result, cut).values() if anchor in row["parent_roles"]]


def witnesses(stars, pair):
    return PHYSICAL["witnesses"](stars, pair)


def witnessed_neighborhood(result, cut, marked):
    level = result["levels"][cut]
    stars, labels = level["holdings"], level["roles"]
    reverse = {label: k for k, label in enumerate(labels)}
    end = END["from_stars"](stars)
    near = set(reverse[k] for k in marked if k in reverse) & end.opens.keys()
    adjacency = END["neighbors"](end)
    support = near.union(*(adjacency[k] for k in near))
    blocks = END["restricted"](end, support).blocks
    proposed = result["cuts"][cut]["proposed_groups"] if len(result["cuts"]) > cut else ()
    return {"live_members": sorted(labels[k] for k in support),
            "witnessed_blocks": sorted(sorted(labels[k] for k in block) for block in blocks),
            "witnessed_pairs": [{"pair": sorted((labels[a], labels[b])),
                                 "actual_older_sharings": [{**w, "older_role": labels[w["holder"]]}
                                                           for w in witnesses(stars, (a, b))]}
                                for a, b in combinations(sorted(support), 2) if b in adjacency[a]],
            "proposed_groups_through_enrolled_members": [sorted(labels[k] for k in row)
                                                         for row in proposed if near & set(row)]}


def separation(level):
    families = level["families"]
    if not families or not families["receiver"]:
        return None
    names = level["roles"]
    start = {names.index(k) for k in families["receiver"]}
    goal = {names.index(k) for k in families["donor_pure"]}
    end = END["from_stars"](level["holdings"])
    neighbors = END["neighbors"](end)
    seen, pending = set(start), deque((k, 0) for k in sorted(start))
    while pending:
        node, steps = pending.popleft()
        if node in goal:
            return steps
        unseen = neighbors.get(node, set()) - seen
        seen.update(unseen)
        pending.extend((k, steps + 1) for k in unseen)
    return "separate"


def pair_probe(result, cut, left, right):
    if len(result["levels"]) <= cut:
        return None
    level = result["levels"][cut]
    roles = level["roles"]
    if left not in roles or right not in roles:
        return None
    pair = (roles.index(left), roles.index(right))
    older = witnesses(level["holdings"], pair)
    return [{**w, "older_role": roles[w["holder"]]} for w in older]


def summary(result):
    cuts, levels = result["cuts"], result["levels"]
    summary = {"statuses": [turn["status"] for turn in cuts],
               "complete_birth_counts": [len(turn["births"]) for turn in cuts],
               "founder_knots": len(levels[0]["holdings"]),
               "founder_distinctions": len(levels[0]["word"]),
               "level_projection_certificates": [level["projection"] for level in levels],
               "family_counts": [{k: len(v) for k, v in level["families"].items()} for level in levels]}
    if error := result.get("failed_gate"):
        summary["failed_gate"] = error
    if len(levels) < 5 or not levels[4]["families"]:
        return summary

    summary["donor_release"] = {k: births_at(result, 1)[k] for k in sorted(DONOR)}
    summary["receiver_release"] = {k: births_at(result, 2)[k] for k in sorted(RECEIVER)}
    summary["central_cut_two_births"] = {k: births_at(result, 2).get(k) for k in (*SECOND, "V2")}
    summary["release_neighborhood"] = witnessed_neighborhood(result, 2, RECEIVER)
    summary["receiver_release_children"] = {k: actual_siblings(result, 3, k) for k in sorted(RECEIVER)}
    summary["focal_birth"] = births_at(result, 3)["G"]
    summary["focal_neighborhood"] = witnessed_neighborhood(result, 3, ("G",))
    summary["focal_children"] = actual_siblings(result, 4, "G")
    summary["focal_children_receiving_donor_descendant"] = [
        row for row in summary["focal_children"] if set(row["parent_roles"]) & set(levels[3]["families"]["donor_inclusive"])
    ]
    summary["X_V2_older_witnesses"] = pair_probe(result, 2, "X", "V2")
    summary["X_P3_older_witnesses"] = pair_probe(result, 2, "X", "D2-P3")
    summary["pure_family_separation"] = [separation(level) for level in levels]
    summary["pure_focal_children"] = [row for row in summary["focal_children"]
                                     if row["role"] in levels[4]["families"]["focal"]]
    summary["focal_family_by_cut"] = [level["families"].get("focal") for level in levels]
    summary["source_branch"] = successive_unaries(result, 1, "Zs")
    summary["donor_branch"] = successive_unaries(result, 2, "DT")
    summary["receiver_branch"] = successive_unaries(result, 2, "T")
    return summary


def successive_unaries(result, start_cut, start):
    path = [start]
    for cut in range(start_cut + 1, len(result["cuts"]) + 1):
        options = [row for row in actual_siblings(result, cut, path[-1]) if len(row["parents"]) == 1]
        if len(options) != 1:
            break
        path.append(options[0]["role"])
    return path


def release_comparison(left, right, key):
    peer = right.get(key, {})
    verdict = {}
    for role, one in left.get(key, {}).items():
        two = peer.get(role, {})
        verdict[role] = bool(two) and paid_role_words(one) == paid_role_words(two) and all(
            one[field] == two[field] for field in ("fresh", "fresh_values"))
    return verdict


def paid_role_words(row):
    return sorted(zip(row["parent_roles"], row["paid"], row["paid_values"], strict=True))


def structural_signature(result):
    return [sorted((tuple(sorted(row["parent_roles"])), len(row["fresh"]), row["demand"]) for row in cut["births"])
            for cut in result["cuts"]]


def comparison(law, marks):
    intact = run(law, True, marks)
    diverted = run(law, False, marks)
    restored = run(law, True, marks)
    sham = run(law, True, marks, sham=True)
    runs = {"present": intact, "diverted": diverted, "restored": restored, "swapped_D2": sham,
            "renamed_present": relabel_trace(law, intact), "renamed_diverted": relabel_trace(law, diverted),
            "aligned_focal_present": run(law, True, marks, align_focal=True),
            "aligned_focal_diverted": run(law, False, marks, align_focal=True)}
    summaries = {k: summary(v) for k, v in runs.items()}
    summaries["checks"] = {
        "restored_exact_physical_trace": restored == intact,
        "binding_sham_preserves_structural_rosters": structural_signature(sham) == structural_signature(intact),
        "literal_receiver_release_match": release_comparison(summaries["present"], summaries["diverted"], "receiver_release"),
        "literal_donor_release_match": release_comparison(summaries["present"], summaries["diverted"], "donor_release"),
        "paid_child_counts": {name: len(row["focal_children"]) for name, row in summaries.items()
                              if "focal_children" in row},
        "renaming_preserves_complete_rosters": {
            name: structural_signature(runs[f"renamed_{name}"]) == structural_signature(runs[name])
            for name in ("present", "diverted")},
        "matched_focal_binding_preserves_complete_rosters": {
            name: structural_signature(runs[f"aligned_focal_{name}"]) == structural_signature(runs[name])
            for name in ("present", "diverted")},
    }
    aligned = [row.get("focal_birth") for name, row in summaries.items() if name.startswith("aligned_focal_")]
    if all(aligned):
        summaries["checks"]["matched_focal_actual_parent_payments_and_values"] = (
            paid_role_words(aligned[0]) == paid_role_words(aligned[1]))
    return runs, summaries


def founder_diff(left, right, mark_labels):
    old, new = [dict(zip(x["levels"][0]["roles"], map(set, x["levels"][0]["holdings"]), strict=True))
                for x in (left, right)]
    return {role: {"lost": [mark_labels[d] for d in sorted(old.get(role, set()) - new.get(role, set()))],
                   "gained": [mark_labels[d] for d in sorted(new.get(role, set()) - old.get(role, set()))]}
            for role in sorted(old.keys() | new.keys()) if old.get(role) != new.get(role)}


def knot_checks(traces):
    """Use the whole-presentation projections and symbolic checks at large arity."""
    result = {}
    for law, runs in traces.items():
        levels = [level for arm in runs.values() for level in arm["levels"]]
        supports = Counter(len(box) for level in levels for box in level["holdings"])
        result[law] = {
            "complete_physical_cuts": len(levels),
            "full_projection_pass": sum(level["projection"]["gate"] for level in levels),
            "symbolic": [{"arity": width, "holders_across_saved_cuts": n,
                          "allowed_words": (2**(width-1) if law == "parity" else 2**width-2),
                          "K1_K2_K3": width >= 3} for width, n in sorted(supports.items())],
            "explicit_knotlab_cli_controls": [PHYSICAL["canonical_check"](law, width)
                                              for width in sorted(supports) if 3 <= width <= 8],
        }
    return result


def main():
    contract = json.loads((HERE / "contract.json").read_text())
    freeze = sha256((ROOT / contract["preregistration"]).read_bytes()).hexdigest()
    assert freeze == contract["preregistration_sha256"] == FREEZE_HASH
    marks = Marks()
    traces, results = {}, {}
    for law in LAWS:
        traces[law], results[law] = comparison(law, marks)
        print(law, [(key, x["complete_birth_counts"], x.get("failed_gate"))
                    for key, x in results[law].items() if key != "checks"], flush=True)
        print(law, results[law]["checks"], flush=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    raw = {"marks": marks.names, "preparations": traces}
    complete_knot_checks = knot_checks(traces)
    compressed = compress((json.dumps(raw, separators=(",", ":")) + "\n").encode(), mtime=0)
    (OUTPUT / "physical_replay.json.gz").write_bytes(compressed)
    reports = {"freeze_sha256": freeze, "physical_replay_sha256": sha256(compressed).hexdigest(),
               "full_projection_and_knot_gates": complete_knot_checks,
               "physical_founder_changes": founder_diff(traces["parity"]["present"],
                                                        traces["parity"]["diverted"], marks.names),
               "law_and_preparation": results}
    (OUTPUT / "results.json").write_text(json.dumps(reports, indent=2) + "\n")


if __name__ == "__main__":
    main()
