"""Independent checks on the census outputs (after the runs; nothing here changes a definition or a verdict rule).

  V1  Every P3 first failing stage and the stage before it, when the stage has at most nine knots: the routine's verdict equals a
      brute-force minor search on the knot-sharing graph (every distinction has at most two holders, so the incidence pattern is a
      subdivision of it).
  V2  Rewiring invariants on 300 funded starts: every distinction has at most two holders; the births of each step keep their number
      of fresh distinctions, and the number of parents of each birth falls short of the original only by the recorded shortfall.
  V3  Replay: one P3 chunk (law parity, arm 2) is regenerated and compared byte for byte with the saved file.

Run from the repo root:  timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file>
"""
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

import networkx as nx

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gates  # noqa: E402
import lib  # noqa: E402


def sharing_graph(stars, n):
    holders = {}
    for k in range(n):
        for d in stars[k]:
            holders.setdefault(d, []).append(k)
    g = nx.Graph()
    g.add_nodes_from(range(n))
    for hs in holders.values():
        assert len(hs) <= 2
        if len(hs) == 2:
            g.add_edge(*hs)
    return g


def v1(report):
    checked = bad = 0
    previous_passes = 0
    draws = {(d["arm"], d["draw"]): d for d in lib.p3_draws()}
    for path in sorted(lib.OUT.glob("p3_*_arm*_*.jsonl")):
        for line in path.open():
            r = json.loads(line)
            if r["kind"] != "history" or r["first_failing_step"] is None:
                continue
            h = lib.grow(draws[(r["arm"], r["draw"])]["stars"], r["law"], 12, 5000, time_limit=60)
            t = r["first_failing_step"]
            for stage in (t, t - 1):
                if stage < 0 or h["n_at"][stage] > 9:
                    continue
                n = h["n_at"][stage]
                routine = not lib.passes(lib.incidence_graph(h["stars"], n))
                brute = gates.brute_force_nonplanar(sharing_graph(h["stars"], n))
                checked += 1
                bad += routine != brute
                if stage == t - 1:
                    previous_passes += (not brute)
                if stage == t:
                    assert brute, "first failing stage is planar by brute force"
    report["V1"] = {"stages_checked": checked, "disagreements": bad, "previous_stage_passes_by_brute_force": previous_passes}


def kuratowski_certified(g):
    """The routine's counterexample is a subdivision of K5 or K3,3: suppress degree-two nodes and compare."""
    ok, cert = nx.check_planarity(g, counterexample=True)
    if ok:
        return False
    h = nx.Graph(cert)
    changed = True
    while changed:
        changed = False
        for v in list(h):
            if h.degree(v) == 2:
                a, b = list(h[v])
                if h.has_edge(a, b):
                    return False
                h.remove_node(v)
                h.add_edge(a, b)
                changed = True
                break
    return nx.is_isomorphic(h, nx.complete_graph(5)) or nx.is_isomorphic(h, nx.complete_bipartite_graph(3, 3))


def embedding_certified(g):
    """A planar verdict is backed by a combinatorial embedding whose faces, counted component by component, satisfy Euler's
    formula V - E + F = 2C."""
    ok, emb = nx.check_planarity(g)
    if not ok:
        return False
    emb.check_structure()
    marked, faces = set(), 0
    for v, w in list(emb.edges()):
        if (v, w) not in marked:
            emb.traverse_face(v, w, mark_half_edges=marked)
            faces += 1
    isolated = sum(1 for v in g if g.degree(v) == 0)
    return g.number_of_nodes() - g.number_of_edges() + faces + isolated == 2 * nx.number_connected_components(g)


