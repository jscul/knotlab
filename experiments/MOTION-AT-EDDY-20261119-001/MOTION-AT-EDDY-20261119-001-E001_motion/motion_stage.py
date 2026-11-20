"""Literal parity incidence, minimum responses, and co-knotted-pair steps."""

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from functools import cache, cached_property
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, product
import json
from math import comb, prod
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EDDY = "EDDY-WORLD-20261119-001"
STAGES = ROOT / "artifacts" / EDDY / (EDDY + "-E001_world") / "stages.json"
INPUTS = HERE / "inputs.json"
SHORT_CIRCUIT_LIMIT = 200_000
OVERLAP_WORK_LIMIT = 5_000_000


@dataclass(frozen=True)
class MinimumResponse:
    minimum_size: int | None
    count: int
    outside_count: int
    least_reach: int | None
    greatest_reach: int | None
    supports: tuple[frozenset[int], ...]

    @property
    def listed_all_supports(self):
        return self.count == len(self.supports)


def anonymous_owners(stars):
    owners = defaultdict(list)
    for v, row in enumerate(stars):
        if len(row) != len(set(row)):
            raise ValueError(f"repeated distinction in junction {v}")
        for bit in row:
            owners[bit].append(v)
    if any(len(holders) > 2 for holders in owners.values()):
        raise ValueError("a distinction has more than two holders")
    return {bit: tuple(holders) for bit, holders in sorted(owners.items())}


