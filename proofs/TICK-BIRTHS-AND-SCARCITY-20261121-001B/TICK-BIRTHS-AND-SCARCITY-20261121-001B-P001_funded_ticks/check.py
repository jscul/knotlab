"""Verify the stated counts and every retained unguarded trace from physical supports."""
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations
from math import comb
from pathlib import Path
import json

import networkx as nx


HERE = Path(__file__).resolve().parent
ID = HERE.parent.name
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / ID / (ID + "-E001_serial")
ARMS = {"alone": "bare", "same_continuation": "attachment_3", "other_continuation": "attachment_2"}
PHASES = {
    "bare": [({0}, None), (set(), None)],
    "attachment_3": [({0}, 2), (set(), None)],
    "attachment_2": [({0}, None), (set(), 1)],
    "supply_only": [({0, 1, 2}, None), (set(), None)],
}


def parse(stars, nsource):
    owners = defaultdict(list)
    for j, row in enumerate(stars):
        assert len(row) == len(set(row))
        for x in row:
            owners[x].append(j)
    neighbours = [set() for _ in stars]
    loose = defaultdict(set)
    for d, at in owners.items():
        if len(at) == 1:
            loose[at[0]].add(d)
        else:
            a, b = at
            neighbours[a].add(b)
            neighbours[b].add(a)
    parents = {j: tuple(sorted(i for i in neighbours[j] if i < j)) for j in range(nsource, len(stars))}
    return neighbours, loose, parents


def groups(neighbours, living):
    witnesses = [row.intersection(living) for row in neighbours]
    graph = nx.Graph()
    graph.add_nodes_from(living)
    for witness in witnesses:
        graph.add_edges_from(combinations(witness, 2))
    large = {tuple(sorted(clique)) for clique in nx.find_cliques(graph)
             if len(clique) >= 3 and not any(set(clique).issubset(w) for w in witnesses)}
    pairs = {tuple(sorted(pair)) for pair in graph.edges}
    return large | {p for p in pairs if not any(set(p).issubset(g) for g in large)}


def validate_write(stars, nsource, event, policy, target=None):
    neighbours, loose, earlier = parse(stars, nsource)
    q = tuple(event["parents"])
    assert q == tuple(sorted(set(q)))
    built = [set(row) for row in earlier.values()]
    multi = {g for g in groups(neighbours, set(loose)) if not any(set(g).issubset(h) for h in built)}
    spend = Counter(x for g in multi for x in g)
    unary = {(i,) for i, ds in loose.items() if len(ds) > spend[i]}
    enabled = multi if policy == "joins_first" and multi else multi | unary
    assert q in enabled, "the recorded parent set is not admitted"
    if target is not None:
        assert event["target_admitted_before"] == (target in enabled)
    inputs = event["consumed_slots"]
    assert len(inputs) == len(q) and all(d in loose[j] for j, d in zip(q, inputs))
    assert len(inputs) < sum(map(len, loose.values()))
    child = len(stars)
    assert event["child"] == child
    p_stars = stars + [list(inputs)]
    temporary, remain, _ = parse(p_stars, nsource)
    demand = {g for g in groups(temporary, set(remain) | {child}) if child in g}
    assert demand == set(map(tuple, event["current_demand"]))
    f = event["fresh"]
    assert len(f) == max(len(demand), 3-len(q), 1)
    previous = set().union(*stars)
    assert not previous.intersection(f) and len(set(f)) == len(f)
    assert event["pre_total_loose"] == sum(map(len, loose.values()))
    assert event["post_total_loose"] == sum(map(len, loose.values())) - len(q) + len(f)
    return stars + [inputs + f]


def direct_match(reference_stars, target, observed, nsource):
    _, _, req = parse(reference_stars, nsource)
    needed = set()
    todo = [target]
    while todo:
        current = todo.pop()
        if current >= nsource and current not in needed:
            needed.add(current)
            todo.extend(req[current])
    _, _, actual = parse(observed, nsource)
    indexed = defaultdict(list)
    for j, ps in actual.items():
        indexed[ps].append(j)
    maps = [{j: j for j in range(nsource)}]
    for role in sorted(needed):
        new_maps = []
        for m in maps:
            ps = tuple(sorted(m[p] for p in req[role]))
            for j in indexed[ps]:
                if j not in m.values():
                    new_maps.append({**m, role: j})
        maps = new_maps
    return [m[target] for m in maps]


def impossible_required_role(reference, goal, observed, nsource):
    """A uniquely irreplaceable parent may have permanently spent its last slot."""
    _, _, needed = parse(reference, nsource)
    _, loose, actual = parse(observed, nsource)
    available = defaultdict(list)
    for child, ps in actual.items():
        available[ps].append(child)

    def settle(role):
        if role < nsource:
            return role, None
        inputs = []
        for old in needed[role]:
            fixed, loss = settle(old)
            if loss:
                return None, loss
            if fixed is None:
                return None, None
            inputs.append(fixed)
        parents = tuple(sorted(inputs))
        matches = available.get(parents, [])
        if len(matches) == 1:
            # Subsequent exact multiparent copies are forbidden by the physical
            # common-child filter; a second unary needs a remaining slot.
            if len(parents) >= 2 or not loose[parents[0]]:
                return matches[0], None
        if not matches and any(not loose[j] for j in parents):
            return None, {"required_ordinary_role": role, "unique_actual_parents": list(parents),
                          "remaining_slots": [len(loose[i]) for i in parents]}
        return None, None

    return settle(goal)[1]


