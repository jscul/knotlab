"""Independent growth and exact physical rulers for the registered closing comparison."""

from argparse import ArgumentParser
from collections import Counter, defaultdict, deque
from functools import cache
from itertools import combinations
import json
from pathlib import Path
from random import Random
import sys
from tempfile import NamedTemporaryFile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "rulers.json"
LENGTHS = (4, 5, 8, 16)
sys.path.insert(0, str(ROOT / "tools"))
from knotlab import Relation, check_knot


def source(length, extra, doubled=False):
    hub, far = (0, 0) if length is None else (0, 1)
    first = []
    tails = []
    links = []
    n = 1 if length is None else 2
    for _ in range(3):
        tail = list(range(n, n + (1 if length is None else length - 1)))
        n += len(tail)
        first.append(tail[0])
        if length is None:
            links.append((hub, tail[0]))
        else:
            rail = [hub, *tail, far]
            for i, (u, v) in enumerate(zip(rail, rail[1:])):
                links.extend([(u, v)] * (2 if doubled or 0 < i < length - 1 else 1))
            tails.append(tail)
    loose = {v: 2 for v in first}
    if extra:
        loose[far] = 1
    rows = [[] for _ in range(n)]
    for d, (a, b) in enumerate(links):
        rows[a].append(d)
        rows[b].append(d)
    bit = len(links)
    for v, count in loose.items():
        rows[v].extend(range(bit, bit + count))
        bit += count
    return tuple(map(tuple, rows)), {"near_hub": hub, "far_holder": far, "leaves": first, "tails": tails}


def owners(stars):
    result = defaultdict(list)
    for v, row in enumerate(stars):
        for d in row:
            result[d].append(v)
    assert all(1 <= len(row) <= 2 for row in result.values())
    return {d: tuple(row) for d, row in result.items()}


def observed(stars):
    roster = owners(stars)
    loose = defaultdict(list)
    ord_adj = [set() for _ in stars]
    for d, row in roster.items():
        if len(row) == 2:
            v, w = row
            ord_adj[v].add(w)
            ord_adj[w].add(v)
        else:
            loose[row[0]].append(d)
    return {v: sorted(ds) for v, ds in sorted(loose.items())}, ord_adj


def groups(live, adj):
    candidate = {frozenset(pair) for pair in combinations(live, 2) if adj[pair[0]] & adj[pair[1]]}
    valid = []
    for n in range(len(live), 2, -1):
        for row in combinations(live, n):
            group = frozenset(row)
            if (all(frozenset(pair) in candidate for pair in combinations(row, 2))
                    and not set.intersection(*(adj[v] for v in row))
                    and not any(group < top for top in valid)):
                valid.append(group)
    return [tuple(sorted(row)) for row in valid + sorted(
        (q for q in candidate if not any(q < top for top in valid)), key=sorted)]


def reduce_rows(rows):
    pivots = {}
    for mask in rows:
        while mask:
            i = mask.bit_length() - 1
            if i not in pivots:
                pivots[i] = mask
                break
            mask ^= pivots[i]
    return pivots


def mask(row):
    return sum(1 << d for d in row)


def implied(equations, row):
    residual = mask(row)
    while residual:
        high = residual.bit_length() - 1
        if high not in equations:
            return False
        residual ^= equations[high]
    return True


@cache
def canonical_local_relation(arity, even):
    names = tuple(str(i) for i in range(arity))
    relation = Relation.from_predicate(
        names, lambda values: sum(values.values()) % 2 == 0 if even else 0 < sum(values.values()) < arity)
    assert check_knot(relation, names[:-1], names[-1]).is_knot


def legal_stars(stars):
    words = list(map(mask, stars))
    r = len(reduce_rows(words))
    assert all(len(row) >= 3 for row in stars)
    for row, k in zip(stars, words, strict=True):
        # The supported equations have rank one, so the actual projected relation is even parity.
        assert r - len(reduce_rows(w & ~k for w in words)) == 1
        canonical_local_relation(len(row), even=True)
    return r


def check_nae_projections(stars, states):
    for row in stars:
        w = mask(row)
        projected = {x & w for x in states}
        assert 0 not in projected and w not in projected and len(projected) == (1 << len(row)) - 2
        canonical_local_relation(len(row), even=False)


