"""Reconstruct the first meetings and retain the actual endpoint roles."""

import ast
from collections import Counter
import gzip
import hashlib
from itertools import product
import json
import os
from pathlib import Path
import sys
import tempfile
import time
from types import ModuleType


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OLD_ENGINE = (
    ROOT / "experiments" / "WHAT-A-BIRTH-CARRIES-20261125-001B"
    / "WHAT-A-BIRTH-CARRIES-20261125-001B-E001_link_through_a_made_knot"
)
PROBE = ROOT / "research" / "WHAT-A-BIRTH-CARRIES-20261125-001" / "checks" / "reach_further"
ARCHIVED_CENSUS = ROOT / "research" / "KNOTS-WITHIN-REACH-20261125-001A" / "census_starts.json"
ARCHIVED_STARTS = ROOT / "research" / "WHAT-A-BIRTH-CARRIES-20261125-001B" / "starts.json"
ENGINE_BASE_SHA = "09017631d84ea56182230be5a4345ae8fbfcc504ae244ad4b34d74c282803a40"
READ_BASE_SHA = "f6295ac1e8bf89c904513a4dec033029d7ba22f9c854343e589f74e3f7c1db7e"
TAKES = {
    "MOST": "MET2-MANY",
    "SOLE": "MET2-SOLE",
    "RECENT": "MET2-RECENT",
    "OUTER": "MET2-OUTER",
}


def replace_once(source, old, new):
    if source.count(old) != 1:
        raise ValueError(f"archived engine patch expected one match for {old!r}")
    return source.replace(old, new)


def engine_source():
    """Apply the archived probe's replacements without executing its writer."""
    base = (OLD_ENGINE / "eng.py").read_bytes()
    reader = (OLD_ENGINE / "read.py").read_bytes()
    if hashlib.sha256(base).hexdigest() != ENGINE_BASE_SHA:
        raise ValueError("archived growth engine changed")
    if hashlib.sha256(reader).hexdigest() != READ_BASE_SHA:
        raise ValueError("archived reading code changed")
    patch_program = ast.parse((PROBE / "make_engine.py").read_text())
    patches = next(
        ast.literal_eval(node.value)
        for node in patch_program.body
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "REPS" for target in node.targets
        )
    )
    source = base.decode()
    for before, after in patches:
        source = replace_once(source, before, after)
    source = replace_once(
        source,
        "\n\n\ndef reach(S, take, p):",
        "\nTAKES += ('MET2-RECENT', 'MET2-OUTER')\n"
        "MET_KIND += ('MET2-RECENT', 'MET2-OUTER')\n"
        "\n\ndef reach(S, take, p):",
    )
    source = replace_once(
        source,
        "                elif len(c) == 1:          # a sole candidate (BD2 2.1)",
        "                elif take in ('MET2-RECENT', 'MET2-OUTER'):\n"
        "                    b['takes'] = choose_alternative(S, law, G, b, R, c)\n"
        "                elif len(c) == 1:          # a sole candidate (BD2 2.1)",
    )
    source = replace_once(
        source,
        "    S.round = rnd\n    return {'round': rnd,",
        "    S.round = rnd\n"
        "    G.previous_takes = frozenset(d for b in births for d in b['takes'])\n"
        "    return {'round': rnd,",
    )
    return source


def near_candidates(stage, law, birth, roster=None):
    near_law = ENG.Law(law.ration, law.treatment, "MET-SOLE", law.knot_law)
    return ENG.candidates(stage, near_law, birth, roster)


def choose_alternative(stage, law, guard, birth, roster, candidates):
    if len(candidates) == 1:
        return [candidates[0][0]]
    offered = {d for d, _ in candidates}
    if law.take == "MET2-RECENT":
        choices = offered & getattr(guard, "previous_takes", frozenset())
    else:
        choices = offered - {d for d, _ in near_candidates(stage, law, birth, roster)}
    return list(choices) if len(choices) == 1 else []


