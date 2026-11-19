"""Shared-runner job: the referee's candidate groups and states for MEET-ONCE (after job_meet_tables.py).  One case per bucket of
stages with the same number of distinctions and the same invariant of the table read to distance 8.  Within a bucket:
arrangements deduplicated by exact isomorphism (provenance kept); grouped by exact isomorphism of the tables read to distance 8
(VF2 on the labelled graph of entries at most nine); in each group of two or more, states decided against each state group's
first member, by a junction-graph isomorphism (o a plain vertex) or else by referee_meet.same_states (exact, capped); each test's
kind recorded: a closed stage against an open one of one junction fewer, the same junction graph, or other junction graphs.

  .venv/bin/python -B scripts/longrun.py launch research/MEET-ONCE-20261119-001/referee-R1/job_meet_groups.py \\
      --out runs/referee-meet-once-groups --unit referee-meet-once-groups --workers 6 --case-timeout 3600 --case-mem 2G \\
      --mem-max 16G
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
BUCKETS = defaultdict(list)


def setup(params):                                     # --param src=runs/referee-meet-once-past-tables, one size past
    for line in open(ROOT / params.get("src", "runs/referee-meet-once-tables") / "results.jsonl"):
        r = json.loads(line)["result"]
        BUCKETS[(r["distinctions"], r["invariant"])].append(r)


def cases():
    for i, k in enumerate(sorted(BUCKETS)):
        if len(BUCKETS[k]) >= 2:
            yield f"b{i:04d}", {"stages": BUCKETS[k]}


def run(case_id, p):
    import networkx as nx
    import referee_meet as RM

    def inc(stars):
        G = nx.Graph()
        for j, s in enumerate(stars):
            G.add_node(("j", j), k="j")
            for b in s:
                G.add_node(("b", b), k="b")
                G.add_edge(("j", j), ("b", b))
        return G
    NM = nx.algorithms.isomorphism.categorical_node_match("k", None)
    EM = nx.algorithms.isomorphism.categorical_edge_match("d", None)
    classes = []
    for s in p["stages"]:
        g = inc(s["stars"])
        for c in classes:
            if nx.is_isomorphic(g, c["inc"], node_match=NM):
                c["prov"].append([s["index"], s["round"]])
                break
        else:
            classes.append({"stars": s["stars"], "inc": g, "prov": [[s["index"], s["round"]]], "nb": s["distinctions"],
                            "closed": s["closed"], "t": {(a, b): d for a, b, d in s["table8"]}})
    for c in classes:
        c["lg"] = RM.labelled(c["nb"], c["t"])
    groups = []
    for i, c in enumerate(classes):
        for g in groups:
            if nx.is_isomorphic(classes[g[0]]["lg"], c["lg"], edge_match=EM):
                g.append(i)
                break
        else:
            groups.append([i])
    out = []
    for g in groups:
        if len(g) < 2:
            continue
        sg, tests, undecided = [], [], 0
        for i in g:
            for s in sg:
                a, b = classes[s[0]], classes[i]
                if a["closed"] != b["closed"] and abs(len(a["stars"]) - len(b["stars"])) == 1:
                    kind = "closed and open, one junction fewer"
                elif len(a["stars"]) == len(b["stars"]):
                    kind = "same junction count"
                else:
                    kind = "other"
                if RM.junction_graph_iso(a["stars"], b["stars"]):
                    v, how = True, "junction graphs isomorphic"
                else:
                    v, how = RM.same_states(a["stars"], b["stars"], a["nb"], a["t"], b["t"]), "search"
                tests.append({"kind": kind, "how": how, "same states": v})
                if v is None:
                    undecided += 1
                if v:
                    s.append(i)
                    break
            else:
                sg.append([i])
        out.append({"arrangements": len(g), "distinctions": classes[g[0]]["nb"],
                    "junctions": [len(classes[i]["stars"]) for i in g], "state groups": len(sg), "tests": tests,
                    "undecided": undecided, "provenance": [classes[i]["prov"] for i in g]})
    return {"classes": len(classes), "groups": out}
