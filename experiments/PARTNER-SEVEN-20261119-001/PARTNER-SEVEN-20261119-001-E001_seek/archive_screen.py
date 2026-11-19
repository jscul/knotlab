"""Exact complete-roster screens of the frozen partner-seeking archives."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import cache
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
import json
from pathlib import Path
import sys
from tempfile import NamedTemporaryFile

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARTIFACTS = ROOT / "artifacts" / HERE.parent.name / HERE.name
TOUCH_RUN = ROOT / "runs/touch-census"
EXPLOSIVE_RUN = ROOT / "runs/explosive"
MERGE_RUN = ROOT / "runs/merge-burst"
WALL_SUMMARY = ROOT / "artifacts/WALL-READ-20261119-001B/WALL-READ-20261119-001B-E001_past/results.json"
TOUCH_AGES = 6
EXPLOSIVE_AGES = 24
POINT_LIMIT = 2200
PAIR_LIMIT = 240_000
CLIQUE_LIMIT = 36_000
SHARD_SIZE = 96


@cache
def source(name, filename):
    spec = spec_from_file_location(name, ROOT / filename)
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def runner():
    sys.path.insert(0, str(ROOT / "scripts"))
    import longrun
    return longrun


def vertex_ids(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def bit_mask(points):
    return sum(1 << p for p in points)


def starting_stars(sizes, links):
    out = [[] for _ in sizes]
    for i, (a, b) in enumerate(links):
        out[a].append(i)
        out[b].append(i)
    fresh = len(links)
    for p, size in enumerate(sizes):
        spare = size - len(out[p])
        if spare < 0:
            raise ValueError("A start has too many meetings for its listed places")
        out[p].extend(range(fresh, fresh + spare))
        fresh += spare
    return out


def starting_roster(sizes, links):
    checker = source("partner_archived_checker", "experiments/GROWN-END-SWAP-20261119-001/"
                     "GROWN-END-SWAP-20261119-001-E001_reached/verify.py")
    start = checker.Arrangement.parse(starting_stars(sizes, links))
    gate = checker.start_audit(start)
    live = {u: i for i, u in enumerate(sorted(start.live))}
    opens = Counter(start.loose.values())
    blocks = [[live[u] for u in adjacent if u in live] for adjacent in start.neighbors]
    roster = Roster(tuple(opens[u] for u in live), tuple(bit_mask(b) for b in blocks))
    return roster, gate


@dataclass(frozen=True)
class Roster:
    opens: tuple
    blocks: tuple

    @property
    def points(self):
        return len(self.opens)

    @property
    def candidates(self):
        rows = [0] * self.points
        for block in set(self.blocks):
            for p in vertex_ids(block):
                rows[p] |= block
        return tuple(neighbors & ~(1 << p) for p, neighbors in enumerate(rows))


class ScreenLimit(Exception):
    pass


@dataclass(frozen=True)
class GroupPlan:
    demand: tuple
    count: int
    groups: tuple | None


def groups_at(roster, candidates):
    """List exact groups under the admitted complete-round roster law."""
    n = roster.points
    candidate_pairs = sum(row.bit_count() for row in candidates) // 2
    if not candidate_pairs:
        return GroupPlan((0,) * n, 0, ())
    full = (1 << n) - 1
    held = set(roster.blocks)
    if candidate_pairs == n * (n - 1) // 2:
        if full not in held and n >= 3:
            return GroupPlan((1,) * n, 1, (full,))
        if candidate_pairs > CLIQUE_LIMIT:
            # The exact profile suffices for the preceding birth's open counts.
            return GroupPlan((n - 1,) * n, candidate_pairs, None)
        return GroupPlan((n - 1,) * n, candidate_pairs,
                         tuple((1 << a) | (1 << b) for a, b in combinations(range(n), 2)))
    if candidate_pairs > PAIR_LIMIT:
        raise ScreenLimit("candidate_pair_limit")

    graph = nx.Graph()
    graph.add_nodes_from(range(n))
    for a, row in enumerate(candidates):
        graph.add_edges_from((a, b) for b in vertex_ids(row >> (a + 1) << (a + 1)))
    groups = []
    covered = [0] * n
    demand = [0] * n
    for i, clique in enumerate(nx.find_cliques(graph), 1):
        if i > CLIQUE_LIMIT:
            raise ScreenLimit("maximal_candidate_sets_limit")
        if len(clique) < 3:
            continue
        group = bit_mask(clique)
        if group in held:
            continue
        groups.append(group)
        for p in clique:
            covered[p] |= group
            demand[p] += 1
    for a, row in enumerate(candidates):
        remaining = (row & ~covered[a]) >> (a + 1) << (a + 1)
        if len(groups) + remaining.bit_count() > CLIQUE_LIMIT:
            raise ScreenLimit("listed_groups_limit")
        for b in vertex_ids(remaining):
            groups.append((1 << a) | (1 << b))
            demand[a] += 1
            demand[b] += 1
    return GroupPlan(tuple(demand), len(groups), tuple(sorted(groups)))


def births(roster, plan):
    """Return the next literal parentsets or a certified refusal before expansion."""
    if not roster.points:
        return "closed", None
    if any(supply < demand for supply, demand in zip(roster.opens, plan.demand, strict=True)):
        return "stall", None
    spare = [supply - demand for supply, demand in zip(roster.opens, plan.demand, strict=True)]
    count = plan.count + sum(spare)
    if count > POINT_LIMIT:
        return "birth_point_limit", count
    if plan.groups is None:
        return "listed_groups_limit", count
    parents = list(plan.groups)
    for u, k in enumerate(spare):
        parents.extend([1 << u] * k)
    assert len(parents) == count and count > 0
    return None, parents


def next_blocks(parents, former_count):
    blocks = [0] * former_count
    for child, group in enumerate(parents):
        for u in vertex_ids(group):
            blocks[u] |= 1 << child
    return tuple(blocks)


def complement_pairs(roster, pairing, candidates, demand):
    """Exact held and free word counts for this named partnered set."""
    order = len(pairing)
    chosen = bit_mask(p for pair in pairing for p in pair)
    word_mask = (1 << order) - 1
    held = set()
    for block in set(roster.blocks):
        meeting = block & chosen
        if meeting.bit_count() == order:
            # A block cannot hold two noncandidates, so it holds one per pair.
            held.add(bit_mask(i for i, (_, right) in enumerate(pairing) if (meeting >> right) & 1))
    both_held = sorted(word for word in held if word < (word ^ word_mask) and (word ^ word_mask) in held)
    blocked_pairs = {min(word, word ^ word_mask) for word in held}
    free_pairs = (1 << (order - 1)) - len(blocked_pairs)
    example = None
    if free_pairs:
        word = next(w for w in range(len(blocked_pairs) + 1) if w not in blocked_pairs)
        example = [[pair[(w >> i) & 1] for i, pair in enumerate(pairing)] for w in (word, word ^ word_mask)]
    common = ((1 << roster.points) - 1) ^ chosen
    for p in vertex_ids(chosen):
        common &= candidates[p]
    supply = [[p, roster.opens[p], demand[p]] for p in vertex_ids(chosen)]
    return {"order": order, "pairing": pairing, "outside_common_candidates": list(vertex_ids(common)),
            "held_transversals": len(held), "held_complement_pairs": len(both_held),
            "held_complement_pair_words": both_held, "held_complement_closed": 2 * len(both_held) == len(held),
            "free_complement_pairs": free_pairs, "free_example": example,
            "open_supply_and_group_demand": supply}


def partner_pairs(candidates):
    n = len(candidates)
    if n < 6 or n % 2 or any(neighbors.bit_count() != n - 2 for neighbors in candidates):
        return None
    full = (1 << n) - 1
    pairing = []
    for u, row in enumerate(candidates):
        other = full ^ row ^ (1 << u)
        v = other.bit_length() - 1
        if u < v:
            pairing.append((u, v))
    assert len(pairing) * 2 == n
    return pairing


def complete_partnered(roster, candidates, plan):
    pairing = partner_pairs(candidates)
    if pairing is None:
        return None
    report = complement_pairs(roster, pairing, candidates, plan.demand)
    order, held = report["order"], report["held_transversals"]
    consumes_exactly = roster.opens == plan.demand
    just_transversals = plan.count == (1 << order) - held
    distinct_blocks = sorted({b for b in roster.blocks if b.bit_count() >= 2}, key=lambda b: (-b.bit_count(), b))
    maximal = []
    for b in distinct_blocks:
        if not any(b & large == b for large in maximal):
            maximal.append(b)
    free_law = held == 0 and consumes_exactly and just_transversals
    canonical_free = free_law and all(b.bit_count() == 2 for b in maximal)
    canonical_later = (held != 0 and report["held_complement_closed"] and consumes_exactly and just_transversals
                       and all(b.bit_count() == order for b in maximal)
                       and 3 <= held // 2 < order)
    return {**report, "free_law": free_law, "canonical_free": canonical_free,
            "canonical_later": canonical_later, "exact_open_supply": consumes_exactly,
            "only_transversal_groups": just_transversals,
            "block_sizes": sorted(Counter(b.bit_count() for b in maximal).items())}


def induced_example(roster, candidates, demand):
    """Deterministic greedy examples. Only the returned witness is graded."""
    full = (1 << roster.points) - 1
    best = None
    for minimize_degree in (True, False):
        remaining = full
        pairs = []
        while remaining.bit_count() > 1:
            possible = [(u, remaining & ~(candidates[u] | (1 << u))) for u in vertex_ids(remaining)]
            possible = [(u, others) for u, others in possible if others]
            if not possible:
                break
            u, others = min(possible, key=lambda row: ((1 if minimize_degree else -1) * row[1].bit_count(), row[0]))
            v = min(vertex_ids(others), key=lambda w: (-(remaining & candidates[u] & candidates[w]).bit_count(), w))
            pairs.append(tuple(sorted((u, v))))
            remaining &= candidates[u] & candidates[v]
        if len(pairs) < 3:
            continue
        report = complement_pairs(roster, sorted(pairs), candidates, demand)
        assert report["outside_common_candidates"] == list(vertex_ids(remaining))
        key = (not remaining, report["free_complement_pairs"], len(pairs))
        if best is None or key > best[0]:
            best = key, report
    return best and best[1]


def check_first_literal(sizes, links, parents=None, opens=None, stop=None):
    """Compare the first reached roster to the separate literal growth engine."""
    law = source("partner_literal_law", "experiments/FIRST-KNOT-20261118-001B/"
                 "FIRST-KNOT-20261118-001B-E001_two_knots/startlib.py")
    physical = law.from_junctions(starting_stars(sizes, links))
    live = {holder: i for i, holder in enumerate(u for u in range(len(sizes)) if physical.loose(u))}
    result = physical.step(law.gf2(law.F.fewest), None)
    if stop == "closed_start":
        assert result == {"new": 0}
        return
    if stop == "stall":
        assert result is None
        return
    assert result["new"] == len(parents) and not physical.implied_mismatch
    literal = Counter()
    for child in range(len(sizes), len(physical.bits_of)):
        taken = physical.bits_of[child][:physical.parents[child]]
        keep = bit_mask(live[physical.owner[b][0]] for b in taken)
        literal[keep, physical.fresh[child]] += 1
    assert literal == Counter(zip(parents, opens, strict=True))


def screen(sizes, links, ages, *, archived_counts=(), induced=False, literal_first=False):
    roster, gate = starting_roster(sizes, links)
    canonical = not gate["non_outside_cut_holders"] and not gate["forced_distinctions"]
    if not roster.points:
        if literal_first:
            check_first_literal(sizes, links, stop="closed_start")
        return canonical, "closed_start", [], None
    table = []
    candidates = roster.candidates
    plan = groups_at(roster, candidates)
    total, width = len(sizes), sum(sizes) - len(links)
    for age in range(1, ages + 1):
        reason, parents = births(roster, plan)
        if reason:
            if age == 1 and literal_first and reason == "stall":
                check_first_literal(sizes, links, stop="stall")
            return canonical, reason, table, parents
        points = len(parents)
        if age < len(archived_counts):
            assert points == archived_counts[age], (age, points, archived_counts)
        blocks = next_blocks(parents, roster.points)
        projected = Roster((0,) * points, blocks)
        following = projected.candidates
        try:
            following_plan = groups_at(projected, following)
        except ScreenLimit as exc:
            return canonical, str(exc), table, {"births": points, "age": age, "J": total + points,
                                               "n_lower": width + (points if points > 1 else 0),
                                               "complete_candidate_graph": partner_pairs(following) is not None}
        implied = points == 1
        opens = tuple(d if implied else max(d, 3 - parents[p].bit_count(), 1)
                      for p, d in enumerate(following_plan.demand))
        if age == 1 and literal_first:
            check_first_literal(sizes, links, parents, opens)
        total += points
        width += sum(opens)
        if implied:
            assert opens == (0,)
            table.append({"age": age, "births": 1, "J": total, "n": width, "live": 0})
            return canonical, "closed", table, None
        roster = Roster(opens, blocks)
        complete = complete_partnered(roster, following, following_plan)
        row = {"age": age, "births": points, "J": total, "n": width, "live": points}
        if complete:
            row["complete_partnered"] = complete
        if induced and not complete:
            candidate = induced_example(roster, following, following_plan.demand)
            if candidate:
                row["induced_example"] = candidate
        table.append(row)
        candidates, plan = following, following_plan
    return canonical, "horizon", table, None


@cache
def archives():
    read = runner().load_results
    for path in (TOUCH_RUN, EXPLOSIVE_RUN):
        if not (path / "results.jsonl").is_file():
            raise FileNotFoundError(f"Required closed archive is unavailable: {path / 'results.jsonl'}")
    touching = read(TOUCH_RUN)
    exploded = read(EXPLOSIVE_RUN)
    assert touching and exploded and all(r["status"] == "ok" for r in (*touching.values(), *exploded.values()))
    touch = sorted((a for row in touching.values() for a in row["result"]["arrangements"]), key=lambda a: a["key"])
    boom = [{"source_case": name, "source_draw": i, **a} for name, row in sorted(exploded.items())
            if name.startswith("cap-7-") for i, a in enumerate(row["result"]["starts"])
            if a["measured"] == "explosive"]
    boom.sort(key=lambda a: (a["n"], sum(a["sizes"]), a["sizes"], a["edges"], a["source_case"], a["source_draw"]))
    assert len(touch) == 26441 == len({str(x["key"]) for x in touch})
    assert sum(a["labelled"] for a in touch) == 2626697
    assert len(boom) == 16 and all(max(a["sizes"]) == 7 for a in boom)
    return touch, boom


def setup(_params):
    archives()


def cases():
    touch, boom = archives()
    for i in range(0, len(touch), SHARD_SIZE):
        yield f"touch-{i // SHARD_SIZE:03d}", ["touch", i]
    for i in range(len(boom)):
        yield f"explosive-{i:02d}", ["explosive", i]


def touch_case(a, index):
    sizes, multiplicities = a["key"]
    links = [pair for pair, count in zip(combinations(range(len(sizes)), 2), multiplicities, strict=True)
             for _ in range(count)]
    canonical, outcome, stages, omitted = screen(sizes, links, TOUCH_AGES, literal_first=True)
    if not stages:
        assert (outcome == "stall" and a["stall_round"] == 1) or outcome == "closed_start", index
    for row in stages:
        age = row["age"]
        tail_age = a["rounds"] - len(a["last"]) + 1
        if tail_age <= age <= a["rounds"]:
            assert row["births"] == a["last"][age - tail_age], index
    if outcome in ("closed", "closed_start"):
        assert a["outcome"] == "closed" and a["rounds"] == len(stages), index
    return {"source_index": index, "canonical": canonical, "labelled": a["labelled"],
            "outcome": outcome, "stages": stages, "omitted": omitted}


def score_one(family, index):
    touch, boom = archives()
    if family == "touch":
        return touch_case(touch[index], index)
    a = boom[index]
    sizes, links = a["sizes"], a["edges"]
    canonical, outcome, stages, omitted = screen(sizes, links, EXPLOSIVE_AGES, archived_counts=a["counts"],
                                                induced=True, literal_first=True)
    return {"tag": f"start-{index:02d}", "source_case": a["source_case"], "source_draw": a["source_draw"],
            "sizes": sizes, "links": links, "canonical": canonical,
            "outcome": outcome, "stages": stages, "omitted": omitted,
            "archived_birth_counts": a["counts"], "archived_outcome": a["outcome"]}


def touch_summary(rows):
    start = Counter()
    ages = defaultdict(Counter)
    matches = []
    for a in rows:
        weight = a["labelled"]
        start["starts"] += 1
        start["labelled"] += weight
        start["canonical"] += a["canonical"]
        start["canonical_labelled"] += weight * a["canonical"]
        start[a["outcome"]] += 1
        if a["canonical"]:
            start["canonical_" + a["outcome"]] += 1
        for row in a["stages"]:
            p = ages[row["age"]]
            p["reached"] += 1
            p["labelled"] += weight
            p["canonical"] += a["canonical"]
            p["canonical_labelled"] += weight * a["canonical"]
            p["closed"] += row["live"] == 0
            if "complete_partnered" in row:
                p["complete_candidate"] += 1
                matches.append({**row, "source_index": a["source_index"], "canonical": a["canonical"], "labelled": weight})
    return {"starts": start, "ages": ages, "matches": matches}


def run(_case_id, payload):
    family, i = payload
    if family == "explosive":
        return score_one(family, i)
    count = len(archives()[0])
    return touch_summary(score_one(family, k) for k in range(i, min(i + SHARD_SIZE, count)))


def controls():
    wall = source("partner_wall_job", "proofs/WALL-READ-20261119-001A/"
                  "WALL-READ-20261119-001A-P001_partnered/job.py")
    opn, blocks = wall.partnered(3)
    sizes, links = wall.hub_start(opn, blocks)
    roster, gate = starting_roster(sizes, links)
    assert gate["census_open_legal"] and max(sizes) == 8
    free = complete_partnered(roster, roster.candidates, groups_at(roster, roster.candidates))
    assert free["canonical_free"] and free["held_transversals"] == 0 and free["free_complement_pairs"] == 4
    for shift in (-1, 1):
        different = Roster(tuple(x + shift for x in roster.opens), roster.blocks)
        rejected = complete_partnered(different, roster.candidates, groups_at(different, roster.candidates))
        assert not rejected["free_law"] and not rejected["exact_open_supply"]

    canonical, _, continuation, _ = screen(sizes, links, 3, archived_counts=(30, 8, 10, 24))
    assert canonical
    assert [r["births"] for r in continuation] == [8, 10, 24]
    assert all(r["complete_partnered"]["canonical_later"] for r in continuation)
    canonical, end, binomial, _ = screen([4], [], 5, archived_counts=(1, 4, 6, 4, 1))
    assert canonical and end == "closed"
    held = binomial[1]["complete_partnered"]
    assert held["order"] == 3 and held["held_transversals"] == 4 and held["held_complement_pairs"] == 0
    assert held["free_complement_pairs"] == 0 and not held["free_law"] and not held["canonical_later"]

    law = source("partner_literal_law", "experiments/FIRST-KNOT-20261118-001B/"
                 "FIRST-KNOT-20261118-001B-E001_two_knots/startlib.py")
    for start, meetings, expected in ((sizes, links, continuation), ([4], [], binomial)):
        physical = law.from_junctions(starting_stars(start, meetings))
        for r in expected:
            assert physical.step(law.gf2(law.F.fewest), None)["new"] == r["births"]
            assert len(physical.bits_of) == r["J"] and physical.nbits == r["n"]
            assert len(physical.live) == r["live"] and not physical.implied_mismatch
    return {"wall_read_order_three_start": free, "wall_read_post_start": continuation,
            "finite_binomial_six": binomial[1], "blocked_and_excess_open_controls": True,
            "independent_literal_growth": True}


def archive_tail(case, history):
    """Reject full partnering from necessary scalar counts where blocks are unavailable."""
    counts = history["counts"]
    base_counts = case["archived_birth_counts"][1:]
    assert base_counts == counts[:len(base_counts)]
    checked = {stage["age"]: stage["births"] for stage in case["stages"]}
    pending = case["omitted"]
    if isinstance(pending, dict) and not pending["complete_candidate_graph"]:
        checked[pending["age"]] = pending["births"]
    elif isinstance(pending, int):
        assert pending == counts[len(checked)]
    assert all(counts[age - 1] == n for age, n in checked.items())
    assert set(history["stages"]) == {str(age) for age in range(len(counts) + 1)}
    next_groups = {row["t"]: row["groups_next"] for row in history["checks"]}
    results = []
    for age, n in enumerate(counts, 1):
        stage = history["stages"][str(age)]
        assert stage["points"] == n
        if age in checked:
            continue
        largest = history["largest_block"][age - 1]
        candidate_pairs = stage.get("edges")
        if n < 6 or n % 2:
            why = {"method": "live_count"}
        elif largest > n // 2:
            why = {"method": "block_exceeds_partnered_clique_size", "largest_block": largest}
        elif candidate_pairs is not None and candidate_pairs != n * (n - 2) // 2:
            why = {"method": "candidate_pair_count", "candidate_pairs": candidate_pairs}
        elif age - 1 in next_groups and next_groups[age - 1] < n and largest < n - 1:
            why = {"method": "offshoot_degree", "offshoots": n - next_groups[age - 1],
                   "candidate_degree_at_most": largest - 1}
        elif age - 1 in history["one_block_rounds"]:
            parents = counts[age - 2]
            exact_pairs = parents * (parents - 1) // 2
            if n == exact_pairs == next_groups.get(age - 1) and 2 * (parents - 2) != n - 2:
                why = {"method": "all_pairs_of_one_block", "previous_live": parents,
                       "candidate_degree": 2 * (parents - 2)}
            else:
                why = {"method": "unavailable"}
        else:
            why = {"method": "unavailable"}
        results.append({"age": age, "births": n, **why})
    return results


def collect(run_dir, output):
    records = runner().load_results(run_dir)
    roster = list(cases())
    assert set(records) == {case_id for case_id, _ in roster}
    assert all(r["status"] == "ok" for r in records.values())
    starts, ages, touch_matches, boom = Counter(), defaultdict(Counter), [], []
    for case_id, (family, _) in roster:
        data = records[case_id]["result"]
        if family == "explosive":
            boom.append(data)
            continue
        starts.update(data["starts"])
        for age, tallies in data["ages"].items():
            ages[int(age)].update(tallies)
        touch_matches.extend(data["matches"])
    assert starts["starts"] == 26441 and len(boom) == 16
    assert starts["labelled"] == 2626697
    assert ages[1]["reached"] + starts["stall"] + starts["closed_start"] == starts["starts"]
    assert all(a["omitted"] is None or a["outcome"].endswith("_limit") for a in boom)

    wall = json.loads(WALL_SUMMARY.read_text())["follow"]
    merge = runner().load_results(MERGE_RUN)
    assert set(wall) == set(merge) == {a["tag"] for a in boom}
    outcomes = Counter(a["outcome"] for a in boom)
    variants = Counter(archived_unresolved=0)
    for a in boom:
        tag = a["tag"]
        assert merge[tag]["status"] == "ok"
        stored_start = merge[tag]["result"]["start"]
        assert stored_start["sizes"] == a["sizes"] and stored_start["edges"] == a["links"]
        a["stored_archive_remainder"] = archive_tail(a, wall[tag])
        variants["canonical_starts"] += a["canonical"]
        variants["full_stages"] += len(a["stages"])
        variants["canonical_full_stages"] += len(a["stages"]) * a["canonical"]
        variants["projected_rejections"] += (isinstance(a["omitted"], dict)
                                             and not a["omitted"]["complete_candidate_graph"])
        variants["archived_stages"] += len(wall[tag]["counts"])
        variants["canonical_archived_stages"] += len(wall[tag]["counts"]) * a["canonical"]
        for row in a["stored_archive_remainder"]:
            variants["archived_unresolved" if row["method"] == "unavailable" else "aggregate_rejections"] += 1
        for row in a["stages"]:
            variants["complete_candidates"] += "complete_partnered" in row
            if info := row.get("induced_example"):
                variants["named_induced_stages"] += 1
                variants["induced_no_outside_common"] += not info["outside_common_candidates"]
                variants["induced_no_outside_common_with_free_pair"] += (not info["outside_common_candidates"]
                                                                          and info["free_complement_pairs"] > 0)
    touch_variants = Counter()
    for row in touch_matches:
        info = row["complete_partnered"]
        touch_variants["canonical_complete_candidates"] += row["canonical"]
        touch_variants["complete_candidate_labelled"] += row["labelled"]
        touch_variants["canonical_complete_candidate_labelled"] += row["labelled"] * row["canonical"]
        for field in ("free_law", "canonical_free", "canonical_later"):
            touch_variants[field] += info[field]
        touch_variants["with_free_complement_pair"] += info["free_complement_pairs"] > 0
    assert variants["archived_stages"] == (variants["full_stages"] + variants["projected_rejections"]
                                           + variants["aggregate_rejections"] + variants["archived_unresolved"])
    paths = (TOUCH_RUN / "results.jsonl", EXPLOSIVE_RUN / "results.jsonl", MERGE_RUN / "results.jsonl", WALL_SUMMARY)
    payload = {"inputs": {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in paths},
               "limits": {"touch_ages": TOUCH_AGES, "explosive_ages": EXPLOSIVE_AGES, "points": POINT_LIMIT,
                          "candidate_pairs": PAIR_LIMIT, "listed_groups_and_cliques": CLIQUE_LIMIT},
               "touch": {"starts": starts, "by_age": ages, "checks": touch_variants,
                         "complete_candidate_rows": touch_matches},
               "explosive": {"outcomes": outcomes, "checks": variants, "starts": boom}, "controls": controls(),
               "literal_first_round_checks": starts["starts"] + len(boom)}
    output.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(mode="w", encoding="ascii", prefix="archive_screen_pending_",
                            dir=output.parent, delete=False) as stream:
        json.dump(payload, stream, indent=2, sort_keys=True)
        stream.write("\n")
    Path(stream.name).replace(output)
    return {"touch_starts": starts, "touch_by_age": ages, "touch_candidate_rows": len(touch_matches),
            "touch_checks": touch_variants,
            "explosive_outcomes": outcomes, "explosive_checks": variants}


def main():
    parser = ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("controls")
    one = sub.add_parser("one")
    one.add_argument("family", choices=("touch", "explosive"))
    one.add_argument("index", type=int)
    merge = sub.add_parser("collect")
    merge.add_argument("run_dir", type=Path)
    merge.add_argument("--output", type=Path, default=ARTIFACTS / "archive_screen.json")
    args = parser.parse_args()
    if args.command == "controls":
        result = controls()
    elif args.command == "one":
        result = score_one(args.family, args.index)
    else:
        result = collect(args.run_dir, args.output)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
