"""Independent flattened-path bond search for the A2--A4 gate.

No path/ray DP, census Block, Operation, graph or state encoding is imported.
Only the supplied description-language usualisation/limit reference is used.
The addendum fixes the usual-limit frontier, every root entry, and an endpoint
among main's ports.  ``brute`` now enumerates those paths independently.  The
earlier full-tree construction remains available as ``full_tree_cnf`` and
``full_tree_brute`` for provenance; it is not used by the addendum gate.

All distinctions, including unused own distinctions, are retained.  Only the
chosen copies are expanded; every other self-holding call uses its limit.
Members belong to main and the own distinctions of its chosen descendants.
Assignments to each path instance are enumerated directly, and
projections are checked by their full truth tables through member-set size 7.
"""
from __future__ import annotations

import argparse
from functools import lru_cache
import importlib.util
import itertools
import json
import os
from pathlib import Path
import time

for _name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_name] = "1"
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
LS_PATH = (ROOT / "experiments/LIMIT-STATE-20261112-001A/"
           "LIMIT-STATE-20261112-001A-E001_limit_states/census.py")
_spec = importlib.util.spec_from_file_location("_paths_brute_limit_reference", LS_PATH)
LS = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(LS)


class BruteLimit(RuntimeError):
    pass


def _normalise(defs):
    if not defs:
        raise ValueError("a family must contain a definition")
    out = []
    for i, (k, own, calls) in enumerate(defs):
        if not isinstance(k, int) or k < 3 or not isinstance(own, int) or own < 0:
            raise ValueError("invalid port or own-distinction count")
        body = []
        for target, args in calls:
            args = tuple(args)
            if any(not isinstance(a, int) or not 0 <= a < k + own for a in args):
                raise ValueError("call argument outside its definition")
            if target in ("K", "SELF"):
                if len(args) != 3 or (target == "SELF" and k != 3):
                    raise ValueError("K and SELF require three arguments; SELF has three ports")
            elif not isinstance(target, int) or not 0 <= target < i or len(args) != out[target][0]:
                raise ValueError("a callee must be an earlier definition with matching arity")
            body.append((target, args))
        out.append((k, own, body))
    return out


def flat_body(defs, index):
    """Inline non-self-holding definitions with independently assigned locals."""
    holding = {i for i, (_, _, calls) in enumerate(defs)
               if any(target == "SELF" for target, _ in calls)}
    k = defs[index][0]
    next_var = k
    flat = []

    def visit(i, ports):
        nonlocal next_var
        _, own, calls = defs[i]
        env = tuple(ports) + tuple(range(next_var, next_var + own))
        next_var += own
        for target, arguments in calls:
            actual = tuple(env[a] for a in arguments)
            if target == "K":
                flat.append(("K", actual))
            elif target == "SELF":
                flat.append((i, actual))
            elif target in holding:
                flat.append((target, actual))
            else:
                visit(target, actual)

    visit(index, tuple(range(k)))
    return dict(index=index, k=k, own=next_var - k, V=next_var, calls=tuple(flat))


def _description(defs):
    defs = _normalise(defs)
    usual, passes = LS.usual(defs)
    main = len(usual) - 1
    root = flat_body(usual, main)
    holding = {i for i, (_, _, calls) in enumerate(usual)
               if any(target == "SELF" for target, _ in calls)}
    S = main if main in holding else next((t for t, _ in root["calls"] if t != "K"), None)
    if S is None:
        raise ValueError("family has no census-selected self-holding definition")
    body = root if S == main else flat_body(usual, S)
    if body["k"] != 3:
        raise ValueError("S must have three ports")
    _, _, limits = LS.L.depth_sequence(usual, LS.L.TOP)
    return usual, root, body, S, limits, passes