def setup(params):
    global ENG, READ, CASES, RULES, KNOT_LAWS, OUTPUT, CENSUS, NAMED, CASE_FILTER
    global CONTRACT_SHA256, CASES_SHA256, ENGINE_SHA256
    contract_path = Path(params.get("contract", HERE.parent / "contract.json"))
    contract_bytes = contract_path.read_bytes()
    CONTRACT_SHA256 = hashlib.sha256(contract_bytes).hexdigest()
    if params.get("contract_sha256", CONTRACT_SHA256) != CONTRACT_SHA256:
        raise ValueError("frozen contract changed")
    contract = json.loads(contract_bytes)
    if contract["status"] != "frozen":
        raise ValueError("the link contract must be frozen")
    for relative, expected in contract["inputs"].items():
        if hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() != expected:
            raise ValueError(f"frozen input changed: {relative}")
    case_path = contract_path.parent / contract["cases"]
    case_bytes = case_path.read_bytes()
    CASES_SHA256 = hashlib.sha256(case_bytes).hexdigest()
    if CASES_SHA256 != contract["inputs"][str(case_path.resolve().relative_to(ROOT))]:
        raise ValueError("frozen cases changed")
    CASES = json.loads(case_bytes)
    RULES, KNOT_LAWS = contract["rules"], contract["knot_laws"]
    OUTPUT = Path(params["artifact_dir"]).resolve()
    CASE_FILTER = set(params["rehearsal_case_ids"].split(",")) if "rehearsal_case_ids" in params else None
    if CASE_FILTER is not None and CASE_FILTER - {row["id"] for row in CASES}:
        raise ValueError("unknown frozen rehearsal case")
    CENSUS = json.loads(ARCHIVED_CENSUS.read_bytes())
    NAMED = json.loads(ARCHIVED_STARTS.read_bytes())

    source = engine_source()
    ENGINE_SHA256 = hashlib.sha256(source.encode()).hexdigest()
    if params.get("engine_sha256", ENGINE_SHA256) != ENGINE_SHA256:
        raise ValueError("rendered engine changed")
    ENG = ModuleType("eng")
    ENG.__file__ = str(OLD_ENGINE / "eng.py")
    ENG.choose_alternative = choose_alternative
    sys.modules["eng"] = ENG
    sys.path.insert(0, str(OLD_ENGINE))
    exec(compile(source, "<frozen reach probe>", "exec"), ENG.__dict__)
    import read as READ


def cases():
    for case in CASES:
        if CASE_FILTER is None or case["id"] in CASE_FILTER:
            for rule, kl in product(RULES, KNOT_LAWS):
                yield f"{case['id']}--{rule}--{kl}", {**case, "rule": rule, "kl": kl}


def start_stars(name):
    if name.startswith("census:"):
        return CENSUS[int(name.split(":")[1])]["stars"]
    if name.startswith("ringk:"):
        loose = list(map(int, name.split(":")[1].split(",")))
        size = len(loose)
        next_distinction = size
        stars = []
        for i, count in enumerate(loose):
            stars.append([(i - 1) % size, i, *range(next_distinction, next_distinction + count)])
            next_distinction += count
        return stars
    if name == NAMED["extra"]["name"]:
        return NAMED["extra"]["stars"]
    return NAMED["stars"][name]


def write_rows(kind, rows):
    digest = hashlib.sha256()
    folder = OUTPUT / "raw" / kind
    folder.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix=".pending-", dir=folder, delete=False) as output:
        pending = Path(output.name)
        try:
            with gzip.GzipFile(filename="", fileobj=output, mode="wb", mtime=0, compresslevel=3) as file:
                for row in rows:
                    line = json.dumps(row, separators=(",", ":"), sort_keys=True).encode("ascii") + b"\n"
                    digest.update(line)
                    file.write(line)
            output.flush()
            os.fsync(output.fileno())
            sha256 = digest.hexdigest()
            path = folder / f"{sha256}.jsonl.gz"
            try:
                os.link(pending, path)
            except FileExistsError:
                pass
        finally:
            pending.unlink(missing_ok=True)
    return str(path.relative_to(OUTPUT)), sha256


