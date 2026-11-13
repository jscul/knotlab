"""Independent truth-table synthesis; never imports the study implementation.

Run each subcommand with the requested .venv Python, -B, and an external timeout.
Even-state witnesses are nonempty selections of complete helper assignments.
Complement invariance permits fixing named variable zero to zero.
"""
import argparse
import hashlib
import itertools as it
import json
from pathlib import Path
import resource
import time

from pysat.card import CardEnc, EncType
from pysat.solvers import Solver

HERE = Path(__file__).resolve().parent
resource.setrlimit(resource.RLIMIT_AS, (7 * 1024**3, 7 * 1024**3))


def parity(x):
    return x.bit_count() & 1


def triples(f):
    return [t for t in it.combinations(range(4 + f), 3) if max(t) >= 4]


def violates(a, t):
    b = [(a >> v) & 1 for v in t]
    return b[0] == b[1] == b[2]


def projected(f, gadget):
    return [x for x in range(16)
            if any(not any(violates(x | (y << 4), t) for t in gadget)
                   for y in range(1 << f))]


def formula(f, m, symmetry=False, reduced=False):
    ks = triples(f)
    cs = []
    top = len(ks)
    odd_covers = set()
    # All representatives with named variable 0 = 0, four even and four odd.
    for x in range(0, 16, 2):
        witness_ids = []
        for y in range(1 << f):
            bad = tuple(j + 1 for j, t in enumerate(ks)
                        if violates(x | (y << 4), t))
            if parity(x):
                odd_covers.add(bad)
            else:
                top += 1
                witness_ids.append(top)
                cs.extend([[-top, -j] for j in bad])
        if not parity(x):
            cs.append(witness_ids)
    cs.extend(map(list, sorted(odd_covers)))
    if reduced:
        # In a least-size definition no used helper has degree one: its
        # sole NAE constraint could be satisfied after assigning all others.
        # Degree zero is dropped. Every helper here is therefore used >=2.
        for u in range(4, 4 + f):
            incident = [j + 1 for j, t in enumerate(ks) if u in t]
            enc = CardEnc.atleast(incident, bound=2, top_id=top,
                                  encoding=EncType.totalizer)
            cs.extend(enc.clauses)
            top = enc.nv
        # A witness extending named 0000 must block each one-name flip.
        for u in range(4):
            cs.append([j + 1 for j, t in enumerate(ks)
                       if u in t and sum(v < 4 for v in t) == 1])
    if symmetry:
        index = {t: j + 1 for j, t in enumerate(ks)}
        # Lex leaders against adjacent helper transpositions. Every orbit's
        # globally least bit string satisfies these necessary comparisons.
        swaps = list(range(4, 3 + f))
        if reduced:
            swaps += [0, 1, 2]
        for u in swaps:
            perm = list(range(4 + f))
            perm[u], perm[u + 1] = perm[u + 1], perm[u]
            pairs = [(j + 1, index[tuple(sorted(perm[v] for v in t))])
                     for j, t in enumerate(ks)]
            pairs = [(a, b) for a, b in pairs if a != b]
            top += 1
            prefix = top
            cs.append([prefix])
            for a, b in pairs:
                cs.append([-prefix, -a, b])
                top += 1
                cs.append([-prefix, a, b, top])
                cs.append([-prefix, -a, -b, top])
                prefix = top
    if ks and m < len(ks):
        enc = CardEnc.atmost(list(range(1, len(ks) + 1)), bound=m,
                             top_id=top, encoding=EncType.totalizer)
        cs.extend(enc.clauses)
        top = enc.nv
    return ks, cs, top


def synthesize(f, m, symmetry=True, solver="cadical195", reduced=False):
    start = time.monotonic()
    ks, clauses, nv = formula(f, m, symmetry, reduced)
    digest = hashlib.sha256(json.dumps(clauses, separators=(",", ":")).encode()).hexdigest()
    # This wrapper's bootstrap path cannot accept an empty clause. Replace
    # each such contradiction by an inconsistent fresh pair of units.
    if [] in clauses:
        nv += 1
        clauses = [c for c in clauses if c] + [[nv], [-nv]]
    with Solver(name=solver, bootstrap_with=clauses) as sat:
        answer = sat.solve()
        stats = sat.accum_stats()
        chosen = None
        if answer:
            positives = {v for v in sat.get_model() if v > 0}
            chosen = [t for j, t in enumerate(ks, 1) if j in positives]
    rel = projected(f, chosen) if answer else None
    if answer:
        assert rel == [x for x in range(16) if not parity(x)]
        assert len(chosen) <= m
    return dict(f=f, bound=m, satisfiable=answer, gadget=chosen,
                projection=rel, selectors=len(ks), variables=nv,
                clauses=len(clauses), cnf_sha256=digest, solver=solver,
                helper_symmetry=symmetry, reduced=reduced,
                seconds=time.monotonic() - start,
                maxrss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                solver_stats=stats)