def unfolding_size(defs, s, *, root_entries, stop_after=None):
    """Count the full S-copy tree without materialising it.

    With stop_after, report an honest lower bound as soon as that bound is
    exceeded; this prevents enormous powers being allocated for a skipped case.
    """
    if not isinstance(s, int) or s < 1:
        raise ValueError("s must be a positive integer")
    if root_entries not in ("all", "census-first"):
        raise ValueError("root_entries must explicitly be 'all' or 'census-first'")
    _, root, body, S, _, _ = _description(defs)
    entry_count = sum(t == S for t, _ in root["calls"])
    c = sum(t == S for t, _ in body["calls"])
    if not entry_count or not c:
        raise ValueError("selected S has no entry or SELF continuation")
    width = entry_count if root_entries == "all" else 1
    total = root["V"]
    copies = 1
    if body["own"] == 0:
        # No new distinctions, but a huge zero-own copy tree remains a genuine
        # construction cost.  Do not pretend its copy count was materialised.
        return dict(n=total, copies=None, c=c, root_calls=width,
                    own_per_copy=0, exact_n=True, zero_own_tree=True)
    for depth in range(1, s + 1):
        total += width * body["own"]
        copies += width
        if stop_after is not None and total > stop_after:
            return dict(n=None, n_lower_bound=total, copies_lower_bound=copies,
                        c=c, root_calls=entry_count if root_entries == "all" else 1,
                        own_per_copy=body["own"], exact_n=False,
                        count_stopped_at_depth=depth)
        width *= c
    return dict(n=total, copies=copies, c=c,
                root_calls=entry_count if root_entries == "all" else 1,
                own_per_copy=body["own"], exact_n=True)


def _forbidden_state_clauses(arguments, relation):
    if len(relation) != 1 << len(arguments):
        raise ValueError("frontier relation has the wrong arity")
    return [[-(v + 1) if (state >> j) & 1 else v + 1
             for j, v in enumerate(arguments)]
            for state, allowed in enumerate(relation) if not allowed]


def full_tree_cnf(defs, s, *, frontier, root_entries, copy_cap=100_000):
    """Return a full unfolding, with G at its explicitly selected frontier.

    frontier='usual-limit' is the only implemented frontier.  Requiring the
    argument does not resolve whether it is the frontier intended by the spec.
    Other self-holding definitions are read as their supplied usual limit G,
    exactly the fixed-S object; they do not become descendants of S.
    """
    if frontier != "usual-limit":
        raise ValueError("explicit frontier='usual-limit' is required; no other frontier is implemented")
    if root_entries not in ("all", "census-first"):
        raise ValueError("root_entries must explicitly be 'all' or 'census-first'")
    if not isinstance(s, int) or s < 1:
        raise ValueError("s must be a positive integer")
    _, root, body, S, limits, passes = _description(defs)
    clauses, copies, targets = [], [], []
    next_var = root["k"]
    root_variables = None

    def build(flat, ports, depth, parent, path_own, path_calls):
        nonlocal next_var, root_variables
        if len(copies) >= copy_cap:
            raise BruteLimit(f"full-tree copies exceed {copy_cap}")
        own = tuple(range(next_var, next_var + flat["own"]))
        next_var += flat["own"]
        env = tuple(ports) + own
        index = len(copies)
        if depth == 0:
            root_variables = env
            path_own = env  # census's main member universe includes its ports
        else:
            path_own = tuple(path_own) + own
        copies.append(dict(id=index, parent=parent, depth=depth,
                           ports=list(ports), own=list(own), path_calls=list(path_calls)))
        if depth == s:
            targets.append(dict(copy=index, own=own,
                                path_variables=tuple(sorted(set(path_own))),
                                path_calls=tuple(path_calls)))
        entries = [j for j, (target, _) in enumerate(flat["calls"]) if target == S]
        chosen_at_root = entries[:1] if root_entries == "census-first" else entries
        for call_index, (target, arguments) in enumerate(flat["calls"]):
            actual = tuple(env[a] for a in arguments)
            if target == "K":
                clauses.append([v + 1 for v in actual])
                clauses.append([-(v + 1) for v in actual])
            elif target == S and depth < s and (depth or call_index in chosen_at_root):
                build(body, actual, depth + 1, index, path_own, path_calls + (call_index,))
            else:
                clauses.extend(_forbidden_state_clauses(actual, limits[target]))

    build(root, tuple(range(root["k"])), 0, None, (), ())
    return dict(clauses=clauses, n=next_var, copies=copies, targets=targets,
                root_variables=tuple(root_variables), root_ports=tuple(range(root["k"])),
                S=S, c=sum(t == S for t, _ in body["calls"]), passes=passes,
                frontier=frontier, root_entries=root_entries,
                limits={str(i): [bool(v) for v in relation] for i, relation in limits.items()})


