"""Literal first-round replay and exact physical projections for concealed demand."""

import argparse
from collections import Counter, defaultdict
from functools import cache
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
import json
from math import prod
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PREVIOUS = ROOT / "experiments/WHOLE-STAGE-SETTINGS-20261120-001C/WHOLE-STAGE-SETTINGS-20261120-001C-E001_masking"
spec = spec_from_file_location("previous_physical", PREVIOUS / "physical.py")
previous = module_from_spec(spec)
spec.loader.exec_module(previous)

BITS = (0, 1)
TRIPLES = tuple(product(BITS, repeat=3))
LAWS = ("parity", "nae")
TERMINALS = tuple(f"terminal.{i}" for i in range(3))
H_PORTS = ("E.wh0", "E.wh1")


def endpoint(end, active, terminals, action=None):
    rows = {}
    for i in BITS:
        shared = (f"{end}.aw{i}.0", f"{end}.aw{i}.1")
        private = (f"{end}.A{i}.open",)
        if i == action:
            private += (f"{end}.edit_open",)
        rows[f"{end}.A{i}"] = (*shared, *private)
        rows[f"{end}.W{i}"] = (*shared, f"{end}.wv{i}", f"{end}.wh{i}")
    rows[f"{end}.V"] = (f"{end}.wv0", f"{end}.wv1", f"{end}.mark", f"{end}.open1", f"{end}.open2", *terminals)
    for i in BITS:
        private = (f"{end}.H{i}.open0", f"{end}.H{i}.open1") if i == active else ()
        rows[f"{end}.H{i}"] = (f"{end}.wh{i}", f"{end}.hh0", f"{end}.hh1", *private)
    return rows


def physical(u, v, mode, x=None, y=None):
    old, lanes, correspondence = previous.physical(u, v, mode)
    a = endpoint("A", u, tuple(f"terminal0.{i}" for i in range(3)), x)
    b = endpoint("B", v, tuple(f"terminal8.{i}" for i in range(3)), y)
    return a | b | {name: row for name, row in old.items() if name.startswith("column")}, lanes, correspondence


def ordinary(rows, law, recode=False, swap=False):
    written = tuple(rows)
    names = written[::-1] if recode else written
    holds = previous.index(rows)
    ids = {d: 10000 - i if recode else i for i, d in enumerate(holds)}
    state = previous.from_stars([tuple(ids[d] for d in rows[k]) for k in names])
    plan = previous.step(state, law=law)

    def decode(group):
        return tuple(sorted(names[i] for i in group))

    proposals = sorted(map(decode, previous.proposals(state)))
    demand = Counter(parent for group in proposals for parent in group)
    loose = {k: [d for d in row if len(holds[d]) == 1] for k, row in rows.items()}
    if swap:
        offer = loose["A.V"]
        offer[0], offer[1] = offer[1], offer[0]
    deficits = {names[i]: dict(available=len(loose[names[i]]), required=demand[names[i]], shortage=gap)
                for i, gap in plan.shortages}
    result = dict(status=plan.status, proposals=proposals, shortages=deficits, births=[])
    if plan.status == "stall":
        return result, rows
    assert plan.status == "extend"
    # The frozen source has no extra openings after all four pairs per side.
    ordered = sorted((decode(g), d, q) for g, d, q in zip(plan.parents, plan.demand, plan.fresh, strict=True))
    assert [group for group, _, _ in ordered] == proposals
    offered = {p: iter(ds) for p, ds in loose.items()}
    grown = dict(rows)
    for parents, d, q in ordered:
        end, label = parents[0].split(".")
        other_end, other_label = parents[1].split(".")
        assert end == other_end and q > 0
        name = f"{end}.birth.{label}-{other_label}"
        taken = tuple(next(offered[p]) for p in parents)
        fresh = tuple(f"{name}.fresh{i}" for i in range(q))
        grown[name] = taken + fresh
        result["births"].append(dict(name=name, parents=parents, p=len(parents), D=d, q=q, taken=taken, fresh=fresh))
    assert all(next(pool, None) is None for pool in offered.values())
    return result, grown