def enumerate_three():
    start = time.monotonic()
    ks, clauses, nv = formula(3, 12)
    gadgets = []
    with Solver(name="cadical195", bootstrap_with=clauses) as sat:
        while sat.solve():
            pos = {v for v in sat.get_model() if v > 0}
            ids = [j for j in range(1, len(ks) + 1) if j in pos]
            assert len(ids) == 12
            g = tuple(ks[j - 1] for j in ids)
            assert projected(3, g) == [x for x in range(16) if not parity(x)]
            gadgets.append(g)
            sat.add_clause([-j for j in ids])
    def orbits(permutations):
        remaining = set(gadgets)
        sizes, reps = [], []
        for seed in sorted(gadgets):
            if seed not in remaining:
                continue
            orb = {tuple(sorted(tuple(sorted(p[v] for v in t)) for t in seed))
                   for p in permutations}
            assert orb <= set(gadgets)
            remaining.difference_update(orb)
            sizes.append(len(orb))
            reps.append(min(orb))
        assert not remaining
        return dict(count=len(sizes), sizes=sorted(sizes), representatives=reps)
    helper_perms = [tuple(range(4)) + p for p in it.permutations(range(4, 7))]
    all_perms = [p + q for p in it.permutations(range(4))
                 for q in it.permutations(range(4, 7))]
    return dict(f=3, bound=12, enumeration_complete=True,
                labelled_count=len(gadgets), gadgets=gadgets,
                helper_relabelling=orbits(helper_perms),
                named_and_helper_relabelling=orbits(all_perms),
                seconds=time.monotonic() - start,
                maxrss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def summarize():
    case_files = sorted(HERE.glob("s1_f*_m*.json"))
    records = {p.name: json.loads(p.read_text()) for p in case_files}
    expected = {0: None, 1: None, 2: None, 3: 12, 4: 10, 5: 10, 6: 10}
    for f, m in expected.items():
        if m is None:
            bound = len(triples(f))
            assert records[f"s1_f{f}_m{bound}.json"]["satisfiable"] is False
        else:
            yes = records[f"s1_f{f}_m{m}.json"]
            no = records[f"s1_f{f}_m{m - 1}.json"]
            assert yes["satisfiable"] is True and no["satisfiable"] is False
            assert projected(f, yes["gadget"]) == [0, 3, 5, 6, 9, 10, 12, 15]
    for f in range(7, 12):
        case = records[f"s1_f{f}_m9_reduced.json"]
        assert case["reduced"] and case["satisfiable"] is False
    enumeration = json.loads((HERE / "s1_enumeration.json").read_text())
    assert enumeration["enumeration_complete"] and enumeration["labelled_count"] == 168
    assert enumeration["helper_relabelling"]["count"] == 28
    assert enumeration["named_and_helper_relabelling"]["sizes"] == [24, 72, 72]
    root = HERE.parents[3]
    original_path = root / "artifacts/CHEAP-COUNT-20261112-001A/CHEAP-COUNT-20261112-001A-E001_cheapest_counter/s1.json"
    original = json.loads(original_path.read_text())
    assert {int(f): row["m"] for f, row in original["table"].items()} == expected
    first = tuple(map(tuple, original["table"]["3"]["gadget"]))
    assert first in {tuple(map(tuple, g)) for g in enumeration["gadgets"]}
    crossed = []
    for name, second in records.items():
        if name.endswith("_glucose4.json"):
            primary = records[name.replace("_glucose4", "")]
            assert primary["cnf_sha256"] == second["cnf_sha256"]
            assert primary["satisfiable"] == second["satisfiable"] is False
            crossed.append(name)
    return dict(scope_kind="epic", scope_id="CHEAP-COUNT-20261112-001",
                scientific_role="Independent referee recomputation; no lifecycle changes",
                encoding="Full helper-assignment witness selections for even boundaries; covers for all odd extensions; complement representatives; totalizer and justified lex symmetry",
                table=expected, original_table_equal=True,
                labelled_minima=168, helper_orbits=28,
                named_helper_orbits=3, named_helper_orbit_sizes=[24, 72, 72],
                helper_bound={"for_m_at_most": 9, "useful_f_at_most": 11,
                              "proof": "Repeatedly delete degree-one helpers and their sole constraint, and discard degree-zero helpers. Existential projection is preserved. Four named variables must occur; remaining helpers have degree at least two. Thus 4+2f<=3m<=27.",
                              "extra_cases": list(range(7, 12)),
                              "extra_cases_unsatisfiable": True,
                              "global_minimum_knots": 10},
                cross_solver_cases=crossed,
                original_first_gadget_in_independent_enumeration=True,
                case_files=list(records),
                longest_case_seconds=max(r["seconds"] for r in records.values()),
                peak_case_rss_kib=max(r["maxrss_kib"] for r in records.values()),
                limits={"external_timeout_seconds": 570, "address_space_gib": 7},
                original_s1_sha256=hashlib.sha256(original_path.read_bytes()).hexdigest(),
                script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                validation="Independent implementation and two SAT solver engines on three selected UNSAT cases; no independently replayed UNSAT proof traces.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["case", "enumerate", "summarize"])
    parser.add_argument("--f", type=int)
    parser.add_argument("--m", type=int)
    parser.add_argument("--no-symmetry", action="store_true")
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--reduced", action="store_true")
    args = parser.parse_args()
    if args.mode == "case":
        out = synthesize(args.f, args.m, not args.no_symmetry, args.solver, args.reduced)
        name = (f"s1_f{args.f}_m{args.m}{'_reduced' if args.reduced else ''}"
                f"{'' if args.solver == 'cadical195' else '_' + args.solver}.json")
    elif args.mode == "enumerate":
        out = enumerate_three()
        name = "s1_enumeration.json"
    else:
        out = summarize()
        name = "s1_summary.json"
    (HERE / name).write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: v for k, v in out.items()
                      if k not in ("gadgets", "gadget", "projection", "solver_stats")}))


if __name__ == "__main__":
    main()