def v1b(report):
    """Certificates for every first failing stage (the routine's own Kuratowski subgraph is a K5 or K3,3 subdivision) and for the
    stage before it (an embedding satisfying Euler's formula), over P2 and P3."""
    draws = {(d["arm"], d["draw"]): d for d in lib.p3_draws()}
    sources = lib.recorded_sources()
    fail_ok = fail_bad = pass_ok = pass_bad = 0
    for path in sorted(lib.OUT.glob("p[23]_*.jsonl")):
        for line in path.open():
            r = json.loads(line)
            if r["kind"] != "history" or r["first_failing_step"] is None or r["law"] != "parity":
                continue
            stars0 = draws[(r["arm"], r["draw"])]["stars"] if r["population"] == "P3" else sources[r["source"]]
            t = r["first_failing_step"]
            h = lib.grow(stars0, "parity", t, 20000 if r["population"] == "P2" else 5000, time_limit=150)
            if len(h["n_at"]) <= t:
                continue
            if r["population"] == "P2" and h["n_at"][t] > 3000:
                continue
            g = lib.incidence_graph(h["stars"], h["n_at"][t])
            ok = kuratowski_certified(g)
            fail_ok += ok
            fail_bad += not ok
            if t >= 1:
                g0 = lib.incidence_graph(h["stars"], h["n_at"][t - 1])
                ok0 = embedding_certified(g0)
                pass_ok += ok0
                pass_bad += not ok0
    report["V1b"] = {"first_failing_stages_with_kuratowski_certificate": fail_ok, "without": fail_bad,
                     "preceding_stages_with_euler_embedding": pass_ok, "without_embedding": pass_bad}


def v2(report):
    funded = 0
    problems = []
    histories = []
    for path in sorted(lib.OUT.glob("p3_*_arm*_*.jsonl")):
        for line in path.open():
            r = json.loads(line)
            if r["kind"] == "history" and r["steps"] >= 1:
                histories.append(r)
    draws = {(d["arm"], d["draw"]): d for d in lib.p3_draws()}
    for r in histories[::max(1, len(histories) // 300)][:300]:
        d = draws[(r["arm"], r["draw"])]
        h = lib.grow(d["stars"], r["law"], 12, 5000, time_limit=60)
        for seed in lib.REWIRE_SEEDS[:2]:
            stars, shortfall, _ = lib.rewire(d["stars"], h["births"], seed)
            funded += 1
            holders = Counter(x for s in stars for x in s)
            if max(holders.values()) > 2:
                problems.append((r["arm"], r["draw"], "a distinction with more than two holders"))
            if len(stars) != h["n_at"][-1]:
                problems.append((r["arm"], r["draw"], "knot count differs"))
            if any(len(set(s)) != len(s) for s in stars):
                problems.append((r["arm"], r["draw"], "a knot holds a distinction twice"))
            # fresh counts and parent counts of each birth
            k = len(d["stars"])
            missing = 0
            for step in h["births"]:
                for p, f in step:
                    got = len(stars[k])
                    # the births' places: parents taken + fresh
                    missing += (p + f) - got
                    k += 1
            if missing != shortfall:
                problems.append((r["arm"], r["draw"], f"places missing {missing} but shortfall {shortfall}"))
    report["V2"] = {"rewirings_checked": funded, "problems": problems[:10], "problem_count": len(problems)}


def v3(report):
    name = "p3_parity_arm2_000-256.jsonl"
    original = (lib.OUT / name).read_bytes()
    with tempfile.TemporaryDirectory() as tmp:
        # the census script writes into lib.OUT; run it with the output redirected through an environment-free copy of the module
        code = (
            "import sys; sys.path.insert(0, %r); import lib, pathlib; lib.OUT = pathlib.Path(%r); "
            "sys.argv = ['census_p3.py', '--law', 'parity', '--arm', '2']; import runpy; "
            "import census_p3; census_p3.lib.OUT = lib.OUT; census_p3.main()" % (str(Path(__file__).resolve().parent), tmp))
        subprocess.run([sys.executable, "-B", "-c", code], check=True, capture_output=True, text=True)
        replay = (Path(tmp) / name).read_bytes()
    report["V3"] = {"file": name, "bytes_equal": replay == original, "size": len(original)}


def main():
    report = {}
    v1(report)
    v1b(report)
    v2(report)
    v3(report)
    report["pass"] = (report["V1"]["disagreements"] == 0 and report["V1b"]["without"] == 0 and report["V1b"]["without_embedding"] == 0 and report["V2"]["problem_count"] == 0 and report["V3"]["bytes_equal"])
    (lib.OUT / "verify.json").write_text(json.dumps(report, indent=1, sort_keys=True) + "\n")
    print(json.dumps(report, indent=1))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
