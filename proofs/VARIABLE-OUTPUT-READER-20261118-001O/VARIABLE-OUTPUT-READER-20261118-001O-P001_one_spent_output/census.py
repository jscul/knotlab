"""Enumerate and read every tagged one-spent source within the frozen width bound."""

from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
from pathlib import Path
from tempfile import TemporaryDirectory
import argparse
import json
import subprocess
import sys


PROOFS = Path(__file__).resolve().parents[2]
N_ID = "VARIABLE-OUTPUT-READER-20261118-001N"
N_PATH = PROOFS / N_ID / (N_ID + "-P001_fourth_at_the_parents")


def predecessor(filename):
    spec = spec_from_file_location("one_spent_" + filename, N_PATH / (filename + ".py"))
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


N = predecessor("census")
old, exact = N.old, N.exact


@dataclass(frozen=True, slots=True)
class Tagged:
    shape: old.Fixture
    gate: int = -1
    child: int = -1

    @property
    def just_spent(self):
        return self.child == self.shape.sites - 1

    def openings(self):
        for group in self.shape.groups((2, 3)):
            if self.gate not in group or self.child < 0:
                yield group, 2
        if self.shape.extra < 2:
            allowed = (1, 2, 3) if self.shape.extra == 0 else (3,)
            yield from ((group, 3) for group in self.shape.groups(allowed))

    def grow(self, group, fresh):
        shape = self.shape.grow(group, fresh)
        shape = replace(shape, extra=self.shape.extra + (fresh == 3))
        gate = self.shape.sites if fresh == 3 and shape.extra == 2 else self.gate
        child = self.shape.sites if self.gate in group else self.child
        return Tagged(shape, gate, child)


def incidence(shape):
    return tuple(tuple(row >> j & 1 for j in range(shape.sites)) for row in shape.neighbors)


def tag_color(shape, gate, child):
    colors = tuple((loose, i == gate, i == child) for i, loose in enumerate(shape.loose))
    return exact.ColoredMatrix.make(incidence(shape), colors)


def next_layer(layer, limit):
    buckets = defaultdict(list)
    seen = set()
    for owner in layer:
        for group, fresh in owner.openings():
            grown = owner.grow(group, fresh)
            shape = grown.shape
            still_needed = 2 - shape.extra + (grown.child < 0)
            if shape.sites + still_needed > limit:
                continue
            phase = (shape.extra, grown.gate >= 0, grown.child >= 0, grown.just_spent)
            literal = phase, shape.neighbors, shape.loose, grown.gate, grown.child
            if literal in seen:
                continue
            seen.add(literal)
            colored = tag_color(shape, grown.gate, grown.child)
            bucket = buckets[phase, hash(colored.invariant)]
            if not any(next(exact.isometries(prior, colored), None) is not None for prior, _ in bucket):
                bucket.append((colored, grown))
    return tuple(tagged for bucket in buckets.values() for _, tagged in bucket)


def physical_classes(layer):
    """Group completed tagged histories, retaining all tag variants and time flags."""
    buckets = defaultdict(list)
    for tagged in layer:
        if tagged.child < 0:
            continue
        assert tagged.shape.loose[tagged.gate] == 2
        color = old.color_incidence(tagged.shape)
        bucket = buckets[color.invariant]
        for prior, members in bucket:
            mapping = next(exact.isometries(color, prior), None)
            if mapping is not None:
                members.append((tagged, mapping[tagged.gate], mapping[tagged.child]))
                break
        else:
            bucket.append((color, [(tagged, tagged.gate, tagged.child)]))
    return [members for bucket in buckets.values() for _, members in bucket]


def tagged_roles(shape, gate, child, groups):
    roles = set()
    for label, site in (("gate", gate), ("child", child)):
        for group in groups:
            if site in group:
                roles.add(label + "_holder")
            if any(shape.neighbors[a] & shape.neighbors[b] & (1 << site) for a, b in combinations(group, 2)):
                roles.add(label + "_pair_witness")
    return roles


def tag_orbits(shape, members):
    colors, representatives = [], []
    for member, gate, child in members:
        color = tag_color(shape, gate, child)
        if not any(next(exact.isometries(prior, color), None) is not None for prior in colors):
            colors.append(color)
            representatives.append((member, gate, child))
    return representatives


def record_table(record):
    return dict(zip(old.pairs(record.fixture.width), record.entries, strict=True))


