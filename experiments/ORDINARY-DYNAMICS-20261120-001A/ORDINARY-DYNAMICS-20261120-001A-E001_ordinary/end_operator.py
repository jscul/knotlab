"""Independent complete-round operator on the growing end of a connected presentation."""

from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations


def maximal_blocks(blocks):
    candidates = {frozenset(row) for row in blocks}
    kept = []
    for row in sorted(candidates,key=lambda row:(-len(row),tuple(sorted(row)))):
        if len(row)>=2 and not any(row<=some for some in kept):
            kept.append(row)
    return tuple(sorted(tuple(sorted(row)) for row in kept))


@dataclass(frozen=True)
class End:
    opens: dict[int,int]
    blocks: tuple[tuple[int,...],...]

    def __post_init__(self):
        opens = dict(sorted(self.opens.items()))
        blocks = maximal_blocks(self.blocks)
        if any(not isinstance(n,int) or n<1 for n in opens.values()):
            raise ValueError("each live knot must supply a positive integer open count")
        if any(p not in opens for group in blocks for p in group):
            raise ValueError("every witnessed knot in a block must be live")
        object.__setattr__(self,"opens",opens)
        object.__setattr__(self,"blocks",blocks)


@dataclass(frozen=True)
class Turn:
    status: str
    parents: tuple[tuple[int,...],...] = ()
    fresh: tuple[int,...] = ()
    demand: tuple[int,...] = ()
    end: End | None = None
    shortages: tuple[tuple[int,int],...] = ()
    implied: bool = False
    planned_births_lower: int | None = None


def neighbors(end):
    graph = {k:set() for k in end.opens}
    for block in end.blocks:
        for a,b in combinations(block,2):
            graph[a].add(b)
            graph[b].add(a)
    return graph


def from_stars(stars):
    holders = defaultdict(list)
    graph = [set() for _ in stars]
    for knot,support in enumerate(stars):
        for distinction in support:
            holders[distinction].append(knot)
    opens = Counter()
    for row in holders.values():
        if len(row)==1:
            opens[row[0]] += 1
        elif len(row)==2 and row[0]!=row[1]:
            a,b = row
            graph[a].add(b)
            graph[b].add(a)
        else:
            raise ValueError("a distinction must have one or two different holders")
    if not graph:
        raise ValueError("a presentation must contain at least one knot")
    todo = [0]
    seen = {0}
    for v in todo:
        unseen = graph[v]-seen
        seen.update(unseen)
        todo.extend(unseen)
    if len(seen)!=len(graph):
        raise ValueError("the proof of the closing case requires one connected presentation")
    return End(opens,tuple(row & opens.keys() for row in graph))


def restricted(end, points):
    keep = set(points)
    return End({p:n for p,n in end.opens.items() if p in keep},
               tuple(tuple(p for p in row if p in keep) for row in end.blocks))


def _maximal_groups(graph, blocks):
    """Enumerate exactly the unheld maximal complete groups by a pivot split."""
    held = tuple(map(frozenset,blocks))
    stack = [(set(),set(graph),set())]
    while stack:
        group,possible,previous = stack.pop()
        if len(group | possible)<3 or any(group|possible <= row for row in held):
            continue
        if not possible:
            if not previous:
                yield tuple(sorted(group))
            continue
        pivot = max(possible|previous,key=lambda k:(len(graph[k]&possible),-k))
        for knot in sorted(possible-graph[pivot]):
            stack.append((group|{knot},possible&graph[knot],previous&graph[knot]))
            possible.remove(knot)
            previous.add(knot)


class _Cap(Exception):
    pass


def _proposals(end, cap):
    graph = neighbors(end)
    big = []
    covered = set()
    for group in _maximal_groups(graph,end.blocks):
        if cap is not None and len(big)==cap:
            raise _Cap
        big.append(group)
        covered.update(combinations(group,2))
    pairs = []
    for a in graph:
        for b in sorted(graph[a]):
            if a<b and (a,b) not in covered:
                if cap is not None and len(big)+len(pairs)==cap:
                    raise _Cap
                pairs.append((a,b))
    return tuple(sorted(big)+pairs)


def proposals(end):
    return _proposals(end,None)


def _parent_blocks(parents):
    children = defaultdict(list)
    for i,group in enumerate(parents):
        for old in group:
            children[old].append(i)
    return tuple(map(tuple,children.values()))


def _demands(parents):
    lookahead = End(dict.fromkeys(range(len(parents)),1),_parent_blocks(parents))
    counts = Counter(v for row in proposals(lookahead) for v in row)
    return tuple(counts[i] for i in range(len(parents))),lookahead.blocks


def step(end, law="parity", max_births=None):
    """Return one full plan; child identities are positions in ``parents`` and ``fresh``."""
    if law not in {"parity","nae"}:
        raise ValueError(f"unknown knot law {law!r}")
    if max_births is not None and max_births<0:
        raise ValueError("max_births must be nonnegative")
    if not end.opens:
        return Turn("closed")
    try:
        multi = _proposals(end,max_births)
    except _Cap:
        return Turn("cap",planned_births_lower=max_births+1)
    used = Counter(v for row in multi for v in row)
    scarce = tuple((k,used[k]-available) for k,available in end.opens.items() if used[k]>available)
    if scarce:
        return Turn("stall",shortages=scarce)
    count = len(multi)+sum(n-used[k] for k,n in end.opens.items())
    if max_births is not None and count>max_births:
        return Turn("cap",planned_births_lower=count)
    parents = multi+tuple((k,) for k,n in end.opens.items() for _ in range(n-used[k]))
    demand,blocks = _demands(parents)
    implied = law=="parity" and len(parents)==1
    fresh = (0,) if implied else tuple(max(d,3-len(group),1) for group,d in zip(parents,demand,strict=True))
    following = End({i:n for i,n in enumerate(fresh) if n},blocks)
    return Turn("extend",parents,fresh,demand,following,implied=implied)


def local_counts(end, anchor):
    """Evaluate births through one parent without consulting global stall or closure."""
    graph = neighbors(end)
    inner = {anchor}|graph[anchor]
    outer = inner.union(*(graph[v] for v in inner))
    multi = proposals(restricted(end,outer))
    local_used = Counter(k for group in multi for k in group if k in inner)
    if any(local_used[k]>end.opens[k] for k in inner):
        return None
    local = tuple(group for group in multi if inner.intersection(group))
    local += tuple((k,) for k in sorted(inner) for _ in range(end.opens[k]-local_used[k]))
    # All siblings of every child of the anchor are present. Groups through it
    # see their entire candidate neighborhoods and thus their exact demand.
    demand,_ = _demands(local)
    return tuple((group,d,max(d,3-len(group),1)) for group,d in zip(local,demand,strict=True) if anchor in group)
