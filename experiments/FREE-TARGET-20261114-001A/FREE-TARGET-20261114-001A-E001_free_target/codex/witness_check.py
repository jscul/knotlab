"""Independent gate (b): direct unfolded CNF and SAT, without table joins.

The producer's marked relations and compiled boundary maps are never used to
decide a witness.  The retained finite schema is used only to locate actual
introduced variables.  Each required copy is expanded directly from the
authorized flattened body; every unopened call is read by its exact limit G.
Actual argument identities, including repeated ports, are substituted before
the SAT queries.
"""
from __future__ import annotations

from itertools import product
from pathlib import Path
import os
import sys
import time

sys.dont_write_bytecode = True


DEFAULT_LIMITS = dict(seconds=1500.0, memory_bytes=5800000000, replay_depth=2000,
                      copies=50000, clauses=2000000, witness_steps=1000000,
                      profile_expansions=100000, sat_calls=2000000)


class _Limit(RuntimeError):
    def __init__(self, detail, reason="cap"):
        super().__init__(detail)
        self.reason = reason


class _Guard:
    def __init__(self, checkpoint, limits):
        self.config = dict(DEFAULT_LIMITS)
        self.external = None
        if isinstance(limits, dict):
            self.config.update({k: v for k, v in limits.items() if k in self.config})
        elif limits is not None:
            self.external = limits.checkpoint
        self.callback = checkpoint
        self.started, self.ticks, self.peak = time.monotonic(), 0, 0
        self.sat_calls = 0

    def check(self, force=False):
        self.callback()
        if self.external is not None:
            self.external()
        self.ticks += 1
        if not force and self.ticks % 128:
            return
        try:
            rss = int(Path("/proc/self/statm").read_text().split()[1]) * os.sysconf("SC_PAGE_SIZE")
        except (FileNotFoundError, IndexError, ValueError):
            rss = 0
        self.peak = max(self.peak, rss)
        if rss >= self.config["memory_bytes"]:
            raise _Limit("independent witness replay RSS ceiling reached", "memory")
        if time.monotonic() - self.started >= self.config["seconds"]:
            raise _Limit("independent witness replay internal time ceiling reached")

    def cap(self, key, value):
        self.check()
        if value > self.config[key]:
            raise _Limit(f"witness replay {key} {value} exceeds explicit cap {self.config[key]}")


def _word(certificate, depth):
    prefix, cycle = certificate["prefix"], certificate["cycle"]
    if depth < len(prefix):
        return prefix[depth]
    return cycle[(depth - len(prefix)) % len(cycle)]


def _expected_subset(certificate, depth):
    trace = certificate["automaton"]["subsets"]
    first = len(certificate["prefix"])
    if depth < first:
        return set(trace[depth])
    return set(trace[first + (depth - first) % len(certificate["cycle"])])


