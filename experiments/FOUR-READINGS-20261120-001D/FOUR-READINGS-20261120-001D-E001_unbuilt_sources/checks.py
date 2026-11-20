"""Rebuild the controls, the minimum sample, physical interventions, and isolated readings."""
from collections import Counter
from functools import cache
from itertools import combinations
import json
import os
from pathlib import Path
import subprocess
import sys

import networkx as nx

from panel import (HERE, ROOT, OUT, LAWS, base, end, fix, graph_of, legality, module, path_features)

prior_dir = ROOT / "experiments/GENERATORS-20261120-001A/GENERATORS-20261120-001A-E001_generators"
sys.path.insert(0, str(prior_dir))
ctl = module("s4_control", str(prior_dir.relative_to(ROOT / "experiments") / "controls.py"))
periods = module("s4_period", str(prior_dir.relative_to(ROOT / "experiments") / "periodic.py"))
med = module("s4_med", "COPIES-AND-MEETINGS-20261120-001A/COPIES-AND-MEETINGS-20261120-001A-E001_copies/mediator.py")


def canonical_cli():
    results = []
    env = dict(os.environ, PYTHONPATH=str(ROOT / "tools"))
    for n in (3,4,5):
        names = [f'x{i}' for i in range(n)]
        for law in LAWS:
            forbidden = [w for w in range(1 << n) if w.bit_count() % 2]
            if law == 'nae':
                forbidden = [0, (1 << n) - 1]
            cnf = ';'.join(' '.join(('~' if (w >> i) & 1 else '') + name
                                     for i, name in enumerate(names)) for w in forbidden)
            cmd = [sys.executable, '-B','-m','knotlab','check','--cnf',cnf,'--loops',*names[:-1],'--contact',names[-1],'--json']
            v = json.loads(subprocess.check_output(cmd, env=env))
            assert v.get('is_knot', v.get('knot', False)), v
            results.append({"arity":n,"law":law,"canonical":v})
    return results


@cache
def traced(stars, law, ages):
    frames,layers = fix.trajectory(stars, law, ages)
    return frames, layers


def inclusive(stars, law, donor, receiver, ages, armed):
    frames,layers = traced(stars, law, ages)
    flags = {}
    pure = {}
    rows = []
    for age, (births, _) in enumerate(layers, 1):
        nf, pure_next = {}, {}
        for b in births:
            tag = 0
            pure_mark = 0
            if age == 1 and b.parents == (receiver,):
                tag = pure_mark = 1
            elif age == 1 and b.parents == (donor,) and armed:
                tag = pure_mark = 2
            elif age > 1:
                for p in b.parents:
                    tag |= flags.get(p, 0)
                if len(b.parents) == 1:
                    pure_mark = pure.get(b.parents[0], 0)
            nf[b.knot], pure_next[b.knot] = tag,pure_mark
        c = Counter(nf.values())
        pur = Counter(pure_next.values())
        assert pur[1] == 1 and pur[2] == int(armed)
        previous = flags
        exact = []
        if c[3]:
            for b in births:
                if nf[b.knot] == 3:
                    exact.append([previous.get(p,0) for p in b.parents])
        rows.append({'age':age,'receiver':c[1]+c[3],'common':c[3],'pure_receiver':pur[1],
                     'pure_donor':pur[2],'joint_parent_marks':exact})
        pure,flags = pure_next,nf
    return rows


def compare(stars, law, donor, receiver, d, simple):
    bit_counts = Counter(b for row in stars for b in row)
    x = min(b for b in stars[donor] if bit_counts[b] == 1)
    if simple:
        off = tuple(tuple(b for b in s if v != donor or b != x) for v,s in enumerate(stars))
    else:
        a,b,c,u,v = range(1 + max(bit_counts), 6 + max(bit_counts))
        off = stars + ((x,a,b),(a,b,c),(c,u,v))
    assert legality(off)[law]['lawful']
    on_state,off_state = end.from_stars(stars),end.from_stars(off)
    adjusted = dict(on_state.opens)
    adjusted[donor] -= 1
    if not simple:
        adjusted[len(stars)+2] = 2
    assert off_state.opens == adjusted and on_state.blocks == off_state.blocks
    assert end.step(off_state,law).status == 'extend'
    n = d+3
    on = inclusive(stars,law,donor,receiver,n,True)
    changed = inclusive(off,law,donor,receiver,n,False)
    assert [r['common'] for r in on] == [0]*d+[0,1,2]
    assert set(on[d+1]['joint_parent_marks'][0]) == {1,2}
    assert [r['receiver']-s['receiver'] for r,s in zip(on,changed,strict=True)] == [0]*(d+1)+[1,2]
    assert not any(r['common'] for r in changed)
    return {"donor":donor, "receiver":receiver,"holding":x,"registered_single_withdrawal":simple,
            "matched_stars":off, "on":on, "off":changed}


def evaluate_interventions(rows):
    answer = []
    for r in rows:
        stars = tuple(map(tuple,r['stars']))
        for law in LAWS:
            parts = r['laws'][law]['parts']
            for p in parts:
                if not p['collateral_candidates']:
                    continue
                assert p['donor_off'], (r['weighting'],r['pair_index'])
                d = len(p['initial_holders'])-1
                receipts = [compare(stars, law, edit['donor'], edit['receiver'], d, edit['legal']) for edit in p['donor_off']]
                answer.append({"weighting":r['weighting'],"draw":r['pair_index'],"law":law,
                               "separation_at_source":d,"comparisons":receipts})
    return answer


