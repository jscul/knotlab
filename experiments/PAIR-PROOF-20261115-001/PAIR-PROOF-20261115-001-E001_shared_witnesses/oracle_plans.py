"""Offline ideal advice for paid pair probes, plus disjoint-block timing choices.

The coverage producer owns the success enumeration and exact cardinality
frontier. A deployment receives only a list of actual [i,j,base] or
[i,j,base,corner_mask] requests. No covered group, width, cost, answer, or
success flag enters the solver. This module never imports a solver or panel.
"""

from collections import defaultdict
from fractions import Fraction
from itertools import chain
from math import comb
from statistics import median
from typing import NamedTuple


SOURCE_DEPENDENCIES = ()
MENUS = ("skip", "one", "two", "four", "partial-low", "partial-high", "full")
# One covered eligible triple is worth four units. Prices allow abstention
# and charge every request separately, even when all its rows are cached.
PRICES = {"partial-low": (8, 1), "partial-high": (16, 2)}
THREE = (7, 11, 13, 14)


class _Option(NamedTuple):
    base: int
    mask: int
    rows: int


class _Pair(NamedTuple):
    key: tuple
    covers: int
    options: tuple
    full: dict
    anchors: dict


def _bitset(values):
    result = 0
    for i in values:
        if type(i) is not int or i < 0:
            raise ValueError("expected nonnegative integer indices")
        result |= 1 << i
    return result


def _rows(i, j, base, mask):
    corners = (base, base | (1 << i), base | (1 << j), base | (1 << i) | (1 << j))
    return sum(1 << row for k, row in enumerate(corners) if mask & (1 << k))


def _request(key, choice):
    return [*key, choice.base] if choice.mask == 15 else [*key, choice.base, choice.mask]


def _pair(raw, m):
    i, j, canonical = raw["test"]
    if type(i) is not int or type(j) is not int or not 0 <= i < j < m:
        raise ValueError("invalid pair indices")
    bases = tuple(raw.get("bases", (canonical,)))
    corner_masks = raw.get("corner_masks", [[] for _ in bases])
    if len(corner_masks) != len(bases) or len(set(bases)) != len(bases) or canonical not in bases:
        raise ValueError("invalid base or corner-mask list")
    choices, full, anchors = [], {}, {}
    for base, masks in sorted(zip(bases, corner_masks)):
        if type(base) is not int or not 0 <= base < 1 << m or base & ((1 << i) | (1 << j)):
            raise ValueError("a pair base must clear the two varied coordinates")
        full[base] = _Option(base, 15, _rows(i, j, base, 15))
        if masks:
            for mask in sorted(set(masks)):
                if type(mask) is not int or mask not in THREE:
                    raise ValueError("invalid three-corner mask")
                option = _Option(base, mask, _rows(i, j, base, mask))
                # The L's corner opposite the omitted one has an observed
                # unit edge on both axes. Several such Ls may share a center.
                center = ((15 ^ mask).bit_length() - 1) ^ 3
                anchor = base | ((center & 1) << i) | ((center >> 1) << j)
                anchors[anchor] = option
                choices.append(option)
        else:
            option = full[base]
            choices.append(option)
            for c in range(4):
                anchor = base | ((c & 1) << i) | ((c >> 1) << j)
                anchors[anchor] = option
    return _Pair((i, j), _bitset(raw["covers"]), tuple(choices), full, anchors)


def _union(options):
    result = 0
    for opt in options:
        result |= opt.rows
    return result


def _cost(options):
    return _union(options).bit_count(), sum(o.mask.bit_count() for o in options)


def _best_option(pair, already):
    return min(pair.options, key=lambda opt: ((opt.rows & ~already).bit_count(),
                                               opt.mask.bit_count(), opt.base, opt.mask))


def _tune(pairs, initial):
    """Coordinate descent; stop on equality, so a pass cannot cycle."""
    chosen = list(initial)
    for reverse in (False, True, False, True):
        improved = False
        order = reversed(range(len(pairs))) if reverse else range(len(pairs))
        for j in order:
            others = _union(chain(chosen[:j], chosen[j + 1:]))
            replacement = _best_option(pairs[j], others)
            old = chosen[j]
            if ((replacement.rows & ~others).bit_count(), replacement.mask.bit_count()) < (
                    (old.rows & ~others).bit_count(), old.mask.bit_count()):
                chosen[j] = replacement
                improved = True
        if not improved:
            break
    return chosen


