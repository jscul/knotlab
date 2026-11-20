"""Independent replay of the persistence obstruction for the old four phases."""

from argparse import ArgumentParser
from collections import defaultdict, deque
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OLD = "MOTION-AT-EDDY-20261119-001"
PHASE_ARTIFACT = ROOT / "artifacts" / OLD / (OLD + "-E001_motion") / "b_updates.json"
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "no_repair_audit.json"
SITES = tuple(range(14))


def position(word, anchor, orientation=1):
    return frozenset(anchor + orientation * bit for bit in word)


def phase_envelopes(phases, fires):
    """Largest coordinate fired up through each next event, relative to its anchor."""
    assert len(phases) == len(fires) == 4
    canonical = set()
    for p, (word, fire) in enumerate(zip(phases, fires, strict=True)):
        following = phases[p + 1] if p < 3 else position(phases[0], 1)
        assert word ^ {fire} == following
        for direction in (1, -1):
            oriented = position(word, 0, direction)
            normalized = position(oriented, -min(oriented))
            assert normalized not in canonical
            canonical.add(normalized)
    # For all previous cycles the maximum occurs at the immediately previous
    # anchor, since the recipe shifts its entire word and firing list by one.
    return tuple(max(max(fires) - 1, *fires[:p + 1]) for p in range(len(phases)))


def rectangle_seed(phases, fires, envelopes, a, p, b, q):
    extreme_right = a + envelopes[p]
    extreme_left = b - envelopes[q]
    if extreme_right >= extreme_left:
        raise ValueError("the two prefixes may have a common fired coordinate")
    right_word = position(phases[p], a)
    left_word = position(phases[q], b, -1)
    assert max(right_word) <= extreme_right < extreme_left <= min(left_word)
    word = right_word | left_word
    events = (a + fires[p], b - fires[q])
    assert events[0] <= extreme_right < extreme_left <= events[1]
    assert (word | set(events)) <= set(SITES)
    return word, events


def seed_facts(phases, fires, envelopes):
    facts = {}
    targets = []
    for a, b, p, q in product(SITES, SITES, range(4), range(4)):
        if b - a > 11 or a + envelopes[p] >= b - envelopes[q]:
            continue
        word, events = rectangle_seed(phases, fires, envelopes, a, p, b, q)
        targets.append((a, p, b, q))
        for site in events:
            facts.setdefault((word, site), (a, p, b, q))
    return facts, targets


def prefix(phases, fires, start, direction, length):
    """Check the actual isolated recipe without computing any two-packet rule."""
    word = position(phases[0], start, direction)
    events = []
    for time in range(length + 1):
        shift, p = divmod(time, 4)
        anchor = start + direction * shift
        assert word == position(phases[p], anchor, direction)
        events.append(anchor + direction * fires[p])
        if time < length:
            word ^= {events[-1]}
    return word, events


def validate_axes(phases, fires, envelopes, targets):
    """A single inward phase-A pair works for the entire certificate at each radius."""
    controls = []
    for radius in (0, 1, 6, 31, 10**9):
        # These choices satisfy the inequalities for every nonnegative radius.
        start_right = min(SITES) - radius - 5
        start_left = max(SITES) + radius + 5
        parked_right = position(phases[0], start_right)
        parked_left = position(phases[0], start_left, -1)
        smallest_margin = None
        for a, p, b, q in targets:
            right_end = a + envelopes[p]
            left_end = b - envelopes[q]
            margin = min(min(parked_left) - right_end, left_end - max(parked_right))
            assert margin > radius
            smallest_margin = margin if smallest_margin is None else min(smallest_margin, margin)
            if radius <= 31:
                right_word, right = prefix(phases, fires, start_right, 1, 4 * (a - start_right) + p)
                left_word, left = prefix(phases, fires, start_left, -1, 4 * (start_left - b) + q)
                word, events = rectangle_seed(phases, fires, envelopes, a, p, b, q)
                assert right_word | left_word == word
                assert (right[-1], left[-1]) == events
                assert max(right) == right_end and min(left) == left_end
                assert set(right).isdisjoint(left)
        controls.append({"radius": radius, "common_phase_A_anchors": [start_right, start_left],
                         "minimum_axis_separation": smallest_margin,
                         "all_prefixes_replayed": radius <= 31})
    return controls


