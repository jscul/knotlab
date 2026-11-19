"""Certify the least marked reading or an interval without enumerating graph bonds."""
from collections import Counter, defaultdict
from ctypes import CDLL, POINTER, c_int, c_ubyte, c_uint32
from functools import cache
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import fcntl
import os
import re
import subprocess
import tempfile

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BLISS_ROOT = ROOT / ('experiments/LUBIW-NATURAL-CERTIFIED-SEARCH-001A1/'
                     'LUBIW-NATURAL-CERTIFIED-SEARCH-001A1-E001_maintained_symbolic_controls/'
                     'vendor/extracted/usr')


def bit_indices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def insert(basis, word):
    while word:
        j = word.bit_length() - 1
        if j not in basis:
            basis[j] = word
            return
        word ^= basis[j]


class Stage:
    def __init__(self, stars):
        owned = defaultdict(list)
        raw = [tuple(row) for row in getattr(stars, 'stars', stars)]
        for j, row in enumerate(raw):
            if not row or len(set(row)) != len(row):
                raise ValueError('Expected nonempty ordinary supports with distinct names')
            for x in row:
                owned[x].append(j)
        if not owned or any(len(pair) > 2 for pair in owned.values()):
            raise ValueError('Each distinction must have one or two ordinary holders')
        self.names = sorted(owned)
        position = {x:i for i,x in enumerate(self.names)}
        self.stars = [sum(1 << position[x] for x in row) for row in raw]
        self.loose = Counter(holders[0] for holders in owned.values() if len(holders)==1)
        outside = len(raw)
        self.vertices = outside + bool(self.loose)
        self.ends = []
        bags = defaultdict(list)
        for i,x in enumerate(self.names):
            holders = owned[x]
            edge = tuple(holders) if len(holders)==2 else (holders[0],outside)
            self.ends.append(edge)
            bags[edge].append(i)
        self.links = list(bags)
        self.bags = list(bags.values())
        self.bag_masks = [sum(1 << i for i in bag) for bag in self.bags]
        self.fixed = [j for j,(a,b) in enumerate(self.links) if a in self.loose or b in self.loose]
        self.free = sorted(set(range(len(self.links))) - set(self.fixed))
        self.graph = nx.Graph()
        self.graph.add_nodes_from(range(self.vertices))
        self.graph.add_edges_from(self.links)
        if not nx.is_connected(self.graph):
            raise ValueError('Expected a connected wired holder graph')
        self.basis = {}
        for word in self.stars:
            insert(self.basis,word)
        # Normal forms of single coordinates modulo the true row space.
        self.syndromes = []
        for j in range(len(self.names)):
            if j not in self.basis:
                self.syndromes.append(1 << j)
                continue
            rest = self.basis[j] ^ (1 << j)
            value = 0
            for i in bit_indices(rest):
                value ^= self.syndromes[i]
            self.syndromes.append(value)

    def permits_transpositions(self, names):
        return self.unsafe_swap(names) is None

    def unsafe_swap(self, names):
        if names:
            i = names[0]
            for j in names[1:]:
                if self.ends[i] != self.ends[j] and self.syndromes[i] != self.syndromes[j]:
                    return [self.names[i],self.names[j]]
        return None

    def carries_blocks(self, blocks, changes):
        errors = [0]*self.vertices
        for u,v in changes:
            if u == v:
                continue
            for i,j in zip(blocks[u],blocks[v],strict=True):
                difference = self.syndromes[i] ^ self.syndromes[j]
                a,b = self.ends[i]
                errors[a] ^= difference
                errors[b] ^= difference
        return not any(errors)

    def can_grow(self):
        if not self.loose:
            return False
        live = set(self.loose)
        common = {frozenset(live.intersection(self.graph.neighbors(u))) for u in range(len(self.stars))}
        candidates = {pair for members in common for pair in combinations(sorted(members),2)}
        graph = nx.Graph()
        graph.add_edges_from(candidates)
        valid = [clique for clique in nx.find_cliques(graph) if len(clique)>=3
                 and not any(set(clique)<=witness for witness in common)]
        covered = {pair for group in valid for pair in combinations(sorted(group),2)}
        demand = Counter(x for group in valid for x in group)
        demand.update(x for pair in candidates-covered for x in pair)
        return all(demand[x] <= self.loose[x] for x in live)