def _best_settings(pairs):
    if not pairs:
        return []
    # Geometric lower bound: the read rows have an edge in every incident
    # direction, hence at least v+1 rows. For every compulsory four-corner
    # square, its quadratic contributes another independent function.
    axes = set(chain.from_iterable(p.key for p in pairs))
    compulsory_full = sum(all(opt.mask == 15 for opt in p.options) for p in pairs)
    lower = 1 + len(axes) + compulsory_full
    common = set(pairs[0].anchors)
    for pair in pairs[1:]:
        common.intersection_update(pair.anchors)
    best = None
    best_key = None
    # Common-centred threes/fours attain the lower bound whenever no
    # avoidable fourth corners occur. Other settings remain legal candidates.
    for anchor in sorted(common):
        options = [p.anchors[anchor] for p in pairs]
        key = _cost(options)
        if best is None or key < best_key:
            best, best_key = options, key
        if key[0] == lower and key[1] == 3 * len(pairs) + compulsory_full:
            return options
    # A small fixed multistart search; no optimality claim if the lower bound
    # is not reached. This work belongs only to the free grading-side oracle.
    frequencies = defaultdict(int)
    for p in pairs:
        for anchor in p.anchors:
            frequencies[anchor] += 1
    seeds = [None, *sorted(frequencies, key=lambda r: (-frequencies[r], r))[:3]]
    for seed in seeds:
        chosen, observed = [], 0
        for p in pairs:
            opt = p.anchors.get(seed)
            if opt is None:
                opt = _best_option(p, observed)
            chosen.append(opt)
            observed |= opt.rows
        chosen = _tune(pairs, chosen)
        key = _cost(chosen)
        if best is None or key < best_key:
            best, best_key = chosen, key
        if best_key[0] == lower and best_key[1] == 3 * len(pairs) + compulsory_full:
            break
    return best


def _ordered(pairs, settings):
    pending = list(zip(pairs, settings))
    covered = observed = 0
    requests = []
    while pending:
        j = min(range(len(pending)), key=lambda k: (
            -(pending[k][0].covers & ~covered).bit_count(),
            (pending[k][1].rows & ~observed).bit_count(), pending[k][0].key))
        pair, choice = pending.pop(j)
        covered |= pair.covers
        observed |= choice.rows
        requests.append(_request(pair.key, choice))
    return requests


