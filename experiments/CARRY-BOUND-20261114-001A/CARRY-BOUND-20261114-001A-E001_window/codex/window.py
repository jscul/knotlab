"""Literal finite-window computation for the frozen CARRY specification.

State = (Boolean main-to-copy relation, identity partition of main+copy ports).
No SAT/unfolding code is used here. Missing certificates never prove growth.
"""
from __future__ import annotations

from itertools import combinations
import math
import json

import inputs
from scope import scope, stratum

paths = inputs.load_paths()
relations = inputs.load_relations()
from limits import LimitReached, Limits
import numpy as np


def canonical_partition(values):
    first = {}
    return tuple(first.setdefault(v, i) for i, v in enumerate(values))


def body_allowed(prep, definition):
    block = prep.flat(definition)
    # Avoid an allocation already known to exceed the prescribed case memory.
    if (1 << block["V"]) * 40 > 2_800_000_000:
        raise LimitReached("memory", "block truth-table allocation exceeds case memory")
    values = np.arange(1 << block["V"], dtype=np.int64)
    ok = np.ones(len(values), dtype=bool)
    for callee, args in block["calls"]:
        states = sum(((values >> v) & 1) << j for j, v in enumerate(args))
        ok &= (paths.L.NAE if callee == "K" else prep.G[callee])[states]
    return block, values[ok]


def start_state(prep, entry_index=None):
    k = prep.k
    if prep.main == prep.S:
        return sum(1 << (8 * t + t) for t in range(8)), tuple(range(k)) + tuple(range(3))
    main = prep.flat(prep.main)
    entries = [j for j, (c, _) in enumerate(main["calls"]) if c == prep.S]
    if entry_index is None:
        if len(entries) != 1:
            raise ValueError("a single wrapper start requires an explicit entry_index")
        entry_index = 0
    selected = entries[entry_index]
    arguments = main["calls"][selected][1]
    # Block.incoming masks with 7; construct main's potentially wider port table explicitly.
    values = np.arange(1 << main["V"], dtype=np.int64)
    ok = np.ones(len(values), dtype=bool)
    for j, (callee, args) in enumerate(main["calls"]):
        if j == selected:
            continue
        states = sum(((values >> v) & 1) << b for b, v in enumerate(args))
        ok &= (paths.L.NAE if callee == "K" else prep.G[callee])[states]
    relation = 0
    for value in values[ok]:
        v = int(value)
        outgoing = sum(((v >> a) & 1) << b for b, a in enumerate(arguments))
        relation |= 1 << (8 * (v & ((1 << k) - 1)) + outgoing)
    identity = canonical_partition(list(range(k)) + [a if a < k else ("own", a) for a in arguments])
    return relation, identity


def start_states(prep):
    """A1: one start per direct S-call of main; no covered target is omitted."""
    if prep.main == prep.S:
        return (start_state(prep),)
    entries = [c for c, _ in prep.flat(prep.main)["calls"] if c == prep.S]
    if not entries:
        raise ValueError("wrapper has no direct S entry")
    return tuple(start_state(prep, j) for j in range(len(entries)))


def step(state, call, k):
    joint, partition = state
    args = call["arguments"]
    identity = canonical_partition(list(range(k)) +
                                   [partition[k + a] if a < 3 else ("new", a) for a in args])
    # compose() supports square 8x8 tables; the same row operation extends to k main ports.
    new_joint = 0
    for t in range(1 << k):
        row = (joint >> (8 * t)) & 255
        new_row = 0
        for a in range(8):
            if row >> a & 1:
                new_row |= (call["relation"] >> (8 * a)) & 255
        new_joint |= new_row << (8 * t)
    return new_joint, identity


def project_state(prep, state, body=None):
    """Exact allowed window rows; canonical symbols agree with brute.py."""
    block, allowed = body_allowed(prep, prep.S) if body is None else body
    k = prep.k
    joint, partition = state
    aliases = list(range(k)) + list(partition[k:]) + [k + v for v in range(3, block["V"])]
    labels = sorted(set(aliases))
    index = {v: i for i, v in enumerate(labels)}
    end_aliases = list(partition[k:]) + [k + v for v in range(3, block["V"])]
    rows = []
    port_values = allowed & 7
    for t in range(1 << k):
        exits = (joint >> (8 * t)) & 255
        if not exits:
            continue
        ok = np.array([bool(exits >> v & 1) for v in range(8)])[port_values]
        for j, alias in enumerate(partition[k:]):
            if alias < k:
                ok &= ((allowed >> j) & 1) == ((t >> alias) & 1)
            else:
                first_port = alias - k
                ok &= ((allowed >> j) & 1) == ((allowed >> first_port) & 1)
        selected = allowed[ok]
        packed = np.full(len(selected), t, dtype=np.int64)
        for v, alias in enumerate(end_aliases):
            if alias >= k:
                packed |= ((selected >> v) & 1) << index[alias]
        rows.extend(map(int, np.unique(packed)))
    return dict(labels=labels, allowed=sorted(set(rows)), main_aliases=list(range(k)),
                end_aliases=end_aliases, root_labels=list(range(k)),
                own_labels=[k + v for v in range(3, block["V"])])


