"""Compare an independent growth replay with the archived Ticket B records."""

import argparse
import ast
from collections import Counter, defaultdict
import gzip
from itertools import combinations
import json
from pathlib import Path
import re
from time import perf_counter

from b_growth import Law, bar, components, grow, roster_for


ROOT = Path(__file__).resolve().parents[3]
TICKET = "WHAT-A-BIRTH-CARRIES-20261125-001B"
RECORD = ROOT / "research" / TICKET
ARCHIVE = ROOT / "artifacts" / TICKET / f"{TICKET}-E001_link_through_a_made_knot"
DEFINITIONS = {row["id"]: row for row in json.loads((RECORD / "family.json").read_text())["search"]}
STARTS = json.loads((RECORD / "starts.json").read_text())["stars"]
DESCENTS = ("neither", "X only", "Y only", "both")


def records(name):
    with gzip.open(ARCHIVE / f"{name}.jsonl.gz", "rt") as source:
        yield from (json.loads(line) for line in source)


class Audit:
    def __init__(self):
        self.checked = Counter()
        self.mismatches = Counter()
        self.examples = defaultdict(list)

    def same(self, field, actual, archived, context):
        self.checked[field] += 1
        if actual == archived:
            return
        self.mismatches[field] += 1
        if len(self.examples[field]) < 4:
            self.examples[field].append(dict(context=context, replay=str(actual)[:600], archived=str(archived)[:600]))


def label_descendants(run, s, parts):
    labels = [0] * len(run.states[-1].knots)
    for part, members in enumerate(parts):
        for member in members:
            labels[member] = 1 << part
    for knot in range(len(run.states[s].knots), len(labels)):
        for parent in run.states[-1].knots[knot].parents:
            labels[knot] |= labels[parent]
    return labels


def union_bits(labels, members):
    bits = 0
    for member in members:
        bits |= labels[member]
    return bits


def bit_indices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask -= bit


def pair_classes(state, parts):
    owner = {member: part for part, members in enumerate(parts) for member in members}
    sharing = {part: set() for part in range(len(parts))}
    for holders in state.holders.values():
        involved = {owner[knot] for knot in holders if knot in owner}
        for part in involved:
            sharing[part].update(involved - {part})
    return {part: c for c, group in enumerate(components(sharing)) for part in group}


def record_meetings(run, s, parts, classes):
    labels = label_descendants(run, s, parts)
    meetings = {}
    for t in range(s + 1, len(run.states)):
        step = run.steps[t]
        now = defaultdict(set)

        def add(a, b, how):
            if classes[a] != classes[b]:
                now[tuple(sorted((a, b)))].add(how)

        for how, groups in (("group", step.groups), ("demand group", step.demand_groups)):
            for group in groups:
                for a, b in combinations(bit_indices(union_bits(labels, group)), 2):
                    add(a, b, how)
        for birth in step.births.values():
            for distinction in birth.takes:
                suppliers = run.states[t - 1].holders[distinction]
                for a in bit_indices(labels[birth.knot]):
                    for b in bit_indices(union_bits(labels, suppliers)):
                        add(a, b, "take")
        for pair, how in now.items():
            meetings.setdefault(pair, (t, sorted(how)))
    return meetings, labels


def all_ancestors(state):
    ancestry = []
    for knot in state.knots:
        ancestry.append(set(knot.parents).union(*(ancestry[parent] for parent in knot.parents)))
    return ancestry


