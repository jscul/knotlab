"""Find a matched last-slot loss on the registered eight-knot raw clock."""

from argparse import ArgumentParser
from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import json
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRIOR = "TICK-BIRTHS-AND-SCARCITY-20261121-001B"
PRIOR_RUN = PRIOR + "-E001_serial"
PRIOR_ARTIFACTS = ROOT / "artifacts" / PRIOR / PRIOR_RUN
DESIGN = ROOT / "research" / HERE.parent.name / "design.md"
DESIGN_SHA256 = "274a638190d841e7ae1ac91f389178ddabadcf2242c18994e6ff44b825b452e1"
LAWS = ("parity", "nae")
TIES = ("ascending", "descending")
ATTACHED = 8
PREP_LIMITS = {2: 600, 3: 600}
VARIANT_LIMIT = 300
DISJOINT_COMPLETION_LIMIT = 512

sys.path.insert(0, str(ROOT / "experiments" / PRIOR / PRIOR_RUN))
import raw as prior


@dataclass(frozen=True)
class History:
    stars: tuple
    events: tuple = ()


@dataclass(frozen=True)
class Reference:
    roles: dict
    levels: dict
    order: tuple
    goal: int
    recorded: dict

    @classmethod
    def from_receipt(cls, receipt):
        cell = receipt["sources"]["same_continuation"]["parity"]
        trace = cell["cold"]["unrestricted"]["ascending"]["trace"]
        assert len(trace) == 20
        actual_roles = {i: i for i in range(len(cell["source"]))}
        roles, levels, order = {}, {}, []
        for event in trace:
            child, role = event["child"], event["reference_role"]
            parents = tuple(sorted(actual_roles[p] for p in event["parents"]))
            roles[role] = parents, event["reference_fresh"]
            levels[role] = event["reference_parent_depth"]
            order.append(role)
            actual_roles[child] = role
        goal = order[-1]
        assert set(prior.needed_roles(goal, roles)) == set(order)
        assert [roles[role][0] for role in order if len(roles[role][0]) == 1] == [(0,)]
        return cls(roles, levels, tuple(order), goal, cell)


class Present:
    """Read the physical prefix, pending roles, and permanently fixed roles."""

    def __init__(self, frame, reference):
        self.stage, self.loose, self.children, self.ancestry, self.by_parents, self.multi, self.unary = (
            prior.facts(frame.stars, ATTACHED + 1)
        )
        self.parents = {child: ps for ps, children in self.by_parents.items() for child in children}
        self.pool = set(self.multi + self.unary)
        self.current = {i: i for i in range(ATTACHED + 1)}
        self.fixed = self.current.copy()
        self.pending = {}
        for role in reference.order:
            given, _ = reference.roles[role]
            if all(p in self.current for p in given):
                ps = tuple(sorted(self.current[p] for p in given))
                matches = self.by_parents.get(ps, ())
                if len(matches) == 1 and matches[0] not in self.current.values():
                    self.current[role] = matches[0]
                    if all(p in self.fixed for p in given) and (len(ps) > 1 or not self.loose.get(ps[0])):
                        self.fixed[role] = matches[0]
                elif not matches and ps in self.pool:
                    self.pending[role] = ps

    def consumer_parent(self, parents):
        return next((p for p in parents if ATTACHED in self.ancestry[p]), None)

    def older_common_child(self, parents):
        return set.intersection(*(self.children.get(p, set()) for p in parents))

    def outside_chain(self, parent):
        chain = [parent]
        while chain[-1] != ATTACHED:
            chain.append(next(p for p in self.parents[chain[-1]] if ATTACHED in self.ancestry[p]))
        return chain


def write(history, parents, law):
    _, _, _, _, _, multi, unary = prior.facts(history.stars, ATTACHED + 1)
    assert parents in prior.pool(multi, unary, "unrestricted")
    next_stars, detail = prior.apply(history.stars, ATTACHED + 1, parents, law)
    copied = {**detail, "also_passes_joins_first": parents in prior.pool(multi, unary, "joins_first")}
    return History(next_stars, (*history.events, copied))


def replay(source, parent_lists, law):
    history = History(source)
    for parents in parent_lists:
        history = write(history, tuple(parents), law)
    return history


def target_read(history, reference):
    return prior.realizations(history.stars, ATTACHED + 1, reference.goal, reference.roles, sorted(reference.order))


