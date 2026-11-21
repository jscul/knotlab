"""Reconstruct the sender, both true parents and the registered count on ordinary paid starts."""
from importlib.util import module_from_spec, spec_from_file_location
from itertools import pairwise, product
from pathlib import Path
import gzip
import hashlib
import json

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name
OLD = "SIGN-RECORDS-AND-RECEIVER-TICKS-20261120-001B"
SPEC = spec_from_file_location("prior_receiving_clock", ROOT / "experiments" / OLD / (OLD + "-E001_ticks") / "registered.py")
old = module_from_spec(SPEC)
SPEC.loader.exec_module(old)
SIZES = (32, 48, 64, 80)


def start(lifetime, modes, reserve):
    original = old.layout("active" if lifetime == "active" else "rewired", 32)
    middle = original.copy()
    sites = (15,) if len(modes) == 1 else (20, 24) if len(modes) == 2 else ()
    cells = {}
    split = {}
    for pos, mode in zip(sites, modes):
        a, b, w = f"c{pos}", f"c{pos+1}", f"w{pos}"
        group = frozenset((a, b, w))
        middle.add_edges_from(((a, w), (b, w)))
        for u, v in ((a, b), (b, w), (w, a)):
            cells[frozenset((u, v))] = (group, mode)
        if mode == "S":
            for donor in group:
                split[donor] = group
    holdings = dict(middle.degree())
    if reserve:
        holdings[reserve] += 2
    return middle, cells, split, holdings


def tile(a, b, cells):
    pair = frozenset((a, b))
    if pair in cells and cells[pair][1] == "S":
        return cells[pair][0]
    return pair


def units(word, cells):
    return tuple(tile(a, b, cells) for a, b in pairwise(word))


def donor_readings(tiles):
    """Reconstruct every compatible route from actual age-one parent sets, up to reversal."""
    if len(tiles) == 1:
        return tuple((a, b) for a in sorted(tiles[0]) for b in sorted(tiles[0] - {a}))
    middle = []
    for a, b in pairwise(tiles):
        seam = a & b
        if len(seam) != 1:
            return ()
        middle.append(next(iter(seam)))
    if any(a == b for a, b in pairwise(middle)):
        return ()
    return tuple((a, *middle, b) for a in sorted(tiles[0]-{middle[0]})
                 for b in sorted(tiles[-1]-{middle[-1]}))


def index(tile_seq):
    x = tuple(tuple(sorted(s)) for s in tile_seq)
    return min(x, x[::-1])


def frame_orientations(tiles):
    out = set()
    for direction in (tiles, tiles[::-1]):
        for word in donor_readings(direction):
            if old.orientation(word) == word:
                out.add(word)
    return sorted(out)


def paid(window, g, cells, supply):
    """Count all distinct rank-one extensions from the actual closed support in the block cover."""
    if len(window) == 1:
        return supply[window[0]]
    occurrences = list(window)
    internal = []
    for a, b in pairwise(window):
        pair = frozenset((a, b))
        if pair not in cells:
            internal.append(("binary", 2, 2))
            continue
        group, mode = cells[pair]
        if mode == "C":
            internal.append(("common", 2, 3))
        else:
            third, = group - pair
            occurrences.append(third)
            internal.append(("separate", 3, 3))
    candidates = sum(supply[x] for x in occurrences)
    return candidates - sum(loss for _, _, loss in internal)


