"""Independent literal, reader, and fairness controls for the serial comparisons."""

from argparse import ArgumentParser
from collections import Counter, deque
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, product
import json
from pathlib import Path
from random import Random
from tempfile import NamedTemporaryFile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "scaffolds.json"
FRESH = ROOT / "experiments/FRESH-DEMAND-20261120-001A/FRESH-DEMAND-20261120-001A-E001_orders"
ORDINARY = ROOT / "experiments/ORDINARY-DYNAMICS-20261120-001A/ORDINARY-DYNAMICS-20261120-001A-E001_ordinary"
BOND = ROOT / "experiments/BOND-CLOSURE-20261120-001A/BOND-CLOSURE-20261120-001A-E001_proposals"
U, V, S, W, A, B, Z = range(7)
LAWS = ("parity", "nae")
FOCUS = (U, V)


def load(name, path):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def wired_stars(size, meetings, opens, multiplicity=2):
    rows = [[] for _ in range(size)]
    d = 0
    for a, b in meetings:
        for _ in range(multiplicity):
            rows[a].append(d)
            rows[b].append(d)
            d += 1
    for a, count in opens.items():
        rows[a].extend(range(d, d + count))
        d += count
    return tuple(map(tuple, rows))


def seven_knots(m, w, z, *, connect_to_z=False):
    pairs = [(U, S), (V, S), (W, S), (S, A), (A, B), (B, W), (A, Z)]
    if connect_to_z:
        pairs.append((B, Z))
    return wired_stars(7, pairs, {U: 2, V: 2, Z: z, W: w}, m)


def mask(names):
    return sum(1 << name for name in names)


def remainder(word, basis):
    for j in sorted(basis, reverse=True):
        if word & (1 << j):
            word ^= basis[j]
    return word


def basis_of(words):
    basis = {}
    for word in words:
        word = remainder(word, basis)
        if word:
            basis[word.bit_length() - 1] = word
    return basis


def parity_profile(stars):
    words = list(map(mask, stars))
    rank = len(basis_of(words))
    return [rank - len(basis_of(word & ~support for word in words)) for support in words]


def patterns(literal, stars, marks, law):
    if law == "nae":
        with literal.nae_solver(stars) as solver:
            return literal.sat_patterns(solver, marks)
    basis = basis_of(map(mask, stars))
    eqs = [mask(marks[i] for i, bit in enumerate(row) if bit)
           for row in product((0, 1), repeat=len(marks)) if any(row)]
    eqs = [eq for eq in eqs if not remainder(eq, basis)]
    return tuple(row for row in product((0, 1), repeat=len(marks))
                 if all((eq & mask(d for d, b in zip(marks, row, strict=True) if b)).bit_count() % 2 == 0
                        for eq in eqs))


def declared_patterns(n, law):
    return tuple(row for row in product((0, 1), repeat=n)
                 if (sum(row) % 2 == 0 if law == "parity" else 0 < sum(row) < n))


def paired_bundle_gate(literal, stars, *, exhaustive):
    # Every incomplete bundle can be made mixed. The only obstructions are fully pinned stars.
    ordinary = literal.holder_graph(stars)
    shared = bundle_sizes(literal, stars)
    assert len(literal.steps(ordinary, 0)) == len(stars)
    assert all(n >= 2 for n in shared.values())
    sets = tuple(map(set, stars))
    valid = (all(len(row) >= 3 for row in stars)
             and all(not a <= b for i, a in enumerate(sets) for j, b in enumerate(sets) if i != j))
    if exhaustive:
        with literal.nae_solver(stars) as solver:
            passed = [literal.sat_patterns(solver, row) == declared_patterns(len(row), "nae") for row in stars]
        assert all(passed) == valid
        return valid, passed
    return valid, None


def bundle_sizes(literal, stars):
    return Counter(tuple(row) for row in literal.owners(stars).values() if len(row) == 2)


def initial_by_repeated_meetings(literal, stars):
    initial = {v for pair, size in bundle_sizes(literal, stars).items() if size > 1 for v in pair}
    return tuple(stars[v] for v in sorted(initial))


def actual_birth(literal, stars, spent, count, law, *, expected_input=None):
    coholders = literal.owners(stars)
    assert all(len(coholders[d]) == 1 for d in spent)
    assert len({coholders[d][0] for d in spent}) == len(spent)
    old = patterns(literal, stars, spent, law)
    if expected_input == "implied":
        assert old == declared_patterns(len(spent), law)
    elif expected_input == "free":
        assert len(old) == 1 << len(spent)
    next_name = max(coholders) + 1
    fresh = tuple(range(next_name, next_name + count))
    row = (*spent, *fresh)
    new = (*stars, row)
    admitted = declared_patterns(len(row), law)
    assert patterns(literal, new, row, law) == admitted
    # All already permitted rows extend exactly when each observed old word has some new lift.
    assert {word[:len(spent)] for word in admitted} >= set(old)
    return new, {"spent": spent, "fresh": fresh, "allowed_inputs": old, "local_rows": len(admitted),
                 "all_earlier_rows_extend": True}


