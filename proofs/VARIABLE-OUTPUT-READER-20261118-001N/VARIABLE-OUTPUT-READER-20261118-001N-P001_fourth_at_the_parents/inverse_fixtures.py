"""Read the 31-distinction table with a directly involved hidden junction, and the planted 27 control."""
from collections import Counter, deque
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
from pathlib import Path
import json
import sys

PROOFS = Path(__file__).resolve().parents[2]
SERIES = "VARIABLE-OUTPUT-READER-20261118-001"


def predecessor(letter, slug, filename):
    ticket = SERIES + letter
    path = PROOFS / ticket / (ticket + "-P001_" + slug) / filename
    spec = spec_from_file_location("fourth_inverse_" + letter, path)
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


algebra = predecessor("I", "cycle_obstruction", "fixtures.py")
wired = predecessor("K", "third_three_fresh", "high_check.py")
literal = wired.literal
CORE = ((0,1,2), (0,3,4,5), (3,6,7,8), (1,6,9,10,11), (4,9,12,13),
        (7,12,14,15), (14,10,16,17), (2,16,18,19), (5,18,20,21), (8,20,22,23),
        (19,11,22,24,25), (13,21,24,26,27))
LIVE = CORE + ((15,23,26,28,29,30),)
OTHER = CORE + ((15,23,27,28,29,30),)
PLANTED = ((0,1,2), (0,3,4,5), (1,6,7,8), (2,9,10,11), (3,6,12,13), (4,9,14,15),
           (7,10,16,17), (12,14,16,18,19,20), (5,18,21,22), (8,19,23,24), (11,20,25,26))
WITHOUT = PLANTED[:7] + PLANTED[8:]


def menus(rows):
    holders, adjacent = literal.incidence(rows)
    loose = sorted(bit for bit, ends in holders.items() if len(ends) == 1)
    return tuple(mark for mark in combinations(loose, 3)
                 if literal.legal_parents(tuple(holders[bit][0] for bit in mark), adjacent))


def clipped(table, order):
    return {pair: min(value, order + 1) for pair, value in table.items()}


def presentations(pool, width, limit):
    """All reachable named arrangements using pool, insensitive to topological order."""
    seed, = (word for word in pool if word.bit_count() == 3)
    words = {word: algebra.bits(word) for word in pool
             if word != seed and (word & seed).bit_count() <= 1}
    start = frozenset((seed,))
    queue = deque((start,))
    seen = {start}
    counts = Counter()
    completed = []
    while queue:
        state = queue.popleft()
        counts[len(state)] += 1
        rows = [algebra.bits(word) for word in sorted(state)]
        holders, adjacent = literal.incidence(rows)
        if len(holders) == width:
            completed.append(state)
            continue
        if len(state) >= limit or len(holders) + 3 * (limit - len(state)) < width:
            continue
        for word, support in words.items():
            if word in state:
                continue
            used = [bit for bit in support if bit in holders]
            if len(support) - len(used) not in (2, 3) or any(len(holders[b]) == 2 for b in used):
                continue
            if not literal.legal_parents([holders[bit][0] for bit in used], adjacent):
                continue
            new = state | {word}
            if new not in seen:
                seen.add(new)
                queue.append(new)
    return completed, dict(sorted(counts.items()))


def read(table, width, rank_ceiling):
    # Six is a bond cardinality, corresponding to a bond distance of five.
    known, unresolved, _, _ = algebra.force_from_table(table, width, 6)
    known_bonds = {w for w in known if 3 <= w.bit_count() <= 6
                   and not any(v & w == v for v in known if 0 < v.bit_count() < w.bit_count())}
    pool = known_bonds | unresolved
    complete, layers = presentations(pool, width, rank_ceiling)
    through_five = []
    all_distances = []
    for state in complete:
        rows = [algebra.bits(word) for word in sorted(state)]
        current, _ = wired.wired_table(rows)
        if clipped(current, 6) == clipped(table, 6):
            through_five.append(state)
        if current == table:
            all_distances.append(state)

    def cases(states):
        return [{"supports": sorted(algebra.bits(w) for w in state), "menu": menus([algebra.bits(w) for w in state])}
                for state in sorted(states, key=lambda x: sorted(x))]

    return {"rank_ceiling": rank_ceiling, "forced_rank_through_D5": algebra.rank(known), "possible_star_count": len(pool),
            "unforced_star_candidates": len(unresolved), "prefix_counts_by_size": layers,
            "full_width_before_comparing_tables": len(complete), "through_D5": cases(through_five),
            "exact": cases(all_distances)}