def preferred(present, reference, tie):
    if not present.pending:
        return None
    possible = [(reference.levels[role], ps, role) for role, ps in present.pending.items()]
    latest = max(age for age, _, _ in possible)
    pick = min if tie == "ascending" else max
    return pick(row for row in possible if row[0] == latest)[1]


def trajectory(history, reference, law, tie):
    """Walk only still-needed true-parent roles from a physical prefix."""
    while True:
        present = Present(history, reference)
        yield history, present
        if reference.goal in present.current:
            return
        parents = preferred(present, reference, tie)
        if parents is None:
            return
        history = write(history, parents, law)


def finish_trial(history, reference, law, tie):
    for history, _ in trajectory(history, reference, law, tie):
        pass
    return history, target_read(history, reference)


def finish(history, reference, law, tie):
    result, matches = finish_trial(history, reference, law, tie)
    return result if len(matches) == 1 else None


def candidates(present, reference):
    ranked = sorted(present.pending, key=lambda role: (role != reference.goal, -reference.levels[role], role))
    for role in ranked:
        if not all(p in present.fixed for p in reference.roles[role][0]):
            continue
        required = present.pending[role]
        if len(required) < 2:
            # A unary with one loose distinction permits no multipart at that donor.
            continue
        assert not present.older_common_child(required)
        for donor in required:
            if len(present.loose[donor]) != 1 or ATTACHED in present.ancestry[donor]:
                continue
            for rival in sorted(present.multi):
                outside = present.consumer_parent(rival)
                if donor in rival and outside is not None and not set(required) <= set(rival):
                    yield role, required, donor, rival, outside


def full_joins_first(history):
    return all(event["also_passes_joins_first"] for event in history.events)


def certify_fork(prefix, candidate, reference, law, tie, control=None):
    """Keep only a physical lost role paired with a full unique control turn."""
    role, required, donor, rival, outside = candidate
    present = Present(prefix, reference)
    assert candidate in candidates(present, reference)
    assert not target_read(prefix, reference)
    assert not present.by_parents.get(required) and not present.older_common_child(required)
    assert present.pending[role] == tuple(sorted(present.fixed[p] for p in reference.roles[role][0]))
    slot, = present.loose[donor]
    cut = len(prefix.events)
    if control is None:
        control = finish(write(prefix, required, law), reference, law, tie)
        if control is None:
            return None
    tick, = target_read(control, reference)
    treatment = write(prefix, rival, law)
    after = Present(treatment, reference)
    assert not after.loose.get(donor) and not after.older_common_child(required)
    assert not after.by_parents.get(required) and not target_read(treatment, reference)
    for event in (control.events[cut], treatment.events[-1]):
        assert event["consumed_slots"][event["parents"].index(donor)] == slot
    assert control.events[:cut] == treatment.events[:cut] == prefix.events
    assert control.events[cut]["parents"] == required
    assert treatment.events[-1]["parents"] == rival
    parents = {child: present.parents[child] for child in sorted(present.children.get(donor, ()))}
    fork = {"role": role, "required_parents": required, "donor": donor, "slot": slot,
            "donor_loose_before": present.loose[donor], "donor_loose_after_treatment": after.loose.get(donor, ()),
            "old_children_at_donor": parents, "rival_parents": rival,
            "rival_omits": sorted(set(required) - set(rival)),
            "outside_chain": present.outside_chain(outside), "fixed_roles": present.fixed,
            "is_tick": role == reference.goal,
            "older_shared_child_before": sorted(present.older_common_child(required)),
            "older_shared_child_after_treatment": sorted(after.older_common_child(required)),
            "fork_joins_first_admits_both": all(s in prior.pool(present.multi, present.unary, "joins_first")
                                               for s in (required, rival))}
    tick_birth = tick + 1 - (ATTACHED + 1)
    assert tick_birth == len(control.events)
    counts = {"control_tick_birth": tick_birth, "irreversible_loss_birth": cut + 1,
              "at_fork_write": {"control_strict": 0, "control_inclusive": int(role == reference.goal),
                                "treatment_strict": 0, "treatment_inclusive": 0},
              "at_control_tick": {"control_strict": 0, "control_inclusive": 1,
                                  "treatment_strict": 0, "treatment_inclusive": 0}}
    return {"common": prefix.events, "fork": fork, "control": control.events[cut:],
            "treatment": treatment.events[cut:], "control_marked_realization": [tick],
            "unrestricted_weak_fair_extension": True,
            "joins_first_full_histories": {"control": full_joins_first(control),
                                            "treatment": full_joins_first(treatment)},
            "counts": counts, "positive_tie_order": tie}