class _Schema:
    def __init__(self, prep, certificate, guard):
        self.prep, self.certificate, self.guard = prep, certificate, guard
        self.automaton = certificate["automaton"]
        self.operations = {int(k): v for k, v in self.automaton["operations"].items()}
        self.profiles = {int(k): v for k, v in self.automaton["profiles"].items()}
        self.closing = {int(k): v for k, v in self.automaton["closing"].items()}
        self.states = {int(k): v for k, v in self.automaton["states"].items()}
        self.blocks = {}
        self.edges = {}
        for row in self.automaton["edges"]:
            self.edges.setdefault((row["source"], row["call"]), []).append((row["target"], row["operation"]))
        self.profile_expansions = 0
        self.flat_calls = [j for j, (c, _) in enumerate(self.block(prep.S)["calls"]) if c == prep.S]

    def block(self, typ):
        if typ not in self.blocks:
            self.blocks[typ] = self.prep.flat(typ)
        return self.blocks[typ]

    def children(self, typ):
        return [(j, c, args) for j, (c, args) in enumerate(self.block(typ)["calls"]) if c != "K"]

    def structural_mismatches(self):
        c, a, errors = self.certificate, self.automaton, []
        if c.get("main") != self.prep.main or c.get("S") != self.prep.S or self.prep.main != self.prep.S:
            errors.append(dict(kind="main_or_target_type", detail="certificate must use the unambiguous main == S case"))
        if c.get("k") not in (3, 4, 5):
            errors.append(dict(kind="budget", value=c.get("k")))
        if not c["cycle"] or any(type(j) is not int or not 0 <= j < len(self.flat_calls)
                                 for j in c["prefix"] + c["cycle"]):
            errors.append(dict(kind="path", detail="invalid nonempty call cycle"))
            return errors
        if type(c.get("onset")) is not int or c["onset"] < 1:
            errors.append(dict(kind="onset", value=c.get("onset")))
        calls = [dict(call_index=i, flat_call_index=j,
                      arguments=list(self.block(self.prep.S)["calls"][j][1]))
                 for i, j in enumerate(self.flat_calls)]
        if c.get("self_calls") != calls:
            errors.append(dict(kind="self_call_source", expected=calls, recorded=c.get("self_calls")))
        trace, start = a["subsets"], len(c["prefix"])
        if len(trace) != start + len(c["cycle"]) + 1 or a.get("cycle_start") != start:
            errors.append(dict(kind="subset_trace_shape"))
        elif set(trace[-1]) != set(trace[start]):
            errors.append(dict(kind="subset_cycle_return"))
        else:
            starts = {row["state"] for row in a["starts"]}
            if starts != set(trace[0]):
                errors.append(dict(kind="initial_subset", expected=sorted(starts), recorded=trace[0]))
            for depth, label in enumerate(c["prefix"] + c["cycle"]):
                actual = {v for u in trace[depth] for v, _ in self.edges.get((u, label), ())}
                if actual != set(trace[depth + 1]):
                    errors.append(dict(kind="subset_transition", depth=depth, call=label,
                                       missing=sorted(set(trace[depth + 1]) - actual),
                                       extra=sorted(actual - set(trace[depth + 1]))))
                if depth >= start and not any(state in self.closing for state in trace[depth]):
                    errors.append(dict(kind="nonaccepting_cycle_step", depth=depth))
        for state, values in self.states.items():
            if len(values) != 3 or not 1 <= int(values[2]) < c["k"]:
                errors.append(dict(kind="state_shape", state=state))
        for row in a["starts"]:
            top = row["top_ports"]
            if not top or len(set(top)) != len(top) or any(j not in range(3) for j in top):
                errors.append(dict(kind="top_identities", state=row["state"], top=top))
        # Origins are checked without evaluating any marked truth table.
        # A zero-mark origin is an unopened G boundary, not a recursive loop.
        done, active = set(), set()

        def visit(number):
            if number in done:
                return
            if number in active:
                raise ValueError("cyclic finite marked-profile witness")
            active.add(number)
            record = self.profiles[number]
            block = self.block(record["type"])
            count = record["count"]
            if count == 0:
                if record["own"] is not None or record["children"] is not None:
                    raise ValueError("zero-mark profile must be a G boundary")
                exact = sum(1 << i for i, allowed in enumerate(self.prep.G[record["type"]]) if allowed)
                if int(record["relation"], 16) != exact:
                    errors.append(dict(kind="zero_profile_G", profile=number))
            else:
                owned, children = record["own"], record["children"]
                if owned is None or children is None:
                    raise ValueError("positive marked profile lacks a concrete origin")
                if len(owned) != len(set(owned)) or any(not block["k"] <= j < block["V"] for j in owned):
                    raise ValueError("profile marks must be distinct introduced variables")
                source = self.children(record["type"])
                if len(children) != len(source):
                    raise ValueError("profile child count differs from flattened source")
                total = len(owned)
                for child, (_, callee, _) in zip(children, source):
                    visit(child)
                    if self.profiles[child]["type"] != callee:
                        raise ValueError("profile child type differs from flattened call")
                    total += self.profiles[child]["count"]
                if total != count or not 0 < count <= c["k"] - 2:
                    raise ValueError("profile mark budget or count mismatch")
            active.remove(number)
            done.add(number)

        for number in sorted(self.profiles):
            visit(number)
        for number, record in self.operations.items():
            owned, children, continued = record["own"], record["children"], record["continued"]
            block = self.block(self.prep.S)
            if len(set(owned)) != len(owned) or any(not block["k"] <= j < block["V"] for j in owned):
                errors.append(dict(kind="operation_owned_identities", operation=number))
            source = self.children(self.prep.S)
            if len(source) != len(children):
                raise ValueError("operation child count differs from flattened source")
            if continued is not None and (type(continued) is not int or not 0 <= continued < len(self.flat_calls)):
                raise ValueError("invalid operation continuation")
            flat_continued = None if continued is None else self.flat_calls[continued]
            total = len(owned)
            for child, (flat_j, callee, _) in zip(children, source):
                if flat_j == flat_continued:
                    if child != -1:
                        errors.append(dict(kind="continuation_was_not_open", operation=number))
                    continue
                if child not in self.profiles or self.profiles[child]["type"] != callee:
                    raise ValueError("operation child profile differs from flattened source")
                total += self.profiles[child]["count"]
            if total != record["count"]:
                errors.append(dict(kind="operation_count", operation=number, expected=total,
                                   recorded=record["count"]))
            if continued is None and not owned:
                errors.append(dict(kind="closing_lacks_target_own", operation=number))
        for (source, label), targets in self.edges.items():
            for target, operation in targets:
                if source not in self.states or target not in self.states or operation not in self.operations:
                    raise ValueError("edge references a missing state or operation")
                if self.operations[operation]["continued"] != label:
                    errors.append(dict(kind="edge_call_label", source=source, target=target, call=label))
        for state, operation in self.closing.items():
            if state not in self.states or self.operations[operation]["continued"] is not None:
                errors.append(dict(kind="closing_reference", state=state, operation=operation))
        return errors

    def profile_members(self, number, anchor, relative):
        result, pending = [], [(number, tuple(relative))]
        while pending:
            profile, address = pending.pop()
            self.profile_expansions += 1
            self.guard.cap("profile_expansions", self.profile_expansions)
            record = self.profiles[profile]
            if record["count"] == 0:
                continue
            result.extend(dict(anchor=anchor, relative_path=list(address), var=j) for j in record["own"])
            for child, (flat_j, _, _) in zip(record["children"], self.children(record["type"])):
                if self.profiles[child]["count"]:
                    pending.append((child, address + (flat_j,)))
        return result

    def operation_members(self, number, anchor):
        record = self.operations[number]
        result = [dict(anchor=anchor, relative_path=[], var=j) for j in record["own"]]
        for child, (flat_j, _, _) in zip(record["children"], self.children(self.prep.S)):
            if child >= 0 and self.profiles[child]["count"]:
                result.extend(self.profile_members(child, anchor, (flat_j,)))
        return result

    def members(self, depth, top, run, closing):
        operations = []
        while run is not None:
            previous, operation = run
            operations.append(operation)
            run = previous
        operations.reverse()
        if len(operations) != depth:
            raise ValueError("NFA witness run has the wrong depth")
        result = [dict(anchor=0, relative_path=[], var=j, top=True) for j in top]
        for anchor, operation in enumerate(operations):
            if self.operations[operation]["continued"] != _word(self.certificate, anchor):
                raise ValueError("concrete witness run follows the wrong call")
            result.extend(self.operation_members(operation, anchor))
        result.extend(self.operation_members(closing, depth))
        return result

    def flat_path(self, depth):
        return tuple(self.flat_calls[_word(self.certificate, i)] for i in range(depth))

    def member_flags(self, member, target_depth):
        anchor, relative = member["anchor"], member["relative_path"]
        on_path = all(flat_j == self.flat_calls[_word(self.certificate, anchor + offset)]
                      for offset, flat_j in enumerate(relative))
        return dict(on_path=on_path, side=not on_path,
                    beyond_target=anchor + len(relative) > target_depth)

    def unfold(self, members, target_depth):
        """Expand a prefix-closed finite set of copies, directly to CNF."""
        root = dict(children={}, marks=[], target=False)
        target_path = self.flat_path(target_depth)

        def insert(address):
            node = root
            for flat_j in address:
                node = node["children"].setdefault(flat_j, dict(children={}, marks=[], target=False))
            return node

        insert(target_path)["target"] = True
        for index, member in enumerate(members):
            anchor = member["anchor"]
            if type(anchor) is not int or not 0 <= anchor <= target_depth:
                raise ValueError("invalid member anchor")
            address = self.flat_path(anchor) + tuple(member["relative_path"])
            insert(address)["marks"].append((index, member["var"]))
        p = self.block(self.prep.main)["k"]
        next_variable = p
        root_ports = list(range(1, p + 1))
        pending = [(root, self.prep.main, root_ports)]
        clauses, variables, copies, target_own, target_ports = [], {}, 0, None, None
        while pending:
            node, typ, supplied = pending.pop()
            block = self.block(typ)
            if len(supplied) != block["k"]:
                raise ValueError("unfolded call has the wrong port arity")
            owned = list(range(next_variable + 1, next_variable + 1 + block["V"] - block["k"]))
            next_variable += len(owned)
            env = list(supplied) + owned
            copies += 1
            self.guard.cap("copies", copies)
            if node["target"]:
                target_own, target_ports = owned, list(supplied)
            for index, local in node["marks"]:
                if type(local) is not int or not 0 <= local < len(env):
                    raise ValueError("member variable is outside its introduction copy")
                variables[index] = env[local]
            unconsumed = set(node["children"])
            for flat_j, (callee, args) in enumerate(block["calls"]):
                actual = [env[x] for x in args]
                if callee == "K":
                    clauses.append(actual)
                    clauses.append([-x for x in actual])
                elif flat_j in node["children"]:
                    pending.append((node["children"][flat_j], callee, actual))
                    unconsumed.remove(flat_j)
                else:
                    # Direct truth-table-to-CNF conversion at this exact
                    # boundary.  No producer table or projection is used.
                    for word, allowed in enumerate(self.prep.G[callee]):
                        if not allowed:
                            clauses.append([-v if (word >> bit) & 1 else v
                                            for bit, v in enumerate(actual)])
                self.guard.cap("clauses", len(clauses))
            if unconsumed:
                raise ValueError("a witness address is not a child call in the flattened body")
        if len(variables) != len(members) or target_own is None:
            raise ValueError("unfolding did not reach every member and the target")
        return dict(clauses=clauses, variables=[variables[j] for j in range(len(members))],
                    root_ports=root_ports, target_own=target_own, target_ports=target_ports,
                    copies=copies, n_variables=next_variable)