def pendant_data(prep):
    """Count knots after inlining, and remember arguments of inlined calls too."""
    flat = prep.flat(prep.S)
    call_arguments = set()
    next_id = flat["k"]

    def visit(i, actual):
        nonlocal next_id
        k, own, calls = prep.u[i]
        env = list(actual) + list(range(next_id, next_id + own))
        next_id += own
        for callee, args in calls:
            mapped = tuple(env[a] for a in args)
            if callee != "K":
                call_arguments.update(mapped)
            if callee not in ("K", "SELF") and callee not in prep.holding:
                visit(callee, mapped)

    visit(prep.S, range(3))
    counts = {v: 0 for v in range(flat["V"])}
    knots = [tuple(args) for c, args in flat["calls"] if c == "K"]
    for knot in knots:
        for v in set(knot):
            counts[v] += 1
    pendant = {v for v in range(3, flat["V"]) if counts[v] == 1 and v not in call_arguments}
    K = sorted({v for knot in knots for v in knot if v < 3 and len(set(knot)) == 3
                and all(x in pendant for x in knot if x != v)})
    meeting = sorted({v for knot in knots for v in knot if v < 3 and any(x >= 3 for x in knot)})
    return dict(K=K, pendant=sorted(pendant), knot_meeting_positions=meeting,
                call_arguments=sorted(call_arguments), knots=[list(t) for t in knots])


def bond_features(prep, state, projection, members, syntactic):
    k = prep.k
    partition = state[1]
    aliases = projection["end_aliases"]
    support = set(members)
    carried = [j for j in range(3) if partition[k + j] < k]
    B, widened = False, False
    for knot in syntactic["knots"]:
        if {aliases[v] for v in knot} != support:
            continue
        for p in knot:
            if p not in carried:
                continue
            others = [v for v in knot if v != p]
            widened |= any(v >= 3 for v in others)
            B |= len(others) == 2 and all(v in syntactic["pendant"] for v in others)
    rows = projection["allowed"]
    indices = {v: i for i, v in enumerate(projection["labels"])}
    ties = []
    for p in range(k):
        if p not in support:
            continue
        for j in range(3):
            if aliases[j] == p:
                continue
            differences = {((v >> indices[p]) ^ (v >> indices[aliases[j]])) & 1 for v in rows}
            if len(differences) == 1:
                ties.append(dict(main=p, copy_port=j, opposite=bool(next(iter(differences)))))
    tie = not carried and bool(ties)
    kinds = (["B"] if B else []) + (["widened-B"] if widened else []) + (["tie"] if tie else [])
    return dict(B=B, widened_B=widened, tie=tie, other=not kinds, kinds=kinds or ["other"],
                carried_positions=carried, semantic_ties=ties)


def window_bond(prep, state, body=None, syntactic=None, checkpoint=lambda: None):
    projection = project_state(prep, state, body)
    labels, rows = projection["labels"], projection["allowed"]
    if not rows:
        raise ValueError("empty window in a living family")
    values = np.asarray(rows, dtype=np.int64)
    indices = {v: i for i, v in enumerate(labels)}
    roots, own = set(projection["root_labels"]), set(projection["own_labels"])
    cache = {(): True}
    def shattered(support):
        if support not in cache:
            if len(values) < (1 << len(support)):
                cache[support] = False
            else:
                mapped = sum(((values >> indices[v]) & 1) << j for j, v in enumerate(support))
                cache[support] = len(np.unique(mapped)) == (1 << len(support))
        return cache[support]
    syntactic = pendant_data(prep) if syntactic is None else syntactic
    for size in range(2, min(6, len(labels)) + 1):
        bonds = []
        for support in combinations(labels, size):
            if not roots.intersection(support) or not own.intersection(support):
                continue
            checkpoint()
            if shattered(support):
                continue
            if all(shattered(support[:j] + support[j + 1:]) for j in range(size)):
                bonds.append(dict(members=list(support),
                                  **bond_features(prep, state, projection, support, syntactic)))
        if bonds:
            return dict(g=size, least_bonds=bonds, allowed_count=len(rows), labels=labels)
    return dict(g="> 6", least_bonds=[], allowed_count=len(rows), labels=labels)


