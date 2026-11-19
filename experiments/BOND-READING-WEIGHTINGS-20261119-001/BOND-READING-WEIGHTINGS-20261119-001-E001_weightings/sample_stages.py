"""Sample labelled starts and replay their complete cheapest-count rounds.

Each JSONL draw starts with its named ordinary meeting pattern and ends with
one outcome. In between, positive-age rows carry every literal support and a
check of whether another complete round is available, including at age three.
The two production paths below are the archived growth law with its equivalent
maximal-clique implementation and the independent support-lineage checker.
"""

from collections import Counter
from functools import cache
import hashlib
import heapq
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
from pathlib import Path
import random
import sys
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARTIFACTS = ROOT / "artifacts" / HERE.parent.name / HERE.name
START_LAW = "FIRST-KNOT-20261118-001B/FIRST-KNOT-20261118-001B-E001_two_knots/startlib.py"
CLIQUE_LAW = "JOIN-GROWTH-20261118-001B/JOIN-GROWTH-20261118-001B-E001_joins/fastlib.py"
CHECKER = "GROWN-END-SWAP-20261119-001/GROWN-END-SWAP-20261119-001-E001_reached/verify.py"

WEIGHTINGS = ("uniform_labelled_tree", "uniform_tree_plus_links", "uniform_recursive_tree")
SIZES = (4, 6, 8, 12, 20, 32)
REPLICATES = 64
BASE_SEED = 20261119071
MAX_AGE = 3
JUNCTION_CAP = 350
DISTINCTION_CAP = 950


@cache
def load_source(name, source):
    spec = spec_from_file_location(name, ROOT / "experiments" / source)
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def decode_prufer(word, m):
    degrees = [1] * m
    for holder in word:
        degrees[holder] += 1
    leaves = [holder for holder in range(m) if degrees[holder] == 1]
    heapq.heapify(leaves)
    links = []
    for holder in word:
        leaf = heapq.heappop(leaves)
        links.append(tuple(sorted((leaf, holder))))
        degrees[holder] -= 1
        if degrees[holder] == 1:
            heapq.heappush(leaves, holder)
    links.append(tuple(sorted(leaves)))
    return sorted(links)