def contraction(factors, scope):
    """Return exact integer multiplicities under the given retained variables."""
    factors = list(factors)
    missing = set().union(*(set(names) for names, _ in factors)) - set(scope)
    while missing:
        def width(var):
            return len(set().union(*(set(names) for names, _ in factors if var in names))), var

        var = min(missing, key=width)
        affected = [(names, table) for names, table in factors if var in names]
        factors = [(names, table) for names, table in factors if var not in names]
        names = tuple(sorted(set().union(*(set(names) for names, _ in affected))))
        removed = names.index(var)
        reduced = Counter()
        indexed = [(tuple(names.index(key) for key in sub), table) for sub, table in affected]
        for word in product(BITS, repeat=len(names)):
            count = prod(table.get(tuple(word[i] for i in indices), 0) for indices, table in indexed)
            if count:
                reduced[word[:removed] + word[removed + 1:]] += count
        factors.append((names[:removed] + names[removed + 1:], reduced))
        missing.remove(var)
    indexed = [(tuple(scope.index(key) for key in names), table) for names, table in factors]
    result = {}
    for word in product(BITS, repeat=len(scope)):
        count = prod(table.get(tuple(word[i] for i in indices), 0) for indices, table in indexed)
        if count:
            result[word] = count
    return result


@cache
def relation(arity, law):
    return {word: 1 for word in product(BITS, repeat=arity) if previous.allowed(word, law)}


def factors(rows, law):
    return [(row, relation(len(row), law)) for row in rows]


@cache
def endpoint_factor(active, action, law, scope):
    rows = endpoint("E", active, TERMINALS, action)
    return contraction(factors(rows.values(), law), scope)


@cache
def endpoint_projections(active, action, law):
    rows = endpoint("E", active, TERMINALS, action)
    result = {k[2:]: previous.canonical_check(len(row), frozenset(endpoint_factor(active, action, law, row)))
              for k, row in rows.items()}
    assert set(endpoint_factor(active, action, law, TERMINALS)) == set(TRIPLES)
    return result


def projections(rows, lanes, u, v, x, y, law, births):
    result = {}
    for end, active, action in (("A", u, x), ("B", v, y)):
        result.update({f"{end}.{k}": check for k, check in endpoint_projections(active, action, law).items()})
    _, pad = previous.pad_factor(law)
    for left, right in lanes:
        result[left] = previous.canonical_check(3, frozenset(pad[0]))
        result[right] = previous.canonical_check(3, frozenset(pad[1]))
    for birth in births:
        names = tuple("E." + item[2:] for item in birth["taken"])
        end = birth["name"][0]
        active, action = (u, x) if end == "A" else (v, y)
        possible = endpoint_factor(active, action, law, names)
        # Each satisfying choice on this birth coexists with the remaining
        # births, whose private fresh distinctions complete any old input.
        words = {old + fresh for old in possible for fresh in product(BITS, repeat=birth["q"])
                 if previous.allowed(old + fresh, law)}
        result[birth["name"]] = previous.canonical_check(len(rows[birth["name"]]), frozenset(words))
    assert set(result) == set(rows)
    return result


def visible(rows, end, enlarged=False):
    left = end == "A"
    guard = 0 if left else 7
    local = {k: row for k, row in rows.items() if k.startswith(f"column{guard}.") or
             k.startswith(f"{end}.") and (enlarged or not k.startswith(f"{end}.H"))}
    holds = previous.index(rows)
    return dict(supports=local, holders={d: holds[d] for row in local.values() for d in row},
                outer_guard=tuple(f"terminal{1 if left else 7}.{i}" for i in range(3)))


