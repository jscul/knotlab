"""Independently enumerate first receipts in the frozen B280 comparison.

The source below is rebuilt from the prospective design. The only earlier
code used is the published sending word and the two known clock calendars.
A finite search stops a history at the FIRST complete sending word, in
either orientation. Equal shortest histories into one search state are all
retained. The universe is finite even when no qualified history exists.
"""
import argparse
from collections import defaultdict, deque
from dataclasses import dataclass
from functools import cache
import gzip
import importlib.util
import json
from itertools import product
import os
from pathlib import Path
import subprocess
import sys
import networkx as nx

ROOT = Path(__file__).resolve().parents[2]
OLDER = ROOT / "research/JOINT-PARENTS-AND-ERASURE-20261120-001/audit_clock.py"
spec = importlib.util.spec_from_file_location("older_clock", OLDER)
older = importlib.util.module_from_spec(spec)
spec.loader.exec_module(older)

SENDS = (32, 48, 64, 80)


@dataclass(frozen=True)
class Case:
    d: int
    setting: str
    decoration: bool = True
    second_port: bool = True
    ternaries: bool = False

    def label(self):
        return f"{self.d}/{self.setting}/z{int(self.decoration)}/ports{1+int(self.second_port)}/ss{int(self.ternaries)}"


def enroll():
    for setting in ("intact", "full", "near", "far"):
        yield Case(32, setting)
    for setting in ("intact", "full"):
        yield Case(32, setting, decoration=False)
        yield Case(32, setting, second_port=False)
        yield Case(64, setting)
        yield Case(32, setting, ternaries=True)


