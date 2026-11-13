"""Replay the input selection, powers and every positive triple, using tuples."""
from collections import Counter
from itertools import combinations, product
from pathlib import Path
import gzip
import hashlib
import json
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "artifacts/LIMIT-ONLY-20261112-001A/LIMIT-ONLY-20261112-001A-E001_limit_only"
OUT = ROOT / "artifacts/BRANCH-DEPTH-20261112-001C/BRANCH-DEPTH-20261112-001C-E001_port_census"
TRIPLES = set(product((0, 1), repeat=3))


def select(word, indices):
    return tuple(word[j] for j in indices)


def encode(word):
    return sum(value << j for j, value in enumerate(word))


def join(left, right):
    return frozenset((a, c) for a, b in left for other, c in right if b == other)


def copies(definition):
    n, own, calls = definition
    assert n == 3
    sub = [args for op, args in calls if op == "SELF"]
    permanent = [args for op, args in calls if op == "K"]
    words = list(product((0, 1), repeat=n+own))
    def step(g, usual):
        knots = list(permanent)
        if usual and any(sorted(c) == [0,1,2] for c in sub):
            knots.append([0,1,2])
        return [w for w in words if all(len(set(select(w,a))) > 1 for a in knots)
                and all(select(w,a) in g for a in sub)]
    # A finite depth uses a fresh NAE knot in place of each bottom call.
    ports = TRIPLES - {(0,0,0),(1,1,1)}
    seen = set()
    first_dead = 0
    while ports and frozenset(ports) not in seen:
        seen.add(frozenset(ports))
        ports = {w[:3] for w in step(ports, False)}
        first_dead += 1
    assert not ports
    g = TRIPLES.copy()
    while True:
        local = step(g, True)
        next_g = {w[:3] for w in local}
        if next_g == g:
            break
        g = next_g
    return g, local, sub, first_dead


def rectangular(p):
    return all((a,d) in p for a,_ in p for _,d in p)


def knot(table):
    if not table:
        return False
    size=len(next(iter(table)))
    return (size >= 3 and len(table) < 1 << size and all(
        len({select(row, keep) for row in table}) == 1 << (size-1)
        for keep in combinations(range(size),size-1)))


def projections(power, local, sub, own, cert):
    grouped = {}
    for w in local:
        grouped.setdefault(w[:3], []).append(w)
    table = set()
    for top, p in power:
        for root in grouped[p]:
            words = [(root, root)]
            for ordinal in cert["path"]:
                words = [(carry + child[3:], child) for carry, last in words
                         for child in grouped[select(last, sub[ordinal])]]
            for full, _ in words:
                table.add(tuple(top["abc".index(l)] if l in ("a","b","c") else full[int(l[1:])]
                                for l in cert["variables"]))
    return table


def canonical(mask,size=3):
    names = tuple("ABCDE"[:size])
    clauses = []
    for row in product((0,1),repeat=size):
        if not (1 << encode(row)) & mask:
            clauses.append(" ".join(("~" if bit else "")+n for n,bit in zip(names,row)))
    if not clauses:
        clauses.append("A ~A")
    argv = [sys.executable,"-B","-m","knotlab","check","--cnf","; ".join(clauses),
            "--loops",*names[:-1],"--contact",names[-1],"--json"]
    env = {**os.environ, "PYTHONPATH":str(ROOT / "tools")}
    return json.loads(subprocess.check_output(argv, cwd=ROOT, env=env))["is_knot"]


