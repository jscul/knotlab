"""Classify roster automorphisms that displace every junction to a noncandidate."""

import argparse
import gzip
import hashlib
import json
import re
import time
from collections import Counter, defaultdict
from pathlib import Path


def set_bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def bitmask(indices):
    mask = 0
    for value in indices:
        mask |= 1 << value
    return mask


def colors(profiles):
    ids = {}
    return [ids.setdefault(profile, len(ids)) for profile in profiles], len(ids)


def read_json_gzip(path):
    with gzip.open(path, "rt") as readable:
        return json.load(readable)


def load_blocks(path):
    raw = path.read_bytes()
    header, *lines = raw.splitlines()
    n, b = map(int, header.split())
    if n < 0 or b < 0 or len(lines) != b:
        raise ValueError(f"invalid roster dimensions in {path.name}")
    blocks = []
    for line in lines:
        block = tuple(sorted(map(int, line.split())))
        if len(block) < 2 or block[0] < 0 or block[-1] >= n or len(set(block)) != len(block):
            raise ValueError(f"invalid roster block in {path.name}")
        blocks.append(block)
    if len(set(blocks)) != b:
        raise ValueError(f"repeated roster block in {path.name}")
    return n, blocks, hashlib.sha256(raw).hexdigest()


def literal_roster(source):
    sizes = source["sizes"]
    actual = [set() for _ in sizes]
    for a, b in source["edges"]:
        actual[a].add(b)
        actual[b].add(a)
    loose = [size - len(neighbors) for size, neighbors in zip(sizes, actual, strict=True)]
    live = [v for v, open_count in enumerate(loose) if open_count > 0]
    labels = {v: i for i, v in enumerate(live)}
    all_blocks = {frozenset(labels[v] for v in adjacent if v in labels) for adjacent in actual}
    blocks = []
    for block in sorted(all_blocks, key=lambda a: (-len(a), sorted(a))):
        if len(block) >= 2 and not any(block <= current for current in blocks):
            blocks.append(block)
    return [loose[v] for v in live], [tuple(sorted(block)) for block in blocks]


def verify_mapping(image, blocks, affiliations, opens=None):
    """Replay a literal certificate without any assumed automorphism orbits."""
    n = len(affiliations)
    if sorted(image) != list(range(n)):
        return False
    if any(a == b or affiliations[a] & affiliations[b] for a, b in enumerate(image)):
        return False
    if opens is not None and any(opens[a] != opens[b] for a, b in enumerate(image)):
        return False
    given = set(blocks)
    return all(tuple(sorted(image[v] for v in block)) in given for block in blocks)


def allowed_images(classes, affiliations, block_masks):
    allowed = {}
    for nodes in classes.values():
        if len(nodes) <= 32:
            for v in nodes:
                allowed[v] = bitmask(w for w in nodes if v != w and not affiliations[v] & affiliations[w])
                if not allowed[v]:
                    return allowed, v
            continue
        class_mask = bitmask(nodes)
        for v in nodes:
            remaining = class_mask & ~(1 << v)
            for b in set_bits(affiliations[v]):
                remaining &= ~block_masks[b]
                if not remaining:
                    break
            if not remaining:
                return allowed, v
            allowed[v] = remaining
    return allowed, None


def find_matching(classes, allowed):
    """Either one permitted bijection or a replayable Hall obstruction."""
    import networkx as nx

    image = {}
    for nodes in classes.values():
        graph = nx.Graph()
        left = [(0, v) for v in nodes]
        graph.add_nodes_from(left)
        graph.add_nodes_from((1, v) for v in nodes)
        for v in nodes:
            graph.add_edges_from(((0, v), (1, w)) for w in set_bits(allowed[v]))
        match = nx.algorithms.bipartite.hopcroft_karp_matching(graph, top_nodes=left)
        if len(match) != 2 * len(nodes):
            # Build the reachable left set in the alternating graph.
            reached = {v for v in left if v not in match}
            queue = list(reached)
            seen_right = set()
            for v in queue:
                for right in graph[v]:
                    if right in seen_right:
                        continue
                    seen_right.add(right)
                    nxt = match.get(right)
                    if nxt is not None and nxt not in reached:
                        reached.add(nxt)
                        queue.append(nxt)
            source = sorted(v for _, v in reached)
            targets = sorted(w for _, w in seen_right)
            if len(source) <= len(targets):
                raise ArithmeticError("matching search did not yield a Hall obstruction")
            return None, {"source": source, "allowed_targets": targets}
        image.update((v, match[0, v][1]) for v in nodes)
    return [image[v] for v in range(len(allowed))], None


class SearchCap(Exception):
    pass


