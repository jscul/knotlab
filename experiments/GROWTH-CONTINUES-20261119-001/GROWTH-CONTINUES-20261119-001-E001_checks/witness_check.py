"""Replay literal round-nine children and certify lower bounds for round ten."""

from argparse import ArgumentParser
from base64 import b64encode
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import sys
from zlib import compress


ROOT = Path(__file__).resolve().parents[3]
HUB = "HUB-GUIDED-SAMPLE-20261119-001"
FAMILY = HUB + "-E001_sampler"
SOURCE = ROOT / "artifacts" / HUB / FAMILY
sys.path.insert(0, str(ROOT / "experiments" / HUB / FAMILY))
from group_profile import Stage, members, pack


COMPANIONS = (
    ((10192, 12056), False),
    ((9578, 21525), False),
    ((8834, 27756), True),
    ((10070, 27756), True),
    ((8464, 27760), True),
    ((10002, 11620), False),
    ((9936, 23184), True),
    ((20323, 2), False),
    ((2, 8824, 18681, 20896, 20902), False),
)

PARTNERS = (
    (((13533, 27760), True), (9797, 21067)),
    (((9936, 23184), True), (9797, 20903)),
    (((10019, 27756), True), (9797, 20923)),
    (((10038, 27756), True), (9797, 21025)),
    (((10035, 27756), True), (9797, 21033)),
    (((9840, 27620), True), (9797, 20713)),
    (((10083, 21553), False), (9797, 18069)),
    (((17841, 2), False), (9797, 21474)),
)

SECTORS = ((35, 0), (13, 4), (3, 31))
GUARD = (7120, 8326, 15714, 10065, 12040, 8626)


def intersection(rows, full):
    for row in rows:
        full &= row
    return full


def complete(stage, neighbors, recipe):
    seeds, descending = recipe
    chosen = pack(seeds, stage.n)
    allowed = intersection((neighbors[v] for v in seeds), stage.full)
    assert chosen & allowed == chosen
    remaining = allowed & ~chosen
    while remaining:
        u = remaining.bit_length() - 1 if descending else next(members(remaining))
        bit = 1 << u
        chosen |= bit
        remaining &= neighbors[u] & ~bit
    assert intersection((neighbors[v] for v in members(chosen)), stage.full) == chosen
    assert chosen.bit_count() >= 3 and all(chosen & ~block for block in stage.blocks)
    return chosen


def two_cover(rows, full):
    """Any cover of size at most two must hit the smallest given support."""
    if not rows:
        return ()
    ordered = sorted(rows, key=int.bit_count)
    for u in members(ordered[0]):
        bit = 1 << u
        other = intersection((row for row in ordered if not row & bit), full)
        if other:
            return u, next(members(other))
    return None


