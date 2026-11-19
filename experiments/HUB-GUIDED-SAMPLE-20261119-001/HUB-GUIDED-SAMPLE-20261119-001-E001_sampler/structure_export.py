"""Export a uniform maximal-set unranker for an actual induced two-block stage."""
import argparse
import hashlib
import json
import random
from pathlib import Path

from structure_union import context, irreducible, make_diagram, project, read_blocks, transposed


def portable(diagram, root):
    numbers = {0: 0, 1: 1}
    nodes = [(diagram.n, 0, 0, 0), (diagram.n, 1, 1, 1)]
    def visit(index):
        if index not in numbers:
            coord, low, high = diagram.nodes[index]
            lo, hi = visit(low), visit(high)
            numbers[index] = len(nodes)
            nodes.append((coord, lo, hi, diagram.models(index, coord)))
        return numbers[index]
    return visit(root), nodes


def recipe(blocks, left_id, right_id, coordinate_limit, literal_columns=None, cap=1500000):
    left, right, exclusions = context(blocks, left_id, right_id)
    selected = list(irreducible(exclusions))[:coordinate_limit] if literal_columns is None else literal_columns
    columns, _, row_masks = project(exclusions, left, selected)
    diagram, root, order = make_diagram(row_masks, len(columns), cap)
    count = diagram.models(root)
    order_names = [columns[j] for j in order]
    sites = physical_sites(blocks, left_id, right_id, left, right, exclusions, order_names)
    compact_root, nodes = portable(diagram, root)
    return dict(coordinates=order_names, count=count, root=compact_root, nodes=nodes,
                sites=sites, blocks=[left_id, right_id])


def physical_sites(blocks, left_id, right_id, left, right, exclusions, order_names):
    raw = {v: exclusions[v] for v in order_names}
    signs = transposed(raw, left)
    sites = [(v, 0, sign) for v, sign in signs.items()]
    sites.extend((v, 0, 0) for v in set(blocks[left_id]) & set(blocks[right_id]))
    for v in right:
        missing = exclusions[v]
        generated = 0
        sign = 0
        for j, value in enumerate(raw.values()):
            if missing & value == value:
                generated |= value
                sign |= 1 << j
        if generated == missing:
            sites.append((v, 1, sign))
    return sorted(sites)


def unrank(data, index):
    k = len(data["coordinates"])
    assert 0 <= index < data["count"]
    root = data["root"]
    nodes = data["nodes"]
    occupied = 0
    for j in range(k):
        level, lo, hi, _ = nodes[root]
        if level != j:
            assert level > j
            lo = hi = root
        next_level, _, _, ways = nodes[lo]
        lower = ways << (next_level - j - 1)
        if index < lower:
            root = lo
        else:
            index -= lower
            root = hi
            occupied |= 1 << j
    assert root == 1 and index == 0
    return [v for v, side, mask in data["sites"]
            if ((mask & occupied == 0) if side else (mask & ~occupied == 0))]


def save(data, n, path):
    k = len(data["coordinates"])
    w = (k+63)//64
    mask = (1<<64)-1
    with path.open("w") as stream:
        print(n, k, len(data["nodes"]), len(data["sites"]), data["root"], data["count"], file=stream)
        print(*data["coordinates"], file=stream)
        for row in data["nodes"]:
            print(*row, file=stream)
        for v, side, sign in data["sites"]:
            print(v, side, *((sign>>(64*i)) & mask for i in range(w)), file=stream)


def check_groups(blocks, data, ranks, decode=unrank):
    # Compare direct clique and maximality conditions on the original vertices.
    inside = {v for v, _, _ in data["sites"]}
    all_mask = sum(1<<v for v in inside)
    adj = dict.fromkeys(inside, 0)
    for block in blocks:
        subset = inside.intersection(block)
        mask = sum(1<<v for v in subset)
        for v in subset:
            adj[v] |= mask
    duplicates = set()
    audits = []
    for i in ranks:
        group = decode(data, i)
        mask = sum(1<<v for v in group)
        allowed = all_mask
        for v in group:
            allowed &= adj[v]
        assert allowed == mask and mask not in duplicates
        duplicates.add(mask)
        fingerprints = hashlib.sha256(" ".join(map(str, group)).encode()).hexdigest()
        audits.append(dict(rank=i, size=len(group), sha256_space_separated_sorted_decimal_ids=fingerprints))
    return audits


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--columns", type=int, default=85)
    parser.add_argument("--literal-columns", type=Path)
    parser.add_argument("--left", type=int, default=35)
    parser.add_argument("--right", type=int, default=0)
    parser.add_argument("--cap", type=int, default=1500000)
    args = parser.parse_args()
    n, blocks = read_blocks(args.stage)
    literal = None if args.literal_columns is None else json.loads(args.literal_columns.read_text())
    data = recipe(blocks, args.left, args.right, args.columns, literal, args.cap)
    save(data, n, args.destination)
    ranks = {0, data["count"]-1}
    rng = random.Random(23111723)
    for _ in range(12):
        ranks.add(rng.randrange(data["count"]))
    audits = check_groups(blocks, data, sorted(ranks))
    record = dict(stage_sha256=hashlib.sha256(args.stage.read_bytes()).hexdigest(),
                  source_blocks=data["blocks"], induced_vertices=len(data["sites"]),
                  left_vertices=sum(side==0 for _,side,_ in data["sites"]),
                  right_vertices=sum(side==1 for _,side,_ in data["sites"]), coordinates=len(data["coordinates"]),
                  count=data["count"], diagram_nodes_including_terminals=len(data["nodes"]),
                  file=args.destination.name, uncompressed_sha256=hashlib.sha256(args.destination.read_bytes()).hexdigest(),
                  literal_projection=data["coordinates"], direct_maximality_checks=audits)
    if args.report:
        args.report.write_text(json.dumps(record, indent=2)+"\n")
    print({k:v for k,v in record.items() if k not in ("literal_projection","direct_maximality_checks")})


if __name__ == "__main__":
    main()
