"""Separate R1 syntax recomputation directly from raw census keys.

Only Python's standard library is imported.  This module does not import the
primary READ-RULE producer or any CARRY parser, inliner, or R1 predicate.
No allowed-state or bond calculation is performed.  The CLI writes stdout
only; callers own output capture and scheduling.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any, Iterable

sys.dont_write_bytecode = True


@dataclass(frozen=True)
class Definition:
    arity: int
    own: int
    calls: tuple[tuple[int | str, tuple[int, ...]], ...]
    usual_added: bool


# A variable is identified by an invocation's raw call-index word and its
# local index.  Formal parameters are substituted before a variable is used.
Variable = tuple[tuple[int, ...], int]


@dataclass
class BlockSyntax:
    arity: int
    variables: list[Variable]
    constraints: list[tuple[Variable, ...]]
    retained_calls: list[tuple[int, tuple[Variable, ...]]]
    argument_uses: set[Variable]


def _integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def parse_key(key: str) -> tuple[Definition, ...]:
    """Validate raw local indices and apply precisely the census usual rule."""
    raw = json.loads(key)
    if not isinstance(raw, list) or not raw:
        raise ValueError("a family key must be a nonempty list of definitions")
    definitions: list[Definition] = []
    for index, item in enumerate(raw):
        if not isinstance(item, list) or len(item) != 3:
            raise ValueError(f"definition {index}: expected [arity, own, calls]")
        arity, own, body = item
        if not _integer(arity) or arity < 1 or not _integer(own) or own < 0:
            raise ValueError(f"definition {index}: invalid arity or own count")
        if not isinstance(body, list):
            raise ValueError(f"definition {index}: calls must be a list")
        calls: list[tuple[int | str, tuple[int, ...]]] = []
        for number, call in enumerate(body):
            if not isinstance(call, list) or len(call) != 2:
                raise ValueError(f"definition {index}, call {number}: invalid call")
            callee, args = call
            if callee == "K":
                required = 3
            elif callee == "SELF":
                if arity != 3:
                    raise ValueError("the census SELF grammar requires three ports")
                required = arity
            elif _integer(callee) and 0 <= callee < index:
                required = definitions[callee].arity
            else:
                raise ValueError(f"definition {index}, call {number}: invalid callee")
            if not isinstance(args, list) or len(args) != required:
                raise ValueError(f"definition {index}, call {number}: wrong argument count")
            if any(not _integer(a) or not 0 <= a < arity + own for a in args):
                raise ValueError(f"definition {index}, call {number}: invalid local index")
            calls.append((callee, tuple(args)))
        # This appends one occurrence, including when a matching K was already
        # present.  Repeated constraint occurrences remain repeated syntax.
        usual_added = any(c == "SELF" and len(a) == 3 and set(a) == {0, 1, 2}
                          for c, a in calls)
        if usual_added:
            calls.append(("K", (0, 1, 2)))
        definitions.append(Definition(arity, own, tuple(calls), usual_added))
    return tuple(definitions)


def _holding(definitions: tuple[Definition, ...]) -> set[int]:
    return {i for i, definition in enumerate(definitions)
            if any(c == "SELF" for c, _ in definition.calls)}


def _first_holding(definitions: tuple[Definition, ...], holding: set[int], start: int) -> int:
    # Reversing pushes preserves raw, depth-first call order without following
    # SELF recursively.  Repeated definition visits are harmless in this DAG.
    pending = [start]
    while pending:
        current = pending.pop()
        if current in holding:
            return current
        children = [c for c, _ in definitions[current].calls if _integer(c)]
        pending.extend(reversed(children))
    raise ValueError("family has no reachable SELF-holding definition")


def flatten_syntax(definitions: tuple[Definition, ...], start: int) -> BlockSyntax:
    """Substitute symbolic variables and retain *all* non-K argument uses.

    Each inlined invocation has a distinct call-index word, even when two
    calls have identical arguments.  Calls into a SELF-holding definition
    stay as calls.  Their bodies are not part of the current block.
    """
    holding = _holding(definitions)
    arity = definitions[start].arity
    variables: list[Variable] = [((), p) for p in range(arity)]
    constraints: list[tuple[Variable, ...]] = []
    retained: list[tuple[int, tuple[Variable, ...]]] = []
    used_as_argument: set[Variable] = set()

    def substitute(definition_index: int, actual: tuple[Variable, ...],
                   invocation: tuple[int, ...]) -> None:
        definition = definitions[definition_index]
        local = [(invocation, p) for p in
                 range(definition.arity, definition.arity + definition.own)]
        variables.extend(local)
        environment = actual + tuple(local)
        for call_index, (callee, arguments) in enumerate(definition.calls):
            mapped = tuple(environment[p] for p in arguments)
            if callee == "K":
                constraints.append(mapped)
                continue
            # Record a use before deciding whether to inline the callee.
            used_as_argument.update(mapped)
            if callee == "SELF":
                retained.append((definition_index, mapped))
            elif callee in holding:
                retained.append((callee, mapped))
            else:
                substitute(callee, mapped, invocation + (call_index,))

    substitute(start, tuple(variables), ())
    if len(set(variables)) != len(variables):
        raise ValueError("independent inlining reused an own variable identity")
    return BlockSyntax(arity, variables, constraints, retained, used_as_argument)


def _scope(definitions: tuple[Definition, ...], S: int, main: int) -> dict[str, Any]:
    """Recompute the two declared scope predicates, without allowed states."""
    holding = _holding(definitions)
    own_counts: list[int] = []
    for definition in definitions:
        own_counts.append(definition.own + sum(own_counts[c]
                          for c, _ in definition.calls
                          if _integer(c) and c not in holding))

    def reachable(start: int) -> set[int]:
        found: set[int] = set()
        todo = [start]
        while todo:
            current = todo.pop()
            if current not in found:
                found.add(current)
                todo.extend(c for c, _ in definitions[current].calls if _integer(c))
        return found

    from_S, from_main = reachable(S), reachable(main)
    others = sorted((holding & (from_S | from_main)) - {S})
    other_own = [i for i in others if own_counts[i] > 0]
    delayed = [i for i in others if S in reachable(i)]
    return {
        "in_scope": not other_own and not delayed,
        "other_own_types": other_own,
        "delaying_types": delayed,
        "other_own_from_S": any(i in from_S for i in other_own),
        "other_own_from_main": any(i in from_main for i in other_own),
        "wrapper": main != S,
    }


def _position(variable: Variable, arity: int) -> int | None:
    invocation, local_index = variable
    return local_index if not invocation and local_index < arity else None


def _syntax(block: BlockSyntax) -> dict[str, Any]:
    ids = {variable: i for i, variable in enumerate(block.variables)}
    own = set(block.variables[block.arity:])
    occurrences: Counter[Variable] = Counter()
    for constraint in block.constraints:
        occurrences.update(set(constraint))
    pendant = {variable for variable in own
               if occurrences[variable] == 1 and variable not in block.argument_uses}
    witnesses: list[dict[str, int]] = []
    for number, constraint in enumerate(block.constraints):
        if len(constraint) != 3 or len(set(constraint)) != 3:
            continue
        for variable in constraint:
            position = _position(variable, block.arity)
            if position is None:
                continue
            others = set(constraint) - {variable}
            if not others <= own:
                continue
            for z in sorted(others & pendant, key=ids.__getitem__):
                x = next(iter(others - {z}))
                witnesses.append({"position": position, "x": ids[x], "z": ids[z],
                                  "constraint": number})
    return {
        "arity": block.arity,
        "V": len(block.variables),
        "own_count": len(own),
        "knots": [[ids[v] for v in c] for c in block.constraints],
        "constraint_occurrences": {str(ids[v]): occurrences[v]
                                   for v in block.variables},
        "call_arguments": sorted(ids[v] for v in block.argument_uses),
        "pendant": sorted(ids[v] for v in pendant),
        "R1_positions": sorted({w["position"] for w in witnesses}),
        "R1_witnesses": witnesses,
    }


def _carried(definitions: tuple[Definition, ...], S: int, main: int,
             block: BlockSyntax, R1_positions: Iterable[int]) -> dict[str, Any]:
    if block.arity != 3:
        raise ValueError("R_s is specified only for three-port S")
    if main == S:
        current = frozenset(range(3))
    else:
        main_block = flatten_syntax(definitions, main)
        entries = [args for callee, args in main_block.retained_calls if callee == S]
        if not entries:
            raise ValueError("wrapper has no direct S entry after inlining")
        current = frozenset(j for args in entries for j, variable in enumerate(args)
                            if _position(variable, main_block.arity) is not None)
    maps = [tuple(_position(v, 3) for v in args)
            for callee, args in block.retained_calls if callee == S]
    if not maps:
        raise ValueError("S block has no onward S call")
    seen: dict[frozenset[int], int] = {}
    levels: list[frozenset[int]] = []
    while current not in seen:
        seen[current] = len(levels)
        levels.append(current)
        current = frozenset(child for call_map in maps for child, parent in enumerate(call_map)
                            if parent is not None and parent in current)
    preperiod = seen[current]
    period = len(levels) - preperiod
    eligible = set(R1_positions)
    residues = [{
        "residue": offset,
        "representative_depth": preperiod + offset,
        "s_mod_period": (preperiod + offset) % period,
        "carried_positions": sorted(positions),
        "mask": sum(1 << p for p in positions),
        "R1_positions_carried": sorted(eligible & positions),
        "R1_covered": bool(eligible & positions),
    } for offset, positions in enumerate(levels[preperiod:])]
    return {
        "preperiod": preperiod,
        "period": period,
        "masks": [sum(1 << p for p in positions) for positions in levels],
        "self_argument_maps": [list(call_map) for call_map in maps],
        "residues": residues,
    }


def check_family(key: str) -> dict[str, Any]:
    """Return exact R1 syntax and repeating R_s flags for one raw census key."""
    definitions = parse_key(key)
    main = len(definitions) - 1
    S = _first_holding(definitions, _holding(definitions), main)
    block = flatten_syntax(definitions, S)
    syntax = _syntax(block)
    carried = _carried(definitions, S, main, block, syntax["R1_positions"])
    covered = [phase["R1_covered"] for phase in carried["residues"]]
    every, some = all(covered), any(covered)
    return {
        "key": key,
        "implementation": "independent-raw-key-r1-v1",
        "status": "ok",
        "S": S,
        "main": main,
        "scope": _scope(definitions, S, main),
        "usual_added_definitions": [i for i, definition in enumerate(definitions)
                                    if definition.usual_added],
        "syntax": syntax,
        "carried": carried,
        "R1_every_residue": every,
        "R1_some_residue": some,
        "R1_progressions_only": some and not every,
        "R1_kind": "bounded" if every else "progressions" if some else "none",
    }


def aligned_residues(result: dict[str, Any], preperiod: int, period: int) -> list[dict[str, Any]]:
    """Align to another declared eventual period, without using its flags.

    For a requested progression preperiod+j modulo period, retain exactly the
    R_s phases with a compatible depth congruence.  This can be used to compare
    with CARRY window residues whose period is longer than R_s's period.
    """
    if not _integer(preperiod) or preperiod < 0 or not _integer(period) or period < 1:
        raise ValueError("invalid requested preperiod or period")
    sequence = result["carried"]
    divisor = math.gcd(period, sequence["period"])
    output = []
    for residue in range(period):
        phases = [phase for phase in sequence["residues"]
                  if (phase["representative_depth"] - preperiod - residue) % divisor == 0]
        if not phases:
            raise ValueError("no compatible R_s phase")
        output.append({
            "residue": residue,
            "s_mod_period": (preperiod + residue) % period,
            "carried_masks": sorted({phase["mask"] for phase in phases}),
            "R1_covered": all(phase["R1_covered"] for phase in phases),
            "R1_on_some_phase": any(phase["R1_covered"] for phase in phases),
        })
    return output


def controls() -> dict[str, Any]:
    """Hand-specified syntax controls; called only by explicit CLI/API use."""
    K = lambda *args: ["K", list(args)]
    SELF = lambda *args: ["SELF", list(args)]
    cases = [
        ("one_pendant_suffices", [[3, 3, [K(0, 3, 4), K(3, 1, 5), SELF(0, 3, 5)]]],
         {"positions": [0], "kind": "bounded", "pendant": [4]}),
        ("two_pendants", [[3, 2, [K(0, 3, 4), SELF(0, 1, 2)]]],
         {"positions": [0], "kind": "bounded", "pendant": [3, 4]}),
        ("own_call_arguments_disqualify", [[3, 2, [K(0, 3, 4), SELF(0, 3, 4)]]],
         {"positions": [], "kind": "none", "pendant": []}),
        ("second_constraint_disqualifies", [[3, 2, [K(0, 3, 4), K(0, 3, 4), SELF(0, 1, 2)]]],
         {"positions": [], "kind": "none", "pendant": []}),
        ("inlined_call_arguments_disqualify",
         [[3, 0, [K(0, 1, 2)]], [3, 2, [[0, [0, 3, 4]], SELF(0, 1, 2)]]],
         {"positions": [], "kind": "none", "pendant": []}),
        ("unconstraining_call_arguments_still_disqualify",
         [[3, 0, []], [3, 2, [K(0, 3, 4), [0, [3, 4, 0]], SELF(0, 1, 2)]]],
         {"positions": [], "kind": "none", "pendant": []}),
        ("own_created_inside_inline_call",
         [[3, 2, [K(0, 3, 4)]], [3, 0, [[0, [0, 1, 2]], SELF(0, 1, 2)]]],
         {"positions": [0], "kind": "bounded", "pendant": [3, 4]}),
        ("two_inline_invocations_have_distinct_own_variables",
         [[3, 2, [K(0, 3, 4)]],
          [3, 0, [[0, [0, 1, 2]], [0, [1, 2, 0]], SELF(0, 1, 2)]]],
         {"positions": [0, 1], "kind": "bounded", "pendant": [3, 4, 5, 6], "own_count": 4}),
        ("two_phase_progressions_only",
         [[3, 2, [K(0, 3, 4), SELF(1, 0, 3)]], [3, 2, [[0, [0, 3, 4]]]]],
         {"positions": [0], "kind": "progressions", "masks": [1, 2], "period": 2}),
        ("all_wrapper_entries_are_used",
         [[3, 2, [K(0, 3, 4), SELF(1, 0, 3)]],
          [3, 2, [[0, [0, 3, 4]], [0, [3, 1, 4]]]]],
         {"positions": [0], "kind": "bounded", "masks": [3], "period": 1}),
        ("transient_coverage_does_not_count",
         [[3, 3, [K(0, 3, 4), SELF(1, 3, 5)]]],
         {"positions": [0], "kind": "none", "masks": [7, 1, 0], "preperiod": 2}),
        ("third_member_port_does_not_qualify",
         [[3, 1, [K(0, 1, 3), SELF(0, 1, 2)]]],
         {"positions": [], "kind": "none"}),
        ("usual_port_constraint_does_not_qualify",
         [[3, 0, [SELF(2, 0, 1)]]],
         {"positions": [], "kind": "none"}),
        ("other_holding_own_is_out_of_scope",
         [[3, 1, [K(0, 1, 3), SELF(0, 1, 2)]],
          [3, 2, [K(0, 3, 4), SELF(0, 1, 2), [0, [0, 1, 2]]]]],
         {"positions": [0], "kind": "bounded", "in_scope": False}),
        ("another_holding_type_delays_S",
         [[3, 2, [K(0, 3, 4), SELF(0, 1, 2)]],
          [3, 0, [SELF(0, 1, 2), [0, [0, 1, 2]]]],
          [3, 0, [[0, [0, 1, 2]], [1, [0, 1, 2]]]]],
         {"positions": [0], "kind": "bounded", "in_scope": False}),
    ]
    rows = []
    progression = None
    for name, raw, expected in cases:
        result = check_family(json.dumps(raw, separators=(",", ":")))
        observed = {
            "positions": result["syntax"]["R1_positions"], "kind": result["R1_kind"],
            "pendant": result["syntax"]["pendant"], "own_count": result["syntax"]["own_count"],
            "masks": result["carried"]["masks"], "period": result["carried"]["period"],
            "preperiod": result["carried"]["preperiod"], "in_scope": result["scope"]["in_scope"],
        }
        observed = {k: observed[k] for k in expected}
        rows.append({"name": name, "expected": expected, "observed": observed,
                     "passed": observed == expected})
        if name == "two_phase_progressions_only":
            progression = result
    aligned = aligned_residues(progression, 3, 2)
    observed = [row["R1_covered"] for row in aligned]
    rows.append({"name": "alignment_respects_absolute_depth", "expected": [False, True],
                 "observed": observed, "passed": observed == [False, True]})
    aligned = aligned_residues(progression, 0, 1)
    observed = {k: aligned[0][k] for k in ("R1_covered", "R1_on_some_phase")}
    expected = {"R1_covered": False, "R1_on_some_phase": True}
    rows.append({"name": "alignment_does_not_promote_one_phase_to_all", "expected": expected,
                 "observed": observed, "passed": observed == expected})
    return {"passed": all(row["passed"] for row in rows), "controls": rows}


def _keys_from_census(path: Path) -> list[str]:
    latest = {}
    with path.open() as stream:
        for line in stream:
            if line.strip():
                row = json.loads(line)
                latest[row["case"]] = row
    if any(row["status"] != "ok" for row in latest.values()):
        raise ValueError("census input has a final non-ok record")
    keys = [key for key, row in latest.items()
            if not row["result"]["chain"]
            and row["result"]["verdict"] in ("non-forgetting", "capped")]
    return sorted(keys, key=lambda key: hashlib.sha256(("CARRY:" + key).encode()).hexdigest())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--controls", action="store_true")
    source.add_argument("--census", type=Path, help="CENSUS-FORGET runner results JSONL")
    source.add_argument("--keys-jsonl", type=Path, help="JSON strings or objects with key/case")
    arguments = parser.parse_args(argv)
    if arguments.controls:
        result = controls()
        print(json.dumps(result, sort_keys=True, allow_nan=False))
        return 0 if result["passed"] else 1
    if arguments.census is not None:
        keys = _keys_from_census(arguments.census)
    else:
        keys = []
        with arguments.keys_jsonl.open() as stream:
            for line in stream:
                if line.strip():
                    value = json.loads(line)
                    keys.append(value if isinstance(value, str) else
                                value["key"] if "key" in value else value["case"])
    failed = False
    for key in keys:
        try:
            result = check_family(key)
        except Exception as error:
            failed = True
            result = {"key": key, "status": "error", "error_type": type(error).__name__,
                      "error": str(error)}
        print(json.dumps(result, sort_keys=True, allow_nan=False), flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