def close_seeds(seeds):
    """Use a worklist joining each new fact to already processed companion facts."""
    proof = dict.fromkeys(seeds)
    unseen = deque(proof)
    processed = defaultdict(set)

    def preserve(word, fired, retained):
        destination = (word ^ {fired}, retained)
        if destination not in proof:
            proof[destination] = (word, fired)
            unseen.append(destination)

    while unseen:
        word, site = unseen.popleft()
        for companion in sorted(processed[word]):
            preserve(word, site, companion)
            preserve(word, companion, site)
        processed[word].add(site)
    return proof, processed


def isolated_fire(word, phases, fires):
    matches = []
    for p, phase in enumerate(phases):
        for sign in (1, -1):
            oriented = position(phase, 0, sign)
            anchor = min(word) - min(oriented)
            if position(phase, anchor, sign) == word:
                matches.append((p, sign, anchor, anchor + sign * fires[p]))
    assert len(matches) <= 1
    return matches[0] if matches else None


def certificate(proof, seeds, target):
    """Collect just the ancestors of one contradiction, in deduction order."""
    steps = {}

    def visit(fact):
        if fact in steps:
            return
        word, retained = fact
        reason = proof[fact]
        if reason is None:
            row = {"rectangle": seeds[fact]}
        else:
            prior, fired = reason
            visit((prior, fired))
            visit((prior, retained))
            row = {"from": sorted(prior), "fire_first": fired}
        steps[fact] = {"occupied": sorted(word), "forced_fire": retained, **row}

    visit(target)
    return list(steps.values())


def replay_certificate(steps, phases, fires, envelopes):
    have = set()
    for row in steps:
        word, kept = frozenset(row["occupied"]), row["forced_fire"]
        if "rectangle" in row:
            given, events = rectangle_seed(phases, fires, envelopes, *row["rectangle"])
            assert given == word and kept in events
        else:
            source, fired = frozenset(row["from"]), row["fire_first"]
            assert fired != kept
            assert (source, fired) in have and (source, kept) in have
            assert word == source ^ {fired}
        have.add((word, kept))
    return have


def old_rule_control(phases, fires, radius):
    """Rebuild the old guard directly from the registered words for an infinite chain."""
    accepted = {position(word, -sign * fire, sign)
                for word, fire in zip(phases, fires, strict=True) for sign in (-1, 1)}
    assert frozenset() not in accepted

    def enabled(word):
        local_roots = {root for bit in word for root in range(bit - radius, bit + radius + 1)}
        return {root for root in local_roots
                if frozenset(bit - root for bit in word if abs(bit - root) <= radius) in accepted}

    for word, fire in zip(phases, fires, strict=True):
        for direction in (1, -1):
            assert enabled(position(word, 0, direction)) == {direction * fire}
    # The prior B81 collision places the leftmost occupied sites 12 places apart.
    initial = position(phases[0], 20) | position(phases[0], 36, -1)
    agenda = deque([(initial, ())])
    visited = {initial}
    while agenda:
        word, path = agenda.popleft()
        choices = enabled(word)
        for fire in sorted(choices):
            after = word ^ {fire}
            disabled = choices - {fire} - enabled(after)
            if disabled:
                return {"initial": sorted(initial), "earlier_firings": path, "occupied": sorted(word),
                        "enabled_before": sorted(choices), "first_fire": fire,
                        "enabled_after": sorted(enabled(after)), "disabled_other": sorted(disabled)}
            if after not in visited and len(path) < 2:
                visited.add(after)
                agenda.append((after, path + (fire,)))
    raise AssertionError("the old guard failed to reproduce the two-fire collision control")


def spreading_control():
    """All binary words needed for co-enabled persistence at either adjacent site."""
    def enabled(word, i):
        return i not in word and bool({i - 1, i + 1} & word)

    coenabled = 0
    for bits in product((0, 1), repeat=4):
        word = {i for i, on in zip(range(-1, 3), bits, strict=True) if on}
        if enabled(word, 0) and enabled(word, 1):
            assert enabled(word ^ {0}, 1) and enabled(word ^ {1}, 0)
            coenabled += 1
    assert coenabled > 0
    return {"adjacent_windows": 16, "coenabled_windows": coenabled,
            "outer_pairs": "sites more than one apart cannot change each other's guards"}