def separations(rows):
    # The predecessor's separation reader uses these names to locate the same
    # two edit holders and detector on each side.
    names = {f"{end}.{source}": f"{end}.{target}" for end in "AB"
             for source, target in (("A0", "address0"), ("A1", "address1"), ("V", "detector"))}
    return previous.separations({names.get(k, k): row for k, row in rows.items()})


def parity_count(rows):
    positions = {d: i for i, d in enumerate(previous.index(rows))}
    basis = {}
    for row in rows.values():
        word = sum(1 << positions[d] for d in row)
        while word:
            pivot = word.bit_length()
            if pivot not in basis:
                basis[pivot] = word
                break
            word ^= basis[pivot]
    return dict(rank=len(basis), distinctions=len(positions), assignments=2**(len(positions) - len(basis)))


def certified_counts(base, lanes, type_word, correspondence, law):
    u, v = type_word
    left = endpoint_factor(u, None, law, TERMINALS)
    right = endpoint_factor(v, None, law, TERMINALS)
    link = {base[a][0]: base[b][0] for a, b in lanes}
    for i, j in enumerate(correspondence):
        d = f"terminal0.{i}"
        for _ in range(8):
            d = link[d]
        assert d == f"terminal8.{j}"
    piece, _ = previous.pad_factor(law)
    matrix = previous.path_factor(piece, 8)
    joint = [[left[a] * right[b] * prod(matrix[a[i]][b[j]] for i, j in enumerate(correspondence)) for b in TRIPLES]
             for a in TRIPLES]

    hidden = []
    for r in BITS:
        endpoint_rows = endpoint("E", r, TERMINALS)
        hidden_rows = [row for k, row in endpoint_rows.items() if k.startswith("E.H")]
        hidden.append(contraction(factors(hidden_rows, law), H_PORTS))
    assert hidden[0] == hidden[1]
    hidden_counts = [[hidden[0][a, b] for b in BITS] for a in BITS]
    assert hidden_counts == ([[4, 4], [4, 4]] if law == "parity" else [[12, 11], [11, 12]])

    # One observed guard is part of the fixed local record. The unobserved
    # seven pads per path and the opposite endpoint contribute this factor.
    exterior = previous.path_factor(piece, 7)
    outside_a = [sum(right[b] * prod(exterior[a[i]][b[j]] for i, j in enumerate(correspondence)) for b in TRIPLES)
                 for a in TRIPLES]
    outside_b = [sum(left[a] * prod(exterior[a[i]][b[j]] for i, j in enumerate(correspondence)) for a in TRIPLES)
                 for b in TRIPLES]
    return dict(terminal_order=["".join(map(str, word)) for word in TRIPLES], terminal_counts=joint,
                old_assignments=sum(map(sum, joint)), hidden_near_counts=hidden_counts,
                exterior_by_outer_guard=dict(A=outside_a, B=outside_b),
                terminal_local_completions=dict(A=[left[w] for w in TRIPLES], B=[right[w] for w in TRIPLES]),
                visible_record_integer_weight="For a locally lawful visible word multiply its hidden-near entry "
                                              "by its exterior entry; other words have weight zero.")


