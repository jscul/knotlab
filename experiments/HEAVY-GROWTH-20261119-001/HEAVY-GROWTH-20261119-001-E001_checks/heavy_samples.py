"""Replay two literal heavy-body erasures without enumerating the unread rounds."""

from argparse import ArgumentParser
from base64 import b64decode
from collections import Counter, defaultdict, deque
from functools import cached_property
import gzip
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import sys
from zlib import decompress


ROOT = Path(__file__).resolve().parents[3]
HUB = "HUB-GUIDED-SAMPLE-20261119-001"
HUB_FAMILY = HUB + "-E001_sampler"
HUB_ARTIFACTS = ROOT / "artifacts" / HUB / HUB_FAMILY
GIANT = (
    ROOT / "artifacts/GROWTH-CONTINUES-20261119-001"
    / "GROWTH-CONTINUES-20261119-001-E001_checks/witness_checks.json"
)
MARKED_PAIRS = tuple(combinations(range(4), 2))
MARKED_TRIPLES = tuple(combinations(range(4), 3))


def names(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def packed(vertices):
    return sum(1 << v for v in vertices)


def sha(path):
    with path.open("rb") as stream:
        digest = sha256()
        while block := stream.read(1 << 20):
            digest.update(block)
        return digest.hexdigest()


class Frame:
    def __init__(self, parents, degrees=None):
        self.parents = tuple(map(tuple, parents))
        self.n = len(parents)
        self.blocks = defaultdict(list)
        for v, row in enumerate(self.parents):
            assert row and tuple(sorted(set(row))) == row
            for p in row:
                self.blocks[p].append(v)
        self.degrees = degrees

    def neighbors(self, v):
        return {w for p in self.parents[v] for w in self.blocks[p]} - {v}

    def distances(self, source, erase=()):
        distance = {source: 0}
        queue = deque([source])
        expanded = set()
        while queue:
            v = queue.popleft()
            for p in self.parents[v]:
                if p in expanded:
                    continue
                expanded.add(p)
                for w in self.blocks[p]:
                    if w not in distance and w not in erase:
                        distance[w] = distance[v] + 1
                        queue.append(w)
        return distance

    @cached_property
    def mark(self):
        tip, = (v for v, row in enumerate(self.parents) if len(row) == 1)
        sibling, = self.neighbors(tip)
        common, = self.parents[tip]
        siblings = sorted(self.neighbors(sibling) - {tip})
        assert len(self.parents[sibling]) == 2
        assert len(siblings) == 4
        held, = set(self.parents[sibling]) - {common}
        assert set(self.blocks[held]) == {sibling, *siblings}
        assert set(self.blocks[common]) == {tip, sibling}
        return tip, sibling, siblings

    def profiles(self, siblings):
        membership = defaultdict(list)
        excluded = set(siblings) | set(self.mark[:2])
        for i, v in enumerate(siblings):
            assert len(self.parents[v]) == 2
            for w in self.neighbors(v) - excluded:
                membership[w].append(i)
        profiles = defaultdict(list)
        for v in sorted(membership):
            profiles[tuple(membership[v])].append(v)
        assert {p for p in profiles if len(p) > 1} == set(MARKED_PAIRS)
        assert all(len(profiles[p]) == 1 for p in MARKED_PAIRS)
        return dict(sorted(profiles.items()))


def load_frame(folder, record):
    files = record["files"]
    for file in files.values():
        assert sha(folder / file["name"]) == file["sha256"], file["name"]
    with gzip.open(folder / files["parents"]["name"], "rt") as stream:
        parents = json.load(stream)
    with gzip.open(folder / files["degrees"]["name"], "rt") as stream:
        degrees = json.load(stream)
    frame = Frame(parents, degrees)
    assert frame.n == record["live"] == len(degrees)
    return frame


def earlier_frames(tag):
    sys.path.insert(0, str(ROOT / "experiments" / HUB / HUB_FAMILY))
    from stages import archive_replay

    frames = {}

    def save(age, frame):
        frames[age] = Frame([tuple(names(mask)) for mask in frame.parent_masks])

    archive_replay(tag, range(2, 7), save)
    return frames


def pendant_paths(frame, removed):
    degrees = list(frame.degrees)
    for r in removed:
        for v in frame.neighbors(r) - removed:
            degrees[v] -= 1
    histogram = Counter(d for v, d in enumerate(degrees) if v not in removed)
    paths = []
    for v, d in enumerate(degrees):
        if v in removed or d != 1:
            continue
        path = [v]
        while len(path) == 1 or degrees[path[-1]] == 2:
            previous = set(path[-2:-1])
            w, = frame.neighbors(path[-1]) - removed - previous
            assert w not in path
            path.append(w)
        paths.append(path)
    unique_k = next(k for k in sorted(histogram) if histogram[k] == 1)
    unique_v, = (v for v, d in enumerate(degrees) if d == unique_k and v not in removed)
    return {"pendant_paths": paths, "isolates": histogram[0],
            "unique_degree_certificate": [unique_v, unique_k]}


def frame_report(frame, preceding):
    tip, sibling, siblings = frame.mark
    profile = frame.profiles(siblings)
    old_tip, old_sibling, old_siblings = preceding.mark
    assert frame.parents[tip] == (old_tip,)
    assert set(frame.parents[sibling]) == {old_tip, old_sibling}
    for v, p in zip(siblings, old_siblings, strict=True):
        assert set(frame.parents[v]) == {old_sibling, p}

    # The unique two-index sites intersect exactly when their index pairs intersect.
    pair_sites = {p: profile[p][0] for p in MARKED_PAIRS}
    supports = {p: set(frame.parents[v]) for p, v in pair_sites.items()}
    old_inners = set(old_siblings)
    private = set()
    for (i, j), row in supports.items():
        assert row & old_inners == {old_siblings[i], old_siblings[j]}
        remainder, = row - old_inners
        private.add(remainder)
    assert len(private) == 6
    for a, b in combinations(MARKED_PAIRS, 2):
        assert bool(supports[a] & supports[b]) == bool(set(a) & set(b))
    for triple in MARKED_TRIPLES:
        assert not set.intersection(*(supports[p] for p in combinations(triple, 2)))

    distance = frame.distances(tip)
    assert len(distance) == frame.n
    assert {v for v, d in distance.items() if d == 2} == set(siblings)
    assert {v for v, d in distance.items() if d == 3} == set(sum(profile.values(), []))
    report = {
        "live": frame.n,
        "tip": tip,
        "companion": sibling,
        "interface": siblings,
        "parent_rows_at_interface": [frame.parents[v] for v in (tip, sibling, *siblings)],
        "outer_profiles": [[p, vertices] for p, vertices in profile.items()],
        "outer_pair_parent_rows": [[p, frame.parents[v]] for p, v in pair_sites.items()],
        "candidate_step_histogram": dict(sorted(Counter(distance.values()).items())),
        "intact_interface_demand": {
            "tip": 1, "companion": 5,
            "four_pair_children": [4 + len(profile.get((i,), ())) for i in range(4)],
        },
        "intact_tip_supply": 2,
        "held_blocks_changed_by_both_erasures": [[tip, sibling], [sibling, *siblings]],
    }
    if frame.degrees is not None:
        erasures = {"intact": set(), "tip": {tip}, "tip_and_companion": {tip, sibling}}
        report["body"] = {}
        for label, removed in erasures.items():
            assert len(frame.distances(siblings[0], removed)) == frame.n - len(removed)
            report["body"][label] = {
                "live": frame.n - len(removed), "components": 1,
                **pendant_paths(frame, removed),
            }
    return report


def cohort(frame):
    """Identify the 17 junctions from the rooted candidate graph alone."""
    tip, sibling, w = frame.mark
    distance = frame.distances(tip)
    profile = frame.profiles(w)
    pair_sites = {ij: profile[ij][0] for ij in MARKED_PAIRS}
    triple_sites = {}
    for triple in MARKED_TRIPLES:
        common = set.intersection(*(frame.neighbors(pair_sites[ij])
                                    for ij in combinations(triple, 2)))
        triple_sites[triple], = (v for v in common if distance[v] == 4)
    common = set.intersection(*(frame.neighbors(v) for v in triple_sites.values()))
    last, = (v for v in common if distance[v] == 5)
    cohort = [tip, sibling, *w, *pair_sites.values(), *triple_sites.values(), last]
    assert len(set(cohort)) == 17
    return pair_sites, triple_sites, last, cohort


def cohort_transitions(frames):
    history = {age: cohort(frames[age]) for age in (6, 7, 8)}
    report = []
    for age in (7, 8):
        old = frames[age - 1]
        new = frames[age]
        old_p, old_h, old_k, members = history[age - 1]
        new_p, new_h, new_k, _ = history[age]
        for (i, j), v in new_p.items():
            assert set(new.parents[v]) == {old.mark[2][i], old.mark[2][j], old_p[i, j]}
        for triple, v in new_h.items():
            assert set(new.parents[v]) == {old_h[triple], *(old_p[ij] for ij in combinations(triple, 2))}
        assert set(new.parents[new_k]) == {old_k, *old_h.values()}
        assert all(set(new.parents[v]) <= set(members) for v in history[age][-1])
        report.append({"age": age, "triple_sites": list(new_h.values()), "last_site": new_k,
                       "parent_rows_by_cohort_label": [
                           [v, new.parents[v]] for v in history[age][-1]],
                       "old_cohort": members})
    return report


def detached_cohort(frame):
    _, _, _, vertices = cohort(frame)
    isolated = Frame([frame.parents[v] for v in vertices[2:]])
    counts = [isolated.n]
    while isolated.n > 1:
        following, total, _ = direct_births(isolated)
        assert following.n < isolated.n
        counts.append(following.n)
        if following.n == 1:
            assert total == isolated.n and following.parents == (tuple(range(isolated.n)),)
        isolated = following
    assert counts == [15, 11, 5, 1]
    return {"first_generation_is_an_induced_restriction": True, "counts": counts,
            "last_birth_consumes_all_loose_distinctions": True}


def maximal_cliques(graph, ps, xs=0, chosen=0):
    if not (ps or xs):
        yield chosen
        return
    pivot = max(names(ps | xs), key=lambda v: (graph[v] & ps).bit_count())
    for v in names(ps & ~graph[pivot]):
        bit = 1 << v
        yield from maximal_cliques(graph, ps & graph[v], xs & graph[v], chosen | bit)
        ps ^= bit
        xs |= bit


def direct_births(frame, removed=(), original_supply=None):
    """Independent finite clique and loose-count replay on the small controls."""
    survivors = set(range(frame.n)) - set(removed)
    graph = [packed(frame.neighbors(v) & survivors) for v in range(frame.n)]
    groups = []
    used_pairs = [0] * frame.n
    for mask in maximal_cliques(graph, packed(survivors)):
        if mask.bit_count() < 3:
            continue
        row = tuple(names(mask))
        if set.intersection(*(set(frame.parents[v]) for v in row)):
            continue
        groups.append(row)
        for v in row:
            used_pairs[v] |= mask
    for v in sorted(survivors):
        uncovered = graph[v] & ~used_pairs[v] & ~((1 << (v + 1)) - 1)
        groups.extend((v, w) for w in names(uncovered))
    demand = Counter(v for row in groups for v in row)
    supply = {
        v: max(demand[v], 3 - len(frame.parents[v]), 1) if original_supply is None
        else original_supply[v]
        for v in survivors
    }
    for v in sorted(survivors):
        assert supply[v] >= demand[v]
        groups.extend([(v,)] * (supply[v] - demand[v]))
    return Frame(sorted(groups)), sum(supply.values()), supply


def arity_counts(frame):
    return [
        sum(len(row) >= 3 for row in frame.parents),
        sum(len(row) == 2 for row in frame.parents),
        sum(len(row) == 1 for row in frame.parents),
    ]


def differences(singletons):
    return {
        "tip_retuned": [[0, -1, -1], [0, -5, -1], [-6, -5 - singletons, -1]],
        "both_retuned": [[0, -5, -1], [-6, -5 - singletons, -1]],
        "tip_keep_opens": [[0, -1, 0], [0, -1, -1]],
        "both_keep_opens": [[0, -5, 3], [-6, 7, -1]],
    }


def match_births(edited, intact, parent_map):
    by_row = {row: v for v, row in enumerate(intact.parents)}
    assert len(by_row) == intact.n
    matches = {}
    for v, row in enumerate(edited.parents):
        if all(p in parent_map for p in row):
            key = tuple(sorted(parent_map[p] for p in row))
            if key in by_row:
                matches[v] = by_row[key]
    return matches


def direct_controls(frame):
    tip, sibling, w = frame.mark
    profile = frame.profiles(w)
    singles = sum(len(v) for p, v in profile.items() if len(p) == 1)
    expected = differences(singles)
    full1, _, supply = direct_births(frame)
    full2, _, _ = direct_births(full1)
    full3, _, _ = direct_births(full2)
    full_frames = [full1, full2, full3]
    base = [arity_counts(f) for f in full_frames]
    ending = cohort(full3)[2]
    out = {"live": frame.n, "full_birth_breakdowns": base, "erased_birth_breakdowns": {},
           "matched_five_parent_birth_in_third_generation": {}}
    for label, steps in expected.items():
        drop = {tip, sibling} if label.startswith("both") else {tip}
        budget = supply if label.endswith("keep_opens") else None
        first, _, _ = direct_births(frame, drop, budget)
        second, _, _ = direct_births(first)
        third, _, _ = direct_births(second)
        frames = [first, second, third]
        observed = [arity_counts(f) for f in frames]
        assert observed[:len(steps)] == [[u + v for u, v in zip(a, b, strict=True)]
                                         for a, b in zip(base, steps)], (label, observed, base, steps)
        image = {v: v for v in range(frame.n) if v not in drop}
        for edited, full in zip(frames, full_frames, strict=True):
            image = match_births(edited, full, image)
        match, = (v for v, full in image.items() if full == ending)
        out["matched_five_parent_birth_in_third_generation"][label] = {
            "edited_birth": match, "intact_birth": ending,
            "intact_parents": full3.parents[ending],
        }
        out["erased_birth_breakdowns"][label] = observed
    return out


def stage_transition(before, after, opens):
    old_distance = before.distances(before.mark[0])
    new_distance = after.distances(after.mark[0])
    born = dict(Counter(v for row in after.parents for v in row))
    assert opens == [born[v] for v in range(before.n)]
    assert all(
        new_distance[v] == 1 + min(old_distance[p] for p in row)
        for v, row in enumerate(after.parents) if v != after.mark[0]
    )
    tip, sibling, w = before.mark
    counts = arity_counts(after)
    assert sum(counts) == after.n
    assert [opens[v] for v in (tip, sibling, *w)] == [
        2, 5, *(4 + len(before.profiles(w).get((i,), ())) for i in range(4)),
    ]
    result = {"intact": counts}
    used = {"intact": sum(opens)}
    for label, steps in differences(sum(len(v) for p, v in before.profiles(w).items()
                                        if len(p) == 1)).items():
        removed = {tip, sibling} if label.startswith("both") else {tip}
        remaining = [row for row in after.parents if not set(row) & removed]
        if label.endswith("keep_opens"):
            remainder = Counter(v for row in remaining for v in row)
            for v in set(range(before.n)) - removed:
                remaining.extend([(v,)] * (opens[v] - remainder[v]))
        recorded = [sum(len(row) >= 3 for row in remaining),
                    sum(len(row) == 2 for row in remaining),
                    sum(len(row) == 1 for row in remaining)]
        assert recorded == [a + b for a, b in zip(counts, steps[0], strict=True)]
        result[label] = recorded
        used[label] = sum(map(len, remaining))
    return {"distance_rows_checked": after.n - 1, "open_sum": sum(opens),
            "birth_breakdowns": result, "open_sum_by_arm": used}


def giant_replay(frame, roster_sha):
    evidence = json.loads(GIANT.read_text())
    assert evidence["age_eight_roster_sha256"] == roster_sha
    evidence = evidence["round_ten_giant"]
    block_masks = {}
    for p, block in frame.blocks.items():
        block_masks[p] = packed(block)
    full = (1 << frame.n) - 1
    allowed = full
    distance = frame.distances(frame.mark[0])
    companion_min = []
    for row in evidence["companions"]:
        raw = decompress(b64decode(row["literal_bitset_zlib_base64"]))
        assert sha256(raw).hexdigest() == row["sha256"]
        group = int.from_bytes(raw, "little")
        assert group.bit_count() == row["parent_count"]
        union_of_hoods = 0
        maximality = full
        for v in names(group):
            neighborhood = 0
            for p in frame.parents[v]:
                neighborhood |= block_masks[p]
            maximality &= neighborhood
            union_of_hoods |= neighborhood
        assert maximality == group and all(group & ~b for b in block_masks.values())
        allowed &= union_of_hoods
        companion_min.append(min(distance[v] for v in names(group)))
    histogram = Counter(distance[v] for v in names(allowed))
    assert min(companion_min) == min(histogram) == 6
    return {"old_site_candidate_step_histogram_after_nine_necessary_meetings": dict(histogram),
            "old_minimum_steps_per_compulsory_support": companion_min,
            "age_ten_distance": 2 + min(histogram),
            "smallest_candidate_step_for_any_age_nine_parent": 1 + min(histogram),
            "parent_count_lower": evidence["parent_count_lower"]}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("folder", nargs="?", type=Path,
                        default=Path("/var/tmp/hub-sample-20261119"))
    args = parser.parse_args()
    manifest = json.loads((HUB_ARTIFACTS / "stages.json").read_text())
    out = {"arity_column_order": ["at_least_three", "two", "one"], "starts": {}}
    # The two unary ends require one shared companion rather than two equal births.
    peers = Frame([(0,), (0,)])
    births, _, _ = direct_births(peers)
    assert births.parents == ((0,), (0, 1), (1,))
    out["overlapping_mark_control"] = {"births": births.parents, "marked_union_size": 3,
                                        "naive_marked_sum": 4}
    for tag in ("start-03", "start-14"):
        records = {r["age"]: r for r in manifest["stages"]
                   if r["case"] == tag and r["age"] in (7, 8)}
        frames = earlier_frames(tag)
        frames.update((age, load_frame(args.folder, record)) for age, record in records.items())
        reports = {age: frame_report(frames[age], frames[age - 1]) for age in (7, 8)}
        with gzip.open(args.folder / records[7]["files"]["opens"]["name"], "rt") as stream:
            opens = json.load(stream)
        profile = frames[8].profiles(frames[8].mark[2])
        singles = sum(len(v) for p, v in profile.items() if len(p) == 1)
        result = {
            "age_two_to_six_interface_sizes": [len(frames[i].mark[2]) for i in range(2, 7)],
            "stages": reports,
            "age_seven_to_eight": stage_transition(frames[7], frames[8], opens),
            "age_six_to_eight_literal_cohort": cohort_transitions(frames),
            "detached_heavy_cohort_from_age_eight": detached_cohort(frames[8]),
            "age_eight_forecast_deltas": differences(singles),
            "age_eight_input_sha256": records[8]["files"]["blocks"]["sha256"],
            "small_erasure_replay_from_age_four": direct_controls(frames[4]),
        }
        if tag == "start-03":
            result["age_ten_giant"] = giant_replay(frames[8], result["age_eight_input_sha256"])
            known = json.loads((HUB_ARTIFACTS / "literal_residual03.json").read_text())
            residuals = {tuple(row) for row in known["residual_pairs"]}
            tip, sibling, w = frames[8].mark
            assert {r for r in residuals if {tip, sibling} & set(r)} == {
                tuple(sorted((sibling, v))) for v in [tip, *w]
            }
            result["age_nine_exact_residual_pair_counts_after_erasure"] = {
                label: len(residuals) + steps[0][1]
                for label, steps in {"intact": [[0, 0, 0]], **differences(singles)}.items()
            }
            known_floor = json.loads((HUB_ARTIFACTS / "structure_bound.json").read_text())
            assert len(residuals) == known_floor["residual_pairs"]
            result["age_nine_birth_count_lower_by_arm"] = {
                label: known_floor["all_births_lower"] + sum(steps[0])
                for label, steps in {"intact": [[0, 0, 0]], **differences(singles)}.items()
            }
            result["age_nine_restricted_from_intact_deletion_lower"] = {
                "tip_only": known_floor["all_births_lower"] - 1,
                "tip_and_companion": known_floor["all_births_lower"] - 2,
            }
        out["starts"][tag] = result
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