@cache
def literal_nae(stars):
    assert max(owners(stars)) < 16, "the real allowed-state control is for the small star"
    words = list(map(mask, stars))
    states = tuple(x for x in range(1 << (max(owners(stars)) + 1)) if all(0 < (x & w) < w for w in words))
    assert states
    check_nae_projections(stars, states)
    return states


def lift_nae(old, grown):
    old_width = max(owners(old)) + 1
    fresh_width = max(owners(grown)) + 1 - old_width
    added_words = list(map(mask, grown[len(old):]))
    states = []
    for row in literal_nae(old):
        before = len(states)
        for fresh in range(1 << fresh_width):
            assignment = row | (fresh << old_width)
            if all(0 < (assignment & w) < w for w in added_words):
                states.append(assignment)
        assert len(states) > before
    check_nae_projections(grown, states)
    return len(states)


def step(stars, nae=False):
    """Literal exhaustive group selection; small fronts make enumeration cheap."""
    loose, adj = observed(stars)
    if not loose:
        return stars, [], {"status": "closed"}
    multi = groups(tuple(loose), adj)
    used = Counter(v for group in multi for v in group)
    assert all(len(ports) >= used[v] for v, ports in loose.items())
    roster = multi + [(v,) for v, ports in loose.items() for _ in range(len(ports) - used[v])]
    n = len(stars)
    new = tuple(range(n, n + len(roster)))
    next_adj = [set() for _ in range(n + len(roster))]
    for v, ps in zip(new, roster, strict=True):
        for p in ps:
            next_adj[v].add(p)
            next_adj[p].add(v)
    demands = Counter(v for row in groups(new, next_adj) for v in row)
    old_basis = reduce_rows(map(mask, stars))
    old_values = literal_nae(stars) if nae else None
    allocations = {v: iter(ds) for v, ds in loose.items()}
    next_bit = max(owners(stars)) + 1
    births = []
    for j, ps in zip(new, roster, strict=True):
        spent = tuple(next(allocations[v]) for v in ps)
        if nae:
            boundary = mask(spent)
            witness = next((a for a in old_values if (a & boundary) in (0, boundary)), None)
            already = witness is None
        else:
            already = implied(old_basis, spent)
            assert already == (len(spent) == sum(map(len, loose.values())))
            witness = None
        h = 0 if already else max(demands[j], 3 - len(ps), 1)
        fresh = tuple(range(next_bit, next_bit + h))
        next_bit += h
        births.append({"knot": j, "parents": ps, "spent": spent, "fresh": fresh, "arity": len(ps) + h,
                       "raw_demand": demands[j], "implied": already, "nae_counterstate": witness})
    grown = stars + tuple((*r["spent"], *r["fresh"]) for r in births)
    return grown, births, {"status": "open" if any(r["fresh"] for r in births) else "closed", "no_underfunding": True}


def bfs(adj, root):
    distance = {root: 0}
    queue = deque([root])
    while queue:
        v = queue.popleft()
        for u in adj[v]:
            if u not in distance:
                distance[u] = distance[v] + 1
                queue.append(u)
    return distance


def ordinary_rows(stars):
    loose, adj = observed(stars)
    live_adj = {v: {w for w in loose if w != v and adj[v] & adj[w]} for v in loose}
    marks = {d: v for v, ds in loose.items() for d in ds}
    whole, end = {v: bfs(adj, v) for v in loose}, {v: bfs(live_adj, v) for v in loose}
    return [{"marks": (a, b), "growing_end_steps": end[v].get(w), "whole_ordinary_holder_steps": whole[v][w],
             "whole_co_knotted_distinction_steps": whole[v][w] + 1}
            for (a, v), (b, w) in combinations(sorted(marks.items()), 2)]


def connected(adj, side):
    pending = side & -side
    unseen = side ^ pending
    while pending:
        lo = pending & -pending
        pending ^= lo
        v = lo.bit_length() - 1
        onward = adj[v] & unseen
        unseen ^= onward
        pending |= onward
    return not unseen


def bits(values):
    return sum(1 << v for v in set(values))


def encode_links(stars):
    exterior = len(stars)
    return {d: (row if len(row) == 2 else (*row, exterior)) for d, row in owners(stars).items()}


