"""Independent unfolded-CNF projection and bond checks for CARRY-BOUND.

Only the description-language input module is imported.  In particular this
file does not import the window, per-call relations, composition, or path DP.
The usual-limit relations are recomputed from raw definitions.  Every copy
through the requested absolute cutoff is explicit in CNF; calls below it use
their usual-limit relations.
"""
from __future__ import annotations

from dataclasses import dataclass
import importlib.util
import json
from pathlib import Path
import sys
from typing import Mapping

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
INPUT = ROOT / "experiments/SHORT-DESC-20261112-001A/SHORT-DESC-20261112-001A-E001_description_census/dlang.py"
DEFAULT_CAPS = {"max_variables": 15_000, "max_clauses": 100_000,
                "max_copies": 25_000, "max_rows": 1 << 20}


class CalculationCap(Exception):
    """A declared resource cap, never a completed projection or exclusion."""

    def __init__(self, name, limit, observed):
        self.name, self.limit, self.observed = name, int(limit), int(observed)
        super().__init__(f"{name}: {observed} exceeds {limit}")

    def record(self):
        return {"name": self.name, "limit": self.limit, "observed": self.observed}


class ComputationAmbiguity(Exception):
    """An input convention that the frozen text has not selected."""


def _language():
    name = "carry_independent_description_language"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, INPUT)
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot load input language: {INPUT}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


def _raw_definitions(prep):
    if isinstance(prep, str):
        raw = json.loads(prep)
    elif isinstance(prep, Mapping):
        if "key" in prep:
            raw = json.loads(prep["key"])
        elif "defs" in prep:
            raw = prep["defs"]
        else:
            raise ValueError("family mapping needs raw key or defs")
    elif hasattr(prep, "defs"):
        raw = prep.defs
    else:
        raw = prep
    defs = []
    for i, (k, own, calls) in enumerate(raw):
        k, own = int(k), int(own)
        if k < 1 or own < 0:
            raise ValueError("invalid definition size")
        body = []
        for callee, args in calls:
            args = tuple(int(a) for a in args)
            if callee == "K" or callee == "SELF":
                arity = 3
                if callee == "SELF" and k != 3:
                    raise ValueError("SELF requires three ports")
            elif isinstance(callee, int) and not isinstance(callee, bool) and 0 <= callee < i:
                arity = defs[callee][0]
            else:
                raise ValueError(f"invalid callee {callee!r} in definition {i}")
            if len(args) != arity or any(a < 0 or a >= k + own for a in args):
                raise ValueError("invalid call arguments")
            body.append((callee, args))
        defs.append((k, own, body))
    if not defs:
        raise ValueError("no definitions")
    return defs


@dataclass
class Family:
    raw: list
    defs: list
    holding: frozenset
    limits: dict
    main: int
    S: int
    alive: bool
    flat_cache: dict

    def flat(self, definition, *, max_variables=15_000, max_calls=100_000):
        """Own inlining, matching raw-call order without using prep.flat()."""
        if definition in self.flat_cache:
            result = self.flat_cache[definition]
            if result["V"] > max_variables:
                raise CalculationCap("max_flat_variables", max_variables, result["V"])
            if len(result["calls"]) > max_calls:
                raise CalculationCap("max_flat_calls", max_calls, len(result["calls"]))
            return result
        k = self.defs[definition][0]
        next_variable, calls, owners = k, [], {}

        def inline(i, actual):
            nonlocal next_variable
            _, own, body = self.defs[i]
            if next_variable + own > max_variables:
                raise CalculationCap("max_flat_variables", max_variables, next_variable + own)
            fresh = tuple(range(next_variable, next_variable + own))
            next_variable += own
            env = tuple(actual) + fresh
            for local, variable in enumerate(fresh):
                owners[variable] = {"definition": i, "own_index": local}
            for callee, args in body:
                a = tuple(env[x] for x in args)
                if callee == "K":
                    calls.append(("K", a))
                elif callee == "SELF":
                    calls.append((i, a))
                elif callee in self.holding:
                    calls.append((callee, a))
                else:
                    inline(callee, a)
                if len(calls) > max_calls:
                    raise CalculationCap("max_flat_calls", max_calls, len(calls))

        inline(definition, tuple(range(k)))
        result = {"k": k, "V": next_variable, "calls": calls, "owners": owners}
        self.flat_cache[definition] = result
        return result


