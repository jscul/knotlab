"""Exact literal-port comparisons for sample_0:4710; no output files.

Replay: python3 -B <this file> [--json] [--skip-cli]
The default run prints a compact summary.  ``analyse()`` returns the complete
one/two-copy tables and the finite-orbit certificates for arbitrary block
lengths.  This component independently reads the archived definition and
uses tuple-valued assignments; it imports no predecessor's implementation.

Uniform means equality of the *whole* observed-output table for every full
root word sharing the retained raw input slots.  It does not mean equality
after averaging or existentially forgetting the unretained input first.
Knot means K1--K3 on distinct physical variables, with complement closure
also reported.  No finite-flip source or all-depth endpoint theorem is claimed.
"""

from collections import Counter, defaultdict
import argparse
import gzip
import hashlib
from itertools import combinations, product
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
SOURCE = (ROOT / "artifacts/LIMIT-ONLY-20261112-001A/"
          "LIMIT-ONLY-20261112-001A-E001_limit_only/sample_0.jsonl.gz")
EXPECTED = [3, 2, [
    ["K", [4, 3, 1]], ["SELF", [3, 0, 4]], ["K", [1, 3, 2]],
    ["SELF", [2, 1, 4]], ["SELF", [4, 2, 1]], ["K", [2, 4, 1]],
]]
PORTS = tuple(product((0, 1), repeat=3))
PAIRS = tuple(combinations(range(3), 2))


def text_word(word):
    return "".join(map(str, word))


