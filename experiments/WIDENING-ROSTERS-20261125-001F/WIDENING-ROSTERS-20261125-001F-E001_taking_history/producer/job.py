"""Run the further-reaching taking rules on the frozen first-meeting panel."""

from collections import Counter
import hashlib
import importlib.util
from itertools import product
import json
from pathlib import Path
import time


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PREDECESSOR = (
    ROOT / "experiments" / "WIDENING-ROSTERS-20261125-001D"
    / "WIDENING-ROSTERS-20261125-001D-E001_links"
)
TAKES = {
    "EVER": "MET2-EVER",
    "LAST_USE": "MET2-LAST_USE",
    "NEWEST": "MET2-NEWEST",
    "SOLE_MADE": "MET2-SOLE_MADE",
    "THREE": "MET2-THREE",
}
MEETING_TYPES = {"group": "met", "demand group": "demand", "take": "take"}


def extend_growth_source(source):
    new_names = tuple(TAKES.values())
    source = D.replace_once(
        source,
        "MET_KIND += ('MET2-RECENT', 'MET2-OUTER')\n",
        "MET_KIND += ('MET2-RECENT', 'MET2-OUTER')\n"
        f"TAKES += {new_names!r}\nMET_KIND += {new_names!r}\n",
    )
    source = D.replace_once(
        source,
        "        self.peak = Counter()\n",
        "        self.peak = Counter()\n        self.latest_extra_round = {}\n",
    )
    source = D.replace_once(
        source,
        "elif take in ('MET2-RECENT', 'MET2-OUTER'):",
        f"elif take in {('MET2-RECENT', 'MET2-OUTER', *new_names)!r}:",
    )
    source = D.replace_once(
        source,
        "    G.previous_takes = frozenset(d for b in births for d in b['takes'])\n",
        "    G.previous_takes = frozenset(d for b in births for d in b['takes'])\n"
        "    for d in G.previous_takes:\n        G.latest_extra_round[d] = rnd\n",
    )
    return source


def creation_round(structure, distinction):
    maker = structure.maker[distinction]
    return 0 if maker is None else structure.made[maker]


def choose_using_history(stage, law, guard, birth, roster, candidates):
    if law.take not in TAKES.values():
        return PREDECESSOR_CHOICE(stage, law, guard, birth, roster, candidates)
    offered = [d for d, _ in candidates]
    if len(offered) < 2:
        return offered
    rule = law.take.removeprefix("MET2-")
    if rule == "EVER":
        chosen = [d for d in offered if d in guard.latest_extra_round]
    elif rule == "LAST_USE":
        latest = max((guard.latest_extra_round.get(d, 0) for d in offered), default=0)
        chosen = [d for d in offered if guard.latest_extra_round.get(d) == latest]
    elif rule == "NEWEST":
        ages = {d: creation_round(stage, d) for d in offered}
        latest = max(ages.values())
        chosen = [d for d in offered if ages[d] == latest]
    elif rule == "SOLE_MADE":
        chosen = [d for d in offered if stage.maker[d] is not None]
    else:
        assert rule == "THREE"
        chosen = [d for d in offered if len(stage.holders[d]) == 3]
    return chosen if len(chosen) == 1 else []


def setup(params):
    global D, PREDECESSOR_CHOICE, CONTRACT_SHA256, CASES_SHA256, RULES, KNOT_LAWS
    contract_path = Path(params.get("contract", HERE.parent / "contract.json"))
    contract_bytes = contract_path.read_bytes()
    CONTRACT_SHA256 = hashlib.sha256(contract_bytes).hexdigest()
    if params.get("contract_sha256", CONTRACT_SHA256) != CONTRACT_SHA256:
        raise ValueError("frozen history-taking contract changed")
    contract = json.loads(contract_bytes)
    if contract["status"] != "frozen" or set(contract["rules"]) != set(TAKES):
        raise ValueError("unexpected taking-history contract")
    for relative, digest in contract["inputs"].items():
        if hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() != digest:
            raise ValueError(f"frozen input changed: {relative}")
    CASES_SHA256 = contract["inputs"][contract["cases"]]
    RULES = list(contract["rules"])
    KNOT_LAWS = contract["knot_laws"]
    spec = importlib.util.spec_from_file_location("frozen_first_meeting_producer", PREDECESSOR / "producer/job.py")
    D = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(D)
    PREDECESSOR_CHOICE = D.choose_alternative
    source = extend_growth_source(D.engine_source())
    D.engine_source = lambda: source
    D.choose_alternative = choose_using_history
    D.setup({
        **params,
        "contract": str(PREDECESSOR / "contract.json"),
        "contract_sha256": contract["inputs"][str((PREDECESSOR / "contract.json").relative_to(ROOT))],
    })
    assert D.CASES_SHA256 == CASES_SHA256


