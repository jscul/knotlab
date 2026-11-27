"""Read families directly from supplied distinctions; never execute ordinary growth."""
import argparse
import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent.parent
PREVIOUS = RESEARCH / "CHAIN-COUNT-20261127-001"


def families(parents):
    """Maximal families with no common parent, followed by every uncovered pair."""
    holders = defaultdict(list)
    for child, ps in parents.items():
        for parent in ps:
            holders[parent].append(child)
    candidates = nx.Graph()
    for siblings in holders.values():
        candidates.add_edges_from(combinations(siblings, 2))
    groups = set()
    uncovered = set(frozenset(pair) for pair in candidates.edges)
    for members in nx.find_cliques(candidates):
        if len(members) >= 3 and not set.intersection(*(set(parents[x]) for x in members)):
            groups.add(frozenset(members))
            uncovered.difference_update(map(frozenset, combinations(members, 2)))
    return groups | uncovered


class Reading:
    def __init__(self, stars):
        owners = defaultdict(list)
        for knot, star in enumerate(stars):
            assert len(set(star)) == len(star)
            for distinction in star:
                owners[distinction].append(knot)
        loose = Counter()
        neighbours = defaultdict(set)
        for held in owners.values():
            if len(held) == 1:
                loose[held[0]] += 1
            else:
                left, right = held
                neighbours[left].add(right)
                neighbours[right].add(left)
        live = sorted(loose)
        self.parents = {w: frozenset() for w in live}
        self.chains = {w: frozenset() for w in live}
        self.ranks = [live, []]
        self.next_id = len(stars)
        groups = families({w: neighbours[w] for w in live})
        for group in sorted(tuple(sorted(g)) for g in groups):
            self.add(1, group, ())
        chain = 0
        for w in live:
            spare = loose[w] - sum(w in g for g in groups)
            if spare < 0:
                raise ValueError("shortage")
            for _ in range(spare):
                count = max(0, 3 - loose[w])
                self.add(1, [w], range(chain, chain + count))
                chain += count

    def add(self, rank, parents, chains):
        code = self.next_id
        self.next_id += 1
        self.parents[code] = frozenset(parents)
        self.chains[code] = frozenset(chains)
        self.ranks[rank].append(code)

    def next_rank(self):
        last = self.ranks[-1]
        groups = families({n: self.parents[n] for n in last})
        self.ranks.append([])
        for group in sorted(tuple(sorted(g)) for g in groups):
            self.add(len(self.ranks) - 1, group,
                     frozenset().union(*(self.chains[n] for n in group)))

    def children_round(self, current, t):
        """Every vector with positive total has one predecessor removing its largest index."""
        self.next_rank()
        new = [(c, ()) for c in self.ranks[t + 1]]
        for c, vector in current:
            new.extend((c, vector + (e,)) for e in sorted(self.chains[c])
                       if not vector or e >= vector[-1])
        return new

    def extended_parents(self, node):
        c, vector = node
        used = frozenset(vector)
        shortened = {(c, vector[:i] + vector[i + 1:]) for i in range(len(vector))
                     if i == 0 or vector[i - 1] != vector[i]}
        lifted = {(p, vector) for p in self.parents[c] if used <= self.chains[p]}
        return frozenset(shortened | lifted)