def scan(prefix, present, reference, law, counts):
    if reference.goal in present.current:
        return None
    counts["prefixes_examined"] += 1
    counts["available_roles_examined"] += len(present.pending)
    counts["available_raw_groups_examined"] += len(present.pool)
    for candidate in candidates(present, reference):
        counts["matched_forks_tested"] += 1
        for tie in TIES:
            result = certify_fork(prefix, candidate, reference, law, tie)
            if result is not None:
                return result
            counts["failed_control_completions"] += 1
    return None


def preliminary_options(prefix, present, reference):
    """Prefer spending a two-slot reserve, then forming an outside co-parent."""
    needed = {present.current[p] for role in reference.order if role not in present.current
              for p in reference.roles[role][0] if p in present.current and present.loose.get(present.current[p])}
    two_slots = {donor for donor in needed if len(present.loose[donor]) == 2}
    for group in sorted(present.pool - set(present.pending.values())):
        spends_reserve = bool(two_slots.intersection(group))
        potential_witness = present.consumer_parent(group) is not None and any(
            set(group).intersection(present.stage.nbr[d]) for d in needed
        )
        rank = 0 if spends_reserve else 1 if potential_witness else 2
        yield rank, prefix, group


def prepared_search(options, reference, law, depth, limit):
    counts = Counter()
    previous = set()
    new_options = []
    ranked = sorted(options, key=lambda row: (row[0], -len(row[1].events), row[2], row[1].stars))
    for _, prefix, group in ranked:
        if (prefix.stars, group) in previous:
            continue
        if limit is not None and counts["preparations_tested"] >= limit:
            counts["censored"] = True
            break
        previous.add((prefix.stars, group))
        counts["preparations_tested"] += 1
        first = write(prefix, group, law)
        reached = set()
        for tie in TIES:
            for current, now in trajectory(first, reference, law, tie):
                if current.stars in reached:
                    continue
                reached.add(current.stars)
                result = scan(current, now, reference, law, counts)
                if result is not None:
                    return result, dict(counts), new_options
                if depth < 3 and reference.goal not in now.current:
                    new_options.extend(preliminary_options(current, now, reference))
    return None, dict(counts), new_options


def prepared_source(host, omissions):
    base, _ = prior.rings.attached_ring(8, (0,))
    source, _ = prior.rings.attached_ring(8, (0,), host)
    source = list(source)
    for side in omissions:
        step = -1 if side == "before" else 1
        old = (host + step) % 8
        extra, = set(source[old]) - set(base[old])
        source[old] = tuple(d for d in source[old] if d != extra)
    return tuple(source)


def source_funding(source, law):
    from end_operator import from_stars, step

    prior.physical.certify_source(source, law)
    plan = step(from_stars(source), law)
    return {"status": plan.status, "shortages": plan.shortages, "funded_births": len(plan.parents)}


def search(source, reference, primary_only):
    law = "parity"
    known = []
    canonical = History(source)
    for archived in reference.recorded["cold"]["unrestricted"]["ascending"]["trace"]:
        known.append((canonical, Present(canonical, reference)))
        canonical = write(canonical, tuple(archived["parents"]), law)
        assert all(archived[k] == json.loads(json.dumps(v)) for k, v in canonical.events[-1].items())
    assert target_read(canonical, reference) == [len(source) + 19]
    counts = Counter()
    options = []
    stages = []
    for prefix, now in reversed(known):
        result = scan(prefix, now, reference, law, counts)
        if result is not None:
            return source, result, [{"phase": "canonical", **counts}], 3, ()
        options.extend(preliminary_options(prefix, now, reference))
    stages.append({"phase": "canonical", **counts})
    for depth in (1, 2, 3):
        result, progress, options = prepared_search(options, reference, law, depth, PREP_LIMITS.get(depth))
        stages.append({"phase": "shared_preparations", "count": depth, **progress})
        if result is not None:
            return source, result, stages, 3, ()
        if primary_only:
            return source, None, stages, 3, ()

    for omissions in ((), ("before",), ("after",), ("before", "after")):
        for host in range(5):
            if host == 3 and not omissions:
                continue
            variant = prepared_source(host, omissions)
            funding = {law: source_funding(variant, law) for law in LAWS}
            progress = Counter()
            variants = []
            for tie in TIES:
                for prefix, now in trajectory(History(variant), reference, law, tie):
                    result = scan(prefix, now, reference, law, progress)
                    if result is not None:
                        stages.append({"phase": "variant", "host": host, "omissions": omissions,
                                       "funding": funding, **progress})
                        return variant, result, stages, host, omissions
                    if reference.goal not in now.current:
                        variants.extend(preliminary_options(prefix, now, reference))
            result, counts, _ = prepared_search(variants, reference, law, 3, VARIANT_LIMIT)
            stages.append({"phase": "variant", "host": host, "omissions": omissions,
                           "funding": funding, **progress, "preparatory_search": counts})
            if result is not None:
                return variant, result, stages, host, omissions
    return source, None, stages, 3, ()