def link_details(run, s, t, X, Y):
    labels = label_descendants(run, s, [X, Y])
    step = run.steps[t]
    state = run.states[t]
    old_state = run.states[t - 1]
    ancestors = all_ancestors(state)
    linked = defaultdict(set)
    witnesses = defaultdict(list)
    weak = False
    for roster in [step.roster, step.demand_roster]:
        for knot, members in roster.met_sets.items():
            if union_bits(labels, members) != 3:
                continue
            if state.knots[knot].made:
                weak = True
            if knot < len(old_state.knots):
                linked[knot].add("met set")
                witnesses[knot].append(members)

    for birth in step.births.values():
        flags = labels[birth.knot]
        for distinction in birth.takes:
            for knot in old_state.holders[distinction]:
                other = labels[knot]
                if (flags & 1 and other & 2) or (flags & 2 and other & 1):
                    linked[knot].add("supplier of a cross take")

    result = []
    for knot, how in sorted(linked.items()):
        info = state.knots[knot]
        ancestral = False
        for members in witnesses[knot]:
            for a in members:
                for b in members:
                    if a == b or not (labels[a] & 1 and labels[b] & 2):
                        continue
                    if knot in ancestors[a] and knot in ancestors[b] and (
                        knot not in state.knots[a].parents or knot not in state.knots[b].parents
                    ):
                        ancestral = True
        every = bool(info.made and all(knot in ancestors[member] for member in tuple(X) + tuple(Y)))
        distinctions = []
        for d in sorted(info.places):
            if any(labels[member] for member in state.holders[d]):
                holders = [[member, state.knots[member].made, DESCENTS[labels[member]], state.knots[member].kind]
                           for member in sorted(state.holders[d])]
                distinctions.append(dict(d=d, first_holder_round=min(row[1] for row in holders), holders=holders))
        result.append(dict(knot=knot, made=info.made, kind=info.kind, parents=list(info.parents),
                           descent=DESCENTS[labels[knot]], ancestry=[[a, state.knots[a].made] for a in sorted(ancestors[knot])],
                           ancestral_made=bool(info.made and ancestral), every_member_form=every,
                           how=sorted(how), linking_distinctions=distinctions))
    strict = bool(result) and all(link["made"] for link in result)
    starts_hold = any(holder[1] == 0 for link in result for d in link["linking_distinctions"] for holder in d["holders"])
    return result, strict, weak, starts_hold


def course_record(run, s, end, X, Y):
    """Serialize the frozen labelled course with unary incidences counted on their knot."""
    state = run.states[end]
    labels = label_descendants(run, s, [X, Y])
    selected = [knot for knot in range(len(state.knots)) if labels[knot] == 1]
    knot_names = {knot: index for index, knot in enumerate(selected)}
    start_distinctions = run.states[s].holders
    by_knot = defaultdict(Counter)
    shared = []
    for d, holders in sorted(state.holders.items()):
        included = sorted(holders & knot_names.keys())
        if not included:
            continue
        origin = "E" if d in start_distinctions else "FX" if labels[min(holders)] == 1 else "FO"
        tag = f"{origin}:{int(d in state.bars)}"
        if len(included) == 1:
            by_knot[included[0]][tag] += 1
        else:
            shared.append((tag, included))

    tags = []
    incidence = []
    for knot in selected:
        info = state.knots[knot]
        first = max(info.made, s)
        history = ",".join(f"{h}.{k}" for h, k in (run.states[t].loose_counts(knot) for t in range(first, end + 1)))
        singletons = ",".join(f"{tag}*{count}" for tag, count in sorted(by_knot[knot].items()))
        tags.append(f"K|{first}|{info.kind}|{len(info.places)}|{history}|{singletons}")
        incidence.extend((knot_names[knot], knot_names[p], "p") for p in info.parents if p in knot_names)
    for tag, holders in shared:
        incidence.extend((knot_names[knot], len(tags), "i") for knot in holders)
        tags.append(f"D|{tag}")
    return len(selected), tuple(tags), frozenset(incidence)


def archived_course(course):
    return course["n_knots"], tuple(course["labels"]), frozenset(tuple(link) for link in course["edges"])


def course_end(course):
    return max(int(fields[1]) + len(fields[4].split(",")) - 1
               for fields in (label.split("|") for label in course["labels"]) if fields[0] == "K")