def plan(operator, stars, law):
    end = operator.from_stars(stars)
    result = operator.step(end, law)
    return {"status": result.status, "parents": result.parents,
            "fresh": result.fresh, "demand": result.demand,
            "shortages": result.shortages, "implied": result.implied}


def focused(result, parents=FOCUS):
    i = result["parents"].index(parents)
    return {"parents": parents, "fresh": result["fresh"][i], "demand": result["demand"][i]}


def materialize(operator, literal, stars, law, *, keep_only_joins=False, desired=None):
    first = plan(operator, stars, law)
    assert first["status"] == "extend"
    slots = [[] for _ in stars]
    for d, owners in sorted(literal.owners(stars).items()):
        if len(owners) == 1:
            slots[owners[0]].append(d)
    queues = [deque(row) for row in slots]
    births = []
    for group, fresh in zip(first["parents"], first["fresh"], strict=True):
        if keep_only_joins and len(group) < 2:
            continue
        slot = tuple(queues[p].popleft() for p in group)
        input_type = "implied" if first["implied"] else "free"
        stars, receipt = actual_birth(literal, stars, slot, fresh, law, expected_input=input_type)
        births.append({"parents": group, **receipt})
    if desired is not None:
        assert len(births) == desired
    return stars, births


def ordinary_view(literal, stars, roots, radius):
    """Complete rows at displayed holders, loose flags, and the names of all their coholders."""
    holders = literal.holder_graph(stars)
    shown = set().union(*(set(v for v, d in literal.steps(holders, r).items() if d <= radius) for r in roots))
    owner = literal.owners(stars)
    return [(v, tuple((d, tuple(owner[d])) for d in sorted(stars[v]))) for v in sorted(shown)]


def shared_parent_view(operator, literal, stars, roots, radius=None):
    """Witnessed sets restricted to the displayed live holders, with common names."""
    end = operator.from_stars(stars)
    neighbors = operator.neighbors(end)
    shown = set().union(*(set(v for v, d in literal.steps(neighbors, r).items()
                             if radius is None or d <= radius) for r in roots))
    ordinary = literal.holder_graph(stars)
    return {"opens": [(v, end.opens[v]) for v in sorted(shown)],
            "witnessed": [(w, tuple(sorted(row & shown))) for w, row in enumerate(ordinary) if row & shown]}


def opening_controls(operator, literal, serial):
    results = {}
    for name, w, z, bypass in (("spent", 0, 4, False), ("live", 2, 2, False),
                                ("one_three", 1, 3, False), ("four_zero", 4, 0, False),
                                ("four_zero_with_BZ", 4, 0, True)):
        primary = seven_knots(9, w, z, connect_to_z=bypass)
        if name in ("spent", "live"):
            assert primary == serial.source(9, 2, name == "live")
        low = seven_knots(2, w, z, connect_to_z=bypass)
        nae, checked = paired_bundle_gate(literal, low, exhaustive=True)
        assert paired_bundle_gate(literal, primary, exhaustive=False)[0] == nae
        ranks = parity_profile(primary)
        assert ranks == parity_profile(low)
        parity = all(rank == 1 for rank in ranks)
        assert parity == nae == (name != "four_zero")
        row = {"W_Z": (w, z), "source": primary, "local_parity_ranks": ranks,
               "literal_NAE_small_source_star_checks": checked, "lawful": parity}
        raw = {law: plan(operator, primary, law) for law in LAWS}
        if name == "one_three":
            assert all(r["status"] == "stall" and r["shortages"] == ((W, 1),) for r in raw.values())
            row["fate"] = "W owes two but holds one"
        elif name == "four_zero":
            assert set(primary[Z]) < set(primary[A])
            assert ranks[A] > 1 and not checked[A]
            assert all(r["status"] == "extend" for r in raw.values())
            row["fate"] = "funded roster on a source failing the lawfulness gate"
        else:
            width = 2 if name == "spent" else 1
            marked = min(set(primary[U]) - set(primary[S])), min(set(primary[V]) - set(primary[S]))
            row["funded_birth"] = {law: focused(raw[law]) for law in LAWS}
            row["literal_birth"] = {}
            for law in LAWS:
                assert row["funded_birth"][law]["fresh"] == width and not raw[law]["implied"]
                _, row["literal_birth"][law] = actual_birth(literal, primary, marked, width, law,
                                                             expected_input="free")
        results[name] = row
    return results