def packed(stage, group):
    raw = group.to_bytes((stage.n + 7) // 8, "little")
    return {"parent_count": group.bit_count(),
            "literal_bitset_zlib_base64": b64encode(compress(raw)).decode("ascii"),
            "sha256": sha256(raw).hexdigest()}


def sector_data(path, stage, neighbors):
    dossier = json.loads((SOURCE / "structure_sectors.json").read_text())
    assert sha256(path.read_bytes()).hexdigest() == dossier["stage_sha256"]
    counted = json.loads((SOURCE / "structure_bound.json").read_text())
    known = {tuple(entry["hubs"]): entry for entry in dossier["rows"]}
    counts = [known[key]["large_global_groups_lower"] for key in SECTORS[:2]]
    assert tuple(counted["projection"]["hubs"]) == SECTORS[2]
    counts.append(counted["projection"]["unheld_lower"])
    core = []
    for a, b in SECTORS:
        joint = stage.blocks[a] | stage.blocks[b]
        core.append(intersection((neighbors[v] for v in members(joint)), joint))
    a, b = SECTORS[2]
    assert core[2] == stage.blocks[a] & stage.blocks[b]
    # The projected third population retains all original shared sites.
    assert sum(counts) == counted["large_groups_lower"]

    checks = []
    for first, second in combinations(range(3), 2):
        a, b = SECTORS[first], SECTORS[second]
        claim, = [c for c in dossier["disjointness_certificates"]
                  if tuple(c["first_hubs"]) == a and tuple(c["second_hubs"]) == b]
        x, y = claim["first_universal_site"], claim["second_universal_site"]
        assert (1 << x) & core[first] and (1 << y) & core[second]
        assert not neighbors[x] & (1 << y)
        shared = core[first] & core[second]
        assert shared
        checks.append({
            "sectors": [a, b], "shared_parent_count": shared.bit_count(),
            "first_shared_parent": next(members(shared)),
            "incompatible_names_certifying_distinct_populations": [x, y],
        })
    return counts, core, checks


def check(roster):
    stage = Stage(roster)
    assert (stage.n, len(stage.blocks)) == (28065, 365)
    neighbors = tuple(stage.hood(sig) | (1 << u) for u, sig in enumerate(stage.at))
    stage.hood.cache_clear()
    counts, core, cross = sector_data(roster, stage, neighbors)
    companions = [complete(stage, neighbors, recipe) for recipe in COMPANIONS]
    assert len(set(companions)) == len(COMPANIONS)
    meetings = [next(members(a & b)) for a, b in combinations(companions, 2)]
    assert two_cover(companions, stage.full) is None
    drops = [two_cover(companions[:i] + companions[i+1:], stage.full) for i in range(len(companions))]
    assert all(drops)
    for group, universal in product(companions, core):
        assert group & universal and universal & ~group

    seed_cover_three = None
    for u in members(intersection(core, stage.full)):
        other = two_cover([group for group in companions if not group & (1 << u)], stage.full)
        if other:
            seed_cover_three = u, *other
            break

    # The attempted protection test only imposed compatibility with the
    # finite guards. These six age-eight names defeat that relaxation.
    guard = pack(GUARD, stage.n)
    assert not guard & core[0] and all(guard & group for group in companions)
    guard_common = intersection((neighbors[u] for u in GUARD), stage.full)
    assert guard & guard_common == guard

    residual_pairs = json.loads((SOURCE / "literal_residual03.json").read_text())
    actual_pairs = {tuple(pair) for pair in residual_pairs["residual_pairs"]}
    assert len(actual_pairs) == residual_pairs["residual_count"] == 1241
    partners = []
    for recipe, residual in PARTNERS:
        assert residual in actual_pairs
        a, b = (1 << residual[0]), (1 << residual[1])
        assert neighbors[residual[0]] & b
        larger, smaller = complete(stage, neighbors, recipe), a | b
        assert not larger & smaller
        partners.append((larger, smaller))
    partner_cross = [next(members(a & b)) for left,right in combinations(partners, 2)
                     for a,b in product(left, right)]
    held_traces = set()
    eligible = intersection((a | b for a,b in partners), stage.full)
    for u in members(eligible):
        held_traces.add(sum(1 << i for i, (_, small) in enumerate(partners) if small & (1 << u)))
    distinct = (1 << len(partners)) - len(held_traces)
    extra = next(((i, j) for i,(large,_) in enumerate(partners)
                  for j,group in enumerate(companions) if not large & group), None)
    assert len(partner_cross) == 112 and distinct == 246 and extra is not None

    lower = sum(counts) + len(companions)
    return {
        "freeze": "1452ab8a5",
        "age_eight_roster_sha256": sha256(roster.read_bytes()).hexdigest(),
        "age_eight_current_live_count": stage.n,
        "round_ten_giant": {
            "parent_count_lower": lower,
            "floor_ratio_to_age_eight_live_count": lower // stage.n,
            "whole_group_block_cover_lower": 3,
            "explicit_three_label_cover_of_certified_subfamily": seed_cover_three,
            "companions": [
                {"seed": recipe[0], "descending": recipe[1], **packed(stage, g),
                 "overlap_with_each_universal_set": [(g & b).bit_count() for b in core]}
                for recipe, g in zip(COMPANIONS, companions, strict=True)
            ],
            "literal_companion_pair_meetings": meetings,
            "two_covers_after_individual_companion_removal": drops,
            "included_populations": [
                {"blocks": blocks, "count_lower": count, "universal_parent_count": u.bit_count()}
                for blocks, count, u in zip(SECTORS, counts, core, strict=True)
            ],
            "cross_population_checks": cross,
        },
        "global_replacement_guard": {
            "relaxed_old_clique_away_from_35_0_universal_set": GUARD,
            "has_literal_parent_in_each_of_the_nine_companions": True,
            "allowed_common_35_0_universal_parents": (guard_common & core[0]).bit_count(),
            "global_replaceable_parent_fraction": None,
        },
        "round_ten_birth_count_lower": {
            "partner_pairs": [
                {"large_seed": recipe[0], "descending": recipe[1],
                 "large_group": packed(stage, larger), "residual_pair": residual}
                for (recipe,residual),(larger,_) in zip(PARTNERS, partners, strict=True)
            ],
            "literal_cross_pair_meetings": partner_cross,
            "transversals": 1 << len(partners),
            "held_trace_masks": sorted(held_traces),
            "unheld_transversals": distinct,
            "all_large_transversal_excluded_from_giant_by_indices": extra,
            "combined_distinct_births_lower": distinct + 1,
        },
    }


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("roster", type=Path, help="literal start-03 age-eight block export")
    args = parser.parse_args()
    print(json.dumps(check(args.roster), indent=2, sort_keys=True))
