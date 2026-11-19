"""Shared-runner job, second half of the referee's meet-once rebuild (after job_meetonce.py): one case per bucket of meet-once
grown stages with one table invariant.  Within a bucket: arrangements deduplicated by exact isomorphism (provenance kept); grouped
by exact table isometry (the referee's twin-quotient search on its closed-aware shore tables); within each table group of two or
more arrangements, grouped by states with job_grown.same_states (exact).  meetonce_readout.py tallies the result.

  .venv/bin/python -B scripts/longrun.py launch research/GROWN-PAIR-20261119-001/referee-R1/job_meetonce_groups.py \\
      --out runs/referee-grown-meetonce-groups --unit referee-grown-meetonce-groups --workers 6 --case-timeout 1800 \\
      --case-mem 2G --mem-max 16G
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
for p in ("research/VARIABLE-OUTPUT-READER-20261118-001F/referee-R1", "research/CENSUS-READ-20261118-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
BUCKETS = defaultdict(list)


def setup(params):                                     # --param src=runs/referee-grown-meetonce16 for one size past
    for line in open(ROOT / params.get("src", "runs/referee-grown-meetonce") / "results.jsonl"):
        for s in json.loads(line)["result"]["stages"]:
            BUCKETS[json.dumps(s["inv"])].append(s)


def cases():
    for i, k in enumerate(sorted(BUCKETS)):
        if len(BUCKETS[k]) >= 2:
            yield f"b{i:04d}", {"stages": BUCKETS[k]}


def run(case_id, payload):
    import networkx as nx
    import referee_f as F
    import referee_census as RC
    from job_grown import same_states

    def inc(stars):
        G = nx.Graph()
        for j, s in enumerate(stars):
            G.add_node(("j", j), k="j")
            for b in s:
                G.add_node(("b", b), k="b")
                G.add_edge(("j", j), ("b", b))
        return G
    NM = nx.algorithms.isomorphism.categorical_node_match("k", None)
    classes = []                                       # [stars, n, incidence, provenance]
    for s in payload["stages"]:
        g = inc(s["stars"])
        for c in classes:
            if nx.is_isomorphic(g, c[2], node_match=NM):
                c[3].append([s["index"], s["round"]])
                break
        else:
            classes.append([s["stars"], s["distinctions"], g, [[s["index"], s["round"]]]])
    tabs = [RC.shore_table(c[0])[0] for c in classes]
    groups = []                                        # lists of class numbers with one table
    for i in range(len(classes)):
        for grp in groups:
            if F.isometric(tabs[grp[0]], tabs[i]) is not None:
                grp.append(i)
                break
        else:
            groups.append([i])
    out = []
    for grp in groups:
        if len(grp) < 2:
            continue
        sgroups, undecided = [], 0
        for i in grp:
            for sg in sgroups:
                r, _ = same_states(classes[sg[0]][0], classes[i][0], tabs[sg[0]], tabs[i], classes[i][1])
                if r is None:
                    undecided += 1
                if r:
                    sg.append(i)
                    break
            else:
                sgroups.append([i])
        out.append({"arrangements": len(grp), "distinctions": classes[grp[0]][1],
                    "junctions": [len(classes[i][0]) for i in grp], "state groups": len(sgroups),
                    "state group members": [[grp.index(i) for i in sg] for sg in sgroups],
                    "undecided searches": undecided, "provenance": [classes[i][3][:3] for i in grp],
                    "stars": [classes[i][0] for i in grp]})
    return {"classes": len(classes), "table groups": out}
