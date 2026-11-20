"""Physical stage data shared by the growing-end and current-distance checks."""
from collections import Counter, defaultdict, deque
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / "artifacts" / HERE.parent.name / HERE.name
PREV = "SAME-SIDE-READING-20261119-001"
sys.path.insert(0, str(ROOT / "experiments" / PREV / (PREV+"-E001_side")))
from side_sources import cases, generate, loads, padded


def distances(adjacencies, roots):
    distance = dict.fromkeys(roots, 0)
    queue = deque(distance)
    while queue:
        v = queue.popleft()
        for u in adjacencies[v]:
            if u not in distance:
                queue.append(u)
                distance[u] = distance[v]+1
    return distance


class Stage:
    """Construct from literal current supports. The correspondence is separate from the reading."""
    def __init__(self, stars, occupied, knot_ids, age, ancestor_sets):
        self.stars = stars
        self.occupied = set(occupied)
        self.ids = knot_ids[:]
        self.age = age
        self.ancestors = ancestor_sets[:]
        self.ends = defaultdict(list)
        self.neighbors = [set() for row in stars]
        for v, row in enumerate(stars):
            for m in row:
                self.ends[m].append(v)
        self.open = Counter()
        for m, holders in self.ends.items():
            if len(holders)==1:
                self.open[holders[0]]+=1
            else:
                p,q=holders
                self.neighbors[p].add(q)
                self.neighbors[q].add(p)
        assert len(self.stars)==len(self.ids)==len(set(self.ids))
        assert len(self.ancestors)==len(self.stars)


def stages(spec, occupied, end_at, shared_codes):
    names = list(range(len(spec["sizes"])))
    ancestors = [1 << i for i in names]
    for t, frame in generate(spec, occupied, end_at):
        if t:
            sibling_counts = Counter()
            for v in frame["born"]:
                ps = frame["parent_sets"][v]
                pattern = tuple(sorted(names[p] for p in ps))
                sibling_counts[pattern] += 1
                key = (pattern,sibling_counts[pattern])
                code = shared_codes.setdefault(key, len(spec["sizes"])+len(shared_codes))
                assert v == len(names)
                names.append(code)
                origins = 0
                for p in ps:
                    origins |= ancestors[p]
                ancestors.append(origins)
        yield Stage(frame["stars"], frame["occupied"], names, t, ancestors)
