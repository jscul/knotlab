"""Run the frozen separated-readings cohort on initial and first-grown stages."""

import argparse
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
import gzip
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from random import Random
import sys
import time

from exact_counts import NotAllEqual, NotAllEqualSupport, Parity, boolean_words
from readings import choose_placements, ratio, score, total_variation
from summarize import summarize


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DESIGN = ROOT / "research/ENTANGLEMENT-READ-20261120-001/preregistration.md"
ARCHIVE = ROOT / ("artifacts/HEAVY-GROWTH-20261119-001/HEAVY-GROWTH-20261119-001-E001_checks/"
                  "sources_audit.json")
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name
GROWTH = ROOT / "experiments/NAE-GROWTH-20261119-001B/NAE-GROWTH-20261119-001B-E001_nae"
MODELS = ("parity", "nae")
sys.path.insert(0, str(GROWTH))
import naelib as canonical  # noqa: E402

J = canonical.J


@dataclass(frozen=True)
class Source:
    name: str
    group: str
    sizes: tuple
    meetings: tuple
    provenance: dict

    @property
    def supports(self):
        return tuple(tuple(sorted(support)) for support in J.stars_from(self.sizes, self.meetings))

    def fixed_marks(self, width):
        if self.name == "two_sharing_one" and width == 2:
            return 0, 1, (1, 2), (3, 4)
        if self.name == "two_disjoint" and width == 2:
            return 0, 1, (0, 1), (3, 4)
        if self.name == "two_disjoint" and width == 3:
            return 0, 1, (0, 1, 2), (3, 4, 5)
        return None


def decode_prufer(word):
    """The smallest labelled leaf convention for the Prüfer bijection."""
    degree = [1] * (len(word) + 2)
    for name in word:
        degree[name] += 1
    meetings = []
    for name in word:
        leaf = degree.index(1)
        meetings.append(tuple(sorted((leaf, name))))
        degree[leaf] = 0
        degree[name] -= 1
    meetings.append(tuple(index for index, value in enumerate(degree) if value == 1))
    return tuple(sorted(meetings))


def sources(controls_only):
    for name, sizes, meetings in (("single_ternary", (3,), ()),
                                  ("two_sharing_one", (3, 3), ((0, 1),)),
                                  ("two_disjoint", (3, 3), ())):
        yield Source(name, "controls", sizes, meetings, {"method": "specified minimum specimen"})
    if controls_only:
        return
    for name, n, meetings, surplus in (
        ("bare_chain_six", 6, [(j, j + 1) for j in range(5)], 0),
        ("bare_ring_five", 5, J.ring_edges(5), 0),
        ("one_spare_ring_five", 5, J.ring_edges(5), 1),
    ):
        meetings = tuple(sorted(tuple(sorted(meeting)) for meeting in meetings))
        sizes = tuple(size + surplus for size in J.bare_sizes(n, meetings))
        yield Source(name, "built", sizes, meetings, {"method": "specified funded specimen", "surplus": surplus})
    rng = Random(20261120)
    for n, replicate in product((4, 5, 6), range(4)):
        word = tuple(rng.randrange(n) for _ in range(n - 2))
        meetings = decode_prufer(word)
        bare = tuple(J.bare_sizes(n, meetings))
        for variant, sizes in (("bare", bare), ("extra", (bare[0] + 1, *bare[1:]))):
            yield Source(f"prufer_{n}_{replicate}_{variant}", f"prufer_{n}_{variant}", sizes, meetings,
                         {"method": "uniform labelled Prüfer word, with replacement",
                          "possible_words": n ** (n - 2), "draw": replicate, "word": word})
    archived = json.loads(ARCHIVE.read_text())["named_archive_starts"]
    fates = {"00": "finite burst and ends", "04": "finite burst and ends", "13": "unbounded births under parity"}
    for name, fate in fates.items():
        archive_id = f"start-{name}"
        row = archived[archive_id]
        assert row["gate"]["canonical"]
        source = Source(f"archive_{name}", "archive", tuple(row["sizes"]), tuple(map(tuple, row["meetings"])),
                        {"method": "declared equal-weight stress panel", "archive_label": archive_id,
                         "archived_draw": row["identifier"], "prior_parity_fate": fate,
                         "prior_parity_births": row["round_junction_counts"]})
        assert source.supports == tuple(map(tuple, row["gate"]["literal_supports"]))
        yield source


def live_knots(presentation):
    return [i for i in presentation.live if presentation.loose(i)]