def variable_name(index):
    return "abc"[index] if index < 3 else "xy"[(index - 3) % 2] + str((index - 3) // 2)


def project(rows, indices):
    return {tuple(row[i] for i in indices) for row in rows}


def knot_test(relation, arity):
    full_deletions = [len(project(relation, [j for j in range(arity) if j != i]))
                      == 2 ** (arity - 1) for i in range(arity)]
    nonempty = bool(relation)
    constrained = len(relation) < 2 ** arity
    complement_closed = all(tuple(1 - b for b in word) in relation for word in relation)
    return dict(arity=arity, states=len(relation), nonempty=nonempty,
                constrained=constrained, deletion_full=full_deletions,
                complement_closed=complement_closed,
                is_knot=arity >= 3 and nonempty and constrained and all(full_deletions))


def load_rule():
    with gzip.open(SOURCE, "rt") as source:
        record = next(json.loads(line) for n, line in enumerate(source, 1) if n == 4710)
    definition, = record["defs"]
    assert definition == EXPECTED
    return definition


def exact_local_words(definition):
    """Greatest fixed point, including the usual-limit pass-through knot."""
    pass_through = any(kind == "SELF" and set(args) == {0, 1, 2}
                       for kind, args in definition[2])
    allowed = set(PORTS)
    history = []
    while True:
        words = {w for w in product((0, 1), repeat=3 + definition[1])
                 if (not pass_through or len(set(w[:3])) > 1)
                 and all((len({w[i] for i in args}) > 1 if kind == "K"
                          else tuple(w[i] for i in args) in allowed)
                         for kind, args in definition[2])}
        new = {w[:3] for w in words}
        history.append(sorted(map(text_word, new)))
        if new == allowed:
            return allowed, words, pass_through, history
        allowed = new


def environments(definition, copies):
    first = next(args for kind, args in definition[2] if kind == "SELF")
    boundary = [0, 1, 2]
    envs = []
    for depth in range(copies):
        env = boundary + [3 + 2 * depth, 4 + 2 * depth]
        envs.append(env)
        boundary = [env[i] for i in first]
    return envs, boundary


def brute_words(definition, local, copies):
    envs, boundary = environments(definition, copies)
    words = {w for w in product((0, 1), repeat=3 + 2 * copies)
             if all(tuple(w[i] for i in env) in local for env in envs)}
    return words, boundary


def compare_fibres(root_observations, retained):
    conflicts = [(p, q) for p, q in combinations(PORTS, 2)
                 if tuple(p[i] for i in retained) == tuple(q[i] for i in retained)
                 and root_observations[p] != root_observations[q]]
    conflict = None
    if conflicts:
        p, q = conflicts[0]
        conflict = dict(left_input=text_word(p), right_input=text_word(q),
                        left_table=sorted(map(text_word, root_observations[p])),
                        right_table=sorted(map(text_word, root_observations[q])))
    return not conflicts, conflict


def physical_candidate(words, retained, boundary, output_slots, helper):
    observed = [boundary[i] for i in output_slots] + ([] if helper is None else [helper])
    support = list(dict.fromkeys([*retained, *observed]))
    by_root = {p: {tuple(w[i] for i in observed) for w in words if w[:3] == p}
               for p in PORTS}
    uniform, conflict = compare_fibres(by_root, retained)
    relation = project(words, support)
    return dict(input_slots=list(retained), output_slots=list(output_slots),
                outputs=[variable_name(boundary[i]) for i in output_slots],
                output_birth_depths=[None if boundary[i] < 3 else (boundary[i] - 3) // 2
                                     for i in output_slots],
                helper=None if helper is None else variable_name(helper),
                support=[variable_name(i) for i in support], uniform=uniform,
                conflict=conflict,
                conditional_tables={text_word(p): sorted(map(text_word, by_root[p])) for p in PORTS},
                relation=sorted(map(text_word, relation)), **knot_test(relation, len(support)))


def tally(candidates):
    return dict(candidates=len(candidates), uniform=sum(c["uniform"] for c in candidates),
                constrained=sum(c["constrained"] for c in candidates),
                marginal_knots=sum(c["is_knot"] for c in candidates),
                uniform_constrained=sum(c["uniform"] and c["constrained"] for c in candidates),
                uniform_knots=sum(c["uniform"] and c["is_knot"] for c in candidates))


def basic_comparison(definition, local, copies):
    words, boundary = brute_words(definition, local, copies)
    groups = {}
    for width in (1, 2, 3):
        for kind in ("output_helper", "output_pair", "output_pair_helper"):
            candidates = []
            for retained in combinations(range(3), width):
                outputs = ([(i,) for i in range(3) if boundary[i] >= 3]
                           if kind == "output_helper" else PAIRS)
                for slots in outputs:
                    used = {boundary[i] for i in slots}
                    helpers = ([None] if kind == "output_pair" else
                               [h for h in range(3, 3 + 2 * copies) if h not in used])
                    for helper in helpers:
                        candidates.append(physical_candidate(words, retained, boundary, slots, helper))
            groups[f"input_{width}_{kind}"] = dict(summary=tally(candidates), tests=candidates)
    carries = [dict(input_slot=name, output_slot=i) for i, name in enumerate(boundary) if name < 3]
    pair_carries = [dict(input_slots=list(p), output_slots=list(q)) for p in PAIRS for q in PAIRS
                    if set(p) == {boundary[i] for i in q}]
    return dict(copies=copies, variables=[variable_name(i) for i in range(3 + 2 * copies)],
                final_boundary=[variable_name(i) for i in boundary],
                assignments_before_constraints=2 ** (3 + 2 * copies), assignments=len(words),
                assignments_by_input={text_word(p): sum(w[:3] == p for w in words) for p in PORTS},
                literal_carries=carries, literal_pair_carries=pair_carries, groups=groups)


def compose(left, right):
    by_input = defaultdict(set)
    for middle, end in right:
        by_input[middle].add(end)
    return {(start, end) for start, middle in left for end in by_input[middle]}


def power_orbit(transition):
    powers, seen = [], {}
    current = {(p, p) for p in PORTS}
    while frozenset(current) not in seen:
        seen[frozenset(current)] = len(powers)
        powers.append(current)
        current = compose(current, transition)
    return powers, seen[frozenset(current)], len(powers) - seen[frozenset(current)]


def marked_compose(left, marked, right):
    marks, ends = defaultdict(set), defaultdict(set)
    for p, q, h in marked:
        marks[p].add((q, h))
    for p, q in right:
        ends[p].add(q)
    return {(p, r, h) for p, t in left for u, h in marks[t] for r in ends[u]}


def abstract_candidate(rows, retained, outputs, with_helper):
    """For blocks >=2, roots and final boundary are disjoint actual identities."""
    by_root = {p: {tuple(q[i] for i in outputs) + ((h,) if with_helper else ())
                   for pp, q, h in rows if pp == p} for p in PORTS}
    uniform, conflict = compare_fibres(by_root, retained)
    relation = {tuple(p[i] for i in retained) + tuple(q[i] for i in outputs)
                + ((h,) if with_helper else ()) for p, q, h in rows}
    arity = len(retained) + len(outputs) + int(with_helper)
    return dict(input_slots=list(retained), output_slots=list(outputs), uniform=uniform,
                conflict=conflict,
                conditional_tables={text_word(p): sorted(map(text_word, by_root[p])) for p in PORTS},
                relation=sorted(map(text_word, relation)),
                **knot_test(relation, arity))


def crossing_minimal_bonds(candidate, inputs=2, outputs=2):
    relation = {tuple(map(int, w)) for w in candidate["relation"]}
    arity = candidate["arity"]
    result = []
    for size in range(2, arity + 1):
        for support in combinations(range(arity), size):
            if (not set(support).intersection(range(inputs))
                    or not set(support).intersection(range(inputs, inputs + outputs))):
                continue
            table = project(relation, support)
            test = knot_test(table, size)
            if test["nonempty"] and test["constrained"] and all(test["deletion_full"]):
                result.append(list(support))
    return result


def simple_cycles(edges):
    adjacency = defaultdict(set)
    for left, right in edges:
        adjacency[tuple(left)].add(tuple(right))
    found = set()
    def visit(start, path):
        for end in adjacency[path[-1]]:
            if end == start:
                rotations = [tuple(path[i:] + path[:i]) for i in range(len(path))]
                found.add(min(rotations))
            elif end not in path:
                visit(start, path + [end])
    for start in list(adjacency):
        visit(start, [start])
    return [[list(p) for p in cycle] for cycle in sorted(found)]


def arbitrary_blocks(local, basics):
    transition = {(w[:3], (w[3], w[0], w[4])) for w in local}
    powers, repeat_start, period = power_orbit(transition)
    assert repeat_start == 6 and period == 1 and powers[6] == set(product(PORTS, repeat=2))
    unmarked = []
    edges = set()
    for c in basics[0]["groups"]["input_2_output_pair"]["tests"]:
        if c["uniform"] and c["constrained"]:
            edges.add((tuple(c["input_slots"]), tuple(c["output_slots"])))
    for n, relation in enumerate(powers[2:], 2):
        candidates = [abstract_candidate([(p, q, 0) for p, q in relation], retained, slots, False)
                      for retained in PAIRS for slots in PAIRS]
        for c in candidates:
            if c["uniform"] and c["constrained"]:
                edges.add((tuple(c["input_slots"]), tuple(c["output_slots"])))
        unmarked.append(dict(copies=n, summary=tally(candidates), tests=candidates))
    summaries = {kind: Counter() for kind in ("output_helper", "output_pair_helper")}
    uniform_knots, crossing_pair_helper, uniform_constrained = [], [], []
    classes = []
    for before, left in enumerate(powers):
        for after, right in enumerate(powers):
            copies = before + after + 1
            if copies == 1:  # Aliased root a is handled by the physical enumeration above.
                continue
            for helper_index in (3, 4):
                marked = {(w[:3], (w[3], w[0], w[4]), w[helper_index]) for w in local}
                rows = marked_compose(left, marked, right)
                counts = {}
                for kind in summaries:
                    candidates = []
                    for retained in PAIRS:
                        for slots in ([(i,) for i in range(3)] if kind == "output_helper" else PAIRS):
                            # x is carried for two boundary occurrences; y for one.
                            if ((after == 0 and ((helper_index == 3 and 0 in slots)
                                                 or (helper_index == 4 and 2 in slots)))
                                    or (after == 1 and helper_index == 3 and 1 in slots)):
                                continue
                            c = abstract_candidate(rows, retained, slots, True)
                            candidates.append(c)
                            _, physical_boundary = environments(EXPECTED, copies)
                            helper_physical = 3 + 2 * before + helper_index - 3
                            description = dict(before=before, after=after, copies=copies,
                                               helper_kind="xy"[helper_index - 3],
                                               helper_name=variable_name(helper_physical),
                                               helper_in_final_boundary=helper_physical in physical_boundary,
                                               output_names=[variable_name(physical_boundary[i]) for i in slots],
                                               output_birth_depths=[(physical_boundary[i] - 3) // 2 for i in slots],
                                               reaches_last_copy_own=any(physical_boundary[i] >= 3 + 2 * (copies - 1)
                                                                        for i in slots),
                                               kind=kind, **c)
                            if c["uniform"] and c["constrained"]:
                                uniform_constrained.append(description)
                            if c["uniform"] and c["is_knot"]:
                                uniform_knots.append(description)
                            if kind == "output_pair_helper" and c["uniform"]:
                                bonds = crossing_minimal_bonds(c)
                                if bonds:
                                    crossing_pair_helper.append(dict(bonds=bonds, **description))
                    counts[kind] = tally(candidates)
                    summaries[kind].update(counts[kind])
                classes.append(dict(before=before, after=after, copies=copies,
                                    helper_kind="xy"[helper_index - 3], states=len(rows), summaries=counts))
    assert not crossing_pair_helper
    assert edges == {((1, 2), (0, 2))} and not simple_cycles(edges)
    assert len(uniform_knots) == 3 and all(c["input_slots"] == [1, 2] for c in uniform_knots)
    return dict(power_sizes=[len(p) for p in powers], repeat_start=repeat_start, period=period,
                power_tables=[[[text_word(p), text_word(q)] for p, q in sorted(r)] for r in powers],
                unmarked_pair_tests=unmarked,
                explanation=("Every n>=6 has T^n=T^6. A helper introduced after j copies, with d later "
                             "copies, has exact table T^j M_h T^d. Checking j,d=0..6 therefore covers "
                             "all finite insertion positions and block lengths. The n=1 identity "
                             "aliases are checked separately; helpers equal to an output are excluded."),
                marked_class_count=len(classes), marked_classes=classes,
                marked_summaries={k: dict(v) for k, v in summaries.items()},
                uniform_marked_knots=uniform_knots,
                uniform_constrained_marked=uniform_constrained,
                uniform_pair_helper_crossing_minimal_bonds=crossing_pair_helper,
                constrained_uniform_pair_edges=[[list(a), list(b)] for a, b in sorted(edges)],
                pair_cycles=simple_cycles(edges),
                limitation=("This tests raw port pairs and zero or one physical helper owned on the "
                            "opened first branch. It does not cover maintained restrictions, recodings, "
                            "multiple helpers, or helpers in side descendants. A local knot or an "
                            "interface cycle would require a separate all-depth endpoint argument."))


def controls(local, basics, blocks):
    nae = {w for w in product((0, 1), repeat=3) if len(set(w)) > 1}
    pair_atom = set(product((0, 1), repeat=4)) - {(0, 0, 1, 1), (1, 1, 0, 0)}
    assert knot_test(nae, 3)["is_knot"] and knot_test(pair_atom, 4)["is_knot"]
    free = set(product((0, 1), repeat=4))
    assert not knot_test(free, 4)["is_knot"]
    old_pair = {(w[1], w[2], w[3], w[4]) for w in local}
    assert len(old_pair) == 8 and not knot_test(old_pair, 4)["is_knot"]
    # Positive full-input fibre fixture: NAE-four on p1,p2,q0,q2;
    # p0 and q1 remain free. Every full p has exactly its advertised table.
    fixture = {(p, q, 0) for p in PORTS for q in PORTS
               if (p[1], p[2], q[0], q[2]) in pair_atom}
    good = abstract_candidate(fixture, (1, 2), (0, 2), False)
    assert good["uniform"] and good["is_knot"]
    # A hidden spectator can preserve that marginal atom while breaking lifting.
    # q1 is unobserved, so remove both q1 completions of the same observation.
    wrong = {r for r in fixture if not (r[0] == (0, 0, 0) and (r[1][0], r[1][2]) == (0, 0))}
    bad = abstract_candidate(wrong, (1, 2), (0, 2), False)
    assert bad["is_knot"] and not bad["uniform"]
    actual_three = next(c for item in blocks["unmarked_pair_tests"] if item["copies"] == 3
                        for c in item["tests"] if c["uniform"] and c["is_knot"])
    assert set(actual_three["relation"]) == set(map(text_word, pair_atom))
    actual_marginal = next(c for c in basics[1]["groups"]["input_1_output_helper"]["tests"]
                           if c["is_knot"])
    assert not actual_marginal["uniform"]
    assert simple_cycles([((1, 2), (1, 2))]) == [[[1, 2]]]
    assert not simple_cycles([((1, 2), (0, 2))])
    # Independent full-word enumeration cross-checks unmarked and all marked
    # relations for blocks up to four, including actual identity aliases.
    definition = EXPECTED
    powers = [{(tuple(map(int, p)), tuple(map(int, q))) for p, q in rows}
              for rows in blocks["power_tables"]]
    transition_checks = []
    for copies in range(1, 5):
        words, boundary = brute_words(definition, local, copies)
        actual = {(w[:3], tuple(w[i] for i in boundary)) for w in words}
        assert actual == powers[copies]
        for birth in range(copies):
            for offset in (0, 1):
                helper = 3 + 2 * birth + offset
                direct = {(w[:3], tuple(w[i] for i in boundary), w[helper]) for w in words}
                marked = {(w[:3], (w[3], w[0], w[4]), w[3 + offset]) for w in local}
                assert direct == marked_compose(powers[birth], marked, powers[copies - birth - 1])
        transition_checks.append(dict(copies=copies, assignments=len(words),
                                      marked_helper_positions=2 * copies))
    return dict(positive_uniform_pair_atom=True, free_fails_K1=True,
                local_nonminimal_relation_fails_K2=True,
                hidden_spectator_preserves_marginal_but_fails_uniformity=True,
                cycle_positive_and_acyclic_negative=True,
                independent_full_word_checks=transition_checks,
                canonical_relations=dict(nae=nae, pair_atom=pair_atom, free=free, nonminimal=old_pair))


def canonical_checks(relations):
    results = {}
    env = dict(os.environ, PYTHONPATH=str(ROOT / "tools"))
    for label, relation in relations.items():
        arity = len(next(iter(relation)))
        names = ["A", "B", "C", "D"][:arity]
        forbidden = set(product((0, 1), repeat=arity)) - relation
        # A tautology keeps every declared variable in the free control's CNF.
        clauses = ([" ".join(("~" if bit else "") + name for bit, name in zip(w, names))
                    for w in sorted(forbidden)] or [f"{name} ~{name}" for name in names])
        command = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", ";".join(clauses),
                   "--loops", *names[:-1], "--contact", names[-1], "--json"]
        completed = subprocess.run(command, cwd=ROOT, env=env, check=True, text=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = json.loads(completed.stdout)
        assert result["allowed"] == sorted(map(text_word, relation))
        assert result["is_knot"] == knot_test(relation, arity)["is_knot"]
        results[label] = dict(cnf=";".join(clauses), **result)
    return results


def analyse(run_cli=True):
    definition = load_rule()
    allowed, local, pass_through, history = exact_local_words(definition)
    assert allowed == set(PORTS) and not pass_through and len(local) == 16
    basics = [basic_comparison(definition, local, copies) for copies in (1, 2)]
    assert basics[0]["assignments"] == 16 and basics[1]["assignments"] == 32
    assert basics[1]["groups"]["input_1_output_helper"]["summary"]["marginal_knots"] == 5
    assert basics[1]["groups"]["input_1_output_helper"]["summary"]["uniform"] == 0
    blocks = arbitrary_blocks(local, basics)
    checked = controls(local, basics, blocks)
    relations = checked.pop("canonical_relations")
    # Replay every distinct actual positive marginal table as well as controls.
    seen = {frozenset(r) for r in relations.values()}
    for block in basics:
        for group in block["groups"].values():
            for candidate in group["tests"]:
                if candidate["is_knot"]:
                    assert candidate["complement_closed"]
                    relation = frozenset(tuple(map(int, w)) for w in candidate["relation"])
                    if relation not in seen:
                        relations[f"actual_marginal_{len(seen)}"] = set(relation)
                        seen.add(relation)
    canonical = canonical_checks(relations) if run_cli else None
    return dict(source=str(SOURCE.relative_to(ROOT)), source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                source_line=4710, definition=definition, usual_limit_ports=sorted(map(text_word, allowed)),
                pass_through=pass_through, greatest_fixed_point_history=history,
                exact_local_words=sorted(map(text_word, local)), basic=basics,
                arbitrary_blocks=blocks, controls=checked, canonical_checks=canonical,
                validation="Independent same-task tuple enumeration and transfer construction; V1, no external replication.",
                native_at_infinite_solutions="Not assessed.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print all exact tables")
    parser.add_argument("--skip-cli", action="store_true", help="omit the separate knotlab subprocesses")
    args = parser.parse_args()
    result = analyse(not args.skip_cli)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(dict(
            root_table=result["usual_limit_ports"],
            basic=[dict(copies=b["copies"], assignments=b["assignments"],
                        root_counts=b["assignments_by_input"],
                        pair_retention={k: v["summary"] for k, v in b["groups"].items() if k.startswith("input_2_")})
                   for b in result["basic"]],
            powers=result["arbitrary_blocks"]["power_sizes"],
            uniform_marked_knots=result["arbitrary_blocks"]["uniform_marked_knots"],
            constrained_pair_edges=result["arbitrary_blocks"]["constrained_uniform_pair_edges"],
            pair_cycles=result["arbitrary_blocks"]["pair_cycles"], controls=result["controls"],
            canonical_verdicts=None if result["canonical_checks"] is None else
                {label: table["is_knot"] for label, table in result["canonical_checks"].items()}), indent=2))


if __name__ == "__main__":
    main()