def mixed_prefixes(operator, literal, serial):
    cases = {}
    for law in LAWS:
        arms = {}
        for shifted, name in ((False, "spent"), (True, "live")):
            source = seven_knots(9, 2 if shifted else 0, 2 if shifted else 4)
            main_plan = plan(operator, source, law)
            owners = literal.owners(source)
            open_at = lambda v: tuple(d for d in source[v] if len(owners[d]) == 1)
            qu, qv = open_at(U), open_at(V)
            qw = open_at(W)
            sides = [((U, W), (qu[1], qw[0])), ((V, W), (qv[1], qw[1]))] if shifted else [
                ((U,), (qu[1],)), ((V,), (qv[1],))
            ]
            state = source
            prefix = []
            for i, (parents, inputs) in enumerate(sides):
                f = focused(main_plan, parents)["fresh"]
                assert f == (1 if shifted else 2)
                state, birth = actual_birth(literal, state, inputs, f, law, expected_input="free")
                assert parity_profile(state) == [1] * len(state)
                assert initial_by_repeated_meetings(literal, state) == source
                prefix.append({"parents": parents, **birth})
                if i == 0 and not shifted:
                    restarted = plan(operator, state, law)
                    assert focused(restarted)["fresh"] == 1 and focused(main_plan)["fresh"] == 2
                    assert FOCUS in serial.all_choices(state, joins_first=False)
                    assert all(len(p) == 2 for p in operator.proposals(operator.from_stars(state)))
                    target = (qu[0], qv[0])
                    branches = {}
                    for reading, count in (("original_map", 2), ("restart", 1)):
                        _, branches[reading] = actual_birth(literal, state, target, count, law,
                                                          expected_input="free")
                    cases.setdefault("same_literal_restart", {})[law] = {
                        "state": state, "mark": target, "prefix": birth, "two_answers": branches,
                        "repeated_meeting_reconstruction_requires_the_old_source_promise": True
                    }
            assert FOCUS in serial.all_choices(state, joins_first=False)
            reference_fresh = focused(main_plan)["fresh"]
            current_source_fresh = focused(plan(operator, state, law))["fresh"]
            assert current_source_fresh == 1
            _, current_birth = actual_birth(literal, state, (qu[0], qv[0]), reference_fresh, law,
                                             expected_input="free")
            arms[name] = {"state": state, "correct_prefix": prefix, "fixed_map_birth": current_birth,
                          "original_fresh": reference_fresh, "if_restarted_fresh": current_source_fresh,
                          "end_view": shared_parent_view(operator, literal, state, FOCUS),
                          "physical_radius_zero": ordinary_view(literal, state, FOCUS, 0),
                          "physical_radius_one": ordinary_view(literal, state, (U,), 1),
                          "recovered_original_source": initial_by_repeated_meetings(literal, state)}
        assert arms["spent"]["end_view"] == arms["live"]["end_view"]
        assert arms["spent"]["physical_radius_zero"] == arms["live"]["physical_radius_zero"]
        assert arms["spent"]["physical_radius_one"] != arms["live"]["physical_radius_one"]
        cases.setdefault("both_siblings_already_placed", {})[law] = arms

    # All starred relations of both literal restart interpretations also pass on the small analogue.
    small = seven_knots(2, 0, 4)
    d = [d for d, hs in literal.owners(small).items() if hs == [U]][-1]
    reset, _ = actual_birth(literal, small, (d,), 2, "nae", expected_input="free")
    assert parity_profile(reset) == [1] * len(reset)
    with literal.nae_solver(reset) as solver:
        assert all(literal.sat_patterns(solver, row) == declared_patterns(len(row), "nae") for row in reset)
    cases["small_restart_lawfulness_all_stars"] = len(reset)
    return cases