def grow_once(old, law):
    before = J.S.from_junctions(old)
    grown = J.S.from_junctions(old)
    old_count = len(old)
    old_nbits = before.nbits
    rule = canonical.parity_rule(J.F.fewest) if law == "parity" else canonical.nae_rule(J.F.fewest)
    old_live = live_knots(before)
    reference = J.fastlib._orig(before, old_live)
    reference_demand = Counter(parent for group in reference for parent in group)
    assert reference == before.groups_among(old_live)
    result = grown.step(rule, None)
    if result is None:
        shortages = {j: reference_demand[j] - len(before.loose(j)) for j in old_live
                     if reference_demand[j] > len(before.loose(j))}
        assert shortages and grown.rounds == 0
        return "stalled", {"shortages": shortages}, None
    if result["new"] == 0:
        assert not old_live and grown.rounds == 0
        return "closed", {}, None

    supports = tuple(tuple(sorted(row)) for row in grown.bits_of)
    assert supports[:old_count] == old and grown.rounds == 1 and result["new"] == len(supports) - old_count
    new_ids = list(range(old_count, len(supports)))
    reference_following = J.fastlib._orig(grown, new_ids)
    assert reference_following == grown.groups_among(new_ids)
    following_demand = Counter(parent for group in reference_following for parent in group)
    taken = Counter()
    roster = []
    actual_groups = []
    for knot in new_ids:
        consumed = tuple(bit for bit in supports[knot] if bit < old_nbits)
        fresh = tuple(bit for bit in supports[knot] if bit >= old_nbits)
        taken.update(consumed)
        parents = tuple(sorted(before.owner[bit][0] for bit in consumed))
        assert len(set(parents)) == len(consumed) == grown.parents[knot]
        assert following_demand[knot] == grown.demand_at_birth[knot]
        assert len(fresh) == grown.fresh[knot]
        if fresh:
            assert len(fresh) == max(1, 3 - len(consumed), following_demand[knot])
        else:
            assert law == "parity" and len(new_ids) == 1 and not following_demand[knot]
        actual_groups.append(parents)
        roster.append({"knot": knot, "parents": parents, "consumed": consumed,
                       "fresh": fresh, "lookahead_demand": following_demand[knot]})
    assert taken == Counter(bit for j in old_live for bit in before.loose(j))
    expected_groups = [tuple(sorted(group)) for group in reference]
    expected_groups.extend((j,) for j in old_live for _ in range(len(before.loose(j)) - reference_demand[j]))
    assert Counter(actual_groups) == Counter(expected_groups)
    if law == "parity":
        # Every old row is still imposed. Matching projected rank forbids any new old condition.
        assert len(Parity(supports).projected_rows(range(old_nbits))) == Parity(old).rank
    else:
        # Every new support has its own fresh distinctions, so a full extension exists for every old state.
        assert all(row["fresh"] for row in roster)
    return "grown", {"births": roster, "old_projection_preserved": True,
                     "reference_group_and_demand_match": True}, supports


def certify(supports, law):
    if law == "parity":
        oracle = Parity(supports)
        return [oracle.certificate(support) for support in supports]
    with NotAllEqualSupport(supports) as oracle:
        return [oracle.certificate(support) for support in supports]


class CountStage:
    def __init__(self, old_supports, supports, law):
        if law == "parity":
            self.parity = Parity(supports)
            self.nae = None
        else:
            self.parity = None
            self.nae = NotAllEqual(old_supports, supports)

    @lru_cache(maxsize=1024)
    def histogram(self, marks, weighting):
        if self.parity is not None:
            return self.parity.histogram(marks), 1, None
        return self.nae.histogram(marks, weighting)


def project_counts(counts, marks, kept):
    bins = {word: 0 for word in boolean_words(len(kept))}
    positions = [marks.index(bit) for bit in kept]
    for word, weight in zip(boolean_words(len(marks)), counts, strict=True):
        bins["".join(word[i] for i in positions)] += weight
    return list(bins.values())


def measure(slot, width, old_nbits, counter, original, age):
    placement = slot["placement"]
    marks = placement["alice"] + placement["bob"]
    raw, _, u_peak = counter.histogram(marks, "U")
    lifted, scale, l_peak = counter.histogram(marks, "L")
    old_total = original.histogram((), "U")[0][0]
    if counter.parity is not None:
        scale, remainder = divmod(counter.parity.total, old_total)
        assert remainder == 0
    assert [item > 0 for item in raw] == [item > 0 for item in lifted]
    tilted = [value * (1 + int(word[0])) for value, word in zip(raw, boolean_words(len(marks)), strict=True)]
    assert sum(raw) == counter.histogram((), "U")[0][0] and sum(lifted) == scale * old_total
    result = {"mark_order": marks, "weightings": {}}
    for weighting, values, unit, peak in (("U", raw, 1, u_peak), ("L", lifted, scale, l_peak),
                                          ("T", tilted, 1, u_peak)):
        scores = score(values, width)
        for contexts in scores.values():
            for row in contexts["contexts"]:
                assert row["weight"] == sum(row["pair_joint"])
        entry = {"counts": values, "total": sum(values), "integer_units_per_unscaled_mass": unit,
                 "peak_counting_variables": peak, "arms": scores}
        if age == 1:
            prior_marks = tuple(bit for bit in marks if bit < old_nbits)
            prior, _, _ = original.histogram(prior_marks, "U")
            marginal = project_counts(values, marks, prior_marks)
            challenge = total_variation(marginal, prior)
            if weighting == "L":
                assert challenge == 0
            assert all((left > 0) == (right > 0) for left, right in zip(marginal, prior, strict=True))
            entry["old_mark_check"] = {"marks": prior_marks, "start_counts": prior, "grown_counts": marginal,
                                        "mass_tv_from_start_u": ratio(challenge), "same_support": True}
        result["weightings"][weighting] = entry
    return result