def support_rows(growth):
    before = 0
    for t, stage in enumerate(growth.snaps):
        births = [] if t == 0 else growth.recs[t - 1]["births"]
        yield {
            "round": t,
            "knots": stage.n_knots,
            "distinctions": stage.n_distinctions,
            "supports": [sorted(support) for support in stage.places[before:]],
            "barred": [d for d, barred in enumerate(stage.barred) if barred],
            "births": [
                {key: birth[key] for key in ("id", "kind", "parents", "loose", "takes", "implied")}
                for birth in births
            ],
        }
        before = stage.n_knots


def take_offers(growth):
    """The exact pre-round offer and its one-step control for births that took."""
    offers = {}
    for t, record in enumerate(growth.recs, 1):
        stage = growth.snaps[t - 1]
        for birth in record["births"]:
            if birth["takes"]:
                near = dict(near_candidates(stage, growth.law, birth))
                offers[birth["id"]] = {
                    "round": t,
                    "taken": birth["takes"],
                    "C1": sorted(near),
                    "C2": [
                        {"d": d, "witnesses": list(ws), "holders": list(stage.holders[d])}
                        for d, ws in birth["cands"]
                    ],
                }
    return offers


def put_route(routes, kind, w, u, v, supports, roles, **extra):
    key = kind, w, u, v
    x, y = supports[u], supports[v]
    if kind == "take":
        x_arms = y_arms = set(extra.pop("taken"))
    else:
        x_arms, y_arms = supports[w] & x, supports[w] & y
    route = {
        "route": kind, "w": w, "u": u, "v": v,
        "contacts": sorted(x_arms & y_arms),
        "x_arms": sorted(x_arms), "y_arms": sorted(y_arms),
        "a": sorted(x - y), "b": sorted(y - x),
        "u_roles": READ.bitlist(roles[u]), "v_roles": READ.bitlist(roles[v]),
        "w_roles": READ.bitlist(roles[w]),
        **extra,
    }
    if key not in routes:
        routes[key] = route
    elif routes[key] != route:
        raise ValueError(f"conflicting route records for {key}")


def meeting_routes(growth, t, i, j, roles, offers, supports):
    """Use actual met sets at each phase and actual previously held takes."""
    record = growth.recs[t - 1]
    prev = growth.snaps[t - 1]
    mx, my = 1 << i, 1 << j
    mask = mx | my
    routes = {}
    for kind, roster in (("met", record["roster"]), ("demand", record["demand"])):
        if roster is None:
            continue
        for members, witnesses in roster.sc.items():
            xs = [u for u in members if roles[u] & mask == mx]
            ys = [v for v in members if roles[v] & mask == my]
            for w in witnesses:
                if w < prev.n_knots:
                    for u, v in product(xs, ys):
                        put_route(routes, kind, w, u, v, supports, roles)
    for birth in record["births"]:
        recipient = birth["id"]
        side = roles[recipient] & mask
        if side not in (mx, my) or not birth["takes"]:
            continue
        for d, holders in birth["take_holders"].items():
            near = d in offers[recipient]["C1"]
            for w in holders:
                if roles[w] & mask == mask ^ side:
                    u, v = (recipient, w) if side == mx else (w, recipient)
                    put_route(
                        routes, "take", w, u, v, supports, roles, taken=[d],
                        recipient=recipient, pre_holder=w, near_eligible=near,
                    )
    return [routes[key] for key in sorted(routes)]


def distinction_records(prev, stage, routes):
    distinctions = set()
    for route in routes:
        for key in ("a", "b", "x_arms", "y_arms"):
            distinctions.update(route[key])
    return [
        {
            "d": d,
            "first_holder_round": min(stage.made[w] for w in stage.holders[d]),
            "holders_before": list(prev.holders[d]) if d < prev.n_distinctions else [],
            "holders_after": list(stage.holders[d]),
        }
        for d in sorted(distinctions)
    ]