def radius_two(operator, literal):
    u, v, w, s, x, y, rx, tx, ry, ty, d, e, z = range(13)
    links = [(u, s), (v, s), (w, s), (v, rx), (rx, x), (x, tx), (tx, w),
             (v, ry), (ry, y), (y, ty), (ty, w), (s, d), (d, e), (e, z)]
    arms = {}
    for active in (False, True):
        source = wired_stars(13, links, {u: 2, v: 3, w: 3, z: 2 if active else 4,
                                         x: int(active), y: int(active)})
        assert parity_profile(source) == [1] * len(source)
        assert paired_bundle_gate(literal, source, exhaustive=True)[0]
        result = {law: plan(operator, source, law) for law in LAWS}
        expected = 1 if active else 2
        assert all(focused(r)["demand"] == focused(r)["fresh"] == expected for r in result.values())
        arms[str(active)] = {"source": source, "parents_and_witness": ordinary_view(literal, source, (u, v, s), 0),
                              "rooted_end_one": shared_parent_view(operator, literal, source, (u,), 1),
                              "rooted_end_two": shared_parent_view(operator, literal, source, (u,), 2),
                              "all_parent_one": shared_parent_view(operator, literal, source, (u, v), 1),
                              "holder_three": ordinary_view(literal, source, (u,), 3),
                              "holder_four": ordinary_view(literal, source, (u,), 4),
                              "first_plan_both_laws": result}
    for key in ("parents_and_witness", "rooted_end_one", "holder_three"):
        assert arms["False"][key] == arms["True"][key]
    for key in ("rooted_end_two", "all_parent_one", "holder_four"):
        assert arms["False"][key] != arms["True"][key]
    return arms


def closure(operator, literal):
    source = ((0, 1, 2),)
    result = {}
    for law in LAWS:
        stars = source
        cohorts = []
        for size in (3, 3, 1):
            stars, births = materialize(operator, literal, stars, law, desired=size)
            cohorts.append(births)
        last, = cohorts[-1]
        assert len(last["fresh"]) == int(law == "nae")
        assert len(last["allowed_inputs"]) == (4 if law == "parity" else 8)
        result[law] = {"births_by_layer": cohorts, "after_top": plan(operator, stars, law)["status"]}
    return result


def priority_ring(operator, literal):
    stars = wired_stars(8, [(i, (i + 1) % 5) for i in range(5)] + [(0, 5), (5, 6), (6, 7)],
                        {**dict.fromkeys(range(5), 2), 7: 2})
    assert parity_profile(stars) == [1] * len(stars)
    assert paired_bundle_gate(literal, stars, exhaustive=True)[0]
    result = {}
    for law in LAWS:
        state = stars
        cohorts = []
        for _ in range(4):
            state, births = materialize(operator, literal, state, law, keep_only_joins=True, desired=5)
            assert all(len(r["parents"]) == 2 and len(r["fresh"]) == 2 for r in births)
            end = operator.from_stars(state)
            assert end.opens[7] == 2 and not any(7 in group for group in operator.proposals(end))
            assert len(operator.proposals(end)) == 5
            cohorts.append(births)
        result[law] = cohorts
    return {"source": stars, "joins_only_prefix": result, "starved_unary_source": 7}


def priority_loss(literal, serial):
    source = seven_knots(9, 2, 2)
    output = {}
    for law in LAWS:
        stars = source
        sequence = []
        for event in ((U, W), (V, W), (7, 8), (U, V, 9)):
            assert event in serial.all_choices(stars, joins_first=True)
            following, graded = serial.apply_move(stars, event, law)
            independent, receipt = actual_birth(literal, stars, graded["consumed"],
                                                 graded["fresh_count"], law, expected_input="free")
            assert independent == following
            stars = following
            sequence.append({"actual_rule": graded, "projection_check": receipt})
        assert not serial.naive_live(serial.archived.S.from_junctions(stars)).keys() & {U, V}
        output[law] = sequence
    return output


def rename_check(operator, literal, example):
    stars = example["True"]["source"]
    rng = Random(20261120527)
    holders = list(range(len(stars)))
    names = list(sorted(literal.owners(stars)))
    rng.shuffle(holders)
    rng.shuffle(names)
    coded = [None] * len(stars)
    for v, row in enumerate(stars):
        coded[holders[v]] = tuple(sorted(names[d] for d in row))
    focus = tuple(sorted((holders[U], holders[V])))
    assert all(focused(plan(operator, coded, law), focus)["fresh"] == 1 for law in LAWS)
    return {"holders": holders, "distinctions": names}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    operator = load("complete_end_control", ORDINARY / "end_operator.py")
    literal = load("literal_state_control", BOND / "scaffolds.py")
    serial = load("archived_serial_control", FRESH / "serial_orders.py")
    radius = radius_two(operator, literal)
    result = {
        "opening_and_lawfulness_controls": opening_controls(operator, literal, serial),
        "mixed_prefixes": mixed_prefixes(operator, literal, serial),
        "single_root_radius": radius,
        "closing_top": closure(operator, literal),
        "joins_first_fairness_control": priority_ring(operator, literal),
        "archive_lost_birth_prefix": priority_loss(literal, serial),
        "relabel": rename_check(operator, literal, radius),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("w", dir=args.out.parent, delete=False) as out:
        temporary = Path(out.name)
        json.dump(result, out, separators=(",", ":"))
        out.write("\n")
    temporary.replace(args.out)


if __name__ == "__main__":
    main()