def proof_tree(word, cells, proper):
    """Use the actual removable-coordinate rule on every distinct contiguous interval."""
    tiles = units(word, cells)
    for a, b, c in zip(word, word[1:], word[2:]):
        left = cells.get(frozenset((a, b)))
        right = cells.get(frozenset((b, c)))
        assert a != c and not (left is not None and right is not None and left[0] == right[0])
    assert all((not proper) or len(group) == 2 for group in tiles)
    assert all(len(group) in (2, 3) for group in tiles)
    # A split block fully inside the interval has support on all three originals.
    # The third donor is retained at its one first birth, not added as a walk step.
    # Dividing words into the two endpoint deletions is exhaustive by the proof.
    # Distinct deletion children of every interval have distinct physical orbits.
    signatures = [tuple(sorted(t)) for t in tiles]
    for offset in (1, 2, 3):
        assert all(signatures[i] != signatures[i+offset]
                   for i in range(len(signatures)-offset))
    h = hashlib.sha256()
    for length in range(1, len(tiles)+1):
        for i in range(len(tiles)-length+1):
            j = i+length
            if length == 1:
                h.update(repr((i, j, signatures[i])).encode())
            else:
                h.update(repr((i, j, (i+1,j), (i,j-1))).encode())
    return {"intervals":len(tiles)*(len(tiles)+1)//2,"actual_parent_digest":h.hexdigest(),
            "original_extra_parents":[[i,sorted(t)] for i,t in enumerate(tiles) if len(t)>2]}