def carried_sequence(prep, syntactic=None):
    """Identity-graph R_s, from every wrapper entry, without any truth table."""
    syntactic = pendant_data(prep) if syntactic is None else syntactic
    if prep.main == prep.S:
        current = 7
    else:
        current = 0
        for callee, arguments in prep.flat(prep.main)["calls"]:
            if callee == prep.S:
                for j, a in enumerate(arguments):
                    if a < prep.k:
                        current |= 1 << j
    edges = [tuple(a) for c, a in prep.flat(prep.S)["calls"] if c == prep.S]
    seen, masks = {}, []
    while current not in seen:
        seen[current] = len(masks)
        masks.append(current)
        current = sum(1 << k for k in range(3)
                      if any(a[k] < 3 and current >> a[k] & 1 for a in edges))
    return dict(preperiod=seen[current], period=len(masks) - seen[current], masks=masks,
                K=syntactic["K"], knot_meeting_positions=syntactic["knot_meeting_positions"])


def residue_flags(sequence, preperiod, period, residue):
    """All distinct asymptotic phases at depths s = preperiod+residue mod period."""
    t, p = sequence["preperiod"], sequence["period"]
    g = math.gcd(period, p)
    masks = [sequence["masks"][j] for j in range(t, t + p)
             if (j - preperiod - residue) % g == 0]
    K = sum(1 << j for j in sequence["K"])
    meeting = sum(1 << j for j in sequence["knot_meeting_positions"])
    return dict(carried_masks=sorted(set(masks)), B_covered=all(m & K for m in masks),
                B_on_some_phase=any(m & K for m in masks),
                knot_meeting_some=any(m & meeting for m in masks),
                knot_meeting_every=all(m & meeting for m in masks),
                empty_some=any(m == 0 for m in masks), empty_every=all(m == 0 for m in masks))


def iterate(prep, calls, starts, checkpoint=lambda: None, max_states=200_000, max_levels=2000):
    body = body_allowed(prep, prep.S)
    syntactic = pendant_data(prep)
    sequence = carried_sequence(prep, syntactic)
    current = frozenset(starts)
    seen, levels, bonds, images = {}, [], {}, set()
    stored = 0
    cap = None
    while current not in seen:
        if len(levels) >= max_levels or stored + len(current) > max_states:
            cap = "Q_s level cap" if len(levels) >= max_levels else "Q_s stored-state cap"
            break
        seen[current] = len(levels)
        stored += len(current)
        minima = []
        for q in sorted(current):
            checkpoint()
            if q not in bonds:
                bonds[q] = window_bond(prep, q, body, syntactic, checkpoint)
            minima.append(bonds[q]["g"])
            images.add(context_image(q[0], prep.k))
        finite = [n for n in minima if isinstance(n, int)]
        U = min(finite) if finite else "> 6"
        witnesses = [witness for q in current if bonds[q]["g"] == U
                     for witness in bonds[q]["least_bonds"]]
        readings = dict(witness_count=len(witnesses), basis="all equally least U witnesses")
        for name in ("B", "widened_B", "tie", "other"):
            readings[name + "_any"] = any(w[name] for w in witnesses)
            readings[name + "_every"] = bool(witnesses) and all(w[name] for w in witnesses)
        readings["exclusive"] = next((name for name in ("B", "widened_B", "tie", "other")
                                      if readings[name + "_any"]), None)
        levels.append(dict(s=len(levels), states=len(current), U=U, readings=readings))
        nxt = set()
        for q in current:
            for call in calls:
                nxt.add(step(q, call, prep.k))
                if stored + len(nxt) > max_states:
                    cap = "Q_s construction stored-state cap"
                    break
                checkpoint()
            if cap:
                break
        if cap:
            break
        current = frozenset(nxt)
    complete = cap is None
    preperiod = seen[current] if complete else None
    period = len(levels) - preperiod if complete else None
    residues = []
    if complete:
        for residue, row in enumerate(levels[preperiod:]):
            residues.append(dict(residue=residue, s_mod_period=row["s"] % period, U=row["U"],
                                 readings=row["readings"],
                                 **residue_flags(sequence, preperiod, period, residue)))
    finite = [r["U"] for r in residues if isinstance(r["U"], int)]
    verdict = ("undecided" if not complete else "bounded" if len(finite) == period
               else "progressions" if finite else "none")
    violations = [r for r in residues if r["B_covered"] and
                  (not isinstance(r["U"], int) or r["U"] > 3)]
    K_mask = sum(1 << j for j in sequence["K"])
    no_B_coverage = not any(mask & K_mask for mask in sequence["masks"][sequence["preperiod"]:])
    # Keep all least bonds, with every tied witness, on each Q_s through depth 3.
    early = []
    qlevel = set(starts)
    for s in range(min(3, len(levels) - 1) + 1):
        for q in sorted(qlevel):
            item = bonds[q]
            early.append(dict(s=s, J=hex(q[0]), partition=list(q[1]), **item))
        qlevel = {step(q, call, prep.k) for q in qlevel for call in calls}
    result = dict(complete=complete, cap=cap, verdict=verdict, preperiod=preperiod, period=period,
                  repeat_at=len(levels) if complete else None,
                  U_at_repeat=levels[preperiod]["U"] if complete else None,
                  levels=levels, residues=residues, maximum=max(finite) if finite else None,
                  stored_states=stored, unique_states=len(bonds), context_images=sorted(images),
                  carried=sequence, syntactic=syntactic, early_states=early,
                  gate_b=dict(passed=not violations, violations=violations,
                              complete=complete or no_B_coverage,
                              applicable=any(r["B_covered"] for r in residues),
                              basis="complete window residues" if complete else
                                    "syntactically no B-covered residue" if no_B_coverage else
                                    "incomplete window with possible B coverage"))
    priority = ("B", "widened_B", "tie", "other")
    result["exclusive_reading"] = (max((r["readings"]["exclusive"] for r in residues),
                                       key=priority.index) if verdict == "bounded" else None)
    result["starts"] = [dict(J=hex(q[0]), partition=list(q[1])) for q in starts]
    # Every state's least witnesses are retained for all repeating residues, not only U's winners.
    result["state_bonds"] = [dict(J=hex(q[0]), partition=list(q[1]), **bonds[q]) for q in sorted(bonds)]
    return result