def exact_search(n, blocks, point_color, block_color, allowed, supply_check, limit):
    """Enumerate all qualifying incidence automorphisms unless a work cap fires."""
    import networkx as nx

    graph = nx.Graph()
    graph.add_nodes_from((v, {"color": (0, point_color[v])}) for v in range(n))
    graph.add_nodes_from((n + b, {"color": (1, block_color[b])}) for b in range(len(blocks)))
    graph.add_edges_from((v, n + b) for b, block in enumerate(blocks) for v in block)

    class Constrained(nx.algorithms.isomorphism.GraphMatcher):
        attempts = 0

        def syntactic_feasibility(self, v, w):
            self.attempts += 1
            if self.attempts > limit:
                raise SearchCap
            if graph.nodes[v]["color"] != graph.nodes[w]["color"]:
                return False
            if v < n and not (allowed[v] >> w) & 1:
                return False
            return super().syntactic_feasibility(v, w)

    matcher = Constrained(graph, graph)
    structural_witness = None
    try:
        for mapping in matcher.isomorphisms_iter():
            image = [mapping[v] for v in range(n)]
            if supply_check(image):
                return image, matcher.attempts, True, None
            if structural_witness is None:
                structural_witness = image
    except SearchCap:
        return None, limit, False, structural_witness
    return None, matcher.attempts, True, structural_witness


def classify(n, blocks, opens, support, *, search_vertices=240, search_attempts=400000):
    """Decide what the incidence and verified supply support on one roster."""
    record = {"live": n, "blocks": len(blocks), "exact_opens_given": opens is not None}
    if not n:
        return record | {"verdict": "closed", "reason": "no live junctions"}
    if opens is not None and (len(opens) != n or any(x < 1 for x in opens)):
        raise ValueError("exact opens must give a positive count for every live junction")
    affinities = [0] * n
    for b, block in enumerate(blocks):
        bit = 1 << b
        for v in block:
            affinities[v] |= bit

    block_sizes = [len(block) for block in blocks]
    block_color, num_block_colors = colors(block_sizes)
    point_color, num_point_colors = colors(
        (opens[v] if opens is not None else 0,
         tuple(sorted(block_sizes[b] for b in set_bits(affinities[v])))) for v in range(n)
    )
    step = 0
    while True:
        frequencies = Counter(point_color)
        if 1 in frequencies.values():
            v = next(v for v, x in enumerate(point_color) if frequencies[x] == 1)
            return record | {"verdict": "excluded_all", "reason": "unique invariant junction profile",
                             "refinement_steps": step, "profile_classes": num_point_colors,
                             "fixed_junction": v,
                             "incident_block_sizes": sorted(block_sizes[b] for b in set_bits(affinities[v]))}
        next_block, next_block_count = colors(
            (block_color[b], tuple(sorted(point_color[v] for v in block))) for b, block in enumerate(blocks)
        )
        next_point, next_point_count = colors(
            (point_color[v], tuple(sorted(next_block[b] for b in set_bits(affinities[v])))) for v in range(n)
        )
        if (num_point_colors, num_block_colors) == (next_point_count, next_block_count):
            break
        point_color, block_color = next_point, next_block
        num_point_colors, num_block_colors = next_point_count, next_block_count
        step += 1
    record.update(refinement_steps=step, profile_classes=num_point_colors)
    classes = defaultdict(list)
    for v, profile in enumerate(point_color):
        classes[profile].append(v)
    allowed, no_image = allowed_images(classes, affinities, [bitmask(block) for block in blocks])
    if no_image is not None:
        return record | {"verdict": "excluded_all", "reason": "entire invariant class is closed candidate",
                         "junction": no_image, "class_size": len(classes[point_color[no_image]])}

    def supply_check(image):
        if opens is not None:
            return all(opens[v] == opens[w] for v, w in enumerate(image))
        if support is None:
            return False
        return all(support[v] == support[w] for v, w in enumerate(image))

    def positive(image, method):
        if not verify_mapping(image, blocks, affinities, opens) or not supply_check(image):
            raise ArithmeticError("mapped incidence certificate failed replay")
        return record | {"verdict": "certified", "reason": method, "image": image,
                         "involution": all(image[image[v]] == v for v in range(n)),
                         "supply_basis": "exact opens" if opens is not None else "one-parent flag and open rule"}

    if all(choices.bit_count() == 1 for choices in allowed.values()):
        forced = [allowed[v].bit_length() - 1 for v in range(n)]
        if not verify_mapping(forced, blocks, affinities, opens):
            return record | {"verdict": "excluded_all", "reason": "only allowed map fails block preservation or bijection"}
        if supply_check(forced):
            return positive(forced, "literal verification of forced images")
        return record | {"verdict": "partial", "reason": "only map preserves incidence, opens unverified",
                         "block_only_image": forced}

    matching = None
    if n <= 512:
        matching, hall = find_matching(classes, allowed)
        if hall is not None:
            return record | {"verdict": "excluded_all", "reason": "Hall obstruction", "hall": hall}
        if verify_mapping(matching, blocks, affinities, opens) and supply_check(matching):
            return positive(matching, "literal verification of permitted matching")

    if n + len(blocks) > search_vertices:
        return record | {"verdict": "partial", "reason": "incidence search outside declared size limit",
                         "search_vertices": search_vertices}
    image, attempts, complete, structural = exact_search(
        n, blocks, point_color, block_color, allowed, supply_check, search_attempts
    )
    record["search_attempts"] = attempts
    if image is not None:
        return positive(image, "constrained incidence automorphism")
    if structural is not None:
        if not verify_mapping(structural, blocks, affinities, opens):
            raise ArithmeticError("block-only certificate failed replay")
        return record | {"verdict": "partial", "reason": "incidence symmetry found, opens unverified",
                         "block_only_image": structural, "search_finished": complete}
    if complete:
        return record | {"verdict": "excluded_all", "reason": "exhaustive constrained incidence search"}
    return record | {"verdict": "partial", "reason": "exact search work cap"}


