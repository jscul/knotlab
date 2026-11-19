"""Run and literally replay the higher-order folded-certificate frontier."""

from argparse import ArgumentParser
from collections import Counter
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
import json
from math import isqrt
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LATER = ROOT / "experiments/LATER-BOND-READING-20261119-001/LATER-BOND-READING-20261119-001-E001_future"
FAST = ROOT / "experiments/JOIN-GROWTH-20261118-001B/JOIN-GROWTH-20261118-001B-E001_joins"


def setup(params):
    global engine, low, high, plans
    engine = params["engine"]
    low, high = int(params.get("low", 4)), int(params.get("high", 6))
    plans = params.get("plans", "one,both,static").split(",")


def cases():
    for order in range(low, high + 1):
        for plan in plans:
            yield f"order{order}-{plan}", [order, plan]


def run(case_id, payload):
    return json.loads(subprocess.run([engine, *map(str, payload)], capture_output=True, text=True, check=True).stdout)


def prepare(where):
    where.mkdir(parents=True, exist_ok=True)
    engine = where / "high"
    subprocess.run(["c++", "-std=c++20", "-O3", str(HERE / "high.cpp"), "-o", engine], check=True)
    return engine


def load(path, name):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def stable_split(capacity):
    g = max(1, isqrt(capacity)) if capacity >= 16 else 3 if capacity >= 11 else 2 if capacity >= 6 else 1
    return [capacity // g + (i < capacity % g) for i in range(g)]


def core(record, folded):
    order = record["r"]
    rcount, bcount = record["shield_counts"]
    hub, hot, hr, hb, br, bb, _ = record["weights"]
    left, right = 0, 0 if folded else 1
    v = 6
    anchors = list(range(v, v + order - 1))
    first_shield = v + order - 1
    red = list(range(first_shield, first_shield + rcount))
    blue = list(range(first_shield + rcount, first_shield + rcount + bcount))
    outside = first_shield + rcount + bcount
    edges, virtual = {}, {}
    for site in range(2, 6):
        edges[site, left if site <= 3 else right] = hub
        for u in anchors:
            edges[site, u] = hot if u == v else 1
    for color, shields in enumerate((red, blue)):
        h = (left, right)[color]
        weight_hub = (hr, hb)[color]
        price = (br, bb)[color]
        for site in shields:
            edges[site, h] = weight_hub + price if folded else weight_hub
            for u in anchors:
                edges[site, u] = 1
            if not folded:
                virtual[site, outside] = price
    return outside, anchors, red, blue, edges, virtual


def literal_fixture(record):
    n, anchors, red, blue, edges, virtual = core(record, False)
    arbitrary = record.get("arbitrary_later_set", False)
    replacement = None
    if arbitrary:
        replacement = (blue[-1], anchors[-1])
        assert edges.pop(replacement) == 1
        edges.update(virtual)
        n += 1  # The previously simulated outside is now ordinary and exhausted.
    rows = [[] for _ in range(n)]
    labels, width = {}, 0

    def site():
        rows.append([])
        return len(rows) - 1

    def wire(holders, count=1):
        nonlocal width
        names = list(range(width, width + count))
        for u in holders:
            rows[u].extend(names)
        width += count
        return names

    for edge, multiplicity in edges.items():
        labels[edge] = wire(edge, multiplicity)
    old = list(range(width))
    for target in (0, *anchors):
        reciprocal = 1 if target == 0 else target
        for a, b in zip(labels[2, target], labels[4, reciprocal], strict=True):
            old[a], old[b] = b, a

    if arbitrary:
        a, b = replacement
        wire((a,))
        wire((b,))
        return rows, labels, old, {"ordinary_junctions": n, "replacement_terminals": replacement}, anchors, red, blue

    def decreasing(pole, capacity):
        if capacity == 2:
            a, b, z = (site() for _ in range(3))
            for edge, w in (((pole, a), 1), ((pole, b), 1), ((a, b), 1), ((b, z), 2),
                            ((a,), 2), ((b,), 1), ((z,), 1)):
                wire(edge, w)
        elif capacity == 3:
            for _ in range(3):
                leaf = site()
                wire((pole, leaf))
                wire((leaf,), 2)
        else:
            children = [site() for _ in range(capacity)]
            u, v, special = children[1], children[2], site()
            for i, child in enumerate(children):
                wire((pole, child))
                if i >= 3:
                    wire((child, u if i % 2 else v))
                wire((child,), 2 if i else capacity - 1)
            for edge in ((u, v), (u, special), (v, special), (special,)):
                wire(edge)

    for hub in red:
        decreasing(hub, record["weights"][4])
    for hub in blue:
        capacity = record["weights"][5]
        if record["shrink_both"]:
            decreasing(hub, capacity)
        else:
            for share in stable_split(capacity):
                first = site()
                wire((hub, first), share)
                wire((first,), share)
    return rows, labels, old, {"ordinary_junctions": n, "ports": red + blue}, anchors, red, blue


def literal_shore(ordering, image, target, anchors, red, blue):
    hubs, v, weak, rt, bt, rs, bs = ordering
    required = {3, 4} if image else {2, 3}
    positive = {h for h in (0,1) if hubs & (1 << h)}
    if v:
        positive.add(anchors[0])
    positive.update(anchors[1:weak+1])
    for sites, count in (((2, 3), rt), ((4, 5), bt)):
        marked = required.intersection(sites)
        hub = 0 if sites[0] == 2 else 1
        forced = marked if not (v if target == "anchor" else hubs & (1 << hub)) else set()
        optional = [q for q in sites if q not in marked]
        left = count - len(forced)
        assert 0 <= left <= len(optional)
        positive.update(forced)
        positive.update(optional[:left])
    positive.update(red[:rs])
    positive.update(blue[:bs])
    return positive


def replay_tools():
    helpers = load(LATER / "census_interfaces.py", "high_branch_helpers")
    prior = load(helpers.PRIOR / "census.py", "high_production_wrapper")
    verify = load(helpers.VERIFY / "verify.py", "high_independent_verify")
    fast = load(FAST / "fastlib.py", "high_fast_groups")
    return helpers, prior.production_law(), verify, fast


def replay(record, helpers, law, verify, fast):
    start, labels, image, host, anchors, red, blue = literal_fixture(record)
    state = law.from_junctions(start)
    stages = [verify.Arrangement.parse(start)]
    with patch.object(law.F.Presentation, "groups_among", fast.groups_among):
        for _ in range(2):
            result = state.step(law.gf2(law.F.fewest), None)
            assert result is not None and result["new"] and not state.implied_mismatch
            after = verify.Arrangement.parse([sorted(row) for row in state.bits_of])
            verify.round_replay(stages[-1], after)
            stages.append(after)

    arbitrary = record.get("arbitrary_later_set", False)
    terminals = host.get("replacement_terminals")
    arities, capacities, pinned = [], [], []

    def bridge(stage):
        ends, _, ext = stage.holder_graph()
        edges = [edge for edge in ends.values() if max(edge) >= host["ordinary_junctions"]]
        return ends, edges, ext

    loop = [labels[2,0][0], labels[2,anchors[0]][0], labels[3,anchors[0]][0], labels[3,0][0]]
    for age, stage in enumerate(stages):
        arities.append(max(map(len, stage.stars)))
        assert verify.start_audit(stage)["census_open_legal"]
        holds = {b for site in stage.live for b in stage.stars[site]}
        if age or not arbitrary:
            assert all(b >= len(image) or image[b] == b for b in holds)
        assert all(len(set(loop).intersection(support)) % 2 == 0 for support in stage.stars)
        assert len(set(loop).intersection(image[i] for i in stage.stars[0])) == 1
        pinned.append(len(holds))
        if arbitrary:
            _, parts, _ = bridge(stage)
            assert helpers.separating_cost(parts, *terminals) == 1
            capacities.append([1])
            continue
        ends, _, outside = stage.holder_graph()
        membership = helpers.branch_membership(stage, host)
        flow = {}
        for hub in red + blue:
            relevant = [edge for edge in ends.values() if membership[hub].intersection(edge)]
            flow[hub] = helpers.separating_cost(relevant, hub, outside)
        red_expected = record["weights"][4] if age < 2 else 1
        blue_expected = 1 if age == 2 and record["shrink_both"] else record["weights"][5]
        assert all(flow[hub] == red_expected for hub in red)
        assert all(flow[hub] == blue_expected for hub in blue)
        capacities.append([red_expected, blue_expected])

    actual = [[len(stage.stars), len(stage.labels)] for stage in stages]
    for a, b in zip(actual, record["sizes"], strict=True):
        assert a[0] == b[0] and (b[1] < 0 or a[1] == b[1])
    def lift(stage, positive):
        ends, adjacent, outside = stage.holder_graph()
        if arbitrary:
            _, parts, _ = bridge(stage)
            left, right = terminals
            if left in positive and right in positive:
                positive.update(range(host["ordinary_junctions"], len(adjacent)))
            elif (left in positive) != (right in positive):
                if left not in positive:
                    left, right = right, left
                _, shore = helpers.separating_cut(parts, left, right)
                positive.update(shore)
        else:
            membership = helpers.branch_membership(stage, host)
            for port in positive.copy().intersection(membership):
                related = [edge for edge in ends.values() if membership[port].intersection(edge)]
                _, shore = helpers.separating_cut(related, port, outside)
                positive.update(shore)
        side = sum(1 << v for v in positive)
        assert verify.connected(side, adjacent) and verify.connected(((1 << len(adjacent)) - 1) ^ side, adjacent)
        return sorted(b for b, (a, c) in ends.items() if (a in positive) != (c in positive))

    pair_report = {}
    if not arbitrary:
        pair_kind = record["pair_kind"]
        target = 0 if pair_kind == "hub" else anchors[0]
        p = [labels[2, target][0], labels[3, target][0]]
        q = sorted(image[b] for b in p)
        bonds = []
        for i, (shape, pair, k) in enumerate(zip(record["successor_cut_parameters"], (p,q), record["successor_pair_cardinalities"], strict=True)):
            support = lift(stages[2], literal_shore(shape, bool(i), pair_kind, anchors, red, blue))
            assert set(pair) <= set(support) and len(support) == k
            bonds.append(support)
        pair_report = {"old_pair":p,"mapped_pair":q,"successor_literal_bonds":bonds}

    h, v, hr, hb, br, bb, _ = record["weights"]
    special = red[0]
    larger = sorted([labels[special,0][0],labels[special,anchors[0]][0], *(labels[4,a][0] for a in anchors)])
    larger_image = sorted(image[b] for b in larger)
    positive = {0, 2, 3, *anchors}
    if h <= v + len(anchors) - 1:
        positive.add(5)
    if br <= hr + len(anchors):
        positive.update(red[1:])
    if hb + bb < len(anchors):
        positive.update(blue[1:])
    support = lift(stages[1], positive.copy())
    expected = (v + len(anchors)-1 + min(h, v + len(anchors)-1) + hr + len(anchors)
                + (len(red)-1)*min(br,hr + len(anchors)) + len(anchors)
                + (len(blue)-1)*min(hb+bb,len(anchors)))
    assert len(support) == expected and set(larger) <= set(support)
    higher = {"order":len(larger),"marks":larger,"image":larger_image,
              "cardinalities":[expected,None],"literal_finite_bond":support}
    if arbitrary:
        after = lift(stages[2], positive.copy())
        assert len(after)==expected and set(larger) <= set(after)
        higher["successor_literal_finite_bond"] = after
    owners = Counter(tuple(x) for x in stages[0].owners.values() if len(x) == 2)
    repeated = sum(v-1 for v in owners.values())
    return {"sizes": actual, "meet_once_graft_sizes": [[j+4*repeated,n+6*repeated] for j,n in actual],
            "largest_supports": arities, "capacities": capacities, "pinned_distinctions": pinned,
            "old_permutation_prefix": image, "equation_change_allowed_difference": loop,
            "phase_hashes": [sha256(json.dumps([sorted(s) for s in phase.stars]).encode()).hexdigest() for phase in stages],
            "first_higher_reading": higher, **pair_report}


def analytic(order):
    s, l = 4 * order, 2 * order**2 + 1
    m = (21 * order + 1) // 2
    k = order - 2
    c = 4 * (2 * l + k) + 2*s * (m + k + 1)
    core = k + 7 + 2*s
    start = [core + 2*s*(m + 1), c + 2*s*(5*m - 2)]
    current = [start[0] + 2*s*m, start[1] + 2*s*m]
    after = [current[0] + 2*s, current[1] + 2*s]
    bound = k*(2*s + 4) + 8*l + 4*k + order*(2*m + k + 1)
    separating = s*m + 2*l
    witness = 2*l + s*order
    assert s*m >= 2*l and separating - bound >= 9*order+10 and witness < 4*l
    repeated_start = 8*(l - 1) + 2*s*(m - 1)
    once = [[j + 4*repeated_start, n + 6*repeated_start] for j, n in (start, current, after)]
    return {"r": order, "anchors": order - 1, "shield_counts": [s,s], "arm_weight": l,
            "prices": [m,m], "sizes": [start,current,after], "meet_once_sizes": once,
            "folded_bound": bound, "splitting_lower_bound": separating,
            "future_source_upper": witness, "future_image_lower": 4*l}


def static_analytic(order, small_junction_count):
    s = 2*order-1 if small_junction_count else 4*order
    m = 5*order**2-10 if small_junction_count else (9*order+1)//2
    k = order-2
    bound = k*(2*s+4) + max(8+4*k,4+2*s+4*k) + (order-1)*(2*m+k+1)
    threshold = s*m+2
    assert s*m >= 2 and bound < threshold
    core_j = order + 6 + 2*s
    core_n = 4*order + 2*s*(2*m+k+1)
    return {"r":order, "shield_counts":[s,s], "price":m, "folded_bound":bound,
            "splitting_lower_bound":threshold,"sizes":[[core_j,core_n+1],[core_j+2,core_n+5],[core_j+6,core_n+13]],
            "first_distinguishing_order": order+1, "smaller_J_variant":small_junction_count}


def raw_control(binary):
    """Small independent unquotiented checks of every weighted minimum used by the screen."""
    _, _, verify, _ = replay_tools()
    r = 4
    measurements = []
    for weights in ([2,4,3,6,2,3,1], [4,3,2,1,4,2,1]):
        row = {"r": r, "shield_counts": [1,2], "weights": weights}

        def table(folded):
            outside, anchors, _, _, core_edges, virtual = core(row, folded)
            old_exterior = 0 if folded else outside
            holders = [v for v in range(outside+1) if v in {u for pair in core_edges | virtual for u in pair}]
            index = {v:i for i,v in enumerate([x for x in holders if x!=old_exterior]+[old_exterior])}
            edges = list((core_edges | virtual).items())
            adj = [0] * len(index)
            for (a,b),_ in edges:
                adj[index[a]] |= 1 << index[b]
                adj[index[b]] |= 1 << index[a]
            seen = []
            splitting = []
            universe = (1 << len(index)) - 1
            for side in range(1,1 << (len(index)-1)):
                cost, marks = 0,0
                for e,((a,b),w) in enumerate(edges):
                    if ((side >> index[a]) ^ (side >> index[b])) & 1:
                        cost += w
                        marks |= 1 << e
                if not folded and side & (1 << index[0] | 1 << index[1]):
                    splitting.append(cost)
                if verify.connected(side,adj) and verify.connected(universe ^ side,adj):
                    seen.append((cost,marks))
            bonds = sorted(seen)
            columns = [0] * len(edges)
            for i,(_,mask) in enumerate(bonds):
                for e in verify.indices(mask):
                    columns[e] |= 1 << i

            def minimum(terms):
                choices = columns[terms[0]]
                for e in terms[1:]:
                    choices &= columns[e]
                return bonds[(choices & -choices).bit_length()-1][0] if choices else None

            if folded:
                test = {i for i,((a,b),_) in enumerate(edges) if a in range(2,6)}
                values = [minimum(marks) for a in range(1,r+1) for marks in combinations(range(len(edges)),a)
                          if test.intersection(marks)]
                assert None not in values
                return max(values)
            labels = {pair:i for i,(pair,_) in enumerate(edges)}
            p = tuple(minimum(tuple(labels[x] for x in marks)) for marks in (
                ((2,0),(3,0)),((4,1),(3,0)),((2,anchors[0]),(3,anchors[0])),((4,anchors[0]),(3,anchors[0]))))
            return list(p), min(splitting)

        folded = table(True)
        pair, split = table(False)
        reference = json.loads(subprocess.run([binary,"case",*map(str,(r,1,2,*weights[:6]))],
                                             text=True,capture_output=True,check=True).stdout)
        assert reference == {"worst_folded_minimum":folded,"least_splitting_cut":split,"pair_cardinalities":pair}
        measurements.append({"weights":weights,**reference})
    return measurements


def collect(folders):
    sys.path.insert(0, str(ROOT / "scripts"))
    from longrun import load_results
    records = []
    tools = replay_tools()
    controls = []
    for path in folders:
        metadata = json.loads((path/"job.json").read_text())
        setup(metadata["params"])
        ledger = load_results(path)
        assert set(ledger) == {key for key,_ in cases()} and all(row["status"]=="ok" for row in ledger.values())
        controls += raw_control(Path(engine))
        for key,_ in cases():
            row = ledger[key]["result"]
            winner = row["winner"]
            if winner:
                row["two_complete_rounds"] = replay(winner, *tools)
            records.append(row)
    return {"freeze":"3ccfb7f630","panel_bounds":{"anchors":"r-1","shield_counts_each":"r..3r+4",
                                                   "maximum_color_count_difference":2,"prices":"2..6r+8",
                                                   "blue_price":"ceil(red count * red price / blue count) or one more",
                                                   "hub_bundle_prices":"equal to corresponding current branch price",
                                                   "test_spoke_width":"1..r * red shield count","test_v_width_added":[0,1,2],
                                                   "marked_site_cap":"200r^2"},
            "static_panel_bounds":{"anchors":"r-1","shield_counts_each":"1..3r+2","maximum_color_count_difference":2,
                                    "prices":"2..5r^2","blue_price":"ceil(red count * red price / blue count) or one more",
                                    "test_spoke_and_v_width":[1,2]},
            "independent_small_controls":controls,"panels":records,
            "general_formula_examples":[analytic(r) for r in (4,5,6,7,8,9,10,12,16,24,32)],
            "static_formula_examples":[static_analytic(r,small) for r in (4,5,6,7,8,9,10,12,16,24,32)
                                       for small in (True,False)]}


def main():
    p = ArgumentParser(description=__doc__)
    jobs = p.add_subparsers(dest="mode", required=True)
    prep = jobs.add_parser("prepare")
    prep.add_argument("directory", type=Path)
    output = jobs.add_parser("collect")
    output.add_argument("runs", type=Path, nargs="+")
    args = p.parse_args()
    if args.mode == "prepare":
        print(prepare(args.directory))
    else:
        print(json.dumps(collect(args.runs), indent=2))


if __name__ == "__main__":
    main()