def prepare_family(prep):
    """Read raw definitions from a prepared family, row, key, or raw list."""
    if isinstance(prep, Family):
        return prep
    raw = _raw_definitions(prep)
    usual = []
    for k, own, calls in raw:
        body = list(calls)
        if any(c == "SELF" and sorted(a) == [0, 1, 2] for c, a in calls):
            body.append(("K", (0, 1, 2)))
        usual.append((k, own, body))
    holding = frozenset(i for i, (_, _, calls) in enumerate(usual)
                        if any(c == "SELF" for c, _ in calls))

    def first_holding(i):
        if i in holding:
            return i
        for callee, _ in usual[i][2]:
            if callee != "K":
                found = first_holding(callee)
                if found is not None:
                    return found
        return None

    main = len(usual) - 1
    S = first_holding(main)
    if S is None:
        raise ValueError("family has no self-holding definition reachable from main")
    expected_S = prep.get("S") if isinstance(prep, Mapping) else getattr(prep, "S", None)
    if expected_S is not None and int(expected_S) != S:
        raise ComputationAmbiguity("recorded S differs from raw-call first self-holding definition")
    lang = _language()
    _, _, limits = lang.depth_sequence(usual, lang.TOP)
    alive = bool(lang.relations(usual, limits)[main].any())
    return Family(raw=raw, defs=usual, holding=holding,
                  limits={i: tuple(bool(v) for v in relation) for i, relation in limits.items()},
                  main=main, S=S, alive=alive, flat_cache={})


def unfold_pattern(prep, cutoff_depth, *, target_depth=None, word=None,
                   entry_index=None, max_variables=15_000, max_clauses=100_000,
                   max_copies=25_000):
    """Explicit full pattern, all blocks through absolute cutoff inclusive.

    A self-holding main is at depth 0.  A nonholding main's direct
    self-holding entries are at depth 1.  SELF adds one to depth; a numeric
    self-holding call within a self-holding block does not.  Numeric helpers
    are inlined in raw-call order.  Covered S copies start directly at main
    and thereafter use S-to-S calls only.  Every other copy is still unfolded.

    With ``word`` selected, ``entry_index`` is the ordinal among main's
    retained S calls.  A wrapper with several such entries requires it;
    no entry is chosen automatically in that case.
    """
    family = prepare_family(prep)
    cutoff_depth = int(cutoff_depth)
    if cutoff_depth < 0:
        raise ValueError("negative cutoff depth")
    if word is not None:
        word = tuple(word)
        if any(not isinstance(i, int) or isinstance(i, bool) or i < 0 for i in word):
            raise ValueError("word letters must be nonnegative integer S-call ordinals")
    def bounded_flat(i):
        return family.flat(i, max_variables=max_variables, max_calls=max_clauses)

    main_flat = bounded_flat(family.main)
    s_flat = bounded_flat(family.S)
    s_calls = [j for j, (c, _) in enumerate(s_flat["calls"]) if c == family.S]
    if word is not None and any(i >= len(s_calls) for i in word):
        raise ValueError("word letter outside S's SELF-call alphabet")
    entries = [j for j, (c, _) in enumerate(main_flat["calls"]) if c == family.S]
    if word is not None and family.main != family.S:
        if entry_index is None:
            if len(entries) != 1:
                raise ComputationAmbiguity("multiple direct wrapper S entries require entry_index")
            entry_index = 0
        if not isinstance(entry_index, int) or isinstance(entry_index, bool) or not 0 <= entry_index < len(entries):
            raise ValueError("entry_index outside direct wrapper S entries")
    elif word is not None and entry_index not in (None, 0):
        raise ValueError("self-holding main has no wrapper entry choice")
    entry_ordinals = {flat_index: ordinal for ordinal, flat_index in enumerate(entries)}
    n = main_flat["k"]
    clauses, copies, origins, targets = [], [], {}, set()
    end_variables = None

    def append(clause):
        if len(clauses) >= max_clauses:
            raise CalculationCap("max_clauses", max_clauses, len(clauses) + 1)
        clauses.append(clause)

    def substitute_limit(actual, relation):
        for state, allowed in enumerate(relation):
            if not allowed:
                append([-(v + 1) if state >> j & 1 else v + 1 for j, v in enumerate(actual)])

    def visit(i, actual, depth, address, covered_word=None, covered_entry=None, is_main=False):
        nonlocal n, end_variables
        flat = bounded_flat(i)
        own = flat["V"] - flat["k"]
        if n + own > max_variables:
            raise CalculationCap("max_variables", max_variables, n + own)
        if len(copies) >= max_copies:
            raise CalculationCap("max_copies", max_copies, len(copies) + 1)
        fresh = tuple(range(n, n + own))
        n += own
        env = tuple(actual) + fresh
        copy = {"definition": i, "depth": depth, "address": list(address),
                "ports": list(actual), "own": list(fresh),
                "covered": covered_word is not None and i == family.S,
                "word": None if covered_word is None else list(covered_word),
                "entry_index": covered_entry}
        copies.append(copy)
        for flat_index in range(flat["k"], flat["V"]):
            origins[env[flat_index]] = {"definition": i, "depth": depth,
                "address": list(address), "flat_index": flat_index,
                "raw_owner": flat["owners"][flat_index], "covered": copy["covered"],
                "word": copy["word"], "entry_index": covered_entry}
        if copy["covered"] and target_depth is not None and depth == target_depth:
            targets.update(fresh)
        if word is not None and copy["covered"] and covered_word == word and (
                family.main == family.S or covered_entry == entry_index):
            if end_variables is not None:
                raise AssertionError("a chosen entry and S word found more than one end copy")
            end_variables = env
        self_ordinals = {j: ordinal for ordinal, j in enumerate(
            j for j, (c, _) in enumerate(flat["calls"]) if c == family.S)}
        for flat_index, (callee, args) in enumerate(flat["calls"]):
            actual_child = tuple(env[x] for x in args)
            if callee == "K":
                append([v + 1 for v in actual_child])
                append([-(v + 1) for v in actual_child])
                continue
            child_depth = depth + 1 if callee == i else (depth if i in family.holding else 1)
            if child_depth > cutoff_depth:
                substitute_limit(actual_child, family.limits[callee])
                continue
            child_word, child_entry = None, None
            if is_main and family.main != family.S and callee == family.S:
                child_word, child_entry = (), entry_ordinals[flat_index]
            elif i == family.S and callee == family.S and covered_word is not None:
                child_word = covered_word + (self_ordinals[flat_index],)
                child_entry = covered_entry
            visit(callee, actual_child, child_depth, address + (flat_index,),
                  child_word, child_entry)

    visit(family.main, tuple(range(main_flat["k"])), 0, (),
          () if family.main == family.S else None, None, True)
    return {"family": family, "clauses": clauses, "n": n,
            "roots": tuple(range(main_flat["k"])), "targets": targets,
            "copies": copies, "origin": origins, "end": end_variables,
            "end_flat": s_flat, "entry_index": entry_index,
            "cutoff_depth": cutoff_depth}