def _enumerate_models(clauses, n, checkpoint):
    """Evaluate every full assignment directly; no DP or SAT projection oracle."""
    if n > 22:
        raise ValueError("direct model enumeration is limited to 22 distinctions")
    models = []
    for first in range(0, 1 << n, 1 << 18):
        checkpoint()
        assignments = np.arange(first, min(first + (1 << 18), 1 << n), dtype=np.uint32)
        allowed = np.ones(len(assignments), dtype=bool)
        for clause in clauses:
            clause_ok = np.zeros(len(assignments), dtype=bool)
            for literal in clause:
                bits = ((assignments >> (abs(literal) - 1)) & 1).astype(bool)
                clause_ok |= bits if literal > 0 else ~bits
            allowed &= clause_ok
            if not allowed.any():
                break
        if allowed.any():
            models.append(assignments[allowed])
    return np.concatenate(models) if models else np.empty(0, dtype=np.uint32)


def full_tree_brute(defs, s, max_size=7, *, frontier, root_entries, main_endpoint,
          max_variables=22, checkpoint=lambda: None, copy_cap=100_000):
    """Take the exact minimum over all target paths, through member size 7.

    main_endpoint='main-ports' reproduces the census start gate. 'main-all'
    instead permits any root distinction as the required main member.  Neither
    choice is silently adopted for the unresolved G-brute contract.
    """
    started = time.monotonic()
    if not isinstance(max_size, int) or not 1 <= max_size <= 7:
        raise ValueError("max_size must be an integer in 1..7")
    if not 1 <= max_variables <= 22:
        raise ValueError("max_variables must be in 1..22")
    if main_endpoint not in ("main-ports", "main-all"):
        raise ValueError("main_endpoint must explicitly be 'main-ports' or 'main-all'")
    size = unfolding_size(defs, s, root_entries=root_entries, stop_after=max_variables)
    result = dict(s=s, max_size=max_size, max_variables=max_variables,
                  frontier=frontier, root_entries=root_entries, main_endpoint=main_endpoint,
                  unfolding_size=size, least_size=None, witness=None,
                  target_copy=None, checked_target_copies=0)
    if not size["exact_n"] or size["n"] > max_variables:
        return dict(result, status="skipped_variable_cap", reason="full unfolded instance exceeds direct-enumeration cap",
                    seconds=time.monotonic() - started)
    if size.get("zero_own_tree"):
        return dict(result, status=f"none up to {max_size}", reason="no target has an own distinction",
                    target_copies_with_own=0, seconds=time.monotonic() - started)
    instance = full_tree_cnf(defs, s, frontier=frontier, root_entries=root_entries, copy_cap=copy_cap)
    checkpoint()
    built = time.monotonic()
    models = _enumerate_models(instance["clauses"], instance["n"], checkpoint)
    enumerated = time.monotonic()
    result.update(n=instance["n"], clauses=len(instance["clauses"]), copies=len(instance["copies"]),
                  target_copies=len(instance["targets"]), model_count=len(models),
                  build_seconds=built - started, enumeration_seconds=enumerated - built)
    if not len(models):
        return dict(result, status="dead", projection_checks=0,
                    seconds=time.monotonic() - started)
    samples = {}

    def full_on(rows, W):
        projected = np.zeros(len(rows), dtype=np.uint8)
        for j, variable in enumerate(W):
            projected |= (((rows >> variable) & 1) << j).astype(np.uint8)
        return bool(np.bincount(projected, minlength=1 << len(W)).all())

    @lru_cache(maxsize=200_000)
    def free(W):
        checkpoint()
        if len(models) < 1 << len(W):
            return False
        count = min(len(models), max(64, 8 * (1 << len(W))))
        if count not in samples:
            samples[count] = models[np.linspace(0, len(models) - 1, count, dtype=np.int64)]
        # A sample may certify fullness only; every non-full sample is followed
        # by every model. Thus no sampling claim enters a constrained verdict.
        return full_on(samples[count], W) or full_on(models, W)

    main = set(instance["root_ports"] if main_endpoint == "main-ports" else instance["root_variables"])
    targets = [target for target in instance["targets"] if target["own"]]
    result["target_copies_with_own"] = len(targets)
    checks = 0
    found = None
    found_target = None
    for member_count in range(2, max_size + 1):
        for target in targets:
            target_own = set(target["own"])
            for W in itertools.combinations(target["path_variables"], member_count):
                if not main.intersection(W) or not target_own.intersection(W):
                    continue
                checks += 1
                if free(W):
                    continue
                if all(free(W[:j] + W[j + 1:]) for j in range(member_count)):
                    found, found_target = W, target
                    break
            if found is not None:
                break
        if found is not None:
            break
    result.update(status="found" if found is not None else f"none up to {max_size}",
                  least_size=len(found) if found is not None else None,
                  witness=list(found) if found is not None else None,
                  target_copy=found_target["copy"] if found_target is not None else None,
                  target_path=list(found_target["path_calls"]) if found_target is not None else None,
                  candidate_sets_checked=checks, projection_checks=free.cache_info().misses,
                  projection_cache=free.cache_info()._asdict(),
                  checked_target_copies=len(targets), search_seconds=time.monotonic() - enumerated,
                  seconds=time.monotonic() - started)
    return result