@cache
def flow_library():
    source = HERE / 'scale_reader.cpp'
    digest = sha256(source.read_bytes()).hexdigest()[:24]
    build = Path(tempfile.gettempdir()) / f'prespatial-mincuts-{os.getuid()}'
    build.mkdir(mode=0o700,exist_ok=True)
    if build.is_symlink() or build.stat().st_uid!=os.getuid() or build.stat().st_mode & 0o077:
        raise RuntimeError('Expected a private per-user kernel cache')
    binary = build / (digest+'.so')
    with (build/'compile.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        if not binary.exists():
            pending = binary.with_suffix('.building')
            subprocess.run(['g++','-O3','-std=c++17','-fPIC','-shared',str(source),'-o',str(pending)],
                           check=True)
            os.replace(pending,binary)
    handle = CDLL(str(binary))
    handle.marked_minimum_rows.argtypes = [c_int,c_int,POINTER(c_int),POINTER(c_uint32),POINTER(c_ubyte)]
    handle.marked_minimum_rows.restype = c_int
    return handle


def minimum_rows(stage):
    """Return exact K(singleton), and one bitmap of directed pair bits per holder pair."""
    m = len(stage.links)
    data = [x for (a,b),bag in zip(stage.links,stage.bags) for x in (a,b,len(bag))]
    sizes = (c_uint32*m)()
    stride = (m+7)//8
    raw = (c_ubyte*(m*stride))()
    status = flow_library().marked_minimum_rows(stage.vertices,m,(c_int*len(data))(*data),sizes,raw)
    if status:
        raise ValueError('Invalid network or capacity outside the compiled integer range')
    payload = bytes(raw)
    rows = [int.from_bytes(payload[j*stride:(j+1)*stride], 'little') for j in range(m)]
    if any(not (row >> j & 1) for j,row in enumerate(rows)):
        raise AssertionError('Each distinction must belong to an attained singleton minimum')
    return list(sizes),rows


def unique_basis(stage, costs, rows):
    basis = {}
    for j in stage.loose:
        insert(basis,stage.stars[j])
    rank_live = len(basis)
    unique = set()
    for price,row in zip(costs,rows):
        if row in unique:
            continue
        if sum(len(stage.bags[j]) for j in bit_indices(row)) == price:
            unique.add(row)
            literal = 0
            for j in bit_indices(row):
                literal |= stage.bag_masks[j]
            insert(basis,literal)
    return basis,rank_live,len(unique)


def focus_upper(stage,basis):
    if len(basis)==len(stage.basis):
        return 2
    cuts = set(nx.articulation_points(stage.graph))
    costs = []
    for i,row in enumerate(stage.stars):
        if i in stage.loose:
            continue
        bound = row.bit_count()
        if i not in cuts:
            bound = min(bound,stage.graph.degree[i]+1)
        costs.append((bound,row))
    result = 2
    for required,row in sorted(costs):
        old = len(basis)
        insert(basis,row)
        if len(basis)>old:
            result = max(result,required)
        if len(basis)==len(stage.basis):
            return result
    raise AssertionError('Ordinary star rows did not regenerate their own span')


def compact_colors(signatures):
    numbers = {}
    return [numbers.setdefault(sig,len(numbers)) for sig in signatures]


def color_cells(colors):
    cells = defaultdict(list)
    for i,c in enumerate(colors):
        cells[c].append(i)
    return list(cells.values())


def fingerprint_partition(stage,costs,rows):
    """Compress observable equal rows/columns, then refine the directed relation."""
    columns = [0]*len(rows)
    for i,row in enumerate(rows):
        for j in bit_indices(row):
            columns[j] |= 1 << i
    twins = defaultdict(list)
    for i in stage.free:
        twins[costs[i],rows[i],columns[i]].append(i)
    groups = list(twins.values())
    representatives = [g[0] for g in groups]
    blocks = [sorted(x for i in g for x in stage.bags[i]) for g in groups]
    def project(row):
        return sum(1 << j for j,i in enumerate(representatives) if row >> i & 1)
    adjacency = [project(rows[i]) for i in representatives]
    incoming = [project(columns[i]) for i in representatives]
    fixed = sum(1 << j for j in stage.fixed)
    colors = compact_colors((costs[i],len(b),rows[i]&fixed,columns[i]&fixed)
                            for i,b in zip(representatives,blocks))
    rounds = 0
    while True:
        cells = color_cells(colors)
        if len(cells)==len(blocks):
            break
        masks = [sum(1 << j for j in cell) for cell in cells]
        signatures = [None]*len(blocks)
        for cell in cells:
            if len(cell)==1:
                i = cell[0]
                signatures[i] = (colors[i],)
                continue
            for i in cell:
                a,b = adjacency[i],incoming[i]
                signatures[i] = (colors[i],tuple(((a&m).bit_count(),(b&m).bit_count(),(a&b&m).bit_count())
                                                 for m in masks))
        refined = compact_colors(signatures)
        rounds += 1
        if len(set(refined))==len(cells):
            break
        colors = refined
    return blocks,adjacency,colors,rounds


def protected_rows(stage,blocks,cells,basis):
    """A row is common if every free cell it partially intersects has a constant syndrome."""
    variable = []
    for cell in cells:
        names = [j for u in cell for j in blocks[u]]
        if any(stage.syndromes[j] != stage.syndromes[names[0]] for j in names[1:]):
            variable.append(sum(1 << j for j in names))
    for row in stage.stars:
        if all((row & names) in (0,names) for names in variable):
            insert(basis,row)


def bliss_certificate(stage,blocks,adjacency,colors,timeout):
    """Optional exact feature-group generators after the polynomial certificate stalls."""
    executable = BLISS_ROOT/'bin/bliss'
    if not executable.is_file():
        return False,'unavailable',0
    active = [i for cell in color_cells(colors) if len(cell)>1 for i in cell]
    which = {u:i+1 for i,u in enumerate(active)}
    edges = [(which[u],which[v]) for u in active for v in bit_indices(adjacency[u])
             if v in which and v != u]
    lines = [f'p edge {len(active)} {len(edges)}']
    lines.extend(f'n {which[u]} {colors[u]+1}' for u in active)
    lines.extend(f'e {a} {b}' for a,b in edges)
    env = dict(os.environ,LD_LIBRARY_PATH=str(BLISS_ROOT/'lib/x86_64-linux-gnu'))
    try:
        process = subprocess.run([str(executable),'-directed','-v=1'],
                                 input='\n'.join(lines)+'\n',text=True,capture_output=True,
                                 timeout=timeout,env=env)
    except (OSError,subprocess.TimeoutExpired):
        return False,'unavailable_or_timeout',0
    if process.returncode:
        return False,'runtime_failure',0
    reported = re.search(r'^Generators:\s*(\d+)\s*$',process.stdout,re.M)
    printed = re.findall(r'^Generator:\s*(.*)$',process.stdout,re.M)
    if not reported or int(reported.group(1))!=len(printed) or '|Aut|' not in process.stdout:
        return False,'incomplete_output',0
    safe = True
    for generator in printed:
        if not re.fullmatch(r'(?:\(\d+(?:,\d+)+\))+',generator):
            return False,'unrecognized_generator',0
        mapping = list(range(len(blocks)))
        for cycle in re.findall(r'\(([^)]+)\)',generator):
            ids = [int(x) for x in cycle.split(',')]
            if min(ids)<1 or max(ids)>len(active):
                raise AssertionError('Invalid BLISS point')
            points = [active[i-1] for i in ids]
            for u,v in zip(points,points[1:]+points[:1]):
                mapping[u] = v
        if sorted(mapping)!=list(range(len(blocks))) or any(colors[u]!=colors[v] for u,v in enumerate(mapping)):
            raise AssertionError('Invalid BLISS generator')
        for u,v in enumerate(mapping):
            if sum(1 << mapping[j] for j in bit_indices(adjacency[u]))!=adjacency[v]:
                raise AssertionError('BLISS generator failed the entire directed relation')
        if not stage.carries_blocks(blocks,[(u,v) for u,v in enumerate(mapping) if u!=v]):
            safe = False
    return safe,('all_generators_safe' if safe else 'unsafe_feature_generator'),len(printed)


def scale_order(stars, has_successor=None, *, use_bliss=True, bliss_timeout=5):
    """Return sound inclusive strict-future order bounds. An unknown pair verdict is None."""
    stage = Stage(stars)
    n = len(stage.names)
    free = [x for j in stage.free for x in stage.bags[j]]
    features = dict(junctions=len(stage.stars),distinctions=n,holder_pairs=len(stage.links),
                    movable_names=len(free),rank=len(stage.basis))
    def answer(lo,hi,method):
        return dict(lo=lo,hi=hi,pair_suffices=True if hi<=2 else None,
                    method=method,features=features)
    if has_successor is None:
        has_successor = stage.can_grow()
    if not has_successor:
        return answer(0,0,'no_strict_future')
    if not stage.loose:
        raise ValueError('A closed stage has no strict successor')
    zero_witness = stage.unsafe_swap(free)
    if zero_witness is None:
        return answer(0,0,'fixed_end')
    features['unsafe_zero_swap'] = zero_witness
    prices,rows = minimum_rows(stage)
    singleton = defaultdict(list)
    for j in stage.free:
        singleton[prices[j]].extend(stage.bags[j])
    features['singleton_classes'] = len(singleton)
    one_witness = next((pair for group in singleton.values()
                        if (pair:=stage.unsafe_swap(group)) is not None),None)
    if one_witness is None:
        return answer(1,1,'singleton_classes')
    features['unsafe_singleton_swap'] = one_witness
    basis,live_rank,unique = unique_basis(stage,prices,rows)
    features.update(live_rank=live_rank,unique_minimum_rows=unique,
                    unique_minimum_and_live_rank=len(basis))
    hi = focus_upper(stage,basis.copy())
    features['focus_upper'] = hi
    if hi==2:
        return answer(2,2,'recovered_generators')
    blocks,adjacency,colors,rounds = fingerprint_partition(stage,prices,rows)
    cells = color_cells(colors)
    features.update(movable_twin_blocks=len(blocks),refined_cells=len(cells),
                    largest_cell=max(map(len,cells),default=0),refinement_rounds=rounds)
    protected_rows(stage,blocks,cells,basis)
    hi = min(hi,focus_upper(stage,basis.copy()))
    features.update(protected_rank=len(basis),protected_focus_upper=hi)
    if hi==2:
        return answer(2,2,'protected_rows')
    twin_witness = next((pair for block in blocks if (pair:=stage.unsafe_swap(block)) is not None),None)
    if twin_witness is not None:
        features['unsafe_bit_twin_swap'] = twin_witness
        return answer(2,hi,'unsafe_bit_twins')
    if all(stage.carries_blocks(blocks,[(cell[0],v),(v,cell[0])])
           for cell in cells for v in cell[1:]):
        return answer(2,2,'refined_cells')
    if use_bliss:
        safe,status,generators = bliss_certificate(stage,blocks,adjacency,colors,bliss_timeout)
        features.update(bliss=status,bliss_generators=generators)
        if safe:
            return answer(2,2,'bit_group_generators')
    return answer(2,hi,'uncertified_pair')


def check_kernel(stage):
    """Independent connected-shore enumeration for bounded deterministic controls."""
    edges = [(1 << a,1 << b) for a,b in stage.links]
    neighbors = [sum(1 << v for v in stage.graph.neighbors(u)) for u in range(stage.vertices)]
    full = (1 << stage.vertices) - 1
    def connected(mask):
        seen = pending = mask & -mask
        while pending:
            bit = pending & -pending
            extra = neighbors[bit.bit_length()-1] & mask & ~seen
            seen |= extra
            pending = (pending ^ bit) | extra
        return seen==mask
    spaces = {0}
    widths = [len(bag) for bag in stage.bags]
    exact = [len(stage.names)+1]*len(edges)
    unions = [0]*len(edges)
    for shore in range(1,1 << (stage.vertices-1)):
        cut = [i for i,(a,b) in enumerate(edges) if bool(a&shore)!=bool(b&shore)]
        spaces.add(sum(stage.bag_masks[i] for i in cut))
        if not (connected(shore) and connected(full ^ shore)):
            continue
        weight = sum(widths[i] for i in cut)
        mask = sum(1 << i for i in cut)
        for i in cut:
            if weight<exact[i]:
                exact[i],unions[i] = weight,mask
            elif weight==exact[i]:
                unions[i] |= mask
    assert minimum_rows(stage)==(exact,unions)
    trials = 0
    for i,j in combinations(range(len(stage.names)),2):
        swap = (1 << i) | (1 << j)
        carries = all((row ^ swap) in spaces for row in stage.stars if (row & swap).bit_count()==1)
        assert stage.permits_transpositions([i,j])==carries
        trials += 1
    return trials


def controls():
    import json
    count = entries = swaps = 0
    for n in range(2,6):
        pairs = list(combinations(range(n),2))
        for selected in range(1,1 << len(pairs)):
            graph = nx.Graph()
            graph.add_nodes_from(range(n))
            graph.add_edges_from(pairs[i] for i in bit_indices(selected))
            if not nx.is_connected(graph):
                continue
            for weighted in (False,True):
                stars = [set() for _ in range(n-1)]
                name = 0
                for i in bit_indices(selected):
                    a,b = pairs[i]
                    for _ in range(1+int(weighted and (i+n)%3==0)):
                        stars[a].add(name)
                        if b != n-1:
                            stars[b].add(name)
                        name += 1
                stage = Stage(stars)
                swaps += check_kernel(stage)
                count += 1
                entries += len(stage.links)**2
    directory = ROOT/'artifacts'/'BOND-READING-SCALE-20261119-001'/'BOND-READING-SCALE-20261119-001-E001_size'
    small = json.loads((directory/'lower_native_center_summary_17.json').read_text())
    large = json.loads((directory/'lower_probe_symmetric.json').read_text())
    stages = [small['least_observed']['changes_equations']['unrestricted']['witness_at_min_width']['current'],
              large['witnesses']['least_junctions']['replay']['support_history'][1]]
    outcomes = []
    for rows,insufficient in zip(stages,(2,3)):
        stage = Stage(rows)
        check_kernel(stage)
        result = scale_order(rows)
        assert result['hi']>insufficient and result['lo']==2
        outcomes.append(dict(J=len(rows),n=len(stage.names),lo=result['lo'],hi=result['hi']))
    # A colored four-point relation inside the six columns of a tetrahedron.
    # Its single coupled swap is a vertex symmetry. Freeing the two exchanges separately
    # supplies a genuine non-carrying generator, testing both BLISS outcomes.
    k4 = [set() for _ in range(4)]
    for i,(a,b) in enumerate(combinations(range(4),2)):
        k4[a].add(i)
        k4[b].add(i)
    stage = Stage(k4)
    blocks = [[i] for i in range(6)]
    colors = [0,0,2,3,1,1]
    empty = [1 << i for i in range(6)]
    coupled = empty.copy()
    for u,v in ((0,4),(1,5)):
        coupled[u] |= 1 << v
        coupled[v] |= 1 << u
    yes = bliss_certificate(stage,blocks,coupled,colors,5)
    no = bliss_certificate(stage,blocks,empty,colors,5)
    if (BLISS_ROOT/'bin/bliss').is_file():
        assert yes[0] and not no[0] and no[1]=='unsafe_feature_generator'
    return dict(networks=count,directed_bits=entries,transpositions=swaps,
                archive=outcomes,bliss_control=[yes,no])


if __name__=='__main__':
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true',required=True)
    parser.parse_args()
    print(json.dumps(controls(),sort_keys=True))