def cases():
    for case in D.CASES:
        if D.CASE_FILTER is None or case["id"] in D.CASE_FILTER:
            for rule, kl in product(RULES, KNOT_LAWS):
                yield f"{case['id']}--{rule}--{kl}", {**case, "rule": rule, "kl": kl}


def inspect_plural_offers(growth, offers):
    counts = Counter()
    samples = {}
    lower_recipients = set()
    previous_round = {}
    for t, record in enumerate(growth.recs, 1):
        stage = growth.snaps[t - 1]
        for birth in record["births"]:
            candidates = [d for d, _ in birth["cands"]]
            if len(candidates) < 2:
                continue
            holder_counts = {d: len(stage.holders[d]) for d in candidates}
            maximum = max(holder_counts.values())
            most = [d for d, n in holder_counts.items() if n == maximum]
            taken = birth["takes"]
            if not taken:
                verdict = "abstained_with_unique_max" if len(most) == 1 else "abstained_with_max_tie"
            elif holder_counts[taken[0]] < maximum:
                verdict = "took_lower_than_max"
                lower_recipients.add(birth["id"])
            else:
                verdict = "took_unique_max" if len(most) == 1 else "took_tied_max"
            counts[verdict] += 1
            if verdict not in samples:
                samples[verdict] = {
                    "round": t, "recipient": birth["id"], "parents": list(birth["parents"]), "taken": taken,
                    "holders_of_most_held_candidates": maximum, "most_held_candidates": most,
                    "outer": bool(taken and taken[0] not in offers[birth["id"]]["C1"]),
                    "offer": [
                        {
                            "d": d, "holders": holder_counts[d], "created_round": creation_round(stage, d),
                            "last_extra_round": previous_round.get(d),
                        }
                        for d in candidates
                    ],
                }
        for birth in record["births"]:
            for d in birth["takes"]:
                previous_round[d] = t
    return counts, samples, lower_recipients


def outer_meeting_keys(growth, splits, offers):
    """All RD cross takes beyond the near offer, including mixed descent."""
    keys = set()
    for s in splits:
        if s >= growth.rounds_read:
            continue
        parts = D.ENG.roster_parts(growth.recs[s]["roster"])
        part_of = {u: i for i, part in enumerate(parts) for u in part}
        roles = D.READ.desc_bits(growth, s, part_of)
        for t in range(s + 1, growth.rounds_read + 1):
            births = [
                birth for birth in growth.recs[t - 1]["births"]
                if birth["takes"] and birth["takes"][0] not in offers[birth["id"]]["C1"]
            ]
            crosses = D.READ.round_meetings({"groups": [], "demand": None, "births": births}, roles)
            keys.update((s, t, parts[i], parts[j]) for i, j in crosses)
    return keys


def physical_sample(row, route):
    return {
        "s": row["s"], "t": row["t"], "X": row["X"], "Y": row["Y"],
        "meeting_types": sorted(MEETING_TYPES[t] for t in row["meeting_types"]),
        "link_verdict": row["link_verdict"],
        "start_knot_holds_linking_distinction": row["start_knot_holds_linking_distinction"],
        "linking_knots": row["linking_knots"], "route": route,
        "offer": row["take_offers"].get(str(route["recipient"])) if route and route["route"] == "take" else None,
    }