def sibling_swap(run, s, X, Y, details):
    """Check a constructed swap, fixing every start knot, start distinction and linking knot."""
    state = run.states[s]
    parents = [{state.knots[member].parents for member in part} for part in (X, Y)]
    if len(X) != len(Y) or any(len(choices) != 1 for choices in parents):
        return False
    first, second = (choices.pop() for choices in parents)
    if len(first) != 1 or len(second) != 1:
        return False
    swaps = list(zip([*first, *X], [*second, *Y]))
    mapping = dict(swaps + [(b, a) for a, b in swaps])
    if len(mapping) != 2 * len(swaps):
        return False
    fixed_knots = set(range(len(run.states[0].knots))) | {link["knot"] for link in details}
    if any(knot in mapping for knot in fixed_knots):
        return False
    for knot, source in enumerate(state.knots):
        target = state.knots[mapping.get(knot, knot)]
        if (source.made, source.kind) != (target.made, target.kind):
            return False
        if sorted(mapping.get(parent, parent) for parent in source.parents) != list(target.parents):
            return False

    start_distinctions = run.states[0].holders
    renamed = {d: frozenset(mapping.get(knot, knot) for knot in holders) for d, holders in state.holders.items()}
    if any(renamed[d] != state.holders[d] for d in start_distinctions):
        return False
    return (Counter((holders, d in state.bars) for d, holders in renamed.items() if d not in start_distinctions)
            == Counter((frozenset(h), d in state.bars) for d, h in state.holders.items() if d not in start_distinctions))


def compare_link(audit, row, run, pair, meeting):
    s, X, Y = pair["s"], pair["X"], pair["Y"]
    context = row["id"], s, X, Y
    audit.same("meeting_round_and_source", meeting, (pair["meeting_round"], sorted(pair["meeting_how"])), context)
    if meeting is None:
        return
    details, strict, weak, starts_hold = link_details(run, s, meeting[0], X, Y)
    for key, replay in {"strict": strict, "weak_FD57": weak, "start_knot_holds_linking_distinction": starts_hold,
                        "ancestral": strict and any(link["ancestral_made"] for link in details),
                        "ancestral_every_member": strict and any(link["every_member_form"] for link in details)}.items():
        audit.same(f"link_{key}", replay, pair[key], context)
    archive_details = [{key: value for key, value in link.items() if key != "class"} for link in pair["linking"]]
    audit.same("link_incidence_and_provenance", details, archive_details, context)
    if strict and row["law"]["ration"] == "PARENT-OWING" and row["law"]["treatment"] == "CANCEL-OFFSHOOT":
        audit.same("owing_sibling_swap_fixes_every_start_distinction", sibling_swap(run, s, X, Y, details),
                   True, context)


def compare_rosters(audit, row, run):
    context = row["id"]
    total_size = sum(len(state.knots) for state in run.states)
    audit.same("rounds_read", len(run.states) - 1, row["rounds_read"], context)
    audit.same("final_knot_count", len(run.states[-1].knots), row["knots"], context)
    audit.same("stop", run.stop, row["stop"], context)
    audit.same("guard", run.guard, row["guard"], context)
    for field, count in run.peaks.items():
        audit.same(f"peak_{field}", count, row["peaks"][field], context)
    if row["knot_test_A"]["n_untested"] == 0:
        audit.same("total_knots_over_rounds", total_size, row["knot_test_A"]["verdicts"], context)

    meetings_by_s = {}
    for s_text, archived in row["s"].items():
        s = int(s_text)
        if not archived["reached"]:
            audit.same("round_reached", s < len(run.states), False, (context, s))
            continue
        state = run.states[s]
        parts = roster_for(state.holders, state.member_loose).parts
        classes = pair_classes(state, parts)
        meetings, _ = record_meetings(run, s, parts, classes)
        meetings_by_s[s] = meetings
        audit.same("roster_part_members", [list(part) for part in parts], archived["parts"], (context, s))
        n_parts = len(parts)
        all_pairs = [(a, b) for a in range(n_parts) for b in range(n_parts) if classes[a] != classes[b]]
        no_meeting = [list((a, b)) for a, b in all_pairs if tuple(sorted((a, b))) not in meetings]
        audit.same("eligible_ordered_pairs", len(all_pairs), archived["n_ordered_pairs"], (context, s))
        audit.same("no_meeting_pair_identities", no_meeting, archived["no_meeting_pairs"], (context, s))
    for pair in row["pairs"]:
        index = tuple(sorted((pair["X_part"], pair["Y_part"])))
        compare_link(audit, row, run, pair, meetings_by_s[pair["s"]].get(index))


