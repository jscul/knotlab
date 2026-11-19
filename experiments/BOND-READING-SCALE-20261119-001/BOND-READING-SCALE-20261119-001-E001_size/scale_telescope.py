"""Check individual repricings of two fixed weighted cores, including all moved queries."""

import argparse
import functools
import importlib.util
import itertools
import json
from pathlib import Path

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "scale_telescope.json"


def one_price(arity, anchors, shields, spoke, arm, hub_cost, price, red_changes, tracked=None):
    outer_count = anchors + 3
    outside = 2
    all_outer = (1 << outer_count) - 1
    weights = []
    names = []
    types = []
    unnamed = []
    special_middle = ["a", "b", "c", "d"]

    def middle(name, kind, weights_here):
        start = len(names)
        hub = kind % 2
        ends = [(hub, "hub"), *[(3 + i, f"anchor{i}") for i in range(anchors)]]
        if kind >= 2:
            ends.append((outside, "outside"))
        types.append(kind)
        row = []
        for (end, role), cost in zip(ends, weights_here, strict=True):
            names.append((name, role))
            row.append((end, cost, 1 << (start + len(row))))
        weights.append(row)

    for i, mid in enumerate(special_middle):
        middle(mid, i // 2, [spoke, arm, *([1] * (anchors - 1))])
    for color, count in enumerate(shields):
        prices = [1 if color == 0 and i < red_changes else price for i in range(count)]
        for value in sorted(set(prices)):
            members = [i for i, cost in enumerate(prices) if cost == value]
            visible = members[:arity - 1]
            for i in visible:
                middle(f"{'R' if color == 0 else 'B'}{i}", color + 2,
                       [hub_cost, *([1] * anchors), value])
            if len(members) > len(visible):
                unnamed.append((color, len(members) - len(visible), value))

    neighbors = []
    for kind in range(4):
        ends = [kind % 2, *range(3, outer_count)]
        if kind >= 2:
            ends.append(outside)
        neighbors.append(sum(1 << u for u in ends))
    counts = (2, 2, *shields)

    @functools.lru_cache(maxsize=None)
    def connected(outer, middle_counts):
        if not outer:
            return sum(middle_counts) == 1
        incident = [outer & ends for count, ends in zip(middle_counts, neighbors) if count]
        if 0 in incident:
            return False
        seen = outer & -outer
        while True:
            before = seen
            for group in incident:
                if group & seen:
                    seen |= group
            if before == seen:
                return seen == outer

    best = {}
    for outer in range(1 << outer_count):
        if outer & (1 << outside):
            continue
        placed = []
        for row in weights:
            choices = []
            for sign in (0, 1):
                crossings = [(cost, bit) for end, cost, bit in row if (outer >> end & 1) != sign]
                choices.append((sum(c for c, _ in crossings), sum(b for _, b in crossings)))
            placed.append(choices)
        extras = [{0: 0}, {0: 0}]
        for color, count, price_here in unnamed:
            positive_anchors = (outer >> 3).bit_count()
            positive_hub = outer >> color & 1
            cost_if_negative = hub_cost * positive_hub + positive_anchors
            cost_if_positive = hub_cost * (1 - positive_hub) + anchors - positive_anchors + price_here
            merged = {}
            for existing, cost in extras[color].items():
                for k in range(count + 1):
                    total = cost + k * cost_if_positive + (count - k) * cost_if_negative
                    key = existing + k
                    merged[key] = min(merged.get(key, total), total)
            extras[color] = merged

        @functools.lru_cache(maxsize=None)
        def best_extra(explicit):
            answer = None
            for red, red_cost in extras[0].items():
                for blue, blue_cost in extras[1].items():
                    positive = (explicit[0], explicit[1], explicit[2] + red, explicit[3] + blue)
                    negative = tuple(n - k for n, k in zip(counts, positive))
                    if connected(outer, positive) and connected(all_outer ^ outer, negative):
                        candidate = red_cost + blue_cost
                        answer = candidate if answer is None else min(answer, candidate)
            return answer

        for signs in itertools.product((0, 1), repeat=len(types)):
            positive = [0] * 4
            cut_word = cost = 0
            for kind, sign, choices in zip(types, signs, placed):
                positive[kind] += sign
                amount, partial = choices[sign]
                cost += amount
                cut_word |= partial
            extra = best_extra(tuple(positive))
            if extra is not None:
                candidate = cost + extra
                best[cut_word] = min(best.get(cut_word, candidate), candidate)

    sorted_cuts = sorted(best, key=best.get)
    rows = [bytearray((len(sorted_cuts) + 7) // 8) for _ in names]
    for i, word in enumerate(sorted_cuts):
        while word:
            bit = word & -word
            rows[bit.bit_length() - 1][i // 8] |= 1 << (i % 8)
            word ^= bit
    rows = [int.from_bytes(row, "little") for row in rows]
    index = {name: i for i, name in enumerate(names)}
    rename = [index[({"a": "c", "c": "a"}.get(m, m), role)] for m, role in names]

    def minimum(query):
        possible = rows[query[0]]
        for i in query[1:]:
            possible &= rows[i]
        if possible:
            first = (possible & -possible).bit_length() - 1
            return best[sorted_cuts[first]]
        return None

    records = []
    first = None
    for order in range(1, arity + 1):
        checked = failed = 0
        for group in itertools.combinations(range(len(names)), order):
            image = tuple(sorted(rename[i] for i in group))
            if image == group:
                continue
            checked += 1
            a, b = minimum(group), minimum(image)
            if a != b:
                failed += 1
                if first is None:
                    first = {"query": [names[i] for i in group], "image": [names[i] for i in image],
                             "values": [a, b], "order": order}
        records.append({"order": order, "moved_representative_queries": checked, "failures": failed})
    result = {"red_links_at_one": red_changes, "rows": records, "first_failure": first}
    if tracked:
        aliases = {}
        for color in "RB":
            used = sorted({int(m[1:]) for m, role in tracked if m.startswith(color)})
            for reduced in (False, True):
                chosen = [i for i in used if (color == "R" and i < red_changes) == reduced]
                allowed = [i for i in range(shields["RB".index(color)])
                           if (color == "R" and i < red_changes) == reduced]
                aliases.update({f"{color}{a}": f"{color}{b}" for a, b in zip(chosen, allowed)})
        indices = [index[(aliases.get(m, m), role)] for m, role in tracked]
        result["tracked_values"] = [minimum(indices), minimum([rename[i] for i in indices])]
    return result


def load_python(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def literal_stages(anchors, shields, spoke, arm, hub_cost, price, changing, query):
    old = "LATER-BOND-READING-20261119-001"
    branch = load_python("scale_archived_branch",
                         ROOT / "experiments" / old / f"{old}-E001_future" / "constructive_branch.py")
    engine = load_python("scale_archived_round", branch.ENGINE)
    starts = 3 + anchors
    names = ["a", "b", "c", "d"]
    names.extend(f"{color}{i}" for color, n in zip("RB", shields) for i in range(n))
    stars = [set() for _ in range(starts + len(names))]
    edges = {}
    pole = None
    next_bit = 0
    for j, middle in enumerate(names):
        u = starts + j
        special = middle in "abcd" and len(middle) == 1
        hub = int(middle in ("c", "d") if special else middle.startswith("B"))
        pools = [(hub, "hub", spoke if special else hub_cost), (3, "anchor0", arm if special else 1)]
        pools.extend((3 + i, f"anchor{i}", 1) for i in range(1, anchors))
        if not special:
            if middle == changing:
                pole = u
            else:
                amount = 1 if middle.startswith("R") and int(middle[1:]) < int(changing[1:]) else price
                pools.append((2, "outside", amount))
        for v, role, amount in pools:
            edges[middle, role] = list(range(next_bit, next_bit + amount))
            stars[u].update(edges[middle, role])
            stars[v].update(edges[middle, role])
            next_bit += amount
    start, branches = branch.attach_branches(price, stars, [pole, 2])
    current = engine.grow1(start)
    after = engine.grow1(current)
    first = branch.actual_additions(start, current)
    second = branch.actual_additions(current, after)
    branch_nodes = {pole, 2}
    cap_sites = []
    for root, a, c, middle in branches:
        expected = [frozenset((a, b)) for b in middle] + [frozenset([c, *middle])]
        posts = frozenset(first[row] for row in expected)
        cap_sites.append(second[posts])
        branch_nodes.update({a, c, *middle, *posts})
    assert len(first) == 2 * price and len(second) == 2
    assert nx.minimum_cut_value(branch.wired(current, branch_nodes), pole, 2) == price
    assert nx.minimum_cut_value(branch.wired(after, branch_nodes | set(cap_sites)), pole, 2) == 1
    for stage in (start, current, after):
        graph = branch.wired(stage, set(range(len(stage))))
        assert all(len(star) >= 3 for star in stage)
        assert all(u == "outside" for u in nx.articulation_points(graph))
        assert all(graph[u][v]["capacity"] > 1 for u, v in nx.bridges(graph))
    image = {}
    for role in ["hub", *[f"anchor{i}" for i in range(anchors)]]:
        for a, c in zip(edges["a", role], edges["c", role], strict=True):
            image[a], image[c] = c, a
    for stage in (current, after):
        ownership = branch.holders(stage)
        live = {ends[0] for ends in ownership.values() if len(ends) == 1}
        assert all(x not in image for u in live for x in stage[u])
    chosen = [edges[m, role][0] for m, role in query]
    return {
        "ordinary_sites": [len(a) for a in (start, current, after)],
        "distinctions": [len(branch.holders(a)) for a in (start, current, after)],
        "two_pole_price": [price, 1],
        "swapped_name_pairs": [[a, c] for a, c in image.items() if a < c],
        "decisive_old_names": chosen, "images": [image.get(x, x) for x in chosen],
    }


def telescope(arity, anchors, shields, spoke, arm, hub_cost, price):
    stages = []
    for i in range(shields[0] + 1):
        record = one_price(arity, anchors, shields, spoke, arm, hub_cost, price, i)
        stages.append(record)
        if record["first_failure"]:
            assert i > 0 and record["first_failure"]["order"] == arity
            e = (f"R{i - 1}", "outside")
            assert e not in record["first_failure"]["query"]
            assert e not in record["first_failure"]["image"]
            break
    else:
        raise AssertionError("the selected trajectory needs a failure")
    a = stages[-1]["first_failure"]
    tracked = one_price(arity, anchors, shields, spoke, arm, hub_cost, price, i - 1, a["query"])
    assert tracked["tracked_values"][0] == tracked["tracked_values"][1]
    literal = literal_stages(anchors, shields, spoke, arm, hub_cost, price, f"R{i-1}", a["query"])
    return {"arity": arity, "anchors": anchors, "shields_per_hub": shields, "test_to_hub": spoke,
            "test_to_special_anchor": arm, "shield_to_hub": hub_cost, "initial_exterior_price": price,
            "stages": stages, "changing_link": [f"R{i - 1}", "outside"],
            "decisive_query": a, "previous_values": tracked["tracked_values"], "literal": literal}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = {
        "method": "Enumerate all outer signs and marked-middle representatives. Unmarked same-price shields permute freely. A dynamic minimum over their counts tests connectedness of both shores before scoring. Every moved query contains a or c, so at most r-1 shield sites of any color/price are needed explicitly.",
        "cases": [telescope(2, 1, [3, 3], 4, 4, 14, 14),
                  telescope(3, 2, [6, 6], 2, 3, 6, 4)],
    }
    # JSON supplies lists for edge names on both creation and comparison.
    encoded = json.dumps(result, indent=2) + "\n"
    if args.check:
        if OUT.read_text() != encoded:
            raise SystemExit("saved telescope differs")
    else:
        OUT.write_text(encoded)
    for case in result["cases"]:
        print(case["arity"], case["changing_link"], case["decisive_query"]["values"])