class _Space:
    def __init__(self, task):
        self.m = task["m"]
        self.eligible = _bitset(task["eligible"])
        entries = [_pair(x, self.m) for x in task["available"]]
        self.pairs = {p.key: p for p in entries}
        if len(entries) != len(self.pairs) or any(p.covers & ~self.eligible for p in entries):
            raise ValueError("duplicated pair or ineligible covered group")
        self.coverable = 0
        for p in entries:
            self.coverable |= p.covers
        self.frontier = {r["k"]: r for r in task["frontier"]}
        cap = task["min_full"]
        if type(cap) is not int or cap < 0 or set(self.frontier) != set(range(cap + 1)):
            raise ValueError("an exact frontier is required for every budget up to full coverage")
        if self.frontier[0]["covered"] != 0 or self.frontier[cap]["covered"] != self.coverable.bit_count():
            raise ValueError("coverage frontier endpoints disagree with the available pairs")
        self.cap = cap

    def stats(self, actions):
        observed = covered = pins = four = total_rows = 0
        used = set()
        for req in actions:
            if len(req) not in (3, 4):
                raise ValueError("malformed probe request")
            i, j, base = req[:3]
            pair = self.pairs[(i, j)]
            if pair.key in used:
                raise ValueError("repeated pair in an ideal plan")
            used.add(pair.key)
            mask = req[3] if len(req) == 4 else 15
            if mask == 15:
                opt = pair.full[base]
            elif mask in THREE:
                center = ((15 ^ mask).bit_length() - 1) ^ 3
                anchor = base | ((center & 1) << i) | ((center >> 1) << j)
                opt = pair.anchors.get(anchor)
                if opt is None or opt.mask != mask or opt.base != base:
                    raise ValueError("three-corner advice lacks a successful diagnostic witness")
            else:
                raise ValueError("invalid probe corner mask")
            observed |= opt.rows
            covered |= pair.covers
            pins |= (1 << i) | (1 << j)
            four += mask == 15
            total_rows += mask.bit_count()
        k = len(used)
        return {"requests": k, "covered_groups": covered.bit_count(),
                "eligible_groups_without_this_proof": (self.eligible & ~covered).bit_count(),
                "distinct_cited_stage_rows": observed.bit_count(), "cited_stage_row_requests": total_rows,
                "three_corner_replay_requests_if_all_returned": 3 * k,
                "incident_axes": pins.bit_count(), "four_corner_requests": four,
                "geometry_row_lower_bound": 1 + pins.bit_count() + four if k else 0}

    def frontier_settings(self, k):
        record = self.frontier[k]
        pairs = [self.pairs[tuple(t[:2])] for t in record["tests"]]
        if len(pairs) != k or len({p.key for p in pairs}) != k:
            raise ValueError("frontier action count does not match its stated budget")
        actions = _ordered(pairs, _best_settings(pairs))
        if self.stats(actions)["covered_groups"] != record["covered"]:
            raise ValueError("frontier witness does not attain its declared coverage")
        return actions

    def reuse_prefixes(self, request_price, row_price):
        """Allow slightly lower cardinality coverage to gain cheap shared reads."""
        remaining = list(self.pairs.values())
        covered = observed = 0
        sequence = []
        yield []
        while remaining and len(sequence) < self.cap:
            best_score, best_j, choice = None, None, None
            for j, pair in enumerate(remaining):
                gain = (pair.covers & ~covered).bit_count()
                if not gain:
                    continue
                opt = _best_option(pair, observed)
                added = (opt.rows & ~observed).bit_count()
                cost = request_price + row_price * added
                # Exact ratio comparison; iteration order is canonicalized.
                score = (Fraction(gain, cost), gain, -added, -pair.key[0], -pair.key[1])
                if best_score is None or score > best_score:
                    best_score, best_j, choice = score, j, opt
            if best_j is None:
                break
            pair = remaining.pop(best_j)
            sequence.append(_request(pair.key, choice))
            covered |= pair.covers
            observed |= choice.rows
            yield list(sequence)


def _priced(space, candidates, prices):
    request_price, row_price = prices
    best, best_key = [], (0, 0, 0, ())
    for seq in candidates:
        d = space.stats(seq)
        utility = 4 * d["covered_groups"] - request_price * d["requests"] - row_price * d["distinct_cited_stage_rows"]
        key = (-utility, d["requests"], d["distinct_cited_stage_rows"], tuple(map(tuple, seq)))
        if key < best_key:
            best, best_key = seq, key
    return best


def make_plans(task, full_plan=None):
    """Return seven menu-name -> executable-action-list entries for one edit.

    The uniform coverage proxy is diagnostic. True width, edit kind and CPU
    are unused. The full-menu baseline preserves its supplier's existing
    four-corner order and settings, including the tie choices.
    """
    space = _Space(task)
    frontier = [space.frontier_settings(k) for k in range(space.cap + 1)]
    if full_plan is None:
        full_plan = space.frontier[space.cap]["tests"]
    full_plan = [list(t) for t in full_plan]
    full = space.stats(full_plan)
    if full["requests"] != space.cap or full["covered_groups"] != space.coverable.bit_count():
        raise ValueError("supplied full advice does not attain the minimum full cover")
    out = {"skip": [], "one": frontier[min(1, space.cap)], "two": frontier[min(2, space.cap)],
           "four": frontier[min(4, space.cap)], "full": full_plan}
    for name, prices in PRICES.items():
        out[name] = _priced(space, chain(frontier, space.reuse_prefixes(*prices)), prices)
    return {name: out[name] for name in MENUS}


