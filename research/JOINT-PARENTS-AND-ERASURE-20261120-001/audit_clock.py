"""Verify the paid passages used by the two member readings.

The initial end is specified by the earlier marked frames and the frozen
ordinary witness edit. We build both initial rosters without the study's
implementation. A member word is then verified bottom up. This checks that
every interval along its two genuine parent chains is paid, including those
containing a ternary first birth. A geometric short path alone cannot do that.
Frontier additions check the grants independently. The proof gives the decoder
using all physically compatible readings.
"""
import importlib.util
import gzip
import json
import sys
from collections import Counter, defaultdict
from itertools import combinations, pairwise
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parents[2]
PREV = ROOT / "research/SIGN-RECORDS-AND-RECEIVER-TICKS-20261120-001/check_receiver_turns.py"
spec = importlib.util.spec_from_file_location("previous_clock_reads", PREV)
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
FRAME = (("v","r1"),("r1","r2"),("r2","r3"),("r3","v"),("v","s"),("t","v"),
         ("s","b0"),("t","b0"),("s","b1"),("b1","t"),("t","b2"),("b2","s"))
CALENDAR = ("b0", "t", "v", "r1", "r2", "r3", "v", "r1", "r2", "r3", "v", "s")


def groups(held):
    network = nx.Graph()
    for row in held:
        network.add_nodes_from(row)
        network.add_edges_from(combinations(row, 2))
    large = [frozenset(c) for c in nx.find_cliques(network)
             if len(c) >= 3 and not any(set(c) <= w for w in held)]
    covered = {frozenset(p) for g in large for p in combinations(g, 2)}
    pairs = [frozenset(p) for p in network.edges if frozenset(p) not in covered]
    return large + pairs


def parent_rosters(arm, gate, reserve):
    middle = prior.middle(arm, 32)
    network = nx.Graph(middle)
    for prefix in ("R", "S"):
        network.add_edges_from((prefix+a, prefix+b) for a, b in FRAME)
    network.add_edges_from([("Rr1","Sb2"),("Rb2","a"),("b","Sb2")])
    held = [frozenset(p) for p in network.edges]
    locations = ([15] if len(gate) == 1 else [20, 24]) if gate else []
    for j, mode in zip(locations, gate):
        u, v, w = f"c{j}", f"c{j+1}", f"w{j}"
        for donor in (u, v):
            prior.meet(middle, donor, w)
            network.add_edge(donor, w)
        if mode == "C":
            held.remove(frozenset((u,v)))
            held.append(frozenset((u,v,w)))
        else:
            held.extend([frozenset((u,w)), frozenset((v,w))])
    first = groups(held)
    costs = Counter(d for parents in first for d in parents)
    for d, h in network.degree:
        extra = (2 if d == reserve else 0) + h - costs[d]
        assert extra >= 0
        first.extend([frozenset((d,))] * extra)
    siblings = defaultdict(set)
    pair_id = {}
    for i, parents in enumerate(first):
        for d in parents:
            siblings[d].add(i)
        for pair in combinations(parents, 2):
            key = frozenset(pair)
            assert key not in pair_id
            pair_id[key] = i
    second = groups(siblings.values())
    covered2 = {frozenset(p) for g in second for p in combinations(g, 2)}
    return middle, first, pair_id, set(second), covered2


def paid_word(donors, first, pair_id, second, covered2):
    ids = [pair_id[frozenset(p)] for p in pairwise(donors)]
    # At lengths one and two these are the literal ordinary parent sets.
    ancestry = [dict(enumerate(first))]
    levels = 1
    while len(ids) > 1:
        new, intern, asc = [], {}, {}
        parents = ancestry[-1]
        for x, y in pairwise(ids):
            pair = frozenset((x,y))
            assert len(pair) == 2
            if levels == 1:
                assert pair in second, ("no genuine two-parent continuation", pair)
            else:
                left, right = parents[x], parents[y]
                overlap = left & right
                assert len(overlap) == 1
                u, = left - overlap
                v, = right - overlap
                if levels == 2:
                    assert frozenset((u,v)) not in covered2
                else:
                    assert not ancestry[-2][u] & ancestry[-2][v]
                # Every third co-candidate outside the common parent's roster
                # must be a child of both u and v. The above excludes that.
            if pair not in intern:
                index = len(intern)
                intern[pair] = index
                asc[index] = pair
            new.append(intern[pair])
        ancestry.append(asc)
        ids = new
        levels += 1
    return levels


def count_extensions(word, incident, pair_id, specials):
    """Enumerate unused original services for each distinct occurrence."""
    available = [set(incident[v]) for v in word]
    for i, (u, v) in enumerate(pairwise(word)):
        to_v = pair_id[frozenset((u,v))]
        available[i].remove(to_v)
        available[i+1].remove(to_v)
        gate = specials.get(frozenset((u,v)))
        if gate is None:
            continue
        third, mode = gate
        if mode == "S":
            # The actual first child contains this third parent as well.
            available.append(set(incident[third]) - {to_v})
        else:
            # Both first children toward the same third occurrence extend
            # the current support by the very same new point.
            alternate = pair_id[frozenset((third,v))]
            available[i+1].remove(alternate)
    return sum(map(len, available))