def direct_example(history, inverse):
    record = N.two_method_record(history)
    rows = tuple(row for _, row in history)
    events = N.checker.replay(history)
    gate = N.fourth(record)
    outputs = set(events[gate]["fresh"])
    touched = [(i, sorted(outputs & set(rows[i]))) for i in range(gate + 1, len(rows))
               if outputs & set(rows[i])]
    (child, (spent,)), = touched
    assert len(events[gate]["operands"]) == 3 and len(events[child]["fresh"]) == 2
    before, after = inverse.menus(rows[:child]), inverse.menus(rows[:child + 1])
    current = sorted(N.bits(word) for word in record.menu)
    assert current == list(inverse.menus(rows))
    width = record.fixture.width
    multiplier = next(n for n in range(2, width) if len({n * i % width for i in range(width)}) == width)
    rename = tuple((multiplier * i + 7) % width for i in range(width))
    remap = lambda word: tuple(sorted(rename[i] for i in word))
    renamed = N.two_method_record(old.previous.named(remap(row) for row in rows))
    new_table = record_table(renamed)
    assert all(new_table[remap(pair)] == k for pair, k in record_table(record).items())
    assert old.transport(record.menu, rename) == renamed.menu
    return {"width": width, "chronological_supports": rows, "gate": gate, "gate_input": events[gate]["operands"],
            "gate_outputs": sorted(outputs), "child": child, "child_move": events[child], "spent_output": spent,
            "surviving_siblings": sorted(outputs - {spent}), "before_spending_menu": before,
            "immediately_after_spending_menu": after, "surviving_original_triples": sorted(set(before) & set(after)),
            "current_menu": current, "current_legal_readings": [{"mark": mark, **N.mark_status(record, mark)} for mark in current],
            "gate_roles": N.roles(record, str(gate)), "child_roles": N.roles(record, str(child)),
            "rank_certificate": N.rank_certificate(record), "renaming_checked": rename,
            "pair_entries_checked_by_both_methods": len(new_table)}


def sibling_outcome(siblings, original_gate, rivals):
    holders = [tuple(row for row in rivals if sibling in row) for sibling in siblings]
    if any(len(users) != 1 for users in holders):
        return "shared", holders
    if holders[0] != holders[1]:
        return "split", holders
    if holders[0] != (original_gate,):
        return "different_physical_support", holders
    return "at_transported_support", holders


def equal_rank_rivals(record, members, inverse, counts):
    """Enumerate every named physical explanation after the table has forced the code."""
    short = {word for word in N.algebra.span(record.stars) if 0 < word.bit_count() <= 6}
    pool = {word for word in short if not any(other != word and other & word == other for other in short)}
    grown, prefix_counts = inverse.presentations(pool, record.fixture.width, record.fixture.sites)
    rivals = [state for state in grown if len(state) == record.fixture.sites]
    assert record.stars in rivals
    counts["reached_named_prefixes_from_same_code"] += sum(prefix_counts.values())
    counts["full_width_same_code_rivals"] += len(rivals)
    counts["physical_inverse_sources"] += len(rivals) == 1
    counts["sources_with_alternative_physical_rival"] += len(rivals) > 1
    alternatives = []
    for state in rivals:
        if state == record.stars:
            continue
        candidate = tuple(sorted(N.bits(word) for word in state))
        menu = inverse.menus(candidate)
        assert set(menu) == {N.bits(word) for word in record.menu}
        owners, neighbors = inverse.literal.incidence(candidate)
        options = []
        for _, gate, child in members:
            original_gate = record.history[gate][1]
            original_child = record.history[child][1]
            siblings = sorted(set(original_gate) - set().union(*(set(row) for i, (_, row) in enumerate(record.history) if i != gate)))
            assert len(siblings) == 2
            status, holders = sibling_outcome(siblings, original_gate, candidate)
            assert status not in {"shared", "split"}
            counts["alternate_rival_siblings_" + status] += 1
            holder = owners[siblings[0]][0]
            self_neighbors = {candidate[j] for j in neighbors[holder]}
            old_neighbors = {row for j, (_, row) in enumerate(record.history) if record.fixture.neighbors[gate] & (1 << j)}
            fixed_supports = {row for _, row in record.history} & set(candidate)
            options.append({"siblings": siblings, "status": status, "holder": holders[0][0],
                            "source_gate": original_gate, "source_child": original_child,
                            "lost_fixed_neighbor_supports": sorted((old_neighbors - self_neighbors) & fixed_supports),
                            "gained_fixed_neighbor_supports": sorted((self_neighbors - old_neighbors) & fixed_supports)})
        actual, _ = inverse.wired.wired_table(candidate)
        assert actual == record_table(record)
        alternatives.append({"source_replay": N.literal_record(record), "rival_supports": candidate, "menu": menu,
                             "sibling_diagnostics": options})
    return alternatives


