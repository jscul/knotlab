"""First distinguishing radii of anonymous rooted incidence observations."""

from collections import Counter, defaultdict
from dataclasses import dataclass
from hashlib import file_digest
from pathlib import Path
import importlib.util
import json

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
INPUTS = HERE / "inputs.json"
SETUP = json.loads(INPUTS.read_text())
PREDECESSOR = SETUP["same_side"]
SOURCE_PATH = ROOT / "experiments" / PREDECESSOR / f"{PREDECESSOR}-E001_side" / "side_sources.py"
LOADER = importlib.util.spec_from_file_location("front_local_sources", SOURCE_PATH)
sources = importlib.util.module_from_spec(LOADER)
LOADER.loader.exec_module(sources)
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "front_local.json"
CAPS = dict(zip(("junctions", "distinctions"), SETUP["path_caps"], strict=True))
MAX_AGE = 8
MATCH_BUDGET = 30_000
MATCH_VERTEX_CAP = 1_500
INSTRUMENTS = ("induced", "port_degree", "full_degree")


def digest(path):
    with path.open("rb") as stream:
        return file_digest(stream,"sha256").hexdigest()


@dataclass
class Incidence:
    knot_count: int
    neighbors: list
    distinctions: dict
    occupied: set

    @classmethod
    def from_stars(cls, stars, occupied):
        graph = [[] for _ in stars]
        physical = {}
        for knot,support in enumerate(stars):
            for bit in support:
                if bit not in physical:
                    physical[bit] = len(graph)
                    graph.append([])
                other = physical[bit]
                graph[knot].append(other)
                graph[other].append(knot)
        assert all(1 <= len(graph[v]) <= 2 for v in physical.values())
        return cls(len(stars),graph,physical,{physical[x] for x in occupied})

    def root_wave(self, physical):
        roots = {self.distinctions[d] for d in physical}
        distance = [-1] * len(self.neighbors)
        queue = sorted(roots)
        for root in queue:
            distance[root] = 0
        for node in queue:
            for neighbor in self.neighbors[node]:
                if distance[neighbor] == -1:
                    distance[neighbor] = distance[node]+1
                    queue.append(neighbor)
        assert len(queue) == len(self.neighbors)
        return RootWave(self,roots,distance,queue)


@dataclass
class RootWave:
    incidence: Incidence
    roots: set
    distance: list
    order: list

    @property
    def outermost_radius(self):
        return self.distance[self.order[-1]]

    def tally(self, instrument):
        observations = [Counter() for _ in range(self.outermost_radius+1)]
        for v in self.order:
            observations[self.distance[v]][self.node_label(v,instrument)] += 1
        return observations

    def node_label(self, v, instrument):
        distinction = v >= self.incidence.knot_count
        degree = len(self.incidence.neighbors[v]) if instrument=="full_degree" or (
            distinction and instrument=="port_degree") else 0
        return (distinction, v in self.roots, degree)

    def cut(self, radius, instrument):
        nodes = [v for v in self.order if self.distance[v]<=radius]
        inside = set(nodes)
        neighbors = {v:tuple(w for w in self.incidence.neighbors[v] if w in inside) for v in nodes}
        # The layer is inferable inside the ball from the complete unordered root set.
        color = {v:(self.distance[v],self.node_label(v,instrument)) for v in nodes}
        return neighbors,color


def first_counter_delta(left,right):
    for r in range(max(len(left),len(right))):
        a = left[r] if r<len(left) else Counter()
        b = right[r] if r<len(right) else Counter()
        if a!=b:
            return r
    return None


def refine(graphs, colors):
    """Compare exact simultaneous refinement signatures, without hashing."""
    def compact(rows):
        names = {}
        return [{v:names.setdefault(label,len(names)) for v,label in row.items()} for row in rows]
    current = compact(colors)
    while True:
        a,b = (Counter(labels.values()) for labels in current)
        if a!=b:
            return None
        signatures = [{v:(color[v],tuple(sorted(color[w] for w in adjacent))) for v,adjacent in graph.items()}
                      for graph,color in zip(graphs,current,strict=True)]
        more = compact(signatures)
        if len(set(more[0].values()) | set(more[1].values())) == len(a):
            return more
        current = more


