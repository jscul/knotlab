"""Test the two forbidden minors directly on each finished pattern of meetings."""

from collections import Counter, defaultdict
from functools import lru_cache
from itertools import combinations
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
PRIOR = HERE.parents[1] / "READER-SPLIT-20261127-001" / "referee-R1"


def graph(knots):
    holders = defaultdict(list)
    for index, distinctions in enumerate(knots):
        for distinction in distinctions:
            holders[distinction].append(index)
    assert all(len(pair) == 2 for pair in holders.values())
    return tuple(sorted(set(map(tuple, holders.values()))))


def connected(vertices, meetings):
    reached = {next(iter(vertices))}
    while True:
        more = {v for pair in meetings if reached.intersection(pair) for v in pair}
        if more <= reached:
            return reached == vertices
        reached.update(more)


def contract(meetings, u, v):
    # Relabel densely after identifying the ends of one meeting.
    named = sorted({k for pair in meetings for k in pair if k != v})
    indices = {k: i for i, k in enumerate(named)}
    indices[v] = indices[u]
    return tuple(sorted({tuple(sorted((indices[a], indices[b]))) for a, b in meetings
                         if indices[a] != indices[b]}))


@lru_cache(maxsize=32768)
def forbidden_minor(meetings):
    neighbours = defaultdict(set)
    for u, v in meetings:
        neighbours[u].add(v)
        neighbours[v].add(u)
    if len(neighbours) < 5 or len(meetings) < 9:
        return None
    # A pendant meeting or a subdivision preserves planarity in both directions.
    for vertex, adj in neighbours.items():
        if len(adj) <= 2:
            return forbidden_minor(contract(meetings, next(iter(adj)), vertex))
    for triple in combinations(neighbours, 3):
        if len(set.intersection(*(neighbours[k] for k in triple))) >= 3:
            return "K3,3"
    for five in combinations((k for k in neighbours if len(neighbours[k]) >= 4), 5):
        if all(v in neighbours[u] for u, v in combinations(five, 2)):
            return "K5"
    # If disjoint connected branch sets model either minor, contract within
    # them until its simple graph is present. Extra vertices/meetings can be ignored.
    if len(neighbours) > 5:
        for u, v in meetings:
            witness = forbidden_minor(contract(meetings, u, v))
            if witness:
                return witness
    return None


def main():
    k5 = tuple(combinations(range(5), 2))
    k33 = tuple((u, v) for u in range(3) for v in range(3, 6))
    for expected, pattern in (("K5", k5), ("K3,3", k33)):
        assert forbidden_minor(pattern) == expected
        assert forbidden_minor(pattern[1:]) is None
        a, b = pattern[0]
        assert forbidden_minor(tuple(sorted((*pattern[1:], (a, 9), (b, 9))))) == expected
    splits = {(r["population"], r["key"]): r for r in
              map(json.loads, (PRIOR / "split_rows.jsonl").open())}
    data = {}
    for pop, identifier, source in (("birth", "start", "results.jsonl"), ("type", "type", "census_types.jsonl")):
        reference = {r[identifier]: r for r in map(json.loads, (HERE.parent / source).open())}
        counts = Counter()
        rows = []
        differences = []
        for row in map(json.loads, (PRIOR / "rebuilt_inputs.jsonl").open()):
            if row["population"] != pop:
                continue
            key = row["key"]
            meetings = graph(row["supports"])
            vertices = set(range(len(row["supports"])))
            assert connected(vertices, meetings)
            minor = forbidden_minor(meetings)
            split = splits[pop, key]
            strict, general = split["strict_min"], split["general_min"]
            kind = "strict" if strict is not None else ("other only" if general is not None else "none")
            counts[" / ".join(("nonplanar" if minor else "planar", kind))] += 1
            arc = reference[key]
            if (minor is None, kind) != (arc["planar"], arc["readers study's kind"]):
                differences.append(key)
            rows.append({"id": key, "minor": minor, "strict_min": strict, "general_min": general})
        assert len(rows) == len(reference) and len({r["id"] for r in rows}) == len(rows)
        data[pop] = {"weighting": "one per census start" if pop == "birth" else "one per finished census type",
                     "connected": len(rows), "counts": counts, "archived_row_disagreements": differences,
                     "general_minimum_lower_despite_strict_split": sum(
                         r["strict_min"] is not None and r["general_min"] < r["strict_min"] for r in rows),
                     "rows": rows}
    (HERE / "meetings.json").write_text(json.dumps(data, indent=1) + "\n")
    print({k: (dict(v["counts"]), v["archived_row_disagreements"]) for k, v in data.items()})


if __name__ == "__main__":
    main()