def context_image(joint, k):
    image = 0
    for t in range(1 << k):
        image |= (joint >> (8 * t)) & 255
    return image


def dead_positions(prep):
    """A2: dead is the complement of least knot-seeded call liveness."""
    blocks = [prep.flat(i) for i in range(len(prep.u))]
    live = [set() for _ in prep.u]
    while True:
        new = [set(positions) for positions in live]
        for i, flat in enumerate(blocks):
            for p in range(flat["k"]):
                if any(c == "K" or j in live[c]
                       for c, args in flat["calls"] for j, a in enumerate(args) if a == p):
                    new[i].add(p)
        if new == live:
            return [sorted(set(range(flat["k"])) - positions)
                    for flat, positions in zip(blocks, live)]
        live = new


def reduce_state(value, live):
    return sum(((value >> j) & 1) << b for b, j in enumerate(live))


def reduce_relation(relation, live):
    size = 1 << len(live)
    result = 0
    for a in range(8):
        for b in range(8):
            if relation >> (8 * a + b) & 1:
                result |= 1 << (size * reduce_state(a, live) + reduce_state(b, live))
    return result


def trimmed_gap(generators, images, G, checkpoint=lambda: None, size=8, max_r=8):
    """Complete length sets through max_r (A7: census r on gate c only)."""
    current = frozenset(generators)
    stored = 0
    length_sizes = []
    for r in range(1, max_r + 1):
        stored += len(current)
        if stored > 250_000:
            return dict(complete=False, certified=False, r=None, cap="stored P_n product cap 250000")
        length_sizes.append(len(current))
        success = True
        for A in images:
            mask = sum(1 << (size * a + b) for a in range(size) if A >> a & 1
                       for b in range(size) if G >> b & 1)
            for M in current:
                if not relations.rectangular(M & mask, size):
                    success = False
                    break
                checkpoint()
            if not success:
                break
        if success:
            return dict(complete=True, certified=True, r=r, length_set_sizes=length_sizes,
                        contexts=len(images), size=size)
        if r == max_r:
            break
        nxt = set()
        for M in current:
            for R in generators:
                nxt.add(relations.compose(M, R, size))
                if stored + len(nxt) > 250_000:
                    return dict(complete=False, certified=False, r=None,
                                cap="P_n construction product cap 250000")
                checkpoint()
        current = frozenset(nxt)
    return dict(complete=True, certified=False, r=None, length_set_sizes=length_sizes,
                contexts=len(images), size=size)