def past_rival(receipt, law):
    target = receipt["sources"]["same_continuation"][law]["warm"]["6"]
    target_parents = tuple(target["physical_target_parents"])
    arm = target["policies"]["unrestricted"]["any_donor_plus_one_intervening"]
    archived_guarded = json.loads((PRIOR_ARTIFACTS / "receipt.json").read_bytes())
    frame = archived_guarded["laws"][law]["attachment_3"]["complete_cuts"]["5"]["supports"]
    prefix = replay(tuple(map(tuple, frame)), (event["parents"] for event in arm["trace"]), law)
    _, loose, children, *_ = prior.facts(prefix.stars, ATTACHED + 1)
    common = sorted(set.intersection(*(children[p] for p in target_parents)))
    assert len(prefix.events) == 4 and common and all(loose[p] for p in target_parents)
    return {"target_parents": target_parents, "trace": prefix.events, "shared_child": common,
            "remaining_target_slots": {p: loose[p] for p in target_parents}, "last_slot": False}


def exhaustions(present, reference):
    exhausted = []
    for role, (given, _) in reference.roles.items():
        if not all(parent in present.fixed for parent in given):
            continue
        parents = tuple(sorted(present.fixed[parent] for parent in given))
        zero = [p for p in parents if not present.loose.get(p)]
        if zero and not present.by_parents.get(parents):
            exhausted.append({"role": role, "required_parents": parents, "empty": zero})
    return exhausted


def disjoint_completion(first, base, required, reference, law):
    trials = []
    for required_first in (True, False):
        if required_first and required not in Present(first, reference).pool:
            continue
        start = write(first, required, law) if required_first else first
        for tie in TIES:
            end, matches = finish_trial(start, reference, law, tie)
            trial = {"required_immediately_after": required_first, "tie": tie,
                     "writes": end.events[base:], "full_realizations": matches,
                     "permanent_exhaustions": exhaustions(Present(end, reference), reference)}
            trials.append(trial)
            if len(matches) == 1:
                return {"status": "marked turn completed", "writes": end.events[base:],
                        "full_realizations": matches, "priority_trials": trials}

    visited = set()
    pending = [first]
    while pending and len(visited) < DISJOINT_COMPLETION_LIMIT:
        history = pending.pop()
        if history.stars in visited:
            continue
        visited.add(history.stars)
        now = Present(history, reference)
        if reference.goal in now.current:
            matches = target_read(history, reference)
            if len(matches) == 1:
                return {"status": "marked turn completed", "writes": history.events[base:],
                        "full_realizations": matches, "priority_trials": trials, "other_orders_visited": len(visited)}
        if not exhaustions(now, reference):
            for role in sorted(now.pending, key=lambda r: (reference.levels[r], now.pending[r], r)):
                pending.append(write(history, now.pending[role], law))
    return {"status": "censored" if pending else "no ancestry-only order completed",
            "priority_trials": trials, "other_orders_visited": len(visited)}