def inspect_difference(core, parents, rule_only, reading_only, proposed):
    """Describe all incidences, round-rule gains and losses, with no fallback label."""
    def compatible(a, b):
        return bool(parents[a] & parents[b])

    def twin(g):
        lower = [c for c, v in g if not v]
        upper = [(p, v) for p, v in g if v]
        if len(lower) < 2 or len(upper) < 2:
            return None
        vectors = {v for p, v in upper}
        if len(vectors) != 1 or len(next(iter(vectors))) != 1:
            return None
        if not all(p in core.parents[c] for c in lower for p, v in upper):
            return None
        if not all(compatible(a, b) for a, b in combinations(upper, 2)):
            return None
        return [len(lower), len(upper)]

    twin_groups = {g: twin(g) for g in rule_only if twin(g)}
    split_groups = defaultdict(list)
    splits = []
    for lost in reading_only:
        nodes = proposed[lost]
        for c, vector in nodes:
            short = frozenset(x for x in lost if x[0] == c)
            lifts = lost - short
            missing = [(a, b) for a, b in combinations(lost, 2) if not compatible(a, b)]
            if not missing:
                continue
            assert short and all(a in lifts and b in lifts for a, b in missing)
            graph = nx.Graph()
            graph.add_nodes_from(lifts)
            graph.add_edges_from((a, b) for a, b in combinations(lifts, 2) if compatible(a, b))
            pieces = {short | frozenset(part) for part in nx.find_cliques(graph)}
            for part in pieces & rule_only:
                split_groups[part].append((c, vector))
            splits.append(dict(short=len(short), lifts=len(lifts), incompatible=len(missing),
                               pieces=sorted(map(len, pieces)), exact=pieces <= rule_only))
    def listing(groups):
        return sorted(sorted(g) for g in groups)
    return dict(gained=listing(rule_only), lost=listing(reading_only),
                children=[dict(family=sorted(g), children=sorted(proposed[g])) for g in sorted(reading_only, key=sorted)],
                twins=sorted(twin_groups.values()), splits=splits,
                unexplained_gains=listing(rule_only - twin_groups.keys() - split_groups.keys()),
                unexplained_losses=listing({g for g in reading_only
                     if not any(g < h for h in twin_groups)
                     and all(compatible(a, b) for a, b in combinations(g, 2))}),
                twin_absorbed=sorted(len(g) for g in reading_only if any(g < h for h in twin_groups)))


def first_failure(stars, horizon=20, width_cap=12000):
    core = Reading(stars)
    current = [(c, ()) for c in core.ranks[1]]
    history = []
    for t in range(1, horizon):
        if max(len(current), len(core.ranks[-1])) > width_cap:
            return dict(status="cut", round=t, history=history)
        parents = {x: core.extended_parents(x) for x in current}
        rule = families(parents)
        following = core.children_round(current, t)
        proposed = defaultdict(list)
        for y in following:
            ps = core.extended_parents(y)
            if len(ps) >= 2:
                proposed[ps].append(y)
        counts = Counter({family: len(children) for family, children in proposed.items()})
        history.append([t, len(current), len(rule), counts.total()])
        gained = rule - proposed.keys()
        lost = set(counts - Counter(rule))
        if gained or lost:
            return dict(status="failure", member_round=t, child_round=t + 1, history=history,
                        repeated_parent_sets=[sorted(ps) for ps, n in counts.items() if n > 1],
                        **inspect_difference(core, parents, gained, lost, proposed))
        if not following:
            break
        current = following
    return dict(status="agreement", history=history)


def load_rows():
    # Use the prior failed-row index only to locate original starts. The anonymous
    # replay entry has no draw key, so test all three starts in that input file.
    seen = set()
    for name in ["ext_samples.txt", "ext_cycles.txt"]:
        for line in (PREVIOUS / name).read_text().splitlines():
            if not line.startswith("{"):
                continue
            index = json.loads(line)
            if not index.get("first failing round"):
                continue
            path = (PREVIOUS / index["file"]).resolve()
            for i, record in enumerate(map(json.loads, path.read_text().splitlines()), 1):
                if record.get("draw", record.get("index")) != index["draw"]:
                    continue
                key = (path, i)
                if key not in seen:
                    seen.add(key)
                    yield path, i, record
    path = HERE.parent / "referee_witnesses.jsonl"
    for i, row in enumerate(map(json.loads, path.read_text().splitlines()), 1):
        yield path, i, row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rows = []
    for path, i, record in load_rows():
        if args.limit is not None and len(rows) >= args.limit:
            break
        result = first_failure(record["stars"])
        rows.append(dict(file=str(path.relative_to(RESEARCH)), line=i, **result))
    print(Counter(r["status"] for r in rows), Counter(r.get("child_round") for r in rows))
    if args.output:
        args.output.write_text(json.dumps(rows, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