def first_meeting_rows(growth, splits, offers, coverage):
    supports = [set(support) for support in growth.S.places]
    for s in splits:
        split = {"split": s, "has_following_round": s < growth.rounds_read}
        coverage.append(split)
        if not split["has_following_round"]:
            continue
        parts = ENG.roster_parts(growth.recs[s]["roster"])
        part_of = {u: i for i, part in enumerate(parts) for u in part}
        classes = ENG.classes_of_parts(growth.snaps[s], parts)
        same = Counter(classes)
        split["eligible_pairs"] = (len(parts) ** 2 - sum(n ** 2 for n in same.values())) // 2
        roles = READ.desc_bits(growth, s, part_of)
        first = READ.first_meetings(growth, s, roles)
        index = {}
        ancestors = {}
        for (i, j), (t, how) in sorted(first.items(), key=lambda item: (item[1][0], item[0])):
            if classes[i] == classes[j]:
                continue
            prev, stage = growth.snaps[t - 1:t + 1]
            routes = meeting_routes(growth, t, i, j, roles, offers, supports)
            view = READ.View(growth, None, roles, i, j, s, parts[i], parts[j])
            if t not in index:
                index[t] = READ.RoundIndex(growth.recs[t - 1], roles)
                ancestors[t] = READ.ancestor_bits(stage)
            link = READ.linking(view, t, index[t], ancestors[t])
            recipients = sorted({route["recipient"] for route in routes if route["route"] == "take"})
            yield {
                "s": s, "t": t, "X": list(parts[i]), "Y": list(parts[j]),
                "meeting_types": how,
                "routes": routes,
                "take_offers": {str(u): offers[u] for u in recipients},
                "distinctions": distinction_records(prev, stage, routes),
                "linking_knots": [
                    {key: knot[key] for key in ("knot", "made", "how", "class", "linking_distinctions")}
                    for knot in link["linking"]
                ],
                "link_verdict": link["link_verdict"],
                "strict": link["strict"],
                "start_knot_holds_linking_distinction": link["start_knot_holds_linking_distinction"],
            }


def run(case_id, case):
    if case_id != f"{case['id']}--{case['rule']}--{case['kl']}":
        raise ValueError("case identifiers disagree")
    started = time.monotonic()
    law = ENG.Law(case["ration"], case["treatment"], TAKES[case["rule"]], case["kl"])
    growth = ENG.Run(law, stars=start_stars(case["start"]), rounds=case["rounds"], knot_bound=case["knot_bound"])
    grew = time.monotonic()
    support_file, support_sha256 = write_rows("supports", support_rows(growth))
    wrote_supports = time.monotonic()
    offers = take_offers(growth)
    coverage = []
    tallies = Counter()

    def measured_events():
        for row in first_meeting_rows(growth, case["splits"], offers, coverage):
            tallies["meetings"] += 1
            made = row["strict"] and not row["start_knot_holds_linking_distinction"]
            tallies["meetings_through_made_only"] += made
            tallies["meetings_with_pure_routes"] += bool(row["routes"])
            outer_take = any(route.get("near_eligible") is False for route in row["routes"])
            tallies["meetings_with_outer_take_route"] += outer_take
            tallies["made_only_meetings_with_outer_take_route"] += made and outer_take
            yield row

    events_file, events_sha256 = write_rows("events", measured_events())
    return {
        "case": case["id"], "start": case["start"], "ration": case["ration"], "treatment": case["treatment"],
        "rule": case["rule"], "kl": case["kl"], "rounds_read": growth.rounds_read,
        "stop": growth.stop or "rounds", "guard": growth.guard, "knots": growth.S.n_knots,
        "parity_closing_rounds": [row["round"] for row in growth.recs if row["closing"]],
        "support_file": support_file, "support_sha256": support_sha256,
        "events_file": events_file, "events_sha256": events_sha256,
        "take_count": sum(len(offer["taken"]) for offer in offers.values()),
        "outer_take_count": sum(len(set(offer["taken"]) - set(offer["C1"])) for offer in offers.values()),
        "meeting_counts": tallies,
        "split_coverage": coverage,
        "cases_sha256": CASES_SHA256, "contract_sha256": CONTRACT_SHA256, "engine_sha256": ENGINE_SHA256,
        "grow_seconds": round(grew - started, 6),
        "support_write_seconds": round(wrote_supports - grew, 6),
        "meeting_seconds": round(time.monotonic() - wrote_supports, 6),
    }