class MotionStage:
    """A fixed anonymous stage. Integer names are used only for identity."""

    def __init__(self, stars):
        self.stars = tuple(tuple(sorted(row)) for row in stars)
        self.owners = anonymous_owners(self.stars)
        self.outside = len(self.stars)
        self.loose = frozenset(bit for bit, row in self.owners.items() if len(row) == 1)
        self.ends = {bit: row if len(row) == 2 else (*row, self.outside)
                     for bit, row in self.owners.items()}
        self.bundles = [defaultdict(list) for _ in range(self.outside + 1)]
        for bit, (u, v) in self.ends.items():
            self.bundles[u][v].append(bit)
            self.bundles[v][u].append(bit)

    def co_knotted(self, first, second):
        return first != second and bool(set(self.owners[first]) & set(self.owners[second]))

    def distances_from(self, marks):
        """Physical distinction-step lengths. Unreachable distinctions are omitted."""
        mark_order = tuple(dict.fromkeys(marks))
        if not mark_order or not all(bit in self.owners for bit in mark_order):
            raise ValueError("co-knotted-pair steps require at least one literal distinction")
        found = dict.fromkeys(mark_order, 0)
        queue = deque(mark_order)
        processed_holders = set()
        while queue:
            bit = queue.popleft()
            for v in self.owners[bit]:
                if v in processed_holders:
                    continue
                processed_holders.add(v)
                for other in self.stars[v]:
                    if other not in found:
                        found[other] = found[bit] + 1
                        queue.append(other)
        return found

    def allowed_change(self, support):
        support = set(support)
        if not support <= self.owners.keys():
            raise ValueError("change contains an unknown distinction")
        odd = set()
        for bit in support:
            odd.symmetric_difference_update(self.owners[bit])
        return not odd

    def _steps(self, v, target, pinned_loose):
        for w, names in self.bundles[v].items():
            if pinned_loose and self.outside in (v, w):
                continue
            for bit in names:
                if bit != target:
                    yield w, bit

    def _search(self, source, target, pinned_loose):
        distances = {source: 0}
        order = [source]
        for v in order:
            for w, _ in self._steps(v, target, pinned_loose):
                if w not in distances:
                    distances[w] = distances[v] + 1
                    order.append(w)
        return distances, order

    @cached_property
    def short_circuits(self):
        """All literal simple circuits of size two through four, including parallel pairs."""
        catalogue = defaultdict(list)

        def add(length, alternatives):
            count = prod(map(len, alternatives))
            if len(catalogue[length]) + count > SHORT_CIRCUIT_LIMIT:
                raise ValueError(f"literal size-{length} circuit roster exceeds the cap")
            catalogue[length].extend(frozenset(row) for row in product(*alternatives))

        wedges = defaultdict(list)
        for v, neighbors in enumerate(self.bundles):
            for w in neighbors:
                if v < w:
                    if len(catalogue[2]) + comb(len(neighbors[w]), 2) > SHORT_CIRCUIT_LIMIT:
                        raise ValueError("literal parallel-pair roster exceeds the cap")
                    catalogue[2].extend(frozenset(row) for row in combinations(neighbors[w], 2))
            for u, w in combinations(sorted(neighbors), 2):
                wedges[u, w].append(v)
                if u < v < w and w in self.bundles[u]:
                    add(3, (self.bundles[u][v], self.bundles[v][w], self.bundles[u][w]))
        for (u, w), middles in wedges.items():
            for v, x in combinations(middles, 2):
                if (u, w) < (v, x):
                    add(4, (self.bundles[u][v], self.bundles[v][w],
                            self.bundles[w][x], self.bundles[x][u]))
        cooked = {}
        for length in (2, 3, 4):
            rows = catalogue[length]
            assert len(set(rows)) == len(rows)
            cooked[length] = tuple(sorted(rows, key=lambda row: tuple(sorted(row))))
        return cooked

    @cached_property
    def _short_by_bit(self):
        rows = defaultdict(list)
        for supports in self.short_circuits.values():
            for support in supports:
                for bit in support:
                    rows[bit].append(support)
        return rows

    @cache
    def minimum_response(self, target, *, pinned_loose=False):
        """Count all minimum supports and list every tie whenever the size is at most four."""
        impossible = MinimumResponse(None, 0, 0, None, None, ())
        u, v = self.ends[target]
        if pinned_loose and target in self.loose:
            return impossible
        left, order = self._search(u, target, pinned_loose)
        if v not in left:
            return impossible
        right, _ = self._search(v, target, pinned_loose)
        total = left[v]
        reach = self.distances_from([target])
        paths = Counter({u: 1})
        outside = Counter()
        low, high = {u: 0}, {u: 0}
        for x in order:
            if x not in right or left[x] + right[x] != total:
                continue
            for y, bit in self._steps(x, target, pinned_loose):
                if y not in right or left[y] != left[x] + 1 or left[y] + right[y] != total:
                    continue
                paths[y] += paths[x]
                outside[y] += paths[x] if y == self.outside else outside[x]
                r = reach[bit]
                lo, hi = max(low[x], r), max(high[x], r)
                low[y] = min(low.get(y, lo), lo)
                high[y] = max(high.get(y, hi), hi)
        size = total + 1
        tied = ()
        if size <= 4:
            tied = tuple(row for row in self._short_by_bit[target]
                         if len(row) == size and (not pinned_loose or not row & self.loose))
            assert len(tied) == paths[v]
            assert sum(bool(row & self.loose) for row in tied) == outside[v]
        return MinimumResponse(size, paths[v], outside[v], low[v], high[v], tied)

    @cache
    def ordinary_quads(self, *, pinned_loose=False):
        """Ordinary four-distinction changes that minimize for at least one of their marks."""
        four = self.short_circuits[4]
        return tuple(row for row in four if not row & self.loose and any(
            self.minimum_response(bit, pinned_loose=pinned_loose).minimum_size == 4 for bit in row))


def support_neighbors(supports, overlap=1):
    """Adjacency on the supplied support order, using exact distinction identity."""
    if overlap < 1:
        raise ValueError("overlap must be positive")
    supports = tuple(supports)
    postings = defaultdict(list)
    for i, support in enumerate(supports):
        for bit in set(support):
            postings[bit].append(i)
    if sum(comb(len(indices), 2) for indices in postings.values()) > OVERLAP_WORK_LIMIT:
        raise ValueError("support pair roster exceeds the overlap work cap")
    overlaps = Counter(pair for indices in postings.values() for pair in combinations(indices, 2))
    neighbors = [[] for _ in supports]
    for (i, j), count in overlaps.items():
        if count == overlap:
            neighbors[i].append(j)
            neighbors[j].append(i)
    return tuple(tuple(sorted(row)) for row in neighbors)