def run():
    by_mode = {}
    for mode in ("primary", "commuting"):
        cases = {}
        by_mode[mode] = cases
        for u, v in product(BITS, repeat=2):
            base, lanes, correspondence = physical(u, v, mode)
            own = {e: visible(base, e) for e in "AB"}
            enlarged = {e: visible(base, e, enlarged=True) for e in "AB"}
            data = dict(old_supports=base, pre_accessible=own, pre_accessible_enlarged=enlarged,
                        correspondence=correspondence, separations=separations(base), laws={})
            cases[f"{u}{v}"] = data
            for law in LAWS:
                cases_for_law = dict(old_projection_checks=projections(base, lanes, u, v, None, None, law, ()),
                                     old_counts=certified_counts(base, lanes, (u, v), correspondence, law), trials={})
                data["laws"][law] = cases_for_law
                if law == "parity":
                    cases_for_law["old_parity_rank"] = parity_count(base)
                    assert cases_for_law["old_parity_rank"]["assignments"] == cases_for_law["old_counts"]["old_assignments"]
                actions = (None, *BITS) if mode == "primary" else BITS
                for x, y in product(actions, repeat=2):
                    edited, _, _ = physical(u, v, mode, x, y)
                    turn, grown = ordinary(edited, law)
                    funded = int((x, y) == (u, v))
                    assert turn["status"] == ("extend" if funded else "stall")
                    expected = {f"{e}.A{r}" for e, r, action in (("A", u, x), ("B", v, y)) if action != r}
                    assert turn["shortages"].keys() == expected and all(s["shortage"] == 1 for s in turn["shortages"].values())
                    assert len(turn["births"]) == 8 * funded
                    mark_holders = {e: previous.index(grown)[f"{e}.mark"] for e in "AB"}
                    assert all(len(holders) == 1 + funded for holders in mark_holders.values())
                    assert ordinary(edited, law, recode=True) == (turn, grown)
                    swapped, alternate = ordinary(edited, law, swap=True)
                    assert all(len(previous.index(alternate)[f"{e}.mark"]) == 1 + funded for e in "AB")
                    swap_changed = [b["name"] for a, b in zip(turn["births"], swapped["births"], strict=True)
                                    if a["taken"] != b["taken"]]
                    assert len(swap_changed) == 2 * funded
                    after = projections(grown, lanes, u, v, x, y, law, turn["births"])
                    assert after == projections(alternate, lanes, u, v, x, y, law, swapped["births"])
                    key = "".join("-" if a is None else str(a) for a in (x, y))
                    trial = dict(status=turn["status"], round=turn, offer_swap_changed=swap_changed,
                                 mark_holders=mark_holders, projections=after,
                                 edited_supports={k: edited[k] for k in edited if edited[k] != base[k]},
                                 post_accessible={e: visible(grown, e) for e in "AB"})
                    cases_for_law["trials"][key] = trial
                    if law == "parity":
                        trial["edited_parity_rank"] = parity_count(edited)
                        trial["grown_parity_rank"] = parity_count(grown)
                        lifts = 2**sum(b["q"] - 1 for b in turn["births"])
                        assert trial["grown_parity_rank"]["assignments"] == trial["edited_parity_rank"]["assignments"] * lifts
        check_visible_equivalence(cases)
    return dict(freeze="2180807278", observer="Both A/W holders, V, the first full guard, all co-holder names, and "
                "after the step all incident births and their distinctions.",
                local_value_lifts={"parity": "Set the new edit distinction to zero. At each local birth divide "
                                   "by 2^(q-1) among parity completions for its actual inputs.",
                                   "nae": "Assign the new edit distinction a fair independent bit. At each local "
                                   "birth divide by 2^q-1 if inputs agree or 2^q otherwise among legal completions."},
                modes=by_mode)


def check_visible_equivalence(cases):
    for end in "AB":
        reference = cases["00"]["pre_accessible"][end]
        assert all(case["pre_accessible"][end] == reference for case in cases.values())
        r_type = "10" if end == "A" else "01"
        assert cases["00"]["pre_accessible_enlarged"][end] != cases[r_type]["pre_accessible_enlarged"][end]
        for law in LAWS:
            weights = [case["laws"][law]["old_counts"] for case in cases.values()]
            assert all((w["old_assignments"], w["hidden_near_counts"], w["exterior_by_outer_guard"][end]) ==
                       (weights[0]["old_assignments"], weights[0]["hidden_near_counts"], weights[0]["exterior_by_outer_guard"][end])
                       for w in weights)
            records = {}
            for case in cases.values():
                for actions, trial in case["laws"][law]["trials"].items():
                    key = actions[0 if end == "A" else 1], trial["status"]
                    observed = trial["post_accessible"][end]
                    assert records.setdefault(key, observed) == observed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    text = json.dumps(run(), sort_keys=True, separators=(",", ":")) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