def describe_plans(task, plans):
    space = _Space(task)
    return {name: space.stats(actions) for name, actions in plans.items()}


def build_plan_maps(coverage, full_advice=None):
    """Return plans[menu][parent_id][edit_id] for the deployment runner."""
    tasks = coverage["tasks"]
    complete = full_advice["parents"] if full_advice is not None else None
    output = {name: {} for name in MENUS}
    for parent, edits in tasks.items():
        for name in MENUS:
            output[name][parent] = {}
        for edit, task in edits.items():
            advice = make_plans(task, None if complete is None else complete[parent][edit])
            for name, requests in advice.items():
                output[name][parent][edit] = requests
    return output


def structural_bounds(task, request_price=8, row_price=1):
    """An optimistic *work-unit* bound for every action selector, including untried menus.

    The exact maximum group coverage for k paid successful directions comes
    from the upstream exhaustive frontier. A search may never visit some of
    these groups. Free label knowledge, positive coverage, and no unsuccessful
    attempts all favor the bound. There is no clock-unit conversion.
    """
    space = _Space(task)
    if request_price < 0 or row_price < 0:
        raise ValueError("work prices must be nonnegative")
    curve, best_upper = [], 0
    for k in range(space.cap + 1):
        n = 0
        while comb(n, 2) < k:
            n += 1
        # Each tested three-corner L contains a unit edge along BOTH axes.
        # Their differences span all incident coordinate directions. If R
        # raw stage points were read, their affine span has dimension <= R-1.
        row_min = 1 + n if k else 0
        covered = space.frontier[k]["covered"]
        upper = 4 * covered - request_price * k - row_price * row_min
        best_upper = max(best_upper, upper)
        curve.append({"requests": k, "coverage_max": covered,
                      "uncovered_eligible_min": space.eligible.bit_count() - covered,
                      "distinct_rows_min_any_corners": row_min,
                      "distinct_rows_min_all_four": row_min + k if k else 0,
                      "coverage_proxy_utility_upper": upper})
    # Above min_full, coverage saturates and the price/lower row bound cannot
    # improve. The actual task may multiply a stage lookup into raw checking.
    return {"frontier": curve, "max_coverage_proxy_utility_upper": best_upper,
            "units_per_covered_group": 4, "units_per_request": request_price,
            "units_per_distinct_row": row_price,
            "covered_groups_possible": space.coverable.bit_count(),
            "eligible_groups": space.eligible.bit_count()}


def favorable_width_routing(coverage, active_plan):
    """Separate favorable diagnostic. It knows the *final edited* width in advance.

    The public solver instead sees only its current certified incumbent, which
    can still improve later. This routing is not among the seven base menus.
    """
    return {p: {e: active_plan[p][e] if d["width"] == 2 else [] for e, d in edits.items()}
            for p, edits in coverage["tasks"].items()}


def _cube(records, arms):
    if not arms or len(set(arms)) != len(arms):
        raise ValueError("timing arms must be nonempty and distinct")
    selected = set(arms)
    blocks, panels = {}, set()
    for r in records:
        arm = r["arm"]
        if arm not in selected:
            continue
        if "panel" in r:
            panels.add(r["panel"])
        if r.get("failure") or type(r["cpu_ns"]) is not int or r["cpu_ns"] < 0:
            raise ValueError("a failed or unmeasured oracle arm cannot enter a timing envelope")
        parent, edit = r["parent"], r["edit"]
        cell = blocks.setdefault(r["block"], {}).setdefault((parent, edit), {})
        if arm in cell:
            raise ValueError("duplicate timing cell")
        cell[arm] = r["cpu_ns"]
    if not blocks or len(panels) > 1:
        raise ValueError("use nonempty timings for exactly one panel")
    first = next(iter(blocks.values()))
    tasks = tuple(sorted(first))
    if not tasks or any(set(cells) != set(tasks) or any(set(times) != selected for times in cells.values())
                        for cells in blocks.values()):
        raise ValueError("timing block/parent/edit/arm matrix is incomplete")
    return blocks, tasks