@cache
def _load_archive(path):
    return json.loads(path.read_text())["cases"]


def extra_case_specs():
    """The four specified sources, with literal shared labels in meeting order."""
    cases = []
    for name, seams in (("B81", ()), ("J81", (30,)), ("T81", (30, 50)), ("R31", ())):
        path = list(range(81)) if name != "R31" else []
        meetings = [[i, i + 1] for i in path[:-1]]
        anchors = list(range(len(meetings)))
        rings = [[seam, *range(81 + 4 * i, 85 + 4 * i)] for i, seam in enumerate(seams)]
        if name == "R31":
            rings = [list(range(31))]
        ring_edges = []
        for vertices in rings:
            first = len(meetings)
            meetings.extend([u, v] for u, v in zip(vertices, vertices[1:] + vertices[:1], strict=True))
            ring_edges.append(list(range(first, len(meetings))))
        background_spares = [0, 1, 79, 80] if path else []
        ring_spares = [[ring[2]] if seams else [] for ring in rings]
        spare = set(background_spares) | {v for row in ring_spares for v in row}
        n = max(max(pair) for pair in meetings) + 1
        neighbors = [set() for _ in range(n)]
        for u, v in meetings:
            neighbors[u].add(v)
            neighbors[v].add(u)
        sizes = [len(row) + sum(len(neighbors[u]) - 1 for u in row) + (v in spare)
                 for v, row in enumerate(neighbors)]
        assert all(x >= 3 for x in sizes)
        cases.append({"id": name, "sizes": sizes, "meetings": meetings, "ages": [0, 1],
                      "roles": {"background": path, "rings": rings, "seams": list(seams), "anchors": anchors,
                                "ring_edges": ring_edges, "background_spares": background_spares,
                                "ring_spares": ring_spares}})
    return cases


@cache
def growth_engine():
    producer_path = ROOT / "experiments" / EDDY / (EDDY + "-E001_world") / "world_growth.py"
    spec = spec_from_file_location("motion_eddy_growth", producer_path)
    growth = module_from_spec(spec)
    spec.loader.exec_module(growth)
    return growth


@cache
def _extra_case(case, inputs):
    source = json.loads(inputs.read_text())
    found = source.get("extra_cases", source.get("cases", []))
    if isinstance(found, dict):
        literal = found[case]
        literal = {"id": case, **literal}
    else:
        literal, = (row for row in found if row["id"] == case)
    expected, = (row for row in extra_case_specs() if row["id"] == case)
    assert all(literal[key] == expected[key] for key in ("sizes", "meetings", "roles"))
    grown = growth_engine().grow_case(literal, 1, {"junctions": 2048, "distinctions": 8192})
    assert set(grown["stages"]) == {"0", "1"}
    assert grown["qualification"]["canonical"] and grown["qualification"]["DOUBLE_IDENT"]["in_class"]
    return grown


def load_case_record(case, *, path=STAGES, inputs=INPUTS):
    archive = _load_archive(Path(path).resolve())
    if case in archive:
        return archive[case]
    return _extra_case(case, Path(inputs).resolve())


def load_stage(case, age=1, *, path=STAGES):
    return MotionStage(load_case_record(case, path=path)["stages"][str(age)]["stars"])


def load_marks(case, *, path=STAGES):
    """Evaluator crosswalk, separate from the anonymous stage and response rules."""
    entry = load_case_record(case, path=path)
    stars = tuple(tuple(row) for row in entry["stages"]["0"]["stars"])
    owners = anonymous_owners(stars)
    roles = entry["input"]["roles"]
    anchors = roles["anchors"]
    return {**roles, "source_stars": stars, "source_owners": owners,
            "source_shared": frozenset(bit for bit, row in owners.items() if len(row) == 2),
            "source_loose": frozenset(bit for bit, row in owners.items() if len(row) == 1),
            "path_landmarks": (anchors[0], anchors[-1]) if anchors else (),
            "ring_landmarks": tuple((row[1], row[3]) for row in roles["ring_edges"])}