def check_cycle(cycle, local, children, own):
    assert cycle and any(link.get("kind") != "carry" for link in cycle)
    child_words = {}
    for w in local:
        child_words.setdefault(w[:3], []).append(w)
    for i, link in enumerate(cycle):
        assert link["out"] == cycle[(i+1)%len(cycle)]["top"]
        carrier = children[0][link["out"]]
        if link.get("kind") == "carry":
            assert carrier == link["top"]
            continue
        assert link["carrier"] == carrier and carrier >= 3
        who, aux = link["child"],link["var"]
        assert 3 <= aux < 3+own
        if who is None:
            assert aux != carrier
        else:
            assert 0 < who < len(children)
        triads = set()
        conditional = {}
        for port, extensions in child_words.items():
            table = set()
            x = port[link["top"]]
            for w in extensions:
                witnesses = [w] if who is None else child_words[select(w,children[who])]
                table.update((x,w[carrier],other[aux]) for other in witnesses)
            if x in conditional:
                assert table == conditional[x]
            conditional[x] = table
            triads |= table
        assert knot(triads) and {tuple(1-v for v in t) for t in triads} == triads
        assert sum(1<<encode(t) for t in triads) == link["mask"]


def verify():
    data = json.loads((OUT/"port_tables.json").read_text())
    endpoints = json.loads((OUT/"endpoint_tables.json").read_text())
    chains = json.loads((OUT/"chains.json").read_text())
    four = json.loads((OUT/"four_members.json").read_text())
    silent = {(v["file"],v["line"]):v for v in json.loads((OUT/"silent_ports.json").read_text())}
    records = {(r["file"],r["line"]):r for r in data["rows"]}
    samples = {(r["file"],r["line"]):r for r in endpoints["rows"]}
    chain_rows = {(r["file"],r["line"]):r["cycle"] for r in chains["rows"]}
    four_rows = {(r["file"],r["line"]):r for r in four["rows"]}
    result, masks, quadrum, seen_keys = Counter(), set(), set(), set()
    for name, sha in data["source_files"].items():
        path = SOURCE/name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == sha
        for line, text in enumerate(gzip.open(path,"rt"),1):
            raw = json.loads(text)
            if not raw.get("limit_only") or len(raw["defs"]) != 1:
                continue
            key = name,line
            definition = raw["defs"][0]
            own = definition[1]
            g, local, sub, death = copies(definition)
            assert death == raw["first_dead"], (key,death,raw["first_dead"])
            if not g:
                assert key not in records
                result["empty"] += 1
                continue
            seen_keys.add(key)
            row = records[key]
            assert sorted(map(encode,g)) == row["allowed"]
            step = frozenset((w[:3], select(w,sub[0])) for w in local)
            integer_step = sorted([encode(a),encode(b)] for a,b in step)
            assert integer_step == row["transition"]
            r = step
            history = []
            while r not in history:
                history.append(r)
                r=join(r,step)
            rec = next((i for i,q in enumerate(history,1) if rectangular(q)),None)
            full = next((i for i,q in enumerate(history,1) if q == set(product(g,repeat=2))),None)
            assert (rec,full)==(row["rectangular"],row["full"])
            assert row["power_period_start"] == history.index(r)+1
            assert row["power_period"] == len(history)-history.index(r)
            if key in silent:
                s=silent[key]
                calls=definition[2]
                # Trace every port's actual identity in every reachable slot.
                # Reachability of a K occurrence is precisely observability.
                used_by_k = {i for op,args in calls if op=="K" for i in args if i<3}
                if any(sorted(child)==[0,1,2] for child in sub):
                    used_by_k.update(range(3))
                active=[]
                for index in range(3):
                    trace={index}
                    while True:
                        nxt=trace|{j for child in sub for j,v in enumerate(child) if v in trace}
                        if trace==nxt:
                            break
                        trace=nxt
                    if trace & used_by_k:
                        active.append(index)
                assert active==s["active_slots"] and len(active)<3
                stripped=frozenset((select(a,active),select(b,active)) for a,b in step)
                p=stripped
                for k in range(1,s["rectangular"]):
                    assert not rectangular(p)
                    p=join(p,stripped)
                assert rectangular(p)
                check_cycle(s["cycle"],local,sub,own)
                result["linear_after_unused_ports_removed"]+=1
            if rec is not None:
                assert key not in samples
                result["rectangular"] += 1
                cycle = chain_rows[key]
                if cycle:
                    check_cycle(cycle,local,sub,own)
                    masks.update(link["mask"] for link in cycle if link.get("kind") != "carry")
                    result["linear_certificates"] += 1
                continue
            info = samples[key]
            r = frozenset((s,s) for s in g)
            names = (0,1,2)
            states, flags = [], []
            for cert in info["certificates"]:
                assert (r,names) not in states
                states.append((r,names))
                if cert:
                    assert cert["size"] == 3 and len(set(cert["variables"])) == 3
                    labels = cert["variables"]
                    assert any(c in labels for c in "abc")
                    assert any("v"+str(i) in labels for i in range(3,3+own))
                    assert all(not (("v"+str(i) in labels) and (names[i] in range(3)))
                               for i in range(3))
                    table = projections(r,local,sub,own,cert)
                    mask = sum(1 << encode(w) for w in table)
                    assert mask == cert["mask"] and knot(table), key
                    masks.add(mask)
                    result["checked_triples"] += 1
                flags.append(bool(cert))
                r=join(r,step)
                names=tuple(names[i] if i<3 else -1 for i in sub[0])
            assert (r,names)==states[info["start"]]
            assert len(states)-info["start"] == info["period"]
            recurrent=flags[info["start"]:]
            all_depths = all(flags[1:]) and all(recurrent)
            assert all_depths == (info["classification"]=="every_positive_depth")
            result["bounded" if all_depths else "residual"] += 1
            if not all_depths:
                quadruples=four_rows[key]
                options=[(info,0)]
                for kind,offset in (("parent",1),("target",0)):
                    orbit=quadruples[kind]
                    if orbit is None:
                        continue
                    assert orbit["start"]==info["start"] and orbit["period"]==info["period"]
                    options.append((orbit,offset))
                    for (relation,names),cert in zip(states,orbit["certificates"],strict=True):
                        if cert is None:
                            continue
                        labels=cert["variables"]
                        assert cert["size"]==4 and len(set(labels))==4 and any(c in labels for c in "abc")
                        assert any("v"+str(i) in labels for i in range(3+offset*own,3+(offset+1)*own))
                        if offset:
                            assert cert["path"]==[0]
                        for l in labels:
                            if l.startswith("v") and int(l[1:]) < 3:
                                assert names[int(l[1:])]==-1
                        projected=projections(relation,local,sub,own,cert)
                        assert knot(projected) and sum(1<<encode(w) for w in projected)==cert["mask"]
                        quadrum.add(cert["mask"])
                        result["checked_four_member_tables"]+=1
                def has_witness(n):
                    for o,k in options:
                        i=n-k
                        if i>=len(states):
                            i=o["start"]+(i-o["start"])%o["period"]
                        if o["certificates"][i]:
                            return True
                    return False
                start=info["start"]+1
                initial=all(has_witness(n) for n in range(1,start))
                repeats=[has_witness(n) for n in range(start,start+info["period"])]
                verdict=("every_positive_depth" if initial else "eventually_every_depth") if all(repeats) else (
                    "some_periodic_depths" if any(repeats) else "no_eventual_certificate")
                assert verdict==quadruples["classification"]
                result["quads_"+verdict]+=1
    assert seen_keys==set(records)
    assert set(samples)=={k for k,v in records.items() if v["rectangular"] is None}
    assert set(chain_rows)==set(records)-set(samples)
    for m in masks:
        assert canonical(m)
    for m in quadrum:
        assert canonical(m,4)
    assert not canonical(255) and not canonical(195)  # free, and a proper part already constrained
    return dict(totals=result,canonical_triple_tables=sorted(masks),canonical_four_member_tables=sorted(quadrum),
                controls=["free triple rejected","pair-constrained triple rejected"])


if __name__ == "__main__":
    print(json.dumps(verify(),indent=2))