def prepare_paths(defs):
    """Independent flat bodies, limit relations and ordered path choices."""
    usual, root, body, S, limits, passes = _description(defs)
    entries = tuple(j for j, (target, _) in enumerate(root["calls"]) if target == S)
    continuations = tuple(j for j, (target, _) in enumerate(body["calls"]) if target == S)
    if not entries or not continuations:
        raise ValueError("selected S has no root entry or SELF continuation")
    return dict(usual=usual, root=root, body=body, S=S, limits=limits,
                passes=passes, entries=entries, continuations=continuations,
                c=len(continuations), n_defs=len(usual),
                main_size=root["V"], s_size=body["V"])


def path_count(prepared, s, *, root_entries="all"):
    if not isinstance(s, int) or s < 1:
        raise ValueError("s must be a positive integer")
    if root_entries not in ("all", "census-first"):
        raise ValueError("root_entries must be 'all' or 'census-first'")
    e = len(prepared["entries"]) if root_entries == "all" else 1
    return e * prepared["c"] ** (s - 1)


def path_at(prepared, s, ordinal, *, root_entries="all"):
    """Unrank a path in entry/SELF-call order without materialising a tree."""
    count = path_count(prepared, s, root_entries=root_entries)
    if not isinstance(ordinal, int) or not 0 <= ordinal < count:
        raise ValueError("path ordinal is outside this depth's path range")
    choices = [0] * s
    for depth in range(s - 1, 0, -1):
        ordinal, choices[depth] = divmod(ordinal, prepared["c"])
    choices[0] = ordinal
    entries = prepared["entries"] if root_entries == "all" else prepared["entries"][:1]
    return (entries[choices[0]],) + tuple(prepared["continuations"][i] for i in choices[1:])


def path_size(prepared, s):
    if not isinstance(s, int) or s < 1:
        raise ValueError("s must be a positive integer")
    return prepared["root"]["V"] + s * prepared["body"]["own"]


def path_cnf(defs, s, path, *, prepared=None, frontier="usual-limit",
             checkpoint=lambda: None):
    """Expand one entry and s-1 SELF choices; close every side call by G.

    ``path`` contains indices in each independently flattened call body.  A
    repeated argument denotes the same distinction, including repeated ports;
    no fresh distinction is allocated for a port.  All own distinctions are
    allocated even when absent from every clause.
    """
    if frontier != "usual-limit":
        raise ValueError("the A2--A4 frontier is usual-limit")
    if not isinstance(s, int) or s < 1 or len(path) != s:
        raise ValueError("a depth-s path must have exactly s choices")
    p = prepare_paths(defs) if prepared is None else prepared
    if path[0] not in p["entries"] or any(j not in p["continuations"] for j in path[1:]):
        raise ValueError("path contains a call outside its allowed entries/SELF calls")
    clauses, copies = [], []
    next_var = p["root"]["k"]
    top = tuple(range(next_var))
    ports = top
    for depth in range(s + 1):
        checkpoint()
        flat = p["root"] if depth == 0 else p["body"]
        own = tuple(range(next_var, next_var + flat["own"]))
        next_var += flat["own"]
        env = tuple(ports) + own
        selected = path[depth] if depth < s else None
        copies.append(dict(id=depth, depth=depth, ports=list(ports), own=list(own),
                           selected_flat_call=selected))
        outgoing = None
        for j, (target, arguments) in enumerate(flat["calls"]):
            actual = tuple(env[a] for a in arguments)
            if target == "K":
                clauses.append([v + 1 for v in actual])
                clauses.append([-(v + 1) for v in actual])
            elif j == selected:
                outgoing = actual
            else:
                clauses.extend(_forbidden_state_clauses(actual, p["limits"][target]))
        if depth < s:
            if outgoing is None:
                raise ValueError("selected path call did not provide the next ports")
            ports = outgoing
    return dict(clauses=clauses, n=next_var, copies=copies,
                root_ports=top,
                root_variables=top + tuple(copies[0]["own"]),
                target_own=tuple(copies[-1]["own"]),
                path_variables=tuple(range(next_var)), path=list(path),
                S=p["S"], c=p["c"], frontier=frontier,
                passes=p["passes"])