def enumerate_projection(clauses, n, variables, *, max_rows=1 << 20, backend="glucose42"):
    """Enumerate precisely the extendible assignments, blocking only projection.

    Unused distinctions are declared to the solver too.  ``max_rows`` limits
    retained rows; hitting it raises rather than returning a partial relation.
    """
    from pysat.solvers import Solver

    variables = tuple(int(v) for v in variables)
    if len(set(variables)) != len(variables) or any(v < 0 or v >= n for v in variables):
        raise ValueError("projection variables must be unique unfolded variable indices")
    rows = []
    with Solver(name=backend, bootstrap_with=clauses) as sat:
        if n:
            sat.add_clause([n, -n])
        while sat.solve():
            model = {abs(literal) - 1: literal > 0 for literal in sat.get_model()}
            row = sum(int(model.get(v, False)) << j for j, v in enumerate(variables))
            if len(rows) >= max_rows:
                raise CalculationCap("max_rows", max_rows, len(rows) + 1)
            rows.append(row)
            sat.add_clause([-(v + 1) if row >> j & 1 else v + 1
                            for j, v in enumerate(variables)])
    return sorted(rows)


def bond_check_cnf(clauses, n, support, *, max_rows=1 << 20, backend="glucose42"):
    """Recheck non-shattering and EVERY one-variable deletion by fresh SAT."""
    support = tuple(int(v) for v in support)
    allowed = enumerate_projection(clauses, n, support, max_rows=max_rows, backend=backend)
    deletions = []
    for drop, variable in enumerate(support):
        keep = [j for j in range(len(support)) if j != drop]
        rows = {sum(((state >> j) & 1) << p for p, j in enumerate(keep)) for state in allowed}
        deletions.append({"variable": variable, "allowed_count": len(rows),
                          "full": len(rows) == 1 << len(keep)})
    living = bool(allowed)
    non_shattered = len(allowed) < 1 << len(support)
    return {"support": list(support), "allowed": allowed, "living": living,
            "non_shattered": non_shattered,
            "deletions": deletions, "every_deletion_full": all(d["full"] for d in deletions),
            "is_bond": living and non_shattered and all(d["full"] for d in deletions),
            "backend": backend}