def payment_vector(word, incident, entries, specials, m):
    center = len(word)//2
    sent = tuple("S"+v for v in prior.sent_word(m))
    windows = {"receipt":word, "receiver_internal_parent":word[:-1],
               "receiver_incoming_parent":word[1:],
               "receiver_launch":word[center-m//2:center+(m+1)//2], "send":sent,
               "send_other_end_deletion":sent[:-1], "send_outside_end_deletion":sent[1:]}
    return {key:count_extensions(w,incident,entries,specials) for key,w in windows.items()}


def compare_archive(result):
    evidence = ROOT/"artifacts"/(Path(__file__).resolve().parent.name+"A")
    archive, = evidence.glob("*/clock.json.gz")
    with gzip.open(archive,"rt") as stream:
        cases = json.load(stream)["cases"]
    compared = registered = grants = 0
    for case in cases:
        arm = "active" if case["lifetime"]=="active" else "matched"
        gate, reserve = case["gates"], case["reserve"]
        panel = result["/".join((arm,gate or "unchanged",reserve or "baseline"))]
        for theirs, ours in (("extended","admits_three"),("hereditary","requires_two")):
            for send in case["readers"][theirs]:
                compared += 1
                expected = panel[ours]
                assert bool(send["minimizers"]) == expected["registered"]
                if not expected["registered"]:
                    continue
                row = expected["sends"][str(send["m"])]
                assert len(send["minimizers"]) == row["paid_words"]
                for word in send["minimizers"]:
                    assert (word["size"], word["ticks_after_send"], word["ticks_from_origin"]) == (
                        row["size"], row["since_send"], row["since_origin"])
                    assert word["price_vector"] in row["grant_vectors"]
                    assert len(word["route"])-1 == expected["passage"]
                    registered += 1
                    grants += len(word["price_vector"])
    print(f"{compared} arm/reader/send cases, {registered} paid registrations, {grants} individual endpoint grants matched.")


def panel(arm, gate, reserve):
    middle, first, entries, second, covered2 = parent_rosters(arm, gate, reserve)
    incident = defaultdict(set)
    for j, group in enumerate(first):
        for d in group:
            incident[d].add(j)
    loc = ([15] if len(gate)==1 else [20,24]) if gate else []
    specials = {frozenset((f"c{j}", f"c{j+1}")):(f"w{j}", mode)
                for j,mode in zip(loc,gate)}
    routes = list(prior.simple_paths(middle, "a", "b"))
    cases = {}
    for reader in ("admits_three", "requires_two"):
        allowed = [p for p in routes if all(len(first[entries[frozenset(pair)]]) == 2
                   or reader == "admits_three" for pair in pairwise(p))]
        if not allowed:
            cases[reader] = {"registered": False, "reason":"no permitted port passage"}
            continue
        distance = min(len(p) for p in allowed)-1
        paths = [p for p in allowed if len(p)-1 == distance]
        item = {"registered":True, "passage":distance, "sends":{}}
        for m in (32,48,64,80):
            endings = list(prior.sender_endings(prior.sent_word(m)))
            need = min(map(len, endings))
            suffixes = [w for w in endings if len(w) == need]
            verified = set()
            for path in paths:
                for tail in suffixes:
                    right = ("Rt","Rb2") + path + tuple("S"+d for d in tail)
                    left = tuple("R"+CALENDAR[j % 12] for j in range(-len(right), 0))
                    word = left+("Rb1",)+right
                    levels = paid_word(word,first,entries,second,covered2)
                    assert levels == len(word)-1
                    verified.add(word)
            vectors = [payment_vector(w,incident,entries,specials,m) for w in sorted(verified)]
            size, = {len(w) for w in verified}
            ticks = prior.receiver_ticks(size)
            item["sends"][str(m)] = {"size":size, "since_send":sum(t > m for t in ticks),
                                   "since_origin":len(ticks), "paid_words":len(verified), "grant_vectors":vectors}
        cases[reader] = item
    return cases


if __name__ == "__main__":
    result = {}
    for arm in ("active", "matched"):
        for gate in ("", "C", "S", "CC", "CS", "SC", "SS"):
            reserves = (None, "c17", "c54") if gate in ("C","S") else (None,)
            for reserve in reserves:
                key = (arm, gate or "unchanged", reserve or "baseline")
                result["/".join(key)] = panel(arm, gate, reserve)
    if sys.argv[1:] == ["--check"]:
        compare_archive(result)
    elif not sys.argv[1:]:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        raise SystemExit("Usage: audit_clock.py [--check]")