def _search_path_instance(instance, max_size, checkpoint):
    """Direct K1--K3 truth tables; no DP transitions or DP output is used."""
    started = time.monotonic()
    models = _enumerate_models(instance["clauses"], instance["n"], checkpoint)
    enumerated = time.monotonic()
    base = dict(n=instance["n"], clauses=len(instance["clauses"]),
                model_count=len(models), least_size=None, witness=None,
                enumeration_seconds=enumerated - started)
    if not len(models):
        return dict(base, status="dead", projection_checks=0, candidate_sets_checked=0,
                    search_seconds=0.0)
    main, target = set(instance["root_ports"]), set(instance["target_own"])
    # A variable absent from all clauses cannot be essential to a constrained
    # projection. It stays in n and in full assignments but never in a bond.
    active = {abs(literal) - 1 for clause in instance["clauses"] for literal in clause}
    universe = tuple(v for v in instance["path_variables"] if v in active)
    if not target.intersection(active) or len(models) == 1 << instance["n"]:
        return dict(base, status=f"none up to {max_size}", projection_checks=0,
                    candidate_sets_checked=0, search_seconds=time.monotonic() - enumerated,
                    inactive_distinctions=instance["n"] - len(active))
    samples = {}

    def full_on(rows, W):
        projected = np.zeros(len(rows), dtype=np.uint8)
        for j, variable in enumerate(W):
            projected |= (((rows >> variable) & 1) << j).astype(np.uint8)
        return bool(np.bincount(projected, minlength=1 << len(W)).all())

    @lru_cache(maxsize=200_000)
    def free(W):
        checkpoint()
        if len(models) < 1 << len(W):
            return False
        count = min(len(models), max(64, 8 * (1 << len(W))))
        if count not in samples:
            samples[count] = models[np.linspace(0, len(models) - 1, count, dtype=np.int64)]
        return full_on(samples[count], W) or full_on(models, W)

    found, checks = None, 0
    for member_count in range(2, min(max_size, len(universe)) + 1):
        for W in itertools.combinations(universe, member_count):
            checkpoint()
            if not main.intersection(W) or not target.intersection(W):
                continue
            checks += 1
            if not free(W) and all(free(W[:j] + W[j + 1:]) for j in range(member_count)):
                found = W
                break
        if found is not None:
            break
    return dict(base, status="found" if found is not None else f"none up to {max_size}",
                least_size=len(found) if found is not None else None,
                witness=list(found) if found is not None else None,
                projection_checks=free.cache_info().misses,
                projection_cache=free.cache_info()._asdict(),
                candidate_sets_checked=checks,
                inactive_distinctions=instance["n"] - len(active),
                search_seconds=time.monotonic() - enumerated)


def brute_path(defs, s, path, max_size=7, *, prepared=None, max_variables=22,
               checkpoint=lambda: None):
    """Compute one path using complete CNF assignments and member subsets."""
    started = time.monotonic()
    if not isinstance(max_size, int) or not 1 <= max_size <= 7:
        raise ValueError("max_size must be an integer in 1..7")
    if not isinstance(max_variables, int) or not 1 <= max_variables <= 22:
        raise ValueError("max_variables must be an integer in 1..22")
    p = prepare_paths(defs) if prepared is None else prepared
    n = path_size(p, s)
    base = dict(s=s, path=list(path), max_size=max_size, max_variables=max_variables,
                n=n, least_size=None, witness=None, frontier="usual-limit",
                main_endpoint="main-ports")
    if n > max_variables:
        return dict(base, status="skipped_variable_cap", complete=False,
                    reason=f"path distinctions exceed {max_variables}",
                    seconds=time.monotonic() - started)
    instance = path_cnf(defs, s, path, prepared=p, checkpoint=checkpoint)
    built = time.monotonic()
    searched = _search_path_instance(instance, max_size, checkpoint)
    return dict(base, **{k: v for k, v in searched.items() if k not in base},
                least_size=searched["least_size"], witness=searched["witness"],
                complete=True, build_seconds=built - started,
                copy_ports=[copy["ports"] for copy in instance["copies"]],
                target_own=list(instance["target_own"]),
                carried_target_ports=[j for j, variable in enumerate(instance["copies"][-1]["ports"])
                                      if variable in instance["root_ports"]],
                uncarried=not any(variable in instance["root_ports"]
                                  for variable in instance["copies"][-1]["ports"]),
                seconds=time.monotonic() - started)