def controls(prefix, witness, control, reference, law):
    fork = witness["fork"]
    rival = fork["rival_parents"]
    after = Present(control, reference)
    late = {"admitted": rival in after.pool,
            "exhausted_parents": [p for p in rival if not after.loose.get(p)],
            "older_common_child": sorted(after.older_common_child(rival))}
    if late["admitted"]:
        late_event = write(control, rival, law)
        late["write"] = late_event.events[-1]
        assert target_read(late_event, reference) == target_read(control, reference)
    else:
        assert fork["donor"] in late["exhausted_parents"]
    before = Present(prefix, reference)
    required = fork["required_parents"]
    options = sorted(group for group in before.multi if len(group) == len(rival)
                     and not set(required).intersection(group) and before.consumer_parent(group) is not None)
    attempts = []
    for group in options:
        first = write(prefix, group, law)
        result = disjoint_completion(first, len(prefix.events), required, reference, law)
        attempts.append({"group": group, "first_write": first.events[-1], **result})
        if result["status"] == "marked turn completed":
            break
    disjoint = {"eligible_equal_cost_groups": options, "attempts": attempts,
                "status": attempts[-1]["status"] if attempts else "unavailable"}
    alternate = next(tie for tie in TIES if tie != witness["positive_tie_order"])
    finish_alt, matches = finish_trial(write(prefix, required, law), reference, law, alternate)
    return {"after_turn": late, "disjoint": disjoint,
            "other_tie_order": {"tie": alternate, "status": "completed" if len(matches) == 1 else "stalled",
                                "writes": finish_alt.events[len(prefix.events):], "full_realizations": matches,
                                "permanent_exhaustions": exhaustions(Present(finish_alt, reference), reference)}}


def confirm(source, witness, reference, law, rename=False):
    if rename:
        ceiling = max(d for star in source for d in star)
        origin = source
        source = tuple(tuple(sorted(ceiling - d for d in row)) for row in source)
    required = tuple(witness["fork"]["required_parents"])
    rival = tuple(witness["fork"]["rival_parents"])
    source_cert = source_funding(source, law)
    common = replay(source, (e["parents"] for e in witness["common"]), law)
    continuation = common
    for event in witness["control"]:
        continuation = write(continuation, tuple(event["parents"]), law)
    now = Present(common, reference)
    relevant = (witness["fork"]["role"], required, witness["fork"]["donor"], rival,
                witness["fork"]["outside_chain"][0])
    assert relevant in candidates(now, reference)
    confirmed = certify_fork(common, relevant, reference, law, witness["positive_tie_order"], control=continuation)
    assert confirmed is not None and confirmed["counts"] == witness["counts"]
    confirmed.update(source=source, first_ordinary_roster=source_cert)
    if rename:
        assert source != origin
        confirmed["source_names_reversed_through"] = ceiling
    else:
        confirmed["controls"] = controls(common, confirmed, continuation, reference, law)
    return confirmed


def run(primary_only):
    assert sha256(DESIGN.read_bytes()).hexdigest() == DESIGN_SHA256
    archived_bytes = (PRIOR_ARTIFACTS / "raw.json").read_bytes()
    archived = json.loads(archived_bytes)
    reference = Reference.from_receipt(archived)
    source = tuple(map(tuple, reference.recorded["source"]))
    source, result, coverage, host, omissions = search(source, reference, primary_only)
    output = {"design_sha256": DESIGN_SHA256, "b262_raw_receipt_sha256": sha256(archived_bytes).hexdigest(),
              "reference": {"roles": reference.roles, "levels": reference.levels,
                            "canonical_order": reference.order, "goal": reference.goal},
              "search": {"coverage": coverage, "more_than_one_preparation_caps": PREP_LIMITS,
                         "one_preparation_variant_cap": VARIANT_LIMIT,
                         "disjoint_control_alternative_order_cap": DISJOINT_COMPLETION_LIMIT},
              "status": "witness" if result else "no witness in checked prefixes",
              "preceding_shared_child_control": {law: past_rival(archived, law) for law in LAWS},
              "source_parameters": {"host": host, "omissions": omissions}}
    if result is not None:
        output["witnesses"] = {law: confirm(source, result, reference, law) for law in LAWS}
        output["reversed_source_names"] = {law: confirm(source, result, reference, law, rename=True) for law in LAWS}
    return output


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--primary-only", action="store_true", help="stop after the one-preparation pass")
    args = parser.parse_args()
    data = json.dumps(run(args.primary_only), sort_keys=True, separators=(",", ":")) + "\n"
    if args.out is None:
        print(data, end="")
    else:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(data)


if __name__ == "__main__":
    main()