def all_small_bonds(kept, links, origins, exterior):
    """Enumerate both-shore connected cuts, keeping each physical distinction separate."""
    ordered = sorted(kept - {exterior}) + [exterior]
    ids = {v: i for i, v in enumerate(ordered)}
    adj = [0] * len(ordered)
    for u, v in links.values():
        adj[ids[u]] |= 1 << ids[v]
        adj[ids[v]] |= 1 << ids[u]
    all_vertices = (1 << len(ordered)) - 1
    full = 1 << (len(ordered) - 1)
    best = {}
    origins = sorted(origins)
    score = {d: 1 << ids[links[d][0]] for d in origins}
    assert all(links[d][1] == exterior for d in origins)
    for side in range(1, full):
        selected = [d for d, hit in score.items() if hit & side]
        if len(selected) < 2:
            continue
        if not connected(adj, side) or not connected(adj, all_vertices ^ side):
            continue
        cut = [d for d, (u, v) in links.items() if ((side >> ids[u]) ^ (side >> ids[v])) & 1]
        for pair in combinations(selected, 2):
            if pair not in best or len(cut) < best[pair][0]:
                best[pair] = (len(cut), {v for v, i in ids.items() if (side >> i) & 1})
    assert len(best) == len(origins) * (len(origins) - 1) // 2
    return best


def contraction(stars, roles):
    """Quotient only for cuts: along each tail pay at its last meeting."""
    links = encode_links(stars)
    erased = set(v for row in roles["tails"] for v in row[1:])
    keep = set(range(len(stars) + 1)) - erased
    reduced = {d: row for d, row in links.items() if keep.issuperset(row)}
    for rail in roles["tails"]:
        for d, row in links.items():
            if set(row) == {rail[-1], roles["far_holder"]}:
                reduced[d] = (rail[0], roles["far_holder"])
    return keep, reduced


def cut_rulers(stars, roles, direct):
    loose, adj = observed(stars)
    marks = {d for ds in loose.values() for d in ds}
    outside = len(stars)
    links = encode_links(stars)
    kept, reduced = contraction(stars, roles)
    results = all_small_bonds(kept, reduced, marks, outside)
    if direct:
        literal = all_small_bonds(set(range(outside + 1)), links, marks, outside)
        assert {p: r[0] for p, r in results.items()} == {p: r[0] for p, r in literal.items()}
    full_adj = [bits(row) for row in adj] + [bits(loose)]
    for v in loose:
        full_adj[v] |= 1 << outside
    out = []
    for row in ordinary_rows(stars):
        pair = row["marks"]
        cost, core = results[pair]
        shore = set(core)
        for rail in roles["tails"]:
            if rail[0] in shore:
                shore.update(rail[1:])
        side = bits(shore)
        assert connected(full_adj, side) and connected(full_adj, ((1 << (outside + 1)) - 1) ^ side)
        cut = sorted(d for d, (u, v) in links.items() if (u in shore) != (v in shore))
        assert len(cut) == cost and set(pair) <= set(cut)
        canonical_local_relation(cost, even=True)
        out.append({**row, "bond_distance": cost - 1, "whole_literal_bond": cut, "shore_away_from_exterior": sorted(shore)})
    return out


def renaming_control(stars, next_stars, common_births):
    n = len(next_stars)
    r = Random(183)
    order = list(range(n))
    r.shuffle(order)
    names = list(6 * i + 31 for i in range(len(owners(next_stars))))
    r.shuffle(names)
    bits_map = dict(zip(sorted(owners(next_stars)), names, strict=True))
    moved = tuple(tuple(bits_map[d] for d in next_stars[v]) for v in order)
    loose, adj = observed(moved)
    peeled = {frozenset(row) for v, row in enumerate(moved) if v not in loose}
    assert peeled == {frozenset(bits_map[d] for d in row) for row in stars}
    common = {order.index(row["knot"]) for row in common_births}
    assert len(common) == 3
    witnesses = [frozenset(adj[v] & adj[w]) for v, w in combinations(sorted(common), 2)]
    assert all(len(row) == 1 for row in witnesses) and len(set(witnesses)) == 3
    assert len(set.union(*(adj[v] for v in common))) == 3
    for root in common:
        reachable = bfs({v: {w for w in loose if w != v and adj[v] & adj[w]} for v in loose}, root)
        assert reachable == ({root: 0} | {v: 1 for v in common if v != root})
        assert all(len(loose[v]) == 1 for v in reachable)
    return {"root_choices_in_identical_component": 3, "distinct_single_pair_witnesses": 3, "shuffled_literal_peel_exact": True}