def _choose_timed(blocks, tasks, calibration, arms, default):
    if len(set(calibration)) != len(calibration) or not calibration or not set(calibration) <= blocks.keys():
        raise ValueError("invalid calibration block IDs")
    choices, scores = {}, {}
    for p, e in tasks:
        deltas = {}
        for arm in arms:
            paired = [blocks[b][p, e][arm] - blocks[b][p, e][default] for b in calibration]
            deltas[arm] = median(paired)
        # No positive price floor or effect-size margin: even a small strict
        # improvement can be selected. An exact tie with abstention abstains.
        choice = min(arms, key=lambda a: (deltas[a], a != default, arms.index(a)))
        choices.setdefault(p, {})[e] = choice
        scores.setdefault(p, {})[e] = deltas
    return {"calibration_blocks": list(calibration), "choices": choices,
            "median_paired_delta_from_skip_ns": scores}


def fit_timing_choices(records, calibration_blocks, default="skip", arms=MENUS):
    """Freeze one menu name per *same edit* from disjoint calibration repeats.

    Input records have block, parent, edit, arm and complete per-edit cpu_ns.
    Call per panel. Grading may use opaque identities; the deployed request
    contains only the chosen pair indices, settings and optional corner mask.
    """
    arms = tuple(arms)
    if default not in arms:
        raise ValueError("the selector must include its abstention arm")
    calibration = tuple(calibration_blocks)
    allowed = set(calibration)
    blocks, tasks = _cube((r for r in records if r["block"] in allowed), arms)
    return _choose_timed(blocks, tasks, calibration, arms, default)


def materialize_choices(plan_maps, choices):
    """Use this one advice map for an actual mixed-policy holdout replay."""
    return {p: {e: [list(t) for t in plan_maps[arm][p][e]] for e, arm in edits.items()}
            for p, edits in choices.items()}


def balanced_folds(blocks):
    """A/B and B/A splits with both panel orders and both rotation directions."""
    ordered = sorted(blocks)
    if len(ordered) < 2 or len(set(ordered)) != len(ordered):
        raise ValueError("at least two distinct timing blocks are needed")
    a = [b for i, b in enumerate(ordered) if i % 4 in (0, 3)]
    b = [v for v in ordered if v not in a]
    return [(a, b), (b, a)]


def _block_cost(blocks, tasks, arm, b, totals):
    if totals is None:
        return sum(blocks[b][t][arm] for t in tasks)
    val = totals[b][arm]
    if type(val) is not int or val < sum(blocks[b][t][arm] for t in tasks):
        raise ValueError("block total cannot be smaller than its measured edit calls")
    return val


