"""Compare whole observations wholly at a minimum current separation from the donor."""
from collections import Counter, defaultdict
from itertools import zip_longest
import json
import signal
import networkx as nx
from current import DATA, cases, distances, loads, stages


class Budget(Exception):
    pass


def expire(*args):
    raise Budget()


class View:
    def __init__(self, stage, selected, roots, values, *, open_cuts=False, report_loose=False):
        self.ids = {v: stage.ids[v] for v in selected}
        self.loose = {v: [] for v in selected}
        self.links = defaultdict(list)
        for m, actual_holders in stage.ends.items():
            holders = tuple(v for v in actual_holders if v in selected)
            if not holders or (not open_cuts and len(holders)!=len(actual_holders)):
                continue
            label = (m in roots, values and m in stage.occupied, report_loose and len(actual_holders)==1)
            if len(holders)==1:
                self.loose[holders[0]].append(label)
            else:
                self.links[tuple(holders)].append(label)
        self.graph = nx.Graph()
        self.graph.add_nodes_from((v,{"port":tuple(sorted(labels))}) for v,labels in self.loose.items())
        self.graph.add_edges_from((p,q,{"mark":tuple(sorted(labels))}) for (p,q),labels in self.links.items())
        self.size = (len(selected), sum(len(group) for group in self.loose.values())+sum(len(group) for group in self.links.values()))

    def candidate(self):
        knots = {self.ids[v]: row["port"] for v,row in self.graph.nodes(data=True)}
        links = {tuple(sorted((self.ids[p],self.ids[q]))): row["mark"] for p,q,row in self.graph.edges(data=True)}
        return knots, links


def compare(x,y):
    if x.size != y.size:
        return "different sizes"
    if x.candidate()==y.candidate():
        return "checked correspondence"
    nodes = lambda g: Counter((d["port"],g.degree(v)) for v,d in g.nodes(data=True))
    if nodes(x.graph)!=nodes(y.graph):
        return "different port and neighbor counts"
    nm=nx.isomorphism.categorical_node_match("port",())
    em=nx.isomorphism.categorical_edge_match("mark",())
    matcher=nx.algorithms.isomorphism.GraphMatcher(x.graph,y.graph,node_match=nm,edge_match=em)
    signal.setitimer(signal.ITIMER_REAL,1.5)
    try:
        same=matcher.is_isomorphic()
    except (Budget, RecursionError):
        return "unresolved after exact-search limit"
    finally:
        signal.setitimer(signal.ITIMER_REAL,0)
    if not same:
        return "exact nonisomorphism"
    p=matcher.mapping
    assert set(p)==set(x.graph) and set(p.values())==set(y.graph)
    assert all(x.graph.nodes[v]==y.graph.nodes[p[v]] for v in x.graph)
    assert all(y.graph.has_edge(p[v],p[w]) and data==y.graph[p[v]][p[w]] for v,w,data in x.graph.edges(data=True))
    return "checked isomorphism"


def frame_data(stage, seam):
    ds=distances(stage.neighbors,[seam])
    assert len(ds)==len(stage.stars)
    return ds


def run(tag,through):
    source=cases()[tag]
    s,=source["roles"]["seams"]
    N=len(source["roles"]["anchors"])
    interner={}
    arms=[stages(source,state,through,interner) for state in loads(source).values()]
    rows=[]
    for q,l in zip(*arms):
        ds=[frame_data(g,s) for g in (q,l)]
        for d in range(max(s,N-s)):
            exterior=[{v for v,h in values.items() if h>=d} for values in ds]
            for side,m in (("right",s+d),("left",s-1-d)):
                if not 0<=m<N:
                    continue
                for region in ("all","root_component"):
                    chosen=[]
                    for graph,available in zip((q,l),exterior):
                        if region=="all":
                            chosen.append(available)
                        else:
                            reached={m}
                            waiting=[m]
                            while waiting:
                                cur=waiting.pop()
                                nxt=(graph.neighbors[cur]&available)-reached
                                reached.update(nxt); waiting.extend(nxt)
                            chosen.append(reached)
                    for colors in (False,True):
                        if colors and q.age>0:
                            continue
                        views=[View(g,selected,{m},colors) for g,selected in zip((q,l),chosen)]
                        result=compare(*views)
                        rows.append({"age":q.age,"offset":d,"side":side,"root":m,"domain":region,
                                     "actual_values":colors,"quiet":views[0].size,"loaded":views[1].size,
                                     "comparison":result})
    return rows


def main():
    signal.signal(signal.SIGALRM,expire)
    data={"definition":"all induced incidence vertices at least 2d current hops from old attachment; preserve root, hide outside boundary, no occupancy in primary","cases":{}}
    for case in ("J1","P8"):
        data["cases"][case]=run(case,6)
        print(case,Counter(row["comparison"] for row in data["cases"][case]),flush=True)
    (DATA/"current_exterior.json").write_text(json.dumps(data,separators=(",",":"))+"\n")


if __name__=="__main__":
    main()