def validated(graph_a, graph_b, mapping, labels_a, labels_b):
    return set(mapping)==set(graph_a) and set(mapping.values())==set(graph_b) and all(
        labels_a[v]==labels_b[mapping[v]] and {mapping[x] for x in graph_a[v]}==set(graph_b[mapping[v]])
        for v in graph_a)


class BudgetReached(Exception):
    pass


class LimitedMatcher(nx.algorithms.isomorphism.GraphMatcher):
    def __init__(self, a, b):
        self.checks = 0
        super().__init__(a,b,node_match=lambda x,y:x["color"]==y["color"])

    def syntactic_feasibility(self, left, right):
        self.checks += 1
        if self.checks > MATCH_BUDGET:
            raise BudgetReached
        return super().syntactic_feasibility(left,right)


def equivalent(a, b, radius, instrument, meter, retain_map=False):
    ga,ca = a.cut(radius,instrument)
    gb,cb = b.cut(radius,instrument)
    colors = refine((ga,gb),(ca,cb))
    if colors is None:
        meter["refinement_rejected"] += 1
        return False,None
    groups = []
    for labels in colors:
        by_color = defaultdict(list)
        for node,color in labels.items():
            by_color[color].append(node)
        groups.append(by_color)
    for order in (list,sorted):
        mapping = dict((v,w) for c in groups[0] for v,w in zip(order(groups[0][c]),order(groups[1][c]),strict=True))
        if validated(ga,gb,mapping,ca,cb):
            meter["verified_color_map"] += 1
            return True,mapping if retain_map else None
    if len(ga)>MATCH_VERTEX_CAP:
        meter["vertex_cap"] += 1
        return None,None
    work = []
    for graph,labels in zip((ga,gb),colors,strict=True):
        candidate = nx.Graph(graph)
        nx.set_node_attributes(candidate,labels,"color")
        work.append(candidate)
    matcher = LimitedMatcher(*work)
    try:
        iso = matcher.is_isomorphic()
    except BudgetReached:
        meter["search_cap"] += 1
        return None,None
    meter["explicit_search_accept" if iso else "explicit_search_reject"] += 1
    if not iso:
        return False,None
    assert validated(ga,gb,matcher.mapping,ca,cb)
    return True,matcher.mapping if retain_map else None


def shell_totals(wave):
    counts = [Counter() for _ in range(wave.outermost_radius+1)]
    for v in wave.order:
        counts[wave.distance[v]]["knots" if v<wave.incidence.knot_count else "distinctions"] += 1
    return counts


def first_shell_count(a,b,kind):
    for i in range(max(len(a),len(b))):
        x = a[i][kind] if i<len(a) else 0
        y = b[i][kind] if i<len(b) else 0
        if x!=y:
            return i
    return None


def first_difference(a,b,instrument,meter):
    cap = max(a.outermost_radius,b.outermost_radius)
    different = first_counter_delta(a.tally(instrument),b.tally(instrument))
    equal = -1
    if different is None:
        verdict,_ = equivalent(a,b,cap,instrument,meter)
        if verdict is True:
            return {"equal_through":cap,"first_difference":None,"whole_stage_equal":True}
        if verdict is None:
            return {"equal_through":-1,"first_difference":None,"unresolved_through":cap}
        different = cap
    lower_probe,upper_probe = equal+1,different-1
    while lower_probe<=upper_probe and different>equal+1:
        mid = (lower_probe+upper_probe)//2
        verdict,_ = equivalent(a,b,mid,instrument,meter)
        if verdict is True:
            equal, lower_probe = mid,mid+1
        elif verdict is False:
            different, upper_probe = mid,mid-1
        else:
            # This radius is unknown; retain the best delimiters and certify smaller choices.
            upper_probe = mid-1
    if different == equal+1:
        return {"equal_through":equal,"first_difference":different}
    return {"equal_through":equal,"first_difference":None,"different_by":different}


