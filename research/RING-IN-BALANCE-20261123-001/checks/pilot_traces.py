"""The thread's side of ticket A's gate: per-round traces of the pilot's two programs on the runs of A1.

The pilot's programs are private workspace files (docs/prompts/2026-11-23_balance_pilot/); this script runs only there.
It writes pilot_traces.json: for each run and round, the number of members, the number of parts, the sorted usable loose
counts, the sorted sizes of the inclusion-maximal met sets, and the number of births in the round.
Members are the knots with a usable loose distinction (under the three added rules the helper's program keeps a knot
holding only barred distinctions for one more round; it is left out here).
"""
import json, pathlib, sys
import networkx as nx

ROOT = pathlib.Path(__file__).resolve().parents[3]
PILOT = ROOT / "docs/prompts/2026-11-23_balance_pilot"
sys.path.insert(0, str(PILOT / "balance"))
import roster as R  # the helper's program

own = {}
exec(compile((PILOT / "own_check.py").read_text().split("\nfor law in (")[0], "own_check_defs", "exec"), own)


def ring_stars(n, a):
    stars, nxt = [], n
    for i in range(n):
        stars.append([(i - 1) % n, i] + list(range(nxt, nxt + a)))
        nxt += a
    return stars


def summary(members, h, sets, births):
    members = set(members)
    sets = {frozenset(s & members) for s in sets}
    sets = [s for s in sets if len(s) >= 2]
    maximal = [s for s in sets if not any(s < t for t in sets)]
    g = nx.Graph(); g.add_nodes_from(members)
    for s in maximal:
        s = sorted(s)
        g.add_edges_from((s[0], x) for x in s[1:])
    return {"members": len(members), "parts": nx.number_connected_components(g) if members else 0,
            "h": sorted(h[u] for u in members), "met": sorted(len(s) for s in maximal), "births": births}


def roster_trace(n, a, law, rounds):
    st = R.from_stars(ring_stars(n, a)); out = []
    def snap(state, births):
        phi = getattr(state, "phi", {}) or {}
        use = {u: state.h[u] - phi.get(u, 0) for u in state.h}
        members = [u for u in state.h if use[u] > 0]
        return summary(members, use, [set(s) for s in state.witness_family()], births)
    out.append(snap(st, 0))
    for _ in range(rounds):
        t = R.step(st, law)
        if t.status != "extend":
            out.append({"status": t.status}); break
        st = t.state; out.append(snap(st, len(t.births)))
    return out


def own_trace(n, a, law, rounds):
    w = own["World"](); live = [w.knot(a) for _ in range(n)]
    for i in range(n): w.join(live[i], live[(i + 1) % n])
    def snap(live, births):
        return summary(live, w.use, [set(w.meets[k]) for k in w.meets], births)
    out = [snap(live, 0)]
    for _ in range(rounds):
        before = w.next
        live = own["step"](w, live, law)
        if live is None:
            out.append({"status": "stall"}); break
        out.append(snap(live, w.next - before))
        if not live: break
    return out


LAWS = {"two": (R.Law("CAP-3", "CANCEL-WAIT", True), "CAP", 12),
        "three": (R.Law("CAP-3", "CANCEL-WAIT", True, frozenset({"FILLER-INERT"})), "INERT", 20),
        "ordinary": (R.Law("ORD", "STALL", True), "ORD", 8)}
result = {}
for n in range(3, 17):
    for name, (rlaw, olaw, rounds) in LAWS.items():
        key = f"ring({n},3)|{name}"
        try:
            a = roster_trace(n, 3, rlaw, rounds)
        except Exception as e:  # the helper's program refuses some starts
            a = [{"error": repr(e)[:200]}]
        b = own_trace(n, 3, olaw, rounds)
        result[key] = {"roster.py": a, "own_check.py": b, "agree": a == b}
        print(key, "agree" if a == b else "DIFFER", [(x.get("members"), x.get("parts")) for x in b][:7])
pathlib.Path(__file__).with_name("pilot_traces.json").write_text(json.dumps(result, indent=0))
