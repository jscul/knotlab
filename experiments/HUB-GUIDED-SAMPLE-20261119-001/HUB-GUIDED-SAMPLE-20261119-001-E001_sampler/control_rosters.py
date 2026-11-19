"""Archived fixed control rosters and an independent exact group census."""

import argparse
from collections import Counter
import gzip
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import sys

import networkx as nx

from control_hybrid import classify, indices


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SIZE_TICKET = "JUNCTION-SIZE-FOLLOW-20261119-001/JUNCTION-SIZE-FOLLOW-20261119-001-E001_growth"
sys.path.insert(0, str(ROOT / "experiments" / SIZE_TICKET))
from probe_growth import group_deck, initial_roster, maximum_blocks  # noqa: E402


def blocks_text(opens, blocks):
    return f"{len(opens)} {len(blocks)}\n" + "".join(" ".join(map(str, indices(b)))+"\n" for b in blocks)


def normalize_next(opens, blocks):
    deck = group_deck(len(opens), blocks, 1_600_000)
    spare = [o-d for o,d in zip(opens, deck.demand, strict=True)]
    assert min(spare, default=0) >= 0
    parents = sorted([*deck.groups(), *(1 << j for j, free in enumerate(spare) for _ in range(free))])
    if parents == [(1 << len(opens))-1] and opens == (1,)*len(opens):
        return (), (), parents, [0]
    next_blocks = [0]*len(opens)
    for j, parents_of_birth in enumerate(parents):
        for u in indices(parents_of_birth):
            next_blocks[u] |= 1 << j
    next_blocks = maximum_blocks(next_blocks)
    if len(parents) <= 1800:
        demand = group_deck(len(parents), next_blocks, 1_600_000).demand
    else:
        known = classify((1,)*len(parents), next_blocks)
        assert known is not None, "large control continuation lacks an exact structural certificate"
        demand = known.demand
    fresh = tuple(max(f, 3-p.bit_count(), 1) for f,p in zip(demand, parents, strict=True))
    return fresh, next_blocks, parents, fresh


def exact_truth(opens, blocks):
    """Independent NetworkX exact groups, including every compatible residual pair."""
    graph = nx.Graph()
    graph.add_nodes_from(range(len(opens)))
    for b in blocks:
        graph.add_edges_from(combinations(indices(b),2))
    held_parts = set(blocks)
    maximal = [tuple(sorted(c)) for c in nx.find_cliques(graph)]
    held_maximal = sum(sum(1 << x for x in g) in held_parts for g in maximal)
    large = [g for g in maximal if len(g) >= 3 and sum(1 << x for x in g) not in held_parts]
    covered = {pair for members in large for pair in combinations(members,2)}
    remaining = [tuple(sorted(e)) for e in graph.edges() if tuple(sorted(e)) not in covered]
    demand = Counter(u for group in large+remaining for u in group)
    extras = tuple(opens[u]-demand[u] for u in range(len(opens)))
    assert min(extras, default=0) >= 0
    return {"large_groups": len(large), "residual_pairs": len(remaining), "offshoots": sum(extras),
            "births": len(large)+len(remaining)+sum(extras), "raw_maximal_cliques": len(maximal),
            "held_maximal_cliques": held_maximal, "isolated": sum(len(g) == 1 for g in maximal),
            "literal_large": large, "literal_pairs": remaining, "offshoot_by_parent": extras}


def make_entry(name, age, opens, blocks):
    return {"name": name, "age": age, "loose": opens, "blocks": blocks,
            "blocks_sha256": sha256(blocks_text(opens, blocks).encode()).hexdigest()}