def qualify_stage(source, stage, old_nbits, law, age, certificates):
    if age == 0 and not all(row["eligible"] for row in certificates):
        return {"age": age, "status": "unlawful_source", "supports": stage, "support_certificates": certificates}
    return {"age": age, "status": "measured_stage", "supports": stage, "support_certificates": certificates,
            "external_pairs": choose_placements(stage, certificates, old_nbits, 2, source.fixed_marks(2)),
            "six_marks": choose_placements(stage, certificates, old_nbits, 3, source.fixed_marks(3))}


def prepare(source):
    old = source.supports
    old_nbits = 1 + max(map(max, old))
    out = {"name": source.name, "group": source.group, "sizes": source.sizes, "meetings": source.meetings,
           "provenance": source.provenance, "old_distinctions": old_nbits, "laws": {}}
    for law in MODELS:
        stage = qualify_stage(source, old, old_nbits, law, 0, certify(old, law))
        if stage["status"] == "unlawful_source":
            out["laws"][law] = [stage, {"age": 1, "status": "unlawful_source"}]
            continue
        status, growth, grown = grow_once(old, law)
        if grown is None:
            next_stage = {"age": 1, "status": status}
        else:
            next_stage = qualify_stage(source, grown, old_nbits, law, 1, certify(grown, law))
            if source.group == "archive":
                expected = source.provenance["prior_parity_births"][:2]
                assert [len(old), len(growth["births"])] == expected
        next_stage["growth"] = growth
        out["laws"][law] = [stage, next_stage]
    assert_pair_growth(out)
    return out


def assert_pair_growth(source):
    left, right = [source["laws"][law][1] for law in MODELS]
    if "unlawful_source" in (left["status"], right["status"]):
        return
    assert left["status"] == right["status"]
    if "supports" not in left:
        return
    if any(not row["fresh"] for row in left["growth"]["births"]):
        assert len(left["growth"]["births"]) == len(right["growth"]["births"]) == 1
        assert left["growth"]["births"][0]["consumed"] == right["growth"]["births"][0]["consumed"]
    else:
        assert left["supports"] == right["supports"]


def measure_source(source):
    for law, stages in source["laws"].items():
        old = stages[0]["supports"]
        original = CountStage(old, old, law)
        for stage in stages:
            if stage["status"] != "measured_stage":
                continue
            counter = CountStage(old, stage["supports"], law) if stage["age"] else original
            stage["complete_assignments"] = counter.histogram((), "U")[0][0]
            for key, width in (("external_pairs", 2), ("six_marks", 3)):
                for slot in stage[key]["slots"]:
                    if slot["placement"] is not None:
                        slot["result"] = measure(slot, width, source["old_distinctions"], counter, original, stage["age"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--controls-only", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if args.controls_only and args.output == OUTPUT:
        parser.error("use a separate output directory for the controls-only check")
    frozen_hash = json.loads((HERE / "contract.json").read_text())["design_sha256"]
    assert sha256(DESIGN.read_bytes()).hexdigest() == frozen_hash
    start = time.monotonic()
    cohort = [prepare(source) for source in sources(args.controls_only)]
    print(f"Selected placements for {len(cohort)} sources in {time.monotonic() - start:.3f} s", flush=True)
    for source in cohort:
        measure_source(source)
        print(f"{source['name']} measured at {time.monotonic() - start:.3f} s", flush=True)
    metadata = {"design_sha256": frozen_hash, "archive_sha256": sha256(ARCHIVE.read_bytes()).hexdigest(),
                "runtime": sys.version, "controls_only": args.controls_only,
                "mark_order": "Alice u,v[,selector], then Bob u,v[,selector]; binary words run from all-zero to all-one",
                "mark_selection": "lexicographic literal supports; ascending pair then selector on each side, except stated minima",
                "placement_unit": "ordered side marks on an unordered pair of certified support occurrences; u<v on each side",
                "qualification_patterns": "NAE integer encodings assign the first distinction the least significant bit",
                "allocation": "canonical engine order: sorted parent groups, then loose remainder in stored order; each use takes the next loose distinction",
                "weight_units": {"U": "one per complete allowed assignment", "L": "counts divided by the recorded units per unscaled mass give each complete start assignment mass one",
                                 "T": "U multiplied by two for Alice u=1"}}
    args.output.mkdir(parents=True, exist_ok=True)
    raw = json.dumps({"metadata": metadata, "sources": cohort}, separators=(",", ":")).encode()
    (args.output / "exact_readings.json.gz").write_bytes(gzip.compress(raw, mtime=0))
    summary = summarize(cohort)
    summary["metadata"] = metadata
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")


if __name__ == "__main__":
    main()