def _word_pattern(prep, word, *, entry_index, cutoff_depth, caps):
    """Build a word's end block and, by default, its children's level.

    The word length counts SELF steps from the top S copy, at absolute depth
    0 when main is S and 1 for a wrapper.  An explicit absolute cutoff remains
    supported as long as it includes the selected end block.
    """
    family = prepare_family(prep)
    word = tuple(word)
    target_depth = len(word) + (family.main != family.S)
    cutoff = target_depth + 1 if cutoff_depth is None else int(cutoff_depth)
    if cutoff < target_depth:
        raise ComputationAmbiguity("cutoff_depth does not include the selected end block")
    pattern = unfold_pattern(family, cutoff, target_depth=target_depth, word=word,
                             entry_index=entry_index,
                             **{k: caps[k] for k in ("max_variables", "max_clauses", "max_copies")})
    if pattern["end"] is None:
        raise AssertionError("explicit unfolding did not reach selected S word")
    actual_to_label, label_to_actual = {}, {}
    main_aliases, end_aliases = [], []
    k = len(pattern["roots"])
    for symbol, actual in list(enumerate(pattern["roots"])) + [
            (k + v, actual) for v, actual in enumerate(pattern["end"])]:
        if actual not in actual_to_label:
            actual_to_label[actual] = symbol
            label_to_actual[symbol] = actual
        if symbol < k:
            main_aliases.append(actual_to_label[actual])
        else:
            end_aliases.append(actual_to_label[actual])
    labels = list(label_to_actual)
    metadata = {"word": list(word), "word_length": len(word), "depth": target_depth,
        "cutoff_depth": cutoff, "blocks_through_cutoff_inclusive": True,
        "entry_index": pattern["entry_index"], "main": family.main, "S": family.S,
        "labels": labels, "main_aliases": main_aliases, "end_aliases": end_aliases,
        "root_labels": sorted(set(main_aliases)),
        "own_labels": sorted(set(end_aliases[pattern["end_flat"]["k"]:])),
        "variables": pattern["n"], "clauses": len(pattern["clauses"]),
        "copies": len(pattern["copies"]), "limits": caps,
        "usual_limit_alive": family.alive}
    return pattern, metadata, label_to_actual


def project_word(prep, word, *, entry_index=None, cutoff_depth=None,
                 max_variables=15_000, max_clauses=100_000, max_copies=25_000,
                 max_rows=1 << 20):
    """Canonical exact window labels and allowed integer rows from full CNF.

    Labels are first occurrences in ``main[0:k], end[0:V]``: main p has symbol
    p, end block index v has symbol k+v.  Identical variables get the earliest
    symbol.  Word letters are ordinals among S's retained S calls, and s is
    their count from the top copy of S.  The default absolute cutoff is
    s + (main != S) + 1, keeping every copy through the end copy's children's
    level inclusive and using usual-limit relations below it.  ``cutoff_depth``
    can override that absolute cutoff.  Wrappers with several direct S entries
    require ``entry_index``; omitting it returns ``not_computed``.
    """
    caps = dict(max_variables=max_variables, max_clauses=max_clauses,
                max_copies=max_copies, max_rows=max_rows)
    try:
        pattern, metadata, label_to_actual = _word_pattern(
            prep, word, entry_index=entry_index, cutoff_depth=cutoff_depth, caps=caps)
        allowed = enumerate_projection(pattern["clauses"], pattern["n"],
                                       tuple(label_to_actual.values()), max_rows=max_rows)
        return dict(metadata, status="ok", allowed=allowed, backend="glucose42")
    except ComputationAmbiguity as exc:
        return {"status": "not_computed", "reason": str(exc), "word": list(word), "limits": caps}
    except CalculationCap as exc:
        return {"status": "cap", "cap": exc.record(), "word": list(word), "limits": caps}


def recheck_bond(prep, word, support, *, entry_index=None, cutoff_depth=None,
                 max_variables=15_000, max_clauses=100_000, max_copies=25_000,
                 max_rows=1 << 20):
    """SAT-check canonical support using project_word's depth and entry rules."""
    caps = dict(max_variables=max_variables, max_clauses=max_clauses,
                max_copies=max_copies, max_rows=max_rows)
    try:
        pattern, metadata, label_to_actual = _word_pattern(
            prep, word, entry_index=entry_index, cutoff_depth=cutoff_depth, caps=caps)
        support = tuple(sorted(int(label) for label in support))
        if len(set(support)) != len(support) or any(label not in label_to_actual for label in support):
            raise ValueError("bond support must contain unique canonical window labels")
        actual_support = tuple(label_to_actual[label] for label in support)
        answer = bond_check_cnf(pattern["clauses"], pattern["n"], actual_support,
                                max_rows=max_rows, backend="glucose42")
        answer["support"] = list(support)
        for deletion, label in zip(answer["deletions"], support):
            deletion["variable"] = label
        answer["contains_main_port"] = bool(set(support) & set(metadata["root_labels"]))
        answer["contains_end_own"] = bool(set(support) & set(metadata["own_labels"]))
        answer["eligible_bond"] = (answer["is_bond"] and answer["contains_main_port"]
                                    and answer["contains_end_own"])
        return dict(metadata, status="ok", passed=answer["eligible_bond"], check=answer)
    except ComputationAmbiguity as exc:
        return {"status": "not_computed", "passed": False, "reason": str(exc), "word": list(word), "limits": caps}
    except CalculationCap as exc:
        return {"status": "cap", "passed": False, "cap": exc.record(), "word": list(word), "limits": caps}