def load_archive_stage(path, stage, control, expected_digest, sidecars):
    n, blocks, digest = load_blocks(path)
    if expected_digest is not None and digest != expected_digest:
        raise ValueError(f"archive digest mismatch for {path.name}")
    opens_path = path.with_suffix(".opens.json.gz")
    opens = None
    if "opens" in sidecars and opens_path.exists():
        if hashlib.sha256(opens_path.read_bytes()).hexdigest() != sidecars["opens"]["sha256"]:
            raise ValueError(f"opens digest mismatch for {path.name}")
        opens = read_json_gzip(opens_path)
    elif control is not None and control["blocks_sha256"] == digest:
        opens = control["loose"]

    # Try the larger class of incidence automorphisms first. If one
    # survives the exact tests, a noninitial reconstructed stage can
    # replay the open rule from its one-parent flags.
    first = classify(n, blocks, opens, None)
    parent_path = path.with_suffix(".parents.json.gz")
    if (first["verdict"] == "partial" and opens is None and stage > 0
            and "parents" in sidecars and parent_path.exists()):
        parent_digest = hashlib.sha256(parent_path.read_bytes()).hexdigest()
        if parent_digest != sidecars["parents"]["sha256"]:
            raise ValueError(f"parent digest mismatch for {path.name}")
        parents = read_json_gzip(parent_path)
        if len(parents) != n or any(not row for row in parents):
            raise ValueError(f"misaligned parent roster for {path.name}")
        support = [len(row) == 1 for row in parents]
        first = classify(n, blocks, None, support)
        first["parent_sidecar_sha256"] = parent_digest
    return first | {"source_file": path.name, "blocks_sha256": digest}


def run_stage(payload):
    start = time.monotonic()
    if "literal" in payload:
        opens, blocks = literal_roster(payload["literal"])
        summary = classify(len(opens), blocks, opens, None)
        summary["source_file"] = "HUB-GUIDED-SAMPLE stages.json literal_starts"
    else:
        summary = load_archive_stage(Path(payload["file"]), payload["age"], payload.get("control"),
                                     payload.get("sha256"), payload.get("sidecars", {}))
    return {"case": payload["case"], "age": payload["age"], "seconds": time.monotonic() - start} | summary


def archive_cases(archive, control_dir, stage_index, control_index):
    index = json.loads(stage_index.read_text())
    controls = json.loads(control_index.read_text())
    stage_rows = {(row["case"], row["age"]): row for row in index["stages"]}
    control_rows = {(row["name"], row["age"]): row for row in controls}
    used = set()
    for name, literal in sorted(index["literal_starts"].items()):
        used.add((name, 0))
        yield f"{name}-age00", {"case": name, "age": 0, "literal": literal}
    for folder in (archive, control_dir):
        for file in sorted(folder.glob("*.txt")):
            tag = re.fullmatch(r"(start-\d{2}|partner-\d+)-age(\d{2})\.txt", file.name)
            if tag is None:
                continue
            name, text_age = tag.groups()
            age = int(text_age)
            pair = name, age
            if pair in used:
                continue
            recorded = stage_rows.get(pair)
            control = control_rows.get(pair)
            meta = file.with_suffix(".meta.json")
            if recorded is None and folder == archive and meta.exists():
                recorded = json.loads(meta.read_text())
            if recorded is None and control is None:
                continue
            if recorded is not None and folder == archive:
                digest = recorded["files"]["blocks"]["sha256"]
            else:
                digest = None if control is None else control["blocks_sha256"]
            payload = {"case": name, "age": age, "file": str(file), "sha256": digest}
            if folder == archive and recorded is not None:
                payload["sidecars"] = {k: value for k, value in recorded["files"].items()
                                       if k in ("opens", "parents")}
            if control is not None:
                payload["control"] = {key: control[key] for key in ("loose", "blocks_sha256")}
            used.add(pair)
            yield f"{name}-age{age:02d}", payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("controls", type=Path)
    parser.add_argument("stage_index", type=Path)
    parser.add_argument("control_index", type=Path)
    parser.add_argument("--only", action="append")
    args = parser.parse_args()
    for name, payload in archive_cases(args.archive, args.controls, args.stage_index, args.control_index):
        if args.only is None or name in args.only:
            print(json.dumps(run_stage(payload)), flush=True)


if __name__ == "__main__":
    main()