def rank_and_rivals(records, physical_tags, inverse):
    counts = Counter()
    residuals, alternatives = [], []
    for record, members in zip(records, physical_tags, strict=True):
        width = record.fixture.width
        table = record_table(record)
        closed = [[1 << i for i in range(width)] for _ in range(7)]
        for (i, j), size in table.items():
            for limit in range(size, 7):
                closed[limit][i] |= 1 << j
                closed[limit][j] |= 1 << i
        uniquely_forced = []
        for star in record.stars:
            size = star.bit_count()
            if any(table[a, b] == size and closed[size][a] & closed[size][b] == star
                   for a, b in combinations(N.bits(star), 2)):
                uniquely_forced.append(size)
        counts["all_stars_unique_pair_at_D4"] += sum(size <= 5 for size in uniquely_forced) == record.fixture.sites
        if len(uniquely_forced) == record.fixture.sites:
            counts["all_stars_unique_pair_at_D5"] += 1
            alternatives.extend(equal_rank_rivals(record, members, inverse, counts))
            continue
        counts["forced_span_refinements"] += 1
        high = N.rank_certificate(record)["short_rank_checks"][-1]
        if high["forces_every_matching_rival_equation_space"]:
            counts["additional_full_rank_at_D5"] += 1
            alternatives.extend(equal_rank_rivals(record, members, inverse, counts))
            continue
        print(f"width {width} non-full short rank {high['forced_rank']}", file=sys.stderr, flush=True)
        rivals = inverse.read(table, width, record.fixture.sites)
        source_supports = {tuple(row) for _, row in record.history}
        assert any(set(case["supports"]) == source_supports for case in rivals["exact"])
        current_menu = set(N.bits(word) for word in record.menu)
        for key in ("through_D5", "exact"):
            opposing = [case for case in rivals[key] if set(case["menu"]) != current_menu]
            changed = [case for case in rivals[key] if set(case["supports"]) != source_supports]
            counts[key + "_sources_with_opposing_rival"] += bool(opposing)
            counts[key + "_sources_with_changed_supports"] += bool(changed)
        residuals.append({"source": N.literal_record(record), "source_menu": sorted(current_menu), **rivals})
    counts["fully_forced_equation_space_at_D5"] = counts["all_stars_unique_pair_at_D5"] + counts["additional_full_rank_at_D5"]
    return dict(counts), residuals, alternatives


def controls(inverse):
    older = json.loads((N_PATH / "census.json").read_text())
    row23 = older["witnesses"]["D4"]
    source23 = N.two_method_record(old.previous.named(row23["source_replay"]["supports"]))
    control23 = N.describe_comparison(source23, source23, row23["permutation"], 5)
    control27 = N.planted_D4()
    table31, left_bonds = inverse.wired.wired_table(inverse.LIVE)
    assert inverse.literal.replay(inverse.LIVE) and inverse.literal.replay(inverse.OTHER)
    other31, right_bonds = inverse.wired.wired_table(inverse.OTHER)
    assert table31 == other31 and left_bonds != right_bonds
    children = []
    for rows in (inverse.LIVE, inverse.OTHER):
        holders, neighbors = inverse.literal.incidence(rows)
        loose = sorted(bit for bit, uses in holders.items() if len(uses) == 1)
        outcomes = Counter()
        first = None
        for p in (2, 3):
            for operands in combinations(loose, p):
                parents = tuple(holders[bit][0] for bit in operands)
                if len(set(operands) & {28, 29, 30}) != 1 or not inverse.literal.legal_parents(parents, neighbors):
                    continue
                grown = (*rows, (*operands, 31, 32))
                inverse.literal.replay(grown)
                after = inverse.menus(grown)
                outcomes[f"p{p}_moves"] += 1
                outcomes[f"p{p}_empty"] += not after
                if not after and first is None:
                    first = grown[-1]
        assert first is not None
        children.append({"gate_support": rows[-1], "before_menu": inverse.menus(rows),
                         "named_spending_outcomes": dict(outcomes), "one_empty_child_support": first})
    child_support = tuple(children[0]["one_empty_child_support"])
    assert child_support == children[1]["one_empty_child_support"]
    after = [N.two_method_record(old.previous.named((*rows, child_support))) for rows in (inverse.LIVE, inverse.OTHER)]
    changed_after = [{"pair": pair, "before": table31.get(pair), "after_K": (k, g)}
                     for pair, k, g in zip(old.pairs(33), after[0].entries, after[1].entries, strict=True) if k != g]
    assert all(not case.menu for case in after) and all(min(row["after_K"]) == 6 for row in changed_after)
    assert len(changed_after) == 4
    return {"N23": control23, "N27": control27, "N_through27_source_counts": [
                [stage["width"], stage["source_types"], stage["unrestricted_D5_rank_screen"]["arbitrary_rival_spaces_forced_at_D5"]]
                for stage in older["stages"]],
            "N31_terminal_equal_table": {"compared_entries": len(table31), "different_parity_spaces": True,
                                         "before_width": 31, "after_width": 33, "both_sides": children,
                                         "matching_child_control": {"support": child_support, "compared_entries": len(after[0].entries),
                                                                    "newly_different_entries": changed_after}}}