def check_reached_rulers(record, length, extra):
    common = {r["fresh"][0] for r in record["first_births"] if len(r["parents"]) == 2}
    ordinary = 3 if length is None else length + 1
    expected = {2: (1, 2, 3, 2 + extra), 1: (None, ordinary, ordinary + 1, 4), 0: (0, 0, 1, 2)}
    counts = Counter()
    for row in record["reached_rulers"]:
        p = len(common.intersection(row["marks"]))
        assert tuple(row[k] for k in ("growing_end_steps", "whole_ordinary_holder_steps",
                                     "whole_co_knotted_distinction_steps", "bond_distance")) == expected[p]
        counts[p] += 1
    assert counts == ({2: 3, 1: 6, 0: 1} if extra else {2: 3})


def case(length, doubled=False):
    arms = {}
    for extra in (False, True):
        orig, roles = source(length, extra, doubled)
        smallest = length is None or length == 4
        reached, births, first = step(orig)
        later, births2, second = step(reached)
        parents = [r for r in births if len(r["parents"]) == 2]
        target, = (r for r in births2 if len(r["parents"]) == 3)
        assert first["status"] == "open" and len(parents) == 3 and all(len(b["fresh"]) == 1 for b in parents)
        assert target["parents"] == tuple(r["knot"] for r in parents) and len(target["fresh"]) == int(extra)
        loose, adj = observed(orig)
        assert len(loose) == 3 + extra
        s3 = all(len(q) == 2 for q in groups(tuple(loose), adj))
        s4 = all(len(adj[u] & adj[v]) <= 1 for u, v in combinations(loose, 2))
        assert s3 and s4 and sum(map(len, loose.values())) >= 2
        ranks = [legal_stars(stars) for stars in (orig, reached, later)]
        record = {"roles": roles, "source": orig, "reached": reached, "next": later, "first_births": births, "next_births": births2,
                  "first_status": first, "next_status": second, "direct_exhaustive_cuts": smallest,
                  "equation_ranks_by_age": ranks, "proved_class": {"S3": s3, "S4": s4, "S0": True, "S6_prime": True},
                  "renaming": renaming_control(orig, reached, parents), "source_rulers": cut_rulers(orig, roles, smallest),
                  "reached_rulers": cut_rulers(reached, roles, smallest)}
        check_reached_rulers(record, length, extra)
        if length is None:
            nae1, n1, _ = step(orig, nae=True)
            assert nae1 == reached
            nae2, n2, nae_status = step(nae1, nae=True)
            assert len(next(row for row in n2 if len(row["parents"]) == 3)["fresh"]) == 1
            naive_counts = [len(literal_nae(orig)), len(literal_nae(nae1)), lift_nae(nae1, nae2)]
            assert lift_nae(orig, nae1) == naive_counts[1]
            record["nae_small_exact_allowed_rows"] = {"state_counts_by_age": naive_counts,
                                                      "first_births": n1, "next_births": n2, "status": nae_status,
                                                      "all_earlier_rows_extend": True}
        arms["extra" if extra else "base"] = record
    b, a = arms["base"], arms["extra"]
    assert b["next_status"]["status"] == "closed" and a["next_status"]["status"] == "open"
    n = len(b["source"])
    return {"length_in_ordinary_source_steps": length, "all_links_doubled": doubled, "arms": arms,
            "matched_age_zero_support_changes": [1, n], "matched_age_one_birth_changes": [0, 3],
            "extra_age_one_births_fraction_of_augmented_births": [1, 4], "matched_age_two_births_with_changed_parents": [0, 1],
            "matched_age_two_births_with_changed_fresh": [1, 1], "extra_age_two_births_fraction_of_augmented_births": [2, 3],
            "matched_live_fraction_after_base_closes": None}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    result = {"four_knot_star": case(None),
              "theta_cases": [case(length) for length in LENGTHS] + [case(4, doubled=True)],
              "projection_test": "K1–K3 on actual local relations; exact parity projection ranks and literal not-all-equal states",
              "null_means": "no route on the growing end, or no common live denominator after closing"}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("w", dir=args.out.parent, delete=False) as out:
        temporary = Path(out.name)
        json.dump(result, out, separators=(",", ":"))
        out.write("\n")
    temporary.replace(args.out)


if __name__ == "__main__":
    main()