def source(case):
    d = case.d
    neighbors = defaultdict(set)
    circuit_pairs = set()
    marked_pairs = set()

    def pair(a, b):
        assert a != b and b not in neighbors[a]
        neighbors[a].add(b)
        neighbors[b].add(a)

    def chain(roles):
        for a, b in zip(roles, roles[1:]):
            pair(a, b)

    near = {d//4, 3*d//4}
    far = {5*d//4, 7*d//4}
    cuts = {"intact": set(), "near": near, "far": far, "full": near|far}[case.setting]
    for i in range(2*d+1):
        j = (i+1) % (2*d+1)
        for old, other in (("c","u"),("u","c")):
            new = other if i in cuts else old
            a, b = old+str(i), new+str(j)
            pair(a,b)
            key = frozenset((a,b))
            circuit_pairs.add(key)
            if old == new == "c":
                marked_pairs.add(key)
    chain(["a", *(f"p{i}" for i in range(1,d+14)), "b"])
    pair("a","c0")
    if case.second_port:
        pair("b",f"c{d}")
    pair(f"c{3*d//2}", f"u{3*d//2}")
    if case.decoration:
        pair(f"c{3*d//2+2}", "z0")
        chain(("z0","z1","z2","z3","z0"))
    for prefix in ("R","S"):
        for a,b in older.FRAME:
            pair(prefix+a,prefix+b)
    pair("Rr1","Sb2")
    pair("Rb2","a")
    pair("b","Sb2")
    # The extra donor of each true ternary has no way through to another
    # original group. Its actual contribution to growth is accounted below.
    gates = {frozenset(("c26","c27")),frozenset(("c27","c28"))} if case.ternaries else set()
    assert gates <= marked_pairs
    return neighbors, circuit_pairs, marked_pairs, gates


class WordReader:
    def __init__(self, send):
        self.words = {send, send[::-1]}
        prefixes = {w[:i] for w in self.words for i in range(len(w))}
        self.prefix_set = prefixes
        self.alphabet = set(send)

    @cache
    def advance(self, prefix, role):
        if role not in self.alphabet:
            return ()
        word = prefix+(role,)
        if word in self.words:
            return None
        while word not in self.prefix_set:
            word = word[1:]
        return word


def read_windows(roles, allowed_pairs, allowed_roles, size):
    chain = 0
    windows = []
    for end,role in enumerate(roles):
        if end and frozenset((roles[end-1],role)) in allowed_pairs:
            chain += 1
        else:
            chain = int(role in allowed_roles)
        if chain >= size:
            windows.append(end-size+1)
    return windows


def paid(roles, neighbors, gates):
    # In a two-parent passage each unused incident pair gives one extension.
    # Every S block supplies an extra original loose name at either c endpoint.
    # A traversed S also has one unused extension at its compulsory w donor.
    amount = 2+sum(len(neighbors[v])-2 for v in roles)
    for block in gates:
        amount += sum(v in block for v in roles)
        amount += sum(frozenset((a,b))==block for a,b in zip(roles,roles[1:]))
    return amount


def search(case, size, binary_only=False):
    neighbors,circuit,marked,gates = source(case)
    send = tuple("S"+s for s in older.prior.sent_word(size))
    detector = WordReader(send)
    start = ("Rb2","a",(),0)
    work = deque([start])
    dist = {start:0}
    previous = defaultdict(list)
    stops = {"ordinary": [],"qualified": []}
    best = {}
    while work:
        state = work.popleft()
        incoming, here, prefix, run = state
        n = dist[state]+1
        if "qualified" in best and n>best["qualified"]:
            break
        for nxt in sorted(neighbors[here]):
            if nxt==incoming or nxt.startswith("R"):
                continue
            block = frozenset((here,nxt))
            if binary_only and block in gates:
                continue
            if run==size:
                new_run = size
            elif block in marked:
                new_run = min(size,run+1)
            else:
                new_run = int(nxt.startswith("c"))
            found = detector.advance(prefix,nxt)
            if found is None:
                for key in ("ordinary","qualified"):
                    if key=="qualified" and new_run!=size:
                        continue
                    if n == best.setdefault(key,n):
                        stops[key].append((state,nxt))
                continue
            new_state=(here,nxt,found,new_run)
            if new_state not in dist:
                dist[new_state]=n
                work.append(new_state)
            if dist[new_state]==n:
                previous[new_state].append(state)
    def trace(state):
        if state==start:
            yield ("Rt","Rb2","a")
        for parent in previous.get(state,()):
            for past in trace(parent):
                yield past+(state[1],)

    c_roles={v for v in neighbors if v.startswith("c")}
    both=c_roles|{v for v in neighbors if v.startswith("u")}
    def certify(right):
        length=len(right)
        left = tuple("R"+older.CALENDAR[i%len(older.CALENDAR)] for i in range(-length,0))
        whole = left+("Rb1",)+right
        N=len(whole)
        assert tuple(right[-size:]) in detector.words
        assert not any(tuple(whole[i:i+size]) in detector.words for i in range(N-size))
        inputs=(whole[:-1],whole[1:])
        launch=whole[length-size//2:length+(size+1)//2]
        billed=[send,send[:-1],send[1:],launch,*inputs,whole]
        windows=read_windows(inputs[1],marked,c_roles,size)
        loose=read_windows(inputs[1],circuit,both,size)
        restricted = read_windows(inputs[1],marked-gates,c_roles,size)
        observations = {}
        for kind,positions in (("third",windows),("third_no_extra",restricted),("untyped_continuing",loose)):
            intervals=[inputs[1][i:i+size] for i in positions]
            classes={min(word,word[::-1]) for word in intervals}
            observations[kind] = {"positions": positions, "distinct": len(classes)}
        mixed=sum(any(v.startswith("c") for v in inputs[1][i:i+size])
                  and any(v.startswith("u") for v in inputs[1][i:i+size]) for i in loose)
        return dict(size=N, raw_delay=N-size, ticks=sum(s>size for s in older.prior.receiver_ticks(N)),
                    grants=[paid(w,neighbors,gates) for w in billed], marked_windows=len(windows),
                    no_extra_windows=len(restricted), ancestors=observations,
                    all_circuit_windows=len(loose), mixed_windows=mixed,
                    right=list(right))
    result={}
    for key,endpoints in stops.items():
        rows=[certify(pre+(next_role,)) for state,next_role in endpoints for pre in trace(state)]
        assert key!="qualified" or all(row["marked_windows"] for row in rows)
        result[key]=rows
    detector.advance.cache_clear()
    return result


def panel():
    return {case.label():{name:{str(s):search(case,s,binary_only=(name=="binary")) for s in SENDS}
                          for name in (("wide","binary") if case.ternaries else ("wide",))}
            for case in enroll()}


def compare_study(data):
    """Compare every attained minimum, grant field and named ancestor position."""
    location = ROOT/"artifacts"/(Path(__file__).resolve().parent.name+"A")
    with gzip.open(next(location.glob("*/receipts.json.gz")), "rt") as stream:
        archive = json.load(stream)
    grant_keys = ("send", "send_other_end_deletion", "send_outside_end_deletion",
                  "receiver_launch", "receiver_internal_parent", "receiver_incoming_parent", "receipt")
    cases = {c.label():c for c in enroll()}
    comparisons=histories=0
    for raw in archive["cases"]:
        length,style,setting = raw["case"].split("_")
        case = Case(int(length), "intact" if setting=="none" else setting, style!="sym", style!="one", style=="ss")
        assert case == cases.pop(case.label())
        modes = data[case.label()]
        for row in raw["rows"]:
            actor = row["reader"]
            mode = "binary" if actor=="binary" and "binary" in modes else "wide"
            gate = "qualified" if actor=="third_qualified" else "ordinary"
            measured = modes[mode][str(row["m"])][gate]
            rest = {tuple(record["right"]):record for record in measured}
            assert len(measured)==len(rest)==len(row["first_members"]), (raw["case"], row)
            comparisons+=1
            for receipt_id in row["first_members"]:
                member = raw["receipts"][receipt_id]
                mine = rest.pop(tuple(member["right"]))
                assert (mine["size"],mine["raw_delay"],mine["ticks"]) == (
                    member["size"], member["delay"],member["turns_since_send"])
                assert mine["grants"]==[member["seven_grants"][k] for k in grant_keys]
                for kind, obs in mine["ancestors"].items():
                    got=member["ancestors"][kind]
                    assert obs["distinct"]==got["distinct"]
                    assert [[i,i+row["m"]] for i in obs["positions"]] == got["size_m_positions"]
                histories+=1
    assert not cases
    print(f"{comparisons} reader/start/send comparisons, {histories} complete earliest histories, "
          f"{7*histories} grant entries, all three ancestor readings agree.")


def check_reduced_sources():
    """Separate whole-source isomorphism from equal payments along a history."""
    def bridge_parts(neighbors):
        graph=nx.Graph(neighbors)
        cuts=list(nx.bridges(graph))
        sizes=[]
        for a,b in cuts:
            graph.remove_edge(a,b)
            parts=sorted(map(len,nx.connected_components(graph)))
            assert len(parts)==2
            sizes.append(tuple(parts))
            graph.add_edge(a,b)
        return sorted(sizes)

    for d in (32,64):
        pristine,_,_,_=source(Case(d,"intact"))
        switched,_,_,_=source(Case(d,"full"))
        assert {v:len(inc) for v,inc in pristine.items()}=={v:len(inc) for v,inc in switched.items()}
        earlier,later=bridge_parts(pristine),bridge_parts(switched)
        assert earlier!=later
        assert 2*d+1 in [r[0] for r in earlier] and 2*d+1 not in [r[0] for r in later]
        print(f"Asymmetric d={d}, donor counts after singly separating meetings: {earlier} versus {later}.")
    unadorned,_,_,_=source(Case(32,"intact",decoration=False))
    swapped,_,_,_=source(Case(32,"full",decoration=False))
    def rename(v):
        if v.startswith(("c","u")) and sum(c<int(v[1:]) for c in (8,24,40,56))%2:
            return ("u" if v[0]=="c" else "c")+v[1:]
        return v
    for v,adjacent in unadorned.items():
        assert {rename(t) for t in adjacent}==swapped[rename(v)]
    print("Symmetric d=32 control: the given permutation transports the entire reduced donor system.")


def check_scaling_example():
    """One size past the two enrolled source lengths, testing the later proof corollary."""
    size = 80
    results=[]
    for setting in ("intact","full"):
        case=Case(size,setting)
        receipts=search(case,size)["ordinary"]
        assert len(receipts)==1
        results.append(receipts[0])
        _,_,marked,_=source(case)
        # The c predicate does not use what the receiver reports. Recover
        # connected components directly from the remaining c-to-c meetings.
        adjacent={f"c{i}":set() for i in range(2*size+1)}
        for pair in marked:
            a,b=pair
            adjacent[a].add(b)
            adjacent[b].add(a)
        pending=set(adjacent)
        pieces=[]
        while pending:
            first=pending.pop()
            seen=[first]
            for old in seen:
                for new in adjacent[old] & pending:
                    pending.remove(new)
                    seen.append(new)
            pieces.append((len(seen),all(len(adjacent[v])==2 for v in seen)))
        if setting=="intact":
            assert pieces==[(2*size+1,True)]
        else:
            assert sorted(pieces)==[(size//2,False)]*3+[(size//2+1,False)]
    active,finite=results
    assert active["size"]==finite["size"]==4*size+13
    assert active["ticks"]==finite["ticks"]==(4*size+13)//24-size//24
    assert active["grants"]==finite["grants"]
    assert (active["marked_windows"],finite["marked_windows"])==(2,0)
    assert (active["all_circuit_windows"],finite["all_circuit_windows"])==(2,2)
    assert (active["mixed_windows"],finite["mixed_windows"])==(0,2)
    print(f"Supplementary d=m={size}: last finite size {size//2+1}, "
          f"first receipt {active['size']}, own ticks {active['ticks']}, "
          f"matched grants {active['grants']}.")


def check_local_knot_laws():
    """Test the exact 3/4 and 5/4 spent witness relations with the canonical CLI."""
    env=dict(os.environ, PYTHONPATH=str(ROOT/"tools"))
    for width in (7,9):
        names=[f"x{i}" for i in range(width)]
        for law in ("parity","not-all-equal"):
            exclusions=[]
            expected=set()
            for word in product((0,1),repeat=width):
                allowed=(sum(word)%2==0) if law=="parity" else len(set(word))==2
                if allowed:
                    expected.add("".join(map(str,word)))
                else:
                    exclusions.append(" ".join(("~" if b else "")+v for v,b in zip(names,word)))
            command=[sys.executable,"-B","-m","knotlab","check","--cnf",";".join(exclusions),
                     "--loops",*names[:-1],"--contact",names[-1],"--json"]
            check=json.loads(subprocess.check_output(command,cwd=ROOT,env=env,text=True))
            assert check["is_knot"] and check["erasure"]=="forgetting" and set(check["allowed"])==expected
            print(f"Canonical {law} witness, {width} places: {len(expected)} allowed words.")


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,help="optional JSON destination for each witnessed minimum")
    parser.add_argument("--check",action="store_true",help="compare all cases against the independent leaf ledger")
    parser.add_argument("--scaling-example",action="store_true",help="check the binary scaling corollary outside the frozen panel")
    parser.add_argument("--local-knots",action="store_true",help="run the canonical test on each new marking witness")
    args=parser.parse_args()
    if args.scaling_example:
        check_scaling_example()
        raise SystemExit(0)
    if args.local_knots:
        check_local_knot_laws()
        raise SystemExit(0)
    data=panel()
    if args.output:
        args.output.write_text(json.dumps(data,sort_keys=True,separators=(",",":"))+"\n")
    if args.check:
        compare_study(data)
        check_reduced_sources()
        raise SystemExit(0)
    for case,reads in data.items():
        for reader,sends in reads.items():
            print(case,reader,[(s,tuple((r[0]["size"],r[0]["ticks"],len(r),r[0]["marked_windows"],r[0]["mixed_windows"]) if r else None for r in (v["ordinary"],v["qualified"]))) for s,v in sends.items()])