def crossfit_envelope(records, folds=None, default="skip", arms=MENUS, comparators=(), block_totals=None):
    """Held-block estimate for same-edit, timing-informed choices over this finite menu.

    Optional block_totals[block][arm] are actual end-to-end durations. Hold
    skip's process/parent overhead fixed and add only the chosen per-edit
    differences. Materialize and replay to test cross-edit cache interactions.
    The deterministic comparator is independently picked on calibration
    blocks, then evaluated on their held blocks.
    """
    arms, comparators = tuple(arms), tuple(comparators) or (default,)
    if default not in arms:
        raise ValueError("abstention must be selectable")
    methods = tuple(dict.fromkeys((*arms, *comparators)))
    blocks, tasks = _cube(records, methods)
    if folds is None:
        folds = balanced_folds(blocks)
    reports, observed = [], set()
    for cal, test in folds:
        cal, test = tuple(cal), tuple(test)
        if (not test or len(set(test)) != len(test) or set(cal) & set(test)
                or not set(test) <= blocks.keys() or observed & set(test)):
            raise ValueError("test blocks must be distinct and disjoint from their calibration blocks")
        observed.update(test)
        fit = _choose_timed(blocks, tasks, cal, arms, default)
        choice = fit["choices"]
        def cal_delta(arm):
            return median(_block_cost(blocks, tasks, arm, b, block_totals)
                          - _block_cost(blocks, tasks, default, b, block_totals) for b in cal)
        control = min(comparators, key=lambda a: (cal_delta(a), comparators.index(a)))
        fixed_menu = min(arms, key=lambda a: (cal_delta(a), a != default, arms.index(a)))
        tested = []
        for b in test:
            skip = _block_cost(blocks, tasks, default, b, block_totals)
            compare = _block_cost(blocks, tasks, control, b, block_totals)
            fixed = _block_cost(blocks, tasks, fixed_menu, b, block_totals)
            actual = sum(blocks[b][p, e][choice[p][e]] for p, e in tasks)
            baseline_edits = sum(blocks[b][t][default] for t in tasks)
            estimate = skip - baseline_edits + actual
            # This comparison peeks at the current block's timings. It is
            # useful only for quantifying optimism and never selects a plan.
            hindsight = skip - baseline_edits + sum(min(blocks[b][t][a] for a in arms) for t in tasks)
            tested.append({"block": b, "chosen_edit_cpu_ns": actual, "default_cpu_ns": skip,
                           "held_choice_cpu_ns": estimate, "control_cpu_ns": compare,
                           "fixed_menu_cpu_ns": fixed, "saved_vs_fixed_menu_ns": fixed - estimate,
                           "saved_vs_control_ns": compare - estimate, "saved_vs_skip_ns": skip - estimate,
                           "same_block_hindsight_only_ns": hindsight})
        reports.append({"calibration_blocks": list(cal), "evaluation_blocks": list(test),
                        "choices": choice, "control": control, "fixed_menu": fixed_menu, "tested": tested})
    if observed != blocks.keys():
        raise ValueError("each block must be evaluated exactly once")
    results = [r for f in reports for r in f["tested"]]
    savings = [r["saved_vs_control_ns"] for r in results]
    wins, losses = sum(x > 0 for x in savings), sum(x < 0 for x in savings)
    nonzero = wins + losses
    sign_tail = sum(comb(nonzero, k) for k in range(wins, nonzero + 1)) / (2**nonzero)
    return {"folds": reports, "trials": len(results), "wins": wins, "losses": losses,
            "ties": len(results) - nonzero, "median_saved_vs_control_ns": median(savings),
            "median_saved_vs_fixed_menu_ns": median(r["saved_vs_fixed_menu_ns"] for r in results),
            "one_sided_sign_reference": sign_tail,
            "includes_default_process_and_parent_overhead": block_totals is not None,
            "scope": "same-edit finite menu, separate timing blocks, edit costs anchored to abstention overhead"}


def same_return_floor(child, selection_cpu_ns=None):
    """Delete variable phases in one *observed* matched return, retaining physical verification.

    This is phase subtraction for the same circuit and measurement, not a
    hardware lower bound for another implementation or even the next run.
    The alternative-check interval already contains independent proof replay.
    """
    if child.get("failure"):
        raise ValueError("cannot construct a floor from a failed return")
    total = child["cpu_ns"]
    phases = child["phases"]
    solve, verify = phases["solve"], phases["verify"]
    alternatives = child["check"].get("alternative_checks_cpu_ns", 0)
    if any(type(t) is not int or t < 0 for t in (total, solve, verify, alternatives)):
        raise ValueError("invalid deployment phase")
    if alternatives > verify or solve + verify > total:
        raise ValueError("overlapping or invalid measured phases")
    result = {"observed_cpu_ns": total, "checker_alternative_interval_ns": alternatives,
              "baseline_returned_pair_proofs": len((child.get("answer") or {}).get("pair_proofs", ())),
              "remaining_verification_ns": verify - alternatives,
              "free_whole_solve_and_alternative_checks_ns": total - solve - alternatives}
    if selection_cpu_ns is None:
        selection_cpu_ns = child.get("work", {}).get("minimum_selection_cpu_ns")
    if selection_cpu_ns is not None:
        if type(selection_cpu_ns) is not int or not 0 <= selection_cpu_ns <= solve:
            raise ValueError("selection interval must lie within solve")
        result["selection_interval_ns"] = selection_cpu_ns
        result["free_selection_and_alternative_checks_ns"] = total - selection_cpu_ns - alternatives
    return result