def binomial_counts(arm):
    counts = []
    for age in range(1, 11):
        value = 0
        for marks, host in PHASES[arm]:
            for phase in range(4):
                for run in range(1, age + 2):
                    options = sum((phase+k) % 4 in marks for k in range(run))
                    options += sum((phase+k) % 4 == host for k in range(run+1))
                    choices = age+1-run
                    if choices <= options:
                        value += comb(options, choices)
        counts.append(value)
    return counts


def main():
    guarded = json.loads((OUT/"receipt.json").read_text())
    raw = json.loads((OUT/"raw.json").read_text())
    n_writes = n_firings = n_losses = n_cold = 0
    cold_losses = {}
    arities = set()
    for law, group in guarded["laws"].items():
        for name in PHASES:
            actual = [group[name]["depths"][str(a)]["births"] for a in range(1, 11)]
            assert actual == binomial_counts(name)
        for raw_arm, guard_arm in ARMS.items():
            g = group[guard_arm]
            rr = raw["sources"][raw_arm][law]
            ns = len(g["source"])
            assert g["source"] == rr["source"]
            for age in (6, 10):
                j = (age-2)//4
                warm = rr["warm"][str(age)]
                target = tuple(warm["physical_target_parents"])
                win = g["tick_windows"][str(age)]
                assert list(target) == win["parents"]
                completed = g["complete_cuts"][str(age)]["supports"]
                pre = g["complete_cuts"][str(age-1)]["supports"]
                t = win["tick"]
                _, loose, _ = parse(pre, ns)
                h = 2*j+2 if guard_arm == "attachment_3" else j+2
                assert all(len(loose[u]) == h for u in target)
                for policy, c in warm["policies"].items():
                    event = c["immediate_unique_firing"]
                    after = validate_write(pre, ns, event, policy, target)
                    assert direct_match(completed, t, after, ns) == [len(pre)]
                    n_firings += 1
                    n_writes += 1
                    arities.add(len(after[-1]))
                    for variant in ("consumer_donor_only", "any_donor_plus_one_intervening"):
                        w = c.get(variant, {})
                        if w.get("status") != "permanent_loss":
                            continue
                        stars = pre
                        for step in w["trace"]:
                            stars = validate_write(stars, ns, step, policy, target)
                            arities.add(len(stars[-1]))
                            n_writes += 1
                        _, loose, parents = parse(stars, ns)
                        cert = w["certificate"]
                        assert [u for u in target if not loose[u]] == cert["exhausted_target_donors"]
                        assert [x for x, ps in parents.items()
                                if set(target).issubset(ps)] == cert["earlier_children_using_both"]
                        assert cert["exhausted_target_donors"] or cert["earlier_children_using_both"]
                        assert direct_match(completed, t, stars, ns) == []
                        n_losses += 1
            for policy, ties in rr["cold"].items():
                for tie, cell in ties.items():
                    stars = g["source"]
                    for step in cell["trace"]:
                        stars = validate_write(stars, ns, step, policy)
                        arities.add(len(stars[-1]))
                        n_writes += 1
                    reference = g["complete_cuts"]["6"]["supports"]
                    role = g["tick_windows"]["6"]["tick"]
                    assert direct_match(reference, role, stars, ns) == cell["full_realizations"]
                    certificate = impossible_required_role(reference, role, stars, ns)
                    if certificate:
                        cold_losses[f"{law}/{raw_arm}/{policy}/{tie}"] = certificate
                    n_cold += 1
    def normalized_parent_sequence(branch):
        ns = len(branch["source"])
        trace = branch["cold"]["unrestricted"]["ascending"]["trace"]
        return [tuple(("source", x) if x < ns else ("birth", x-ns+1) for x in row["parents"])
                for row in trace]
    for law in ("parity","nae"):
        cases = [raw["sources"][key][law] for key in ARMS]
        sequences = [normalized_parent_sequence(branch) for branch in cases]
        assert sequences[0] == sequences[1][:14] == sequences[2]
        kept = cases[1]["cold"]["unrestricted"]["ascending"]["trace"]
        assert [len(x) for x in kept[14]["eligible_slots_at_parents"]] == [1, 3]
        assert all(8 not in ps for step in kept for ps in step["source_ancestry_of_parents"])
    assert len(cold_losses) == 4
    assert all(c["remaining_slots"] == [0, 0] for c in cold_losses.values())
    # Change the mathematical incidence in a loss witness. The exact pair is
    # no longer admissible at the last write.
    rr=raw["sources"]["same_continuation"]["parity"]["warm"]["6"]
    old=guarded["laws"]["parity"]["attachment_3"]["complete_cuts"]["5"]["supports"]
    steps=rr["policies"]["joins_first"]["any_donor_plus_one_intervening"]["trace"]
    for step in steps[:-1]:
        old=validate_write(old, 9, step, "joins_first")
    wrong={**steps[-1], "parents": rr["physical_target_parents"]}
    try:
        validate_write(old, 9, wrong, "joins_first")
    except AssertionError as exc:
        assert str(exc) == "the recorded parent set is not admitted"
    else:
        raise AssertionError("wrong two-parent replacement passed")
    print(json.dumps({"independent_checked_raw_writes": n_writes, "warm_immediate_turns": n_firings,
                      "certificates_confirmed": n_losses, "cold_terminal_readings": n_cold,
                      "from_original_permanent_certificates": cold_losses,
                      "physical_arities_in_retained_raw_traces": sorted(arities),
                      "wrong_parent_control_rejected": True, "independent_level_counts_per_law": 40,
                      "raw_sha256": sha256((OUT/"raw.json").read_bytes()).hexdigest(),
                      "guarded_sha256": sha256((OUT/"receipt.json").read_bytes()).hexdigest()}, indent=2))


if __name__ == "__main__":
    main()