def compare_barred(audit, row, run, law, pair):
    s, X, Y = pair["s"], pair["X"], pair["Y"]
    context = row["id"], s, X, Y
    final = 4 if law.take == "J-EACH-PART" else 7
    barred = bar(run, s, Y, law, rounds=final)
    if "barred_run" not in pair:
        return None

    branch = pair["barred_run"]
    meeting, _ = record_meetings(barred, s, [X, Y], {0: 0, 1: 1})
    audit.same("barred_meeting", meeting.get((0, 1), (None,))[0], branch["meeting_round"], context)
    audit.same("barred_rounds_read", len(barred.states) - 1, branch["rounds_read"], context)
    audit.same("barred_stop", barred.stop, branch["stop"], context)
    audit.same("barred_guard", barred.guard, branch["guard"], context)

    for stem, source in (("course_A", run), ("course_barred", barred)):
        if stem in pair:
            stored = pair[stem]
            end = course_end(stored)
            concrete = course_record(source, s, end, X, Y) if end < len(source.states) else None
            audit.same(stem + "_concrete_labels_and_incidence", concrete, archived_course(stored), (*context, end))

    for subset in pair.get("subsets", {}).get("subsets", []):
        active = subset["A"]
        if active == Y:
            source = run
        elif not active:
            source = barred
        else:
            source = bar(run, s, set(Y) - set(active), law, rounds=final)
        subset_meetings, _ = record_meetings(source, s, [X, Y], {0: 0, 1: 1})
        t = subset_meetings.get((0, 1), (None,))[0]
        audit.same("subset_meeting", t, subset["meeting_round"], (*context, active))
        if t is not None:
            _, strict, _, _ = link_details(source, s, t, X, Y)
            audit.same("subset_strict", strict, subset["strict"], (*context, active))
        audit.same("subset_rounds_read", len(source.states) - 1, subset["rounds_read"], (*context, active))

    if not pair.get("y_side_knots_first_differing_demand") or not pair["strict"] or law.ration != "PARENT-OWING":
        return None
    observed = pair["y_side_knots_first_differing_demand"]
    round_number = observed["round"]
    focus = tuple(X)
    chains = []
    for source, tag in ((run, "value_A"), (barred, "value_barred")):
        labels = label_descendants(source, s, [X, Y])
        births = source.steps[round_number].births
        focal = [birth for birth in births.values() if birth.parents == focus]
        if len(focal) != 1 or round_number + 1 not in source.steps:
            continue
        join = focal[0]
        demands = [DESCENTS[labels[member]] for group in join.demand_partners
                   for member in group if member != join.knot]
        audit.same("owing_focal_demand_and_partner_descents", (join.demand, sorted(demands)),
                   (observed[tag][0], sorted(observed[tag][1])), (*context, tag))
        offshoot = next((birth for birth in source.steps[round_number + 1].births.values()
                         if birth.kind == "offshoot" and birth.parents == (join.knot,)), None)
        if offshoot is None:
            continue
        audit.same("owing_offshoot_has_parent_demand_fresh", (offshoot.owing, len(offshoot.fresh)),
                   (join.demand, join.demand), (*context, tag))
        chains.append({"branch": tag, "join": join.knot, "parents": list(join.parents), "round": round_number,
                       "inputs": list(join.inputs), "taken": list(join.takes), "demand": join.demand,
                       "fresh": list(join.fresh), "offshoot": offshoot.knot, "offshoot_round": round_number + 1,
                       "offshoot_owing": offshoot.owing, "offshoot_fresh": list(offshoot.fresh)})
    return {"item": row["id"], "s": s, "X": X, "Y": Y, "births": chains}