def colored(structure, first_occupied):
    if first_occupied is None:
        return dict(structure)
    if structure["first_difference"] is not None:
        r = min(first_occupied,structure["first_difference"])
        return {"equal_through":r-1,"first_difference":r}
    if structure["equal_through"] >= first_occupied-1:
        return {"equal_through":first_occupied-1,"first_difference":first_occupied}
    return {"equal_through":structure["equal_through"],"first_difference":None,
            "different_by":min(first_occupied,structure.get("different_by",first_occupied))}


def scoring_roots(spec):
    anchors = spec["roles"]["anchors"]
    seam, = spec["roles"]["seams"]
    groups = [(i,) for i in range(len(anchors))]
    groups.extend((i,i+1) for i in range(len(anchors)-1) if i!=seam-1)
    return [{"marks":group,"physical_roots":[anchors[i] for i in group],
             "side":"left" if group[-1]<seam else "right", "offset":sources.offset(group,seam),
             "common_old_holder_offset":abs(group[1]-seam) if len(group)==2 else None}
            for group in groups]


def full_profile(waves, ring, meter):
    a,b = waves
    assert not a.incidence.occupied
    donor = min(a.distance[v] for v in ring)
    assert donor == min(b.distance[v] for v in ring)
    first_occupied = min((b.distance[v] for v in b.incidence.occupied),default=None)
    results = {kind:first_difference(a,b,kind,meter) for kind in INSTRUMENTS}
    results["actual_values"] = colored(results["induced"],first_occupied)
    s0,s1 = shell_totals(a),shell_totals(b)
    count_deltas = {kind:first_shell_count(s0,s1,kind) for kind in ("knots","distinctions")}
    return {"old_ring_first_hops":donor,"first_visible_occupied_distinction":first_occupied,
            "full_radius":max(a.outermost_radius,b.outermost_radius),"instruments":results,
            "first_count_difference":count_deltas}


def stages(spec, state):
    generator = sources.generate(spec,state,MAX_AGE,caps=CAPS)
    rows = {}
    while True:
        try:
            layer,frame = next(generator)
        except StopIteration as finish:
            stop = {"status":finish.value["status"],"last_layer":max(rows)}
            stop.update({k:v for k,v in finish.value.items() if k.startswith("planned_")})
            return rows,stop
        rows[layer] = frame


def summarize(queries, profiles):
    result = {}
    for idx,query in enumerate(queries):
        label = ",".join(map(str,query["marks"]))
        reading = {"query":query,"first_layer_unrestricted":{},"first_layer_below_ring":{},
                   "earliest_radius_below_ring":{}}
        for kind in (*INSTRUMENTS,"actual_values"):
            records = []
            for age,panel in profiles.items():
                row = panel[idx]
                radius = row["instruments"][kind]["first_difference"]
                if radius is not None:
                    records.append((age,radius,row["old_ring_first_hops"]))
            strict = [(t,r) for t,r,hops in records if r<hops]
            reading["first_layer_unrestricted"][kind] = list(min((t,r) for t,r,_ in records)) if records else None
            reading["first_layer_below_ring"][kind] = list(min(strict)) if strict else None
            reading["earliest_radius_below_ring"][kind] = list(min((r,t) for t,r in strict)) if strict else None
        result[label] = reading
    return result


def witness(waves, radius, instrument, meter):
    a,b = waves
    balls = []
    for wave in waves:
        graph,labels = wave.cut(radius,instrument)
        # Use freshly local labels for the actual disclosure.
        shown = {v:i for i,v in enumerate(graph)}
        balls.append({"node_type_root_full_degree_optional": [labels[v][1] for v in graph],
                      "incidences": [[shown[v],shown[w]] for v,style in graph.items() for w in style if shown[v]<shown[w]]})
    same, mapping = equivalent(a,b,radius-1,instrument,meter,retain_map=True)
    assert radius>0 and same and mapping is not None
    ga,_ = a.cut(radius-1,instrument)
    gb,_ = b.cut(radius-1,instrument)
    a_id,b_id = ({v:i for i,v in enumerate(g)} for g in (ga,gb))
    return {"first_difference_radius":radius,"instrument":instrument,"balls_at_first_difference":balls,
            "verified_mapping_at_previous_radius":[[a_id[v],b_id[mapping[v]]] for v in ga]}