def trace_receiver(word, m, cells, holdings, g):
    ts = units(word,cells)
    n = len(word)
    readings = frame_orientations(ts)
    w = old.send(m//16)
    assert readings and all(old.factors(x[len(x)//2+1:],w) for x in readings)
    parents = [ts[1:], ts[:-1]]
    assert index(parents[0]) != index(parents[1])
    inside = [i for i,p in enumerate(parents) if frame_orientations(p)]
    assert inside == [1]
    outside = ts[1:]
    send_tiles = units(w,cells)
    def hits(x):
        return sum(index(x[i:i+len(send_tiles)])==index(send_tiles)
                   for i in range(len(x)-len(send_tiles)+1))
    assert hits(outside) and not hits(ts[:-1])
    left=0
    right=n
    history=[]
    ticks=[]
    intake_mark=None
    for size in range(n,1,-1):
        current=ts[left:right-1]
        readings_now=frame_orientations(current)
        assert readings_now
        vals={x[0]=='Rb0' and size%2==0 for x in readings_now}
        assert len(vals)==1
        if vals=={True}: ticks.append(size)
        if size==m:
            intake_mark=(left,right)
        history.append([left,right,len(readings_now)])
        if size==2:
            assert all(x[1]=='Rb1' for x in readings_now)
            break
        a = frame_orientations(current[1:])
        b = frame_orientations(current[:-1])
        assert bool(a) != bool(b)
        if a: left+=1
        else: right-=1
    assert sorted(ticks)==list(range(24,n+1,24))
    lo,hi=intake_mark
    return {"size":n,"age":n-1,"ticks_from_origin":len(ticks),
            "ticks_after_send":sum(t>m for t in ticks),"true_receipt_parent_count":2,
            "tick_sizes":sorted(ticks),"launch_slice":[lo,hi],"lineage_slices_and_readings":history,
            "anchored_readings_at_receipt":len(readings),
            "phase_appearances_on_incoming_parent":hits(outside),"phase_appearances_on_internal_parent":hits(ts[:-1]),
            "price_vector":{
                "send":paid(w,g,cells,holdings),
                "send_outside_end_deletion":paid(w[1:],g,cells,holdings),
                "send_other_end_deletion":paid(w[:-1],g,cells,holdings),
                "receiver_launch":paid(word[lo:hi],g,cells,holdings),
                "receiver_internal_parent":paid(word[:-1],g,cells,holdings),
                "receiver_incoming_parent":paid(word[1:],g,cells,holdings),
                "receipt":paid(word,g,cells,holdings)}}


def emissions(version, lifetime, modes, reserve):
    g,cells,split,holdings=start(lifetime,modes,reserve)
    passage=g.subgraph([x for x in g if not x.startswith(("S","R"))]).copy()
    if version=="hereditary":
        for pair,(_group,mode) in cells.items():
            if mode=="S":
                passage.remove_edge(*pair)
    if not nx.has_path(passage,"a","b"):
        return [{"m":m,"status":"no eligible a–b continuation","minimizers":[]} for m in SIZES]
    paths=sorted(nx.all_shortest_paths(passage,"a","b"))
    rows=[]
    for m in SIZES:
        witnesses=[]
        for walk in paths:
            s=old.send(m//16)
            # The right word runs from the receiver through the intake and then the complete packet.
            right=("Rt","Rb2",*walk,"Sb2",*s)
            n=2*len(right)+1
            word=old.left(n//2)+("Rb1",)+right
            assert all(g.has_edge(x,y) for x,y in pairwise(word))
            proper=version=="hereditary"
            pr=proof_tree(word,cells,proper)
            result=trace_receiver(word,m,cells,holdings,g)
            sham=tuple("Sb0" if x=="Sb1" else x for x in word)
            assert paid(sham,g,cells,holdings)==paid(word,g,cells,holdings)
            assert [paid(sham[1:],g,cells,holdings),paid(sham[:-1],g,cells,holdings)]==[
                paid(word[1:],g,cells,holdings),paid(word[:-1],g,cells,holdings)]
            # Apply the same unlabelled member criterion to the paid sham's actual input tiles.
            sham_t=units(sham,cells)
            assert frame_orientations(sham_t) and not any(old.factors(x[len(x)//2+1:],s)
                                                             for x in frame_orientations(sham_t))
            cs=old.c_blocks(word)
            intervals=[(a+i,a+i+m) for a,b in cs for i in range(b-a-m+1)]
            for a,b in intervals:
                assert all(x.startswith("c") for x in word[a:b])
            result.update(pr)
            result.update({"route":walk,"whole_receiving_donors":word,
                           "actual_first_tiles":[sorted(t) for t in units(word,cells)],
                           "simultaneous_third_ancestral_windows":intervals,
                           "strict_no_w_third_windows":[[a,b] for a,b in intervals if all(len(t)==2 for t in units(word[a:b],cells))],
                           "neutral_sham_accepted":False})
            witnesses.append(result)
        rows.append({"m":m,"status":"unambiguous registration","minimizers":witnesses})
    return rows


def third_ceiling(lifetime, modes, allow_extra):
    broken = {48} if lifetime == "rewired" else set()
    sites = (15,) if len(modes) == 1 else (20,24) if len(modes) == 2 else ()
    if not allow_extra:
        broken.update(site for site,mode in zip(sites,modes) if mode=="S")
    if not broken:
        return "unbounded"
    ordered=sorted(broken)
    return max(b-a for a,b in pairwise([*ordered,ordered[0]+65]))


def main():
    arms=[(life,mode,None) for life in ("active","rewired") for mode in ("","C","S","CC","CS","SC","SS")]
    arms.extend((life,mode,reserve) for life,mode,reserve in product(("active","rewired"),("C","S"),("c17","c54")))
    rows=[]
    for life,mode,reserve in arms:
        rows.append({"lifetime":life,"gates":mode,"reserve":reserve,
                     "third_spine_max_size":third_ceiling(life,mode,True),
                     "third_forbidding_every_w_ancestor_max_size":third_ceiling(life,mode,False),
                     "pure_R_receives_this_S_emission":False,
                     "readers":{
            version:emissions(version,life,mode,reserve) for version in ("extended","hereditary")}})
    out={"unit":"complete named preparation, marked send and reader","laws":["parity","not-all-equal"],
         "numeric_authority":"all-age native cluster theorem and actual parent checks; deterministic finite replay",
         "cases":rows}
    OUTPUT.mkdir(exist_ok=True,parents=True)
    p=OUTPUT/"clock.json.gz"
    raw=(json.dumps(out,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode()
    p.write_bytes(gzip.compress(raw,compresslevel=9,mtime=0))
    print(len(rows),"starts",sum(len(x["readers"]["extended"]) for x in rows),"named sends per reader")
    print(p.name,len(raw),len(p.read_bytes()),hashlib.sha256(p.read_bytes()).hexdigest())


if __name__=="__main__":
    main()