def minimum(rows):
    r = min((r for r in rows if any(r['laws'][law]['certified_releases'] for law in LAWS)),
            key=lambda r:(r['knots'],r['distinctions'],r['pair_index']))
    s = tuple(map(tuple,r['stars']))
    out = {}
    for law in LAWS:
        frames,layers = fix.trajectory(s,law,6)
        for f in frames:
            fix.certify_source(f,law)
        by_age=[]
        for age, (births, _) in enumerate(layers,1):
            state = end.from_stars(frames[age])
            live = set(state.opens)
            # Independent invariant from accumulated physical supports, excluding
            # spent pairs while retaining their common-holder witness.
            _, physical, _ = fix.incidence(frames[age])
            g = nx.Graph()
            g.add_nodes_from(live)
            g.add_edges_from((v,w) for v,w in combinations(live,2) if set(physical[v]) & set(physical[w]))
            assert nx.utils.graphs_equal(g, graph_of(state))
            paths = []
            for members in nx.connected_components(g):
                sub=end.restricted(state,members)
                features=path_features(sub,g.subgraph(members))
                paths.append([len(members),len(features[0]),features[1]])
            by_age.append({"age":age,"parent_sets":[list(b.parents) for b in births],
                           "fresh":[len(b.fresh) for b in births],"part_width_tipcount_stable":sorted(paths)})
        renamed = tuple(tuple(10000 - b for b in reversed(star)) for star in reversed(s))
        f2,l2 = fix.trajectory(renamed,law,6)
        assert [sorted(len(b.fresh) for b in born) for born,_ in l2] == [sorted(len(b.fresh) for b in born) for born,_ in layers]
        assert all(legality(renamed)[q]['lawful'] for q in LAWS)
        out[law]=by_age
    return {"weighting":r['weighting'],"pair_index":r['pair_index'],"prufer":r['prufer'],
            "extra_meeting":r['extra_meeting'],"coins":r['coins'],"meetings":r['meetings'],
            "loose":r['loose'],"stars":s,"replay":out}


def matched_end_information():
    # Three live knots separated by spent three-place witnesses. Both outer supports
    # have arity three until one old shared distinction is duplicated at the right.
    pairs=((0,3),(1,3),(1,3),(1,4),(1,4),(2,4))
    one = fix.source_from(pairs,[2,2,2,0,0])
    two = fix.source_from(pairs+((2,4),),[2,2,2,0,0])
    assert end.from_stars(one) == end.from_stars(two)
    result=[]
    for s in (one,two):
        counts=Counter(b for row in s for b in row)
        cuts=[]
        for donor in (0,2):
            x = next(b for b in s[donor] if counts[b]==1)
            off = tuple(tuple(b for b in row if b!=x) if v==donor else row for v,row in enumerate(s))
            cuts.append([legality(off)[q]['lawful'] for q in LAWS])
        result.append({"stars":s,"ends":cuts})
    assert result[0]["ends"]==[[False,False],[False,False]]
    assert result[1]["ends"]==[[False,False],[True,True]]
    return result


def minimum_return_control():
    links = [(0,1),(0,1),(0,4),(1,4),(2,4),(2,6),(3,4),(3,5),(5,6)]
    stars = fix.source_from(links, [3,0,3,3,3,2,2])
    A, B = (4,0,2,5), (4,0,3,6)
    w = A + B
    def source(word):
        used = set()
        for width in range(1, len(word)//2 + 1):
            for start in range(len(word) - 2*width + 1):
                copy = word[start:start+width]
                if copy == word[start+width:start+2*width]:
                    used.update(copy)
        return not {5,6} <= used
    wins = {}
    for size in (15,16,17,18):
        words = set(periods.windows(w,size))
        assert sum(source(word) for word in words) == (8 if size==15 else 0)
        if size > 15:
            previous = set(periods.windows(w,size-1))
            assert all(word[:-1] in previous and word[1:] in previous for word in words)
        wins[size] = {"phases":len(words),"in_source":sum(map(source,words))}
    all_laws = {}
    for law in LAWS:
        fix.certify_source(stars,law)
        frames,layers=fix.trajectory(stars,law,4)
        all_laws[law]=[len(births) for births,_ in layers]
        assert all_laws[law]==[8,12,19,32]
    return {"starts":stars,"word":w,"cut_checks":wins,"release_age":15,
            "available_literal_checks":all_laws}


def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=OUT/'checks.json')
    args=parser.parse_args()
    rows=[json.loads(l) for l in (OUT/'draws.jsonl').read_text().splitlines()]
    sy=periods.symbolic()
    built={"seven_knot_release":minimum_return_control(),"larger_return_sensitivity":sy["emitters"][0],"direct_at_age_16":sy["encounters"][0]}
    for law in LAWS:
        a=ctl.relay_control(law); b=ctl.ring_control(5,law); c=med.compare_right_open(2,law,(1,2))
        built[law]={"relay":a,"bare_ring":b,"indirect_path":c}
    result={"canonical_types":canonical_cli(),"built":built,"smallest_sample":minimum(rows),
            "current_end_comparator_ambiguity":matched_end_information(),
            "physical_interventions":evaluate_interventions(rows)}
    args.output.write_text(json.dumps(result,separators=(',',':'))+'\n')


if __name__ == '__main__':
    main()