HEADER = re.compile(r"^=== (.*?), (\S+).*rounds 1\.\.(\d+)")
ROUND = re.compile(r"^ round (\d+): groups (\[.*\]); short (\[.*\]); owing (\{.*\}); "
                   r"retired (\[.*\]); waiting (\[.*\])")
BIRTH = re.compile(r"^   knot (\d+) (\w+) parents (\[.*\]) inputs (\[.*\]) \(taken (\[.*\])\) "
                   r"D=(\d+) p=(\d+) f=(\d+)")


def listing_law(name):
    parts = name.split("/")
    ration, treatment = parts[:2]
    take = parts[3] if parts[2] == "RELEASE" else parts[2]
    take = {"MET-ONE": "MET-SOLE", "STEPS1-ONE": "STEPS1-SOLE"}.get(take, take)
    if "PARENT-OWING" in parts:
        ration = "PARENT-OWING"
    if "BY-SHORTFALL" in parts:
        treatment = "SHORT-BY"
    return Law(ration, treatment, take, parts[-1])


def compare_listing(audit, file):
    run = None
    for line in file.read_text().splitlines():
        if match := HEADER.match(line):
            start, law, last = match.groups()
            run = grow(STARTS[start], listing_law(law), rounds=int(last))
            context = file.name, start, law
            audit.same("listing_rounds_reached", len(run.states) - 1, int(last), context)
        elif match := ROUND.match(line):
            number = int(match[1])
            step = run.steps[number]
            groups, short, owing, retired, waiting = [ast.literal_eval(part) for part in match.groups()[1:]]
            audit.same("listing_round_groups_owing_and_treatment",
                       ([list(group) for group in step.groups], list(step.short), dict(step.owing),
                        list(step.retired), list(step.waiting)),
                       (groups, short, owing, retired, waiting), (*context, number))
        elif match := BIRTH.match(line):
            knot, kind, parents, inputs, taken, demand, places, fresh = match.groups()
            actual = step.births[int(knot)]
            archived = (kind, tuple(ast.literal_eval(parents)), tuple(ast.literal_eval(inputs)),
                        tuple(ast.literal_eval(taken)), int(demand), int(places), int(fresh))
            audit.same("listing_birth_parents_inputs_takes_demand_and_fresh",
                       (actual.kind, actual.parents, actual.inputs, actual.takes, actual.demand,
                        len(actual.inputs), len(actual.fresh)), archived, (*context, number, int(knot)))
        elif line.startswith("   candidates:"):
            candidates = ast.literal_eval(line.split(":", 1)[1].strip())
            audit.same("listing_take_candidates",
                       [(knot, list(birth.candidates)) for knot, birth in step.births.items() if birth.candidates],
                       candidates, (*context, number))


def rename_start(ordinary, new):
    old = ordinary.states[0]
    renamed = new.states[0]
    new_ids = range(len(renamed.knots))
    renamed_holders = Counter(frozenset(ids) for ids in renamed.holders.values())

    # No start has more than ten knots. Match equal sizes and each shared count before testing all holders.
    candidates = [tuple(j for j in new_ids if len(knot.places) == len(renamed.knots[j].places)) for knot in old.knots]

    def mappings(mapping, used):
        i = len(mapping)
        if i == len(candidates):
            signatures = Counter(frozenset(mapping[knot] for knot in ids) for ids in old.holders.values())
            if signatures == renamed_holders:
                yield mapping
            return
        for j in candidates[i]:
            if j in used:
                continue
            if any(len(set(old.knots[i].places) & set(old.knots[k].places)) !=
                   len(set(renamed.knots[j].places) & set(renamed.knots[l].places))
                   for k, l in enumerate(mapping)):
                continue
            yield from mappings(mapping + (j,), used | {j})

    yield from mappings((), set())