def brute(defs, s, max_size=7, *, frontier="usual-limit", root_entries="all",
          main_endpoint="main-ports", max_variables=22,
          checkpoint=lambda: None, copy_cap=None, on_path=None):
    """A2--A4 minimum over every entry and every SELF choice at depth s.

    A depth is complete only after every path was enumerated.  A missing bond
    means only ``none up to max_size``.  ``copy_cap`` is accepted for the old
    call interface but never limits the number of paths in the new object.
    """
    started = time.monotonic()
    if frontier != "usual-limit" or main_endpoint != "main-ports":
        raise ValueError("A2--A4 fixes usual-limit and main-ports")
    if not isinstance(max_size, int) or not 1 <= max_size <= 7:
        raise ValueError("max_size must be an integer in 1..7")
    if not isinstance(max_variables, int) or not 1 <= max_variables <= 22:
        raise ValueError("max_variables must be an integer in 1..22")
    p = prepare_paths(defs)
    count, n = path_count(p, s, root_entries=root_entries), path_size(p, s)
    base = dict(s=s, max_size=max_size, max_variables=max_variables, n=n,
                frontier=frontier, root_entries=root_entries, main_endpoint=main_endpoint,
                total_paths=count, checked_paths=0, skipped_paths=0,
                least_size=None, witness=None, target_path=None)
    if n > max_variables:
        return dict(base, status="skipped_variable_cap", complete=False,
                    skipped_paths=count, reason=f"every path has {n} distinctions, over {max_variables}",
                    skipped_path_ranges=[[0, count - 1]], seconds=time.monotonic() - started)
    best, best_row, best_uncarried, checked = None, None, None, 0
    for ordinal in range(count):
        checkpoint()
        row = brute_path(defs, s, path_at(p, s, ordinal, root_entries=root_entries),
                         max_size, prepared=p, max_variables=max_variables, checkpoint=checkpoint)
        row["path_index"] = ordinal
        checked += 1
        if row["least_size"] is not None and (best is None or row["least_size"] < best):
            best, best_row = row["least_size"], row
        if row["uncarried"] and row["least_size"] is not None:
            best_uncarried = min(best_uncarried, row["least_size"]) if best_uncarried is not None else row["least_size"]
        if on_path is not None:
            on_path(row)
    return dict(base, status="found" if best is not None else f"none up to {max_size}",
                complete=True, checked_paths=checked, least_size=best,
                witness=best_row["witness"] if best_row else None,
                target_path=best_row["path"] if best_row else None,
                least_size_uncarried=best_uncarried,
                seconds=time.monotonic() - started)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--key", required=True, help="canonical family JSON")
    parser.add_argument("--depth", type=int, required=True)
    parser.add_argument("--frontier", choices=("usual-limit",), default="usual-limit")
    parser.add_argument("--root-entries", choices=("all", "census-first"), default="all")
    parser.add_argument("--main-endpoint", choices=("main-ports",), default="main-ports")
    parser.add_argument("--max-size", type=int, default=7)
    parser.add_argument("--seconds", type=float, default=300)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.seconds <= 0:
        parser.error("--seconds must be positive")
    start = time.monotonic()

    def checkpoint():
        if time.monotonic() - start > args.seconds:
            raise BruteLimit("explicit brute wall-time cap")

    try:
        row = brute(json.loads(args.key), args.depth, args.max_size,
                    frontier=args.frontier, root_entries=args.root_entries,
                    main_endpoint=args.main_endpoint, checkpoint=checkpoint)
    except BruteLimit as exc:
        row = dict(status="timeout_or_copy_cap", error=str(exc), seconds=time.monotonic() - start)
    row["key"] = args.key
    content = json.dumps(row, sort_keys=True) + "\n"
    if args.out is not None:
        out = args.out.resolve()
        if not out.is_relative_to(HERE):
            raise ValueError("all output must remain inside CODEX")
        if out.exists():
            raise FileExistsError("brute output already exists; choose a fresh owned output")
        out.write_text(content)
    print(content, end="", flush=True)


if __name__ == "__main__":
    main()