def run(case_id, case):
    if case_id != f"{case['id']}--{case['rule']}--{case['kl']}":
        raise ValueError("case identifiers disagree")
    started = time.monotonic()
    law = D.ENG.Law(case["ration"], case["treatment"], TAKES[case["rule"]], case["kl"])
    growth = D.ENG.Run(
        law, stars=D.start_stars(case["start"]), rounds=case["rounds"], knot_bound=case["knot_bound"],
    )
    grew = time.monotonic()
    support_file, support_sha256 = D.write_rows("supports", D.support_rows(growth))
    wrote_supports = time.monotonic()
    offers = D.take_offers(growth)
    choice_counts, choice_samples, lower_recipients = inspect_plural_offers(growth, offers)
    outer_keys = outer_meeting_keys(growth, case["splits"], offers)
    prepared = time.monotonic()
    coverage = []
    tallies = Counter()
    samples = {}

    def measured_events():
        for row in D.first_meeting_rows(growth, case["splits"], offers, coverage):
            key = (row["s"], row["t"], tuple(row["X"]), tuple(row["Y"]))
            pure_outer = next((r for r in row["routes"] if r.get("near_eligible") is False), None)
            lower_take = next((r for r in row["routes"] if r.get("recipient") in lower_recipients), None)
            made_only = row["strict"] and not row["start_knot_holds_linking_distinction"]
            direct_any = key in outer_keys
            assert pure_outer is None or direct_any
            tallies["meetings"] += 1
            tallies["strict_made_linkers"] += row["strict"]
            tallies["strict_made_no_start_held"] += made_only
            tallies["direct_outer_any"] += direct_any
            tallies["direct_outer_pure"] += pure_outer is not None
            tallies["strict_made_no_start_held_direct_outer_any"] += made_only and direct_any
            tallies["strict_made_no_start_held_direct_outer_pure"] += made_only and pure_outer is not None
            tallies["strict_made_no_start_held_lower_choice_route"] += made_only and lower_take is not None
            if made_only and "strict_made_no_start_held" not in samples:
                samples["strict_made_no_start_held"] = physical_sample(row, next(iter(row["routes"]), None))
            if made_only and pure_outer and "strict_made_no_start_held_direct_outer_pure" not in samples:
                samples["strict_made_no_start_held_direct_outer_pure"] = physical_sample(row, pure_outer)
            if made_only and lower_take and "strict_made_no_start_held_lower_choice_route" not in samples:
                samples["strict_made_no_start_held_lower_choice_route"] = physical_sample(row, lower_take)
            yield {
                "s": row["s"], "t": row["t"], "X": row["X"], "Y": row["Y"],
                "meeting_types": sorted(MEETING_TYPES[t] for t in row["meeting_types"]),
                "strict": row["strict"],
                "start_knot_holds_linking_distinction": row["start_knot_holds_linking_distinction"],
                "direct_outer": pure_outer is not None, "direct_outer_any": direct_any,
            }

    events_file, events_sha256 = D.write_rows("events", measured_events())
    return {
        "case": case["id"], "start": case["start"], "ration": case["ration"], "treatment": case["treatment"],
        "rule": case["rule"], "kl": case["kl"], "rounds_read": growth.rounds_read,
        "stop": growth.stop or "rounds", "guard": growth.guard, "knots": growth.S.n_knots,
        "splits": case["splits"], "split_coverage": coverage,
        "parity_closing_rounds": [row["round"] for row in growth.recs if row["closing"]],
        "support_file": support_file, "support_sha256": support_sha256,
        "events_file": events_file, "events_sha256": events_sha256,
        "take_count": sum(len(entry["taken"]) for entry in offers.values()),
        "outer_take_count": sum(len(set(entry["taken"]) - set(entry["C1"])) for entry in offers.values()),
        "meeting_counts": tallies, "meeting_samples": samples,
        "plural_offers_vs_most": choice_counts, "plural_offer_samples": choice_samples,
        "cases_sha256": CASES_SHA256, "contract_sha256": CONTRACT_SHA256, "engine_sha256": D.ENGINE_SHA256,
        "grow_seconds": round(grew - started, 6), "support_write_seconds": round(wrote_supports - grew, 6),
        "prepare_seconds": round(prepared - wrote_supports, 6),
        "meeting_seconds": round(time.monotonic() - prepared, 6),
    }