def audit():
    source_bytes = PHASE_ARTIFACT.read_bytes()
    source = json.loads(source_bytes)
    phases = tuple(frozenset(row["occupied"]) for row in source["phase_templates"])
    fires = tuple(row["toggle"] for row in source["phase_templates"])
    envelopes = phase_envelopes(phases, fires)
    assert envelopes == (4, 5, 5, 5)
    seeds, targets = seed_facts(phases, fires, envelopes)
    axes = validate_axes(phases, fires, envelopes, targets)
    proof, words = close_seeds(seeds)
    assert (len(words), len(proof)) == (184, 340)

    before = frozenset((4, 5, 8, 9))
    target = before ^ {6}, 7
    match = isolated_fire(target[0], phases, fires)
    assert {6, 7} <= words[before] and target in proof
    assert match == (2, 1, 4, 8)
    assert target not in seeds and all(isolated_fire(word, phases, fires) is None for word, _ in seeds)
    mirror = position(target[0], 13, -1), 13 - target[1]
    assert mirror in proof and isolated_fire(mirror[0], phases, fires) == (2, -1, 9, 5)
    treatment = certificate(proof, seeds, target)
    assert target in replay_certificate(treatment, phases, fires, envelopes)
    mutate = treatment[:-1] + [{**treatment[-1], "fire_first": target[1]}]
    try:
        replay_certificate(mutate, phases, fires, envelopes)
    except AssertionError:
        pass
    else:
        raise AssertionError("a same-site deduction was accepted")

    touching = (0, 1, 10, 1)
    assert fires[1] == 10 - fires[1]
    try:
        rectangle_seed(phases, fires, envelopes, *touching)
    except ValueError:
        pass
    else:
        raise AssertionError("touching envelopes with identical next fires were accepted")

    return {
        "validation": "V2-independent-reimplementation-or-kernel",
        "source_phase_artifact": str(PHASE_ARTIFACT.relative_to(ROOT)),
        "source_phase_sha256": sha256(source_bytes).hexdigest(),
        "scope": ["one binary coefficient per response, all finite occupied patterns",
                  "a finite uniform radius on a homogeneous line and both reflected isolated orbits",
                  "a sole prescribed event in each isolated phase",
                  "persistence of distinct co-enabled single-response events"],
        "radius_argument": {
            "common_starts": "phase A at -R-5 moving right and 18+R moving left",
            "left_right_fire_bounds": "rightward prefix fires at most a+M[p], leftward at least b-M[q]",
            "base": "on each axis the parked other word is out of range; its enabled event persists",
            "interior": "each next event survives the opposite event from the preceding row or column",
            "blank_quiescence_needed": False,
            "note": "the interval of fourteen sites bounds the closure, not the launches or guard radius",
        },
        "axes": axes,
        "phase_envelopes": envelopes,
        "counts": {"rectangle_targets": len(targets), "seed_facts": len(seeds),
                   "seed_states": len({word for word, _ in seeds}), "closed_facts": len(proof),
                   "closed_states": len(words), "deduction_steps_to_witness": len(treatment)},
        "contradiction": {"predecessor": sorted(before), "force_both": [6, 7],
                          "isolated_C": sorted(target[0]), "forced_extra_event": 7,
                          "sole_declared_event": match[-1]},
        "reflected_contradiction": {"isolated_C": sorted(mirror[0]), "forced_extra_event": mirror[1],
                                    "sole_declared_event": 5},
        "deduction_receipt": {"verified_steps": len(treatment),
                              "sha256": sha256(json.dumps(treatment, sort_keys=True).encode()).hexdigest(),
                              "last_four_steps": treatment[-4:]},
        "controls": {"touching_double_fire_rejected": {"anchors_and_phases": touching, "site": 5},
                     "same_site_deduction_mutant_rejected": True,
                     "no_seed_is_already_an_isolated_phase": True,
                     "old_guard_collision": old_rule_control(phases, fires, source["template_radius"]),
                     "persistent_spreading_rule": spreading_control()},
    }


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    report = audit()
    tmp = args.output.with_suffix(".tmp")
    tmp.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    tmp.replace(args.output)
    print(report["counts"], report["contradiction"])


if __name__ == "__main__":
    main()