def run(last, engine):
    inverse = predecessor("inverse_fixtures")
    layer = tuple(Tagged(shape) for shape in old.starters())
    stages, examples, direct, residuals, alternatives = [], {}, {}, [], []
    first_multiple_tags = None
    limit = (last - 5) // 2
    for sites in range(4, limit + 1):
        layer = next_layer(layer, limit)
        classes = physical_classes(layer)
        width = 2 * sites + 5
        print(f"width {width}: {len(layer)} tagged generation states, {len(classes)} completed physical types",
              file=sys.stderr, flush=True)
        if not classes:
            stages.append({"width": width, "physical_types": 0})
            continue
        records = old.measured([members[0][0].shape for members in classes], engine)
        count = Counter()
        physical_tags = []
        for record, members in zip(records, classes, strict=True):
            groups = tuple(record.fixture.groups((3,)))
            seen = set()
            tags = tag_orbits(record.fixture, members)
            physical_tags.append(tags)
            count["tagged_types_with_time_flag"] += len(members)
            count["tagged_types_ignoring_time_flag"] += len(tags)
            count["physically_multiple_tag_orbits"] += len(tags) > 1
            if len(tags) > 1 and first_multiple_tags is None:
                first_multiple_tags = {"reference": N.literal_record(record), "tags": [
                    {"image_gate": gate, "image_child": child, "history": direct_example(member.shape.history(), inverse)}
                    for member, gate, child in tags]}
            for member, gate, child in members:
                kind = "immediate" if member.just_spent else "later"
                count["tagged_" + kind] += 1
                roles = tagged_roles(record.fixture, gate, child, groups)
                seen.update(roles | {kind})
                if groups:
                    count["live_tagged_types"] += 1
                for role in sorted(roles):
                    if role not in direct:
                        direct[role] = direct_example(member.shape.history(), inverse)
                if roles:
                    seen.add("direct")
            for label in sorted(seen):
                count["physical_" + label] += 1
        native_control = N.two_method_record(records[0].history)
        assert records[0].menu == native_control.menu and records[0].entries == native_control.entries
        rank, remaining, changes = rank_and_rivals(records, physical_tags, inverse)
        residuals.extend(remaining)
        alternatives.extend(changes)
        moved = Counter()
        full = N.screen(records, None, moved, examples)
        complete_at_D5 = rank["fully_forced_equation_space_at_D5"] == len(records)
        clipped5 = full.copy() if complete_at_D5 else N.screen(records, 6, moved, examples)
        clipped4 = N.screen(records, 5, moved, examples)
        stages.append({"width": width, "held_out_width_29": width == 29, "physical_types": len(records),
                       "live_physical_types": sum(bool(record.menu) for record in records),
                       "legal_named_triples": sum(len(record.menu) for record in records),
                       "tagged_counts": dict(count), "full": full, "D5": clipped5, "D4": clipped4,
                       "arbitrary_rival_rank": rank, "moved_full_supports": dict(moved),
                       "all_maps_D5_equal_full_by_rank": complete_at_D5})
    comparisons = {}
    for stage, example in examples.items():
        left, right, image, *_ = example
        cutoff = 5 if stage == "D4" else 6 if stage == "D5" else None
        comparisons[stage] = N.describe_comparison(left, right, image, cutoff)
    return {"freeze": "4d2aac4a7", "through_width": last, "stages": stages,
            "direct_live_examples_by_first_role": direct, "comparison_examples": comparisons,
            "multiple_tag_example": first_multiple_tags, "every_rival_on_residual_tables": residuals,
            "arbitrary_rival_physical_alternatives_with_equal_code": alternatives, "controls": controls(inverse)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--width", type=int, default=29)
    args = parser.parse_args()
    if not 23 <= args.width <= 29 or args.width % 2 == 0:
        parser.error("width must be an odd integer from 23 through 29")
    with TemporaryDirectory(prefix="one-spent-census-") as scratch:
        engine = Path(scratch) / "measure"
        subprocess.run(["c++", "-std=c++20", "-O2", "-pthread", N.L / "census.cpp", "-o", engine], check=True)
        result = run(args.width, engine)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