def same_by_birth_maps(ordinary, renamed):
    # Fixed places make earlier holder sets restrictions of the final holder sets.
    # Bar histories distinguish changes even when two distinctions keep the same holders.
    def signatures(run, knot_map):
        final_state = run.states[-1]
        return Counter((tuple(sorted(knot_map[knot] for knot in holders)),
                        tuple(state.number for state in run.states if d in state.bars))
                       for d, holders in final_state.holders.items())

    if len(ordinary.states) != len(renamed.states):
        return False
    target_signature = signatures(renamed, range(len(renamed.states[-1].knots)))
    for candidate in rename_start(ordinary, renamed):
        knot_map = list(candidate)
        for s in range(1, len(ordinary.states)):
            old_step = ordinary.steps[s]
            new_step = renamed.steps[s]
            target = defaultdict(list)
            for knot, birth in new_step.births.items():
                target[birth.kind, birth.parents].append(knot)
            allocated = Counter()
            for birth in old_step.births.values():
                key = birth.kind, tuple(sorted(knot_map[p] for p in birth.parents))
                at = allocated[key]
                if at >= len(target[key]):
                    break
                knot_map.append(target[key][at])
                allocated[key] += 1
            expected = renamed.states[s]
            actual = ordinary.states[s]
            if len(knot_map) != len(actual.knots) or len(knot_map) != len(expected.knots):
                break
        else:
            if signatures(ordinary, knot_map) == target_signature:
                return True
    return False


def compare_renaming(audit, row, cache):
    _, law_id, start, knot_law, _ = row["id"].split("|")
    specification = DEFINITIONS[law_id]
    law = Law(specification["ration"], specification["treatment"], specification["take"], knot_law)
    renamed = grow(row["stars"], law)
    base_key = start, law
    if base_key not in cache:
        cache[base_key] = grow(STARTS[start], law)
    ordinary = cache[base_key]
    expected = [tuple(int(n) for n in fixed.split("|")[:2]) for fixed in row["structure_invariants"]]
    measured = [(len(state.knots), len(state.holders)) for state in renamed.states]
    audit.same("N2_counts_every_round", measured, expected, row["id"])
    audit.same("N2_rounds_read", len(renamed.states) - 1, row["rounds_read"], row["id"])
    audit.same("N2_concrete_renaming_by_birth_map", same_by_birth_maps(ordinary, renamed), True, row["id"])


def select_control(row):
    if "planted" in row["id"]:
        return False
    return (row["start"] in {"two-knot", "three-knot", "Ring(5,3)"}
            and row["law"]["ration"] == "FLOOR1")


def compare_planted(audit, row):
    knot_law = row["id"].split("|")[-1]
    law = Law("ORD", "CANCEL-RETIRE", "MET", knot_law, "OLDEST")
    run = grow(row["stars"], law)
    s, X, Y = row["s"], row["X"], row["Y"]
    bars = set(Y) - set(row["kept_usable_a1"])
    for name, source in (("a=4", run), ("a=1", bar(run, s, bars, law))):
        context = row["id"], name
        archived = row["runs"][name]
        meetings, _ = record_meetings(source, s, [X, Y], {0: 0, 1: 1})
        meeting = meetings.get((0, 1))
        audit.same("planted_meeting", list(meeting) if meeting else None, archived["meeting"], context)
        audit.same("planted_rounds_read", len(source.states) - 1, archived["rounds_read"], context)
        audit.same("planted_guard", source.guard, archived["guard"], context)
        if meeting:
            links, strict, _, _ = link_details(source, s, meeting[0], X, Y)
            audit.same("planted_link_and_provenance", links,
                       [{k: v for k, v in link.items() if k != "class"} for link in archived["linking"]], context)
            audit.same("planted_strict", strict, archived["strict"], context)