def growth_tests(prep, calls, window, checkpoint=lambda: None):
    dead = dead_positions(prep)
    live = [j for j in range(3) if j not in dead[prep.S]]
    reduced = [reduce_relation(c["relation"], live) for c in calls]
    result = dict(dead_positions=dead, live_S=live)
    try:
        sg = relations.semigroup(reduced, checkpoint, size=1 << len(live))
        result["G"] = dict(certified=sg["r"] is not None, **sg)
    except LimitReached as exc:
        result["G"] = dict(complete=False, certified=False, r=None, cap=str(exc))
    if not window.get("complete"):
        result["G2"] = result["G2_live"] = dict(complete=False, certified=False, r=None,
                                               skipped="reachable contexts incomplete")
        return result
    G = sum(int(v) << j for j, v in enumerate(prep.G[prep.S]))
    images = window["context_images"]
    result["G2"] = trimmed_gap([c["relation"] for c in calls], images, G, checkpoint)
    # OR is required when several original states project onto the same live state.
    def project_mask(mask):
        value = 0
        for a in range(8):
            if mask >> a & 1:
                value |= 1 << reduce_state(a, live)
        return value
    reduced_images = sorted({project_mask(A) for A in images})
    result["G2_live"] = trimmed_gap(reduced, reduced_images, project_mask(G), checkpoint,
                                   size=1 << len(live))
    return result


def run_family(key, census=None, weight=1, *, include_growth=True, budget=None):
    budget = Limits(585, 2_800_000_000) if budget is None else budget
    out = dict(key=key, weight=weight, verdict="undecided", ambiguities=[], caps=[], invalid=False,
               gate_a=dict(passed=False, complete=False), gate_b=dict(passed=True, applicable=False),
               gate_e=dict(passed=True), window=dict(complete=False, verdict="undecided"))
    try:
        if census is not None and census.get("verdict") == "capped":
            out["caps"].append("inherited census semigroup length-set cap")
        prep = paths.Preparation(json.loads(key))
        out["preparation"] = prep.info()
        out["scope"] = scope(prep)
        out["wrapper"] = prep.main != prep.S
        out["depth"] = dict(word_s0_copy_depth=int(out["wrapper"]),
                            word_length="s", absolute_copy_depth="s+1" if out["wrapper"] else "s")
        calls = relations.per_call(prep, budget.checkpoint)
        out["R_i"] = [call["hex"] for call in calls]
        out["c"] = len(calls)
        living = bool(prep.G[prep.S].any()) and bool(prep.alive)
        matches = census is None or out["R_i"] == census["R_i"]
        out["gate_a"] = dict(passed=living and matches, complete=True, living=living,
                             relations_match=matches, census_R_i=None if census is None else census["R_i"])
        out["stratum"], out["stratum_details"] = stratum(prep, out["R_i"])
        if not living or not matches:
            out["invalid"] = True
            return out
        out["syntactic_carried"] = carried_sequence(prep)
        starts = start_states(prep)
        out["window"] = iterate(prep, calls, starts, budget.checkpoint)
        out["gate_b"] = out["window"]["gate_b"]
        if out["window"].get("cap"):
            out["caps"].append(out["window"]["cap"])
        if include_growth:
            out["growth"] = growth_tests(prep, calls, out["window"], budget.checkpoint)
            for name in ("G", "G2", "G2_live"):
                if out["growth"][name].get("cap"):
                    out["caps"].append(out["growth"][name]["cap"])
    except LimitReached as exc:
        out["caps"].append(str(exc))
    except MemoryError:
        out["caps"].append("Python MemoryError")
    finally:
        bounded = out["window"].get("verdict") == "bounded"
        growing = any(out.get("growth", {}).get(n, {}).get("certified") for n in ("G", "G2", "G2_live"))
        out["gate_e"] = dict(passed=not (bounded and growing), bounded=bounded, growing=growing)
        out["invalid"] |= not out["gate_a"]["passed"] or not out["gate_b"]["passed"] or not out["gate_e"]["passed"]
        if not out["invalid"] and not out["caps"]:
            out["verdict"] = ("growing" if growing and out.get("scope", {}).get("in_scope") else
                              "bounded" if bounded else "progressions" if
                              out["window"].get("verdict") == "progressions" else "undecided")
        out.update(budget.metrics())
    return out
