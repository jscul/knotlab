"""Distinguish one knot's read from sums of local reads on chosen family trees."""
import argparse
import json
import resource
from time import perf_counter
from diagnostics import HERE, literal_local_reads, tree_levels


def check(steps):
    live = [0]
    for d in steps:
        live.append(live[-1] + d)
    n = live[-1] + 1
    owners = [(i, i + 1) for i in range(n - 1) for repeat in range(2)]
    owners.extend((i,) for i in live)
    neighbours = [set() for _ in range(n)]
    loose = {}
    rows = [[] for _ in neighbours]
    for distinction, group in enumerate(owners):
        for i in group:
            rows[i].append(distinction)
        if len(group) == 2:
            a, b = group
            neighbours[a].add(b)
            neighbours[b].add(a)
        else:
            loose[group[0]] = distinction
    # Each live knot is its own family. Each pair with a common witness
    # would violate this assertion; consecutive live knots have gaps 1,3,5.
    assert all(len(group.intersection(loose)) <= 1 for group in neighbours)
    assert min(map(len, rows)) >= 3
    # Exhibit an allowed starting change for each even tuple. Pair its
    # selected loose distinctions in order and follow the intervening chain.
    realized = 0
    for value in range(1 << len(live)):
        if value.bit_count() % 2:
            continue
        selected = [k for i, k in enumerate(live) if value & (1 << i)]
        changed = {loose[k] for k in selected}
        for left, right in zip(selected[::2], selected[1::2]):
            changed.update(2 * k for k in range(left, right))
        assert all(len(changed.intersection(row)) % 2 == 0 for row in rows)
        realized += 1
    d = {}
    for i, a in enumerate(live):
        distance = {a: 0}
        queue = [a]
        for u in queue:
            for v in neighbours[u]:
                if v not in distance:
                    queue.append(v)
                    distance[v] = distance[u] + 1
        for j in range(i):
            d[j, i] = distance[live[j]]
    levels, equations = tree_levels(len(live), d)
    kept, local, joint, least = literal_local_reads(len(live), equations)
    all_families = (1 << len(live)) - 1
    local_images = []
    for parent, children in equations:
        places = children if parent == all_families else [parent, *children]
        image = {"".join(str((s & g).bit_count() % 2) for g in places)
                 for s in range(all_families + 1) if s.bit_count() % 2 == 0}
        assert len(image) == 2 ** (len(places) - 1)
        assert all(word.count("1") % 2 == 0 for word in image)
        local_images.append({"places": places, "projected values": sorted(image)})
    example = None
    if kept != local:
        # The test fact adds the first and third sibling-pair parities.
        mask = 0b00110011
        assert mask in kept - local and mask in joint
        refutations = []
        for parent, children in equations:
            view = children if parent == all_families else [parent, *children]
            # Give this knot the same reading as the all-zero state.
            other = next(s for s in range(all_families + 1)
                         if s.bit_count() % 2 == 0 and (s & mask).bit_count() % 2
                         and all((s & g).bit_count() % 2 == 0 for g in view))
            refutations.append({"knot masks": view, "even family tuple with all its readings zero": other})
        example = {"fact mask": mask, "local summands": [3, 48], "single-knot counterexamples": refutations}
    return {"step counts between consecutive live knots": steps, "number of starting knots": n,
            "start, one list of distinctions per knot": rows, "live knots in family order": live,
            "levels, with clusters as family masks": levels, "family tuples realized at the start": realized,
            "values on each chosen local list": local_images,
            "least change of the chosen tree places": least, "nonconstant kept facts": len(kept) - 1,
            "read by one knot": len(local) - 1, "in the sum of single-knot reads": len(joint) - 1,
            "counterexample": example}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (256 << 20, 256 << 20))
    start = perf_counter()
    examples = [check([1, 3, 1])]
    if not args.pilot:
        examples.append(check([1, 3, 1, 5, 1, 3, 1]))
        examples.append(check([1, 3, 1, 5, 1, 3, 1, 5, 1, 3, 1]))
        (HERE / "single_reads.json").write_text(json.dumps(examples, indent=2) + "\n")
    print([(r["number of starting knots"], r["nonconstant kept facts"], r["read by one knot"])
           for r in examples], round(perf_counter() - start, 6))