def _sat_projection(unfolded, guard):
    from pysat.solvers import Solver
    variables, clauses = unfolded["variables"], unfolded["clauses"]
    size, allowed, deleted = len(variables), 0, []
    with Solver(name="cadical153", bootstrap_with=clauses) as solver:
        def sat(selected, word):
            guard.sat_calls += 1
            guard.cap("sat_calls", guard.sat_calls)
            assumptions = [variable if (word >> bit) & 1 else -variable
                           for bit, variable in enumerate(selected)]
            return bool(solver.solve(assumptions=assumptions))

        for word in range(1 << size):
            if sat(variables, word):
                allowed |= 1 << word
        # Re-query every proper projection directly under its own assumptions;
        # do not infer these verdicts from the full projected relation.
        for erase in range(size):
            selected = variables[:erase] + variables[erase + 1:]
            missing = [word for word in range(1 << len(selected)) if not sat(selected, word)]
            deleted.append(dict(erased=erase, shattered=not missing, missing=missing))
    return dict(relation=hex(allowed), nonempty=bool(allowed),
                non_shattered=allowed != (1 << (1 << size)) - 1,
                one_forgotten=deleted, minimal=all(row["shattered"] for row in deleted))


def check(prep, certificate, checkpoint=lambda: None, limits=None):
    """Check every depth 1..onset+2 periods, reporting every mismatch found.

    The literal gate includes depths before onset.  A missing early witness
    is therefore a mismatch even though it is outside the eventual claim.
    """
    guard = _Guard(checkpoint, limits)
    result = dict(passed=False, mismatches=[], depths=[], reason=None,
                  method="direct flattened-block CNF plus G at unopened calls; independent SAT projections")
    try:
        guard.check(force=True)
        schema = _Schema(prep, certificate, guard)
        result["mismatches"].extend(schema.structural_mismatches())
        # A malformed path/schema cannot be interpreted safely.  Retain all
        # structural mismatches already found instead of guessing a meaning.
        if result["mismatches"]:
            result["reason"] = "mismatch"
            return result
        last = certificate["onset"] + 2 * len(certificate["cycle"])
        guard.cap("replay_depth", last)
        result["required_last_depth"] = last
        frontier = {row["state"]: (tuple(row["top_ports"]), None)
                    for row in certificate["automaton"]["starts"]}
        steps = len(frontier)
        for depth in range(1, last + 1):
            label = _word(certificate, depth - 1)
            following = {}
            for source in sorted(frontier):
                top, run = frontier[source]
                for target, operation in schema.edges.get((source, label), ()):
                    following.setdefault(target, (top, (run, operation)))
            frontier = following
            steps += len(frontier)
            guard.cap("witness_steps", steps)
            expected = _expected_subset(certificate, depth)
            if set(frontier) != expected:
                result["mismatches"].append(dict(kind="replay_subset", depth=depth,
                    missing=sorted(expected - set(frontier)), extra=sorted(set(frontier) - expected)))
            accepted = next((state for state in sorted(frontier) if state in schema.closing), None)
            if accepted is None:
                result["mismatches"].append(dict(kind="missing_witness", depth=depth,
                                                 before_onset=depth < certificate["onset"]))
                result["depths"].append(dict(depth=depth, passed=False, reason="missing_witness"))
                continue
            top, run = frontier[accepted]
            members = schema.members(depth, top, run, schema.closing[accepted])
            unfolded = schema.unfold(members, depth)
            actual = unfolded["variables"]
            row = dict(depth=depth, members=members, support_size=len(actual),
                       copies=unfolded["copies"], variables=unfolded["n_variables"],
                       clauses=len(unfolded["clauses"]), state=accepted)
            local_errors = []
            if len(set(actual)) != len(actual):
                local_errors.append(dict(kind="repeated_member_identity", variables=actual))
            if not 3 <= len(actual) <= certificate["k"]:
                local_errors.append(dict(kind="support_budget", size=len(actual), k=certificate["k"]))
            has_top = bool(set(actual) & set(unfolded["root_ports"]))
            has_target = bool(set(actual) & set(unfolded["target_own"]))
            row.update(has_main_port=has_top, has_target_own=has_target)
            if not has_top:
                local_errors.append(dict(kind="missing_main_port"))
            if not has_target:
                local_errors.append(dict(kind="missing_target_own"))
            expected_size = schema.states[accepted][2] + schema.operations[schema.closing[accepted]]["count"]
            if len(actual) != expected_size:
                local_errors.append(dict(kind="state_member_count", expected=expected_size, actual=len(actual)))
            if len(set(actual)) == len(actual) and 3 <= len(actual) <= certificate["k"]:
                projection = _sat_projection(unfolded, guard)
                row.update(projection)
                if not projection["nonempty"]:
                    local_errors.append(dict(kind="K3_empty"))
                if not projection["non_shattered"]:
                    local_errors.append(dict(kind="K1_shattered"))
                for deletion in projection["one_forgotten"]:
                    if not deletion["shattered"]:
                        local_errors.append(dict(kind="K2_not_minimal", erased=deletion["erased"],
                                                 missing=deletion["missing"]))
            flags = [schema.member_flags(member, depth) for member in members]
            selected_top = set(actual) & set(unfolded["root_ports"])
            row.update(uses_side_member=any(flag["side"] for flag in flags),
                       uses_beyond_target=any(flag["beyond_target"] for flag in flags),
                       uses_carried_top=bool(selected_top & set(unfolded["target_ports"])),
                       target_port_identities=[(unfolded["root_ports"].index(v)
                                                if v in unfolded["root_ports"] else None)
                                               for v in unfolded["target_ports"]],
                       member_positions=flags, passed=not local_errors)
            result["depths"].append(row)
            result["mismatches"].extend(dict(error, depth=depth) for error in local_errors)
            guard.check()
        result["passed"] = not result["mismatches"]
        result["reason"] = None if result["passed"] else "mismatch"
        result["features"] = dict(
            uses_side_member=any(row.get("uses_side_member") for row in result["depths"]),
            uses_beyond_target=any(row.get("uses_beyond_target") for row in result["depths"]),
            all_depths_use_carried_top=bool(result["depths"]) and all(row.get("uses_carried_top") for row in result["depths"]))
    except Exception as error:
        reason = getattr(error, "reason", None)
        if reason in ("cap", "memory"):
            result["reason"] = reason
            result["mismatches"].append(dict(kind="resource_limit", reason=reason, detail=str(error)))
        elif isinstance(error, (ValueError, KeyError, IndexError, TypeError, RecursionError)):
            result["reason"] = "mismatch"
            result["mismatches"].append(dict(kind="schema_error", detail=str(error)))
        else:
            raise
    finally:
        result["seconds"] = round(time.monotonic() - guard.started, 6)
        result["peak_memory_bytes"] = guard.peak
        result["sat_calls"] = guard.sat_calls
        result["limits"] = guard.config
    return result
