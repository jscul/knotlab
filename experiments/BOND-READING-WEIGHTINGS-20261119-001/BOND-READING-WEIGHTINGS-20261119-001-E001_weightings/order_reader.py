"""Exact and bounded observation orders for a marked finite parity stage.

read_order(stars, terminal=False) uses the standard library. An optional
compiled exact cut reader (BOND_ORDER_READER_ENGINE) extends the pair range.
refine_order gives a targeted stage wider work limits without sampling.
Witness names are zero-based positions in sorted distinction order.
"""

from argparse import ArgumentParser
from bisect import bisect_right
from collections import defaultdict
from itertools import combinations
import json
import os
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRIOR = ROOT / "experiments/GROWN-END-MEET-ONCE-20261119-001/GROWN-END-MEET-ONCE-20261119-001-E001_rounds"


def prepare_native(directory):
    """Build the exact archived cut engine with this module's input format."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    source = (PRIOR / "census.cpp").read_text()
    signature = "int main(int argc, char** argv)"
    assert source.count(signature) == 1
    source = source.replace(signature, "int archived_census_main(int argc, char** argv)")
    driver = (HERE / "order_reader.cpp").read_text()
    # Reinstantiate exactly the archived pair search with larger vertex masks.
    # The adapter passes the same compressed graph and leaves the cut search intact.
    start = source.index("struct PairTable {")
    stop = source.index("    // The existing extension search", start)
    wide = source[start:stop] + "};\n"
    for original, replacement in (("PairTable", "WidePairTable"), ("Incidence", "WideIncidence"),
                                  ("Mask", "WideMask"), ("60", "128"),
                                  ("std::countr_zero(", "first_wide("), ("bit(", "wide_bit("),
                                  ("pop(", "take_wide(")):
        wide = wide.replace(original, replacement)
    wide_types, separator, main = driver.partition("// End of wide declarations.\n")
    assert separator
    binary = directory / "order_reader"
    subprocess.run(["c++", "-std=c++20", "-O3", "-Wno-return-type", "-iquote", str(PRIOR),
                    "-x", "c++", "-", "-o", binary],
                   input=source + "\nnamespace census {\n" + wide_types + wide + "}\n" + main,
                   text=True, check=True)
    return binary


def indices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def connected(side, neighbors):
    if not side:
        return False
    pending = seen = side & -side
    while pending:
        bit = pending & -pending
        pending ^= bit
        extra = neighbors[bit.bit_length() - 1] & side & ~seen
        pending |= extra
        seen |= extra
    return seen == side


class Basis:
    def __init__(self, rows=()):
        self.rows = {}
        for word in rows:
            self.add(word)

    def reduce(self, word):
        while word and (pivot := word.bit_length()) in self.rows:
            word ^= self.rows[pivot]
        return word

    def add(self, word):
        if word := self.reduce(word):
            self.rows[word.bit_length()] = word


class Stage:
    def __init__(self, stars):
        raw = [tuple(row) for row in stars]
        names = list(dict.fromkeys(b for row in raw for b in row))
        try:
            names.sort()
        except TypeError:
            names.sort(key=lambda x: (type(x).__name__, repr(x)))
        slot = {b: i for i, b in enumerate(names)}
        self.stars = tuple(tuple(sorted(slot[b] for b in row)) for row in raw)
        if any(len(row) != len(set(row)) for row in self.stars):
            raise ValueError("a support repeats a distinction")
        self.width = len(names)
        holder = [[] for _ in names]
        for j, row in enumerate(self.stars):
            for b in row:
                holder[b].append(j)
        if any(len(v) not in (1, 2) for v in holder):
            raise ValueError("a distinction needs one or two holders")
        self.live = {v[0] for v in holder if len(v) == 1}
        self.outside = len(self.stars)
        self.vertices = self.outside + bool(self.live)
        self.fixed = {b for j in self.live for b in self.stars[j]}
        self.free = tuple(b for b in range(self.width) if b not in self.fixed)
        by_edges = defaultdict(list)
        for b, ends in enumerate(holder):
            e = tuple(ends) if len(ends) == 2 else (ends[0], self.outside)
            by_edges[e].append(b)
        self.edges = tuple(by_edges)
        self.bundles = tuple(tuple(names) for names in by_edges.values())
        self.of = [0] * self.width
        self.neighbors = [0] * self.vertices
        self.stars_by_class = [0] * self.vertices
        for e, ((u, v), names) in enumerate(zip(self.edges, self.bundles, strict=True)):
            assert all((b in self.fixed) == (names[0] in self.fixed) for b in names)
            for b in names:
                self.of[b] = e
            self.neighbors[u] |= 1 << v
            self.neighbors[v] |= 1 << u
            self.stars_by_class[u] |= 1 << e
            self.stars_by_class[v] |= 1 << e
        self.free_edges = tuple(e for e, names in enumerate(self.bundles) if names[0] not in self.fixed)
        self.fixed_edges = tuple(e for e, names in enumerate(self.bundles) if names[0] in self.fixed)
        self.universe = (1 << self.vertices) - 1
        self.basis = None
        self.triads = None
        if self.live and not connected(self.universe, self.neighbors):
            raise ValueError("wired incidence is disconnected")

    def upper(self):
        """A whole bond or one mark per bundle plus one more determines its support."""
        upper = 0
        for v, row in enumerate(self.stars):
            if all(b in self.fixed for b in row):
                continue
            if not connected(self.universe ^ (1 << v), self.neighbors):
                return self.width
            upper = max(upper, min(len(row), self.neighbors[v].bit_count() + 1))
        return upper

    def equation_colours(self):
        """Two names may be transposed iff holders coincide or their pair is a cut."""
        adjacent = [[] for _ in range(self.vertices)]
        for e, (u, v) in enumerate(self.edges):
            adjacent[u].append((v, e))
            adjacent[v].append((u, e))
        parents, order = {0: (-1, -1)}, [0]
        for u in order:
            for v, e in adjacent[u]:
                if v not in parents:
                    parents[v] = (u, e)
                    order.append(v)
        tree = {e for _, e in parents.values()}
        branch = [0] * self.vertices
        colours = [None] * len(self.edges)
        for e, (u, v) in enumerate(self.edges):
            if e not in tree:
                chord = 1 << e
                branch[u] ^= chord
                branch[v] ^= chord
                colours[e] = ("cycle", chord)
        for v in reversed(order[1:]):
            u, e = parents[v]
            colours[e] = ("cycle", branch[v])
            branch[u] ^= branch[v]
        return [colours[e] if len(self.bundles[e]) == 1 else ("holders", e) for e in self.of]

    def carries(self, image):
        if self.basis is None:
            self.basis = Basis(sum(1 << b for b in row) for row in self.stars)
        return all(not self.basis.reduce(sum(1 << image[b] for b in row)) for row in self.stars)

    def ternary_discriminator(self, image):
        """A ternary bond whose image fails even to be an equation."""
        if self.triads is None:
            self.triads = [row for v, row in enumerate(self.stars)
                           if len(row) == 3 and connected(self.universe ^ (1 << v), self.neighbors)]
        for row in self.triads:
            if self.basis.reduce(sum(1 << image[b] for b in row)):
                return [row, sorted(image[b] for b in row)]
        return None


def bad_swap(stage, equation, colour):
    reps = {}
    for x in stage.free:
        a = reps.setdefault(colour(x), x)
        if equation[a] != equation[x]:
            return [[a, x], [x, a]]
    return None


class BondIndex:
    """Whole connected-cut enumeration for small wired incidence graphs."""

    def __init__(self, stage):
        hold = stage.stars_by_class
        weights = [len(bundle) for bundle in stage.bundles]
        heavy = sum(1 << e for e, w in enumerate(weights) if w > 1)
        shore = cut = 0
        bonds = []
        for step in range(1, 1 << (stage.vertices - 1)):
            changed = step & -step
            shore ^= changed
            cut ^= hold[changed.bit_length() - 1]
            if not connected(shore, stage.neighbors) or not connected(stage.universe ^ shore, stage.neighbors):
                continue
            bonds.append((cut.bit_count() + sum(weights[e] - 1 for e in indices(cut & heavy)), cut))
        bonds.sort()
        self.costs = [cost for cost, _ in bonds]
        self.words = [word for _, word in bonds]
        occurrences = [bytearray((len(bonds) + 7) // 8) for _ in weights]
        for i, word in enumerate(self.words):
            for e in indices(word):
                occurrences[e][i >> 3] |= 1 << (i & 7)
        self.columns = [int.from_bytes(raw, "little") for raw in occurrences]
        self.cap = {cost: (1 << bisect_right(self.costs, cost)) - 1 for cost in set(self.costs)}

    def minimum(self, mask):
        return self.costs[(mask & -mask).bit_length() - 1] if mask else -1

    def upper(self, stage):
        """Use the span of bonds recognized from singleton and pair minima."""
        fixed = sum(1 << e for e in stage.fixed_edges)
        basis = Basis(row for row in stage.stars_by_class[:-1] if row & fixed == row)
        least_bonds = 0
        for col in self.columns:
            k = self.minimum(col)
            assert k > 0
            best = col & self.cap[k]
            least_bonds |= best
            if best.bit_count() == 1:
                basis.add(self.words[best.bit_length() - 1])
        if len(basis.rows) == stage.outside:
            return 2
        for b in indices(least_bonds):
            basis.add(self.words[b])
        if len(basis.rows) == stage.outside:
            return 3
        for a, b in combinations(self.columns, 2):
            common = a & b
            if common:
                best = common & self.cap[self.minimum(common)]
                if best.bit_count() == 1:
                    basis.add(self.words[best.bit_length() - 1])
        if len(basis.rows) == stage.outside:
            return 3
        return stage.width


def native(stage, binary, mode, limit):
    query = stage.free_edges
    fields = [stage.vertices, len(stage.edges), len(query)]
    for (u, v), names in zip(stage.edges, stage.bundles, strict=True):
        fields.extend((u, v, len(names)))
    fields.extend(query)
    result = subprocess.run([binary, mode], input=" ".join(map(str, fields)), text=True,
                            capture_output=True, timeout=limit, check=True)
    values = list(map(int, result.stdout.split()))
    if mode == "unary":
        assert len(values) == len(query)
        return dict(zip(query, values, strict=True))
    size = len(stage.edges)
    assert len(values) == len(query) * size
    return {e: values[i*size:(i+1)*size] for i, e in enumerate(query)}


class WorkLimit(Exception):
    pass


class Budget:
    def __init__(self, count):
        self.remaining = self.initial = count

    def step(self):
        self.remaining -= 1
        if self.remaining < 0:
            raise WorkLimit


class Group:
    """Exact pair automorphisms from an invariant refinement and MRV search."""

    def __init__(self, colors, table, budget):
        self.table = table
        self.budget = budget
        self.n = len(table)
        self.all = (1 << self.n) - 1

        def classify(descriptions):
            palette = {}
            return [palette.setdefault(value, len(palette)) for value in descriptions]

        colors = classify(colors)
        while len(set(colors)) < self.n:
            refined = classify((colors[u], tuple(sorted((colors[v], table[u][v])
                                                        for v in range(self.n) if v != u))) for u in range(self.n))
            if colors == refined:
                break
            colors = refined
        masks = defaultdict(int)
        for i, c in enumerate(colors):
            masks[c] |= 1 << i
        self.domains = tuple(masks[c] for c in colors)
        self.cells = len(masks)

    def solutions(self, image, free, unused, equation=None):
        self.budget.step()
        if not free:
            yield tuple(image)
            return
        bound = self.all ^ free
        best = self.n + 1
        for u in indices(free):
            allowed = 0
            for v in indices(self.domains[u] & unused):
                for a in indices(bound):
                    b = image[a]
                    if self.table[u][a] != self.table[v][b]:
                        break
                    if equation is not None and (equation[u] == equation[a] or equation[v] == equation[b]):
                        if (u < a) != (v < b):
                            break
                else:
                    allowed |= 1 << v
            size = allowed.bit_count()
            if size == 0:
                return
            if size < best:
                choice, possible, best = u, allowed, size
        for v in indices(possible):
            image[choice] = v
            yield from self.solutions(image, free ^ (1 << choice), unused ^ (1 << v), equation)

    def generators(self):
        # For every stabilizer, one representative of each possible image.
        identity = list(range(self.n))
        for a in range(self.n):
            free = self.all ^ ((1 << (a + 1)) - 1)
            for b in indices(self.domains[a] & free):
                if any(self.table[a][v] != self.table[b][v] for v in range(a)):
                    continue
                image = identity.copy()
                image[a] = b
                each = self.solutions(image, free, (free ^ (1 << b)) | (1 << a))
                if mapped := next(each, None):
                    yield mapped


def pair_group(stage, unary, table, equation, budget):
    """Pool actual table twins rather than assuming the holder classes are visible."""
    blocks = []
    profiles = {x: (unary[x], tuple(table[x][f] for f in stage.fixed_edges)) for x in stage.free_edges}

    def twins(x, y):
        return (profiles[x] == profiles[y]
                and (len(stage.bundles[x]) == 1 or table[x][y] == unary[x])
                and (len(stage.bundles[y]) == 1 or table[x][y] == unary[y])
                and all(table[x][z] == table[y][z] for z in stage.free_edges if z not in (x, y)))

    for x in stage.free_edges:
        for block in blocks:
            y = block[0]
            if twins(x, y):
                a, b = stage.bundles[x][0], stage.bundles[y][0]
                if equation[a] != equation[b]:
                    return [[a,b],[b,a]], {"pair_twin_swap": True}
                block.append(x)
                break
        else:
            blocks.append([x])
    groups = [sorted(b for e in block for b in stage.bundles[e]) for block in blocks]
    colors = [(profiles[block[0]], len(group), table[stage.of[group[0]]][stage.of[group[1]]] if len(group)>1 else -2)
              for block, group in zip(blocks, groups, strict=True)]
    matrix = [[table[a[0]][b[0]] for b in blocks] for a in blocks]
    search = Group(colors, matrix, budget)
    diagnostics = {"pair_twin_classes":len(blocks),"pair_refinement_classes":search.cells,"pair_generators":0}
    for permutation in search.generators():
        diagnostics["pair_generators"] += 1
        image = list(range(stage.width))
        for x, y in enumerate(permutation):
            for a, b in zip(groups[x], groups[y], strict=True):
                image[a] = b
        if not stage.carries(image):
            return moved(image), diagnostics
    return None, diagnostics


def moved(image):
    return [[a,b] for a,b in enumerate(image) if a != b]


def empty_intersection(masks, limit, budget):
    """Least number of columns whose intersection is empty, within limit."""
    candidates = []
    for x in sorted(set(masks), key=int.bit_count):
        if not any(y & x == y for y in candidates):
            candidates.append(x)
    suffix = [None] * (len(candidates) + 1)
    for i in range(len(candidates)-1, -1, -1):
        old = suffix[i+1]
        suffix[i] = candidates[i] if old is None else old & candidates[i]

    def cover(index, remaining, common):
        budget.step()
        if common == 0:
            return True
        if not remaining or index == len(candidates):
            return False
        if common is not None and common & suffix[index]:
            return False
        for j in range(index, len(candidates)):
            other = candidates[j] if common is None else candidates[j] & common
            if other != common and cover(j+1, remaining-1, other):
                return True
        return False

    return next((k for k in range(3,limit+1) if cover(0,k,None)), None)


def distinguishing_order(stage, index, image, upper, budget):
    """Minimize the first changed reading by intersecting eligible bond columns."""
    # If a reading decreases, some reading on the same permutation orbit
    # increases. For each source bond, seek marks whose image has no witness
    # of at most that bond's size. One mark per image bundle is enough.
    mapping = [sum(1 << e for e in {stage.of[image[b]] for b in bundle}) for bundle in stage.bundles]
    image_support = {0:0}
    best = upper
    for weight, word in zip(index.costs,index.words,strict=True):
        budget.step()
        small = word & -word
        remaining = word ^ small
        if remaining not in image_support:
            # The shorter word need not be a bond, so use its literal union.
            union = 0
            for e in indices(remaining):
                union |= mapping[e]
            image_support[remaining] = union
        targets = image_support[remaining] | mapping[small.bit_length()-1]
        image_support[word] = targets
        if targets.bit_count() < 3:
            continue
        allowed = index.cap[weight]
        candidate = [index.columns[e] & allowed for e in indices(targets)]
        common = allowed
        for col in candidate:
            common &= col
            if not common:
                break
        if common:
            continue
        new = empty_intersection(candidate,min(best-1,len(candidate)),budget)
        if new is not None:
            best = new
            if best == 3:
                break
    return best


def _read(stars, terminal, thorough):
    if terminal:
        return {"lo":0,"hi":0,"method":"terminal"}
    stage = Stage(stars)
    if not stage.live:
        return {"lo":0,"hi":0,"method":"closed"}
    extra = {"junctions":stage.outside,"distinctions":stage.width,"free_distinctions":len(stage.free),
             "holder_classes":len(stage.edges),"free_holder_classes":len(stage.free_edges)}

    def result(lo, hi, method):
        assert 0 <= lo <= hi <= stage.width
        return {"lo":lo,"hi":hi,"method":method,**extra}

    equation = stage.equation_colours()
    lower = bad_swap(stage,equation,lambda b: 0)
    if lower is None:
        return result(0,0,"pointwise end")
    extra["lower_witness"] = lower
    extra["witness_preserves_through"] = 0
    upper = stage.upper()
    if upper == 1:
        return result(1,1,"support bound")

    binary = os.environ.get("BOND_ORDER_READER_ENGINE")
    index = None
    if not binary and stage.vertices <= (19 if thorough else 16):
        index = BondIndex(stage)
    if index is not None:
        unary = {e:index.minimum(index.columns[e]) for e in stage.free_edges}
    elif binary and stage.vertices <= (128 if thorough else 60):
        try:
            unary = native(stage,binary,"unary",20 if thorough else 5)
        except subprocess.TimeoutExpired:
            return result(1,upper,"singleton time limit")
    else:
        return result(1,upper,"singleton size limit")
    extra["singleton_classes"] = len(set(unary.values()))
    lower = bad_swap(stage,equation,lambda b: unary[stage.of[b]])
    if lower is None:
        return result(1,1,"singleton minima")
    extra["lower_witness"] = lower
    extra["witness_preserves_through"] = 1
    if upper == 2:
        return result(2,2,"support bound")

    if index is not None:
        table = {e:[index.minimum(index.columns[e] & c) for c in index.columns] for e in stage.free_edges}
    elif binary and stage.vertices <= (128 if thorough else 43) and len(stage.edges) <= (220 if thorough else 110):
        try:
            table = native(stage,binary,"pairs",30 if thorough else 5)
        except subprocess.TimeoutExpired:
            return result(2,upper,"pair time limit")
    else:
        return result(2,upper,"pair size limit")
    extra["exact_pair_rows"] = len(table)
    if index is not None:
        upper=min(upper,index.upper(stage))
        if upper==2:
            return result(2,2,"shortest singleton bonds")
    budget = Budget(450_000 if thorough else 40_000)
    try:
        lower, diagnostics = pair_group(stage,unary,table,equation,budget)
    except WorkLimit:
        return result(2,upper,"pair group work limit")
    extra.update(diagnostics)
    if lower is None:
        return result(2,2,"full pair table")
    extra["lower_witness"] = lower
    extra["witness_preserves_through"] = 2
    if upper == 3:
        return result(3,3,"pair witness and support bound")

    if index is None and stage.vertices <= (19 if thorough else 16):
        index=BondIndex(stage)
    if index is None and not thorough:
        return result(3,upper,"higher reading size limit")
    if index is not None:
        extra["bonds_enumerated"] = len(index.words)
        upper=min(upper,index.upper(stage))
        assert upper >= 3
    if upper == 3:
        return result(3,3,"pair witness and short bond span")
    if len(stage.free) > (100 if thorough else 30):
        return result(3,upper,"higher group size limit")
    free = stage.free
    colors = [(unary[stage.of[b]], tuple(table[stage.of[b]][e] for e in stage.fixed_edges)) for b in free]
    matrix = [[table[stage.of[a]][stage.of[b]] for b in free] for a in free]
    search = Group(colors,matrix,budget)
    best=3
    extra["higher_pair_representatives"]=0
    extra["triple_discriminators"] = []
    unknown = 0
    try:
        # Code-preserving transpositions preserve every reading. The least
        # pair map in each double coset is increasing within each swap class
        # in both directions, so each coset still has a representative here.
        for p in search.solutions(list(range(len(free))),search.all,search.all,[equation[b] for b in free]):
            extra["higher_pair_representatives"] += 1
            image = list(range(stage.width))
            for a, b in enumerate(p):
                image[free[a]] = free[b]
            if stage.carries(image):
                continue
            if triple := stage.ternary_discriminator(image):
                extra["triple_discriminators"].append({"map": moved(image), "marks": triple})
                continue
            if index is None:
                unknown += 1
                continue
            first = distinguishing_order(stage,index,image,upper,budget)
            if first > best:
                best = first
                extra["lower_witness"] = moved(image)
                extra["witness_preserves_through"] = best - 1
            if best == upper:
                break
    except WorkLimit:
        return result(best,upper,"higher group work limit")
    if unknown:
        extra["ungraded_pair_representatives"] = unknown
        return result(best,upper,"no ternary support witness for some pair maps")
    if index is None:
        return result(3,3,"full pair group separated by ternary supports")
    return result(best,best,"complete higher comparison")


def read_order(stars, *, terminal=False):
    return _read(stars, terminal, False)


def refine_order(stars, *, terminal=False):
    """Use up to 128 wired vertices for selected exact pair comparisons."""
    return _read(stars, terminal, True)


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", type=Path)
    parser.add_argument("--refine", action="store_true")
    parser.add_argument("--shape-index", type=Path)
    parser.add_argument("--shapes", type=int, nargs="+")
    args = parser.parse_args()
    if args.prepare:
        print(prepare_native(args.prepare))
    elif args.shape_index:
        if not args.shapes or not args.refine:
            parser.error("an index replay requires --refine and explicit --shapes")
        index = json.loads(args.shape_index.read_text())
        by_id = {row["shape"]: row for row in index["shapes"]}
        ids = sorted(set(args.shapes))
        records = []
        for identifier in ids:
            shape = by_id[identifier]
            answer = refine_order(shape["stars"], terminal=not shape["can_grow"])
            records.append({"shape": identifier, "observations": len(shape["observations"]), **answer})
        print(json.dumps({"shape_index": args.shape_index.name, "shapes": ids, "records": records},
                         sort_keys=True, indent=2))
    else:
        source=json.load(sys.stdin)
        run = refine_order if args.refine else read_order
        print(json.dumps(run(source["stars"], terminal=source.get("terminal",False)),sort_keys=True))