def read_live_through_four(table):
    # Read only entries D<=4. The three absent columns and the rank force a terminal site.
    low = {pair: val if val <= 5 else None for pair, val in table.items()}
    forced, _, _, _ = algebra.force_from_table(low, 31, 5)
    visible = set(bit for word in forced for bit in algebra.bits(word))
    fresh = sorted(set(range(31)) - visible)
    assert len(fresh) == 3 and all(val is None for pair, val in low.items() if set(fresh) & set(pair))
    old_rank = algebra.rank(forced)
    assert old_rank == 12
    short = sorted((w for w in forced if 3 <= w.bit_count() <= 6), key=int.bit_count)
    ordinary_candidates = {w for w in short if not any(v != w and v & w == v for v in short)}
    prefixes, _ = presentations(ordinary_candidates, len(visible), old_rank)
    full_prefixes = [prefix for prefix in prefixes if len(prefix) == old_rank]
    assert len(full_prefixes) == 1
    prefix, = full_prefixes
    assert algebra.span(prefix) == forced
    old_rows = tuple(algebra.bits(w) for w in sorted(prefix))
    possible = menus(old_rows)
    results = []
    for inputs in possible:
        rows = old_rows + (inputs + tuple(fresh),)
        distances, _ = wired.wired_table(rows)
        agree = all((value if value <= 5 else None) == low[pair] for pair, value in distances.items())
        results.append({"inputs": inputs, "clipped_agreement": agree,
                        "next_triples": menus(rows)})
    assert len(results) == 2 and all(result["clipped_agreement"] for result in results)
    return {"rank_of_forced_old_equations": old_rank, "absent_names": fresh,
            "full_rank_reachable_prefixes": len(full_prefixes), "old_legal_triples_and_successors": results}


def sharp_four_control(table):
    results = read_live_through_four(table)["old_legal_triples_and_successors"]
    assert all(result["next_triples"] == ((17,25,28), (17,25,29), (17,25,30)) for result in results)
    perm = list(range(31))
    perm[24], perm[25] = perm[25], perm[24]
    mark = (17,25,28)
    image = tuple(sorted(perm[b] for b in mark))
    diffs = {cutoff: sum(min(v,cutoff+2) != min(table[tuple(sorted(perm[b] for b in p))],cutoff+2)
                         for p,v in table.items()) for cutoff in (3,4,5)}
    assert mark in menus(LIVE) and image not in menus(LIVE) and diffs == {3:0, 4:8, 5:20}
    return {"swap": [24,25], "legal": mark, "forbidden": image, "changed_entries_through_distance": diffs}


def run():
    def key(rows):
        return tuple(sorted(tuple(sorted(s)) for s in rows))

    output = {}
    for title, rows in (("live", LIVE), ("planted", PLANTED)):
        events = literal.replay(rows)
        assert sum(len(r["fresh"]) == 3 for r in events[1:]) == 4
        table, _ = wired.wired_table(rows)
        width = max(max(pair) for pair in table) + 1
        result = read(table, width, (width - 5) // 2)
        assert key(rows) in [key(r["supports"]) for r in result["exact"]]
        # Scramble the order of all rows and columns, including the three fresh bits.
        rename = [(3*i + 7) % width for i in range(width)] if width == 31 else [(5*i + 7) % width for i in range(width)]
        remap = lambda group: tuple(sorted(rename[i] for i in group))
        renamed_table = {remap(pair): val for pair, val in table.items()}
        renamed = read(renamed_table, width, (width - 5) // 2)
        for mode in ("through_D5", "exact"):
            expected = {(key([remap(s) for s in r["supports"]]), tuple(sorted(remap(t) for t in r["menu"])))
                        for r in result[mode]}
            observed = {(key(r["supports"]), tuple(r["menu"])) for r in renamed[mode]}
            assert observed == expected
        if title == "live":
            result["D4_certificate"] = read_live_through_four(table)
            renamed_four = read_live_through_four(renamed_table)
            expected_four = {(remap(r["inputs"]), tuple(sorted(remap(t) for t in r["next_triples"])))
                             for r in result["D4_certificate"]["old_legal_triples_and_successors"]}
            assert expected_four == {(r["inputs"], r["next_triples"])
                                     for r in renamed_four["old_legal_triples_and_successors"]}
            result["D3_lower_control"] = sharp_four_control(table)
        result["renaming_checked"] = rename
        output[title] = result
    tleft, left = wired.wired_table(LIVE)
    tright, right = wired.wired_table(OTHER)
    assert tleft == tright and left != right
    literal.replay(WITHOUT)
    t27, _ = wired.wired_table(PLANTED)
    tb, _ = wired.wired_table(WITHOUT)
    mark = (13, 15, 17)
    assert mark in menus(WITHOUT) and mark not in menus(PLANTED)
    assert all(len(literal.incidence(rows)[0][b]) == 1 for rows in (PLANTED, WITHOUT) for b in mark)
    hist = lambda t: dict(sorted(Counter(v - 1 for v in t.values()).items()))
    output["planted_comparison"] = {"loose_mark": mark, "with_junction_distances": hist(t27),
                                    "without_junction_distances": hist(tb),
                                    "changed_exact_entries": sum(t27[p] != tb[p] for p in t27),
                                    "probe_18_19": [t27[18,19] - 1, tb[18,19] - 1]}
    assert hist(t27) != hist(tb)
    return output


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