def smoke_row(source, row):
    if source == "run1a":
        return row["id"] in {"L02|Ring(5,3)|parity", "L05|Ring(5,3)|parity", "L10|Ring(5,3)|parity"}
    if source == "runN2":
        return row["id"] in {"N2|L10|Ring(7,3)|parity|reversal", "N2|L02|two-knot|parity|n000"}
    return row.get("start") in {"Ring(5,3)", "Ring(5,3)+1+2"} and row.get("law", {}).get("knot_law") == "parity"


def main(smoke):
    started = perf_counter()
    audit = Audit()
    sample = Counter()
    bar_sample = []
    evidence = []
    no_births = {}
    for file in (RECORD / "gate_listing_b.txt", *sorted(ARCHIVE.glob("listing_*.txt"))):
        compare_listing(audit, file)

    for source in ("run1a", "run1b", "run1c", "runP1", "runU1", "runM2", "runC0"):
        for row in records(source):
            if "planted" in row["id"]:
                if not smoke or row["id"].endswith("parity"):
                    compare_planted(audit, row)
                    sample["runC0_planted"] += 1
                continue
            if source == "runC0" and not select_control(row):
                continue
            if smoke and not smoke_row(source, row):
                continue
            law = Law(**row["law"])
            run = grow(row["stars"], law, rounds=4 if law.take == "J-EACH-PART" else 7)
            compare_rosters(audit, row, run)
            sample[source] += 1
            no_birth_rounds = [t for t, step in run.steps.items() if not step.births]
            if no_birth_rounds:
                no_births[row["id"]] = no_birth_rounds
            strict_pair = next((pair for pair in row["pairs"] if pair["strict"]), None)
            start_pair = next((pair for pair in row["pairs"] if not pair["strict"]), None)
            for pair in (strict_pair, start_pair):
                if pair is not None:
                    result = compare_barred(audit, row, run, law, pair)
                    bar_sample.append([row["id"], pair["s"], pair["X"], pair["Y"]])
                    if result:
                        evidence.append(result)

    cache = {}
    for row in records("runN2"):
        if smoke and not smoke_row("runN2", row):
            continue
        compare_renaming(audit, row, cache)
        sample["runN2_reference" if row["renaming"] in {"registered", "n000"} else "runN2"] += 1

    return dict(
        coverage=dict(smoke=smoke, run_A_items=dict(sample), barred_rows=bar_sample,
                      N2="Exact holder-incidence and bar correspondence at each round under an induced map of births.",
                      comparison="Archive counts and concrete memberships, provenance, listings and reduced courses where stored.",
                      not_run=["C0 runs outside the FLOOR1 strata on the two-knot, three-knot and five-knot ring starts, except both planted runs.",
                               "Barred branches beyond the first strict and first other meeting in each unrenamed item.",
                               "N2 barred branches and reduced courses, and independent knot tests and lasting reruns.",
                               "Comparison G with the earlier growth implementation.",
                               "P2 guard scaling, for which no archived item was eligible."],
                      run=["ulimit -v 2097152", ".venv/bin/python -B research/WHAT-A-BIRTH-CARRIES-20261125-001/referee-R1/b_replay.py"]),
        counts=dict(audit.checked), mismatches=dict(audit.mismatches), mismatch_examples=dict(audit.examples),
        owing_birth_records=evidence, no_birth_rounds_read=no_births,
        wall_seconds=round(perf_counter() - started, 3),
    )


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--smoke", action="store_true")
    args = cli.parse_args()
    print(json.dumps(main(args.smoke), indent=2, sort_keys=True))