def archive_regrowth(name):
    archived = json.loads((ROOT / "artifacts" / SIZE_TICKET / "probe_merge.json").read_text())["merge"][name]
    opens, blocks = initial_roster(archived["start_sizes"], [tuple(e) for e in archived["start_meetings"]])
    read_at = archived["growth"]["single_block"]["at_age"]
    data = []
    for age in range(read_at+1):
        entry = make_entry(name, age, opens, blocks)
        if age == read_at:
            hybrid = classify(opens, blocks)
            assert hybrid is not None and hybrid.exact_binomial_tail
            assert hybrid.births == archived["growth"]["rows"][age]["births"]
            data.append(entry | {"recognition": hybrid.kind, "known_births": hybrid.births})
            break
        truth = exact_truth(opens, blocks)
        novel_open, next_blocks, parents, fresh = normalize_next(opens, blocks)
        hist = Counter((p.bit_count(), f) for p,f in zip(parents,fresh,strict=True))
        assert [[p,f,c] for (p,f),c in sorted(hist.items())] == archived["growth"]["rows"][age]["birth_histogram"]
        assert len(parents) == truth["births"]
        hybrid = classify(opens, blocks)
        data.append(entry | {"recognition": None if hybrid is None else hybrid.kind, "truth": truth})
        opens, blocks = novel_open, next_blocks
    return data


def paired_start(k):
    return ((1 << (k-1)),)*(2*k), tuple((1 << a) | (1 << b) for a,b in combinations(range(2*k),2) if a//2 != b//2)


def archive_partnered(k, max_age):
    data = []
    opens, blocks = paired_start(k)
    for age in range(max_age+1):
        table = classify(opens, blocks)
        assert table is not None and table.kind == "complete_partnered" and table.offshoots == 0
        entry = make_entry(f"partner-{k}", age, opens, blocks)
        if len(opens) <= 24:
            truth = exact_truth(opens, blocks)
            assert (truth["large_groups"], truth["residual_pairs"], truth["offshoots"], truth["births"]) == (
                table.large_groups, table.residual_pairs, table.offshoots, table.births)
            entry["truth"] = truth
        data.append(entry)
        if age < max_age:
            opens, blocks, _, _ = normalize_next(opens, blocks)
    return data


def export_rows(source):
    """Emit one compact integrated control record usable by a separate sampler."""
    results = []
    for entry in source:
        item = {k:v for k,v in entry.items() if k not in {"blocks", "truth"}}
        item["blocks"] = [list(indices(b)) for b in entry["blocks"]]
        if "truth" in entry:
            item["truth"] = {k:v for k,v in entry["truth"].items() if not k.startswith("literal_")}
        results.append(item)
    return results


def source_controls():
    return (archive_regrowth("start-00") + archive_regrowth("start-04") +
            archive_partnered(2, 1) + archive_partnered(3, 3) +
            archive_partnered(4, 1) + archive_partnered(5, 1))


def import_start03_age07(folder):
    """Reuse the stage worker's exact archived export and verify every next parent set."""
    path = folder/"start-03-age07.txt"
    size, *lines = path.read_text().splitlines()
    n, count = map(int,size.split())
    blocks = tuple(sum(1 << int(u) for u in row.split()) for row in lines)
    assert n == 386 and len(blocks) == count
    with gzip.open(folder/"start-03-age08.parents.json.gz", "rt") as src:
        children = json.load(src)
    assert len(children) == 28065
    supply = Counter(v for parents in children for v in parents)
    opens = tuple(supply[u] for u in range(n))
    truth = exact_truth(opens, blocks)
    expected = Counter(truth["literal_large"] + truth["literal_pairs"])
    expected.update((u,) for u,c in enumerate(truth["offshoot_by_parent"]) for _ in range(c))
    assert expected == Counter(tuple(sorted(group)) for group in children)
    assert (truth["raw_maximal_cliques"],truth["held_maximal_cliques"],truth["residual_pairs"],truth["offshoots"]) == (28099,91,56,1)
    record = make_entry("start-03", 7, opens, blocks)
    assert record["blocks_sha256"] == sha256(path.read_bytes()).hexdigest()
    return record | {"truth":truth}


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("output", type=Path)
    cli.add_argument("--text-dir", type=Path)
    cli.add_argument("--start03-source", type=Path)
    args = cli.parse_args()
    controls = source_controls()
    if args.start03_source:
        controls.append(import_start03_age07(args.start03_source))
    args.output.write_text(json.dumps(export_rows(controls), separators=(",", ":"))+"\n")
    if args.text_dir:
        args.text_dir.mkdir(parents=True, exist_ok=True)
        for entry in controls:
            leaf = f"{entry['name']}-age{entry['age']:02d}.txt"
            (args.text_dir / leaf).write_text(blocks_text(entry["loose"], entry["blocks"]))