def rename_control(frame, incidence, query, meter):
    top = max(d for star in frame["stars"] for d in star)
    relabeled = Incidence.from_stars([tuple(top-d for d in reversed(star)) for star in reversed(frame["stars"])],
                                    {top-d for d in frame["occupied"]})
    baseline = incidence.root_wave(query)
    transformed = relabeled.root_wave([top-d for d in query])
    assert all(first_counter_delta(baseline.tally(kind),transformed.tally(kind)) is None for kind in INSTRUMENTS)
    for kind in INSTRUMENTS:
        radius = min(9,baseline.outermost_radius)
        assert equivalent(baseline,transformed,radius,kind,meter)[0] is True
    return {"radius":min(9,baseline.outermost_radius),"all_label_instruments_matched":True,
            "occupied_count_preserved":len(relabeled.occupied)==len(incidence.occupied)}


def panel(spec, meter):
    states = sources.loads(spec)
    assert set(states)=={"0","1"}
    (quiet, quiet_stop),(loaded, loaded_stop) = (stages(spec, states[code]) for code in ("0","1"))
    common = sorted(quiet.keys() & loaded.keys())
    queries = scoring_roots(spec)
    ring, = spec["roles"]["rings"]
    result = {}
    witnesses = {}
    rename = None
    for layer in common:
        a,b = (Incidence.from_stars(row[layer]["stars"],row[layer]["occupied"]) for row in (quiet,loaded))
        assert not a.occupied and set(loaded[layer]["occupied"]) == set(states["1"])
        result[layer] = []
        for idx,query in enumerate(queries):
            waves = tuple(inc.root_wave(query["physical_roots"]) for inc in (a,b))
            reading = full_profile(waves,ring,meter)
            assert reading["old_ring_first_hops"] == 2*query["offset"]+1
            assert reading["first_visible_occupied_distinction"] == reading["old_ring_first_hops"]+1
            result[layer].append(reading)
            if spec["id"]=="J1" and query["side"]=="right" and query["offset"] in {2,4} and layer in {1,2,3}:
                shortest = reading["instruments"]["induced"]["first_difference"]
                if shortest is not None and shortest<reading["old_ring_first_hops"]:
                    key = f"{layer}/"+",".join(map(str,query["marks"]))
                    witnesses[key] = witness(waves,shortest,"induced",meter)
            if spec["id"]=="J1" and layer==2 and query["marks"]==(8,9):
                rename = rename_control(loaded[layer],b,query["physical_roots"],meter)
        print(spec["id"],layer,len(queries),len(a.neighbors),len(b.neighbors),dict(meter),flush=True)
    return {"queries":queries,"layers":result,"whole_arm_stops":[quiet_stop,loaded_stop],
            "per_root_summary":summarize(queries,result),"local_map_witnesses":witnesses,"renaming_control":rename}


def main():
    meter = Counter()
    fixtures = sources.cases()
    cases = {tag:panel(fixtures[tag],meter) for tag in SETUP["path_sources"]}
    result = {"source_sha256":digest(Path(__file__)),"inputs_sha256":digest(INPUTS),
              "side_source_sha256":digest(SOURCE_PATH),"nx_version":nx.__version__,"cases":cases,
              "resources":{"physical_caps":CAPS,"layer_limit":MAX_AGE,"matching_vertex_cap":MATCH_VERTEX_CAP,
                           "matcher_candidate_checks":MATCH_BUDGET,"exact_comparison_tally":meter}}
    OUT.write_text(json.dumps(result,separators=(",", ":"))+"\n")
    print(OUT.name,OUT.stat().st_size,dict(meter),flush=True)


if __name__=="__main__":
    main()