def draw_start(weighting, m, replicate):
    """Use a separate Random instance seeded by the complete draw identity."""
    key = f"{BASE_SEED}|{weighting}|{m}|{replicate}".encode("ascii")
    digest = hashlib.sha256(key).hexdigest()
    rng = random.Random(int(digest, 16))
    if weighting == "uniform_recursive_tree":
        parents = [rng.randrange(child) for child in range(1, m)]
        naming = list(range(m))
        rng.shuffle(naming)
        tree = sorted(tuple(sorted((naming[parent], naming[child])))
                      for child, parent in enumerate(parents, 1))
        trace = {"insertion_parents": parents, "insertion_to_name": naming}
    elif weighting in WEIGHTINGS:
        word = [rng.randrange(m) for _ in range(m - 2)]
        tree = decode_prufer(word, m)
        trace = {"prufer_word": word}
    else:
        raise ValueError(f"unknown weighting {weighting!r}")

    additions = []
    if weighting == "uniform_tree_plus_links":
        tree_links = set(tree)
        available = [pair for pair in combinations(range(m), 2) if pair not in tree_links]
        additions = sorted(rng.sample(available, min((m - 1 + 3) // 4, len(available))))
    return sorted(tree + additions), {
        "draw_seed_sha256": digest, "tree_links": tree, "added_links": additions, **trace,
    }


def supports(m, links):
    """One shared distinction per ordinary meeting, then the common loose policy."""
    stars = [[] for _ in range(m)]
    for bit, (u, v) in enumerate(links):
        stars[u].append(bit)
        stars[v].append(bit)
    bit = len(links)
    for star in stars:
        free = max(0, 3 - len(star))
        star.extend(range(bit, bit + free))
        bit += free
    return stars


def round_parents(source, checker):
    """Inspect only the current groups and demand to decide future availability."""
    if not source.loose:
        return {"status": "closed"}, []

    groups = sorted(checker.groups(source.neighbors, source.live), key=sorted)
    used = Counter(holder for group in groups for holder in group)
    available = Counter(source.loose.values())
    deficits = [[holder, used[holder], available[holder]] for holder in sorted(used - available)]
    if deficits:
        return {"status": "stalled", "demand_deficits": deficits}, []

    offshoots = [(holder,) for holder in sorted(available)
                 for _ in range(available[holder] - used[holder])]
    parents = [tuple(sorted(group)) for group in groups] + offshoots
    checker.require(bool(parents), "an open available round has no proposed births")
    return {"status": "available", "new_junctions": len(parents)}, parents


def preflight(source, parents, checker, junction_cap, distinction_cap):
    """Bound a round before creating any of its supports.

    Even if the next arrangement is capped, the current round remains lawfully
    available. When the cheap lower bound already fails we retain that bound
    without constructing the prospective meeting pattern for the lookahead.
    """
    before, births = len(source.stars), len(parents)
    junctions = before + births
    width_lower = len(source.labels) + (births if births > 1 else 0)
    result = {"J": junctions, "J_lower": junctions,
              "n": width_lower if births == 1 else None, "n_lower": width_lower}
    if junctions > junction_cap or width_lower > distinction_cap:
        return result

    # New junctions meet only their parents, so older meetings are immaterial.
    if births == 1:
        width = len(source.labels)
    else:
        neighbors = [set() for _ in range(junctions)]
        for child, holders in enumerate(parents, before):
            neighbors[child].update(holders)
            for parent in holders:
                neighbors[parent].add(child)
        new = frozenset(range(before, junctions))
        demand = Counter(holder for group in checker.groups(neighbors, new) for holder in group)
        width = len(source.labels) + sum(max(demand[holder], 3 - len(group), 1)
                                         for holder, group in enumerate(parents, before))
    return {**result, "n": width, "n_lower": width}


def describe_stage(source, raw, upcoming):
    return {"J": len(raw), "n": len(source.labels), "stars": raw,
            "live_sites": sorted(source.live), "loose_distinctions": sorted(source.loose),
            "loose_by_site": sorted(Counter(source.loose.values()).items()),
            "closed": not source.loose,
            "can_grow": upcoming["status"] == "available", "next_round": upcoming}


def replay(m, links, *, junction_cap=JUNCTION_CAP, distinction_cap=DISTINCTION_CAP, fast=True):
    """Verify the initial gate, then grow with the literal law and replay each round."""
    law = load_source("weighting_startlib", START_LAW)
    checker = load_source("weighting_verify", CHECKER)
    raw = supports(m, links)
    source = checker.Arrangement.parse(raw)
    gate = checker.start_audit(source)
    checker.require(gate["meets_once"], "a sampled ordinary pair meets more than once")
    upcoming, parents = round_parents(source, checker) if gate["census_open_legal"] else ({
        "status": "invalid_start"}, [])
    yield {"kind": "start", "age": 0, **describe_stage(source, raw, upcoming),
           "ordinary_links": links, "gate": gate}
    if not gate["census_open_legal"]:
        yield {"kind": "terminal", "age": 0, "outcome": "invalid_start", "observed_stages": 0}
        return

    grown = law.from_junctions(raw)
    age = 0
    while True:
        status = upcoming["status"]
        if status == "stalled":
            checker.require(grown.step(law.gf2(law.F.fewest), None) is None,
                            "production disagrees about a stall")
            yield {"kind": "terminal", "age": age, "attempted_age": age + 1,
                   "outcome": "first_round_stall" if age == 0 else "later_round_stall",
                   "observed_stages": age, **upcoming}
            return
        if status == "closed" or age == MAX_AGE:
            yield {"kind": "terminal", "age": age, "outcome": "closed" if status == "closed" else "completed",
                   "observed_stages": age}
            return

        forecast = preflight(source, parents, checker, junction_cap, distinction_cap)
        if forecast["J_lower"] > junction_cap or forecast["n_lower"] > distinction_cap:
            yield {"kind": "terminal", "age": age, "attempted_age": age + 1, "outcome": "expansion_cap",
                   "observed_stages": age, "attempted_size": forecast,
                   "caps_exceeded": (["J"] if forecast["J_lower"] > junction_cap else [])
                   + (["n"] if forecast["n_lower"] > distinction_cap else [])}
            return

        production_groups = law.F.Presentation.groups_among
        if fast:
            production_groups = load_source("weighting_fastlib", CLIQUE_LAW).groups_among
        with patch.object(law.F.Presentation, "groups_among", production_groups):
            result = grown.step(law.gf2(law.F.fewest), None)
        checker.require(result and result["new"] == len(parents), "production disagrees with the parent count")
        checker.require(grown.implied_mismatch == 0, "production implication disagrees with elimination")
        raw = [list(star) for star in grown.bits_of]
        following = checker.Arrangement.parse(raw)
        checker.round_replay(source, following)
        checker.require(len(raw) == forecast["J"] and grown.nbits == forecast["n"],
                        "production disagrees with the preflight size")
        checker.require(following.labels == tuple(range(grown.nbits)), "distinction names are not dense")
        pairs = [tuple(owners) for owners in following.owners.values() if len(owners) == 2]
        checker.require(len(pairs) == len(set(pairs)), "a reached ordinary pair meets more than once")

        source = following
        age += 1
        upcoming, parents = round_parents(source, checker)
        yield {"kind": "stage", "age": age, **describe_stage(source, raw, upcoming)}


def run_draw(weighting, m, replicate):
    links, trace = draw_start(weighting, m, replicate)
    rows = list(replay(m, links))
    rows[0].update(trace)
    return [{"weighting": weighting, "m": m, "replicate": replicate, **row} for row in rows]


def check_controls():
    """Literal positive, invalid, stalled, closed, and capped cases without sampling."""
    path = [(0, 1), (1, 2), (2, 3)]
    first_stall = [(0, 1), (0, 2), (0, 3), (3, 4)]
    invalid = list(combinations(range(4), 2)) + [(0, 4)]
    closes = [pair for pair in combinations(range(4), 2) if pair != (0, 1)]
    controls = (("path", 4, path, "completed", 3),
                ("invalid", 5, invalid, "invalid_start", 0),
                ("first_stall", 5, first_stall, "first_round_stall", 0),
                ("closes", 4, closes, "closed", 1))
    summaries = {}
    for name, m, links, outcome, age in controls:
        rows = list(replay(m, links))
        assert rows == list(replay(m, links, fast=False)), name
        assert (rows[-1]["outcome"], rows[-1]["age"]) == (outcome, age), name
        summaries[name] = {"outcome": outcome, "age": age}
    capped = list(replay(4, path, junction_cap=4))
    assert capped[0]["can_grow"] and capped[-1]["outcome"] == "expansion_cap"
    assert capped[-1]["attempted_size"]["J"] > 4
    summaries["capped"] = capped[-1]
    return summaries
