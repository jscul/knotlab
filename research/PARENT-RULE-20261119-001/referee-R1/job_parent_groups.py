"""Shared-runner job, second half of the referee's static check of PARENT-RULE-20261119-001 (after job_parent.py's S-* cases):
one case per bucket of arrangements with the same number of distinctions and table invariant.  Within a bucket: exact table
isometry groups (the referee's twin-quotient search); within each group of two or more, state groups by a junction-graph
isomorphism (the outside a plain point) or else the referee's exact states search (GROWN-PAIR-R1's same_states: every table
isometry, twins in order, pruned by span membership); for every pair in different state groups, which of P1, P1 in the backed
stratum, peel depth >= 1 and >= 2 both sides have.

  .venv/bin/python -B scripts/longrun.py launch research/PARENT-RULE-20261119-001/referee-R1/job_parent_groups.py \\
      --out runs/referee-parent-groups --unit referee-parent-groups --workers 6 --case-timeout 3600 --case-mem 2G --mem-max 16G
"""
import itertools
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/VARIABLE-OUTPUT-READER-20261118-001F/referee-R1", "research/CENSUS-READ-20261118-001/referee-R1",
          "research/GROWN-PAIR-20261119-001/referee-R1", "research/MEET-ONCE-20261119-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
BUCKETS = defaultdict(list)
CHUNK = 40


def setup(params):
    for line in open(ROOT / "runs/referee-parent/results.jsonl"):
        r = json.loads(line)
        if r["case"].startswith("S-"):
            for row in r["result"]["rows"]:
                BUCKETS[(row[4], row[3])].append(row)


def cases():
    work = [v for k, v in sorted(BUCKETS.items(), key=lambda kv: str(kv[0])) if len(v) >= 2]
    for a in range(0, len(work), CHUNK):
        yield f"G-{a // CHUNK:04d}", {"buckets": work[a:a + CHUNK]}


def stars_of(gi, ell):
    import networkx as nx
    g = nx.convert_node_labels_to_integers(nx.graph_atlas_g()[gi])
    n = g.number_of_nodes()
    stars = [[] for _ in range(n)]
    b = 0
    for u, v in sorted(tuple(sorted(e)) for e in g.edges()):
        stars[u].append(b)
        stars[v].append(b)
        b += 1
    for j in range(n):
        for _ in range(int(ell[j])):
            stars[j].append(b)
            b += 1
    return stars


def run(case_id, p):
    import referee_census as RC
    import referee_f as F
    import referee_meet as RM
    from job_grown import same_states
    tally = Counter()
    groups_out = []
    for rows in p["buckets"]:
        items = []
        for row in rows:
            S = stars_of(row[1], row[2])
            items.append((row, S, RC.shore_table(S)[0]))
        groups = []
        for i, (_, _, K) in enumerate(items):
            for g in groups:
                if F.isometric(items[g[0]][2], K) is not None:
                    g.append(i)
                    break
            else:
                groups.append([i])
        for g in groups:
            if len(g) < 2:
                continue
            tally["table groups of two or more"] += 1
            sg = []
            for i in g:
                for s in sg:
                    a, b = items[s[0]], items[i]
                    if RM.junction_graph_iso(a[1], b[1]):
                        same = True
                    else:
                        same, _ = same_states(a[1], b[1], a[2], b[2], a[0][4])
                        if same is None:
                            tally["undecided"] += 1
                    if same:
                        s.append(i)
                        break
                else:
                    sg.append([i])
            if len(sg) == 1:
                tally["same states only"] += 1
                continue
            tally["other-states groups"] += 1

            def flags(row):
                return {"P1": row[5] == 0, "P1 backed stratum": row[5] == 0 and row[8] == "b", "depth >= 1": row[9] >= 1,
                        "depth >= 2": row[9] >= 2}
            for x, y in itertools.combinations(range(len(sg)), 2):
                for i in sg[x]:
                    for j in sg[y]:
                        tally["other-states pairs"] += 1
                        fi, fj = flags(items[i][0]), flags(items[j][0])
                        for k in fi:
                            tally[f"both {k}"] += fi[k] and fj[k]
            groups_out.append({"members": [items[i][0][:3] for i in g], "state groups": [[items[i][0][:3] for i in s] for s in sg]})
    return {"tally": dict(tally), "other-states groups": groups_out}
